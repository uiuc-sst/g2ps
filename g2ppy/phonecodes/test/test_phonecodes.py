import sys,os,re
import pprint
sys.path.append('../src')
import pronlex
import phonecodes
from sentences import sents

'''This script should be run from the command line, in the test directory.
   It will load some pronlexes from the 'fixtures' subdirectory,
   test phone code conversion, and test both word and phone searches.'''

os.makedirs('outputs',exist_ok=True)
# First, test the phonecode conversions
with open('outputs/test_phonecodes.txt','w') as f:
    original=sys.stdout
    sys.stdout = f
    phonecode_cases = [
        ('arpabet','ipa',phonecodes.arpabet2ipa,'eng'),
        ('ipa','arpabet',phonecodes.ipa2arpabet,'eng'),
        ('ipa','callhome',phonecodes.ipa2callhome,'arz'),
        ('ipa','callhome',phonecodes.ipa2callhome,'cmn'),
        ('ipa','callhome',phonecodes.ipa2callhome,'spa'),
        ('callhome','ipa',phonecodes.callhome2ipa,'arz'),
        ('callhome','ipa',phonecodes.callhome2ipa,'cmn'),
        ('callhome','ipa',phonecodes.callhome2ipa,'spa'),
        ('ipa','disc',phonecodes.ipa2disc,'deu'),
        ('ipa','disc',phonecodes.ipa2disc,'eng'),
        ('ipa','disc',phonecodes.ipa2disc,'nld'),
        ('disc','ipa',phonecodes.disc2ipa,'deu'),
        ('disc','ipa',phonecodes.disc2ipa,'eng'),
        ('disc','ipa',phonecodes.disc2ipa,'nld'),
        ('ipa','xsampa',phonecodes.ipa2xsampa,'amh'),
        ('ipa','xsampa',phonecodes.ipa2xsampa,'ben'),
        ('xsampa','ipa',phonecodes.xsampa2ipa,'amh'),
        ('xsampa','ipa',phonecodes.xsampa2ipa,'ben')
        ]
    for case in phonecode_cases:        
        print('##### %s2%s ############################'%(case[0],case[1]))
        print('%s %s'%(case[0],sents[case[3]][case[0]]))
        res=case[2](sents[case[3]][case[0]],case[3])
        suc='Pass' if res==sents[case[3]][case[1]] else 'FAIL'
        print('%s: %s *** %s'%(case[1],res,suc))
        print('')
    sys.stdout=original

