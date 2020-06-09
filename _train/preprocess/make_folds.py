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

import sys,os,re

dash = re.compile(r'_')
bracket = re.compile(r'[\}\|]')
##########################################################################################
def make_train_dev_eval(inputdir, workingdir, bad_dicts):
    inputfiles = os.listdir(inputdir)

    traindir = os.path.join(workingdir,'train')
    os.makedirs(traindir,exist_ok=True)
    devdir = os.path.join(workingdir,'dev')
    os.makedirs(devdir,exist_ok=True)
    evaldir = os.path.join(workingdir,'eval')
    os.makedirs(evaldir,exist_ok=True)
    
    for inputfile in inputfiles:
        if inputfile not in bad_dicts:
            inputpath = os.path.join(inputdir,inputfile)
            outputfile = re.sub(r'_[^\.]*','',inputfile)
            with open(inputpath) as f:
                lines = [ re.sub(dash,'-',line) for line in f.readlines() if not re.match(bracket,line) ] 
            
                if os.path.isfile(os.path.join(traindir,outputfile)):
                    print('Augmenting {} with {}'.format(outputfile,inputfile))
                    writemode='a'
                else:
                    print('Creating {} from {}'.format(outputfile,inputfile))
                    writemode='w'

                if 'wikipedia' in inputfile:
                    with open(os.path.join(traindir,outputfile),writemode) as f:
                        f.write('\n'.join(lines)+'\n')

                else:
                    with open(os.path.join(traindir,outputfile),writemode) as trainfile:
                        with open(os.path.join(devdir,outputfile),writemode) as devfile:
                            with open(os.path.join(evaldir,outputfile),writemode) as evalfile:
                                for n in range(0,len(lines)):
                                    if n%5 == 0:
                                        trainfile.write(lines[n])
                                    elif n%5 == 1:
                                        trainfile.write(lines[n])
                                    elif n%5==2:
                                        trainfile.write(lines[n])
                                    elif n%5==3:
                                        devfile.write(lines[n])
                                    elif n%5==4:
                                        evalfile.write(lines[n])

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
    
