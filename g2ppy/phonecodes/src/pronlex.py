import sys,os,re
import phonecodes
import phonecode_tables

LEAF='LEAF'
MAXSET=8000

def dict_enter_word(d,w,p):
    if len(p) == 0:
        if LEAF not in d:
            d[LEAF] = set()
        d[LEAF].add(w)
    else:
        if p[0] not in d:
            d[p[0]] = {}
        dict_enter_word(d[p[0]],w,p[1:])

def dict_convert_phonecode(d0,code0,code1,language):
    d1 = dict()
    for p0 in d0:
        if p0==LEAF:
            d1[p0]=d0[p0]
        else:
            p1 = phonecodes.convert(p0,code0,code1,language)
            d1[p1] = dict_convert_phonecode(d0[p0],code0,code1,language)
    return(d1)

def dict_phones2words(d, rtd, ph, dist=0, paths=[[]], nmax=MAXSET):
    '''Return up to nmax wordstrings, in a list, that match ph
    with up to `dist' distance.'''
    res = []
    # If we're at the root node, with no ph, then current paths is a result
    # Prepend each path with the remaining dist
    if d == rtd and len(ph)==0:
        res.extend([[-dist]+x for x in paths])
    # If the next phone can extend current word, then do it
    if len(ph)>0 and ph[0] in d:
        res.extend(dict_phones2words(d[ph[0]],rtd,ph[1:],dist,paths,nmax))
    # If we've finished any word, then try to start a new one
    if d != rtd and LEAF in d:
        for w in d[LEAF]:
            ws = [ x+[w] for x in paths ]
            r=dict_phones2words(rtd,rtd,ph,dist,ws,nmax)
            while(len(res)<nmax and len(r)>0):
                res.append(r.pop())
    # If we can sub the next phone to extend current word, then do it
    if len(ph)>0 and ph[0] not in d and dist > 0:
        for p in d:
            if p != LEAF:
                res.extend(dict_phones2words(d[p],rtd,ph[1:],dist-1,paths,nmax))
    # If we can extend current word by skipping a dict phone, then do it
    if dist > 0:
        for p in d:
            if p != LEAF:
                res.extend(dict_phones2words(d[p],rtd,ph,dist-1,paths,nmax))
    # If we can extend current word by skipping a listed phone, then do it
    if len(ph)>1 and ph[1] in d and dist > 0:
        res.extend(dict_phones2words(d[ph[1]],rtd,ph[2:],dist-1,paths,nmax))
    # return up to nmax results
    res = sorted(res)
    return(res[:nmax])

###########################################################
def read_raw_dictfile(filename,language):
    '''Read from unformatted dictfile: eliminate extra spaces and parens, 
    insert a tab.  Return a list of word,pron pairs.'''
    S = []
    with open(filename) as f:
        for line in f:
            words = re.split(r'\s+',line.rstrip())
            S.append((words[0], words[1:]))
    return(S)

def read_isle_dictfile(filename,language,params):
    '''Read from ISLE-formatted dictfile, which is just IPA pronunciations,
    but word has parentheses and part of speech to be removed.
    If params['discard_phones'] is a set of chars, then any phones in the set
    will be discarded.  For example, set('#.') discards morph, syl boundaries.
    If params['discard_diacritics'] is a strings, then chars in the string
    will be discarded.  For example, 'ˈˌ' discards stress markers.
    '''
    S = []
    with open(filename) as f:
        for line in f:
            txt=re.sub(r'\([^\)]*\)','',line.rstrip())
            if 'discard_diacritics' in params:
                patstr=r'[%s]+'%(params['discard_diacritics'])
                txt = re.sub(patstr,'',txt)
            words = re.split(r'\s+',txt)
            if 'discard_phones' in params:
                pr=[p for p in words[1:] if p not in params['discard_phones']]
            else:
                pr = words[1:]
            S.append((words[0], pr))
    return(S)

_babel_pcols = {
    'amh':2,'asm':2,'ben':2,'yue':2,'ceb':1,'luo':1,'kat':2,'gug':1,'hat':1,
    'ibo':1,'jav':1,'kur':1,'lao':2,'lit':1,'mon':2,'pus':2,'swa':1,'tgl':1,
    'tam':2,'tpi':1,'tur':1,'vie':1,'zul':1
}

def read_babel_dictfile(filename, lang, params):
    '''Read from a Babel dictfile in language lang.
    If params['pcol'], then it specifies which column contains phones.
    Otherwise, try to guess based on language.
    '''
    S = []
    if 'pcol' in params:
        pcol = params['pcol']
    else:
        pcol = _babel_pcols[lang]
    with open(filename) as f:
        for line in f:
            words = re.split(r'\t',line.rstrip(), pcol)
            options = words[pcol].split('\s+')
            for option in options:
                S.append((words[0], option.split()))
    return(S)

###########################################################
_celex_pcols = { 'eng':6, 'deu':4, 'nld':4 }

def read_celex_dictfile(filename, lang, params):
    '''Read from a CELEX dictfile in language lang.'
    If params['pcol'] exists, it should be an integer,
    specifying which column contains the phonemes.
    '''
    S = []
    if 'pcol' in params:
        pcol = params['pcol']
    else:
        pcol = _celex_pcols[lang]
    with open(filename) as f:
        for line in f:
            words = re.sub(r'-','',line).rstrip().split('\\')
            word = re.sub(r'\s+','_',words[1])
            options = words[pcol].split('\\')
            for option in options:
                ol=phonecodes.attach_tones_to_vowels(list(option),set("'"),phonecode_tables._disc_vowels,1,-1)
                S.append((word, ol))
    return(S)

###################################################################
#_callhome_columns={'arz':(1,2,3,r'([@aiu%AIOUE])'),'cmn':(0,3,2,r'([iI%eEU&a@o>uR])'),'spa':(0,2,3,r'([aeiou]+)')}
_callhome_columns={'arz':(1,2,3),'cmn':(0,3,2),'spa':(0,2,3)
}
def read_callhome_dictfile(filename, L, params):
    '''Read a callhome dictionary in language L.
    If params['callhome_columns'] exists, then it should be a tuple
    (grapheme column, phone column, tone column).
    '''
    S = []
    if 'callhome_columns' in params:
        (gcol, pcol, tcol) = params['callhome_columns']
    else:
        (gcol, pcol, tcol) = _callhome_columns[L]
    with open(filename) as f:
        for line in f:
            fields = line.rstrip().split('\t')  # Split fields by tab
            tone_options = fields[tcol].split('//') # split options by slash
            syl_options = fields[pcol].split('//') 
            if len(tone_options)==1:
                options=[ (tone_options[0],s) for s in syl_options ]
            elif len(tone_options)==len(syl_options):
                options=[ (tone_options[n],syl_options[n])
                          for n in range(0,len(syl_options)) ]
            else:
                raise KeyError('tone_options and syl_options mismatched: {}'.
                               format(line.rstrip()))
            for option in options:
                syls = option[1].split(' ')
                tones = list(option[0])
                phones=[ syls[n]+tones[n] for n in range(0,len(tones)) ]
                phones.append(''.join(syls[len(tones):]))
                il = list(''.join(phones))
                ol = phonecodes.attach_tones_to_vowels(il, set(phonecode_tables._tone2ipa[L].keys()), phonecode_tables._callhome_vowels[L], -1, 1)
                S.append((fields[gcol], ol))
    return(S)

###########################################################################
def write_dictfile(w2p, filename):
    '''Write a w2p dictionary to filename'''
    lines2write = set()  # make sure each written line is unique
    for (w,pron) in w2p.items():
        if len(w)>0 and len(pron)>0:
            pl = [ re.sub(r"\s*Í¡\s*",'',p)
                   for p in pron if not p.isspace() and len(p)>0 ]
            pstr = ' '.join(pl)
            if len(pstr) > 0:
                lines2write.add('%s\t%s\n' % (w,pstr))
    with open(filename,'w') as f:
        for line in sorted(lines2write):
            f.write(line)

###################################################################
_dictread = {
    'babel':read_babel_dictfile,
    'callhome':read_callhome_dictfile,
    'celex':read_celex_dictfile,
    'isle':read_isle_dictfile
}

class lex:
    def __init__(self,language,phonecode='ipa'):
        self.p2w = {}
        self.w2p = {}
        self.language = language
        self.phonecode = phonecode
    def copy(self):
        other = lex(self.language,self.phonecode)
        other.p2w.update(self.p2w)
        other.w2p.update(self.w2p)
        return(other)
    def add(self,word,pron):
        dict_enter_word(self.p2w,word,pron)
        self.w2p[word] = pron
        return(self)
    def recode(self, code1):
        if self.phonecode==code1:
            return(self.copy())
        else:
            other = lex(self.language, code1)
            other.p2w=dict_convert_phonecode(self.p2w,self.phonecode,code1,self.language)
            for (w,p) in self.w2p.items():
                q=phonecodes.convertlist(p,self.phonecode,code1,self.language)
                other.w2p[w] = q
            return(other)
    def phones2words(self, ph, D=0, paths=[[]], nmax=MAXSET):
        '''Find all word sequences matching ph with up to D string edit dist.
        Return: a dict mapping distances to lists of lists:
        L=lex()
        res=L.phones2words(ph, 2)
        sntce in res[0] is a list of words matching ph with 0 edit distance
        sntce in res[1] is a list of words matching ph with 1 edit distance
        sntce in res[2] is a list of words matching ph with 2 edit distance
        If the total number of candidates is greater than nmax,
        then the set is truncated at nmax candidates, with a priority
        queue behavior, i.e., the highest-edit-distance candidates
        are discarded first.'''
        retval={}
        listlist=dict_phones2words(self.p2w,self.p2w,ph,D,paths,nmax)
        for res in listlist:
            if len(res)>1:
                if res[0]+D not in retval:
                    retval[res[0]+D]=[]
                retval[res[0]+D].append(res[1:])
        return(retval)
    def words2phones(self, words):
        pron = []
        for w in words:
            if w in self.w2p:
                pron.extend(self.w2p[w])
            elif w.upper() in self.w2p:
                pron.extend(self.w2p[w.upper()])
            elif w.lower() in self.w2p:
                pron.extend(self.w2p[w.lower()])
            elif w.capitalize() in self.w2p:
                pron.extend(self.w2p[w.capitalize()])
            else:
                pron.append(w)
        return(pron)
    
    def read(self,filename,lang,dicttype, params={}):
        if dicttype in _dictread:
            plist = _dictread[dicttype](filename,lang,params)
            for p in plist:
                self.add(p[0],p[1])
        else:
            plist = read_raw_dictfile(filename,lang)
            for p in plist:
                self.add(p[0],p[1])
        return(self)
    def save(self,filename):
        write_dictfile(self.w2p, filename)

_dict2phonecode = {'babel':'xsampa','celex':'disc','isle':'ipa'}
def read(filename,lang,dicttype,params={}):
    if dicttype in _dict2phonecode:
        newlex = lex(lang,_dict2phonecode[dicttype])
    else:
        newlex = lex(lang,dicttype)
    return(newlex.read(filename,lang,dicttype,params))
        
