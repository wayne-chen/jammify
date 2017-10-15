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


import magenta

from magenta.models.melody_rnn import melody_rnn_config_flags
from magenta.models.melody_rnn import melody_rnn_model
from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.protobuf import generator_pb2
from magenta.protobuf import music_pb2

from magenta.models.shared import events_rnn_model
import magenta.music as mm

import os
import time
import tempfile
import pretty_midi

BUNDLE_NAME = 'lookback_rnn'
DEFAULT_MIN_NOTE = 48
DEFAULT_MAX_NOTE = 84
DEFAULT_TRANSPOSE_TO_KEY = 0


import tensorflow as tf

class MelodyRnnCustomConfig(events_rnn_model.EventSequenceRnnConfig):
  """Stores a configuration for a MelodyRnn.

  You can change `min_note` and `max_note` to increase/decrease the melody
  range. Since melodies are transposed into this range to be run through
  the model and then transposed back into their original range after the
  melodies have been extended, the location of the range is somewhat
  arbitrary, but the size of the range determines the possible size of the
  generated melodies range. `transpose_to_key` should be set to the key
  that if melodies were transposed into that key, they would best sit
  between `min_note` and `max_note` with having as few notes outside that
  range.

  Attributes:
    details: The GeneratorDetails message describing the config.
    encoder_decoder: The EventSequenceEncoderDecoder object to use.
    hparams: The HParams containing hyperparameters to use.
    min_note: The minimum midi pitch the encoded melodies can have.
    max_note: The maximum midi pitch (exclusive) the encoded melodies can have.
    transpose_to_key: The key that encoded melodies will be transposed into, or
        None if it should not be transposed.
  """

  def __init__(self, details, encoder_decoder, hparams,
               min_note=DEFAULT_MIN_NOTE, max_note=DEFAULT_MAX_NOTE,
               transpose_to_key=DEFAULT_TRANSPOSE_TO_KEY):
    super(MelodyRnnCustomConfig, self).__init__(details, encoder_decoder, hparams)

    if min_note < mm.MIN_MIDI_PITCH:
      raise ValueError('min_note must be >= 0. min_note is %d.' % min_note)
    if max_note > mm.MAX_MIDI_PITCH + 1:
      raise ValueError('max_note must be <= 128. max_note is %d.' % max_note)
    if max_note - min_note < mm.NOTES_PER_OCTAVE:
      raise ValueError('max_note - min_note must be >= 12. min_note is %d. '
                       'max_note is %d. max_note - min_note is %d.' %
                       (min_note, max_note, max_note - min_note))
    if (transpose_to_key is not None and
        (transpose_to_key < 0 or transpose_to_key > mm.NOTES_PER_OCTAVE - 1)):
      raise ValueError('transpose_to_key must be >= 0 and <= 11. '
                       'transpose_to_key is %d.' % transpose_to_key)

    self.min_note = min_note
    self.max_note = max_note
    self.transpose_to_key = transpose_to_key

default_configs = {
    'basic_rnn': MelodyRnnCustomConfig(
        magenta.protobuf.generator_pb2.GeneratorDetails(
            id='basic_rnn',
            description='Melody RNN with one-hot encoding.'),
        magenta.music.OneHotEventSequenceEncoderDecoder(
            magenta.music.MelodyOneHotEncoding(
                min_note=DEFAULT_MIN_NOTE,
                max_note=DEFAULT_MAX_NOTE)),
        tf.contrib.training.HParams(
            batch_size=128,
            rnn_layer_sizes=[128, 128],
            dropout_keep_prob=0.5,
            clip_norm=5,
            learning_rate=0.001)),

    'lookback_rnn': MelodyRnnCustomConfig(
        magenta.protobuf.generator_pb2.GeneratorDetails(
            id='lookback_rnn',
            description='Melody RNN with lookback encoding.'),
        magenta.music.LookbackEventSequenceEncoderDecoder(
            magenta.music.MelodyOneHotEncoding(
                min_note=DEFAULT_MIN_NOTE,
                max_note=DEFAULT_MAX_NOTE)),
        tf.contrib.training.HParams(
            batch_size=128,
            rnn_layer_sizes=[128, 128],
            dropout_keep_prob=0.5,
            clip_norm=5,
            learning_rate=0.001)),

    'attention_rnn': MelodyRnnCustomConfig(
        magenta.protobuf.generator_pb2.GeneratorDetails(
            id='attention_rnn',
            description='Melody RNN with lookback encoding and attention.'),
        magenta.music.KeyMelodyEncoderDecoder(
            min_note=DEFAULT_MIN_NOTE,
            max_note=DEFAULT_MAX_NOTE),
        tf.contrib.training.HParams(
            batch_size=128,
            rnn_layer_sizes=[128, 128],
            dropout_keep_prob=0.5,
            attn_length=40,
            clip_norm=3,
            learning_rate=0.001))
}
config = default_configs[BUNDLE_NAME]
# need to figure out how to modify these params

bundle_file = magenta.music.read_bundle_file(os.path.abspath(BUNDLE_NAME+'.mag'))
steps_per_quarter = 4

generator = melody_rnn_sequence_generator.MelodyRnnSequenceGenerator(
      model=melody_rnn_model.MelodyRnnModel(config),
      details=config.details,
      steps_per_quarter=steps_per_quarter,
      bundle=bundle_file)

def _steps_to_seconds(steps, qpm):
    return steps * 60.0 / qpm / steps_per_quarter

# change hyperparameters of neural net.
def params_changed(batch_size=128, rnn_layer_sizes=[128, 128], dropout_keep_prob=0.5,
                  attn_length=40, clip_norm=3, learning_rate=0.001)
    generator = melody_rnn_sequence_generator.MelodyRnnSequenceGenerator(
      model=melody_rnn_model.MelodyRnnModel(config),
      details=config.details,
      steps_per_quarter=steps_per_quarter,
      bundle=bundle_file)


def generate_midi(midi_data, total_seconds=10):
    # midi_data is in PrettyMIDI format.
    primer_sequence = magenta.music.midi_io.midi_to_sequence_proto(midi_data)

    # predict the tempo
    if len(primer_sequence.notes) > 4:
        estimated_tempo = midi_data.estimate_tempo()
        if estimated_tempo > 240:
            qpm = estimated_tempo / 2
        else:
            qpm = estimated_tempo
    else:
        qpm = 120
    primer_sequence.tempos[0].qpm = qpm

    generator_options = generator_pb2.GeneratorOptions()
    # Set the start time to begin on the next step after the last note ends.
    last_end_time = (max(n.end_time for n in primer_sequence.notes)
                     if primer_sequence.notes else 0)
    generator_options.generate_sections.add(
        start_time=last_end_time + _steps_to_seconds(1, qpm),
        end_time=total_seconds)

    # generate the output sequence
    generated_sequence = generator.generate(primer_sequence, generator_options)

    output = tempfile.NamedTemporaryFile()
    magenta.music.midi_io.sequence_proto_to_midi_file(generated_sequence, output.name)
    output.seek(0)
    return output
