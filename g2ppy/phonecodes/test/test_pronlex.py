import sys,os,re
import pprint
import filecmp
sys.path.append('../src')
import pronlex
import phonecodes

'''This script should be run from the command line, in the test directory.
   It will load some pronlexes from the 'fixtures' subdirectory,
   test phone code conversion, and test both word and phone searches.'''

os.makedirs('outputs',exist_ok=True)

fixtures= [
    ['isle_eng_sample',['arpabet','disc','xsampa']],
    ['babel_amh_sample',['xsampa']],
    ['babel_ben_sample',['xsampa']],
    ['celex_deu_sample',['disc','xsampa']],
    ['celex_eng_sample',['arpabet','disc','xsampa']],
    ['celex_nld_sample',['disc','xsampa']],
    ['callhome_arz_sample',['callhome','xsampa']],
    ['callhome_cmn_sample',['callhome','xsampa']],
    ['callhome_spa_sample',['callhome','xsampa']],
]
p = {}
original = sys.stdout
sys.stdout = open(os.path.join('outputs','test_pronlex.txt'),'w')

#########################################################################
# Test reading in dictionaries, converting phonecodes, and writing them
for fixture in fixtures:
    srcfile = fixture[0]
    p[srcfile]={}
    (dtype,lang,rem)=srcfile.split('_')
    dict_params = {}
    if dtype=='isle':
        dict_params['discard_phones'] = '#.'    
    print('Reading %s dict in %s from %s'%(dtype,lang,srcfile))
    p[srcfile]['ipa']=pronlex.read(os.path.join('fixtures',srcfile)+'.txt',lang,dtype,dict_params).recode('ipa')
    
    # Convert to each target code, and back again, and check results
    for c1 in fixture[1]:
        for c in [['ipa',c1],[c1,'ipa']]:
            print('##########################################################')
            print('# Testing %s[%s].recode(%s)'%(srcfile,c[0],c[1]))
            p[srcfile][c[1]] = p[srcfile][c[0]].recode(c[1])
            destfile=re.sub(r'sample',c[1],srcfile)
            print('%s -> %s'%(srcfile,destfile))
            p[srcfile][c[1]].save(os.path.join('outputs',destfile)+'.txt')
            with open(os.path.join('fixtures',destfile)+'.txt') as f:
                flines = f.readlines()
                flines.append('-----\n')
            with open(os.path.join('outputs',destfile)+'.txt') as f:
                olines = f.readlines()
                olines.append('-----\n')
            if flines==olines:
                print('Pass')
            else:
                print(''.join(['FAIL\n']+flines+olines))

####################################################################
# Test looking up words
from sentences import sents
slists={L:{c:[p for p in S.split(' ')] for (c,S) in D.items()} for (L,D) in sents.items()}
for fixture in fixtures:
    srcfile=fixture[0]
    (dtype,lang,rem)=srcfile.split('_')
    for c1 in ['ipa']+fixture[1]:
        # Test words2phones
        print('##########################################################')
        print('# Testing words2phones(%s,%s)'%(srcfile,c1))

        res = p[srcfile][c1].words2phones(slists[lang]['word'])
        pat=re.compile(' '.join(slists[lang][c1]),re.IGNORECASE)
        if res==slists[lang][c1]:
            print('Pass')
        else:
            print('FAIL')
            m=min(len(res),len(slists[lang][c1]))
            for n in range(0,m):
                if slists[lang][c1][n]==res[n]:
                    print('%s == %s'%(res[n],slists[lang][c1][n]))
                else:
                    print('%s != %s'%(res[n],slists[lang][c1][n]))
            if len(slists[lang][c1])>m:
                print('Ref chars not in hyp:'+':'.join(slists[lang][c1][m:]))
            elif len(res)>m:
                print('Hyp chars not in ref:'+':'.join(res[m:]))
                

        # Test phones2words
        print('##########################################################')
        print('# Testing phones2words(%s,%s)'%(srcfile,c1))
        res = p[srcfile][c1].phones2words(slists[lang][c1])
        pat=re.compile(' '.join(slists[lang]['word']),re.IGNORECASE)
        if any(re.match(pat,' '.join(x)) for x in res[0]):
            print('Pass')
        else:
            print('FAIL')
            print('Target:'+':'.join(slists[lang]['word']))
            print('Results:['+']['.join([':'.join(x) for x in res])+']')


# Test phones2words with 1 or 2 phone distance allowed
print('\n##########################################################')
print('# Testing phones2words(isle_eng_sample) with dist==2')
srcfile='isle_eng_sample'
lang='eng'
c1='ipa'
res = p[srcfile][c1].phones2words(slists[lang][c1],2)
for d in sorted(res.keys()):
    print('### Candidates with string edit distance == %d'%(d))
    for c in res[d]:
        print(' '.join(c))
