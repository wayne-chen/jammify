import os
import sys
import json
import socket


class MessageClient(object):
    def __init__(self, ip_address='localhost', port=8088):
        self.port = port
        self.ip_address = ip_address

        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, message):
        self.clientsocket.connect((self.ip_address, self.port))
        self.clientsocket.send(message)

    def __del__(self):
        self.clientsocket.close()


def main():
    client = MessageClient(ip_address='localhost', port=8088)

    sample_json_message = {"a": "123"}
    sample_json_string = json.dumps(sample_json_message)

    client.send(message=sample_json_string)

if __name__ == '__main__':
    main()
