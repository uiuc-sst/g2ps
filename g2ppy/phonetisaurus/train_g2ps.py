#/usr/bin/python3
'''train_g2ps.py workdir
   For each dictionary in workdir/train, train a G2P using phonetisaurus, put it in workdir/models.
   If dev/dictionary also exists, then use it to calculate phone error rate.
'''

import os,sys,re,subprocess, itertools, logging, tempfile
import cluster.agglomerative_cluster
import numpy as np
sys.path.append('../cluster')

######################################################################################################
def workingdirs(workdir):
    models=os.path.join(workdir,'models')
    os.makedirs(models,exist_ok=True)
    devresults=os.path.join(workdir,'devresults')
    os.makedirs(devresults,exist_ok=True)
    evalresults=os.path.join(workdir,'evalresults')
    os.makedirs(evalresults,exist_ok=True)
    return([models,devresults,evalresults])


######################################################################################################
def launch_subprocess(key,cmd):
    '''Create tempfiles for stdout and stderr, launch the subprocess, return the tempfiles'''
    cmdstr = ' '.join(cmd)
    outf = tempfile.TemporaryFile()
    errf = tempfile.TemporaryFile()
    proc = subprocess.Popen(cmd,stdout=outf,stderr=errf)
    return(key,proc,outf,errf,cmdstr)

def wait_for_process_to_finish(key,proc,outf,errf,cmdstr):
    '''Wait for proc to finish, then log its outf and errf and close the files'''
    logging.debug('Waiting for conclusion of %s'%(cmdstr))
    proc.wait()
    outf.seek(0)
    outstr = outf.read().decode()
    outf.close()
    logging.debug(cmdstr+' STDOUT:\n'+outstr)
    outf.close()
    errf.seek(0)
    errstr = errf.read().decode()
    errf.close()
    logging.debug(cmdstr+' STDERR:\n'+errstr)
    return(outstr, errstr)

def params_to_pathname(dirname, filename, params, ext):
    return(os.path.join(dirname, filename+'+'+'+'.join([str(p) for p in params]) + '.'+ext))

def paramsets_to_pathnames(dirname, filename, listofparamsets, ext):
    pathnames = []
    for params in itertools.product(*listofparamsets):
        pathnames.append(params_to_pathname(dirname, filename, params, ext))
    return(pathnames)

def pathname_to_params(pathname):
    parts = os.path.splitext(pathname)[0].split('+')
    return(parts[1:])
    
######################################################################################################
def emtrain(foldpaths,corpuspaths,language):
    logging.debug('phonetisaurus-align %s %s'%(language,foldpaths[0]))
    dictfile_cmd = ['phonetisaurus-align','--seq1_del=false','--seq2_del=false','--grow=true',
                    '--input='+foldpaths[0]]
    procs = []
    for corpuspath in corpuspaths:
        params = pathname_to_params(corpuspath)
        cmd = dictfile_cmd+['--seq1_max=%d'%params[0],'--seq2_max=%d'%params[1],'--ofile='+corpuspath]
        procs.append((launch_subprocess(corpuspath, cmd)))
        
    for corpuspath, proc, outf, errf, cmdstr in procs:
        wait_for_process_to_finish(corpuspath, proc, outf, errf, cmdstr)
                        
######################################################################################################
def lmtrain(foldpaths,corpuspaths,fstpaths,Nset,language):
    logging.debug('lmtrain %s'%(language))
    eprocs = []
    for corpuspath in corpuspaths:
        corpusparams = pathname_to_params(corpuspath)
        for N in Nset:
            params = corpusparams + [N]
            modelpath = params_to_pathname(modeldir,language,params,'arpa')
            cmd = [ 'estimate-ngram','-o',str(params[2]),'-t',corpuspath,'-wl',modelpath ]
            eprocs.append((launch_subprocess(modelpath, cmd)))
            
    aprocs = []
    for modelpath, proc, outf, errf, cmdstr, fstpath in zip(eprocs,fstpaths):
        wait_for_process_to_finish(modelpath, proc, outf, errf, cmdstr)
        params = pathname_to_params(modelpath)
        cmd = [ 'phonetisaurus-arpa2wfst', '--lm='+modelpath,'--ofile='+fstpath ]
        aprocs.append((launch_subprocess(fstpath, cmd)))
                
    for fstpath, proc, outf, errf, cmdstr in aprocs:
        wait_for_process_to_finish(fstpath, proc, outf, errf, cmdstr)
        
######################################################################################################
def test(foldpaths,workingdirs,language,fstpaths):
    logging.debug('phonetisaurus.test %s'%(language))
    logging.debug('Test %s'%(language))
    PER = {}
    for fstpath in fstpaths:
        params = pathname_to_params(fstpath)
        for fold in  [1,2]:
            wordlist = params_to_pathname(workingdirs[fold],language,params,'wlist')
            hyppath = params_to_pathname(workingdirs[fold],language,params,'txt')
            references = cluster.agglomerative_cluster.Language(language, 'aaa', fstpath, foldpaths[fold])
            # PER is string edit distance from the dictionary to the fst
            PER[hyppath], prons, ds = references.dist(references,'me')
            with open(hyppath,'w')  as f:
                for w in prons:
                    for pron in prons[w]:
                        f.write(w+'\t'+' '.join(pron))
            logging.info('PER %g for hypothesis %s'%(PER[hyppath],hyppath))
        
####################################################################################
if __name__=="__main__":
    if len(sys.argv)<2:
        print(__doc__)
        exit(0)
    workdir=sys.argv[1]

    phonetisaurus_train(workdir)
    
