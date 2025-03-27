use std::ops::{Add, Mul, Sub};

pub mod data_interchange;

pub fn interpolate<Position, Delta, Output>(a: Position, b: Position, frac: f64) -> Output
where
    Position: Clone,
    Position: Sub<Position, Output = Delta>,
    Position: Add<Delta, Output = Output>,
    Delta: Mul<f64, Output = Delta>,
{
    let diff = b - a.clone();
    a + diff * frac
}

pub fn midpoint<Position, Delta, Output>(a: Position, b: Position) -> Output
where
    Position: Clone,
    Position: Sub<Position, Output = Delta>,
    Position: Add<Delta, Output = Output>,
    Delta: Mul<f64, Output = Delta>,
{
    interpolate(a, b, 0.5)
}
