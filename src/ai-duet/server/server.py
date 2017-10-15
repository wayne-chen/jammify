# 
# Copyright 2016 Google Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 

from predict import generate_midi
from read_midi import ReadMidi
import threading
import pdb
import os
from flask import send_file, request
import pretty_midi
import sys
if sys.version_info.major <= 2:
    from cStringIO import StringIO
else:
    from io import StringIO
from time import sleep
import time
import json

from flask import Flask
app = Flask(__name__, static_url_path='', static_folder=os.path.abspath('../static'))
app.ai_midis = []
app.human_midis = []
app.predict_count = 0
threadLock = threading.Lock()

class processThread(threading.Thread):
    def __init__(self, midi_data, duration):
        threading.Thread.__init__(self)
        self.midi_data = midi_data
        self.duration = duration

    def run(self):
        print "Starting " + self.name
        # Get lock to synchronize threads
        ret_midi = generate_midi(self.midi_data, self.duration)
        midi_data = pretty_midi.PrettyMIDI(ret_midi.name)

        if len(midi_data.instruments) > 0:
            for midi_note in midi_data.instruments[0].notes:
                threadLock.acquire()
                app.ai_midis.append({
                    "pitch": midi_note.pitch,
                    "velocity": midi_note.velocity
                })
                threadLock.release()

class midiThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.reader = ReadMidi(port=0)

    def run(self):
        while True:
            message = self.reader.get_message()
            if message:
                threadLock.acquire()
                # print message
                app.human_midis.append(message)
                threadLock.release()

@app.route('/predict', methods=['POST'])
def predict():
    values = json.loads(request.data)
    midi_data = pretty_midi.PrettyMIDI(StringIO(''.join(chr(v) for v in values)))

    duration = float(request.args.get('duration'))
    newThread = processThread(midi_data, duration)
    newThread.start()

    return 'yup'

@app.route('/midi_data', methods=['GET'])
def midi_data():
    threadLock.acquire()
    midi_data = json.dumps(dict(human_midi=app.human_midis, ai_midi=app.ai_midis))
    app.human_midis = []
    app.ai_midis = []
    threadLock.release()
    return midi_data

@app.route('/', methods=['GET', 'POST'])
def index():
    return send_file('../static/index.html')


if __name__ == '__main__':
    midi_process = midiThread()
    midi_process.start()
    # other IP 169.254.213.200
    # 192.168.17.174
    app.run(host='169.254.213.200', port=50007)
