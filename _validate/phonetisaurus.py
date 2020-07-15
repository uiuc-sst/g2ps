import os,subprocess,logging

def load_dict_from_txtfile(txtfile):
    x = {}
    with open(txtfile,encoding='utf-8') as f:
        for line in f:
            words = line.rstrip().split()
            if len(words)==0 or line[0]=='#':
                continue
            if len(words)==1:
                x[words[0]] = ''
            else:
                x[words[0]] = ' '.join(words[1:])
    return(x)


class Language():
    def __init__(self, name, iso, g2pfile, pronlexfile):
        '''A language is a G2P, and a pronlex.  Neither is loaded until needed.'''
        self.name = name
        self.iso = iso
        self.g2pfile = g2pfile
        self.pronlexfile = pronlexfile
        self.precomputes = {}
    def __str__(self):
        return(self.name)
    def load_pronlex(self):
        self.pronlex = load_dict_from_txtfile(self.pronlexfile)
        return(self.pronlex)
    def apply_g2p(self, charseqs):
        '''Apply  my G2P to a given list of character sequences'''
        os.makedirs('exp/wordlists',exist_ok=True)
        wordlistfile = os.path.join('exp/wordlists',self.name+'_wordlist.txt')
        with open(wordlistfile,'w') as f:
            f.write('\n'.join(charseqs))
        cmd=['phonetisaurus-g2pfst','--model=%s'%(self.g2pfile),'--wordlist=%s'%(wordlistfile)]
        proc=subprocess.run(cmd,capture_output=True)
        if len(proc.stderr)>0:
            logging.warning('Errors found doing %s'%(' '.join(cmd)))
        if len(proc.stdout)==0:
            logging.warning('Language(%s).apply_g2p(%s,...) had no output'%(self.name,charseqs[0]))
        prondictfile=os.path.join('exp','wordlists',self.name+'_stdout.txt')
        with open(prondictfile,'wb') as f:
            f.write(proc.stdout)
        return(load_dict_from_txtfile(prondictfile))

