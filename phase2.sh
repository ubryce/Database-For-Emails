#!/bin/bash

echo phase 1: created .txt files
python3 phase1.py

echo phase 2: sorted .txt files and indexing
chmod u+x break.pl
rm -f re.idx | sort recs.txt -u | ./break.pl | db_load -c duplicates=1 -T -t hash re.idx
rm -f te.idx | sort terms.txt -u | ./break.pl | db_load -c duplicates=1 -T -t btree te.idx
rm -f em.idx | sort emails.txt -u | ./break.pl | db_load -c duplicates=1 -T -t btree em.idx
rm -f da.idx | sort dates.txt -u | ./break.pl | db_load -c duplicates=1 -T -t btree da.idx
