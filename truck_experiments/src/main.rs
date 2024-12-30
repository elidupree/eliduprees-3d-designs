mod app;

use app::*;
use std::path::Path;
use std::sync::Arc;
use truck_platform::*;
// use truck_platform::wgpu::Surface;
use truck_rendimpl::*;
use winit::window::Window;
// use crate::wgpu::Color;
use truck_meshalgo::prelude::*;
use truck_modeling::*;
use truck_platform::wgpu::Color;
use truck_stepio::r#in::ruststep::tables::EntityTable;
use truck_stepio::r#in::{ruststep, BSplineSurfaceWithKnotsHolder, Table};

struct MyApp {
    scene: WindowScene,
}

fn draw_cylinder(scene: &mut WindowScene) {
    // let polygon: PolygonMesh =
    //     truck_polymesh::obj::read(include_bytes!("teapot.obj").as_ref()).unwrap();
    // // Once the polygon data is in the form of an "instance".
    // // This may seem wasteful to the beginning user, but this redundancy is useful for saving memory.
    // let instance: PolygonInstance = scene
    //     .instance_creator() // <- instance is created by instance creator.
    //     .create_instance(&polygon, &Default::default());
    // // Sign up the polygon to the scene.
    // scene.add_object(&instance);

    let v = builder::vertex(Point3::origin());
    let e = builder::tsweep(&v, Vector3::unit_x());
    let f = builder::tsweep(&e, Vector3::unit_y());
    let _cube = builder::tsweep(&f, Vector3::unit_z());

    let v = builder::vertex(Point3::new(0.5, 0.25, -0.5));
    let w = builder::rsweep(&v, Point3::new(0.5, 0.5, 0.0), Vector3::unit_z(), Rad(7.0));
    let f = builder::try_attach_plane(&[w]).unwrap();
    let mut cylinder = builder::tsweep(&f, Vector3::unit_z() * 2.0);
    cylinder.not();
    // let and = truck_shapeops::and(&cube, &cylinder, 0.05).unwrap();
    // and.edge_iter().for_each(|edge| {
    //     let mut curve = edge.get_curve();
    //     if let Curve::IntersectionCurve(inter) = &curve {
    //         if matches! { inter.leader(), Leader::Polyline(_) } {
    //             let flag = curve.to_bspline_leader(0.01, 0.1, 20);
    //             println!("{flag}");
    //         }
    //     }
    //     edge.set_curve(curve);
    // });
    for face in cylinder.triangulation(0.01).face_iter() {
        if let Some(mesh) = face.surface() {
            let q: PolygonInstance = scene
                .instance_creator()
                .create_instance(&mesh, &Default::default());
            scene.add_object(&q);
        }
    }
}

fn load_bss(path: impl AsRef<Path>) -> Vec<BSplineSurface<Point3>> {
    let step_string = std::fs::read_to_string(path).unwrap();

    // next two code lines copied from truck-stepio docs:
    // parse step file
    let exchange = ruststep::parser::parse(&step_string).unwrap();
    // convert the parsing results to a Rust struct
    let table = Table::from_data_section(&exchange.data[0]);

    let mut result = Vec::new();
    for bss in EntityTable::<BSplineSurfaceWithKnotsHolder>::owned_iter(&table) {
        let bss = bss.unwrap();
        let bss = BSplineSurface::<Point3>::try_from(&bss).unwrap();
        // dbg!(bss);
        result.push(bss);
    }
    result
}

fn bss_to_face(bss: BSplineSurface<Point3>) -> Face {
    let edge_curves = bss.splitted_boundary();
    // for curve in &edge_curves {
    //     dbg!(
    //         curve.control_points()[0],
    //         curve.control_points().last().unwrap()
    //     );
    // }
    let corners = edge_curves
        .each_ref()
        .map(|curve| Vertex::new(curve.control_points()[0]));
    let edges = [0, 1, 2, 3].map(|idx| {
        Edge::new(
            &corners[idx],
            &corners[(idx + 1) % 4],
            edge_curves[idx].clone().into(),
        )
    });
    Face::new(vec![Wire::from(edges)], Surface::BSplineSurface(bss))
}

#[async_trait(?Send)]
impl App for MyApp {
    async fn init(window: Arc<Window>) -> Self {
        // let size = window.inner_size();

        let mut camera: Camera = Camera::default();
        // specify position and posture
        camera.matrix = Matrix4::look_at_rh(
            // camera position
            Point3::new(5.0, 6.0, 5.0),
            // The camera looks to the center of the model.
            Point3::new(0.0, 1.5, 0.0),
            // the y-up coordinate
            Vector3::unit_y(),
        )
        // The matrix output from `look_at` needs to be inverted,
        // since cgmath uses the "self-centric" theory of moving the world with respect to the camera,
        // while truck uses the "world-centric" theory of moving the camera with respect to the world.
        .invert()
        .unwrap();

        let mut light: Light = Light::default();
        // It is safe to place the camera in the same position as the flash.
        light.position = camera.position();

        // let render_texture = RenderTextureConfig {
        //     canvas_size: size.into(),
        //     format: surface
        //         .get_preferred_format(&device_handler.adapter())
        //         .expect("Failed to get preferred texture."),
        // };
        // let config = render_texture.compatible_surface_config();
        // surface.configure(device_handler.device(), &config);
        let mut scene = WindowScene::from_window(
            window,
            &WindowSceneDescriptor {
                studio: StudioConfig {
                    background: Color::BLACK,
                    camera,
                    lights: vec![light],
                },
                ..Default::default()
            },
        )
        .await;

        let args: Vec<String> = std::env::args().collect();
        if args.len() > 1 {
            let bss = load_bss(&args[1]);
            for bss in bss {
                println!("doing...");
                let face = bss_to_face(bss);
                println!("done face...");
                let shell = Shell::from([face]);
                println!("done shell...");
                // let triangulation = shell.triangulation(10.9);
                // println!("done triangulation...");
                // for face in triangulation.face_iter() {
                //     if let Some(mesh) = face.surface() {
                //         let q: PolygonInstance = scene
                //             .instance_creator()
                //             .create_instance(&mesh, &Default::default());
                //         scene.add_object(&q);
                //         error;
                //     }
                // }
            }
        } else {
            draw_cylinder(&mut scene);
        }

        MyApp { scene }
    }

    fn render(&mut self) {
        self.scene.render_frame();
    }
}

fn main() {
    // let adapters = wgpu::Instance::new(wgpu::Backends::all());
    // for adapter in adapters.enumerate_adapters(wgpu::Backends::all()) {
    //     println!("{:?}", adapter.get_info())
    // }
    // futures::executor::block_on(async {
    //     let adapter = adapters
    //         .request_adapter(&wgpu::RequestAdapterOptions::default())
    //         .await
    //         .unwrap();
    //
    //     println!("{:?}", adapter.get_info())
    // });
    MyApp::run()
}

impl MyApp {
    // /// Adjusts the size of the backend buffers (depth or sampling buffer) to the size of the window.
    // pub fn size_alignment(&mut self) {
    //     let size = self.window.inner_size();
    //     let canvas_size = self.scene.descriptor().render_texture.canvas_size;
    //     if canvas_size != (size.width, size.height) {
    //         let mut desc = self.scene.descriptor_mut();
    //         desc.render_texture.canvas_size = size.into();
    //         let config = desc.render_texture.compatible_surface_config();
    //         drop(desc);
    //         self.surface.configure(self.scene.device(), &config);
    //     }
    // }
    // /// Render scene to initializing window.
    // pub fn render_frame(&mut self) {
    //     self.size_alignment();
    //     let surface_texture = match self.surface.get_current_texture() {
    //         Ok(got) => got,
    //         Err(_) => {
    //             let config = self
    //                 .scene
    //                 .descriptor()
    //                 .render_texture
    //                 .compatible_surface_config();
    //             self.surface.configure(self.scene.device(), &config);
    //             self.surface
    //                 .get_current_texture()
    //                 .expect("Failed to acquire next surface texture!")
    //         }
    //     };
    //     let view = surface_texture
    //         .texture
    //         .create_view(&wgpu::TextureViewDescriptor::default());
    //     self.scene.render(&view);
    //     surface_texture.present();
    // }
}
