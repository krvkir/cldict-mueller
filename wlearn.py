#!/usr/bin/python2

import os, sys
from lib import *

if os.path.islink(__file__):
    fname = os.readlink(__file__)
else:
    fname = __file__
basedir = os.path.dirname(os.path.abspath(fname))

finder = WordFinder(basedir + '/dict/mueller7/mueller7')
keeper = WordKeeper(basedir + '/worddb.sqlite3')
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
