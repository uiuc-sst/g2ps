#!/usr/bin/python3
'''python generate_models_column.py modeldir refdir hypdir
   For each filename modeldir/*.fst, generate a link.
   If the corresponding .txt files also exist in both refdir and hypdir,
   load all lexical entries, and compute average phone error rate.
'''

from collections import deque
import os,sys,re
import editdistance
import numpy as np

def read_dict_from_file(filename):
    '''Read a dictionary from a file.  First word on each line is the key, remainder is the entry.'''
    dict = {}
    with open(filename) as f:
        for line in f:
            words = line.rstrip().split()
            dict[words[0]] = ' '.join(words[1:])
    return(dict)

if __name__=="__main__":
    if len(sys.argv)<4:
        print(__doc__)
        exit(0)

    modelsdir=sys.argv[1]
    refdir=sys.argv[2]
    hypdir=sys.argv[3]

    modelfiles = {}
    for modelfile in os.listdir(modelsdir):
        if re.search(r'_\d_\d_\d\.fst',modelfile):
            rootname = re.sub(r'\.fst','',modelfile)
            refdictfile = re.sub(r'_\d_\d_\d\.fst','.txt',modelfile)
            if refdictfile in modelfiles:
                modelfiles[refdictfile].append(rootname)
            else:
                modelfiles[refdictfile] = [ rootname ]
    refdicts=set(os.listdir(refdir))
    hypdicts=set(os.listdir(hypdir))
    
    for refdictfile in sorted(modelfiles.keys()):
        # If any model files were trained from this dictionary, then print a line
        outputline = []
        if refdictfile in refdicts:
            refdict = read_dict_from_file(os.path.join(refdir,refdictfile))
            for rootname in modelfiles[refdictfile]:
                if rootname+'.txt' in hypdicts:
                    hypdict = read_dict_from_file(os.path.join(hypdir,rootname+'.txt'))
                    pers = []        
                    for word in refdict.keys():
                        if word in hypdict:
                            refpron = refdict[word].split()
                            hyppron = deque(hypdict[word].split())
                            hypprob = hyppron.popleft()
                            pers.append(editdistance.eval(refpron,hyppron) / max(1,len(refpron)))
                    if len(pers)>0:
                        per = 100.0*np.mean(pers)
                        modelname=os.path.join(modelsdir,rootname+'.fst')
                        outputline.append(('%s(%3.1f)' % (modelname, per), per))
        if len(outputline)>0:               # If any phone error rates computed, choose the best
            bestpair = min(outputline, key=lambda p: p[1])
            print(bestpair[0])
        else:                               # Otherwise, sort the models, choose the last
            candidates = sorted(modelfiles[refdictfile])
            print('%s(N/A)'% os.path.join(modelsdir, candidates[-1]+'.fst'))
                
