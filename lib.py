import re
import sqlite3
import time

import dictdlib
from pprint import pprint

sqlite3.paramstyle = 'qmark'


class WordTemplater(object):
    sep = "\t"

    def print_word(self, data):
        # word = data[0]
        meaning_tree = data[1]

        if 'unparsed' in meaning_tree:
            print(meaning_tree['unparsed'])
            return

        print("[%s]" % meaning_tree['transcription'])
        for key, piece in meaning_tree['pieces'].items():
            print("\033[1;30m%s\033[0m" % key)
            self.print_piece(piece)
        return

    def print_piece(self, piece):
        for num, group in enumerate(piece):
            # print "  %i" % num,
            self.print_group(group)
        return

    def print_group(self, group):
        print(self.sep + "\033[1;34m%s\033[0m" % group[0])
        for meaning in group[1:]:
            print(2*self.sep + "\033[0;35m%s\033[0m" % meaning)


class WordKeeper(object):
    """
    Database interface
    """

    def __init__(self, dbname='worddb.sqlite3'):
        """ Establishes connection with database """

        # Creating connection
        self.conn = sqlite3.connect(dbname)
        cur = self.conn.cursor()

        # For debugging
        # cur.execute('DROP TABLE IF EXISTS words;')
        # cur.execute('DROP TABLE IF EXISTS searches;')
        # cur.execute('DROP TABLE IF EXISTS tests;')

        # Creating tables if not exist yet
        cur.execute(
            'CREATE TABLE IF NOT EXISTS words (word CHARACTER(50), active);')
        cur.execute(
            'CREATE TABLE IF NOT EXISTS searches (wordid, timestamp);')
        cur.execute(
            'CREATE TABLE IF NOT EXISTS tests (wordid, timestamp, success);')
        cur.close()
        return

    def __del__(self):
        """ Closes connection to the database """
        self.conn.close()

    def add_word(self, word):
        """ Adds word to the database (if not in it already)
        and logs the time of the query 
        """

        cur = self.conn.cursor()
        row = cur.execute(
            'SELECT ROWID FROM words WHERE word=?', [word]).fetchone()
        if row:
            # Word already in DB
            wordid = row[0]
        else:
            # Word is queried at first time
            cur.execute(
                "INSERT INTO words (word, active) VALUES (?, 1)", [word])
            wordid = cur.execute(
                'SELECT ROWID FROM words WHERE word=?', [word]
            ).fetchone()[0]

        # Logging search attempt
        cur.execute(
            'INSERT INTO searches (wordid, timestamp)\
            VALUES (?, strftime("%s"));',
            [wordid])

        cur.close()
        self.conn.commit()

    def get_words_list(self, ts_from=0, ts_to=None):
        # Handling request conditions
        if ts_to is None:
            ts_to = time.time() + 1
        where_values = [ts_from, ts_to]
        query = "SELECT words.word, COUNT(*) cnt \
            FROM words, searches \
            WHERE words.ROWID=searches.wordid \
                AND strftime('%s', timestamp) \
                    BETWEEN strftime('%s', ?) AND strftime('%s', ?)\
            GROUP BY searches.wordid \
            ORDER BY cnt"

        # Requesting
        cur = self.conn.cursor()
        cur.execute(query, where_values)
        return cur.fetchall()


class WordFinder(object):
    """ Incapsulates word-finding and parsing functions """

    def __init__(self, path='dict/mueller7/mueller7'):
        try:
            self.dictdb = dictdlib.DictDB(path, 'read')
        except IOError as e:
            print('Cannot find the dictionary, exiting.')
            exit()

    def find_word(self, word):
        """
        Returns parsed data in format:
        [ word, word_data ]

        word_data = { 'unparsed' : raw_data     # if set -- parsing failed
            'transcription' : transcription,
            'pieces' : structured data }
        """

        if self.dictdb.hasdef(word):
            # Found word
            ret = [word]
            for article in self.dictdb.getdef(word):
                try:
                    ret.append(self.parse_mueller(article))
                except Exception as e:
                    ret.append({'unparsed': article})
        else:
            # Word not found
            ret = None
        return ret

    @staticmethod
    def trim(text):
        """ Truncate space symbols from start, end and between words """
        text = re.sub(r"^\s|\s$", '', text)
        text = re.sub(r"\n|\t", ' ', text)
        text = re.sub(r"\s+", ' ', text)
        return text

    @staticmethod
    def parse_mueller(article):
        """ Parse Mueller's dictionary article into structure
        Structure:
        [tracscription, speech_parts]
        speech_parts = {
            'n' : [ [tr1_1, tr1_2, ...],
                    [tr2_1, tr2_2, ...],
                    ... ],
            ...,
            'v' : ... }
        """
        speech_parts = {}

        # Whole article level
        items = re.split(r'[0-9]\.', article)

        if len(items) == 1:
            # One-meaning word
            [name, tmp] = re.split(r'\[', article)
            items = re.split(r'\]', tmp)

        transcription = re.sub(r'.*\[|\].*', '', items[0])
        transcription = WordFinder.trim(transcription)

        for item in items[1:]:
            # Speech parts level
            subitems = re.split(r'[0-9]{1,}\)', item)

            if len(subitems) == 1:
                # One-meaning speech-part
                [speech_part, tmp] = re.split(r'\.', subitems[0], maxsplit=1)
                speech_part = WordFinder.trim(re.sub(r'_', '', speech_part))
                subitems.append(tmp)
            else:
                speech_part = WordFinder.trim(
                    re.sub(r'_(\w)\.', r"\1", subitems[0]))

            speech_parts[speech_part] = []

            for subitem in subitems[1:]:
                # Translations level
                meanings = map(WordFinder.trim, re.split(r';\s*', subitem))
                speech_parts[speech_part].append(meanings)

        return {
            'transcription': transcription,
            'pieces': speech_parts
        }


if __name__ == '__main__':
    # Testing the word search time filtering
    import time
    ts = time.time() - 3600

    keeper = WordKeeper("./worddb.sqlite3")
    l = keeper.get_words_list(ts_from=ts)
    pprint(l)
