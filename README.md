# MIDI Narrator Text-to-MIDI

A simple janky Python tool which converts text input to MIDI files which the [Rare Waves MIDI Narrator](https://rarewaves.net/products/midi-narrator/) can speak.

## Install MIDIUtil
```
$ cd MIDIUtil
$ python setup.py install
```
Or
```
$ pip install MIDIUtil
```

## Run

```
$ python ttm/convert.py hello world
```
A `ttm-output-<timestamp>.mid` file will be generated, which can be used by your DAW / MIDI tool of choice.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details