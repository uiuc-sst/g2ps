import argparse,json

def csv2listlist(inputpath):
    listlist = []
    with open(inputpath)  as f:
        s = f.read()[1:]  # eliminate the FEFF character
        rows = s.split('\n')
        for row in rows:
            listlist.append(row.split(','))
    return(listlist)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert CSV file to JSON')
    parser.add_argument('inputpath',help='Path to the input CSV file')
    parser.add_argument('outputpath',help='Path to the output JSON file')
    args = parser.parse_args()
    listlist = csv2listlist(args.inputpath)
    with open(args.outputpath,'w') as f:
        f.write(json.dumps(listlist,indent=0,ensure_ascii=False))
    
    
