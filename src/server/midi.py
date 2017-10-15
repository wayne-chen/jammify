import mido
import pdb
import json
from client import MessageClient

class Midi(object):
    def __init__(self):

        self.client = MessageClient(ip_address='localhost', port=8089)

        inputs = mido.get_input_names()
        with mido.open_input(inputs[1]) as inport:
            for msg in inport:
                self.client.send(message=json.dumps({"yo": "test"}))
                print msg

def main():
    Midi()

if __name__ == '__main__':
    main()
