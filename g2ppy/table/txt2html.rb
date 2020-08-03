#!/usr/bin/ruby
require 'Date'
require 'net/http'
# Mark Hasegawa-Johnson
# Written March 11, 2015
# last revised 3/11/2016
USAGE='USAGE: txt2html.rb <languages.txt> <index.html>
 Convert languages.txt to index.html, an index of available files
 INPUT: languages.txt, each non-comment lists a language
 OUTPUT: index.html, listing all languages _and_ islex.shtml'
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
  iso = fields[1].split(/,/)
  iso6393[fields[0]] = iso[0]
  if fields.size > 2 then
    wiki = fields[2].split(/,/)
    wikipedia[fields[0]] = wiki[0]
  else
    wikipedia[fields[0]] = "#{fields[0]}_language"
  end
  segments[fields[0]] = "#{fields[0]}/#{fields[0]}_segments.html"
end

# Add English
wikipedia['English']='English_language'
iso6393['English']='eng'
segments['English']='islex.shtml'

# Check the wikipedia links
Net::HTTP.start("en.wikipedia.org") do |http|
  wikipedia.each_key do |language|
    path = "/wiki/#{wikipedia[language]}"
    p "Checking for http://en.wikipedia.org/#{path}"
    if http.request_head(path).code == "200"
      wikipedia[language]="<a href=\"http://en.wikipedia.org#{path}\">#{path}</a>"
      p " *** found ***"
    end
  end
end
# Check the phoible.org links
Net::HTTP.start("phoible.org") do |http|
  iso6393.each_key do |language|
    path = "/languages/#{iso6393[language]}"
    p "Checking for http://phoible.org/#{path}"
    if http.request_head(path).code == "200"
      iso6393[language] = "<a href=\"http://phoible.org#{path}\">#{path}</a>"
      p " *** found *** "
    end
  end
end
# Check the segments.html file
segments.each_key do |language|
  if File.exist?(segments[language])
    segments[language]="<a href=\"#{segments[language]}\">#{segments[language]}</a>"
  end
end

# Write index.html
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

