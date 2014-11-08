#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import time

from lib import *

# Input parameters
parser = argparse.ArgumentParser()
# parser.add_argument("num", help="Режим тестирования")
args = parser.parse_args()

# Getting path to dictionary
if os.path.islink(__file__):
    fname = os.readlink(__file__)
else:
    fname = __file__
basedir = os.path.dirname(os.path.abspath(fname))

finder = WordFinder(basedir + '/dict/mueller7/mueller7')
keeper = WordKeeper(basedir + '/worddb.sqlite3')
templater = WordTemplater()

# Remembering when session started
ts_sess_start = time.time()

# Searching in infinite loop
while True:
    print '\n\033[1;31mSearch> ',
    try:
        line = sys.stdin.readline().lower()[:-1]
    except KeyboardInterrupt as e:
        print "\n\033[1;31m",
        print "\nLeaving."
        print "New words for this session:"
        print "\033[0m",
        for record in keeper.get_words_list(
                ts_from=ts_sess_start):
            print "\t%s:\t%i" % (record[0], record[1])
        exit()
    print "\033[0m",

    data = finder.find_word(line)
    if data:
        keeper.add_word(data[0])
        templater.print_word(data)
    else:
        print("Not found.")
