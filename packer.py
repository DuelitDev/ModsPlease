# -*- coding: utf-8 -*-
# Mods, Please (version: 1.4.11)

import argparse
import os
import sys
from io import BytesIO
from pathlib import Path

__author__ = "DuelitDev"
__version__ = "1.4.11"
__all__ = [
    "encrypt",
    "decrypt",
    "pack",
    "unpack"
]

KEY = [0xF2A30174, 0x8C59E5E7, 0xD0A3425D, 0x03692407]
DELTA = 0x9E3779B9


def encrypt(buffer: BytesIO) -> BytesIO:
    size = buffer.getbuffer().nbytes >> 2
    rounds = 52 // size + 6
    current = 0

    # data to uint32 array
    v = []
    buffer.seek(0)
    for i in range(0, size << 2, 4):
        v.append(int.from_bytes(buffer.read(4), "little"))

    # encrypt
    z = v[size - 1]
    for _ in range(rounds):
        current = (current + DELTA) & 0xFFFFFFFF
        e = (current >> 2) & 3
        for p in range(size):
            y = v[(p + 1) % size]  # 순환 처리
            mx = (((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4)) ^ 
                  ((current ^ y) + (KEY[(p & 3) ^ e] ^ z)))
            v[p] = (v[p] + mx) & 0xFFFFFFFF
            z = v[p]

    # rewrite to buffer
    buffer.seek(0)
    buffer.truncate()
    for block in v:
        buffer.write(block.to_bytes(4, 'little'))
    buffer.seek(0)
    return buffer


def decrypt(buffer: BytesIO) -> BytesIO:
    size = buffer.getbuffer().nbytes >> 2
    rounds = 52 // size + 6
    current = (DELTA * rounds) & 0xFFFFFFFF

    # data to uint32 array
    v = []
    buffer.seek(0)
    for i in range(0, size << 2, 4):
        v.append(int.from_bytes(buffer.read(4), "little"))

    # decrypt
    y = v[0]
    for _ in range(rounds):
        e = (current >> 2) & 3
        for p in range(size - 1, 0, -1):
            z = v[p - 1]
            mx = (((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4)) ^ 
                  ((current ^ y) + (KEY[(p & 3) ^ e] ^ z)))
            v[p] = (v[p] - mx) & 0xFFFFFFFF
            y = v[p]
        z = v[size - 1]
        mx = (((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4)) ^ 
              ((current ^ y) + (KEY[e] ^ z)))
        v[0] = (v[0] - mx) & 0xFFFFFFFF
        y = v[0]
        current = (current - DELTA) & 0xFFFFFFFF

    # rewrite to buffer
    buffer.seek(0)
    buffer.truncate()
    for block in v:
        buffer.write(block.to_bytes(4, 'little'))
    buffer.seek(0)
    return buffer


def pack(input_dir: str, output_file: str, verbose: bool = False):
    def s2p(p):
        return p.replace("/", "%2F")

    def load_file(file_path: str) -> int:
        nonlocal data
        with open(file_path, "rb") as file:
            return data.write(file.read())

    # get file list
    if verbose:
        print(f"Sanning: {input_dir}")
    execute_dir = os.getcwd()
    os.chdir(input_dir)
    files = []
    header = b"aoy4:namey"
    data = BytesIO()
    for base, _, filenames in os.walk("assets"):
        for filename in filenames:
            path = os.path.join(base, filename).replace("\\", "/")
            files.append(path)
    files.sort()

    # write header (haxe format)
    if verbose:
        print(f"Found {len(files)} assets to serialize.")
        print("Serializing assets...")
    header += str(len(s2p(files[0]))).encode("utf-8") + b":"
    header += s2p(files[0]).encode("utf-8") + b"y4:size"
    header += f"i{load_file(files[0])}g".encode("utf-8")
    for i in files[1:]:
        escaped = s2p(i)
        header += b"oR0y" + str(len(escaped)).encode("utf-8") + b":"
        header += escaped.encode("utf-8") + b"R2"
        length = load_file(i)
        if length == 0:
            header += b"zg"
        else:
            header += f"i{length}g".encode("utf-8")
    header += b"h"
    header = len(header).to_bytes(2, "little") + header

    # write data
    os.chdir(execute_dir)
    data.seek(0)
    new = BytesIO()
    new.write(header)
    new.write(data.read())

    # encrypt
    if verbose: 
        print("Encrypting...")
    data = encrypt(new)

    # write file
    with open(output_file, "wb") as output:
        output.write(data.read())
    if verbose:
        print(f"Successfully packed to: {output_file.replace('\\', '/')}")


def unpack(input_file: str, output_dir: str, verbose: bool = False):
    # get file
    buffer = BytesIO()
    with open(input_file, "rb") as file:
        buffer.write(file.read())

    # decrypt
    if verbose:
        print("Decrypting...")
    buffer = decrypt(buffer)
    buffer.read(4)  # version?

    # read header (haxe format)
    if verbose:
        print("Deserializing assets...")

    def read_until(sep: str):
        result = ""
        while True:
            char = buffer.read(1).decode("utf-8")
            if char == sep:
                return result
            result += char

    temp = {}
    name, size = [], []
    switch = ""
    i = 0
    while True:
        # haxe format
        operator = buffer.read(1).decode("utf-8")
        if operator == "y":
            data = buffer.read(int(read_until(":"))).decode("utf-8")
        elif operator == "R":
            data = temp[int(buffer.read(1).decode("utf-8"))]
        elif operator == "z":
            data = read_until("g") + "0"
        elif operator == "i":
            data = read_until("g")
        elif operator == "h":
            break
        else:
            continue
        temp[i] = data
        i += 1
        if i & 1:
            switch = data
            continue
        if switch == "name":
            name.append(data)
        elif switch == "size":
            size.append(int(data))
    del temp

    # extract files
    if verbose:
        print(f"Found {len(name)} assets to extract.")
    for n, s in zip(name, size):
        n = n.replace("%2F", "/")
        n = os.path.join(output_dir, n)
        os.makedirs("/".join(n.split("/")[:-1]), exist_ok=True)
        with open(n, "wb") as extracted_file:
            content = buffer.read(s)
            extracted_file.write(content)
        if verbose:
            print(f"\tExtracted: {n.replace('\\', '/')} ({s} bytes)")
    if verbose:
        print(f"Successfully unpacked to: {output_dir.replace('\\', '/')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="mods_please",
        description="Mods, Please - Pack/Unpack tool for Papers, Please.",
        epilog=f"version: {__version__} | Author: {__author__}"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    
    # Add commands
    commands = parser.add_subparsers(dest="command", help="Commands")
    
    pack_cmd = commands.add_parser("pack", help="Pack assets folder into Art.dat")
    pack_cmd.add_argument("input", type=str, help="Input directory containing 'assets' folder.")
    pack_cmd.add_argument("output", type=str, help="Output file")
    
    unpack_cmd = commands.add_parser("unpack", help="Unpack encrypted archive to directory")
    unpack_cmd.add_argument("input", type=str, help="Input Art.dat")
    unpack_cmd.add_argument("output", type=str, help="Output directory")
    
    # Parse args
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Execute commands
    if args.command == "pack":
        if not os.path.exists(args.input):
            print(f"Error: Input directory '{args.input}' does not exist")
            sys.exit(1)
        if not os.path.isdir(args.input):
            print(f"Error: '{args.input}' is not a directory")
            sys.exit(1)
        assets_path = os.path.join(args.input, "assets")
        if not os.path.exists(assets_path):
            print(f"Error: 'assets' directory not found in '{args.input}'")
            sys.exit(1)
        pack(args.input, args.output, True)
        
    elif args.command == 'unpack':
        if not os.path.exists(args.input):
            print(f"Error: Input file '{args.input}' does not exist")
            sys.exit(1)
        unpack(args.input, args.output, True)
