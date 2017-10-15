import json
from client import MessageClient
import rtmidi


class ReadMidi(object):
    def __init__(self, port=0):
        self.midiin = rtmidi.RtMidiIn()

        ports = range(self.midiin.getPortCount())

        if ports:
            self.midiin.openPort(port)
            print self.midiin.getPortName(port)
        else:
            print 'Error no input'

        # client = MessageClient(ip_address='localhost', port=8088)
        # inputs = mido.get_input_names()
        # with mido.open_input(inputs[1]) as inport:
        #     for msg in inport:
        #         client = MessageClient(ip_address='localhost', port=8088)
        #         client.send(message=str(msg))
        #         print msg
        #
        #

    def format_message(self, message):
        d = {}
        d['velocity'] = message.getVelocity()
        d['pressed'] = message.isNoteOn()
        d['note_number'] = message.getNoteNumber()
        d['note_name'] = message.getMidiNoteName(message.getNoteNumber())
        return d

    def get_message(self, timeout=250):
        message = self.midiin.getMessage(timeout) # some timeout in ms

        if message:
            # return MidiMessageHandler(message)
            return self.format_message(message)
        else:
            return None


def main():
    RM = ReadMidi(port=0)

    while True:
        message = RM.get_message()
        if message:
            print message

if __name__ == '__main__':
    main()
