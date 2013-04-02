import sys, re
import dictdlib



class WordFinder(object):
    """ Incapsulates word-finding and parsing functions """

    def __init__(self):
        self.dictdb = dictdlib.DictDB('dict/mueller7/mueller7', 'read')

    def find_word(self, word):
        ret = []
        if self.dictdb.hasdef(word):
            # Found word
            print("Found!")
            for article in self.dictdb.getdef(word):
                try:
                    ret.append(self.parse_mueller(article))
                except Exception as e:
                    ret.append([word, {'unparsed' : [[article]]}])
        else:
            # Word not found
            print("Not found.")
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
    
        for item in items[1:]:
            # Speech parts level
            subitems = re.split(r'[0-9]{1,}\)', item)

            if len(subitems) == 1:
                # One-meaning speech-part
                [speech_part, tmp] = re.split(r'\.', subitems[0], maxsplit=1)
                speech_part = WordFinder.trim(re.sub(r'_', '', speech_part))
                subitems.append(tmp)
            else:
                speech_part = WordFinder.trim(re.sub(r'_(\w)\.', r"\1", subitems[0]))

            speech_parts[speech_part] = []
    
            for subitem in subitems[1:]:
                # Translations level
                meanings = map(WordFinder.trim, re.split(r';\s*', subitem))
                speech_parts[speech_part].append(meanings)

        return [transcription, speech_parts]



################################################################################
# Exapmle: Run loop

finder = WordFinder()

# Searching in infinite loop
while True:
    line = sys.stdin.readline().lower()[:-1]
    for [transcription, speech_parts] in finder.find_word(line):
        print(transcription)
        for speech_part, items in speech_parts.items():
            print(speech_part)
            for meanings in items:
                print("\t" + meanings[0])
    
