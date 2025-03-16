import os
import random
import string
import subprocess

class Decrypt():

    def __init__(self):
        with open('.secrets', 'r') as f:
            self.known_passwords = f.read().split('\n')

    def get_tmp_dir(self, scope='unarchived'):
        path = os.path.join(
            f'./{scope}', ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
        )
        os.makedirs(path)
        return path


    def try_to_decrypt(self, full_path: str):
        path = self.get_tmp_dir('unencrypted')

        for password in self.known_passwords:

            new_name = full_path.split('/')[-1].replace('.gpg', '')

            result = self.decrypt_file(full_path, os.path.join(path, new_name), password)

            if result is True:
                return path, new_name

        return path, None


    def decrypt_file(self, encrypted_file_path: str, output_file_path: str, password):
        """
        Decrypts a file using GPG with the given password.
        """
        print(f"ALARM DECRYPTING {encrypted_file_path}")

        try:
            # Construct the gpg command
            command = [
                'gpg',
                '--batch',  # Use batch mode to avoid interactive prompts
                '--pinentry-mode', 'loopback',  # Use loopback mode for password input
                '--passphrase', password,  # Provide the password
                '--output', output_file_path,  # Specify the output file
                '--decrypt', encrypted_file_path  # Specify the input file
            ]

            print(command)

            # Run the command
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # If the command was successful, return True
            if result.returncode == 0:
                print(f"File decrypted successfully to {output_file_path}")
                return True
            else:
                print(f"Decryption failed with error: {result.stderr.decode()}")
                return False

        except subprocess.CalledProcessError as e:
            print(f"Decryption failed with error: {e.stderr.decode()}")
            return False
