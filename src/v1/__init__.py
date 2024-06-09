# -*- coding: utf-8 -*-
# Mods, Please (version: 1.0.0)
#
# This Program is distributed under the MIT License.
# This Program does not work for v1.4.x or later.

import io
import os
import sys

__all__ = [
    "_encrypt",
    "_decrypt",
    "pack",
    "unpack"
]


def _encrypt(buffer: io.BytesIO) -> io.BytesIO:
    size = buffer.getbuffer().nbytes
    buffer.seek(0)
    while size // 8 != 0:
        data = buffer.read(8)
        buffer.seek(buffer.tell() - 8)
        temp1 = int.from_bytes(data[:4], "little", signed=False)
        temp2 = int.from_bytes(data[4:], "little", signed=False)
        offset = 0
        for i in range(32):
            offset = offset - 0x61C88647 & 0xFFFFFFFF
            temp1 = temp1 + ((16 * (temp2 + 0x5938517)) ^ (offset + temp2) ^
                             ((temp2 >> 5) + 0x3064397E)) & 0xFFFFFFFF
            temp2 = temp2 + ((offset + temp1) ^ (16 * temp1 + 0x2B6D416D) ^
                             ((temp1 >> 5) + 0x61382B6C)) & 0xFFFFFFFF
        data = (temp1.to_bytes(4, "little", signed=False) +
                temp2.to_bytes(4, "little", signed=False))
        buffer.write(data)
        size -= 8
    buffer.seek(0)
    return buffer


def _decrypt(buffer: io.BytesIO) -> io.BytesIO:
    size = buffer.getbuffer().nbytes
    buffer.seek(0)
    while size // 8 != 0:
        data = buffer.read(8)
        buffer.seek(buffer.tell() - 8)
        temp1 = int.from_bytes(data[:4], "little", signed=False)
        temp2 = int.from_bytes(data[4:], "little", signed=False)
        offset = -957401312
        for i in range(32):
            temp2 = temp2 - ((offset + temp1) ^ (16 * temp1 + 0x2B6D416D) ^
                             ((temp1 >> 5) + 0x61382B6C)) & 0xFFFFFFFF
            temp1 = temp1 - ((16 * (temp2 + 0x5938517)) ^ (offset + temp2) ^
                             ((temp2 >> 5) + 0x3064397E)) & 0xFFFFFFFF
            offset = offset + 0x61C88647 & 0xFFFFFFFF
        data = (temp1.to_bytes(4, "little", signed=False) +
                temp2.to_bytes(4, "little", signed=False))
        buffer.write(data)
        size -= 8
    buffer.seek(0)
    return buffer


def pack(input_dir: str, output_file: str):
    def s2p(p):
        return p.replace("/", "%2F")

    def load_file(file_path: str) -> int:
        nonlocal data
        with open(file_path, "rb") as file:
            return data.write(file.read())

    # get file list
    execute_dir = os.getcwd()
    os.chdir(input_dir)
    files = []
    header = b"aoy4:namey"
    data = io.BytesIO()
    for base, _, filenames in os.walk("assets"):
        for filename in filenames:
            path = os.path.join(base, filename).replace("\\", "/")
            files.append(path)
    # end get file list

    # write header
    """
    header example:
    assets%2Fexample1.txtR2i13goR0y21:assets%2Fexample2.txt......
               file size ---^^     ^^--- next file name length
    """
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
    # end write header

    # write data
    os.chdir(execute_dir)
    data.seek(0)
    new = io.BytesIO()
    new.write(header)
    new.write(data.read())
    data = _encrypt(new)
    with open(output_file, "wb") as output:
        output.write(data.read())
        output.write(b"\0" * (8 - output.tell() % 8))
    # end write data


def unpack(input_file: str, output_dir: str):
    # get file
    buffer = io.BytesIO()
    with open(input_file, "rb") as file:
        buffer.write(file.read())
    buffer = _decrypt(buffer)
    buffer.read(4)  # dummy

    # end get file

    # read header
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
        operator = buffer.read(1).decode("utf-8")
        """
        --------------------- operators --------------------
        |  y  |  y(?<len>[0-9]+)   |  read (len) bytes.    |
        |  R  |  R[0-9]            |  ???                  |
        |  z  |  zg                |  file size is zero.   |
        |  i  |  i(?<len>[0-9]+)g  |  file size is (len).  |
        |  h  |  h                 |  stop read.           |
        ----------------------------------------------------
        """
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
    # end read header

    # extract files
    for n, s in zip(name, size):
        n = n.replace("%2F", "/")
        n = os.path.join(output_dir, n)
        os.makedirs("/".join(n.split("/")[:-1]), exist_ok=True)
        with open(n, "wb") as extracted_file:
            extracted_file.write(buffer.read(s))
    # end extract files
