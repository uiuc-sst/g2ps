#!/usr/bin/ruby
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
    <h1>LanguageNet Grapheme-to-Phoneme Tables</h1>
    <h2>Usage</h2>
      <p>
        The "Pronlexes" column, in the table below, is the main data being distributed
        by this site.  Other columns are used primarily for validation.
        This database is synchronized with its
        <a href="https://github.com/uiuc-sst/g2ps">GitHub repository.</a>
      </p>
    <h2>Acknowledgments</h2>
      <p>
        This project was funded from 2016-2019 as part of the 
        <a href="http://www.isle.illinois.edu/sst/research/darpa2015/index.html">LanguageNet</a>
        grant from the 
        <a href="https://www.darpa.mil/program/low-resource-languages-for-emergent-incidents">DARPA LORELEIM/a> program.
      </p>
    <table border=1>
      <tr>
        <th>Codes</th>
        <th>Names</th>
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
texts = {}

f = File.open(csvfilename)
arr_of_arrs = CSV.read(csvfilename)
csvhead = arr_of_arrs.shift()
targets = ['n','c','c','0','s','p','s','p','s','t','s','t','s','t','t']
arr_of_arrs.each do |arr|
  if arr[1].is_a?(String) then
    iso6393 = arr[1].encode(Encoding::UTF_8)
    names[iso6393] = [] unless names.key?(iso6393)
    codes[iso6393] = [] unless codes.key?(iso6393)
    sources[iso6393] = [] unless sources.key?(iso6393)
    texts[iso6393] = [] unless texts.key?(iso6393)
    pronlexes[iso6393] = [] unless pronlexes.key?(iso6393)
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
