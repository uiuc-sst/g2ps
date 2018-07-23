    # LanguageNet Grapheme-to-Phoneme Transducers
    ## Usage
    * Download and install 
    [Phonetisaurus](https://github.com/AdolfVonKleist/Phonetisaurus)
    * Get your own copy of the G2Ps:
    `git clone https://uiuc-sst/g2ps`
    * Test the installation:
    `phonetisaurus-g2pfst --model=g2ps/models/akan.fst --word=ahyiakwa`
    You should see the answer "ahyiakwa	21.7336	a ç i a ɥ a˥".

## Description
    * The column "FSTs" is a trained grapheme-to-phoneme transducer for use with
    phonetisaurus.   If the available lexicons were large enough to test the phone error
    rate (PER), then it is listed in parentheses.  As of this writing, PERs range from
    7\% to 45\%.  Note: some of the trained models exceed git's file size limit, so
    they're not available on the github page; you can still find them at 
    [http://isle.illinois.edu/sst/data/g2ps/](http://isle.illinois.edu/sst/data/g2ps/).
    Currently those are (american-english, arabic, dutch, french, german, 
    portuguese, russian, spanish, turkish).
    * The column "Pronlexes" lists pronunciation lexicons distributed on this
    site; most are just short symbol tables, but a few are longer.
    * Other columns are just pointers to sources.

## Acknowledgments

        This project was funded from 2016-2019 as part of the <a
        [LanguageNet](http://www.isle.illinois.edu/sst/research/darpa2015/index.html).
        Phonetisaurus G2Ps were trained using the lexicons listed
        here, and the lexicons in the LanguageNet.  Some languages had
        other sources: [Appen BABEL](https://www.iarpa.gov/index.php/research-programs/babel)
        lexicons (amharic, assamese, bengali, cebuano,
        georgian, guarani, haitian, igbo, javanese, kurdish, lao,
        lithuanian, luo, mongolian, pushto, swahili, tagalog, tamil,
        tok-pisin, turkish, vietnamese, yue, zulu),
        [CELEX](https://catalog.ldc.upenn.edu/ldc96l14)
        (dutch, english, german), CALLHOME ([egyptian-arabic](https://catalog.ldc.upenn.edu/LDC99L22),
        [mandarin](https://catalog.ldc.upenn.edu/LDC96L15),
        [spanish](https://catalog.ldc.upenn.edu/LDC96L16)).
	

