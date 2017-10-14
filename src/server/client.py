import os
import sys
import json
import socket

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('localhost', 8089))

sample_json_message = {"a": "123"}
sample_json_string = json.dumps(d)

clientsocket.send(sample_json_string)