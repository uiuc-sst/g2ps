import argparse, tempfile, os, sys, shutil, logging, re
from collections import defaultdict
import preprocess
import phonetisaurus
import cluster

###########################################################
def find_inputfiles(datapath, pronlexes, language, dicttypes):
    logging.debug('find_inputfiles(%s,%s,%s,%s)'%(str(datapath),str(pronlexes),language,str(dicttypes)))
    output_pronlexes = []
    for pronlex in pronlexes:
        if pronlex['dicttype'] in dicttypes:
            for d in datapath:
                candidate = os.path.join(d,pronlex['filename'])
                if os.path.exists(candidate):
                    output_pronlexes.append({**pronlex, 'path':candidate})
    return(output_pronlexes)

###########################################################
if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Train G2Ps in the specified languages.')
    parser.add_argument('languages',
                        help='''Colon-separated list of languages to train, e.g.,
                        Modern_Greek:Standard_Arabic.  Specified using ISO 639-3 
                        names, parentheticals removed, spaces turned to underscore, e.g.,
                        pycountry.languages.get(alpha_3="ell").name = "Modern Greek (1453-)" 
                        should be entered as "Modern_Greek". To train all, use the keyword "all".''')
    parser.add_argument('-P','--pronlexlist',
                        help='''Pathname of a text file containing a list of source pronlexes.
                        Each line of the file should contain three whitespace-separated columns: 
                        (1) language, (2) dicttype, (3) lexicon pathname.
                        Lexicon pathname should be relative to one of the directories in DATAPATH.
                        default: preprocess/pronlexlist.txt''',
                        default='preprocess/pronlexlist.txt')
    default_datapath='.:..:'+os.path.expanduser('~/data/dicts')
    parser.add_argument('-d','--datapath',
                        default=default_datapath,
                        help='''Paths (colon-separated) in which to search for pronlexes.
                        Default: %s'''%(default_datapath))
    parser.add_argument('--dicttypes',
                        help='''Colon-separated list of dictionary types to be processed, or [default]
                        "all". Available types are babel, celex, callhome, masterlex, wikipedia.
                        If there are source files not of this type, they are ignored.
                        ''',
                        default='all')
    #parser.add_argument('-l','--language',nargs='*',
    #                    help='''Language(s) for which you want to train G2Ps.
    #                    Default: all the languages in the pronlexlist''')
    #parser.add_argument('-L','--languagelist',
    #                    help='Text file, listing languages for which you want to train G2Ps')
    default_workingdir=os.path.join(os.getcwd(),'exp')
    parser.add_argument('-w','--workingdir',
                        default=default_workingdir,
                        help='Pathname of the working directory. Default: ./exp')
    parser.add_argument('-S','--stages',
                        default='all',
                        help='''Colon-separated list of stages of training that you wish to perform.
                        Will be performed in the order you specify.  
                        --- ALL means the following: ---
                        NORMALIZE: Convert source lexicons to IPA
                        SUBSET: Split lexicons into train, dev, and test subsets.
                        EMTRAIN: Train graphone probabilities using EM.
                        LMTRAIN: Train graphone language model, and parse to an FST.
                        TEST: Compute PER and WER on the eval test fold.
                        --- The following are not included  in "ALL" ---
                        PHONESET: Compute the phoneset for each language.
                        VALIDATE: Check to see if lexicons have bad entries.
                        ''')
    parser.add_argument('--logfile',default='-',
                        help='Logfile to which logging messages are printed. Default: console.')
    parser.add_argument('-v','--verbosity',default='warning',
                        help='''Print logging messages of this level and lower.
                        Options are: DEBUG, INFO, WARNING [default], ERROR, CRITICAL.''')
                        
    args = parser.parse_args()
    datapath = args.datapath.split(':')
    workingdir = args.workingdir
    pronlexes = defaultdict(list)
    with open(args.pronlexlist) as f:
        for line in f:
            if line[0] != '#':
                w=line.rstrip().split()
                language = w[0]
                if len(language)==3 and language.islower():
                    alpha3 = language
                    language = preprocess.normalize_dicts.alpha3_to_language(alpha3)
                else:
                    alpha3 = preprocess.normalize_dicts.language_to_alpha3(language)
                    if alpha3=='mis':
                        logging.warning('mis returned for %s %s %s'%(language,w[1],w[2]))
                pronlexes[language].append({'dicttype':w[1],'filename':w[2],'alpha3':alpha3})
                    
    if args.languages.upper()=='ALL':
        languages=set([x[0] for x in pronlexes])
    else:
        languages=set(args.languages.split(':'))
    if args.dicttypes.upper()=='ALL':
        dicttypes = set([lex['dicttype'] for lexlist in pronlexes.values() for lex in lexlist])
    else:
        dicttypes = set(args.dicttypes.split(':'))
    if args.stages.upper()=='ALL':
        stages=['normalize','subset','emtrain','lmtrain','test']
    else:
        stages = args.stages.split(':')

    loglevel = getattr(logging, args.verbosity.upper(), None)
    if not isinstance(loglevel, int):
        raise ValueError('Invalid verbosity level: %s' % args.verbosity)
    if args.logfile != '-':
        logging.basicConfig(filename=args.logfile, level=loglevel)
    else:
        logging.basicConfig(level=loglevel)

    folddirs = preprocess.make_folds.subsetdirs(workingdir)
    
    workdirs=phonetisaurus.train_g2ps.workingdirs(workingdir)
    S1set=[2,3,4]
    S2set=[2,3,4]
    Nset=[1,2,4,8]
    #S1set=[2]
    #S2set=[2]
    #Nset=[2]

    logging.debug('and hello again')
    
    for language in languages:
        foldpaths=[ os.path.join(d,language+'.txt') for d in folddirs ]
        normalized_dicts = []
        logging.debug('Performing stages %s'%(' '.join(stages)))
        for stage in stages:
            if stage=='phoneset':
                phonesetpath = os.path.join('..',language,'phoneset.txt')
                logging.debug('make phoneset in %s'%(phonesetpath))
                preprocess.validate_phoneset.make_phoneset(phonesetpath,r'.*symboltable.*\.txt')
            elif stage=='normalize':
                logging.debug('normalize %s'%(language))
                fullpaths = find_inputfiles(datapath, pronlexes[language], language, dicttypes)
                phonesetpath = os.path.join('..',language,'phoneset.txt')
                phoneset = preprocess.validate_phoneset.load_phoneset(phonesetpath)
                logging.debug('normalize %s: paths are %s'%(language,str(fullpaths)))
                os.makedirs(os.path.join(workingdir,'dicts'),exist_ok=True)
                for x in fullpaths:                    
                    normalized = os.path.join(workingdir,'dicts',re.sub(r'/','_',x['filename']))
                    preprocess.normalize_dicts.normalize_dict(x['path'],
                                                              normalized,
                                                              language,
                                                              x['alpha3'],
                                                              x['dicttype'],
                                                              phoneset)
            elif stage=='subset':
                fullpaths = find_inputfiles(datapath, pronlexes[language], language, dicttypes)
                for x in fullpaths:
                    normalized = os.path.join(workingdir,'dicts',re.sub(r'/','_',x['filename']))
                    if x['dicttype'].lower()=='wikipedia':
                        preprocess.make_folds.copy_to_train(normalized, foldpaths)
                    else:
                        preprocess.make_folds.make_train_dev_eval(normalized, foldpaths)
            elif stage=='validate':
                phonesetpath = os.path.join('..',language,'phoneset.txt')
                preprocess.validate_phoneset.validate_lexicons(foldpaths,phonesetpath)
            elif stage=='emtrain':
                logging.debug('emtrain %s'%(language))
                corpuspaths=phonetisaurus.train_g2ps.paramsets_to_pathnames(workdirs[0],language,
                                                                            [S1set,S2set],'corpus')
                phonetisaurus.train_g2ps.emtrain(foldpaths,corpuspaths,language)
            elif stage=='lmtrain':
                logging.debug('lmtrain %s'%(language))
                corpuspaths=phonetisaurus.train_g2ps.paramsets_to_pathnames(workdirs[0],language,
                                                                            [S1set,S2set],'corpus')
                fstpaths=phonetisaurus.train_g2ps.paramsets_to_pathnames(workdirs[0],language,
                                                                            [S1set,S2set,Nset],'fst')
                phonetisaurus.train_g2ps.lmtrain(foldpaths,corpuspaths,fstpaths,Nset,language)
            elif stage=='test':
                logging.debug('test %s'%(language))                
                fstpaths=phonetisaurus.train_g2ps.paramsets_to_pathnames(workdirs[0],language,
                                                                            [S1set,S2set,Nset],'fst')
                phonetisaurus.train_g2ps.test(foldpaths,workdirs,language,fstpaths)
