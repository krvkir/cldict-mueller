import sys, sqlite3
sqlite3.paramstyle = 'qmark'

if len(sys.argv) < 2:
    exit()

word = sys.argv[1]

class WordKeeper(object):
    def __init__(self, dbname = 'worddb.sqlite3'):
        # Creating connection
        self.conn = sqlite3.connect(dbname)
        cur = self.conn.cursor()
       
        # For debugging
        #cur.execute('DROP TABLE IF EXISTS words;')
        #cur.execute('DROP TABLE IF EXISTS searches;')
        #cur.execute('DROP TABLE IF EXISTS tests;') 
        
        # Creating tables if not exist yet
        cur.execute('CREATE TABLE IF NOT EXISTS words (word CHARACTER(50), active);')
        cur.execute('CREATE TABLE IF NOT EXISTS searches (wordid, timestamp);')
        cur.execute('CREATE TABLE IF NOT EXISTS tests (wordid, timestamp, success);')
        cur.close()
        return

    def __del__(self):
        self.conn.close()

    def add_word(self, word):
        cur = self.conn.cursor()
        row = cur.execute('SELECT ROWID FROM words WHERE word=?', [word]).fetchone()
        if row:
            # Word already in DB
            print('Found word')
            wordid = row[0]
        else:
            # Word is queried at first time
            cur.execute("INSERT INTO words (word, active) VALUES (?, 1)", [word])
            print("'%s' added." % word)
            wordid = cur.execute('SELECT ROWID FROM words WHERE word=?', [word]).fetchone()[0]

        # Logging search attempt
        print("Word ID = %s" % wordid)
        cur.execute('INSERT INTO searches (wordid, timestamp) VALUES (?, strftime("%s"));', [wordid])

        cur.close()
        self.conn.commit()

dc = WordKeeper()
dc.add_word(word)

print(dc.conn.cursor().execute('SELECT * FROM words;').fetchall())
print(dc.conn.cursor().execute('SELECT * FROM searches;').fetchall())

dc.add_word(word)
