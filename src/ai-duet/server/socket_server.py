import os
import sys
import json
import socket
from time import sleep

class MessageServer(object):
    def __init__(self, ip_address='localhost', port=8088):
        self.port = port
        self.ip_address = ip_address
        self.num_connections = 10
        self.byte_limit = 1024

        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serversocket.bind((ip_address, port))
        # Start listening with N connections
        self.serversocket.listen(self.num_connections)

    def read_buffer(self):
        connection, address = self.serversocket.accept()
        buf = connection.recv(self.byte_limit)
        return buf

    def send(self, data):
        self.serversocket.send(data)

    def receive(self):
        buf = self.read_buffer()

        if len(buf) > 0:
            return buf
            # break
        else:
            print 'Error buf length:', len(buf)
            return None

    def start_sending(self):
        conn, addr = self.serversocket.accept()
        print 'Connected by', addr
        # data = conn.recv(1024)
        conn.sendall('[{"velocity": 100, "pitch": 56}, {"velocity": 100, "pitch": 57}]')
        sleep(1)
        conn.close()

    def __del__(self):
        self.serversocket.close()


def main():
    server = MessageServer(ip_address='169.254.213.200', port=50007)
    server.start_sending()

if __name__ == '__main__':
    main()
