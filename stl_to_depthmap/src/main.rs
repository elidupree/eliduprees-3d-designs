#![allow(unused_variables)]
use clap::{arg, Parser};
use eliduprees_3d_designs_lib::interpolate;
use ordered_float::OrderedFloat;
use std::fs::File;
use std::io::BufReader;
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
    #[arg(short, long, num_args(3))]
    center: Vec<f64>,
    #[arg(short, long, num_args(3))]
    depth_unit_offset: Vec<f64>,
    #[arg(short, long, num_args(3))]
    x_pixel_offset: Vec<f64>,
    #[arg(short, long, num_args(3))]
    y_pixel_offset: Vec<f64>,
    #[arg(short, long)]
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
        (image_space_x.ceil() as usize).max(0)
    }
    fn max_pixel_x_before(&self, image_space_x: f64) -> usize {
        (image_space_x.ceil() as usize).max(self.image_size[0] - 1)
    }
    fn min_pixel_y_after(&self, image_space_y: f64) -> usize {
        (image_space_y.floor() as usize).max(0)
    }
    fn max_pixel_y_before(&self, image_space_y: f64) -> usize {
        (image_space_y.floor() as usize).max(self.image_size[1] - 1)
    }

    fn add_triangle(&mut self, vertices: [StandardVertex; 3]) {
        let mut vertices = vertices
            .each_ref()
            .map(|v| self.vertex_to_pixelspace_location(v));
        vertices.sort_by_key(|l| OrderedFloat(l[1]));
        let vertices = vertices;
        let v0 = vertices[0] + Vector3::new(0.0, -self.tolerance, 0.0);
        let v2 = vertices[2] + Vector3::new(0.0, self.tolerance, 0.0);
        let mid_y = vertices[1][1].floor() as usize;
        // do low-y half
        // TODO reduce duplicate code ID jdfglhfjg0wr4
        {
            let mut others = [vertices[1], vertices[2]];
            others.sort_by_key(|v| OrderedFloat(v[0]));
            let dx_per_dy = others.map(|v| v - v0).map(|v| (v[0] / v[1]));
            let dz_per_dy = others.map(|v| v - v0).map(|v| (v[2] / v[1]));
            for y in self.min_pixel_y_after(v0[1])..mid_y {
                let dy = y as f64 - v0[1];
                let dx = dx_per_dy.map(|d| d * dy);
                let dz = dz_per_dy.map(|d| d * dy);
                let left = v0[0] + dx[0] - self.tolerance;
                let right = v0[0] + dx[1] + self.tolerance;
                for x in self.min_pixel_x_after(left)..=self.max_pixel_x_before(right) {
                    let xfrac = (x as f64 - left) / (right - left);
                    let depth = interpolate(v0[2] + dz[0], v0[2] + dz[1], xfrac);
                    self.rows[y][x] = self.rows[y][x].max(depth)
                }
            }
        }
        // do high-y half
        // TODO reduce duplicate code ID jdfglhfjg0wr4
        {
            let mut others = [vertices[1], vertices[2]];
            // sort by increasing slope, which, since v2 is higher y, is the reverse order of the above...
            others.sort_by_key(|v| OrderedFloat(-v[0]));
            let dx_per_dy = others.map(|v| v - v2).map(|v| (v[0] / v[1]));
            let dz_per_dy = others.map(|v| v - v2).map(|v| (v[2] / v[1]));
            for y in mid_y..=self.max_pixel_y_before(v2[1]) {
                let dy = y as f64 - v2[1];
                let dx = dx_per_dy.map(|d| d * dy);
                let dz = dz_per_dy.map(|d| d * dy);
                let left = v2[0] + dx[0] - self.tolerance;
                let right = v2[0] + dx[1] + self.tolerance;
                for x in self.min_pixel_x_after(left)..=self.max_pixel_x_before(right) {
                    let xfrac = (x as f64 - left) / (right - left);
                    let depth = interpolate(v2[2] + dz[0], v2[2] + dz[1], xfrac);
                    self.rows[y][x] = self.rows[y][x].max(depth)
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

    let input_file = BufReader::new(File::open(input_path).unwrap());
    let mesh = stl::read(input_file, StlType::Automatic).unwrap();
    let rows = (0..image_size[1])
        .map(|_| (0..image_size[0]).map(|_| default_depth).collect())
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
    for vertices in conversion
        .mesh
        .tri_faces()
        .iter()
        .map(|v| v.clone())
        .collect::<Vec<_>>()
    {
        conversion.add_triangle(vertices)
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
}
