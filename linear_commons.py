#! /usr/bin/python3

import traceback
from os import path
from pathlib import Path

from psutil import cpu_count

from linear import *

DEFAULT_THREADS = cpu_count(logical=False)
DEFAULT_COMPRESSION_LEVEL = 6


def is_world_dir(source: Path) -> bool:
    'Returns True if the path given is a Minecraft world.'
    return source.isdir() and source.joinpath('level.dat').exists()


def is_region_file(source: Path) -> bool:
    'Returns True if the path given is a region file.'
    return source.is_file() and source.name.endswith('mca', 'linear')    

def convert_region(format: str, source: Path, destination: Path, threads: int = DEFAULT_THREADS, compression_level: int = DEFAULT_COMPRESSION_LEVEL):
    match format:
        case 'linear':    
            _mca_to_linear(source, destination) 
        case 'mca':
            _linear_to_mca(source, destination)
        case _:
            print('No handler exists for this region conversion')

def _mca_to_linear(source: Path, destination: Path, compression_level: int) -> bool: 
    '''
        Converts an anvil region to the linear format. Returns True 
        if the operation was successful, otherwise False.
    '''
    file_name = source.name
    dest_file = destination.joinpath(file_name.replace('mca', "linear"))    
    
    modif_time_dest = path.getmtime(dest_file)
    modif_time_source = path.getmtime(source)
    source_size = path.getsize(source)
    
    skip_conversion = dest_file.exists() and (modif_time_dest == modif_time_source)
    if skip_conversion or source_size == 0:
        return
        
    try:
        region = open_region_anvil(source)
        write_region_linear(dest_file, region, compression_level)
        destination_size = path.getsize(dest_file)
        compression_percentage = (100 * destination_size / source_size)
        print(f'{file_name} converted, compression {compression_percentage: .2f}')
        return True
        
    except Exception:
        traceback.print_exc()
        print("Error with region file", file_name)
        return False

def _linear_to_mca(filepath: str, outputDir: str) -> bool: 
    '''
        Converts an anvil region to the linear format. Returns True 
        if the operation was successful or the file alreadry exists, 
        otherwise False.
    '''
    return False
