# Linear region file format for Minecraft

Linear region format saves about 50% of disk space in the Overworld and Nether and 95% in The End.

This repository hosts tools to convert to and from `.mca` and `.linear`.

#### TODO:
- Display progress bar and improve output
- Add option to delete old region files
- Add key interrupt handler to stop conversion
- GUI conversion tool (using PyQt5) 
- Unit tests

## Features:
- Saves about 50% of space when compared to Anvil
- Reads and writes whole files, so it will actually be _faster_ than `.mca` on a spinning HDD (way less IOPS than `.mca`)
- Replaces symlinks with files, thus allows caching on HDD
- Uses slightly more memory than Anvil - it has to store the whole region file in memory for individual chunk access
- Much simpler format - about 300 lines of code vs about 1000 LoC for Anvil

## How:
There are three problems with the default Minecraft region file format (Anvil):
- Each chunk is compressed individually
- Anvil uses a very outdated compression algorithm (zlib)
- Each chunk is padded to 4096 bytes

Linear compresses a whole region file at once, achieving superior compression ratio.

It also gets rid of `.mcc` files for chunks bigger than 1MB as it's a stupid, unnecessary kludge. The total limit for whole region file is 4GB.

### Individual compression of chunks:
The fact that each chunk is stored individually in Anvil means that compression doesn't have the opportunity to "learn" the surrounding data.

Thus, the compression ratio is extremely small.

Linear region file solves that problem by writing the whole 32 x 32 (512) chunk region as a single compression stream.

### zlib vs zstd:

zlib is extremely old, slow and offers way worse compression ratio than zstd. [Check the official Github](https://github.com/facebook/zstd) for benchmarks - 5 times the difference in compression/decompression speed.

Zstd also offers slightly better compression ratio, despite the fact that Facebook claims it's similar to zlib.

### Padding to 4096 bytes:

Anvil pads every chunk to 4096. So if your compressed chunk ends up being just 5000 bytes... It will take 4096 * 2 on disk, filling the empty space with zeroes.

This leads to the wasting of (on average) 1MB per full 32 x 32 region file.

It's most obvious in The End where chunks are tiny.

## Stability:

It's been running on Endcrystal.me (3TB world) since November 2021 without issues. I personally consider it stable, I found no region-file specific issues.

Plugins should be 99.99% compatible, except for the occasional strange plugin that absolutely _has to_ open the `.mca` by itself.

All plugins that use NMS or Bukkit (ex. Chunky) will work.

## Supported software:

[LinearPaper](https://github.com/xymb-endcrystalme/LinearPaper) - Linear-enabled version of Paper. No further changes, 100% compatible with Paper. Precompiled binaries included.


[LinearPurpur](https://github.com/xymb-endcrystalme/LinearPurpur) - Linear-enabled version of Purpur. No further changes, 100% compatible with Purpur. Precompiled binaries included.


[LinearMultiPaper](https://github.com/xymb-endcrystalme/LinearMultiPaper) - MultiPaper with a few custom patches, including Linear region file format. No binaries available.

## Prerequisites:

Install the needed dependencies through pip
```
$ cd LinearTools/
$ pip install -r requirements.txt 
```

## Usage:

To see the full list of options, run the script with no arguments.
```
$ linear-tools-cli.py
```

Basic usuage requires the format denoted by either `mca` or `linear` and 
a valid source directory or file 
```
$ linear-tools-cli.py -s <source> [OPTIONS]
```

### Notes:
- The tool supports conversion of worlds and singular region files.
- Arguments requiring a path support both absolute and relative paths
- Default region format format is linear
- Default destination directory is set to the regions folder or the same directory 
- Default compression level is 6.
- Default threads is the amount of physical cores of the CPU.

## Results:

An undisclosed world (overworld) converted on 5950x compressed from 227357M to 119912M at compression_level=6.

Compression took 22min 17s on 5950x.