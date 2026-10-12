use crate::interpolate;
use ndarray::{Array2, Dim, ShapeBuilder};
use ordered_float::{NotNan, OrderedFloat};
use serde::{Deserialize, Serialize};
use std::collections::btree_set::BTreeSet;
use std::iter::zip;
use std::ops::Range;
use truck_polymesh::{InnerSpace, Point3, PolygonMesh, Vector3};

#[derive(Clone)]
pub struct Depthmap {
    pub depths: Array2<BTreeSet<NotNan<f64>>>,
    pub tolerance: f64,
}

fn closest_depth_in_pixel(depths: &BTreeSet<NotNan<f64>>) -> f64 {
    depths
        .iter()
        .next()
        .map_or(f64::INFINITY, |d| d.into_inner())
}

fn farthest_depth_in_pixel(depths: &BTreeSet<NotNan<f64>>) -> f64 {
    depths
        .iter()
        .rev()
        .next()
        .map_or(f64::NEG_INFINITY, |d| d.into_inner())
}

impl Depthmap {
    pub fn new<Sh: ShapeBuilder<Dim = Dim<[usize; 2]>>>(shape: Sh, tolerance: f64) -> Depthmap {
        Depthmap {
            depths: Array2::from_shape_simple_fn(shape, BTreeSet::new),
            tolerance,
        }
    }

    pub fn from_mesh<Sh: ShapeBuilder<Dim = Dim<[usize; 2]>>>(
        mesh: &PolygonMesh,
        shape: Sh,
        frame: &DepthmapFrameOfReference,
        tolerance: f64,
    ) -> Depthmap {
        let mut result = Depthmap::new(shape, tolerance);

        for vertices in mesh
            .tri_faces()
            .iter()
            .map(|v| v.clone())
            .collect::<Vec<_>>()
        {
            result.add_triangle(
                vertices.each_ref().map(|v| {
                    frame.to_pixelspace_location(&mesh.positions()[v.pos], &result.depths)
                }),
            );
        }

        result
    }

    /// Use one depthmap as the "background" for another.
    ///
    /// Assumes that, at any 2d location where the foreground is present, the background should be ignored; but, optionally, assumes that the foreground is "not entirely reliable" at the edges, allowing the background to fade in over the borders of the foreground.
    ///
    /// Ignores multiple depth entries, and only uses the closest.
    pub fn merge_2d(
        foreground: &Depthmap,
        background: &Depthmap,
        foreground_inset_min: f64,
        foreground_inset_max: f64,
    ) -> Depthmap {
        let mut result = Depthmap::new(foreground.depths.raw_dim(), foreground.tolerance);
        let mut xdist_to_not_foreground =
            Array2::from_elem(foreground.depths.raw_dim(), f64::INFINITY);
        for (fr, mut xdr) in zip(foreground.depths.rows(), xdist_to_not_foreground.rows_mut()) {
            fn spread_forwards<'a>(
                i: impl Iterator<Item = (&'a BTreeSet<NotNan<f64>>, &'a mut f64)>,
            ) {
                let mut dist_to_last = f64::INFINITY;
                for (f, x) in i {
                    dist_to_last += 1.0;
                    if f.is_empty() {
                        dist_to_last = 0.0;
                    }
                    *x = dist_to_last;
                }
            }
            spread_forwards(zip(fr, xdr.iter_mut()));
            spread_forwards(zip(fr.into_iter().rev(), xdr.iter_mut().rev()));
        }
        let mut dist_to_not_foreground =
            Array2::from_elem(foreground.depths.raw_dim(), f64::INFINITY);
        for (xdc, mut dc) in zip(
            xdist_to_not_foreground.columns(),
            dist_to_not_foreground.columns_mut(),
        ) {
            for (y1, d) in dc.iter_mut().enumerate() {
                for y2 in result.pixel_ys_strictly_in_range(
                    y1 as f64 - foreground_inset_max..y1 as f64 + foreground_inset_max,
                ) {
                    let dy = y2 as f64 - y1 as f64;
                    let dx = xdc[y2];
                    *d = d.min((dy * dy + dx * dx).sqrt());
                }
            }
        }
        for ((r, d), (f, b)) in zip(
            zip(&mut result.depths, &dist_to_not_foreground),
            zip(&foreground.depths, &background.depths),
        ) {
            match (f.iter().next(), b.iter().next()) {
                (None, None) => {}
                (Some(f), None) => {
                    r.insert(*f);
                }
                (None, Some(b)) => {
                    r.insert(*b);
                }
                (Some(f), Some(b)) => {
                    let frac = ((d - foreground_inset_min)
                        / (foreground_inset_max - foreground_inset_min))
                        .clamp(0.0, 1.0);
                    r.insert(interpolate(*b, *f, frac));
                }
            }
        }
        result
    }

    /// Make a new depthmap where each point of this depthmap is expanded into a sphere.
    pub fn outset_3d(&self, radius: f64) -> Depthmap {
        let mut result = Depthmap::new(self.depths.raw_dim(), self.tolerance);
        for (y, row) in self.depths.rows().into_iter().enumerate() {
            for (x, depths) in row.into_iter().enumerate() {
                for d in depths {
                    result.add_sphere(Point3::new(x as f64, y as f64, d.into_inner()), radius);
                }
            }
        }
        result
    }

    fn min_pixel_x_after(&self, image_space_x: f64) -> usize {
        image_space_x.ceil().max(0.0) as usize
    }
    fn one_past_max_pixel_x_before(&self, image_space_x: f64) -> usize {
        (image_space_x.floor() + 1.0).clamp(0.0, self.depths.ncols() as f64) as usize
    }
    fn min_pixel_y_after(&self, image_space_y: f64) -> usize {
        image_space_y.ceil().max(0.0) as usize
    }
    fn one_past_max_pixel_y_before(&self, image_space_y: f64) -> usize {
        (image_space_y.floor() + 1.0).clamp(0.0, self.depths.nrows() as f64) as usize
    }
    fn pixel_xs_strictly_in_range(&self, range: Range<f64>) -> Range<usize> {
        self.min_pixel_x_after(range.start)..self.one_past_max_pixel_x_before(range.end)
    }
    fn pixel_ys_strictly_in_range(&self, range: Range<f64>) -> Range<usize> {
        self.min_pixel_y_after(range.start)..self.one_past_max_pixel_y_before(range.end)
    }

    fn add_half_triangle(
        &mut self,
        peak: Point3,
        others: [Point3; 2],
        direction: f64,
        y_range: Range<usize>,
    ) {
        let mut others = others.map(|v| v - peak);
        others.sort_by_key(|v| OrderedFloat(v[0] / v[1] * direction));
        let dx_per_dy = others.map(|v| v[0] / v[1]);
        let dz_per_dy = others.map(|v| v[2] / v[1]);
        for y in y_range {
            let dy = y as f64 - peak[1];
            assert!(dy * direction > 0.0);
            let dx = dx_per_dy.map(|d| d * dy);
            let dz = dz_per_dy.map(|d| d * dy);
            let left = peak[0] + dx[0] - self.tolerance;
            let right = peak[0] + dx[1] + self.tolerance;
            assert!(right > left);
            // assert!(vertices
            //     .iter()
            //     .any(|v| left >= v[0] - self.tolerance - 0.000001));
            // assert!(vertices
            //     .iter()
            //     .any(|v| right <= v[0] + self.tolerance + 0.000001));
            for x in self.pixel_xs_strictly_in_range(left..right) {
                let xfrac = (x as f64 - left) / (right - left);
                assert!(xfrac >= 0.0);
                assert!(xfrac <= 1.0);
                let depth =
                    NotNan::new(interpolate(peak[2] + dz[0], peak[2] + dz[1], xfrac)).unwrap();
                self.add_point(y, x, depth)
            }
        }
    }

    /// Add a point to the depthmap, if there's not already a near-identical one.
    fn add_point(&mut self, y: usize, x: usize, depth: NotNan<f64>) {
        let bucket: &mut BTreeSet<NotNan<f64>> = &mut self.depths[[y, x]];
        // "if there's not already a very-close depth entry" (e.g. on triangle boundaries)
        if bucket
            .range((depth - self.tolerance)..=(depth + self.tolerance))
            .next()
            .is_none()
        {
            bucket.insert(depth);
        }
    }

    /// Add a solid range (at a single pixel) to a depthmap - adding the start and endpoints, and deleting any points already in the middle of the range, which are now "squashed". (Main use of this is for outset3d, which logically makes the infinitesimal thing into a "solid" ... not exactly principled, but oh well.)
    fn add_range(&mut self, y: usize, x: usize, depths: Range<NotNan<f64>>) {
        let bucket: &mut BTreeSet<NotNan<f64>> = &mut self.depths[[y, x]];
        // "if there's not already a very-close depth entry" (e.g. on triangle boundaries)
        bucket.retain(|&d| d < depths.start - self.tolerance || d > depths.end + self.tolerance);
        bucket.insert(depths.start);
        if depths.end > depths.start + self.tolerance {
            bucket.insert(depths.end);
        }
    }

    pub fn add_triangle(&mut self, mut vertices: [Point3; 3]) {
        vertices.sort_by_key(|l| OrderedFloat(l[1]));
        let vertices = vertices;
        let v0 = vertices[0] + Vector3::new(0.0, -self.tolerance, 0.0);
        let v2 = vertices[2] + Vector3::new(0.0, self.tolerance, 0.0);

        // println!("Doing triangle {:?}", vertices);
        self.add_half_triangle(
            v0,
            [vertices[1], vertices[2]],
            1.0,
            self.pixel_ys_strictly_in_range(v0[1]..vertices[1][1]),
        );
        self.add_half_triangle(
            v2,
            [vertices[0], vertices[1]],
            -1.0,
            self.pixel_ys_strictly_in_range(vertices[1][1]..v2[1]),
        );
    }

    pub fn add_sphere(&mut self, center: Point3, radius: f64) {
        for y in self.pixel_ys_strictly_in_range(center[1] - radius..center[1] + radius) {
            let dy = y as f64 - center[1];
            let xrad = (radius * radius - dy * dy).sqrt();
            for x in self.pixel_xs_strictly_in_range(center[0] - xrad..center[0] + xrad) {
                let dx = x as f64 - center[0];
                let drad = (xrad * xrad - dx * dx).sqrt();
                self.add_range(
                    y,
                    x,
                    NotNan::new(center[2] - drad).unwrap()..NotNan::new(center[2] + drad).unwrap(),
                );
            }
        }
    }
}

#[derive(Clone, PartialEq, Serialize, Deserialize)]
pub struct DepthmapFrameOfReference {
    pub origin: Point3,
    pub x_pixel_offset: Vector3,
    pub y_pixel_offset: Vector3,
    pub depth_unit_offset: Vector3,
}

impl DepthmapFrameOfReference {
    pub fn to_pixelspace_location(
        &self,
        p: &Point3,
        depths_array: &Array2<BTreeSet<NotNan<f64>>>,
    ) -> Point3 {
        let offset = p - self.origin;
        Point3::new(
            offset.dot(self.x_pixel_offset) / self.x_pixel_offset.dot(self.x_pixel_offset)
                + (depths_array.ncols() - 1) as f64 / 2.0,
            offset.dot(self.y_pixel_offset) / self.y_pixel_offset.dot(self.y_pixel_offset)
                + (depths_array.nrows() - 1) as f64 / 2.0,
            offset.dot(self.depth_unit_offset) / self.depth_unit_offset.dot(self.depth_unit_offset),
        )
    }
} // struct MeshToDepthmap

pub mod depthmap_generation {
    use crate::depthmap::{
        closest_depth_in_pixel, farthest_depth_in_pixel, Depthmap, DepthmapFrameOfReference,
    };
    use serde::{Deserialize, Serialize};
    use std::borrow::Cow;
    use std::collections::btree_map::BTreeMap;
    use std::fs::File;
    use std::path::{Path, PathBuf};
    use truck_polymesh::stl;
    use truck_polymesh::stl::StlType;

    /// Root type of depthmap generation spec, intended to be saved as a JSON file; generates a sequence of depthmaps, each of which may be based on files or previous ones in the sequence, and may or may not be exported.
    #[derive(PartialEq, Serialize, Deserialize)]
    pub struct Spec {
        pub rows: usize,
        pub cols: usize,
        pub frame_of_reference: DepthmapFrameOfReference,
        pub maps: Vec<DepthmapSpec>,
        pub export_path: PathBuf,
        // pub outputs: BTreeMap<String, DepthmapGenerationOutput>,
    }

    #[derive(PartialEq, Serialize, Deserialize)]
    pub struct DepthmapSpec {
        pub name: String,
        pub data: DepthmapConstructor,
        #[serde(skip_serializing_if = "Option::is_none")]
        pub export: Option<ExportKind>,
    }

    #[derive(PartialEq, Serialize, Deserialize)]
    pub enum ExportKind {
        All,
        OnlyClosest,
        OnlyFarthest,
    }

    #[derive(PartialEq, Serialize, Deserialize)]
    pub enum DepthmapConstructor {
        Mesh(Mesh),
        Outset3d(Outset3d),
        Merge(Vec<DepthmapSource>),
        Merge2d(Merge2d),
    }

    #[derive(PartialEq, Serialize, Deserialize)]
    #[serde(untagged)]
    pub enum DepthmapSource {
        Named(String),
        Constructed(Box<DepthmapConstructor>),
    }

    #[derive(PartialEq, Serialize, Deserialize)]
    pub struct Mesh {
        pub file: PathBuf,
        #[serde(skip_serializing_if = "Option::is_none")]
        pub convert_from_frame_of_reference: Option<DepthmapFrameOfReference>,
    }

    #[derive(PartialEq, Serialize, Deserialize)]
    pub struct Outset3d {
        pub radius: f64,
        pub of: DepthmapSource,
    }

    #[derive(PartialEq, Serialize, Deserialize)]
    pub struct Merge2d {
        pub foreground: DepthmapSource,
        pub background: DepthmapSource,
        pub foreground_inset_min: f64,
        pub foreground_inset_max: f64,
    }

    pub struct Run {
        pub spec: Spec,
        pub results: BTreeMap<String, Depthmap>,
    }

    impl Run {
        pub fn load_mesh(&self, mesh_spec: &Mesh) -> Depthmap {
            let input_file = File::open(&mesh_spec.file).unwrap();
            let mesh = stl::read(input_file, StlType::Automatic).unwrap();
            Depthmap::from_mesh(
                &mesh,
                (self.spec.rows, self.spec.cols),
                mesh_spec
                    .convert_from_frame_of_reference
                    .as_ref()
                    .unwrap_or(&self.spec.frame_of_reference),
                0.000001,
            )
        }

        pub fn construct_outset3d(&self, outset3d: &Outset3d) -> Depthmap {
            self.get_depthmap(&outset3d.of).outset_3d(outset3d.radius)
        }

        pub fn construct_merge2d(&self, merge2d: &Merge2d) -> Depthmap {
            let foreground = self.get_depthmap(&merge2d.foreground);
            let background = self.get_depthmap(&merge2d.background);
            Depthmap::merge_2d(
                &*foreground,
                &*background,
                merge2d.foreground_inset_min,
                merge2d.foreground_inset_max,
            )
        }

        pub fn get_depthmap<'a>(&'a self, source: &DepthmapSource) -> Cow<'a, Depthmap> {
            match source {
                DepthmapSource::Named(name) => Cow::Borrowed(self.results.get(name).unwrap()),
                DepthmapSource::Constructed(constructor) => {
                    Cow::Owned(self.construct_depthmap(constructor))
                }
            }
        }

        pub fn construct_depthmap(&self, constructor: &DepthmapConstructor) -> Depthmap {
            match constructor {
                DepthmapConstructor::Mesh(mesh) => self.load_mesh(&mesh),
                DepthmapConstructor::Outset3d(outset3d) => self.construct_outset3d(outset3d),
                DepthmapConstructor::Merge(_depthmap_sources) => todo!(),
                DepthmapConstructor::Merge2d(merge2d) => self.construct_merge2d(merge2d),
            }
        }

        pub fn run(&mut self) {
            let mut spec_as_last_rendered_path = self.spec.export_path.clone();
            spec_as_last_rendered_path.push("spec_as_last_rendered.json");

            if let Ok(file) = File::open(&spec_as_last_rendered_path) {
                if let Ok(spec_as_last_rendered) = serde_json::from_reader::<_, Spec>(file) {
                    if spec_as_last_rendered == self.spec {
                        println!(
                            "Depthmaps at {:?} already up-to-date",
                            &self.spec.export_path
                        );
                        return;
                    }
                }
            }

            println!("Building depthmaps into {:?}", &self.spec.export_path);
            std::fs::create_dir_all(&self.spec.export_path).unwrap();

            for map_spec in &self.spec.maps {
                println!("Constructing depthmap '{}'", map_spec.name);
                let depthmap = self.construct_depthmap(&map_spec.data);
                if let Some(export_kind) = &map_spec.export {
                    let mut export_path = self.spec.export_path.clone();
                    export_path.push(&map_spec.name);
                    export_path.add_extension("npy");
                    match export_kind {
                        ExportKind::All => todo!(),
                        ExportKind::OnlyClosest => {
                            let output = depthmap.depths.map(closest_depth_in_pixel);
                            ndarray_npy::write_npy(&export_path, &output).unwrap()
                        }
                        ExportKind::OnlyFarthest => {
                            let output = depthmap.depths.map(farthest_depth_in_pixel);
                            ndarray_npy::write_npy(&export_path, &output).unwrap()
                        }
                    }
                }
                self.results.insert(map_spec.name.clone(), depthmap);
                println!("Done constructing depthmap '{}'", map_spec.name);
            }
            serde_json::to_writer_pretty(
                File::create(spec_as_last_rendered_path).unwrap(),
                &self.spec,
            )
            .unwrap();
            println!("Done building depthmaps into {:?}", &self.spec.export_path);
        }
    }

    impl Spec {
        pub fn run(self) {
            let mut run = Run {
                spec: self,
                results: BTreeMap::new(),
            };
            run.run();
        }
    }
    pub fn run_specfile(path: &impl AsRef<Path>) {
        let spec: Spec = serde_json::from_reader(File::open(path).unwrap()).unwrap();
        spec.run();
    }
}
