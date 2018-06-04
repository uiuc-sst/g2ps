#!/usr/local/bin/python3
import io,sys,os,re
import csv
from collections import deque
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
isocolumn = 0
g2pcolumn = 2
phoiblefilename = 'phoibletable.csv'

############################################################3
# Read the phoible table
ipa2feats = {}
with open(phoiblefilename) as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        ipa2feats[row[0]] = row

############################################################3
# Read the HTML file
with open(htmlfilename) as f:
    s = f.read()

table = etree.HTML(s).find("body/table")

not_in_ipafeats = {}
for row in iter(table):
    isocode = row[isocolumn].text.strip().rstrip()
    urllist = [ x.get('href') for x in row[g2pcolumn] ]
    g2plist = [ x for x in urllist if isinstance(x,str) and 'http' not in x ]

    if len(g2plist) > 0:
        for g2p in g2plist:
            (filename, extension) = os.path.splitext(g2p)
            with open('../'+filename+'.txt') as f:
                for line in f:
                    p = deque(line.rstrip().split())
                    if len(p) > 1:
                        g = p.popleft()                    
                        for ph in p:
                            if ph not in ipa2feats:
                                not_in_ipafeats[ph] = True
                                print('{}: {} in {}'.format(filename,ph,line.rstrip()))
                

#for k in not_in_ipafeats.keys():
#    print('{} is missing from {}'.format(k,phoiblefilename))
    
