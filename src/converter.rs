#![allow(unused)]
use core::time;
use std::{
    convert, fs::{self, File}, io::{BufReader, Error, Read}, path::{Path, PathBuf}, u16
};

use zstd::stream::read;

const REGION_DIMENSION: usize = 32;
const COMPRESSION_TYPE: u8 = b'\x02';
const COMPRESSION_TYPE_ZLIB: u8 = 2;
const EXTERNAL_FILE_COMPRESSION_TYPE: u8 = 130;
const LINEAR_SIGNATURE: i128 = 0xc3ff13183cca9d9a;
const SUPPORTED_VERSION: [u8; 2] = [1, 2];
const LINEAR_VERSION: u8 = 1;

type RawChunk = Vec<u8>;

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

    fn from_nbt() -> Chunk {
        Chunk {
            x: 0,
            z: 0,
            raw_chunk: RawChunk,
        }
    }
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

const HEADER_SIZE: usize = REGION_DIMENSION * REGION_DIMENSION * 8;

pub struct LinearConverter;
pub struct AnvilConverter;

trait Converter {
    fn open_region_file(&self, path: &PathBuf) -> Result<Region, Error>;

    fn extract_region_coords(&self, path: &PathBuf) -> Option<(i32, i32)> {
        let file_name = path.file_name()?.to_str()?;
        let tokens: Vec<&str> = file_name.split(".").collect();
        if tokens.len() != 4 {
            return None;
        }

        match (tokens[1].parse::<i32>(), tokens[2].parse::<i32>()) {
            (Ok(region_x), Ok(region_z)) => Some((region_x, region_z)),
            _ => None
        }
    }
}

impl Converter for AnvilConverter {
    fn open_region_file(&self, path: &PathBuf) -> Result<Region, Error> {
        const SECTOR: u8 = 4096;
        const REGION_SIZE: usize = REGION_DIMENSION * REGION_DIMENSION;

        let chunks_starts: Vec<Chunk> = Vec::with_capacity(REGION_SIZE);
        let chunks_list: Vec<Chunk> = Vec::with_capacity(REGION_SIZE);
        let chunks_size: Vec<Chunk> = Vec::with_capacity(REGION_SIZE);
        let timestamps: Vec<Chunk> = Vec::with_capacity(REGION_SIZE);
        
        let source_folder = path.parent().unwrap();
        let (region_x, region_z) = self.extract_region_coords(path).expect("Could not extract region coordinates");
        let modified_time = fs::metadata(path)?.modified()?;
        
        let file = File::open(path)?;
        let mut reader = BufReader::new(file);
        let mut buffer = Vec::new();
        reader.read_to_end(&mut buffer)?;
        

        for _ in 0..REGION_SIZE {
            
        }
        


        Ok(Region { chunks: chunks_list, x: region_x, z: region_z, modified_time: todo!(), time_stamp:  todo!() })
    }
}
