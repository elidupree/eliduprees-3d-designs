/// The general design here is that the Ca forms are the "source of truth",
/// and typed forms are cached, type-system-friendly representations for good coding and optimization.
/// So we define traits to generate the typed representations as (intended-to-be-)pure functions of the Ca forms.
use crate::content_addressed_bencode::{ByteString, Ca, CaMap, CaReferents};
use failure::{bail, Error};
use std::any::{Any, TypeId};
use std::collections::HashMap;
use std::convert::TryInto;
use std::ops::Deref;
use std::sync::Arc;

#[allow(unused_variables)]
pub trait FromCa: Sized + Any + Send + Sync {
    fn from_byte_string(bytes: &[u8]) -> Result<Self, Error> {
        bail!(
            "Type {} doesn't implement FromCa::from_byte_string",
            std::any::type_name::<Self>()
        )
    }
    fn from_list(elements: &[Arc<Ca>], typer: &mut Typer) -> Result<Self, Error> {
        bail!(
            "Type {} doesn't implement FromCa::from_list",
            std::any::type_name::<Self>()
        )
    }
    fn from_map(items: &CaMap, typer: &mut Typer) -> Result<Self, Error> {
        bail!(
            "Type {} doesn't implement FromCa::from_map",
            std::any::type_name::<Self>()
        )
    }
}

pub struct TypedCa<T> {
    typed: T,
    erased: Arc<Ca>,
}
impl<T> Deref for TypedCa<T> {
    type Target = T;
    fn deref(&self) -> &Self::Target {
        &self.typed
    }
}
impl<T> TypedCa<T> {
    pub fn erased(&self) -> &Arc<Ca> {
        &self.erased
    }
}

pub trait ToCaByteString: Sized + Any + Send + Sync {
    fn to_byte_string(&self) -> ByteString;
}

impl<T: ToCaByteString> From<T> for TypedCa<T> {
    fn from(typed: T) -> Self {
        let erased = Ca::new_byte_string(typed.to_byte_string());
        TypedCa { typed, erased }
    }
}

// like Deserializer
pub struct Typer {
    in_progress_marker: Arc<dyn Any + Send + Sync>,
    values: HashMap<(TypeId, ByteString), Arc<dyn Any + Send + Sync>>,
}

impl Typer {
    pub fn new() -> Self {
        Typer {
            in_progress_marker: Arc::new(()),
            values: HashMap::new(),
        }
    }
    pub fn type_as<T: FromCa>(&mut self, ca: &Ca) -> Result<Arc<T>, Error> {
        let key = (TypeId::of::<T>(), ca.id_serialized().data.clone());
        if let Some(erased) = self.values.get(&key) {
            if Arc::ptr_eq(erased, &self.in_progress_marker) {
                panic!("Self-reference in a FromCa impl")
            }
            return Ok(Arc::downcast(erased.clone()).unwrap());
        }
        self.values
            .insert(key.clone(), self.in_progress_marker.clone());
        let value = Arc::new(match (ca.referents(), ca.raw_form()) {
            (CaReferents::ByteString, bendy::value::Value::Bytes(b)) => T::from_byte_string(&b)?,
            (CaReferents::List(l), _) => T::from_list(l, self)?,
            (CaReferents::Map(m), _) => T::from_map(m, self)?,
            _ => unreachable!(),
        });
        self.values.insert(key, value.clone());
        Ok(value)
    }
}

macro_rules! ca_le_bytes_primitives {
    ($($t:ty)*) => {
        $(
        impl FromCa for $t {
            fn from_byte_string(bytes: &[u8]) -> Result<Self, Error> {
                Ok(<$t>::from_le_bytes(bytes.try_into()?))
            }
        }
        impl ToCaByteString for $t {
            fn to_byte_string(&self) -> ByteString {
                self.to_le_bytes().to_vec()
            }
        }
        )*
    };
}

ca_le_bytes_primitives!(f32 f64 i8 i16 i32 i64 i128 u8 u16 u32 u64 u128);
