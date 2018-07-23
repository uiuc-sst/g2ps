    <h1>LanguageNet Grapheme-to-Phoneme Transducers</h1>
    <h2>Usage</h2>
    <ol>
    <li>Download and install 
    <a href="https://github.com/AdolfVonKleist/Phonetisaurus">Phonetisaurus</a></li>
    <li>Get your own copy of the G2Ps:
    <code>git clone https://uiuc-sst/g2ps</code></li>
    <li>Test the installation:
    <code>phonetisaurus-g2pfst --model=g2ps/models/akan.fst --word=ahyiakwa</code><br />
    You should see the answer "ahyiakwa	21.7336	a ç i a ɥ a˥".</li>
    </ol>   
    <h2>Description</h2>
    <ul>
    <li>The column "FSTs" is a trained grapheme-to-phoneme transducer for use with
    phonetisaurus.   If the available lexicons were large enough to test the phone error
    rate (PER), then it is listed in parentheses.  As of this writing, PERs range from
    7\% to 45\%.  Note: some of the trained models exceed git's file size limit, so
    they're not available on the github page; you can still find them at 
    <a href="http://isle.illinois.edu/sst/data/g2ps/">http://isle.illinois.edu/sst/data/g2ps/</a>.
    Currently those are (american-english, arabic, dutch, french, german, 
    portuguese, russian, spanish, turkish).
    </li>
    <li>The column "Pronlexes" lists pronunciation lexicons distributed on this
    site; most are just short symbol tables, but a few are longer.</li>
    <li>Other columns are just pointers to sources.</li>  
    </ul>
    <h2>Acknowledgments</h2>
      <p>
        This project was funded from 2016-2019 as part of the <a
        href="http://www.isle.illinois.edu/sst/research/darpa2015/index.html">LanguageNet</a>.
        Phonetisaurus G2Ps were trained using the lexicons listed
        here, and the lexicons in the LanguageNet.  Some languages had
        other sources: <a
        href="https://www.iarpa.gov/index.php/research-programs/babel">Appen
        BABEL</a> lexicons (amharic, assamese, bengali, cebuano,
        georgian, guarani, haitian, igbo, javanese, kurdish, lao,
        lithuanian, luo, mongolian, pushto, swahili, tagalog, tamil,
        tok-pisin, turkish, vietnamese, yue, zulu), <a
        href="https://catalog.ldc.upenn.edu/ldc96l14">CELEX</a>
        (dutch, english, german), CALLHOME (<a
        href="https://catalog.ldc.upenn.edu/LDC99L22">egyptian-arabic</a>,
        <a href="https://catalog.ldc.upenn.edu/LDC96L15">mandarin</a>,
        <a href="https://catalog.ldc.upenn.edu/LDC96L16">spanish</a>).
      </p>
