mod app;

use std::sync::Arc;
use app::App;
use truck_platform::*;
use truck_platform::wgpu::Surface;
use truck_rendimpl::*;
use winit::window::Window;
use crate::wgpu::Color;
use truck_modeling::*;
use truck_meshalgo::prelude::*;

struct MyApp {
    scene: Scene,
    window: Arc<Window>,
    surface: Surface,
}

impl App for MyApp {
    fn init(window: Arc<Window>, surface: Surface, device_handler: DeviceHandler) -> Self {

        let size = window.inner_size();

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

        let render_texture = RenderTextureConfig {
            canvas_size: size.into(),
            format: surface
                .get_preferred_format(&device_handler.adapter())
                .expect("Failed to get preferred texture."),
        };
        let config = render_texture.compatible_surface_config();
        surface.configure(device_handler.device(), &config);
        let mut scene = Scene::new(
            device_handler,
            &SceneDescriptor {
                studio: StudioConfig {
                    background: Color::BLACK,
                    camera,
                    lights: vec![light],
                },
                render_texture,
                ..Default::default()
            },
        );

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
        let cube = builder::tsweep(&f, Vector3::unit_z());

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
        for face in cylinder.triangulation(0.01).unwrap().face_iter() {
            let q: PolygonInstance = scene.instance_creator().create_instance(&
                                                                 face.get_surface(), &Default::default());
            scene.add_object(&q);
        }

        MyApp { scene, window, surface }
    }

    fn render(&mut self) {
        self.render_frame();
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
    /// Adjusts the size of the backend buffers (depth or sampling buffer) to the size of the window.
    pub fn size_alignment(&mut self) {
        let size = self.window.inner_size();
        let canvas_size = self.scene.descriptor().render_texture.canvas_size;
        if canvas_size != (size.width, size.height) {
            let mut desc = self.scene.descriptor_mut();
            desc.render_texture.canvas_size = size.into();
            let config = desc.render_texture.compatible_surface_config();
            drop(desc);
            self.surface.configure(self.scene.device(), &config);
        }
    }
    /// Render scene to initializing window.
    pub fn render_frame(&mut self) {
        self.size_alignment();
        let surface_texture = match self.surface.get_current_texture() {
            Ok(got) => got,
            Err(_) => {
                let config = self
                    .scene
                    .descriptor()
                    .render_texture
                    .compatible_surface_config();
                self.surface.configure(self.scene.device(), &config);
                self.surface
                    .get_current_texture()
                    .expect("Failed to acquire next surface texture!")
            }
        };
        let view = surface_texture
            .texture
            .create_view(&wgpu::TextureViewDescriptor::default());
        self.scene.render(&view);
        surface_texture.present();
    }
}