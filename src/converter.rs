#![allow(unused)]
use core::time;
use std::path::Path;

const REGION_DIMENSION: u32 = 32;
const COMPRESSION_TYPE: u8 = b'\x02';
const COMPRESSION_TYPE_ZLIB: u8 = 2;
const EXTERNAL_FILE_COMPRESSION_TYPE: u8 = 130;
const LINEAR_SIGNATURE: i128 = 0xc3ff13183cca9d9a;
const SUPPORTED_VERSION: [u8; 2] = [1, 2];
const LINEAR_VERSION: u8 = 1;

struct RawChunk {}

struct Chunk {
    x: i32,
    z: i32,
    raw_chunk: RawChunk,
}

impl Chunk {
    fn new(x: i32, z: i32, raw_chunk: RawChunk) -> Chunk {
        Chunk { x, z, raw_chunk }
    }

    fn as_nbt(self: &Self) {}

    fn from_nbt() -> Chunk {}
}

struct Region {
    chunks: Vec<Chunk>,
    x: i32,
    z: i32,
    modified_time: u32,
    time_stamp: time::Duration,
}

impl Region {
    fn new(
        chunks: Vec<Chunk>,
        x: i32,
        z: i32,
        modified_time: u32,
        time_stamp: time::Duration,
    ) -> Region {
        Region {
            chunks,
            x,
            z,
            modified_time,
            time_stamp,
        }
    }
    fn chunk_count(self: &Self) -> u32 {
        return self.chunks.len() as u32;
    }
}

const HEADER_SIZE: u32 = REGION_DIMENSION * REGION_DIMENSION * 8;
struct LinearConverter;
struct McaConverter;

trait Converter {
    fn open_file(path: &Path);
    fn write_file(path: &Path);
    fn convert(path: &Path);
}

impl Converter for LinearConverter {
    fn convert(path: &Path) {
        
    }

    fn open_file(path: &Path) {
        
    }

    fn write_file(path: &Path) {}
}
