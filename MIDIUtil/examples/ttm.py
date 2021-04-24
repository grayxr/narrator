#!/usr/bin/env python
#
# retroSpeak project
#
# A very primitive text to speech command. Only converts text at
# the command line. No attempt is made to convert numbers, much
# punctuation.
#
# As this is based heavily on Public Domain work, this code is relased as public domain.
#
# Ensure retroSpeak.py, en_US_rules.py and vocabulary.py are in the path or
# same directory as this script
#
# Jason Lane 2015
#
# English to Phoneme text to speech
# Python version of Naval Research Laboratory algorithm
# described in NRL Report 7948 January 21st, 1976 Elovitz et al
# http://www.dtic.mil/cgi-bin/GetTRDoc?AD=ADA021929
# Adapted from the public domain C version by Wasser, 1985
# Retrieved from: ftp://svr-ftp.eng.cam.ac.uk/pub/comp.speech/synthesis/english2phoneme.tar.gz
#
# Outputs a form of International Pronounciation Alphabet (IPA) which is mapped
# to the allophone set used by the SP0256-AL2 in the retroSpeak project
#
#   The Phoneme codes (US English):
#
#           IY      bEEt            IH      bIt
#           EY      gAte            EH      gEt
#           AE      fAt             AA      fAther
#           AO      lAWn            OW      lOne
#           UH      fUll            UW      fOOl
#           ER      mURdER          AX      About
#           AH      bUt             AY      hIde
#           AW      hOW             OY      tOY
#           p       Pack            b       Back
#           t       Time            d       Dime
#           k       Coat            g       Goat
#           f       Fault           v       Vault
#           TH      eTHer           DH      eiTHer
#           s       Sue             z       Zoo
#           SH      leaSH           ZH      leiSure
#           HH      How             m       suM
#           n       suN             NG      suNG
#           l       Laugh           w       Wear
#           y       Young           r       Rate
#           CH      CHar            j       Jar
#           WH      WHere
#
#
#   Rules are made up of four parts:
#
#           The left context.
#           The text to match.
#           The right context.
#           The phonemes to substitute for the matched text.
#
#   Procedure:
#
#           Seperate each block of letters (apostrophes included)
#           and add a space on each side.  For each unmatched
#           letter in the word, look through the rules where the
#           text to match starts with the letter in the word.  If
#           the text to match is found and the right and left
#           context patterns also match, output the phonemes for
#           that rule and skip to the next unmatched letter.
#
#
#   Special Context Symbols:
#
#           #       One or more vowels
#           :       Zero or more consonants
#           ^       One consonant.
#           .       One of B, D, V, G, J, L, M, N, R, W or Z (voiced
#                   consonants)
#           %       One of ER, E, ES, ED, ING, ELY (a suffix)
#                   (Found in right context only)
#           +       One of E, I or Y (a "front" vowel)
#


import argparse

# import retroSpeak
from en_US_rules import Rules
from vocabulary import *
from midiutil import MIDIFile

# Parts of rules
leftPart = 0
matchPart = 1
rightPart = 2
outPart = 3


def isVowel(c):
    return c in ('A', 'E', 'I', 'O', 'U')


def isConsonant(c):
    return c.isupper() and not isVowel(c)


def translateWord(t_word):
    # Return a list of IPA phonemes that make up the word
    t_phonemes = ''
    t_word = ' ' + t_word + ' '  # Add padding spaces either side of word
    index = 1  # start on first letter of word - after added space
    while index < len(t_word)-1:
        # print "Index: {} Letter:{}".format(index,word[index])
        if t_word[index].isupper():
            letter_rules = Rules[t_word[index]]
        else:
            letter_rules = Rules['punctuation']
        index, t_phoneme = findRule(t_word, index, letter_rules)
        if t_phoneme != '':
            t_phonemes = t_phonemes + ' ' + t_phoneme
    return t_phonemes.split()


def findRule(r_word, index, rules):
    # Find the matching rule for the character in the word
    # index is the position of the character to check
    # rules is a list of the rules corresponding to the character
    # Find a matching centre pattern, then check the left and right patterns
    # Left hand pattern and text is reversed, as the test moves away from centre character
    # If all 3 tests match, return the index of the remainder of the word, and the
    # phoneme of the matched rule.
    for rule in rules:
        if rule[1] == r_word[index:index+len(rule[matchPart])]:
            # Found a matching centre pattern
            left_rule = rule[leftPart]
            right_rule = rule[rightPart]
            remainder = index+len(rule[matchPart])
            left_word = r_word[:index]  # All letters before centre pattern
            right_word = r_word[remainder:]  # All letters after centre pattern
            # Check for left match and right match
            if lrMatch(left_rule, left_word) and lrMatch(right_rule, right_word, right=True):
                return remainder, rule[outPart]
    # Rule not Found
    print("Error: Can't find rule for '{}' in '{}'".format(word[index],word))
    return index+1, ''


def lrMatch(pattern, context, right=False):
    # Pattern matching
    # pattern is the rule to check for, context is the text to left or right of the letter
    # the right flag signifies checking to the right or left of the current letter
    # If checking to the left, the pattern and context are reversed
    # print "{} Pattern:'{}' Context:'{}'".format('Right:' if right else 'Left:',pattern,context)
    if pattern == '':
        # Empty pattern matches any context
        return True
    if not right:
        # left hand rule - reverse pattern and context
        pattern = pattern[::-1]
        context = context[::-1]
    text_pos = 0
    for p in pattern:
        # First check for simple text or space
        if p.isalpha() or p == "'" or p == " ":
            if p == context[text_pos]:
                text_pos = text_pos+1
                continue
            else:
                return False
        if p == '#':
            # One or more vowels
            if not isVowel(context[text_pos]):
                return False
            text_pos = text_pos+1
            while isVowel(context[text_pos]):
                text_pos = text_pos+1
        elif p == ':':
            # zero or more consonant
            while isConsonant(context[text_pos]):
                text_pos = text_pos+1
        elif p == '^':
            # One consonant
            if not isConsonant(context[text_pos]):
                return False
            text_pos = text_pos+1
        elif p == '.':
            #  B, D, V, G, J, L, M, N, R, W, Z
            if context[text_pos] not in "BDVGJLMNRWZ":
                return False
            text_pos = text_pos+1
        elif p == '+':
            # E, I or Y (front vowel)
            if context[text_pos] not in "EIY":
                return False
            text_pos = text_pos+1
        elif right and p == '%':
            # ER, E, ES, ED, ING, ELY (a suffix)
            # Only used in right hand rules
            if context[text_pos:text_pos + 3] == 'ING' or context[text_pos:text_pos + 3] == 'ERY':
                text_pos = text_pos + 4
            elif context[text_pos:text_pos + 2] == 'ER' or \
                    context[text_pos:text_pos + 2] == 'ES' or \
                    context[text_pos:text_pos + 2] == 'ED':
                text_pos = text_pos + 3
            elif context[text_pos] == 'E':
                text_pos = text_pos + 2
            else:
                return False
        else:
            print("Bad char in {} pattern: '{}'".format('right' if right else 'left', p))
            return False
    return True


def translateText(text):
    # Translate the text and return a list with the phonetic version of the words
    # Each word in the list is a list of phonemes.
    t_phonemes = []
    for t_word in text:
        t_phonemes.append(translateWord(t_word.upper()))
    return t_phonemes


# The NRL phoneme set is a subset of the ones available on the SP0256
# This dictionary maps from IPA to SP0256
NRLIPAtoSPO256 = {'AA': 'AA', 'AE': 'AE', 'AH': 'AX AX', 'AO': 'AO', 'AW': 'AW', 'AX': 'AX',
                  'AY': 'AY', 'b': 'BB1', 'CH': 'CH', 'd': 'DD1', 'DH': 'DH1', 'EH': 'EH',
                  'ER': 'ER1', 'EY': 'EY', 'f': 'FF', 'g': 'GG2', 'h': 'HH1', 'IH': 'IH',
                  'IY': 'IY', 'j': 'JH', 'k': 'KK1', 'l': 'LL', 'm': 'MM', 'n': 'NN1',
                  'NG': 'NG', 'OW': 'OW', 'OY': 'OY', 'p': 'PP', 'r': 'RR1', 's': 'SS',
                  'SH': 'SH', 't': 'TT1', 'TH': 'TH', 'UH': 'UH', 'UW': 'UW2', 'v': 'VV',
                  'w': 'WW', 'WH': 'WH', 'y': 'YY1', 'z': 'ZZ', 'ZH': 'ZH', 'PAUSE': 'PA4'}


def IPAtoSP0256(ipa_phonemes):
    # convert a list of IPA phonemes into SP0256 phonemes
    sp0256 = []
    for phoneme in ipa_phonemes:
        if phoneme in NRLIPAtoSPO256:
            sp0256.append(NRLIPAtoSPO256[phoneme])
    return sp0256


# Create the MIDIFile Object
MyMIDI = MIDIFile(1)

# Add track name and tempo. The first argument to addTrackName and
# addTempo is the time to write the event.
track = 0
time = 0
MyMIDI.addTrackName(track, time, "Sample Track")
MyMIDI.addTempo(track, time, 120)

# Add a note. addNote expects the following information:
channel = 0
pitch = 60
duration = 0.25
volume = 100

parser = argparse.ArgumentParser(description='Simple Text to Speech')
parser.add_argument('text', metavar='text', nargs=argparse.REMAINDER, help='Text to speak')
args = parser.parse_args()

# words_all = args.text
words_all = """sonic sand castles"""
words_all = words_all.split()

phonemes = ''
for word in words_all:
    if word.lower() in vocabulary:
        phonemes = phonemes + ' ' + vocabulary[word.lower()]
    else:
        phonemes = phonemes + ' ' + ' '.join(IPAtoSP0256(translateWord(word.upper())))
    phonemes = phonemes + ' PA4'

print phonemes

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

note_pitches = []
for phoneme in phonemes.split():
    if phoneme in note_dict:
        note_pitches.append(note_dict[phoneme])
        print note_dict[phoneme]
    else:
        print 'not found!'

# Now add the note.
# And write it to disk.

for i, note_pitch in enumerate(note_pitches):
    MyMIDI.addNote(track, channel, note_pitch, time + i * 0.25, duration, volume)

with open("output.mid", 'wb') as binfile:
     MyMIDI.writeFile(binfile)

# MyMIDI.addNote(track, channel, pitch, time, duration, volume)
# with open("output.mid", 'wb') as binfile:
#     MyMIDI.writeFile(binfile)
