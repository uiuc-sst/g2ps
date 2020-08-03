This directory contains code used to look up the articulatory features of the phones
in each language, and to create the corresponding tables.


segments2languages2.rb Create an inventory CSV for each language specifying distinctive features.
html2features.rb Parse each segment's HTML to extract its distinctive feature values.
segment_distances.rb Compute a segment-distance table based on features.
------------------

# Following is the README file from 2016, contains information about downloading the  original files from phoible

This directory contains code used to create the dictionary files.

Mark Hasegawa-Johnson
3/28/2015
steps 6 and 7 updated 6/10/2016

Usage___

1. Download parameters.csv, a list of all segments, from phoible.org
2. run parameters2html.rb to download HTML for each segment
3. run html2features.rb to extract segments.csv feature table
4. Download Values.csv for each language
5. run segments2languages.rb to map segments.csv into each language

6. update the file ../_config/languages2.csv
7. run csv2html.rb to create index.html

