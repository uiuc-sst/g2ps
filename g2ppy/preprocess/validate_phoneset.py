import logging,os,re,phonetisaurus
from collections import defaultdict

def load_dict_from_txtfile(txtfile):
    '''Assume txtfile maps words to sequences of phones, but that 
    each word may have more than one possible pronunciation.
    Return a dict that maps words to lists of possible pronunciations, each of which is a string.
    '''
    x = {}
    with open(txtfile,encoding='utf-8') as f:
        for line in f:
            words = line.rstrip().split()
            if len(words)==0 or line[0]=='#':
                continue
            if words[0] not in x:
                x[words[0]] = []
            if len(words)>1:
                x[words[0]].append(' '.join(words[1:]))
    return(x)

def make_phoneset(phonesetpath,pattern):
    '''Create phoneset file so it contains the set of all phonemes specified in 
    dictionaries matching pattern in the same directory as the specified phonesetpath.'''
    phonesetdir, phonesetfile = os.path.split(phonesetpath)
    phoneset = set()
    for fname in os.listdir(phonesetdir):
        if re.match(pattern,fname):
            thislex = load_dict_from_txtfile(os.path.join(phonesetdir,fname))
            for pronlist in thislex.values():
                for pron in pronlist:
                    logging.debug('%s: %s -> phoneset'%(fname,pron))
                    phoneset |= set(pron.split())
    if len(phoneset)==0:
        logging.warn('No lexicons matching %s found in %s'%(pattern,phonesetpath))
        return(phoneset)
    else:
        logging.debug('%s will have %d phones'%(phonesetpath,len(phoneset)))
        if os.path.exists(phonesetpath):
            logging.warn('WARNING: over-writing %s'%(phonesetpath))
        with open(phonesetpath,'w') as f:
            f.write('\n'.join([p for p in sorted(phoneset)]))
        return(phoneset)

def load_phoneset(phonesetpath):
    with open(phonesetpath) as f:
        phoneset = set([ line.strip() for line in f.readlines() ])
    return(phoneset)
    
def validate_lexicons(lexiconpaths,phonesetpath):
    '''Check that all lexicons in lexiconpaths have only the phones in the file phonesetpath.
    If that is not true, print each offending phone and file to logging.WARN.
    '''
    ecount = defaultdict(lambda: defaultdict(lambda: 0))
    esample = defaultdict(lambda: {})
    with open(phonesetpath) as f:
        phoneset = set([ line.strip() for line in f.readlines() ])
    for lexpath in lexiconpaths:
        lex = load_dict_from_txtfile(lexpath)
        for (w,pronlist) in lex.items():
            for pron in pronlist:
                for p in pron.split():
                    if p not in phoneset:
                        ecount[lexpath][p] += 1
                        esample[lexpath][p] = '\t'.join((w,pron))
    for lexpath in esample:
        logging.warn('%s contains invalid phonemes including:'%(lexpath))
        for p in esample[lexpath]:
            logging.warn('/%s/, %d times, example: %s'%(p,ecount[lexpath][p],esample[lexpath][p]))
        
