Koch method Morse code trainer
==============================

Morse code audio generation and training program, with Word Mode, Callsign Mode, and Random Character Mode.

Installation
------------

::

    $ pip install koch_trainer

Requires:

- `audiogen <https://pypi.python.org/pypi/audiogen>`_ 
- `PyAudio <http://people.csail.mit.edu/hubert/pyaudio/>`_ for audio playback (as opposed to file generation) 

Tested with Python 2.7.9 on Mac OS X.

Note that to install the PyAudio dependency on Mac OS X, you'll need to first
install ``portaudio`` with Homebrew::

    $ brew install portaudio

Examples
--------

Play back strings in Morse by passing them as command line arguments::

    $ koch_trainer hello world

Save the generated code to a WAV file::

    $ koch_trainer -f hello.wav hello world

Change the code speed from the default 20 WPM to 30 WPM::

    $ koch_trainer --effective-speed 30 hello world

And the tone frequency from the default 770 Hz to 440 Hz::

    $ koch_trainer --hertz 440 hello world

Changing the level will add or remove characters from the training pool. The following will result in a default of 100 characters output using the following characters as a base: K·M·R·S·U·A·P·T·L·O·W·I::

    $ koch_trainer --level 12 --effective-speed 7 --character-speed 20

You can also specify word mode by passing the word-mode flag. Settings exist to customize the experience. The following will result in 20 words being output with character counts ranging from 2 to 6 characters using the same 12 characters as above. Changing the level will change the characters available::

    $ koch_trainer --level 12 --effective-speed 7 --character-speed 20 --word-mode --word-count 20 --word-char-min 2 --word-char-max 6

A callsign practice mode is also available via the following::

    $ koch_trainer --effective-speed 7 --character-speed 20 --callsign-mode --callsign-count 20

Get help with CLI options::

    $ koch_trainer -h

See also
--------

- `audiogen`_ (`Github project <https://github.com/casebeer/audiogen>`_),
  a Python generator-based audio generation and processing library

Contributing
------------

Get the source and report any bugs on Github:

    https://github.com/rguisewite/koch_trainer
