#!/usr/bin/env python
import os
import sys
import shutil
import sqlite3

#READER_DIR = 'e:/'
READER_DIR = '/media/READER/'
DB_PATH = os.path.join(READER_DIR, 'Sony_Reader/database/books.db')
DB_BACKUP = DB_PATH + '.bak'
try:
    shutil.copyfile(DB_PATH, DB_BACKUP)
except:
    print u'Could not create backup!'
    sys.exit(1)

try:

    DB_CONN = sqlite3.connect(DB_PATH)

    # Find collectable dirs
    # collectable_dirs = {}
    collectable_files = {}
    for root, dirs, files in os.walk(READER_DIR):
        if '.collection' in files:
            name = root[root.rfind('/') + 1:]
            # collectable_dirs[name] = root
            collectable_files[name] = files
            collectable_files[name].remove('.collection')
        
    with DB_CONN as conn:
        c = conn.cursor()
        for root, files in collectable_files.items():
            ids = []
            for f in files:
                c.execute('''SELECT _id FROM books WHERE file_name = (?) OR 
                        file_path LIKE (?)''', (f, "%" + f + "%",))
                results = c.fetchone()
                if not results:
                    print u'Could not get ID for ' + f + '!'
                    continue
                ids.append(results[0]) # Book only has one unique ID
            collectable_files[root] = ids

        for root in collectable_files:
            # Make sure the collection exists
            c.execute('''SELECT _id FROM collection WHERE title = (?)''', 
                    (root,))
            results = c.fetchone()
            if not results:
                c.execute('''INSERT OR IGNORE INTO collection (title, kana_title, 
                        source_id, uuid) VALUES (?, ?, ?, ?)''', 
                        (root, '', 0, ''))
                c.execute('''SELECT _id FROM collection WHERE title = (?)''', 
                        (root,))
                results = c.fetchone()
                if not results:
                    print u'Could not get collection ID for ' + root + '!'
                    continue
            coll_id = results[0]
            for index, f_id in enumerate(collectable_files[root]):
                c.execute('''SELECT * FROM collections WHERE collection_id = 
                        (?) AND content_id = (?)''', (coll_id, f_id))
                if c.fetchone():
                    print u'Book already in collection, moving on!'
                    continue
                c.execute('''INSERT INTO collections (collection_id, content_id,
                        added_order) VALUES (?, ?, ?)''', (coll_id, f_id, index))
                print u'Added to collection "' + root + '"!'
            
except Exception, e:
    print u'Something went wrong:'
    print e
    print u'Reverting to backup!'
    shutil.copyfile(DB_BACKUP, DB_PATH)
