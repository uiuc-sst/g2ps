#!/usr/local/bin/python3
import io,sys,os,re
from lxml import etree

USAGE='''USAGE: validate_phoneset.py
  Check to make sure that all IPA symbols of all G2Ps in ../index.html are found in phoibletable.csv.
  Assumes that ../index.html has just one table, with:
   ISO 639-3 code in 2nd column
   G2P files are named in every local URL (no "http") of the 5th column.
'''

if len(sys.argv) > 1:
    print(USAGE)
    exit(0)

htmlfilename = '../index.html'
isocolumn = 1
g2pcolumn = 4
phoiblefilename = 'phoibletable.csv'

############################################################3
# Read the HTML file
with open(htmlfilename) as f:
    s = f.read()

table = etree.HTML(s).find("body/table")
    
for row in iter(table):
    isocode = row[isocolumn].text
    urllist = [ x.get('href') for x in row[g2pcolumn] ]
    g2plist = [ x for x in urllist if 'http' not in x ]
    print('{}: {}'.format(isocode,urllist))
    print('{}: {}'.format(isocode,g2plist))
    
    
