#!/Users/jhasegaw/anaconda3/bin/python
import os
import sys
import re
from pprint import pprint
from html_table_parser import HTMLTableParser

USAGE='''USAGE: table2lexicon.py htmlfile tabspec1 [tabspec2 [...]]
  Read pronunciation lexicon from tables in htmlfile.
  tabspecN must have the format \d+:[cr]:\d+:\d+
  The first integer specifies which of the <table> blocks to read.
  The character c means read columns; r means to read rows.
  The second integer specifies which column or row is the "word",
  The third integer specifies which column or row is the "pronunciation".'''

if len(sys.argv) < 3:
    print(USAGE)
    exit(0)
htmlfilename = sys.argv[1]

############################################################
# Read table specifications from the command line
cols = {}
rows = {}
for n in range(2,len(sys.argv)):
    tmp = sys.argv[n].split(':')
    if len(tmp) < 4:
        print(USAGE)
        exit(0)
    nt = int(tmp[0])
    ng = int(tmp[2])
    np = int(tmp[3])
    if tmp[1] == 'c':
        if nt not in cols:
            cols[nt] = {}
        cols[nt][ng] = np
    elif tmp[1] == 'r':
        if nt not in rows:
            rows[nt] = {}
        rows[nt][ng] = np

############################################################3
# Read the HTML file
with open(htmlfilename) as f:
    content = f.read()

p = HTMLTableParser()
p.feed(content)

for nt in cols:
    for (ng,np) in cols[nt].items():
        for row in p.tables[nt]:
            print('{}\t{}'.format(row[ng],row[np]))
for nt in rows:
    for (ng,np) in rows[nt].items():
        rowg = p.tables[nt][ng]
        rowp = p.tables[nt][np]
        for col in range(0,min(len(rowg),len(rowp))):
            print('{}\t{}'.format(rowg[col],rowp[col]))
    
