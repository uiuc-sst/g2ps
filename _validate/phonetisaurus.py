import os,subprocess,logging

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


class Language():
    def __init__(self, name, iso, g2pfile, pronlexfile):
        '''A language is a G2P, and a pronlex.  Neither is loaded until needed.'''
        self.name = name
        self.iso = iso
        self.g2pfile = g2pfile
        self.pronlexfile = pronlexfile
        self.precomputes = {}
        self.N = 1
    def __str__(self):
        return(self.name)
    def ppr(self,level=0):
        return(self.name)
    def load_pronlex(self):
        self.pronlex = load_dict_from_txtfile(self.pronlexfile)
        return(self.pronlex)
    def load_wordlist(self):
        if not hasattr(self,'pronlex'):
            self.load_pronlex()
        self.wordlist = [ k for k in self.pronlex.keys() ]
    def load_charset(self):
        if not hasattr(self,'wordlist'):
            self.load_wordlist()
        self.charset = set()
        for w in self.wordlist:
            self.charset.union(set(w))
    def apply_g2p(self, wordlist, name):
        '''Apply  my G2P to a given wordlist'''
        os.makedirs('exp/wordlists',exist_ok=True)
        wordlistfile = os.path.join('exp/wordlists',name+'_wordlist.txt')
        with open(wordlistfile,'w') as f:
            f.write('\n'.join(wordlist))
        cmd=['phonetisaurus-g2pfst','--model=%s'%(self.g2pfile),'--wordlist=%s'%(wordlistfile)]
        proc=subprocess.run(cmd,capture_output=True)
        if len(proc.stderr)>0:
            logging.warn('Errors found doing %s'%(' '.join(cmd)))
        lines = proc.stdout.decode('utf-8').split('\n')
        if len(lines)==0:
            print('Language(%s).apply_g2p(%s..) no output: %s'%(self.name,wordlist[0],' '.join(cmd)))
        prons = {}
        for line in lines:
            a = line.split()
            if len(a)>0:
                if a[0] not in prons:
                    prons[a[0]] = []
                if len(a) > 2:
                    prons[a[0]].append(a[2:])
                else:
                    prons[a[0]].append('')                    
        return(prons)

