import phonetisaurus
import os,glob

###################################################################
# List characters used as 'phones' in ../_train/exp/dicts
if  __name__=="__main__":
    symbolset = set()
    for dictfile in glob.glob('../_train/exp/dicts/*.txt'):
        pronlex = phonetisaurus.load_dict_from_txtfile(dictfile)
        for pronlist  in pronlex.values():
            for pron in pronlist:
                symbolset.update(pron)
    print(symbolset)
