import os
import random
import string
import shutil
import subprocess

class Archive():

    def get_tmp_dir(self, scope='unarchived'):
        path = os.path.join(
            f'./{scope}', ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
        )
        os.makedirs(path)
        return path


    def prepare_archive(self, full_path: str):
        print(f"ALARM UNARCHIVING {full_path}")

        if full_path.endswith('.tgz') or full_path.endswith('.tar.gz'):
            flags = '-xzf'
        else:
            flags = '-xf'

        out_dir = self.get_tmp_dir()
        command = [
            'tar', flags,
            full_path,
            '--no-same-permissions', '--no-same-owner',
            '-C', out_dir
        ]

        print(command)

        result = subprocess.run(command, capture_output=True)

        if result.returncode > 0:
            print(f"ERROR: Could not extract {full_path}, skipping")
            print(result.stderr.decode('utf-8'))
            shutil.rmtree(out_dir)
            return None

        return out_dir
