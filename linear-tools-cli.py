#!/usr/bin/env python

import argparse
import io
from argparse import SUPPRESS
from contextlib import redirect_stderr
from itertools import repeat
from multiprocessing import Pool
from pathlib import Path

from linear_commons import *

VERSION = '1.0.0'
prog = Path(__file__).name

parser = argparse.ArgumentParser(
    description='Convert Minecraft worlds to and from the linear format',
    add_help=False, 
    usage=SUPPRESS,
    argument_default=SUPPRESS
)

parser.add_argument('region-format', choices=['mca', 'linear'], default="linear")
parser.add_argument('-s', '--source', required=True)
parser.add_argument('-d', '--destination', default='')
parser.add_argument('-t', '--threads', default=DEFAULT_THREADS)
parser.add_argument('-c', '--compression', default=DEFAULT_COMPRESSION_LEVEL)
parser.add_argument('--version', action='version', version=f'LinearTools v{VERSION}')


def print_help():
    print(f"""
    {parser.description}

    Usage: 
        {prog} <mca|linear> [--path] [OPTIONS]

    Options:
        -s, --source               Path to world folder or region file.
        -d, --destination          The destination directory.
        -t, --threads              Number of threads to allocate.
        -c, --compression          Compression level to apply.
        --version                  Show the current version.
    """)
    exit(1)

def _handle_world(format: str, source: Path, destination: Path, threads: int, compression_level: int) -> None:
    format_from = 'linear' if format == 'mca' else 'mca'

    # Handle invalid destination directory
    if destination == Path('') or not (destination.is_dir() and destination.exists()):
        destination = source.joinpath('region')
    
    # Convert region files
    region_files = [f for f in source.joinpath('region').iterdir() if f.name.endswith(format_from)]
    with Pool(threads) as pool:
        pool.starmap(convert_region, zip(repeat(format), region_files, repeat(destination), repeat(threads), repeat(compression_level)))

def _handle_region(format: str, source: Path, destination: str, threads: int, compression_level: int) -> None:

    # Handle invalid destination directory
    if destination == Path('') or not (destination.is_file() and destination.exists()):
        destination = source.parent()
    
    convert_region(format, source, destination, threads, compression_level)

if __name__ == '__main__':
    args = {}
    dest = Path()

    # Handle any exceptions and exit
    try:
        f = io.StringIO()
        with redirect_stderr(f):
            args = vars(parser.parse_args())
    except:
        print_help()

    # Get arguments
    region_format = args['region-format']
    source = Path(args['source'])
    dest = Path(args['destination'])
    dest.mkdir(exist_ok=True)
    threads = args['threads']
    compression_level = args['compression-level']

    # Check if source path exists
    if not (source.exists()):
        print('The path could not be resolved. Please check the path and try again')
        exit(1)
    
    if is_region_file(source):
        _handle_region(region_format, source, dest, threads, compression_level)
    elif is_world_dir(source):
        _handle_world(region_format, source, dest, threads, compression_level)
    else:
        print('The path provided is neither a world directory or region file')