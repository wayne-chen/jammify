import os
import sys
import json
import socket

# clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# clientsocket.connect(('localhost', 8089))

# sample_json_message = {"a": "123"}
# sample_json_string = json.dumps(d)

# clientsocket.send(sample_json_string)


class MessageClient(object):
    def __init__(self, ip_address='localhost', port=8089):
        self.port = port

        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientsocket.connect((ip_address, port))
    
    def send(self, message):
        self.clientsocket.send(message)


def main():
    client = MessageClient(ip_address='localhost', port=8089)

    sample_json_message = {"a": "123"}
    sample_json_string = json.dumps(sample_json_message)

    client.send(message=sample_json_string)

if __name__ == '__main__':
    main()
