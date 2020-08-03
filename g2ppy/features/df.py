import argparse,json,csv,logging
from collections import defaultdict

def csv2listlist(inputpath):
    listlist = []
    with open(inputpath,encoding='utf-8-sig')  as f:
        s = f.read()
        rows = s.split('\n')
        for row in rows:
            listlist.append(row.split(','))
    return(listlist)

def csv2dictdict(inputpath):
    dictdict = {}
    with open(inputpath,encoding='utf-8-sig')  as f:
        reader = csv.DictReader(f)
        for row in reader:
            p = row['segment']
            dictdict[p] = row
    return(dictdict)

def find_unigraphs_in_listlist(listlist):
    '''Find the unigraphs in a list of distinctive feature specifiers'''
    found = {}
    missing = defaultdict(list)
    for row in listlist[1:]:
        p=row[0]
        if len(p)==1:
            found[p] = row
        else:
            for c in p:
                if c not in found:
                    missing[c].append(row)
    for c in found:
        if c in missing:
            del missing[c]
    return(found,missing)

def find_unigraphs_in_dictdict(dictdict):
    '''Find the unigraphs in a list of distinctive feature specifiers'''
    found = {}
    missing = defaultdict(list)
    for (p,row) in dictdict.items():
        if len(p)==1:
            found[p] = row
        else:
            for c in p:
                if c not in found:
                    missing[c].append(row)
    for c in found:
        if c in missing:
            del missing[c]
    return(found,missing)

def find_common_features_in_listlist(char,listlist):
    '''Find the common features among several feature vectors, output the resulting list'''
    features = listlist[0][:]
    features[0] = char
    if len(listlist)>1:
        for row in listlist[1:]:
            if len(row) != len(features):
                logging.warning("%s %d feats, %s %d"%(listlist[0][0],len(features),row[0],len(row)))
            for k in range(1,min(len(row),len(features))):
                if row[k] != features[k]:
                    features[k] = '0'
    return(features)

def find_common_features_in_dictlist(char,dictlist):
    '''Find the common features among several feature vectors, output the resulting list'''
    features = dictlist[0].copy()
    features['segment'] = char
    if len(dictlist)>1:
        for row in dictlist[1:]:
            if len(row) != len(features):
                logging.warning("%s %d feats, %s %d"%(dictlist[0]['segment'],len(features),row['segment'],len(row)))
            for k in row.keys():
                if k in features.keys():
                    if row[k] != features[k]:
                        features[k] = '0'
    return(features)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Separate out unigraphs and non-unigraphs')
    parser.add_argument('inputpath',help='input CSV table listing features of each phone')
    parser.add_argument('found',help='output json table: features of found unigraphs')
    parser.add_argument('missing',help='output json table: features of missing unigraphs')
    args = parser.parse_args()

    logging.basicConfig()
    #listlist = csv2listlist(args.inputpath)
    dictdict = csv2dictdict(args.inputpath)
    #(found,missing) = find_unigraphs_in_listlist(listlist)
    (found,missing) = find_unigraphs_in_dictdict(dictdict)
    with open(args.found,'w')  as f:
        f.write(json.dumps(found,ensure_ascii=False,indent=0))
        #writer = csv.writer(f)
        #writer.writerow(listlist[0]) # header
        #for p in sorted(found.keys()):
        #    writer.writerow(found[p])


    missing_unigraphs = {}
    with open(args.missing,'w')  as f:
        #writer = csv.writer(f)
        #writer.writerow(listlist[0])
        #for p in sorted(missing.keys()):
        #    writer.writerow(find_common_features_in_listlist(p,missing[p]))
        for p in sorted(missing.keys()):
            missing_unigraphs[p] = find_common_features_in_dictlist(p,missing[p])
        f.write(json.dumps(missing_unigraphs,ensure_ascii=False,indent=0))
