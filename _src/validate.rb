#!/usr/bin/ruby
# Run lots of steps to validate the data; report the result
#
# Mark Hasegawa-Johnson
# 9/8/2016
#
require 'net/http'

unless ARGV.size >= 2 then
  print "USAGE: validate.rb ../_config/languages3.csv ../index.html\n"
  print "Converts a CSV table of language resources into an HTML table\n"
  exit
end

###########
# Structure:
# 1. Read the CSV, and strip the header

csvfilename = ARGV[0];

# Read the CSV
csvdat = []
f = File.open(csvfilename)
f.each do |row|
  a = [];
  row.chomp.chomp.split(/,/).each do |x|
    if x.is_a?(String) then
      a << x.encode(Encoding::UTF_8)
    else
      a << []
    end
  end
  csvdat << a
end

# First line is the header
csvhead = csvdat.shift;

# For each entry, get its file from the web
Net::HTTP.start("phoible.org") do |http|
  csvdat.each { |row|
    basefile = row[5];
    resp = http.get(basefile)
    if resp
      p "Successfully downloaded #{basefile}"
    else
      p "** Unable to download #{basefile}"
    end
  }
end



    
