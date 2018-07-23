#!/usr/bin/ruby
# coding: utf-8
# convert the languages.csv file to an index.html file with dictionaries
require 'csv'

unless ARGV.size >= 2 then
  print "  USAGE: csv2html_languages.rb ../_config/languages3.csv ../index.html\n"
  print "  Converts a CSV table of language resources into an HTML table\n"
  exit
end
csvfilename = ARGV[0];
htmlfilename = ARGV[1];


# Heredoc: header and footer for the HTML file
htmlheader = <<ENDHEADER
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
  </head>
  <body bgcolor="#ffffff">
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
    <table border=1>
      <tr>
        <th>Codes</th>
        <th>Names</th>
        <th>FSTs</th>
        <th>Pronlexes</th>
        <th>Texts</th>
        <th>Sources</th>
      </tr>
ENDHEADER
htmlfooter = <<ENDFOOTER
    </table>
  </body>
</html>
ENDFOOTER

###########
# 1. Read the CSV, strip the header, store the rest in specialized bins

names = {}
codes = {}
sources = {}
pronlexes = {}
fsts = {}
texts = {}

f = File.open(csvfilename)
arr_of_arrs = CSV.read(csvfilename)
csvhead = arr_of_arrs.shift()
targets = ['n','c','c','0','s','p','s','p','s','t','s','t','s','t','t','f']
arr_of_arrs.each do |arr|
  if arr[1].is_a?(String) then
    iso6393 = arr[1].encode(Encoding::UTF_8)
    names[iso6393] = [] unless names.key?(iso6393)
    codes[iso6393] = [] unless codes.key?(iso6393)
    sources[iso6393] = [] unless sources.key?(iso6393)
    texts[iso6393] = [] unless texts.key?(iso6393)
    pronlexes[iso6393] = [] unless pronlexes.key?(iso6393)
    fsts[iso6393] = [] unless fsts.key?(iso6393)
  end
  arr.each_with_index do |x,n|
    # if it's a string
    if x.is_a?(String) then
      y = x.encode(Encoding::UTF_8).split(/;/)

      if targets[n] == 'n' then
        names[iso6393].concat(y)
      elsif targets[n] == 'c' then
        codes[iso6393].concat(y)
      elsif targets[n] == 's' then
        sources[iso6393].concat(y)
      elsif targets[n] == 't' then
        texts[iso6393].concat(y)
      elsif targets[n] == 'p' then
        pronlexes[iso6393].concat(y)
      elsif targets[n] == 'f' then
        fsts[iso6393].concat(y)
      end
    end
  end
end

# 3. Create the HTML file
File.open(htmlfilename,"w:UTF-8") do |f|
  f.print htmlheader

  codes.keys.sort.each do |iso6393|
    f.print "      <tr>\n"
    f.print "        <td>\n"
    codes[iso6393].each{|x| f.print "          #{x}<br />\n" }
    f.print "        </td>\n"
    f.print "        <td>\n"
    names[iso6393].each{|x| f.print "          #{x}<br />\n" }
    f.print "        </td>\n"
    f.print "        <td>\n"
    fsts[iso6393].each{|x|
      y=x.split(/[\(\)]/)
      f.print "          <a href=\"#{y[0]}\">#{y[0]}</a>(#{y[1]})<br />\n"
    }
    f.print "        </td>\n"
    f.print "        <td>\n"
    pronlexes[iso6393].each{|x| f.print "          <a href=\"#{x}\">#{x}</a><br />\n" }
    f.print "        </td>\n"
    f.print "        <td>\n"
    texts[iso6393].each{|x| f.print "          <a href=\"#{x}\">#{x}</a><br />\n" }
    f.print "        </td>\n"
    f.print "        <td>\n"
    sources[iso6393].each{|x| f.print "          <a href=\"#{x}\">#{x}</a><br />\n" }
    f.print "        </td>\n"
    f.print "      </tr>\n"
  end

  f.print htmlfooter
end
