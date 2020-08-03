#/usr/bin/python3
'''train_g2ps.py workdir
   For each dictionary in workdir/train, train a G2P using phonetisaurus, put it in workdir/models.
   If dev/dictionary also exists, then use it to calculate phone error rate.
'''

import os,sys,re,itertools

if __name__=="__main__":
    if len(sys.argv)<2:
        print(__doc__)
        exit(0)
    workdir=sys.argv[1]
    
    os.makedirs(os.path.join(workdir,'models'),exist_ok=True)
    os.makedirs(os.path.join(workdir,'dev_wlists'),exist_ok=True)
    os.makedirs(os.path.join(workdir,'dev_hyps'),exist_ok=True)
    os.makedirs(os.path.join(workdir,'logs'),exist_ok=True)
    
    lang2dict = { re.sub(r'_.*.txt','',x.strip()):x.strip() for x in os.listdir(os.path.join(workdir,'train')) }
    
    # First, phonetisaurus-align
    print('Starting the phonetisaurus-align processes')
    alignprocs = {}
    for (language,traindictfile) in lang2dict.items():
        for (seq1_max,seq2_max,model_order) in itertools.product((2, 3, 4),(2,3,4),(1,2,4,8)):
	    modelname = '%s_%d_%d_%d' % (language,model_order,seq1_max,seq2_max)
            print(modelname)
