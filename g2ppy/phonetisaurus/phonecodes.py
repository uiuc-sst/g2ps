#!/usr/bin/python3
'''A set of convenience functions converting other phone sets into IPA'''
import re,sys


vowels = 'aeiouyɑɒɛɪɪ̈ ɔʘʊʊ̈ ʌʏəɘæʉɨøɜɞɐɤɵœɶ'
consonants = 'bɓcdɖɗfɡɠhɦjʝklɭɺmnɳpɸqrɽɹɻsʂɕtʈvʋwxɧzʐʑβʙçðɱɣɢʛɥʜɲɟʄɬɮʎʟɯɰŋɴʋɒʁʀʃθʍχħʒɾɫʔʕʢʡꜛꜜǃ|ǀ‖ǁǂ'
diacritics = re.sub(r'◌','','◌̈◌̟◌̠◌̌◌̥◌̩◌◌◌̂◌̯◌̚◌◌̃◌̘◌̺◌̏◌◌̜◌̪◌̴◌̂◌◌́◌◌◌◌̰◌̀◌◌̄◌̻◌̼◌◌̹◌̞◌̙◌̌◌◌̝◌̋◌̤◌̬◌◌̆◌̽ːʰˀʷʱʼʲˤ')
stressmarkers = "ˈˌ"
tonecharacters = '˥˦˧˨˩˥˧'

_xsampa2ipa = {
    k:re.sub(r'◌','',v) for (k,v) in {
        '#':'#',
        '=':'◌̩',
        '>':'◌ʼ',
        '`':'◌˞',
        '~':'◌̃',
        'a':'a',
        'b':'b',
        'b_<':'ɓ',
        'c':'c',
        'd':'d',
        'd`':'ɖ',
        'd_<':'ɗ',
        'e':'e',
        'f':'f',
        'g':'ɡ',
        'g_<':'ɠ',
        'h':'h',
        'h\\':'ɦ',
        'i':'i',
        'j':'j',
        'j\\':'ʝ',
        'k':'k',
        'l':'l',
        'l`':'ɭ',
        'l\\':'ɺ',
        'm':'m',
        'n':'n',
        'n_d':'nd',
        'n`':'ɳ',
        'o':'o',
        'p':'p',
        'p\\':'ɸ',
        'p_<':'ɓ̥',
        'q':'q',
        'r':'r',
        'r`':'ɽ',
        'r\\':'ɹ',
        'r\\`':'ɻ',
        's':'s',
        's`':'ʂ',
        's\\':'ɕ',
        't':'t',
        't`':'ʈ',
        'u':'u',
        'v':'v',
        'v\\':'ʋ',
        'w':'w',
        'x':'x',
        'x\\':'ɧ',
        'y':'y',
        'z':'z',
        'z`':'ʐ',
        'z\\':'ʑ',
        'A':'ɑ',
        'B':'β',
        'B\\':'ʙ',
        'C':'ç',
        'D':'ð',
        'E':'ɛ',
        'F':'ɱ',
        'G':'ɣ',
        'G\\':'ɢ',
        'G\\_<':'ʛ',
        'H':'ɥ',
        'H\\':'ʜ',
        'I':'ɪ',
        'I\\':'ɪ̈ ',
        'J':'ɲ',
        'J\\':'ɟ',
        'J\\_<':'ʄ',
        'K':'ɬ',
        'K\\':'ɮ',
        'L':'ʎ',
        'L\\':'ʟ',
        'M':'ɯ',
        'M\\':'ɰ',
        'N':'ŋ',
        'N_g':'ŋɡ',
        'N\\':'ɴ',
        'O':'ɔ',
        'O\\':'ʘ',
        'P':'ʋ',
        'Q':'ɒ',
        'R':'ʁ',
        'R\\':'ʀ',
        'S':'ʃ',
        'T':'θ',
        'U':'ʊ',
        'U\\':'ʊ̈ ',
        'V':'ʌ',
        'W':'ʍ',
        'X':'χ',
        'X\\':'ħ',
        'Y':'ʏ',
        'Z':'ʒ',
        '.':'.',
        '"':'ˈ',
        '%':'ˌ',
        '\'':'ʲ',
        ':':'ː',
        ':\\':'ˑ',
        '-':'',
        '@':'ə',
        '@\\':'ɘ',
        '{':'æ',
        '}':'ʉ',
        '1':'ɨ',
        '2':'ø',
        '3':'ɜ',
        '3\\':'ɞ',
        '4':'ɾ',
        '5':'ɫ',
        '6':'ɐ',
        '7':'ɤ',
        '8':'ɵ',
        '9':'œ',
        '&':'ɶ',
        '?':'ʔ',
        '?\\':'ʕ',
        '*':'',
        '/':'',
        '<\\':'ʢ',
        '>\\':'ʡ',
        '^':'ꜛ',
        '!':'ꜜ',
        '!\\':'ǃ',
        '|':'|',
        '|\\':'ǀ',
        '||':'‖',
        '|\\|\\':'ǁ',
        '=\\':'ǂ',
        '-\\':'‿'
    }.items()
}

_xdiacritics2ipa = {
    k:re.sub(r'◌','',v) for (k,v) in {
        '"':'◌̈',
        '+':'◌̟',
        '-':'◌̠',
        '/':'◌̌',
        '0':'◌̥',
        '=':'◌̩',
        '>':'◌ʼ',
        '?\\':'◌ˤ',
        '\\':'◌̂',
        '^':'◌̯',
        '}':'◌̚',
        '`':'◌˞',
        '~':'◌̃',
        'A':'◌̘',
        'a':'◌̺',
        'B':'◌̏',
        'B_L':'◌᷅',
        'c':'◌̜',
        'd':'◌̪',
        'e':'◌̴',
        'F':'◌̂',
        'G':'◌ˠ',
        'H':'◌́',
        'H_T':'◌᷄',
        'h':'◌ʰ',
        'j':'◌ʲ',
        'k':'◌̰',
        'L':'◌̀',
        'l':'◌ˡ',
        'M':'◌̄',
        'm':'◌̻',
        'N':'◌̼',
        'n':'◌ⁿ',
        'O':'◌̹',
        'o':'◌̞',
        'q':'◌̙',
        'R':'◌̌',
        'R_F':'◌᷈',
        'r':'◌̝',
        'T':'◌̋',
        't':'◌̤',
        'v':'◌̬',
        'w':'◌ʷ',
        'X':'◌̆',
        'x':'◌̽'
    }.items()
}

def xsampa2ipa(xsampa,L):
    '''Return the IPA equivalent of X-SAMPA phone x.'''
    try:
        # First, split the whole thing into diacritic pieces
        xwords = xsampa.split('_')
        # Recombine any that exist in _xsampa2ipa
        n = 0
        while n <= len(xwords)-2:
            if '_'.join(xwords[n:(n+2)]) in _xsampa2ipa:
                xwords = xwords[0:n]+['_'.join(xwords[n:(n+2)])]+xwords[(n+2):]
            n += 1
        # Recombine the last two, if they are in _xdiacritics2ipa, and there are more than two
        if len(xwords)>2 and (xwords[-2]+'_'+xwords[-1] in _xdiacritics2ipa):
            xwords = xwords[0:(-2)] + [ xwords[-2]+'_'+xwords[-1] ]
        # Process each piece as a separate phone
        iwords = []
        for n1 in range(0,len(xwords)):
            # Divide into characters
            xchars = list(xwords[n1])
            # Recombine any sequences of 2 to 4 characters length that exist in _xsampa2ipa:
            for checklen in range(4,1,-1):
                n2 = 0
                while n2 <= len(xchars)-checklen:
                    if ''.join(xchars[n2:(n2+checklen)]) in _xsampa2ipa:
                        xchars = xchars[0:n2]+[''.join(xchars[n2:(n2+checklen)])]+xchars[(n2+checklen):]
                    n2 += 1
            # Now each symbol should be in _xsampa2ipa.  Try it and find out
            iwords.append(''.join((_xsampa2ipa[xchar] for xchar in xchars)))
        # Try processing only the last symbol as a diacritic.  If it can be done, replace the phone
        if len(xwords)>1:
            xchars = list(xwords[-1])
            if (xwords[-1] in _xdiacritics2ipa):
                iwords[-1] = _xdiacritics2ipa[xwords[-1]]
            elif all(((xchar in _xdiacritics2ipa) for xchar in xwords[-1])):
                iwords[-1] = ''.join((_xdiacritics2ipa[xchar] for xchar in xwords[-1]))
        ipa = ''.join(iwords)
        return(ipa)
    except KeyError:
        raise KeyError('Unable to find X-SAMPA symbol {} for language {}'.format(xsampa,L))

_tone2ipa = {
    'egyptian-arabic' : [ '', 'ˈ', 'ˌ' ],
    'english' : [ '', 'ˈ', 'ˌ' ],
    'yue' : [ '', '˥', '˧˥', '˧', '˨˩', '˩˧', '˨' ],
    'cantonese' : [ '', '˥', '˧˥', '˧', '˨˩', '˩˧', '˨' ],
    'lao' : [ '', '˧', '˥˧', '˧˩', '˥', '˩˧', '˩' ],
    'mandarin' : [ '', '˥', '˧˥', '˨˩˦', '˥˩', '' ],
    'spanish' : [ '', 'ˈ', 'ˌ' ],
    'vietnamese' : [ '', '˧', '˨˩h', '˧˥', '˨˩˨', '˧ʔ˥', '˧˨ʔ' ],
}
        
def tone2ipa(n, L):
    return(_tone2ipa[L][int(n[1:])])

_disc2ipa_dutch = {
    'w':'ʋ'
}

_disc2ipa_english = {
    'r':'ɻ'
}

_disc2xsampa = {
    ' ':'#',
    "'":'"',
    '_':'dZ',
    'i':'i:',
    'y':'y:',
    'e':'e:',
    '|':'2:',
    'a':'a:',
    'o':'o:',
    'u':'u:',
    '!':'i::',
    '(':'y::',
    ')':'E:',
    '*':'9:',
    '<':'Q:',
    'K':'EI',
    'L':'9I',
    '+':'pf',
    '=':'ts',
    '-':'.',
    '#':'A:',
    '$':'O:',
    '3':'3:',
    '1':'eI',
    '2':'aI',
    '4':'OI',
    '6':'aU',
    'W':'ai',
    'B':'au',
    'X':'Oy',
    '&':'a',
    '^':'9~:',
    'c':'{~',
    'q':'A~:',
    '0':'{~:',
    '~':'O~:',
    'C':'N=',
    'F':'m=',
    'H':'n=',
    'P':'l=',
    'R':'3`',
    '5':'@U',
    '7':'I@',
    '8':'E@',
    '9':'U@'
}

_disc2ipa = {}
for k in set(_disc2xsampa.keys())|set(_xsampa2ipa.keys()):
    if len(k)==1:
        if k not in _disc2xsampa:
            _disc2ipa[k] = _xsampa2ipa[k]
        else:
            x = _disc2xsampa[k]
            if x in _xsampa2ipa:
                _disc2ipa[k] = _xsampa2ipa[x]
            else:
                _disc2ipa[k] = ''.join((_xsampa2ipa[g] for g in x))
            
def disc2ipa(x, L):
    '''Convert DISC symbol x into IPA, for language L'''
    if L=='english' and x in _disc2ipa_english:
        return(_disc2ipa_english[x])
    elif L=='dutch' and x in _disc2ipa_dutch:
        return(_disc2ipa_dutch[x])
    else:
        return(_disc2ipa[x])

_ach = {
    'C':'ʔ',
    'b':'b',
    't':'t',
    'g':'g',
    'H':'ħ',
    'x':'x',
    'd':'d',
    'r':'ɾ',
    'z':'z',
    's':'s',
    '$':'ʃ',
    'S':'sˤ',
    'D':'dˤ',
    'T':'tˤ',
    'Z':'ðˤ',
    'c':'ʕ',
    'G':'ɣ',
    'f':'f',
    'q':'ʔ',
    'Q':'q',
    'k':'k',
    'l':'l',
    'm':'m',
    'n':'n',
    'h':'h',
    'w':'w',
    'y':'j',
    'v':'v',
    'j':'dʒ',
    '@':'æ',
    'a':'a',
    'B':'a',
    'i':'i',
    'u':'u',
    '%':'æː',
    'A':'aː',
    'I':'iː',
    'O':'oː',
    'U':'uː',
    'E':'eː',
    'ay':'aj',
    'aw':'aw'
}

_mch = {
    'b':'p',
    'p':'pʰ',
    'm':'m',
    'd':'t',
    't':'tʰ',
    'l':'l',
    'n':'n',
    'g':'k',
    'k':'kʰ',
    'h':'h',
    'N':'ŋ',
    'z':'ts',
    'c':'tsʰ',
    's':'s',
    'j':'tɕ',
    'q':'tɕʰ',
    'x':'ɕ',
    'r':'ɻ',
    'Z':'ʈʂ',
    'C':'ʈʂʰ',
    'S':'ʂ',
    'f':'f',
    'y':'j',
    'w':'w',
    'W':'ɥ',
    'i':'i',
    'I':'ɨ',
    '%':'ɯ',
    'e':'e',
    'E':'ɛ',
    'U':'y',
    '&':'ə',
    'a':'ɑ',
    '@':'a',
    'o':'o',
    '>':'ɔ',
    'u':'u',
    'R':'ɚ'
}

_sch = {
    'a':'a',
    'i':'i',
    'e':'e',
    'o':'o',
    'u':'u',
    'h':'h',
    'p':'p',
    'b':'b',
    'B':'β',
    'f':'f',
    'v':'v',
    'l':'l',
    'm':'m',
    'w':'w',
    't':'t',
    'd':'d',
    'D':'ð',
    's':'s',
    'S':'ʃ',
    'C':'tʃ',
    'J':'dʒ',
    'n':'n',
    'y':'j',
    'r':'ɾ',
    'R':'r',
    'x':'x',
    'N':'ɲ',
    'k':'k',
    'g':'g',
    'G':'ɣ',
    '9':'ŋ ',
    'z':'z'
}

def callhome2ipa(x,L):
    '''Convert callhome phone symbol x into IPA for language L'''
    if L=='egyptian-arabic':
        return(_ach[x])
    elif L=='mandarin':
        return(_mch[x])
    elif L=='spanish':
        return(_sch[x])
    else:
        raise RuntimeError('callhome2ipa language {} unknown; I only know egyptian-arabic, mandarin and spanish'.format(L))


_arpabet2ipa = {
    'AA':'ɑ',
    'AE':'æ',
    'AH':'ʌ',
    'AO':'ɔ',
    'AW':'aʊ',
    'AX':'ə',
    'AXR':'ɚ',
    'AY':'aɪ',
    'EH':'ɛ',
    'ER':'ɝ',
    'EY':'eɪ',
    'IH':'ɪ',
    'IX':'ɨ',
    'IY':'i',
    'OW':'oʊ',
    'OY':'ɔɪ',
    'UH':'ʊ',
    'UW':'u',
    'UX':'ʉ',
    'B':'b',
    'CH':'tʃ',
    'D':'d',
    'DH':'ð',
    'DX':'ɾ',
    'EL':'l̩ ',
    'EM':'m̩',
    'EN':'n̩',
    'F':'f',
    'G':'ɡ',
    'HH':'h',
    'JH':'dʒ',
    'K':'k',
    'L':'l',
    'M':'m',
    'N':'n',
    'NG':'ŋ',
    'NX':'ɾ̃',
    'P':'p',
    'Q':'ʔ',
    'R':'ɹ',
    'S':'s',
    'SH':'ʃ',
    'T':'t',
    'TH':'θ',
    'V':'v',
    'W':'w',
    'WH':'ʍ',
    'Y':'j',
    'Z':'z',
    'ZH':'ʒ'
}

def arpabet2ipa(x):
    '''Convert ARPABET symbol X to IPA'''
    if isdigit(x):
        return(_tone2ipa['english'][int(x)])
    else:
        return(_arpabet2ipa[x.upper()])

_timit2ipa = {
    'AX-H':'ə̥',
    'BCL':'b',
    'B':'∅',
    'DCL':'d',
    'D':'∅',
    'GCL':'g',
    'G':'∅',
    'PCL':'p',
    'P':'∅',
    'TCL':'t',
    'T':'∅',
    'KCL':'k',
    'K':'∅',
    'ENG':'ŋ̍',
    'HV':'ɦ',
    'PAU':'∅',
    'EPI':'∅',
    'H#':'∅'
}

def timit2ipa(x):
    '''Convert TIMIT phone codes to IPA'''
    x = x.upper()
    if x in _timit2ipa:
        return(_timit2ipa[x])
    else:
        return(_arpabet2ipa[x])
