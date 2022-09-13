import os
from pathlib import Path
import struct
from typing import Literal
import pyzstd
import zlib
import xxhash
from objects.chunk import Chunk
from objects.region import Region

REGION_DIMENSION = 32
COMPRESSION_TYPE = b'\x02'
COMPRESSION_TYPE_ZLIB = 2
EXTERNAL_FILE_COMPRESSION_TYPE = 128 + 2
LINEAR_SIGNATURE = 0xc3ff13183cca9d9a
LINEAR_VERSION = 1

def open_region_linear(file_path):
    HEADER_SIZE = REGION_DIMENSION * REGION_DIMENSION * 8

    file_coords = file_path.split('/')[-1].split('.')[1:3]
    region_x, region_z = int(file_coords[0]), int(file_coords[1])

    raw_region = open(file_path, 'rb').read()
    mtime = os.path.getmtime(file_path)

    signature, version, newest_timestamp, compression_level, chunk_count, complete_region_length, hash64 = struct.unpack_from(">QBQbhIQ", raw_region, 0)

    if signature != LINEAR_SIGNATURE:
        raise Exception("Superblock invalid")
    if version != LINEAR_VERSION:
        raise Exception("Version invalid")

    signature = struct.unpack(">Q", raw_region[-8:])[0]

    if signature != LINEAR_SIGNATURE:
        raise Exception("Footer signature invalid")

    decompressed_region = pyzstd.decompress(raw_region[32:-8])

    sizes = []
    timestamps = []

    real_chunk_count = 0
    total_size = 0
    for i in range(REGION_DIMENSION * REGION_DIMENSION):
        size, timestamp = struct.unpack_from(">II", decompressed_region, i * 8)
        total_size += size
        if size != 0: real_chunk_count += 1
        sizes.append(size)
        timestamps.append(timestamp)

    if total_size + HEADER_SIZE != len(decompressed_region):
        raise Exception("Decompressed size invalid")

    if real_chunk_count != chunk_count:
        raise Exception("Chunk count invalid")

    chunks = [None] * REGION_DIMENSION * REGION_DIMENSION

    iter = HEADER_SIZE
    for i in range(REGION_DIMENSION * REGION_DIMENSION):
        if sizes[i] > 0:
            
            x = REGION_DIMENSION * region_x + i % 32
            z = REGION_DIMENSION * region_z + i // 32
            chunks[i] = Chunk(decompressed_region[iter: iter + sizes[i]], x, z)
        iter += sizes[i]

    return Region(chunks, region_x, region_z, mtime, timestamps)

def quickly_verify_linear(file_path):
    try:
        with open(file_path, 'rb') as f:
            raw_region = f.read()
    except FileNotFoundError: 
        return False

    signature = struct.unpack_from(">QBQbhIQ", raw_region, 0)[0]
    if signature != LINEAR_SIGNATURE or signature != LINEAR_VERSION:
        return False

    signature = struct.unpack(">Q", raw_region[-8:])[0]
    if signature != LINEAR_SIGNATURE:
        return False
        
    return True

def write_region_linear(destination_filename: Path, region: Region, compression_level=1):
    inside_header = []
    newest_timestamp = 0
    chunk_count = 0

    for i in range(32**2):
        if region.chunks[i] != None:
            inside_header.append(struct.pack(">II", len(region.chunks[i].raw_chunk), region.timestamps[i]))
            newest_timestamp = max(region.timestamps[i], newest_timestamp)
            chunk_count += 1
        else:
            inside_header.append(b"\x00" * 8)

    chunks = []

    for i in range(32**2):
        if region.chunks[i] != None:
            chunks.append(region.chunks[i].raw_chunk)
        else:
            chunks.append(b"")

    complete_region = b''.join(inside_header) + b''.join(chunks)
    complete_region_hash = xxhash.xxh64(complete_region).digest()

    option = {pyzstd.CParameter.compressionLevel : compression_level,
                pyzstd.CParameter.checksumFlag : 1}
    complete_region = pyzstd.compress(complete_region, level_or_option=option)

    preheader = struct.pack(">QBQbhI", LINEAR_SIGNATURE, LINEAR_VERSION, newest_timestamp, compression_level, chunk_count, len(complete_region))
    footer = struct.pack(">Q", LINEAR_SIGNATURE)

    final_region_file = preheader + complete_region_hash + complete_region + footer

    with open(destination_filename + ".wip", "wb") as f:
        f.write(final_region_file)

    os.utime(destination_filename + ".wip", (region.mtime, region.mtime))
    os.rename(destination_filename + ".wip", destination_filename)

def open_region_anvil(file_path: Path):
    SECTOR = 4096

    chunk_starts = []
    chunk_sizes = []
    timestamps = []
    chunks = []

    coords = file_path.name.split('.')[1:3]
    region_x, region_z = int(coords[0]), int(coords[1])

    mtime = os.path.getmtime(file_path)
    with open(file_path, 'rb') as f:
        anvil_file = f.read()

    source_folder = file_path.parent()

    for i in range(REGION_DIMENSION * REGION_DIMENSION):
        a, b, c, sector_count = struct.unpack_from(">BBBB", anvil_file, i * 4)
        chunk_starts.append(c + b * 256 + a * 256 * 256)
        chunk_sizes.append(sector_count)

    for i in range(REGION_DIMENSION * REGION_DIMENSION):
        timestamps.append(struct.unpack_from(">I", anvil_file, SECTOR + i * 4)[0])

    chunk = None
    for i in range(REGION_DIMENSION * REGION_DIMENSION):
        if chunk_starts[i] > 0 and chunk_sizes[i] > 0:
            whole_raw_chunk = anvil_file[SECTOR * chunk_starts[i]:SECTOR * (chunk_starts[i] + chunk_sizes[i])]
            chunk_size, compression_type = struct.unpack_from(">IB", whole_raw_chunk, 0)
            
            x = REGION_DIMENSION * region_x + i % 32
            z = REGION_DIMENSION * region_z + i // 32

            match compression_type:
                
                case zlib.COMPRESSION_TYPE_ZLIB:
                    chunk = Chunk(zlib.decompress(whole_raw_chunk[5:5 + chunk_size]), x, z)
                    chunks.append(chunk)
                
                case zlib.EXTERNAL_FILE_COMPRESSION_TYPE:
                    with open(source_folder + f"/c.{x}.{z}.mcc", "rb"):
                        external_file = f.read()
                    chunk = Chunk(zlib.decompress(external_file), x, z)
                    chunks.append(chunk)
                case _:
                    raise Exception(f"Compression type {compression_type} unimplemented!")
        else:
            chunks.append(None)

    return Region(chunks, region_x, region_z, mtime, timestamps)


def write_region_anvil(destination_filename, region: Region, compression_level=zlib.Z_DEFAULT_COMPRESSION):
    SECTOR = 4096

    destination_folder = destination_filename.rpartition("/")[0]
    header_chunks = []
    header_timestamps = []
    sectors = []
    start_sectors = []
    free_sector = 2

    for i in range(REGION_DIMENSION * REGION_DIMENSION):
        start_sectors.append(free_sector)
        if region.chunks[i] != None:
            compressed = zlib.compress(region.chunks[i].raw_chunk, compression_level)
            final_chunk_data = struct.pack(">I", len(compressed) + 1) + COMPRESSION_TYPE + compressed

            padding = 4096 - (len(final_chunk_data) % 4096)
            if padding == 4096:
                padding = 0
            final_chunk_data += b'\x00' * padding

            sector_count = len(final_chunk_data) // 4096
            if sector_count > 255:
                x, z = i % 32, i // 32
                print("Chunk in external file", region.region_x * 32 + x, region.region_z * 32 + z)
                chunk_file_path = destination_folder + "/c.%d.%d.mcc" % (region.region_x * 32 + x, region.region_z * 32 + z)
                open(chunk_file_path + ".wip", "wb").write(compressed)
                os.utime(chunk_file_path + ".wip", (region.mtime, region.mtime))
                os.rename(chunk_file_path + ".wip", chunk_file_path)

                final_chunk_data = struct.pack(">IB", 1, EXTERNAL_FILE_COMPRESSION_TYPE)
                sector_count = 1
                padding = 4096 - (len(final_chunk_data) % 4096)
                if padding == 4096:
                    padding = 0
                final_chunk_data += b'\x00' * padding
            sectors.append(final_chunk_data)
            free_sector += sector_count
        else:
            sectors.append(b'')

    for i in range(REGION_DIMENSION * REGION_DIMENSION):
        if region.chunks[i] != None:
            sector_count = len(sectors[i]) // 4096
            header_chunks.append(struct.pack(">IB", start_sectors[i], sector_count)[1:])
        else:
            header_chunks.append(b"\x00\x00\x00\x00")

    for i in range(REGION_DIMENSION * REGION_DIMENSION):
        header_timestamps.append(struct.pack(">I", region.timestamps[i]))

    open(destination_filename + ".wip", "wb").write(b''.join(header_chunks) + b''.join(header_timestamps) + b''.join(sectors))
    os.utime(destination_filename + ".wip", (region.mtime, region.mtime))
    os.rename(destination_filename + ".wip", destination_filename)