import os
import shutil
import logging

from stat import S_ISSOCK, S_ISLNK, S_ISCHR

from typing import Callable

from aa.mountpoints import Mountpoint
from aa.gpg import Decrypt
from aa.archive import Archive

logger = logging.getLogger("aa")

class Provider():

    def __init__(self):
        pass


class FileSystemProvider(Provider):

    def __init__(self, path: str, filter: Callable=lambda x: True):
        self.path = path
        self.filter = filter


    def is_archive(self, full_path: str):
        return full_path.endswith('.tgz') or \
               full_path.endswith('.tar.gz') or \
               full_path.endswith('.tar')


    def is_encrypted_archive(self, full_path: str):
        return full_path.endswith('.tgz.gpg') or \
               full_path.endswith('.tar.gz.gpg') or \
               full_path.endswith('.tar.gpg')


    def walk(self, path: str, url: str):
        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                full_url = os.path.join(url, item)

                mode = os.lstat(full_path).st_mode

                if S_ISSOCK(mode) or S_ISLNK(mode) or S_ISCHR(mode):
                    print(f"WARNING: unsupported item type {mode=}")
                    continue

                if 'parts.com' in item or 'tiles' in item or item == 'deepsearch':
                    continue

                if os.path.isdir(full_path):
                    logger.info(f"{full_path} is DIR")
                    yield from self.walk(full_path, full_url)

                if os.path.isfile(full_path):
                    yield full_path, full_url

                if self.is_archive(full_path):
                    tmp_dir = Archive().prepare_archive(full_path)

                    if tmp_dir is not None:
                        yield from self.walk(tmp_dir, os.path.join(url, item))
                        shutil.rmtree(tmp_dir)
                    else:
                        continue

                if self.is_encrypted_archive(full_path):
                    decryptor = Decrypt()

                    decrypted_path, decrypted_file = decryptor.try_to_decrypt(full_path)

                    if decrypted_file is None:
                        shutil.rmtree(decrypted_path)
                        continue

                    tmp_dir = Archive().prepare_archive(os.path.join(decrypted_path, decrypted_file))

                    if tmp_dir is not None:
                        yield from self.walk(tmp_dir, os.path.join(url, item, decrypted_file))
                        shutil.rmtree(tmp_dir)

                    shutil.rmtree(decrypted_path)


        except PermissionError:
            print(f"ERROR: Could not access {path}")
