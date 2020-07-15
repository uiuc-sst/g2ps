import csv,os,glob,logging,subprocess,shutil,re,pycountry,itertools
import phonetisaurus
import numpy as np

phone2feat = {}
phone2feat_file = '../_config/phoibletable.csv'
with open(phone2feat_file, encoding='utf-8') as f:
    for row in csv.reader(f, delimiter=',', quotechar='"'):
        phone2feat[row[0]] = row[1:]

class Phone():
    def  __init__(self, char):
        '''Initialize a phone by looking up its articulatory feature vector'''
        self.c = char
        if self.c not in phone2feat:
            #logging.warning('Phone [%s] not in phone2feat.  It will have zero features.'%(self.c))
            self.f=[]
            self.nf = 0
        else:
            self.f = phone2feat[self.c]
            self.nf = len(self.f)
    def dist(self,other):
        '''Distance between two phones = fraction of features in self that differ from other.
        This is an asymmetric dist if and only if the two phones have different numbers of features.
        '''
        if self.nf==0:
            return(1)
        else:
            d=len([1 for n in range(self.nf) if n>=other.nf or self.f[n] != other.f[n]])
            return(d/self.nf)

class Word():
    def __init__(self, chars, phones):
        '''A Word is a sequence of characters, and a sequence of phones'''
        self.chars = chars
        self.phones = [ Phone(p) for p in phones ]
    def dist(self,other):
        '''Distance between words = Levenshtein distance of their phones'''
        # substitution distances
        sub = [ [ p1.dist(p2) for p2 in other.phones ] for p1  in self.phones  ]
        # total distance: initialize using  insert-delete-only  distance
        tot = [ [ n1+n2 for n2  in  range(len(other.phones)+1) ] for n1 in range(len(self.phones)+1) ]
        # total distance = min(substitution, insertion, deletion)
        for n1 in range(1,len(self.phones)+1):
            for n2 in range(1,len(other.phones)+1):
                tot[n1][n2] = min(tot[n1-1][n2-1]+sub[n1-1][n2-1], tot[n1][n2-1]+1, tot[n1-1][n2]+1)
        # return tot distance at the end of the word
        return(tot[-1][-1])

class Cluster():
    def __init__(self, child1, child2, name):
        self.child1 = child1
        self.child2 = child2
        self.name = name
        if type(child1)==Cluster():
            N1 = child1.N
        else:
            N1 = 1
        if type(child2)==Cluster():
            N2 = child2.N
        else:
            N2 = 1
        self.N = N1+N2
    def __str__(self,level):
        return('[' + str(child1,level+1)+',\n' + ' '*(level+1) + str(child2,level+1) + ']')

def dist2wordlist(L1,L2):
    sumd = 0
    wordlist = [ k for k in L1.pronlex.keys() ]
    prons = L2.apply_g2p(wordlist)
    n = 0
    for w in L1.pronlex.keys():
        if w in prons:
            n += 1
            sumd += Word(w,L1.pronlex[w]).dist(Word(w,prons[w]))
    print('Comparing %s dict to %s g2p: %d words'%(L1.name,L2.name,n))
    return(sumd/n)

def agglomerate(dict2dat):
    '''Create an agglomerative clustering of a set of g2ps,
    using the corresponding dictionaries to define the distance measure'''
    clusters = [ phonetisaurus.Language(dat[1],'qqq',dat[0],dic) for (dic,dat) in dict2dat.items() ]
    indices = [ n for n in range(len(clusters)) ]
    nums = [ 1 for n in range(len(clusters)) ]
    for c in clusters:
        c.load_pronlex()
    # Calculate the dist matrix
    dist = np.zeros((len(clusters),len(clusters)))
    for (n1,n2) in itertools.combinations(range(len(clusters)),2):
        d12 = dist2wordlist(clusters[n1],clusters[n2])
        d21 = dist2wordlist(clusters[n2],clusters[n1])
        dist[n1][n2] = d12+d21
        dist[n2][n1] = d12+d21
    # Now cluster them
    while len(clusters)>1:
        md = math.inf
        for (n1,n2) in itertools.combinations(indices,2):
            if dist[n1][n2] < mindist:
                md = dist[n1][n2]
                mp = (n1,n2)
        # Compute average of distances to each other language
        dist[mp[0]] = (nums[mp[0]]*dist[mp[0]]+nums[mp[1]]*dist[mp[1]])/(nums[mp[0]]+nums[mp[1]])
        nums[mp[0]] += nums[mp[1]]
        nums[mp[1]] = 0
        indices.pop(mp[1])
        clusters[mp[0]] = Cluster(clusters[mp[0]],clusters[mp[1]],'cluster%d'%(len(clusters)))
        clusters.pop(mp[1])
    # Return the clusters
    return(clusters)

special_case_languagenames = {
    'ber':'Standard_Moroccan_Tamazight',
}    
special_case_modelnames = {
    'Assyrian_Neo_Aramaic': 'Assyrian_Neo-Aramaic',
    'Sotho':'Southern_Sotho',
    'Greek':'Modern_Greek',
    'Khmer':'Northern_Khmer',
    'Mandarin':'Mandarin_Chinese',
    'Min_Nan':'Min_Nan_Chinese',
    'Ndebele':'North_Ndebele',
    'Tok_Pisin': 'Tok-Pisin',
    'Wu':'Wu_Chinese',
    'Yue':'Yue_Chinese',
    'Berber':'Standard_Moroccan_Tamazight',
    'Levantine_Arabic':'North_Levantine_Arabic',
    'Hmong_Dô':'Hmong-Dô',
    'Luba_Lulua':'Luba-Lulua',
    }

###################################################################
# Load dictionary defs from ../_train/preprocess/pronlexlist.txt,
# then load G2P filenames from ../models,
# try to match them, then call cluster
if  __name__=="__main__":
    language2dict = {}
    for dictfile in glob.glob('../_train/exp/dicts/*.txt'):
        languagename = os.path.splitext(os.path.basename(dictfile))[0]
        language2dict[languagename] = [ dictfile ]
    dict2dat = {}
    os.makedirs('exp/models',exist_ok=True)
    for modelpath in glob.glob('../models/*.gz'):
        modelname = os.path.splitext(os.path.basename(modelpath))[0]
        modelfile = os.path.join('exp','models',modelname)
        if not os.path.exists(modelfile):
            shutil.copyfile(modelpath, modelfile+'.gz')
            subprocess.run(['gunzip',modelfile+'.gz'])
        languagename = '_'.join([ w.capitalize() for w in re.sub(r'_.*','',modelname).split('-') ])
        if languagename in special_case_modelnames:
            languagename = special_case_modelnames[languagename]
        if languagename not in language2dict:
            logging.warning('%s not in pronlexlist; skipping'%(languagename))
        else:
            for dictfile in language2dict[languagename]:
                dict2dat[dictfile] = [ modelfile, languagename ]
    clusters = agglomerate(dict2dat)
    with open('outputfile.txt','w') as f:
        f.write(str(clusters[0]))    
