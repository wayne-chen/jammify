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
from socket_client import MessageClient
import pdb
import os
from flask import send_file, request
import pretty_midi
import sys
if sys.version_info.major <= 2:
    from cStringIO import StringIO
else:
    from io import StringIO
import time
import json

from flask import Flask
app = Flask(__name__, static_url_path='', static_folder=os.path.abspath('../static'))

@app.route('/predict', methods=['POST'])
def predict():
    now = time.time()
    values = json.loads(request.data)
    midi_data = pretty_midi.PrettyMIDI(StringIO(''.join(chr(v) for v in values)))
    duration = float(request.args.get('duration'))
    ret_midi = generate_midi(midi_data, duration)
    midi_data = pretty_midi.PrettyMIDI(ret_midi.name)


    midi_notes = []

    for midi_note in midi_data.instruments[0].notes:
        midi_notes.append({
            "pitch": midi_note.pitch,
            "velocity": midi_note.velocity
        })

    ios_client = MessageClient(ip_address='localhost', port=8088)
    ios_client.send(json.dumps(midi_notes))


    return send_file(ret_midi, attachment_filename='return.mid',
        mimetype='audio/midi', as_attachment=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    return send_file('../static/index.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8090)
