collector
=========

collector is a python script that one can use to create book "Collections" on
the Sony Reader (PRS-T1) ereader. The script will search for directories
containing a file named ".collection" and add all other files in that directory
to a Collection named after the directory. For instance, if you have a bunch of
pdf files in the directory "/media/READER/Papers/", along with a .collection
file, this script will add each of the pdf files to a (newly created) Collection
called "Papers".

A couple of sidenotes:

- If a Collection with a certain name already exists, files will be added to
  the existing Collection instead
- This script does *not* remove Collections or books from your device, it will
  *only* add existing books to existing Collections.
- Books that you want to add to Collections *have* to be known to the reader
  before collector is able to add them; this means that in order to add newly
  uploaded books to a Collection you must first uncouple the device from your
  computer after uploading, then wait for it to add the books to the internal
  database, then reconnect the device and only then will collector be able to
  add your books to a Collection.
- collector creates a backup of the database on your reader and will restore
  this in case of failure of any kind
- If, for whatever reason, the database gets corrupted or something else goes
  wrong you can make the Sony Reader rebuild the database by removing the
  "books.db" file from /path/to/READER/Sony_Reader/database/. WARNING: THIS WILL
  ERASE ALL INFORMATION ABOUT BOOKS ON YOUR DEVICE, INCLUDING INFORMATION ON
  COLLECTIONS ETC. USE WITH EXTREME CAUTION!
