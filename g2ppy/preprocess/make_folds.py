#!/usr/bin/python
'''python make_folds.py inputdir workingdir bad_dicts.txt
   Makes the directories workingdir/train, workingdir/dev, and workingdir/eval if they don't exist.
   For each file in inputdir: 
     If filename contains the word "wikipedia", just move it to train.
     If filename is in bad_dicts.txt, just ignore it.
     Otherwise, divide it 60/20/20 between train, dev, and eval on a line-by-line basis.
   Characters not allowed in phonetisaurus }, |, and _ are eliminated.
   Warning: this will overwrite existing files, but won't check to make sure train,
     dev and eval are empty before starting.
'''

import sys,os,re,logging

bracket=re.compile(r'[\}\|]')
dash = re.compile(r'_')
##########################################################################################
def subsetdirs(workingdir):
    traindir = os.path.join(workingdir,'train')
    os.makedirs(traindir,exist_ok=True)
    devdir = os.path.join(workingdir,'dev')
    os.makedirs(devdir,exist_ok=True)
    evaldir = os.path.join(workingdir,'eval')
    os.makedirs(evaldir,exist_ok=True)
    return(traindir,devdir,evaldir)

##########################################################################################
def make_train_dev_eval(inputpath, foldfiles):
    logging.info('Splitting %s to %s, %s, %s'%(inputpath,foldfiles[0],foldfiles[1],foldfiles[2]))
    with open(inputpath) as f:
        lines = f.readlines()

    with open(foldfiles[0],'a') as trainfile:
        with open(foldfiles[1],'a') as devfile:
            with open(foldfiles[2],'a') as evalfile:
                for n in range(0,len(lines)):
                    if n%5==3:
                        devfile.write(lines[n])
                    elif n%5==4:
                        evalfile.write(lines[n])
                    else:
                        trainfile.write(lines[n])                                

##########################################################################################
def copy_to_train(inputpath, foldfiles):
    logging.info('Appending %s to train split in %s'%(inputpath,foldfiles[0]))
    with open(inputpath) as f:
        #lines = [ re.sub(dash,'-',line) for line in f.readlines() if not re.match(bracket,line) ]
        lines = f.readlines()
    with open(foldfiles[0],'a') as g:
        g.write('\n'.join(lines)+'\n')
                     
####################################################################################
if __name__=="__main__":
    if len(sys.argv)<4:
        print(__doc__)
        exit(0)

    inputdir = sys.argv[1]
    workingdir = sys.argv[2]
    bad_dicts_file = sys.argv[3]

    # Read the list of bad_dicts
    with open(bad_dicts_file) as f:
        bad_dicts = set([ os.path.basename(x.strip()) for x in f.readlines() ])
    
    make_train_dev_eval(inputdir, workingdir, bad_dicts)
    
