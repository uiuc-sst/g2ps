#!/usr/bin/python3
'''python normalize_dicts.py inputdir outputdir
   Converts dictionaries listed in inputdir to normalized IPA format in outputdir.
   Inputdir should contain file lists, with paths that work relative to working directory:
   inputdir/babel.txt - list of BABEL-format dictionaries
   inputdir/celex.txt - list of CELEX-format dictionaries
   inputdir/callhome.txt - list of Callhome-format dictionaries
   inputdir/masterlex.txt - list of masterlex-format dictionaries
   inputdir/ipa.txt - list of pronlex files already using IPA (will just be copied)

   Each filename is searched for known language name or code, which is moved to front of the
   output filename, followed by an underscore (_).  If none found, throw an error.
'''
   
import sys,os,os.path,shutil,re
import phonecodes
import pycountry

###########################################################
def read_ipa_dictfile(filename):
    '''Read from IPA-formatted dictfile; eliminate extra spaces and parens, insert a tab'''
    S = []
    with open(filename) as f:
        for line in f:
            words = re.split(r'\s+',re.sub(r'\(.*\)','',line.strip()))
            S.append((words[0], words[1:]))
    return(S)

def read_babel_dictfile(filename, pcol):
    '''Read from a Babel dict, whose phones start in pcol.
    '''
    S = []
    with open(filename) as f:
        for line in f:
            words = re.split(r'\s+',line.rstrip(), pcol)
            options = words[pcol].split('\t')
            for option in options:
                S.append((words[0], option.split()))
    return(S)

def read_arbitrary_dictfile(filename, splitchar, gcol, pcol, optchar, addspaces=False, napat=None):
    '''From dictfile, read a set of (word,phones) pairs.
    splitchar -- character to split columns
    gcol -- column containing the word
    pcol -- column containing the phones
    optchar -- character to split options, within the phones column (same as splitchar==unused)
    addspaces -- true if spaces should be added betweeen consecutive characters in phone string
    napat -- ignore the line if re.search(napat,word) or re.search(napat,phones), if len(napat)>0
    '''
    S = []
    with open(filename) as f:
        for line in f:
            words = re.sub(r'-','',line).rstrip().split(splitchar)
            if napat and (re.search(napat,words[gcol]) or re.search(napat,words[pcol])):
                pass
            else:
                word = re.sub(r'\s+','_',words[gcol])
                options = words[pcol].split(optchar)
                for option in options:
                    if addspaces:
                        S.append((word, list(option)))
                    else:
                        S.append((word, option.split()))
    return(S)
                    
def read_callhome_dict(filename, gcol, pcol, tcol, vowelpat, L):
    '''Read a callhome dictionary: gcol=word, pcol=phones, tcol=tones or stress.
    vowelpat is a pattern with one parenthesis, specifying what should be called a vowel,
    for example, r'([aeiou]+)\s+'
    '''
    S = []
    with open(filename) as f:
        for line in f:
            words = line.rstrip().split('\t')  # Split at tabs
            tone_options = re.sub(r'\s+','',words[tcol]).split('//')
            syl_options = re.sub(r'\s+','',words[pcol]).split('//') 
            if len(tone_options)==1:
                options=[ (tone_options[0], s) for s in syl_options ]
            elif len(tone_options)==len(syl_options):
                options=[ (tone_options[n], syl_options[n]) for n in range(0,len(syl_options)) ]
            else:
                raise KeyError('tone_options and syl_options mismatched: {}'.format(line.rstrip()))
            for option in options: 
                syls = re.split(vowelpat,option[1])
                tones = list(option[0])
                phones = []
                for n in range(0,len(tones)):  # should match number of syllables
                    if 2*n < len(syls) and len(syls[2*n])>0:
                        phones.extend(list(syls[2*n]))    # should be onset consonants
                    if L=='spanish' or L=='egyptian-arabic':
                        phones.append('_'+tones[n])  # stress marker goes before the vowel
                    if 2*n+1 < len(syls) and len(syls[2*n+1])>0:
                        phones.extend(list(syls[2*n+1]))    # should be the vowel
                    if L=='mandarin':
                        phones.append('_'+tones[n])  # tone marker goes after the vowel
                for m in range(2*len(tones), len(syls)):  # extra consonants after last syllable?
                    if len(syls[m])>0:
                        phones.extend(list(syls[m]))  
                S.append((words[gcol], phones))
    return(S)

#comb_fore=re.compile('^[%s]+$'%phonecodes.stressmarkers)   # These "phones" combine to the next vowel
#comb_back=re.compile('^[%s%s]+$'%(phonecodes.diacritics,phonecodes.tonecharacters))  # These combine to prev vowel

def write_dictfile(S, filename, mode='w'):
    '''Write a (word,phones) list to dictfile'''
    written = set()
    with open(filename,mode) as f:
        for pair in sorted(S):
            if len(pair[0])>0 and len(pair[1])>0:
                plist = [ p for p in pair[1] if not p.isspace() and len(p)>0 ]   # First, eliminate spaces
                for pn in range(0,len(plist)):
                    # First, normalize non-standard IPA characters
                    if plist[pn]=="'":
                        plist[pn]="ˈ"
                    # Second, deal with various combining characters in the IPA
                    if plist[pn]=='͡':     # combiner character
                        if pn>0 and pn<len(plist)-1:
                            plist[pn+1] = plist[pn-1]+plist[pn+1]
                            plist[pn-1] = ''
                            plist[pn]=''
                    elif plist[pn] in phonecodes.stressmarkers:    # stress marker attaches to next vowel
                        if pn<len(plist)-1 and plist[pn+1][0] in phonecodes.vowels:
                            plist[pn+1] = plist[pn]+plist[pn+1]
                        elif pn<len(plist)-2 and plist[pn+2][0] in phonecodes.vowels:
                            plist[pn+2] = plist[pn]+plist[pn+2]
                        elif pn<len(plist)-3 and plist[pn+3][0] in phonecodes.vowels:
                            plist[pn+3] = plist[pn]+plist[pn+3]
                        elif pn<len(plist)-4 and plist[pn+4][0] in phonecodes.vowels:
                            plist[pn+4] = plist[pn]+plist[pn+4]
                        plist[pn]=''
                    elif plist[pn][0] in phonecodes.diacritics:  # diacritic attaches to previous phone
                        if pn>0:
                            plist[pn-1] = plist[pn-1]+plist[pn]
                            plist[pn]=''
                    elif plist[pn][0] in phonecodes.tonecharacters: # tone attaches to previous vowel
                        if pn>0 and len(plist[pn-1])>0 and plist[pn-1][0] in phonecodes.vowels:
                            plist[pn-1] = plist[pn-1]+plist[pn]
                        elif pn>1 and len(plist[pn-2])>0 and plist[pn-2][0] in phonecodes.vowels:
                            plist[pn-2] = plist[pn-2]+plist[pn]
                        elif pn>2 and len(plist[pn-3])>0 and plist[pn-3][0] in phonecodes.vowels:
                            plist[pn-3] = plist[pn-3]+plist[pn]
                        elif pn>0:
                            plist[pn-1] = plist[pn-1]+plist[pn]                            
                        plist[pn]=''
                    pn += 1

                pstr = ' '.join([ p for p in plist if p != '' ])
                if len(pstr) > 0:
                    writeline = '%s\t%s\n' % (pair[0],pstr)
                    if writeline not in written:
                        f.write('{}\t{}\n'.format(pair[0], ' '.join([ p for p in plist if p != '' ])))
                        written.add(writeline)

###########################################################
class extra_language:
    def __init__(self, alpha_3, name):
        self.alpha_3 = alpha_3
        self.name = name

_extra_languages = [
    extra_language('ber','Berber'),
    extra_language('yue','Cantonese'),
    extra_language('yue','Yue'),
    extra_language('eng','American-English'),
    extra_language('swh','Swahili'),
    extra_language('luo','Luo'),
]
extra_languages = { x.name:x.alpha_3 for x in _extra_languages }

# ISO 639-3 uses these geographical modifiers to subdivide dialect continua.
# They are cumbersome, and unnecessary if one doesn't need to distinguish the subdivided dialects.
_words2delete = set(('chinese', 'iranian', 'south', 'southern', 'central', 'modern', 'north'))

def language_to_alpha3(language):
    '''convert language name to alpha_3'''
    if pycountry.languages.get(name=language) != None:
        return(pycountry.languages.get(name=language).alpha_3)
    L = ' '.join([ w[0].upper()+w[1:] for w in language.split('-') ])
    if pycountry.languages.get(name=L) != None:
        return(pycountry.languages.get(name=L).alpha_3)
    if language in extra_languages:
        return(extra_languages[language])
    raise Warning('Unable to find alpha3 for language name %s; using qaa\n'%(language))
    return('qaa')

def alpha3_to_language(alpha3):
    '''convert alpha_3 to language name'''
    return(pycountry.languages.get(alpha_3=alpha3).name)
    
def normalize_filename(infile, nametype):
    '''(outfile, language) = normalize_filename(infile, nametype)
    Divide infile at word and directory boundaries; rm duplicates, extensions, and 'eng'.
    If nametype=='alpha_3', search for ISO 639-3, else search for language name.
    Move language name to the front of the filename, end the filename with .txt.
    '''
    fileparts = [ x.lower() for  x in  re.split(r'[\W_]+',os.path.splitext(infile)[0]) if x != '' ]
    partset = set()
    for f in fileparts[:]:
        if f in partset:  # Remove any duplicate parts, e.g., dpw_dpw in the CELEX path
            fileparts.remove(f)
        if f=='lex':
            fileparts.remove(f)
        partset.add(f)
    # If the last segment is just two characters, remove it
    if len(fileparts[-1])==2:
        fileparts.pop()
    fileparts = fileparts[max(0,len(fileparts)-5):]
    
    matches = {}
    for L in _extra_languages + list(pycountry.languages):
        nameparts = re.split(r'[\W_]+',re.sub(r'\s*\(.*\)\s*','',L.name.lower()))
        nparts = [ npart for npart in nameparts if npart not in _words2delete ] # eliminate modifiers
        if len(nparts)>0:
            name = '-'.join(nparts)
            if nametype=='alpha_3':
                for n in range(0,len(fileparts)):
                    if fileparts[n] == L.alpha_3:
                        matches[L.alpha_3] = ('_'.join(fileparts[0:n]+fileparts[(n+1):]),name)
            else:
                for n in range(0,len(fileparts)-len(nparts)+1):
                    if fileparts[n:(n+len(nparts))] == nparts:
                        matches[name]=('_'.join(fileparts[0:n]+fileparts[(n+len(nparts)):]),name)
    if (len(matches)>1) and ('arabic' in matches):
        del matches['arabic']   # Delete 'arabic' if other options exist, b/c it may be script name
    if (len(matches)>1) and ('latin' in matches):
        del matches['latin']   # Delete 'latin' if other options exist, b/c it may be script name
    if (len(matches)>1) and ('eng' in matches):
        del matches['eng']   # Delete 'eng' if other options exist, b/c it may be translations name
    if len(matches)==0:
        raise FileNotFoundError('Unable to identify a language name in {} ({})'.format(infile,fileparts))

    # Longest matching string
    longest_matching_string = max(matches.items(), key=lambda p: len(p[0]))
    return(longest_matching_string[1])


###########################################################
babel_pcols = {
    'amharic':2,
    'assamese':2,
    'bengali':2,
    'yue':2,
    'cantonese':2,
    'cebuano':1,
    'luo':1,
    'georgian':2,
    'guarani':1,
    'haitian':1,
    'igbo':1,
    'javanese':1,
    'kurdish':1,
    'lao':2,
    'lithuanian':1,
    'mongolian':2,
    'pushto':2,
    'swahili':1,
    'tagalog':1,
    'tamil':2,
    'tok-pisin':1,
    'turkish':1,
    'vietnamese':1,
    'zulu':1
}
def normalize_babel(infile,outfile, language, alpha3):
    # Sometimes pcol==1, sometimes pcol==2, so we split 
    S1 = read_babel_dictfile(infile,babel_pcols[language])
    S2 = []
    for pair in S1:
        inphones = pair[1]
        op = []
        for phone in inphones:
            # Look up a tone, attach it to vowel if possible, else most recent phone
            if re.match(r'_\d',phone):
                op.append(phonecodes.tone2ipa(phone, alpha3))
            # Everything else is assumed to be X-SAMPA
            else:  
                op.append( phonecodes.xsampa2ipa(phone) )
        S2.append((pair[0],op))
    write_dictfile(S2, outfile)
        
###########################################################
def normalize_celex(infile,outfile,language, alpha3):
    if language=='english':
        S1 = read_arbitrary_dictfile(infile, '\\', 1, 6, '\\', addspaces=True)
    else:
        S1 = read_arbitrary_dictfile(infile, '\\', 1, 4, '\\', addspaces=True)
    S2 = []
    for pair in S1:
        try:
            outphones = [ phonecodes.disc2ipa(x, alpha3) for x in pair[1] ]
        except KeyError:
            print('Missing a key: {} in {}'.format(pair,infile))
        S2.append((pair[0],outphones))
    write_dictfile(S2, outfile)
        
###########################################################
def normalize_callhome(infile,outfile,language,alpha3):
    S2 = []
    if language=='egyptian-arabic':
        S1 = read_callhome_dict(infile, 1, 2, 3, r'([@aiu%AIOUE])', language)
    elif language=='mandarin':
        S1 = read_callhome_dict(infile, 0, 3, 2, r'([iI%eEU&a@o>uR])', language)
    elif language=='spanish':
        S1 = read_callhome_dict(infile, 0, 2, 3, r'([aeiou]+)', language)
    for pair in S1:
        inphones = pair[1]
        op = []
        for phone in inphones:
            if re.match(r'_\d',phone):
                op.append(phonecodes.tone2ipa(phone, alpha3))
            else:
                op.append( phonecodes.callhome2ipa(phone, alpha3) )
        S2.append((pair[0],op))
    write_dictfile(S2,outfile)
        
###########################################################
def normalize_masterlex(infile,outfile):
    napat = re.compile(r'N/A')
    S1 = read_arbitrary_dictfile(infile,'\t',0,4,',',True,napat)
    if len(S1) > 0:
        write_dictfile(S1, outfile)

###########################################################
def normalize_ipa(infile,outfile, mode='w'):
    S = read_ipa_dictfile(infile)
    write_dictfile(S, outfile, mode)

###########################################################
if __name__=="__main__":
    if len(sys.argv) < 3:
        sys.stderr.write(__doc__+'\n')
        exit(0)
    inputdir = sys.argv[1]
    outputdir = sys.argv[2]

    for dicttype in ['callhome','babel','celex','ipa','masterlex']:
        listfile = os.path.join(inputdir,'%s.txt'%dicttype)
        if os.path.isfile(listfile):
            outfiles = {}
            languages = {}
            with open(listfile) as f:
                # Eliminate empty lines and comments; otherwise, strip off the newline symbol
                infiles = [ x.rstrip() for x in f.readlines() if len(x)>1 and x[0]!='#' ]

                for infile in infiles:
                    if dicttype=='masterlex':
                        (outbase, language) = normalize_filename(infile,'alpha_3')
                    else:
                        (outbase, language) = normalize_filename(infile,'name')
                    outfile = os.path.join(outputdir,language+'_'+outbase+'.txt')
                    print('Normalizing file {} to {}'.format(infile,outfile))
                
                    if dicttype=='callhome':
                        alpha3 = language_to_alpha3(language)
                        normalize_callhome(infile,outfile,language,alpha3)
                    elif dicttype=='babel':
                        alpha3 = language_to_alpha3(language)
                        normalize_babel(infile,outfile,language, alpha3)
                    elif dicttype=='celex':
                        alpha3 = language_to_alpha3(language)
                        normalize_celex(infile,outfile,language, alpha3)
                    elif dicttype=='masterlex':
                        normalize_masterlex(infile,outfile)
                    else:
                        normalize_ipa(infile,outfile)
