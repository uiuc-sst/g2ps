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
   
import sys,os,os.path,shutil,re,logging
import phonecodes
import phonecodes.src.phonecode_tables as phonecode_tables
import pycountry
from collections import deque

known_dicttypes = set(['callhome','babel','celex','ipa','masterlex'])

###########################################################
def read_ipa_dictfile(filename, phoneset):
    '''Read from IPA-formatted dictfile; eliminate extra spaces and parens, insert a tab'''
    S = set()
    with open(filename) as f:
        for line in f:
            S.add(standardize_ipa_entry_string(re.sub(r'\(.*\)','',line), phoneset))
    return(S)

def read_babel_dictfile(filename, pcol, phoneset):
    '''Read from a Babel dict, whose phones start in pcol.
    '''
    S = set()
    with open(filename) as f:
        for line in f:
            words = re.split(r'\s+',line.rstrip(), pcol)
            options = words[pcol].split('\t')
            for option in options:
                op = []
                for phone in option:
                    # Look up a tone, attach it to vowel if possible, else most recent phone
                    if re.match(r'_\d',phone):
                        op.append(phonecodes.tone2ipa(phone[1:], alpha3))
                    # Everything else is assumed to be X-SAMPA
                    else:  
                        op.append( phonecodes.xsampa2ipa(phone) )
                if len(op)>0:
                    S.add(standardize_ipa_entry_list(words[0],op ,phoneset))
    return(S)

def read_arbitrary_dictfile(fname, splitc, gcol, pcol, optc, napat, cfunc, phoneset):
    '''From dictfile, read a set of (word,phones) pairs.
    splitc -- character to split columns
    gcol -- column containing the word
    pcol -- column containing the phones
    optc -- character to split options, within the phones column (same as splitc==unused)
    napat -- ignore the line if re.search(napat,word) or re.search(napat,phones), if len(napat)>0
    conversion -- convert every phone using this function, if possible
    '''
    S = set()
    with open(fname) as f:
        for line in f:
            words = re.sub(r'-','',line).rstrip().split(splitc)
            if napat and (re.search(napat,words[gcol]) or re.search(napat,words[pcol])):
                pass
            else:
                word = re.sub(r'\s+','_',words[gcol])
                options = words[pcol].split(optc)
                for option in options:
                    if cfunc:
                        S.add(standardize_ipa_entry_list(word, [ cfunc(x) for x in option ],phoneset))
                    else:
                        S.add(standardize_ipa_entry_list(word, list(option), phoneset))
    return(S)
                    
_callhome_params = {
    'arz':(1,2,3,-1,'//','//','iso_8859_6'),
    'cmn':(0,3,2,1,'//','//','gb2312'),
    'spa':(0,2,3,-1,'//','//','latin_1'),
    'deu':(0,2,3,-1,'||','||','latin_1'),
    'jpn':(0,3,None,-1,'/','/','euc_jp')
    }
def read_callhome_dict(filename, alpha3, phoneset):
    '''Read a callhome dictionary: 
    params = (column(word), column(phones), column(tone|stress), istone?, pat(syloptions), pat(toneopts))
    vowelpat = pattern with one parenthesis specifying what should be called vowel,e.g., r'([aeiou]+)\s+'
    '''
    S = set()
    vowelpat = re.compile('(%s)' % '|'.join(phonecode_tables._callhome_vowels[alpha3]))
    (gcol,pcol,tcol,tdir,spat,tpat,encoding) = _callhome_params[alpha3]
    with open(filename, encoding=encoding) as f:
        for line in f:
            words = line.rstrip().split('\t')  # Split at tabs

            # If there are more than one possible pronunciations, get all options
            if tcol == None:
                tone_options = ['0']
            else:
                tone_options = re.sub(r'\s+','',words[tcol]).split(tpat)
            syl_options = re.sub(r'\s+','',words[pcol]).split(spat) 
            if len(tone_options)==1:
                tone_options = tone_options *  len(syl_options)
            elif len(syl_options)==1:
                syl_options = syl_options * len(tone_options)
            elif len(tone_options) != len(syl_options):
                raise KeyError('tone_options and syl_options mismatched: {}'.format(line.rstrip()))

            # For each option, generate a tone/stress-marked pronunciation, and store it
            for (tones,pron) in zip(tone_options,syl_options):
                syls = re.split(vowelpat,pron)
                cons = [ list(x) for x in syls[0::2] ]  # split consonants
                vows = syls[1::2] # keep vowels whole; might be some dipththongs 
                tones = [ t for t in tones ]
                phones = []
                for n in range(max(len(vows),len(cons),len(tones))):
                    if n < len(cons):
                        phones.extend([phonecodes.callhome2ipa(phone, alpha3) for phone in cons[n]])
                    if n < len(tones) and tdir < 0:
                        phones.append(phonecodes.tone2ipa(tones[n], alpha3))
                    if n < len(vows):
                        phones.append(phonecodes.callhome2ipa(vows[n], alpha3))
                    if n < len(tones) and tdir > 0:
                        phones.append(phonecodes.tone2ipa(tones[n], alpha3))

                S.add(standardize_ipa_entry_list(words[gcol],phones,phoneset))
    return(S)

def standardize_ipa_entry_string(entry, phoneset):
    'Split the entry, then call standardize_ipa_entry_list'
    plist = entry.lstrip().rstrip().split()
    if len(plist) > 1:
        word = plist[0]
        plist = plist[1:]
        return(standardize_ipa_entry_list(word, plist, phoneset))
    else:
        return('')

def standardize_ipa_entry_list(word, inputlist, phoneset):
    '''Standardize an IPA entry.
    word = string
    plist = list of phones
    Standardization means:
    (1) some non-standard characters replaced by more standard versions, or removed
    (2) tab after word, spaces between phones
    (3) stress attached before the next vowel
    (4) diacritic attached to previous phone, whatever it was
    (5) tone attached after the previous vowel
    (6) check to make sure each phone is in phoneset; if not, delete this entry
    If these changes result in a zero-length pronunciation string, return value is empty string.
    '''
    op = []
    plist = [ p for p in inputlist if len(p)>0 ]
    for pn in range(len(plist)):
        # First, normalize non-standard IPA characters
        if plist[pn]=="'":
            plist[pn]="ˈ"
        # Second, deal with various combining characters in the IPA
        if len(op)>1 and op[-1]=='͡':   # combiner character
            op[-2] += plist[pn]
            del op[-1]
        elif plist[pn] in phonecodes.stressmarkers: # lone stress marker attaches to next vowel
            #if pn<len(plist)-1 and plist[pn+1][0] in phonecodes.vowels:
            #    plist[pn+1] = plist[pn]+plist[pn+1]
            #elif pn<len(plist)-2 and plist[pn+2][0] in phonecodes.vowels:
            #    plist[pn+2] = plist[pn]+plist[pn+2]
            #elif pn<len(plist)-3 and plist[pn+3][0] in phonecodes.vowels:
            #    plist[pn+3] = plist[pn]+plist[pn+3]
            #elif pn<len(plist)-4 and plist[pn+4][0] in phonecodes.vowels:
            #    plist[pn+4] = plist[pn]+plist[pn+4]
            #else:
            plist[pn+1] = plist[pn]+plist[pn+1]  # if there is no next vowel, attach to consonant
        elif plist[pn][0] in phonecodes.diacritics and len(op)>0:
            op[-1] += plist[pn]
        elif plist[pn][0] in phonecodes.tonecharacters and len(op)>0: # attaches to previous vowel
            #if len(op)>0 and op[-1][0] in phonecodes.vowels:
            #    op[-1] += plist[pn]
            #elif len(op)>1 and op[-2][0] in phonecodes.vowels:
            #    op[-2] += plist[pn]
            #elif len(op)>2 and op[-3][0] in phonecodes.vowels:
            #    op[-3] += plist[pn]
            #else:
            op[-1] += plist[pn]  # if there is no previous vowel, attach to consonant
        else:  # any other symbol is a regular phone
            op.append(plist[pn])

    pstr = ' '.join([ p for p in op if p != '' ])
    plist = op
    op = []
    for pn in range(len(plist)):
        if plist[pn] in phoneset:
            op.append(plist[pn])
        else:
            if pn < len(plist)-1 and plist[pn]+plist[pn+1] in phoneset:
                plist[pn+1] = plist[pn]+plist[pn+1]
            elif len(op)>0 and op[-1]+plist[pn] in phoneset:
                op[-1] = op[-1]+plist[pn]
            else:
                logging.error('Unknown phone %s; discarding entry %s'%(plist[pn],pstr))
                return('')
            
    pstr = ' '.join([ p for p in op if p != '' ])
    if len(pstr) > 0:
        return(word + '\t' + pstr)
    else:
        return('')

def write_dictfile(S, filename, mode, phoneset):
    '''Write a (word,phones) list to dictfile'''
    written = set()
    with open(filename,mode) as f:
        for entry in sorted(S):
            standardized = standardize_ipa_entry_string(entry, phoneset)            
            if len(standardized)>0 and standardized not in written:
                f.write(standardized+'\n')
                written.add(standardized)

###########################################################
class extra_language:
    def __init__(self, alpha_3, name):
        self.alpha_3 = alpha_3
        self.name = name

_extra_languages = [
    extra_language('ber','Berber')
]
for L in pycountry.languages:
    n=re.sub(r'\s*\(.*\)','',L.name)
    if n != L.name:
        _extra_languages.append(extra_language(L.alpha_3, n))
extra_languages = { x.name:x.alpha_3 for x in _extra_languages }
extra_alpha3 = { x.alpha_3:x.name for x in _extra_languages }

# ISO 639-3 uses these geographical modifiers to subdivide dialect continua.
# They are cumbersome, and unnecessary if one doesn't need to distinguish the subdivided dialects.
_words2delete = set(('chinese', 'iranian', 'south', 'southern', 'central', 'modern', 'north'))

###########################################################
def simplify_languagename(language):
    '''Simplify languagename: eliminate parentheticals, and convert spaces to underscore.'''
    return(re.sub(r'\s+','_',re.sub(r'\s*\(.*\)\s*','',language)))

def language_to_alpha3(language):
    '''convert language name to alpha_3'''
    if pycountry.languages.get(name=language) != None:
        return(pycountry.languages.get(name=language).alpha_3)
    for L in pycountry.languages:
        if simplify_languagename(L.name) == language:
            return(L.alpha_3)
    if language in extra_languages:
        return(extra_languages[language])
    logging.warning('Unable to find alpha3 for language name %s; using mis'%(language))
    return('mis')

def alpha3_to_language(alpha3):
    '''convert alpha_3 to language name'''
    L = pycountry.languages.get(alpha_3=alpha3)
    if L:
        return(re.sub(r'\s+','_',re.sub(r'\s*\(.*\)','',L.name)))
    elif alpha3 in extra_alpha3:
        return(extra_alpha3[alpha3])
    else:
        logging.warning('Unable to find language name for code %s; using ""'%(alpha3))
        return("")
    
def normalize_filename(infile, nametype):
    '''(outfile, language) = normalize_filename(infile, nametype)
    Divide infile at word and directory boundaries; rm duplicates, extensions, and 'eng'.
    If nametype=='alpha_3', search for ISO 639-3, else search for language name.
    Move language name to the front of the filename, end the filename with .txt.
    
    This code is old, it might not work any more.
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
    'Amharic':2,
    'Assamese':2,
    'Bengali':2,
    'Yue_Chinese':2,
    'Cantonese':2,
    'Cebuano':1,
    'Luo':1,
    'Georgian':2,
    'Guarani':1,
    'Haitian':1,
    'Igbo':1,
    'Javanese':1,
    'Kurdish':1,
    'Lao':2,
    'Lithuanian':1,
    'Mongolian':2,
    'Pushto':2,
    'Swahili':1,
    'Tagalog':1,
    'Tamil':2,
    'Tok-Pisin':1,
    'Turkish':1,
    'Vietnamese':1,
    'Zulu':1
}
def normalize_babel(infile,outfile, language, alpha3, phoneset):
    try:
        S2 = read_ipa_dictfile(outfile, phoneset)
    except:
        S2 = set()
    S2 |= read_babel_dictfile(infile,babel_pcols[language], phoneset)
    write_dictfile(S2, outfile, 'w', phoneset)
        
###########################################################
def normalize_celex(infile,outfile,language, alpha3, phoneset):
    try:
        S2 = read_ipa_dictfile(outfile, phoneset)
    except:
        S2 = set()
    if language=='english':
        S2 |= read_arbitrary_dictfile(infile, '\\', 1, 6, '\\', None,
                                      lambda x: phonecodes.disc2ipa(x,alpha3), phoneset)
    else:
        S2 |= read_arbitrary_dictfile(infile, '\\', 1, 4, '\\', None,
                                      lambda x: phonecodes.disc2ipa(x,alpha3), phoneset)
    write_dictfile(S2, outfile, 'w', phoneset)
        
###########################################################
def normalize_callhome(infile,outfile,language,alpha3,phoneset):
    try:
        S2 = read_ipa_dictfile(outfile, phoneset)
    except:
        S2 = set()
    S2 |= read_callhome_dict(infile,alpha3, phoneset)
    write_dictfile(S2,outfile,'w',phoneset)
        
###########################################################
def normalize_masterlex(infile,outfile,phoneset):
    try:
        S2 = read_ipa_dictfile(outfile, phoneset)
    except:
        S2 = set()
    napat = re.compile(r'N/A')
    S2 |= read_arbitrary_dictfile(infile,'\t',0,4,',',napat, None, phoneset)
    if len(S2) > 0:
        write_dictfile(S2, outfile,'w',phoneset)

###########################################################
def normalize_ipa(infile,outfile, mode, phoneset):
    try:
        S2 = read_ipa_dictfile(outfile, phoneset)
    except:
        S2 = set()
    S2 |= read_ipa_dictfile(infile, phoneset)
    write_dictfile(S2, outfile, mode, phoneset)

###########################################################
def normalize_dict(inpath,outpath,language,alpha3,dicttype,phoneset):
    logging.debug('normalize_dict(%s,%s,%s,%s,%s)'%(inpath,outpath,language,alpha3,dicttype))    
    if dicttype=='callhome':
        normalize_callhome(inpath,outpath,language,alpha3,phoneset)
    elif dicttype=='babel':
        normalize_babel(inpath,outpath,language,alpha3,phoneset)
    elif dicttype=='celex':
        normalize_celex(inpath,outpath,language,alpha3,phoneset)
    elif dicttype=='masterlex':
        normalize_masterlex(inpath,outpath,phoneset)
    elif dicttype=='wikipedia':
        normalize_ipa(inpath,outpath,'a',phoneset)
    else:
        logging.error('Unknown dicttype %s for %s (%s)'%(dicttype,pronlex['path'],language))
    
###########################################################
if __name__=="__main__":
    if len(sys.argv) < 3:
        sys.stderr.write(__doc__+'\n')
        exit(0)
    inputdir = sys.argv[1]
    outputdir = sys.argv[2]

    for dicttype in known_dicttypes:
        listfile = os.path.join(inputdir,'%s.txt'%dicttype)
        if os.path.isfile(listfile):
            outfiles = {}
            languages = {}
            with open(listfile) as f:
                # Eliminate empty lines and comments; otherwise, strip off the newline symbol
                infiles = [ x.rstrip() for x in f.readlines() if len(x)>1 and x[0]!='#' ]

                for infile in infiles:
                    if dicttype=='masterlex':
                        (outbase, alpha3) = normalize_filename(infile,'alpha_3')
                        language = alpha3_to_language(alpha3)
                    else:
                        (outbase, language) = normalize_filename(infile,'name')
                        alpha3 = language_to_alpha3(language)
                    outfile = os.path.join(outputdir,language+'_'+outbase+'.txt')
                    print('Normalizing file {} to {}'.format(infile,outfile))
                    normalize_dict(infile,outfile,language,alpha3,dicttype)
