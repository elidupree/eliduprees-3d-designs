extern crate const_hex;

use bendy::decoding::FromBencode;
use bendy::encoding::ToBencode;
use std::borrow::Cow;
use std::cmp::Ordering;
use std::collections::BTreeMap;
use std::hash::{Hash, Hasher};
use std::sync::Arc;

pub const HASH_ID_BYTE_LENGTH: usize = 16;
pub const HASH_ID_BENCODE_BYTE_LENGTH: usize = HASH_ID_BYTE_LENGTH + "16:".len();
pub const SIPHASH_KEY: [u8; 16] =
    match const_hex::const_decode_to_array(b"78ca81054e1df045447cd7d48958de7d") {
        Ok(b) => b,
        Err(_) => unreachable!(),
    };

pub type ByteString = Vec<u8>;
pub type BencodeValue = bendy::value::Value<'static>;

#[derive(Clone, Ord, PartialOrd, Eq, PartialEq, Hash, Debug)]
pub struct SerializedBencode {
    pub data: ByteString,
}

enum CaReferents {
    ByteString,
    List(Vec<Arc<Ca>>),
    Map(BTreeMap<Arc<Ca>, Arc<Ca>>),
}

struct CaCaches {
    raw_form: BencodeValue,
    id_raw: BencodeValue,
    serialized: SerializedBencode,
    id_serialized: SerializedBencode,
}
pub struct Ca {
    caches: CaCaches,
    referents: CaReferents,
}

impl SerializedBencode {
    pub fn from_bencode_value(value: &BencodeValue) -> SerializedBencode {
        SerializedBencode {
            data: value.to_bencode().unwrap(),
        }
    }
    pub fn deserialize(&self) -> BencodeValue {
        BencodeValue::from_bencode(&self.data).unwrap()
    }
    pub fn needs_indirection(&self) -> bool {
        self.data.len() >= HASH_ID_BENCODE_BYTE_LENGTH
    }
    fn canonical_hash(&self) -> [u8; 16] {
        let hasher = siphasher::sip128::SipHasher24::new_with_key(&SIPHASH_KEY);
        hasher.hash(&self.data).as_bytes()
    }
}
impl CaCaches {
    pub fn from_raw(raw_form: BencodeValue) -> CaCaches {
        let serialized = SerializedBencode::from_bencode_value(&raw_form);
        let id_raw = if serialized.needs_indirection() {
            BencodeValue::Bytes(Cow::Owned(serialized.canonical_hash().to_vec()))
        } else {
            raw_form.clone()
        };
        let id_serialized = SerializedBencode::from_bencode_value(&id_raw);
        CaCaches {
            raw_form,
            id_raw,
            serialized,
            id_serialized,
        }
    }
}
impl Ca {
    pub fn needs_indirection(&self) -> bool {
        self.serialized().needs_indirection()
    }
    pub fn new_byte_string(bytes: ByteString) -> Arc<Ca> {
        Arc::new(Ca {
            caches: CaCaches::from_raw(BencodeValue::Bytes(bytes.into())),
            referents: CaReferents::ByteString,
        })
    }
    pub fn new_list(elements: Vec<Arc<Ca>>) -> Arc<Ca> {
        Arc::new(Ca {
            caches: CaCaches::from_raw(BencodeValue::List(
                elements.iter().map(|ca| ca.caches.id_raw.clone()).collect(),
            )),
            referents: CaReferents::List(elements),
        })
    }
    pub fn new_map(items: BTreeMap<Arc<Ca>, Arc<Ca>>) -> Arc<Ca> {
        Arc::new(Ca {
            caches: CaCaches::from_raw(BencodeValue::Dict(
                items
                    .iter()
                    .map(|(k, v)| {
                        (
                            Cow::Owned(k.id_serialized().data.clone()),
                            v.id_raw().clone(),
                        )
                    })
                    .collect(),
            )),
            referents: CaReferents::Map(items),
        })
    }
    pub fn raw_form(&self) -> &BencodeValue {
        &self.caches.raw_form
    }
    pub fn serialized(&self) -> &SerializedBencode {
        &self.caches.serialized
    }
    pub fn id_raw(&self) -> &BencodeValue {
        &self.caches.id_raw
    }
    pub fn id_serialized(&self) -> &SerializedBencode {
        &self.caches.id_serialized
    }
}

impl PartialEq for Ca {
    fn eq(&self, other: &Self) -> bool {
        self.caches.id_serialized == other.caches.id_serialized
    }
}
impl Eq for Ca {}
impl PartialOrd for Ca {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        self.caches
            .id_serialized
            .partial_cmp(&other.caches.id_serialized)
    }
}
impl Ord for Ca {
    fn cmp(&self, other: &Self) -> Ordering {
        self.caches.id_serialized.cmp(&other.caches.id_serialized)
    }
}
impl Hash for Ca {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.caches.id_serialized.hash(state)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
}
