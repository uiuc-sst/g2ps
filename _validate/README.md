
Code for validating the content of index.html, and for validating the G2Ps.

* agglomerative_cluster.py - cluster languages based on the similarities of their
  grapheme-to-phoneme maps.   outputfile.txt is its output.

* list_chars.py - go through a list of dictionaries, and list the characters
  in the phone symbols they contain.

* g2ipa2asr.py - G2P a text, then convert to the Aspire phone set,
  so it can be used with the Kaldi Aspire recipe.  Uses the following two text files:
  * aspire2ipa.txt
  * arpabet2ipa.txt

* phoibletable.csv - the table that maps phones to articulatory  features.

