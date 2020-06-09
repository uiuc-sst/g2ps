#!/usr/bin/python3
'''A set of convenience functions for converting among different phone codes.
   Usage: 
   import phonecodes
   print phonecodes.CODES   # the known phone codes
   print phonecodes.LANGUAGES # the known languages
   s1 = phonecodes.convert(s0, code0, code1, language)
   # s0 and s1 are strings containing individual symbols
   # code0 and code1 must be members of phonecodes.CODES, of course
   # language must be a member of phonecodes.LANGUAGES, of course
   #   (but not all languages are known for all phone codes)
   l1 = phonecodes.convertlist(l0, code0, code1, language)
   # l0, l1 are lists of symbols
   phonecodes.vowels
   phonecodes.consonants
   # list known IPA symbols of vowels, consonants.
   # for other tables, see phonecode_tables.py
'''
import re,sys
import phonecodes.src.phonecode_tables as phonecode_tables

CODES=set(('ipa','arpabet','xsampa','disc','callhome'))
LANGUAGES=set(('eng','deu','nld','arz','cmn','spa','yue','lao','vie'))

vowels = phonecode_tables._ipa_vowels
consonants = phonecode_tables._ipa_consonants
stressmarkers = phonecode_tables._ipa_stressmarkers
tonecharacters = phonecode_tables._ipa_tonecharacters
diacritics = phonecode_tables._ipa_diacritics

#####################################################################
def translate_string(s, d):
    '''(tl,ttf)=translate_string(s,d):
    Translate the string, s, using symbols from dict, d, as:
    1. Min # untranslatable symbols, then 2. Min # symbols.
    tl = list of translated or untranslated symbols.
    ttf[n] = True if tl[n] was translated, else ttf[n]=False.
'''
    N = len(s)
    symcost = 1    # path cost per translated symbol
    oovcost = 10   # path cost per untranslatable symbol
    maxsym = max(len(k) for k in d.keys())  # max input symbol length
    # (pathcost to s[(n-m):n], n-m, translation[s[(n-m):m]], True/False)
    lattice = [ (0,0,'',True) ]
    for n in range(1,N+1):
        # Initialize on the assumption that s[n-1] is untranslatable
        lattice.append((oovcost+lattice[n-1][0],n-1,s[(n-1):n],False))
        # Search for translatable sequences s[(n-m):n], and keep the best
        for m in range(1,min(n+1,maxsym+1)):
            if s[(n-m):n] in d and symcost+lattice[n-m][0] < lattice[n][0]:
                lattice[n] = (symcost+lattice[n-m][0],n-m,d[s[(n-m):n]],True)
    # Back-trace
    tl = []
    translated = []
    n = N
    while n > 0:
        tl.append(lattice[n][2])
        translated.append(lattice[n][3])
        n = lattice[n][1]
    return((tl[::-1], translated[::-1]))

def attach_tones_to_vowels(il, tones, vowels, searchstep, catdir):
    '''Return a copy of il, with each tone attached to nearest vowel if any.
    searchstep=1 means search for next vowel, searchstep=-1 means prev vowel.
    catdir>=0 means concatenate after vowel, catdir<0 means cat before vowel.
    Tones are not combined, except those also included in the vowels set.
    '''
    ol = il.copy()
    v = 0 if searchstep>0 else len(ol)-1
    t = -1
    while 0<=v and v<len(ol):
        if (ol[v] in vowels or (len(ol[v])>1 and ol[v][0] in vowels)) and t>=0:
            ol[v]= ol[v]+ol[t] if catdir>=0 else ol[t]+ol[v]
            ol = ol[0:t] + ol[(t+1):]  # Remove the tone
            t = -1 # Done with that tone
        if v<len(ol) and ol[v] in tones:
            t = v
        v += searchstep
    return(ol)

#####################################################################
# X-SAMPA
def ipa2xsampa(x):
    '''Attempt to return X-SAMPA equivalent of an IPA phone x.'''
    (tl,ttf) = translate_string(x, phonecode_tables._ipa2xsampa)
    return(''.join(tl))

def xsampa2ipa(x):
    '''Return the IPA equivalent of X-SAMPA phone x.'''
    (tl,ttf) = translate_string(x, phonecode_tables._xsampa_and_diac2ipa)
    return(''.join(tl))
    
######################################################################
# Language-dependent lexical tones and stress markers
def tone2ipa(n, alpha3):
    return(phonecode_tables._tone2ipa[alpha3][n[1:]])

#####################################################################
# DISC, the system used by CELEX
def disc2ipa(x, alpha3):
    '''Convert DISC symbol x into IPA, for language L'''
    if alpha3=='nld':
        (tl,ttf) = translate_string(x,phonecode_tables._disc2ipa_dutch)
        return(''.join(tl))
    elif alpha3=='eng':
        (tl,ttf) = translate_string(x,phonecode_tables._disc2ipa_english)
        return(''.join(tl))
    else:
        (tl,ttf) = translate_string(x,phonecode_tables._disc2ipa)
        return(''.join(tl))

def ipa2disc(x):
    '''Convert IPA symbol x into DISC'''
    (tl,ttf) = translate_string(x,phonecode_tables._ipa2disc)
    return(''.join(tl))

def ipa2disc_old(x):
    '''Convert IPA symbol x into DISC'''
    # Convert whole thing if possible; otherwise try prefix+vowel; else quit
    if x in phonecode_tables._ipa2disc:
        return(phonecode_tables._ipa2disc[x])
    elif x[0] in phonecode_tables._ipa2disc and x[1:] in phonecode_tables._ipa2disc:
        return(phonecode_tables._ipa2disc[x[0]]+phonecode_tables._ipa2disc[x[1:]])
    else:
        raise KeyError('Unknown IPA symbol %s'%(x))

#######################################################################
# Callhome phone codes
def callhome2ipa(x,alpha3):
    '''Convert callhome phone symbol x into IPA for language alpha3'''
    (il,ttf)=translate_string(x,phonecode_tables._callhome2ipa[alpha3])
    if alpha3=='arz':
        ol = attach_tones_to_vowels(il,phonecode_tables._ipa_stressmarkers,
                                    phonecode_tables._ipa_vowels,-1,-1)
    elif alpha3=='cmn':
        ol=attach_tones_to_vowels(il,phonecode_tables._ipa_tones,
                                  phonecode_tables._ipa_vowels,-1,1)
    elif alpha3=='spa':
        ol=attach_tones_to_vowels(il,phonecode_tables._ipa_stressmarkers,
                                  phonecode_tables._ipa_vowels,-1,-1)
    return(''.join(ol))

def ipa2callhome(x,alpha3):
    '''Convert IPA symbol x into callhome notation, for language alpha3'''
    (il,ttf)=translate_string(x,phonecode_tables._ipa2callhome[alpha3])
    if alpha3=='arz':
        ol=attach_tones_to_vowels(il,'012',phonecode_tables._callhome_vowels['arz'],1,1)
    elif alpha3=='cmn':
        ol=attach_tones_to_vowels(il,'012345',phonecode_tables._callhome_vowels['cmn'],-1,1)
    elif alpha3=='spa':
        ol=attach_tones_to_vowels(il,'012',phonecode_tables._callhome_vowels['spa'],1,1)
    return(''.join(ol))

#########################################################################
# ARPABET and TIMIT
def arpabet2ipa(x):
    '''Convert ARPABET symbol X to IPA'''
    (il,ttf)=translate_string(x,phonecode_tables._arpabet2ipa)
    ol=attach_tones_to_vowels(il,phonecode_tables._ipa_stressmarkers,
                              phonecode_tables._ipa_vowels,-1,-1)
    return(''.join(ol))

def ipa2arpabet(x):
    '''Convert IPA symbols to ARPABET'''
    (il,ttf)=translate_string(x,phonecode_tables._ipa2arpabet)
    ol=attach_tones_to_vowels(il,'012',phonecode_tables._arpabet_vowels,1,1)
    return(''.join(ol))

def timit2ipa(x):
    '''Convert TIMIT phone codes to IPA'''
    x = x.upper()
    (il,ttf)=translate_string(x,phonecode_tables._timit2ipa)
    ol=attach_tones_to_vowels(il,phonecode_tables._ipa_stressmarkers,
                              phonecode_tables._ipa_vowels,-1,-1)
    return(''.join(ol))

#######################################################################
# phonecodes.convert and phonecodes.convertlist
# are used to convert symbols and lists of symbols, respectively,
# to or from IPA, by calling appropriate other functions.
#
_convertfuncs = {
    'arpabet': (arpabet2ipa, ipa2arpabet),
    'xsampa': (xsampa2ipa, ipa2xsampa),
    'disc': (disc2ipa, ipa2disc),
    'callhome': (callhome2ipa,ipa2callhome)
}
def convert(s0, c0, c1, language):
    if c0=='ipa' and c1!='ipa':
        x=_convertfuncs[c1][1](s0, language)
        return(x)
    elif c0!='ipa' and c1=='ipa':
        return(_convertfuncs[c0][0](s0, language))
    else:
        raise RuntimeError('must convert to/from ipa, not %s to %s'%(c0,c1))

def convertlist(l0, c0, c1, language):
    return([ convert(s0,c0,c1,language) for s0 in l0 ])

