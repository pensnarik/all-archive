# Image perceptual hashing algorithm

import os
import math
import hashlib
import subprocess

from PIL import Image

from .file import File

class PCPHash():

    # Size of image perceptive hash, in bits, required to meet 2 conditions:
    # 1) Should be power of 2
    # 2) log(PCP_HASH_SIZE, 2) should be interger
    # Possible values are: 2, 4, 16, 64, 256, 1024, 4096, 16384, ...
    PCP_HASH_SIZE = 256

    PCP_THUMB_SIZE = int(math.sqrt(PCP_HASH_SIZE))
    PCP_BITS_PER_ROW = PCP_THUMB_SIZE

    def __init__(self, file: File, tmp_dir: str):
        self.file = file
        self.tmp_dir = os.path.join(tmp_dir, '.pcp_hash')

        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)

    def __get_thumb_filename(self):
        return f"{self.tmp_dir}/{self.file.md5_hash}.png"

    def get_pcp_hash(self):
        command = f'magick convert -depth 8 -strip -type Grayscale ' \
                  f'-geometry {self.PCP_THUMB_SIZE}x{self.PCP_THUMB_SIZE}! ' \
                  f'"{self.file.path}" "{self.__get_thumb_filename()}"'

        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError:
            return None

        im = Image.open(f'{self.__get_thumb_filename()}')
        width, height = im.size

        if width != height:
            raise Exception('Width != height')

        sum = 0

        for y in range(0, height):
            for x in range(0, width):
                pixel = im.getpixel((x, y))
                sum += pixel

        average = sum / (width*height)

        hash = list()

        for y in range(0, width):
            bits = 0
            for x in range(0, height):
                bit = int(im.getpixel((x, y)) > average)
                bits += bit * math.pow(2, self.PCP_BITS_PER_ROW - 1 - x)

            hash.append(int(bits))

        # We need (PCP_BITS_PER_ROW / 8 * 2) symbols to store a row as a hex string
        # It's (PCP_BITS_PER_ROW / 8) bytes, and 2 characters per byte ('00' - 'ff')
        format_str = '%.{}x'.format(int(self.PCP_BITS_PER_ROW / 8 * 2))
        hash_as_str = ''.join([format_str % i for i in hash])

        os.remove(self.__get_thumb_filename())

        return hash_as_str

