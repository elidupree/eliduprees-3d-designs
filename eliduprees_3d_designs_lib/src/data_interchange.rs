pub trait Interchange {
    fn serialize_in_python() -> String;
    fn serialize_in_rust(input: &Self) -> String;
    fn deserialize_in_python() -> String;
    fn deserialize_in_rust(input: &str) -> Self;
}
