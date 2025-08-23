extern crate bendy;

use bendy::decoding::FromBencode;
use bendy::encoding::{SingleItemEncoder, ToBencode};
use std::collections::BTreeMap;
use std::sync::Arc;

pub const HASH_ID_BYTE_LENGTH: usize = 16;
pub const HASH_ID_BENCODE_BYTE_LENGTH: usize = HASH_ID_BYTE_LENGTH + "16:".len();
pub const SIPHASH_KEY: [u8; 16] =
    const_hex::const_decode_to_array(b"78ca81054e1df045447cd7d48958de7d").unwrap();

pub type ByteString = Vec<u8>;
pub enum BencodeValue {
    ByteString(ByteString),
    List(Vec<BencodeValue>),
    Map(BTreeMap<ByteString, BencodeValue>),
}

pub struct SerializedBencode {
    pub data: ByteString,
}

enum CaReferents {
    ByteString,
    List(Vec<ArcIntern<Ca>>),
    Map(BTreeMap<ArcIntern<Ca>, ArcIntern<Ca>>),
}

struct CaCaches {
    raw_form: BencodeValue,
    id_raw: BencodeValue,
    serialized: SerializedBencode,
    id_serialized: ArrayVec<u8, HASH_ID_BENCODE_BYTE_LENGTH>,
}
pub struct Ca {
    caches: CaCaches,
    referents: CaReferents,
}

impl ToBencode for BencodeValue {
    const MAX_DEPTH: usize = 2048;

    fn encode(&self, encoder: SingleItemEncoder) -> Result<(), bendy::encoding::Error> {
        match self {
            BencodeValue::ByteString(bytes) => encoder.emit(&bendy::encoding::AsString(bytes)),
            BencodeValue::List(list) => encoder.emit(list),
            BencodeValue::Map(map) => encoder.emit(map),
        }
    }
}

impl FromBencode for BencodeValue {
    fn decode_bencode_object(
        object: bendy::decoding::Object,
    ) -> Result<Self, bendy::decoding::Error>
    where
        Self: Sized,
    {
        use bendy::decoding::Object::*;
        match &object {
            List(_) => Ok(BencodeValue::List(Vec::<_>::decode_bencode_object(object)?)),
            Dict(_) => Ok(BencodeValue::Map(BTreeMap::<_, _>::decode_bencode_object(
                object,
            )?)),
            Integer(_) => bendy::decoding::Error::unexpected_token(
                "an EliDuprees-3D-designs-value",
                "a bencode integer",
            ),
            Bytes(bytes) => Ok(BencodeValue::ByteString(bytes.to_vec())),
        }
    }
}

impl BencodeValue {
    pub fn serialize(&self) -> SerializedBencode {
        SerializedBencode {
            data: self.to_bencode().unwrap(),
        }
    }
}
impl SerializedBencode {
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
        let serialized = raw_form.serialize();
        let id_raw = if serialized.needs_indirection() {
            BencodeValue::ByteString(serialized.canonical_hash().to_vec())
        } else {
            raw_form.clone()
        };
        let id_serialized = id_raw.serialize();
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
        self.serialized.needs_indirection()
    }
    pub fn new_byte_string(bytes: ByteString) -> ArcIntern<Ca> {
        ArcIntern::new(Ca {
            caches: CaCaches::from_raw(BencodeValue::ByteString(bytes)),
            referents: CaReferents::ByteString,
        })
    }
    pub fn new_list(elements: Vec<ArcIntern<Ca>>) -> ArcIntern<Ca> {
        ArcIntern::new(Ca {
            caches: CaCaches::from_raw(BencodeValue::List(
                elements.iter().map(|ca| ca.caches.id_raw.clone()).collect(),
            )),
            referents: CaReferents::List(elements),
        })
    }
    pub fn new_map(items: BTreeMap<ArcIntern<Ca>, ArcIntern<Ca>>) -> ArcIntern<Ca> {
        ArcIntern::new(Ca {
            caches: CaCaches::from_raw(BencodeValue::Map(
                items
                    .iter()
                    .map(|(k, v)| {
                        (
                            BencodeValue::ByteString(k.id_serialized().data.clone()),
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
    pub fn id_serialized(&self) -> &ArrayVec<u8, HASH_ID_BENCODE_BYTE_LENGTH> {
        &self.caches.id_serialized
    }
}

#[cfg(test)]
mod tests {
    use super::*;
}
