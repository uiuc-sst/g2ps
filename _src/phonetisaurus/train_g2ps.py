#/usr/bin/python3
'''train_g2ps.py workdir
   For each dictionary in workdir/train, train a G2P using phonetisaurus, put it in workdir/models.
   If dev/dictionary also exists, then use it to calculate phone error rate.
'''

import os,sys,re,subprocess

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
	    modelname='%s_%d_%d_%d'%(language,model_order,seq1_max,seq2_max)
            with open(os.path.join('logs',modelname+'.log'),'w') as logfile:
		cmd=['phonetisaurus-align','--input='+os.path.join(workdir,'train',traindictfile)]
                cmd += ['--ofile='+os.path.join(workdir,'models',modelname+'.corpus')]
                cmd += ['--seq1_del=false','--seq2_del=false','--seq1_max=%d'%seq1_max]
                cmd += ['--seq2_max=%d'%seq2_max,'--grow=true']
                alignprocs[modelname] = subprocess.Popen(cmd, stdout=logfile, stderr=logfile)
                        
    # Second, estimate-ngram
    print('Now waiting on the align procs.  Starting an estimate-ngram proc for each, when it finishes')
    estimateprocs = {}
    while len(alignprocs) > 0:
        for modelname in alignprocs.keys():
            alignproc = alignprocs[modelname]
            if alignproc.poll() ne None:
                params = modelname.split('_')
                corpusname=os.path.join(workdir,'models',modelname+'.corpus')
                if os.path.isfile(corpusname):
                    cmd = [ 'estimate-ngram','-o',params[1].to_s,
                            '-t',corpusname,'-wl',os.path.join(workdir,'models',modelname+'.arpa') ]
                    estimateprocs[modelname]=subprocess.Popen(cmd,stdout=alignproc.stdout,
                                                              stderr=alignproc.stderr)
                del modelname from alignprocs  # delete it from the list once its done
                print('Done: align %s, %d align procs remaining'%(modelname,len(alignprocs)))

    # Third, phonetisaurus-arpa2wfst
    print('Now waiting on the align procs.  Starting an estimate-ngram proc for each, when it finishes')
    arpaprocs = {}
    while len(estimateprocs) > 0:
        for modelname in estimateprocs.keys():
            estimateproc = estimateprocs[modelname]
            if estimateproc.poll() ne None:
                params = modelname.split('_')
                arpaname=os.path.join('models',modelname+'.arpa')
                if os.path.isfile(arpaname):
                    cmd = [ 'phonetisaurus-arpa2wfst', '--lm='+arpaname ,
                            '--ofile='+os.path.join(workdir,'models',modelname+'.fst')
                    ]
                    arpaprocs[modelname]=subprocess.Popen(cmd,stdout=estimateproc.stdout,
                                                              stderr=estimateproc.stderr)
                del modelname from estimateprocs  # delete it from the list once its done
                print('Done: arpa2wfst %s, %d estimate procs remaining'%(modelname,len(estimateprocs)))

    # Fourth, phonetisaurus-g2pwfst
    print('Now waiting on the align procs.  Starting an estimate-ngram proc for each, when it finishes')
    g2pprocs = {}
    while len(arpaprocs) > 0:
        for modelname in arpaprocs.keys():
            arpaproc = arpaprocs[modelname]
            if arpaproc.poll() ne None:
                params = modelname.split('_')
                fstname=os.path.join(workdir,'models',modelname+'.fst')
                devname=os.path.join(workdir,'dev',language+'.txt')
                if os.path.isfile(fstname):
                    if os.path.isfile(devname):
                        with open(os.path.join(workdir,'dev_hyps',modelname+'.txt'),'w') as dev_hyp:
                            cmd = [ 'phonetisaurus-g2pfst','--model='+fstname,
                                    '--nbest=1','--beam=10000','--thresh=99.0',
                                    '--accumulate=false','--pmass=0.0','--nlog_probs=true',
                                    '--wordlist='+os.path.join(workdir,'dev_wlists',language+'.wlist')
                            ]
                            g2pprocs[modelname]=subprocess.Popen(cmd,stdout=dev_hyp,
                                                                 stderr=arpaproc.stderr)
                del modelname from arpaprocs  # delete it from the list once its done
                print('Done: g2pwfst %s, %d arpa2fst procs remaining'%(modelname,len(arpaprocs)))

