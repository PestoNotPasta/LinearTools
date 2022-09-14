#!/usr/bin/env python

import argparse
import io
from argparse import SUPPRESS
from contextlib import redirect_stderr
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
parser.add_argument('-o', '--overwrite', action='store_true')
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
        -o, --overwrite            Overwrite existing, converted reigon files
        --version                  Show the current version.
    """)
    exit(1)

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
    source = Path(args['source']).resolve()
    dest = Path(args['destination']).resolve()
    dest.mkdir(exist_ok=True)
    threads = args['threads']
    compression_level = args['compression']
    overwrite = args['overwrite']

    # Check if source path exists
    if not (source.exists()):
        print('The path could not be resolved. Please check the path and try again')
        exit(1)
    
    convert(region_format, source, dest, threads, compression_level, overwrite)