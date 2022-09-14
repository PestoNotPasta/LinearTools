from time import sleep
import traceback
from itertools import repeat
from os import path
from pathlib import Path
from textwrap import dedent
from turtle import position

import psutil
from p_tqdm import p_map

from linear import *

DEFAULT_THREADS = psutil.cpu_count(logical=False)
DEFAULT_COMPRESSION_LEVEL = 6

def is_world_dir(source: Path) -> bool:
    'Returns True if the path given is a Minecraft world.'
    return source.is_dir() and source.joinpath('level.dat').exists()
def is_region_file(source: Path) -> bool:
    'Returns True if the path given is a region file.'
    return source.is_file() and source.name.endswith(('mca', 'linear'))    

def convert(region_format: str, source: Path, destination: Path, threads: int, compression_level: int, overwrite: bool):
    use_multiprocessing = is_world_dir(source)
    
    def func(args):
        return _mca_to_linear(*args) if region_format == 'linear' else _linear_to_mca(*args)

    # Handles an invalid destination directory
    if destination == Path('') or not (destination.is_dir() and destination.exists()):        
        
        # Check if world is overworld, nethher or end
        if use_multiprocessing: 
            possible_paths = ['region', 'DIM1/region', 'DIM1/region']
            for path in possible_paths:
                new_dest = destination.joinpath(path)
                if new_dest.exists() and new_dest.is_dir():
                    destination = new_dest
                    break

            # If none of the possible paths exist then the
            # region folder is missing.
            raise Exception('Could not find the region folder. Please check your world folder and try again')
        else:
            destination = source.parent

    # Convert                         
    if is_region_file(source):
        args = [source, destination, compression_level, overwrite]
        print(f'\nConverting region file {source.name} to {region_format}...\n')
        if func(args):
            print('Completed sucessfully\n')
        else: 
            print('An unknown error occured')

    elif use_multiprocessing:
        format_from = 'linear' if region_format == 'mca' else 'mca'
        region_files = [f for f in source.joinpath('region').iterdir() if f.name.endswith(format_from)]
        region_files.sort()

        # Create list of args for multiprocessing 
        args = list(zip(region_files, repeat(destination), repeat(compression_level), repeat(overwrite)))

        # Process jobs and display progress bar
        print(f'\nConverting world \'{source.name}\' [{format_from} -> {region_format}]\n')
        p_map(func, args, 
            num_cpus=threads, 
            ncols=80, 
            desc='  > Converting',
            bar_format='{l_bar}{bar:35}| {n_fmt}/{total_fmt}, [{elapsed}]' 
        )
        sleep(1)
        print('\nDone...')
        sleep(0.5)
        # Print additional statistics for linear
        if region_format == 'linear':
            source_size = sum(f.stat().st_size for f in region_files)
            dest_size = sum(f.stat().st_size for f in os.scandir(destination))
            percentage = (100 * dest_size / source_size) 
            output = dedent(f'''
                ----------------------------------
                [#] Statistics:
                ----------------------------------
                Total region size (anvil): {_format_bytes(source_size)}
                Total region size (linear): {_format_bytes(dest_size)}
                Compression achieved: {percentage: .2f}%
                ''')

            print(output)
        # with Pool(threads) as pool:
        #     with tqdm(total=len(args)) as pbar:
        #         result = pool.imap(func, args)
        #         for _ in result:
        #             if any(map(lambda x: isinstance(x, KeyboardInterrupt), result)):
        #                 print('Ctrl-C was entered.')
        #                 pool.close()
        #                 pool.join()
        #             pbar.update()
            
        # result = list(tqdm(pool.imap(func, list(args)), total=len(region_files))) 

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
            return True

    try:
        region = open_region_anvil(source)
        write_region_linear(dest_file, region, compression_level)
        # destination_size = path.getsize(dest_file)
        # compression_percentage = (100 * destination_size / source_size)
        return True
        
    except Exception:
        traceback.print_exc()
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
            return
        
    try:
        region = open_region_anvil(source)
        write_region_linear(dest_file, region, compression_level)
        # destination_size = path.getsize(dest_file)
        # compression_percentage = (100 * destination_size / source_size)
        return True
        
    except Exception:
        traceback.print_exc()
        print('Error with region file', file_name)
        return False

def _format_bytes(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

