#!/usr/bin/ruby
#require 'Date'
#require 'net/http'
# Mark Hasegawa-Johnson
# Written May 28, 2016
# based on txt2html.rb
USAGE='USAGE: txt2csv.rb <languages.txt> <languages.csv>
 Convert languages.txt to languages.csv, a more complete list of
 possible resources, suitable for more consistent later maintenance.
 INPUT: languages.txt, each non-comment lists a language
 OUTPUT: languages.csv, listing all files for all languages
if ARGV.size < 2 then
  puts USAGE;
  exit;
end
INPUT = ARGV[0];
OUTPUT = ARGV[1];

# Read languages.txt
iso6393 = {}
wikipedia = {}
segments = {}
text = File.open(INPUT).read
text.each_line do |line|
  line.chomp!
  next if line.match(/^\#/)
  next if line.match(/^$/)
  fields = line.chomp.split
  iso2 = fields[1]
  iso3 = fields[2].split(/,/)
  iso6391[fields[0]] = iso2
  iso6393[fields[0]] = iso3.join(',')
  vocab[fields[0]] = "vocab/#{iso2}"
  wikitexts[fields[0]] = "http://ifp-08.ifp.uiuc.edu/public/wikitexts/#{iso2}"
  wikipedia[fields[0]] = "http://#{iso2}.wikipedia.org/"
  phoible[fields[0]] = "http://phoible.org/languages/#{iso3[0]}"
  if fields.size > 2 then
    wiki = fields[2].split(/,/)
    wikiref[fields[0]]="http://en.wikipedia.org/wiki/#{wiki[0]}"
  else
    wikiref[fields[0]]="http://en.wikipedia.org/wiki/#{fields[0]}_language"
  end
  segments[fields[0]] = "#{fields[0]}/#{fields[0]}_segments.html"
end

# Add English
wikiref['English']="http://en.wikipedia.org/wiki/English_language"
wikipedia['English']="http://en.wikipedia.org/"
iso6393['English']='eng'
iso6391['English']='en'
segments['English']='islex.shtml'
phoible['English'] = "http://phoible.org/languages/eng"

# Write languages.csv
open(OUTPUT,'w') do |f|
  f.print "<html><body bgcolor=\"#ffffff\">\n"
  f.print "<h1>WS15 Dictionary Data</h1>\n"
  f.print "<p>Table created automatically on #{Date.today} "
  f.print "by Mark Hasegawa-Johnson.</p>"
  f.print "<p>If you are looking for the ISLEX English lexicon, try"
  f.print "<a href=\"islex.shtml\">HERE</a>.</p>"
  f.print "<table border=1>\n"
  f.print "<tr>\n"
  f.print "<th>Wikipedia page</th>\n"
  f.print "<th>Phoible page</th>\n"
  f.print "<th>WS15 Phone inventory w/features</th>\n"
  f.print "</tr>\n"
  iso6393.keys.sort.each do |language|
    f.print "<tr>\n"
    f.print "<td>#{wikipedia[language]}</td>\n"
    f.print "<td>#{iso6393[language]}</td>\n"
    f.print "<td>#{segments[language]}</td>\n"
    f.print "</tr>\n"
  end
  f.print "</table>\n</body>\n</html>\n"
end

