#/usr/bin/python3
'''align_corpora.py traindir modelsdir logdir
   For each dictionary in listfile, train a G2P using phonetisaurus on train/dictfile.
   If dev/dictfile also exists, then use it to calculate phone error rate.
'''

import os,sys,re

if __name__=="__main__":
    if len(sys.argv)<4:
        print(__doc__)
        exit(0)
    traindir=sys.argv[1]
    modelsdir=sys.argv[2]
    logdir=sys.argv[3]
    
    lang2dict = { re.sub(r'.txt','',x.strip()):x.strip() for x in os.listdir(traindir) }
    os.makedirs(modelsdir,exist_ok=True)
    os.makedirs(logdir,exist_ok=True)

    alignprocs = {}
    for (language,traindictfile) in lang2dict.items():
        for seq1_max in (2, 3, 4):
	    for seq2_max in (2, 3, 4):
	        for model_order in (1, 2, 4, 8):
		    modelname='%s_%d_%d_%d'%(language,model_order,seq1_max,seq2_max)
                    with open(os.path.join('logs',modelname+'.log'),'w') as logfile:
		        cmd=['phonetisaurus-align','--input='+os.path.join('train',traindictfile),
                             '--ofile='+os.path.join('models',modelname+'.corpus'),
                             '--seq1_del=false','--seq2_del=false','--seq1_max=%d'%seq1_max,
                             '--seq2_max=%d'%seq2_max,'--grow=true'
                        ]
                        alignprocs[modelname] = subprocess.Popen(cmd, stdout=logfile, stderr=logfile)

    while len(alignprocs) > 0:
        for modelname in alignprocs.keys():
            alignproc = alignprocs[modelname]
            if alignproc.poll() ne None:
                del modelname from alignprocs  # delete it from the list once its done
                print('Done: align %s, %d align procs remaining'%(modelname,len(alignprocs)))

