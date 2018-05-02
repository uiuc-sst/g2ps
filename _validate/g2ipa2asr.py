#!/usr/local/bin/python3
import sys
import os.path
from urllib import request
import io
from collections import deque
import csv

USAGE='''g2ipa2asr.py g2ipa.txt asr2ipa.txt phoibletable.csv
   Generates an output g2asr.txt by compose(g2ipa,inverse(asr2ipa.txt)).
   g2ipa.txt -- text file, first word of each line is a grapheme, succeeding words are IPA.
   asr2ipa.txt -- text file, only two words per line: ASR phone symbol, and corresponding IPA.
   g2asr.txt -- same format as g2ipa.txt, but using ASR phone set.
   If g2ipa.txt includes IPA symbols that are not in aspire2ipa.txt, then
   the closest-matching symbols are used instead, where closest-matching is determined
   by measuring feature vectors in phoibletable.csv, and finding minimum L0 feature vector distance.
'''

if len(sys.argv) < 4:
    print(USAGE)
    exit(0)

g2ipa_filename = sys.argv[1]
asr2ipa_filename = sys.argv[2]
phoiblefilename = sys.argv[3]

# ipa2asr: str -> str, because an ipa2asr is required to be one-to-one
ipa2asr = {}
with open(asr2ipa_filename) as f:
    for line in f:
        p = line.rstrip().split()
        if len(p) > 1:
            ipa2asr[p[1]] = p[0]

# g2ipa: str -> array(str), because a g2ipa can be one-to-many
g2ipa = {}
not_in_asr = {}
with open(g2ipa_filename) as f:
    for line in f:
        p = deque(line.rstrip().split())
        if len(p) > 1:
            g = p.popleft()
            if not g in g2ipa:
                g2ipa[g] = []
            g2ipa[g].append(' '.join(p))
            # If any are missing from ipa2asr, mark them
            for ph in p:
                if ph not in ipa2asr:
                    not_in_asr[ph] = True

# If len(not_in_asr) > 0, read in the ipa2feats table
ipa2feats = {}
if len(not_in_asr) > 0:
    with open(phoiblefilename) as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            ipa2feats[row[0]] = row

        
# define a function that finds the asr phoneme with minimum distance
def nearest_in_table(phone, table, ipa2feats):
    phfeats = ipa2feats[phone]
    mincost = len(phfeats)+1
    bestoutput = '<unk>'
    for testph in table.keys():
        testfeats = ipa2feats[testph]
        # count the number of features that differ between testfeats and phfeats
        cost = len([n for n in range(0,len(phfeats)) if testfeats[n] != phfeats[n]])
        # if cost is less than mincost, then keep this one
        if cost < mincost:
            mincost = cost
            bestoutput = testph
    return(bestoutput)

# Now compose each entry in g2ipa with ipa2feats and ipa2asr
for (g,prons) in g2ipa.items():
    for pron in prons:
        p = pron.split()
        for n in range(0,len(p)):
            if p[n] == 'eps':
                p[n] = '' # arbitrary: add an entry mapping from 'eps' to zero-length output. I'm not quite sure what is the best way to deal with this
            else:
                if p[n] not in ipa2asr:
                    p[n] = nearest_in_table(p[n], ipa2asr, ipa2feats)
                p[n] = ipa2asr[p[n]]
        print('{}\t{}'.format(g,' '.join(p)))

          

    
