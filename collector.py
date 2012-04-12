#!/usr/bin/env python

#***********************************<Config>************************************
# READER_DIR specifies the path to the root directory of the Sony Reader. This
# can either be a linux path or a Windows drive. This configuration parameter is
# *not* optional, it must be configured for collector to work properly.

#READER_DIR = 'e:/'
READER_DIR = '/media/READER/'
#**********************************</Config>************************************

try:
    import os
    import sys
    import shutil
    import sqlite3
except ImportError:
    print u'Make sure the following modules are available:'
    print u'- os'
    print u'- sys'
    print u'- shutil'
    print u'- sqlite3'

db_path = os.path.join(READER_DIR, 'Sony_Reader/database/books.db')
db_backup = db_path + '.bak'
try:
    # Create a backup database file
    shutil.copyfile(db_path, db_backup)
except:
    print u'Could not create backup, exitting!'
    sys.exit(1)

try:
    # Find collectable dirs
    print u'Collecting \'.collection\' locations...',
    collectable_files = {}
    for root, dirs, files in os.walk(READER_DIR):
        if '.collection' in files:
            # Find the shortest name for the collection
            name = root[max(root.rfind('/'), root.rfind('\\')) + 1:]
            collectable_files[name] = files
            collectable_files[name].remove('.collection')
    print u'done!'
        
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        print u'Finding file indexes...',
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
        
        print u'Building Collection database...'
        for root in collectable_files:
            # Make sure the collection exists
            if 'y' not in raw_input('Process ' + root + '?').lower():
                continue

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
                print u'Added book to collection "' + root + '"!'
        print u'All done, disconnect your reader!'
            
except Exception, e:
    print u'Something went wrong:'
    print e
    print u'Reverting to backup!'
    shutil.copyfile(db_backup, db_path)
    sys.exit(1)
