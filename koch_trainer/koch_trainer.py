#!/usr/bin/env python3
# encoding: utf-8

from io import open

import audiogen
import audiogen.util
import contextlib
import itertools
import random
import time
import sys
import re
import os
import os.path

# random.SystemRandom() should be cryptographically secure
try:
    rng = random.SystemRandom
except AttributeError as ex:
    rng = random.Random



class KochTrainer:
    def __init__( self, options ):
        #
        # Defaults
        #

        self._level             = options.level
        self._character_count   = options.character_count
        self._character_speed   = options.character_speed
        self._effective_speed   = options.effective_speed
        self._custom_alphabet   = options.custom_alphabet
        self._file              = options.file
        self._hertz             = options.hertz
        self._bandwidth         = options.bandwidth

        self._callsign_mode     = options.callsign_mode
        self._callsign_count    = options.callsign_count

        self._word_mode         = options.word_mode
        self._word_count        = options.word_count
        self._word_char_min     = options.word_char_min
        self._word_char_max     = options.word_char_max
        self._word_file         = options.word_file
        self._word_separators   = [ " " ]

        if self._word_char_min > self._word_char_max:
            self._word_char_max = self._word_char_min


    def run( self, message=None ):
        if message:
            message                     = message.upper()

            print( "\n\nMessage Mode: Effective Speed: {effective_speed} | Character Speed {character_speed}".format( effective_speed=self._effective_speed, character_speed=self._character_speed ) )
        elif self._callsign_mode:
            message                     = self.build_callsigns()

            print( "\n\nCallsign Mode: Effective Speed: {effective_speed} | Character Speed {character_speed}".format( effective_speed=self._effective_speed, character_speed=self._character_speed ) )
        else:
            #
            # Character Setup
            #

            self._characters            = self.build_character_list()

            if not self._word_mode:
                message                 = self.build_characters()

                print( "\n\nRandom Character Mode: Effective Speed: {effective_speed} | Character Speed {character_speed} | Characters {characters}".format( effective_speed=self._effective_speed, character_speed=self._character_speed, characters="·".join( self._characters ) ) )
            else:
                #
                # Build Word Separators
                #

                if "." in self._characters:
                    self._word_separators.append( "." )

                if "," in self._characters:
                    self._word_separators.append( "," )

                if "?" in self._characters:
                    self._word_separators.append( "?" )

                message                 = self.build_words()

                print( "\n\nWord Mode: Effective Speed: {effective_speed} | Character Speed {character_speed} | Characters {characters}".format( effective_speed=self._effective_speed, character_speed=self._character_speed, characters="·".join( self._characters ) ) )

        audio_generator = KochTrainerAudioGen( message, effective_speed=self._effective_speed, character_speed=self._character_speed, hertz=self._hertz, bandwidth=self._bandwidth )

        if self._file:
            audio_generator.save_file( self._file )
        else:
            print( "Audio beginning in:" )
            sys.stdout.flush()
            time.sleep( 1 )
            print( "3...", end=" " )
            sys.stdout.flush()
            time.sleep( 1 )
            print( "2...", end=" " )
            sys.stdout.flush()
            time.sleep( 1 )
            print( "1..." )
            sys.stdout.flush()
            time.sleep( 1 )

            audio_generator.emit_audio()

        if not self._file:
            print( "\n{}".format( message.upper() ) )


    def build_character_list( self ):
        if self._custom_alphabet:
            characters = self._custom_alphabet
        else:
            characters = [ "K", "M", "R", "S", "U", "A", "P", "T", "L", "O",
                           "W", "I", ".", "N", "J", "E", "F", "0", "Y", ",",
                           "V", "G", "5", "/", "Q", "9", "Z", "H", "3", "8",
                           "B", "?", "4", "2", "7", "C", "1", "D", "6", "X",
                           "BT", "SK", "AR", "AA", "AS", "VE", "IN", "HH",
                           "KA", "CT", "KN", "NJ", "SN" ]

            if self._level != 0:
                characters = characters[ :self._level ]

        return characters


    def build_words( self ):
        file            = self.locate_wordfile( self._word_file )
        words           = set()
        regexp          = re.compile( "^{0}{{{1},{2}}}$".format( "[{}]".format( re.escape( "".join( self._characters ) ).lower() ), self._word_char_min, self._word_char_max ), re.IGNORECASE )

        with open( file, encoding='utf-8' ) as wlf:
            for line in wlf:
                word    = line.strip()

                if regexp.match( word ) is not None:
                    words.add( word )

        words           = list( words ) # uniquify

        finalized_words = [ rng().choice( words ).upper() for i in range( self._word_count ) ]
        combined_words  = []

        for index, word in enumerate( finalized_words ):
            if self._callsign_mode:
                separator = " "
            elif index < self._word_count:
                separator = random.choice( self._word_separators )

                if separator != " ":
                    separator += " "
            else:
                separator = "."

            combined_words.append( word )
            combined_words.append( separator )


        return "".join( combined_words )


    def build_callsigns( self ):
        file                = self.locate_wordfile( "callsigns.txt" )
        callsigns           = set()

        with open( file, encoding='utf-8' ) as wlf:
            for line in wlf:
                callsign    = line.strip()

                if callsign is not None:
                    callsigns.add( callsign )

        callsigns           = list( callsigns ) # uniquify

        finalized_callsigns = [ rng().choice( callsigns ).upper() for i in range( self._callsign_count ) ]
        combined_callsigns  = []

        for index, callsign in enumerate( finalized_callsigns ):
            combined_callsigns.append( callsign )
            combined_callsigns.append( " " )


        return "".join( combined_callsigns )


    def locate_wordfile( self, file=None ):
        common_word_files   = []
        static_dir          = os.path.join( os.path.dirname( os.path.abspath( __file__ ) ), 'static' )

        if file is not None:
            common_word_files.append( os.path.join( static_dir, file ) )
            common_word_files.append( os.path.expanduser( file ) )

        common_word_files.extend( [ os.path.join( static_dir, "english.txt" ) ] )

        for wfile in common_word_files:
            if os.path.isfile( wfile ):
                return wfile


    def build_characters( self ):
        letters = ( random.choice( self._characters ) for i in range( self._character_count ) )
        return "".join( self.build_characters_insertspaces( letters ) )


    def build_characters_insertspaces( self, letters ):
        word_length         = random.randint( 1, 8 )
        count               = 0

        for letter in letters:
            if count >= word_length:
                word_length = random.randint( 1, 8 )
                count       = 0

                yield " "

            count += 1

            yield letter



class KochTrainerAudioGen:
    def __init__( self, message, effective_speed=20, character_speed=20, hertz=770, bandwidth=200 ):
        self._effective_speed       = effective_speed
        self._character_speed       = max( character_speed, self._effective_speed )
        self._hertz                 = hertz
        self._bandwidth             = bandwidth
        self._cached_letter_sounds  = {}

        self._letters               = {
            "A": (self.dit, self.dah),
            "B": (self.dah, self.dit, self.dit, self.dit),
            "C": (self.dah, self.dit, self.dah, self.dit),
            "D": (self.dah, self.dit, self.dit),
            "E": (self.dit,),
            "F": (self.dit, self.dit, self.dah, self.dit),
            "G": (self.dah, self.dah, self.dit),
            "H": (self.dit, self.dit, self.dit, self.dit),
            "I": (self.dit, self.dit),
            "J": (self.dit, self.dah, self.dah, self.dah),
            "K": (self.dah, self.dit, self.dah),
            "L": (self.dit, self.dah, self.dit, self.dit),
            "M": (self.dah, self.dah),
            "N": (self.dah, self.dit),
            "O": (self.dah, self.dah, self.dah),
            "P": (self.dit, self.dah, self.dah, self.dit),
            "Q": (self.dah, self.dah, self.dit, self.dah),
            "R": (self.dit, self.dah, self.dit),
            "S": (self.dit, self.dit, self.dit),
            "T": (self.dah,),
            "U": (self.dit, self.dit, self.dah),
            "V": (self.dit, self.dit, self.dit, self.dah),
            "W": (self.dit, self.dah, self.dah),
            "X": (self.dah, self.dit, self.dit, self.dah),
            "Y": (self.dah, self.dit, self.dah, self.dah),
            "Z": (self.dah, self.dah, self.dit, self.dit),
            "1": (self.dit, self.dah, self.dah, self.dah, self.dah),
            "2": (self.dit, self.dit, self.dah, self.dah, self.dah),
            "3": (self.dit, self.dit, self.dit, self.dah, self.dah),
            "4": (self.dit, self.dit, self.dit, self.dit, self.dah),
            "5": (self.dit, self.dit, self.dit, self.dit, self.dit),
            "6": (self.dah, self.dit, self.dit, self.dit, self.dit),
            "7": (self.dah, self.dah, self.dit, self.dit, self.dit),
            "8": (self.dah, self.dah, self.dah, self.dit, self.dit),
            "9": (self.dah, self.dah, self.dah, self.dah, self.dit),
            "0": (self.dah, self.dah, self.dah, self.dah, self.dah),
            "/": (self.dah, self.dit, self.dit, self.dah, self.dit),
            ".": (self.dit, self.dah, self.dit, self.dah, self.dit, self.dah),
            ",": (self.dah, self.dah, self.dit, self.dit, self.dah, self.dah),
            "?": (self.dit, self.dit, self.dah, self.dah, self.dit, self.dit),
            " ": (self.space,),

            #
            # Prosigns
            #

            "AA": (self.dit, self.dah, self.dit, self.dah),
            "AR": (self.dit, self.dah, self.dit, self.dah, self.dit),
            "AS": (self.dit, self.dah, self.dit, self.dit, self.dit),
            "VE": (self.dit, self.dit, self.dit, self.dah, self.dit),
            "INT": (self.dit, self.dit, self.dah, self.dit, self.dah),
            "HH": (self.dit, self.dit, self.dit, self.dit, self.dit, self.dit, self.dit, self.dit),
            "BT": (self.dah, self.dit, self.dit, self.dit, self.dah),
            "KA": (self.dah, self.dit, self.dah, self.dit, self.dah),
            "CT": (self.dah, self.dit, self.dah, self.dit, self.dah),
            "KN": (self.dah, self.dit, self.dah, self.dah, self.dit),
            "NJ": (self.dah, self.dit, self.dit, self.dah, self.dah, self.dah),
            "SK": (self.dit, self.dit, self.dit, self.dah, self.dit, self.dah),
            "SN": (self.dit, self.dit, self.dit, self.dah, self.dit)
        }

        dit                 = 1.2 / self._character_speed
        t_a                 = ( 60 * self._character_speed - 37.2 * self._effective_speed ) / ( self._character_speed * self._effective_speed )

        self._dit           = dit
        self._dah           = dit * 3
        self._inter_symbol  = dit
        self._inter_letter  = ( t_a * 3 ) / 19.0
        self._inter_word    = ( t_a * 7 ) / 19.0

        self._audio         = self.generate_audio( message )

    def save_file( self, file ):
        with open( file, "wb" ) as f:
            audiogen.write_wav( f, self._audio )


    def emit_audio( self ):
        try:
            stream = audiogen.sampler.play( itertools.chain( self._audio, audiogen.beep() ), blocking=True )
        except KeyboardInterrupt:
            # So further messages don't start with "^C"
            print( "" )


    def generate_audio( self, text ):
        letter_sounds       = [ self.generate_letter_sound( l ) for l in text ]
        band_pass_filter    = audiogen.filters.band_pass( self._hertz, self._bandwidth )

        return band_pass_filter( band_pass_filter( band_pass_filter( itertools.chain( *letter_sounds ) ) ) )


    @audiogen.sampler.cache_finite_samples
    def generate_letter_sound( self, letter ):
        if letter in self._cached_letter_sounds:
            return self._chached_letter_sound[ letter ]

        tones                                   = [ gen() for gen in self._letters[ letter ] ]
        spaces                                  = [ gen() for gen in [ self.inter_symbol ] * ( len( tones ) - 1 ) + [ self.inter_letter ] ]
        letter_sound                            = [ symbol for pair in zip( tones, spaces ) for symbol in pair ]

        self._cached_letter_sounds[ letter ]    = itertools.chain( *letter_sound )

        return self._cached_letter_sounds[ letter ]


    def generate_tone( self, seconds ):
        tone = audiogen.crop( audiogen.util.volume( audiogen.tone( self._hertz ), -3 ), seconds )
        return tone


    def dit( self ):
        for sample in self.generate_tone( self._dit ):
            yield sample


    def dah( self ):
        for sample in self.generate_tone( self._dah ):
            yield sample


    def space( self ):
        for sample in audiogen.silence( self._inter_word ):
            yield sample


    def inter_symbol( self ):
        for sample in audiogen.silence( self._inter_symbol ):
            yield sample


    def inter_letter( self ):
        for sample in audiogen.silence( self._inter_letter ):
            yield sample




def main():
    import argparse

    parser = argparse.ArgumentParser()

    #
    # Global Commands
    #

    parser.add_argument( "--character-speed", type=float, default=20,
                         help="Morse words per minute." )

    parser.add_argument( "--effective-speed", type=float, default=20,
                         help="Effective words per minute (farnsworth speed)." )

    parser.add_argument( "-f", "--file", type=str, default=None,
                         help="Save audio to a WAV file." )

    parser.add_argument( "-H", "--hertz", type=float, default=770,
                         help="Frequency in Hertz to use for practise tones." )

    parser.add_argument( "-B", "--bandwidth", type=float, default=200,
                         help="Audio bandwidth in Hertz, centered on the tone frequency." )

    #
    # Random Character Mode Commands (Default Mode)
    #

    parser.add_argument( "-l", "--level", type=int, default=1,
                         help="Koch training level (one character added per level)." )

    parser.add_argument( "-a", "--custom-alphabet", type=str, default=None,
                         help="Custom alphabet to use in place of default Koch ordering." )

    parser.add_argument( "--character-count", type=int, default=100,
                         help="In random character mode, the number of characters to be output." )

    #
    # Word Generator Specific Commands
    #

    parser.add_argument( "--callsign-mode", action="store_true", default=False,
                         help="Practice call sign recognition." )

    parser.add_argument( "--callsign-count", dest="callsign_count", type=int, default=20,
                         help="Generate exactly X callsigns.")

    #
    # Word Generator Specific Commands
    #

    parser.add_argument( "--word-mode", action="store_true", default=False,
                         help="Practice real word recognition." )

    parser.add_argument( "--word-char-min", dest="word_char_min", type=int, default=1,
                         help="Generate words containing at least X characters.")

    parser.add_argument( "--word-char-max", dest="word_char_max", type=int, default=5,
                         help="Generate words containing at most X characters.")

    parser.add_argument( "--word-count", dest="word_count", type=int, default=20,
                         help="Generate exactly X words.")

    parser.add_argument( "--word-file", type=str, default=None,
                         help="Word file from which to pull random words. Default is 'english.txt', which is a list of the 3,000 most common english words. Also available are 'english-long.txt' and 'english-all.txt'. You can also pass an absolute path to a specific file. Each word must be on its own line" )

    parser.add_argument( "message", nargs="*", default=None )

    args = parser.parse_args()

    trainer = KochTrainer( args )
    trainer.run()

    return 0

if __name__ == "__main__":
    sys.exit(main())