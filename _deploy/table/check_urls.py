#!/usr/bin/python3
'''check_urls.py inputfile
   Read inputfile, find all of the URLs, and report which ones are bad links.
'''

import sys,os
import html.parser
import urllib.error,urllib.request

hrefs = []

class MyHTMLParser(html.parser.HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag=='a':
            for a in attrs:
                if a[0]=='href':
                    hrefs.append(a[1])



if __name__=="__main__":

    if len(sys.argv)<2:
        print(__doc__)
        exit(0)
    inputfile=sys.argv[1]

    parser = MyHTMLParser()
    with open(inputfile) as f:
        content=f.read()
        parser.feed(content)
        
        for href in hrefs:
            if os.path.isfile(href):
                sys.stdout.write('f')
                sys.stdout.flush()
                #print('Success {}'.format(href))
            else:
                try:
                    urllib.request.urlopen(href)
                    sys.stdout.write('u')
                    sys.stdout.flush()
                    #print('Success {}'.format(href))
                except urllib.error.URLError as err:
                    print('\n***** ERROR {} because {}: {}'.format(href,err.code,err.reason))
                except ValueError as err:
                    print('\n***** ERROR {}'.format(href))

