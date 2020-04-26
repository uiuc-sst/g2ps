#!/usr/bin/ruby
# Download descriptions of each IPA segment from phoible.org
# INPUT: parameters.csv from phoible, to tell us the filename for each
# OUTPUT: segments/*.html for each filename
#
# Mark Hasegawa-Johnson
# Written March 9, 2015
#
require 'CSV'
require 'net/http'

# Read the input file
INFILE = 'parameters.csv';
segments = CSV.read(INFILE);
seg_head = segments.shift;

# For each entry, get its file from the web
OUTDIR = 'segments';
unless Dir.exist?(OUTDIR)
  Dir.mkdir(OUTDIR);
end
Net::HTTP.start("phoible.org") do |http|
  segments.each { |row|
    basefile = row[4];
    p "Trying to download http://phoible.org/parameters/#{basefile}/"
    resp = http.get("/parameters/"+basefile)
    open(OUTDIR+'/'+basefile+'.html','w') { |f|
      f.write(resp.body)
    }
  }
end



    
