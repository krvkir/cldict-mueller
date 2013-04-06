#!/usr/bin/python2

import sys
from lib import *

finder = WordFinder()
keeper = WordKeeper()
templater = WordTemplater()

# Searching in infinite loop
while True:
    print "\n\033[1;31mSearch> ",
    try:
        line = sys.stdin.readline().lower()[:-1]
    except KeyboardInterrupt as e:
        print("\nLeaving.\033[0m")
        for record in keeper.get_words_list():
            print(record[0])
        exit()
    print "\033[0m",

    data = finder.find_word(line)
    if data:
        keeper.add_word(data[0])
        templater.print_word(data)
    else:
        print("Not found.")

    
#    for [transcription, speech_parts] in finder.find_word(line):
#        print('[ %s ]' % transcription)
#        for speech_part, items in speech_parts.items():
#            print(speech_part)
#            for meanings in items:
#                print("\t" + meanings[0])
