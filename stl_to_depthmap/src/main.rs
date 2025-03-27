#![allow(unused_variables)]
use clap::{arg, Parser};
use eliduprees_3d_designs_lib::interpolate;
use ordered_float::OrderedFloat;
use std::fs::File;
use std::path::PathBuf;
use truck_polymesh::stl::StlType;
use truck_polymesh::{stl, InnerSpace, Point3, PolygonMesh, StandardVertex, Vector3};

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    input_path: PathBuf,
    output_path: PathBuf,
    #[arg(short, long, num_args(2))]
    image_size: Vec<usize>,
    #[arg(short, long, num_args(3), allow_hyphen_values(true))]
    center: Vec<f64>,
    #[arg(short, long, num_args(3), allow_hyphen_values(true))]
    depth_unit_offset: Vec<f64>,
    #[arg(short, long, num_args(3), allow_hyphen_values(true))]
    x_pixel_offset: Vec<f64>,
    #[arg(short, long, num_args(3), allow_hyphen_values(true))]
    y_pixel_offset: Vec<f64>,
    #[arg(long)]
    default_depth: f64,
}

struct Conversion {
    image_size: [usize; 2],
    mesh: PolygonMesh,
    center: Point3,
    depth_unit_offset: Vector3,
    x_pixel_offset: Vector3,
    y_pixel_offset: Vector3,
    rows: Vec<Vec<f64>>,
    tolerance: f64,
}

impl Conversion {
    fn vertex_to_pixelspace_location(&self, vertex: &StandardVertex) -> Point3 {
        let vertex_offset = self.mesh.positions()[vertex.pos] - self.center;
        Point3::new(
            vertex_offset.dot(self.x_pixel_offset) / self.x_pixel_offset.dot(self.x_pixel_offset)
                + self.image_size[0] as f64 / 2.0,
            vertex_offset.dot(self.y_pixel_offset) / self.y_pixel_offset.dot(self.y_pixel_offset)
                + self.image_size[1] as f64 / 2.0,
            vertex_offset.dot(self.depth_unit_offset)
                / self.depth_unit_offset.dot(self.depth_unit_offset),
        )
    }

    fn min_pixel_x_after(&self, image_space_x: f64) -> usize {
        image_space_x.ceil().max(0.0) as usize
    }
    fn max_pixel_x_before(&self, image_space_x: f64) -> usize {
        image_space_x.floor().min((self.image_size[0] - 1) as f64) as usize
    }
    fn min_pixel_y_after(&self, image_space_y: f64) -> usize {
        image_space_y.ceil().max(0.0) as usize
    }
    fn max_pixel_y_before(&self, image_space_y: f64) -> usize {
        image_space_y.floor().min((self.image_size[1] - 1) as f64) as usize
    }

    fn add_triangle(&mut self, vertices: [StandardVertex; 3]) {
        let mut vertices = vertices
            .each_ref()
            .map(|v| self.vertex_to_pixelspace_location(v));
        vertices.sort_by_key(|l| OrderedFloat(l[1]));
        let vertices = vertices;
        let v0 = vertices[0] + Vector3::new(0.0, -self.tolerance, 0.0);
        let v2 = vertices[2] + Vector3::new(0.0, self.tolerance, 0.0);
        // println!("Doing triangle {:?}", vertices);
        // do low-y half
        // TODO reduce duplicate code ID jdfglhfjg0wr4
        {
            let mut others = [vertices[1], vertices[2]].map(|v| v - v0);
            others.sort_by_key(|v| OrderedFloat(v[0] / v[1]));
            let dx_per_dy = others.map(|v| (v[0] / v[1]));
            let dz_per_dy = others.map(|v| (v[2] / v[1]));
            for y in self.min_pixel_y_after(v0[1])..=self.max_pixel_y_before(vertices[1][1]) {
                let dy = y as f64 - v0[1];
                assert!(dy > 0.0);
                let dx = dx_per_dy.map(|d| d * dy);
                let dz = dz_per_dy.map(|d| d * dy);
                let left = v0[0] + dx[0] - self.tolerance;
                let right = v0[0] + dx[1] + self.tolerance;
                assert!(right > left);
                assert!(vertices
                    .iter()
                    .any(|v| left >= v[0] - self.tolerance - 0.000001));
                assert!(vertices
                    .iter()
                    .any(|v| right <= v[0] + self.tolerance + 0.000001));
                for x in self.min_pixel_x_after(left)..=self.max_pixel_x_before(right) {
                    let xfrac = (x as f64 - left) / (right - left);
                    assert!(xfrac >= 0.0);
                    assert!(xfrac <= 1.0);
                    let depth = interpolate(v0[2] + dz[0], v0[2] + dz[1], xfrac);
                    self.rows[y][x] = self.rows[y][x].min(depth);
                }
            }
        }
        // do high-y half
        // TODO reduce duplicate code ID jdfglhfjg0wr4
        {
            let mut others = [vertices[0], vertices[1]].map(|v| v - v2);
            // sort by decreasing slope, because the dy values will be negative this time...
            others.sort_by_key(|v| OrderedFloat(-v[0] / v[1]));
            let dx_per_dy = others.map(|v| (v[0] / v[1]));
            let dz_per_dy = others.map(|v| (v[2] / v[1]));
            for y in self.min_pixel_y_after(vertices[1][1])..=self.max_pixel_y_before(v2[1]) {
                let dy = y as f64 - v2[1];
                assert!(dy < 0.0);
                let dx = dx_per_dy.map(|d| d * dy);
                let dz = dz_per_dy.map(|d| d * dy);
                let left = v2[0] + dx[0] - self.tolerance;
                let right = v2[0] + dx[1] + self.tolerance;
                assert!(right > left);
                assert!(vertices
                    .iter()
                    .any(|v| left >= v[0] - self.tolerance - 0.000001));
                assert!(vertices
                    .iter()
                    .any(|v| right <= v[0] + self.tolerance + 0.000001));
                for x in self.min_pixel_x_after(left)..=self.max_pixel_x_before(right) {
                    let xfrac = (x as f64 - left) / (right - left);
                    assert!(xfrac >= 0.0);
                    assert!(xfrac <= 1.0);
                    let depth = interpolate(v2[2] + dz[0], v2[2] + dz[1], xfrac);
                    self.rows[y][x] = self.rows[y][x].min(depth);
                }
            }
        }
    }
}

fn point3_arg(input: Vec<f64>) -> Point3 {
    Point3::new(input[0], input[1], input[2])
}
fn vector3_arg(input: Vec<f64>) -> Vector3 {
    Vector3::new(input[0], input[1], input[2])
}

fn main() {
    let Args {
        input_path,
        output_path,
        image_size,
        center,
        depth_unit_offset,
        x_pixel_offset,
        y_pixel_offset,
        default_depth,
    } = Args::parse();

    let input_file = File::open(input_path).unwrap();
    let mesh = stl::read(input_file, StlType::Automatic).unwrap();
    let rows = (0..image_size[1])
        .map(|_| (0..image_size[0]).map(|_| f64::INFINITY).collect())
        .collect();
    let mut conversion = Conversion {
        image_size: image_size.try_into().unwrap(),
        mesh,
        center: point3_arg(center),
        depth_unit_offset: vector3_arg(depth_unit_offset),
        x_pixel_offset: vector3_arg(x_pixel_offset),
        y_pixel_offset: vector3_arg(y_pixel_offset),
        rows,
        tolerance: 0.000001,
    };
    println!(
        "Starting conversion of mesh with bounds {:?}",
        conversion.mesh.bounding_box()
    );
    for vertices in conversion
        .mesh
        .tri_faces()
        .iter()
        .map(|v| v.clone())
        .collect::<Vec<_>>()
    {
        conversion.add_triangle(vertices)
    }
    for row in &mut conversion.rows {
        for val in row {
            if *val == f64::INFINITY {
                *val = default_depth;
            }
        }
    }
    exr::image::write::write_rgb_file(
        output_path,
        conversion.image_size[0],
        conversion.image_size[1],
        |x, y| {
            let depth = conversion.rows[y][x] as f32;
            return (depth, depth, depth);
        },
    )
    .unwrap();
    println!("EXR depthmap written!");
}
