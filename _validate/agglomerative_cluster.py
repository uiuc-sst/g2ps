import csv,os,glob,logging,subprocess,shutil,re,pycountry,itertools,math
import phonetisaurus
import numpy as np

logging.basicConfig(level=logging.ERROR)

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
    def __init__(self, chars, phonelist):
        '''A Word is a sequence of characters, and a list of different possible pronunciations.
        Each pronunciation is a list of Phones.'''
        self.chars = chars
        self.prons = []
        for pron in phonelist:
            self.prons.append([ Phone(p) for p in pron ])
    def dist(self,other):
        '''Distance between words = Levenshtein distance of their phones,
        divided by the number of correct phones in longer of the two pronunciations,
        averaged over the possible pronunciations of each of the two words.
        '''
        totd = 0
        totn = 0
        for pron1 in self.prons:
            for pron2 in other.prons:
                maxlen = max(len(pron1),len(pron2))
                # substitution distances
                sub = [ [ p1.dist(p2) for p2 in pron2 ] for p1  in pron1  ]
                # total distance: initialize using  insert-delete-only  distance
                tot = [ [ n1+n2 for n2  in  range(len(pron2)+1) ] for n1 in range(len(pron1)+1) ]
                # total distance = min(substitution, insertion, deletion)
                for n1 in range(1,len(pron1)+1):
                    for n2 in range(1,len(pron2)+1):
                        tot[n1][n2] = min(tot[n1-1][n2-1]+sub[n1-1][n2-1],
                                          tot[n1][n2-1]+1, tot[n1-1][n2]+1)
                # Add this distance to totd
                totd += tot[-1][-1]/maxlen
                totn += 1
        return(totd/totn)

class Cluster():
    def __init__(self, child1, child2, name, dist):
        self.child1 = child1
        self.child2 = child2
        self.name = name
        self.dist = dist
        if type(child1)==Cluster:
            N1 = child1.N
        else:
            N1 = 1
        if type(child2)==Cluster:
            N2 = child2.N
        else:
            N2 = 1
        self.N = N1+N2
    def ppr(self,level):
        return('[' + self.child1.ppr(level+1)+',\n' +
               ' '*(level+1) + str(self.dist) +'\n'  +
               ' '*(level+1) + self.child2.ppr(level+1) + ']'
        )

def languagedist(self,other):
    prons = other.apply_g2p(self.wordlist,self.name)
    distances = {}
    for w in self.wordlist:
        if w in prons:
            distances[w] = Word(w,self.pronlex[w]).dist(Word(w,prons[w]))
    if len(distances)>0:
        aved = sum([d for d in distances.values()]) / len(distances)
    else:
        aved = 1
    return(aved, prons, distances)
phonetisaurus.Language.dist = languagedist

MAX_WORDLIST_LEN=1000    
def agglomerate(dict2dat):
    '''Create an agglomerative clustering of a set of g2ps,
    using the corresponding dictionaries to define the distance measure'''
    clusters = [ phonetisaurus.Language(dat[1],'qqq',dat[0],dic) for (dic,dat) in dict2dat.items() ]
    for c in clusters:
        c.load_charset()
        c.wordlist=c.wordlist[::max(1,int(len(c.wordlist)/MAX_WORDLIST_LEN))] #downsample
        
    # Calculate the dist matrix: distance to self is always np.inf, to avoid trivial clusters
    dist = np.tile(np.inf,(len(clusters),len(clusters)))
    os.makedirs('exp/distances',exist_ok=True)
    for (n1,n2) in itertools.combinations(range(len(clusters)),2):
        L1 = clusters[n1]
        L2 = clusters[n2]
        print('Calculating dist(%d: %s, %d: %s)'%(n1,L1.name,n2,L2.name))
        d12, prons12, dw12 = L1.dist(L2)
        d21, prons21, dw21 = L2.dist(L1)
        dist[n1][n2] = (d12+d21)/2
        dist[n2][n1] = (d12+d21)/2
        # Write the comparative dict, and word distances
        with open(os.path.join('exp','distances','%s_%s_%g.txt'%(L1.name,L2.name,d12)),'w') as f:
            for w in prons12.keys():
                f.write('%s\t%s\t%g\t%s\n'%(str(w),str(L1.pronlex[w]),dw12[w],str(prons12[w])))
        with open(os.path.join('exp','distances','%s_%s_%g.txt'%(L2.name,L1.name,d21)),'w') as f:
            for w in prons21.keys():
                f.write('%s\t%s\t%g\t%s\n'%(str(w),str(L2.pronlex[w]),dw21[w],str(prons21[w])))
            
    # Now cluster them
    while len(clusters)>1:
        m1=np.argmin(np.min(dist,axis=1),axis=0)    # row number of min-distance pair
        m2=np.argmin(dist[m1,:])                    # column number of min-distance pair
        md = dist[m1,m2]
        N1 = clusters[m1].N
        N2 = clusters[m2].N
        avgdist = (N1*dist[m1,:]+N2*dist[m2,:])/(N1+N2) # avg of distances to all other clusters
        dist[m1,:] = avgdist
        dist[:,m1] = avgdist
        dist = np.delete(np.delete(dist,m2,1),m2,0)
        clustername = 'cluster%d'%(len(clusters))
        print('Merging %s and %s at %g to form %s'%(clusters[m1].name,clusters[m2].name,md,clustername))
        clusters[m1] = Cluster(clusters[m1],clusters[m2],clustername,md)
        clusters.pop(m2)
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
    # Keep these dicts
    for dictfile in glob.glob('../_train/exp/dicts/*.txt'):
        languagename = os.path.splitext(os.path.basename(dictfile))[0]
        language2dict[languagename] = [ dictfile ]
    dict2dat = {}
    os.makedirs('exp/models',exist_ok=True)
    #
    # Instead of these models, use only the wikipedia models?
    models = glob.glob('../models/*.gz')
    for modelpath in models:
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
    # TODO: Find some better way to write out the clustering results!!
    with open('outputfile.txt','w') as f:
        f.write(clusters[0].ppr(0))    
