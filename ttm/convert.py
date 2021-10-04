#!/usr/bin/env python

import argparse
from datetime import datetime
from midiutil import MIDIFile
from retroTTS import *

# Prepare CLI args
parser = argparse.ArgumentParser(description='Text to MIDI')
parser.add_argument(
    'text',
    metavar='text',
    nargs=argparse.REMAINDER
)
args = parser.parse_args()
words = args.text

# Convert text to phonemes
phonemes = ''
for word in words:
    if word.lower() in vocabulary:
        phonemes = phonemes + ' ' + vocabulary[word.lower()]
    else:
        phonemes = phonemes + ' ' + ' '.join(IPAtoSP0256(translateWord(word.upper())))
    phonemes = phonemes + ' PA4'

print(phonemes)


# Create the MIDIFile Object
MyMIDI = MIDIFile(1)

# Add track name and tempo. The first argument to addTrackName and
# addTempo is the time to write the event.
track = 0
time = 0
MyMIDI.addTrackName(track, time, "MIDI Narrator Track")
MyMIDI.addTempo(track, time, 120)

# Default note attributes
channel = 0
pitch = 60
duration = 0.25
volume = 100

# Convert phonemes to MIDI notes
note_dict = {
    'AA': 24,
    'AE': 26,
    'AX': 15,
    'AO': 23,
    'AW': 32,
    'AY': 6,
    'BB1': 28,
    'CH': 50,
    'DD1': 21,
    'DH1': 18,
    'EH': 7,
    'ER1': 51,
    'EY': 20,
    'FF': 40,
    'GG2': 61,
    'HH1': 27,
    'IH': 12,
    'IY': 19,
    'JH': 10,
    'KK1': 42,
    'LL': 45,
    'MM': 16,
    'NN1': 11,
    'NG': 44,
    'OW': 53,
    'OY': 5,
    'PP': 9,
    'RR1': 14,
    'SS': 55,
    'SH': 37,
    'TT1': 17,
    'TH': 29,
    'UH': 30,
    'UW2': 31,
    'VV': 35,
    'WW': 46,
    'WH': 48,
    'YY1': 49,
    'ZZ': 43,
    'ZH': 38,
    'PA4': 3
}

midi_notes = []
for phoneme in phonemes.split():
    if phoneme in note_dict:
        midi_notes.append(note_dict[phoneme])
        print(note_dict[phoneme])
    else:
        print('not found!')

# Now add the note.
# And write it to disk.

for i, pitch in enumerate(midi_notes):
    MyMIDI.addNote(track, channel, pitch, time + i * 0.25, duration, volume)

now = datetime.now()

with open('ttm-output-{}.mid'.format(now.strftime("%Y%m%d-%H%M%S")), 'wb') as binfile:
    MyMIDI.writeFile(binfile)
