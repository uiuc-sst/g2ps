#!/usr/bin/ruby
# Parse each segment's HTML to extract its distinctive feature values.
# INPUT: segments/*.html, local copy of each phoible.org segment page
# OUTPUT: segments.csv, a table of (segments)X(features)
#
# Mark Hasegawa-Johnson
# Written March 10, 2015
#
require 'Nokogiri'
require 'CSV'

# Global hash to contain the feature table
segments = {}

# Parse the file to get distinctive features
INDIR = '_config/segments'
Dir.glob(INDIR+'/*.html').each do |fname|
  doc = ''
  open(fname){|f| doc = Nokogiri::HTML(f)}
  fid = fname.gsub(/segments\//,'').gsub(/\.html/,'');
  segments[fid] = {'FID'=>fid}
  
  # Get the segment name out of the title
  text = doc.at_xpath("//title").content
  segments[fid]["IPA"] = text.gsub(/\s+/,'').gsub(/PHOIBLEOnline-/,'').gsub(/.*Segment/,'')
  
  # Get the features
  doc.xpath("//div//table//tr").each do |feat|
    kids = feat.xpath(".//td")
    if kids.size >= 2 then
      segments[fid][kids[0].content] = kids[1].content;
    end
  end
end

# Get a comprehensive list of the features used
allfeats = {}
segments.each_value do |v|
  v.each_key do |k|
    allfeats[k] = ''
  end
end
header = allfeats.keys.sort
# Swap the IPA and combined-class
header[0],header[2] = header[2],header[0]

OUTFILE = 'segments.csv'
CSV.open(OUTFILE,'w:UTF-8',{:col_sep => "\t",:quote_char => '"'}) do |csv|
  csv << header

  segments.each do |k,v|
    row = []
    header.each{|kk| row << v[kk]}
    csv << row
  end
end


    
