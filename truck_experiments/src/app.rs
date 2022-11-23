//! app.rs copied from https://github.com/ricosjp/truck-tutorial-code/blob/master/src/app.rs
//!
//! When I (Eli Dupree) copied this file on 2022-09-01, it didn't appear to have a license;
//! I inferred permission from the tutorial instructing me to copy this file verbatim
//! into my project, as follows:
//!
//! > Download the submodule app.rs, which is useful for generating the GUI, and copy it under src.
//! >
//! > app.rs provides an object-oriented GUI creation API that is reminiscent of the good old MFC. Although this module is useful, we have not crated it as a crate because there is room for optimization depending on the purpose of the application.
//! - https://ricos.gitlab.io/truck-tutorial/dev/first-window.html
//!
//! Then I modified it a bunch, because it was out of date.
//!
//! A GUI framework module providing MFC-like API.

use std::sync::{Arc, Mutex};
use std::time::*;
use truck_platform::{wgpu::*, DeviceHandler};
use winit::dpi::*;
use winit::event::*;
use winit::event_loop::ControlFlow;
use winit::window::Window;

/// The framework of applications with `winit`.
/// The main function of this file is the smallest usecase of this trait.
pub trait App: Sized + 'static {
    /// Initialize application
    /// # Arguments
    /// - handler: `DeviceHandler` provided by `wgpu`
    /// - info: informations of device and backend
    fn init(window: Arc<Window>, surface: Surface, device_handler: DeviceHandler) -> Self;
    /// By overriding this function, you can change the display of the title bar.
    /// It is not possible to change the window while it is running.
    fn app_title<'a>() -> Option<&'a str> { None }
    /// Default is `ControlFlow::WaitUntil(1 / 60 seconds)`.
    fn default_control_flow() -> ControlFlow {
        let next_frame_time = Instant::now() + Duration::from_nanos(16_666_667);
        ControlFlow::WaitUntil(next_frame_time)
    }
    /// By overriding this function, one can set the update process for each frame.
    fn update(&mut self) {}
    /// By overriding this function, one can set the rendering process for each frame.
    fn render(&mut self) {}
    /// By overriding this function, one can change the behavior when the window is resized.
    fn resized(&mut self, _size: PhysicalSize<u32>) -> ControlFlow { Self::default_control_flow() }
    /// By overriding this function, one can change the behavior when the window is moved.
    fn moved(&mut self, _position: PhysicalPosition<i32>) -> ControlFlow {
        Self::default_control_flow()
    }
    /// By overriding this function, one can change the behavior when the X button is pushed.
    fn closed_requested(&mut self) -> ControlFlow { ControlFlow::Exit }
    /// By overriding this function, one can change the behavior when the window is destoroyed.
    fn destroyed(&mut self) -> ControlFlow { Self::default_control_flow() }
    /// By overriding this function, one can change the behavior when a file is dropped to the window.
    fn dropped_file(&mut self, _path: std::path::PathBuf) -> ControlFlow {
        Self::default_control_flow()
    }
    /// By overriding this function, one can change the behavior when a file is hovered to the window.
    fn hovered_file(&mut self, _path: std::path::PathBuf) -> ControlFlow {
        Self::default_control_flow()
    }
    /// By overriding this function, one can change the behavior when a keybourd input occurs.
    fn keyboard_input(&mut self, _input: KeyboardInput, _is_synthetic: bool) -> ControlFlow {
        Self::default_control_flow()
    }
    /// By overriding this function, one can change the behavior when a mouse input occurs.
    fn mouse_input(&mut self, _state: ElementState, _button: MouseButton) -> ControlFlow {
        Self::default_control_flow()
    }
    /// By overriding this function, one can change the behavior when a mouse wheel input occurs.
    fn mouse_wheel(&mut self, _delta: MouseScrollDelta, _phase: TouchPhase) -> ControlFlow {
        Self::default_control_flow()
    }
    /// By overriding this function, one can change the behavior when the cursor is moved.
    fn cursor_moved(&mut self, _position: PhysicalPosition<f64>) -> ControlFlow {
        Self::default_control_flow()
    }
    /// Run the application.
    fn run() {
        let event_loop = winit::event_loop::EventLoop::new();
        let mut wb = winit::window::WindowBuilder::new();
        if let Some(title) = Self::app_title() {
            wb = wb.with_title(title);
        }
        let window = Arc::new(wb.build(&event_loop).unwrap());
        let instance = Instance::new(Backends::all());
        let surface = unsafe { instance.create_surface(&*window) };

        let (device, queue, adapter) = futures::executor::block_on(init_device(&instance, &surface));

        let device_handler = DeviceHandler::new(
            Arc::new(adapter),
            Arc::new(device),
            Arc::new(queue),
        );

        let mut app = Self::init(window.clone(), surface, device_handler);

        event_loop.run(move |ev, _, control_flow| {
            *control_flow = match ev {
                Event::MainEventsCleared => {
                    window.request_redraw();
                    Self::default_control_flow()
                }
                Event::RedrawRequested(_) => {
                    app.update();
                    // let frame = swap_chain
                    //     .get_current_frame()
                    //     .expect("Timeout when acquiring next swap chain texture");
                    app.render();
                    Self::default_control_flow()
                }
                Event::WindowEvent { event, .. } => match event {
                    WindowEvent::Resized(size) => {
                        // let mut sc_desc = handler.lock_sc_desc().unwrap();
                        // sc_desc.width = size.width;
                        // sc_desc.height = size.height;
                        // swap_chain = handler.device().create_swap_chain(&surface, &sc_desc);
                        Self::default_control_flow()
                    }
                    WindowEvent::Moved(position) => app.moved(position),
                    WindowEvent::CloseRequested => app.closed_requested(),
                    WindowEvent::Destroyed => app.destroyed(),
                    WindowEvent::DroppedFile(path) => app.dropped_file(path),
                    WindowEvent::HoveredFile(path) => app.hovered_file(path),
                    WindowEvent::KeyboardInput {
                        input,
                        is_synthetic,
                        ..
                    } => app.keyboard_input(input, is_synthetic),
                    WindowEvent::MouseInput { state, button, .. } => app.mouse_input(state, button),
                    WindowEvent::MouseWheel { delta, phase, .. } => app.mouse_wheel(delta, phase),
                    WindowEvent::CursorMoved { position, .. } => app.cursor_moved(position),
                    _ => Self::default_control_flow(),
                },
                _ => Self::default_control_flow(),
            };
        })
    }
}

async fn init_device(instance: &Instance, surface: &Surface) -> (Device, Queue, Adapter) {
    let adapter = instance
        .request_adapter(&RequestAdapterOptions {
            power_preference: PowerPreference::default(),
            force_fallback_adapter: false,
            compatible_surface: Some(surface),
        })
        .await
        .unwrap();

    let tuple = adapter
        .request_device(
            &DeviceDescriptor {
                label: Some("uhh -Eli"),
                features: Default::default(),
                limits: Limits::default(),
            },
            None,
        )
        .await
        .unwrap();
    (tuple.0, tuple.1, adapter)
}

