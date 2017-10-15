import os
import sys
import json
import socket


class MessageClient(object):
    def __init__(self, ip_address='localhost', port=8088):
        self.port = port
        self.ip_address = ip_address

        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.clientsocket.connect((self.ip_address, self.port))

    def send(self, message):
        self.clientsocket.connect((self.ip_address, self.port))
        self.clientsocket.send(message)

    def receive(self):
        self.connect()
        return self.clientsocket.recv(1024)

    def __del__(self):
        self.clientsocket.close()


def main():
    while True:
        client = MessageClient(ip_address='192.168.17.174', port=50007)
        data = client.receive()
        if data is None:
            continue
        print 'Received', repr(data)

    # sample_json_message = {"a": "123"}
    # sample_json_string = json.dumps(sample_json_message)
    #
    # client.send(message=sample_json_string)

if __name__ == '__main__':
    main()
