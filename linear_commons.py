import traceback
from itertools import repeat
from multiprocessing import Pool
from os import path
from pathlib import Path
from psutil import cpu_count
from linear import *

DEFAULT_THREADS = cpu_count(logical=False)
DEFAULT_COMPRESSION_LEVEL = 6

def is_world_dir(source: Path) -> bool:
    'Returns True if the path given is a Minecraft world.'
    return source.is_dir() and source.joinpath('level.dat').exists()

def is_region_file(source: Path) -> bool:
    'Returns True if the path given is a region file.'
    return source.is_file() and source.name.endswith(('mca', 'linear'))    

def convert(region_format: str, source: Path, destination: Path, threads: int, compression_level: int, overwrite: bool):
    use_multiprocessing = is_world_dir(source)
    func = _mca_to_linear if region_format == 'linear' else _linear_to_mca

    # Handles and invalid destination directory
    if destination == Path('') or not (destination.is_dir() and destination.exists()):
        destination = source.joinpath('region') if use_multiprocessing else source.parent
    
    if is_region_file(source):
        func(source, destination, compression_level, overwrite)

    elif use_multiprocessing:
        format_from = 'linear' if region_format == 'mca' else 'mca'
        region_files = [f for f in source.joinpath('region').iterdir() if f.name.endswith(format_from)]
        with Pool(threads) as pool:
            pool.starmap(func, zip(
                    repeat(region_format), 
                    region_files, 
                    repeat(destination), 
                    repeat(threads), 
                    repeat(compression_level), 
                    repeat(overwrite)
                )
            )

def _mca_to_linear(source: Path, destination: Path, compression_level: int, overwrite: bool) -> bool: 
    '''
        Converts an anvil region to the linear format. Returns True 
        if the operation was successful, otherwise False.
    '''
    file_name = source.name
    dest_file = destination.joinpath(file_name.replace('mca', 'linear'))    
    source_size = path.getsize(source)
    
    if overwrite:
        dest_file.unlink(missing_ok=True)
    
    if dest_file.exists():
        modif_time_dest = path.getmtime(dest_file)
        modif_time_source = path.getmtime(source)
        
        skip_conversion = modif_time_dest == modif_time_source or source_size == 0
        if skip_conversion:
            print(f'The region \'{dest_file.name}\' already exists. Skipping conversion...')
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
        print('Error with region file', file_name)
        return False

def _linear_to_mca(source: Path, destination: Path, compression_level: int, overwrite: bool) -> bool: 
    '''
        Converts a linear region to the anvil format. Returns True 
        if the operation was successful, otherwise False.
    '''
    file_name = source.name
    dest_file = destination.joinpath(file_name.replace('linear', 'mca'))    
    source_size = path.getsize(source)

    if overwrite:
        dest_file.unlink(missing_ok=True)
    
    if dest_file.exists():
        modif_time_dest = path.getmtime(dest_file)
        modif_time_source = path.getmtime(source)
        
        skip_conversion = modif_time_dest == modif_time_source or source_size == 0
        if skip_conversion:
            print(f'The region \'{dest_file.name}\' already exists. Skipping conversion...')
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
        print('Error with region file', file_name)
        return False
