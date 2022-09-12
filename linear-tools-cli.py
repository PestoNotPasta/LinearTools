#! /usr/bin/python3

import argparse
import io
import os
import os.path as path
from argparse import SUPPRESS
from contextlib import redirect_stderr
from pathlib import Path
from linear_commons import *

VERSION = '1.0.0'
prog = Path(__file__).name

def print_help():
    print(f"""
    {parser.description}

    Usage: 
        {prog} <mca|linear> [--path] [OPTIONS]

    Options:
        -h, --help                 Show this help message.
        -p, --path                 File path to the world folder.
        -t, --threads              Number of threads to allocate.
        -v, --verbose              The level of verbosity.
        -c, --compression-level    Compression level to apply.
        -o, --output               The output directory.
        --version                  Show the current version.
    """)
    exit(1)

parser = argparse.ArgumentParser(
    description='Convert Minecraft worlds to and from the linear format',
    add_help=False, 
    usage=SUPPRESS,
    argument_default=SUPPRESS
)

parser.add_argument('region-format', choices=['mca', 'linear'], default="linear")
parser.add_argument('-h', '--help')
parser.add_argument('-p', '--path', required=True)
parser.add_argument('-t', '--threads', default=4)
parser.add_argument('-c', '--compression-level', default=6)
parser.add_argument('-o', '--output')
parser.add_argument('-v', '--verbose', action='count')
parser.add_argument('--version', action='version', version=f'LinearTools v{VERSION}')

if __name__ == '__main__':
    args = {}

    # Handle any exceptions
    try:
        f = io.StringIO()
        with redirect_stderr(f):
            args = vars(parser.parse_args())
    except:
        print_help()

    region_format = args['region-format']
    world = args['path']
    output=args['output']

    # Check if path exists
    if not is_world(world):
        print('The path could not be resolved. Please check the path and try again')
        exit()

    # Check if an output is provided
    if args['output'] == None:
        out = path.join(path, 'region')
        os.mkdir(out, exist_ok=True)