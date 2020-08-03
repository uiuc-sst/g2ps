#!/usr/bin/ruby
# Create an inventory CSV for each language specifying distinctive features.
# INPUT #1: segments2.csv, distinctive features of all segments used on phoible.
# INPUT #2: <language>/Values.csv for each language, listing its segments
# OUTPUT: <language>/<language>_segments.csv, giving distinctive features of segments
#
# Mark Hasegawa-Johnson
# Written Nov 16, 2015 based on segments2languages.rb
#
require 'CSV'

# Read the segments.csv files
segments = {}
seg_head = []
Dir.glob('_config/segments*.csv').each do |input1|
  csv = CSV.read(input1,'r:UTF-8',{:col_sep => "\t",:quote_char => '"'})
  puts "Reading file #{input1}"
  seg_head = csv.shift[1..-1];
  csv.each do |row|
    ipa = row.shift
    if ipa then
      s = ipa.to_sym
      segments[s] =
        seg_head.map.with_index{|f,n| [f.to_sym, row[n]]}.select{|p| p[1]}.to_h
    else
      puts "Row first element is nil: #{s}\t#{row}\n"
    end
  end
  seg_head=seg_head[3..-1] # get rid of FID, combined class, segment class
end

# Read newsegments.csv
csv = CSV.read('_config/newsegments.csv','r:UTF-8')
p csv
csv = csv.transpose;
hed = csv.shift[1..-1];
newseg = csv.map{|row|
  [row.shift.to_sym,
   hed.map.with_index{|f,n| [f.to_sym,row[n]]}.select{|p| p[1]}.to_h]}.to_h
p newseg
newseg.each{|k,v| segments[k]=v};
  
# Compute primary articulator of each segment based on its symbol
ordered_places = CSV.read('_config/placeofarticulation.txt','r:UTF-8',{:col_sep => " "})
segments.each do |segment,features|
  features[:Place]=false
  p = ordered_places.find{|b| segment.to_s.include?(b[0])}
  if p then
    features[:Place] = p[1]
  else
    p "HELP! Segment #{segment} undefined primary articulator"
    exit
  end
end
seg_head.unshift("Place")

# Read universal feature sets: consonants, vowels, and diphthongs
ccsv = CSV.read('_config/consonants.txt','r:UTF-8');
ched = ccsv.shift[1..-1];
vcsv = CSV.read('_config/vowels.txt','r:UTF-8');
vhed = vcsv.shift[1..-1];
dcsv = CSV.read('_config/diphthongs.txt','r:UTF-8',{:col_sep => "\t"});
dhed = dcsv.shift[1..-1];
universals = 
  ( ccsv.map{|row|
      [ row.shift.to_sym,
        ched.map.with_index{|f,n| [f.to_sym, row[n]]}.select{|p| p[1]}.to_h ]}+
    vcsv.map{|row|
      [ row.shift.to_sym,
        vhed.map.with_index{|f,n| [f.to_sym, row[n]]}.select{|p| p[1]}.to_h ]}
  ).to_h
diphthongs = dcsv.map{|row|
  [ row.shift.to_sym,
    dhed.map.with_index{|f,n| [f.to_sym, row[n]]}.select{|p| p[1]}.to_h ]
}.to_h

# Find universal symbol for each segment
segments.each do |segment,features|
  features[:IPA_Core] = 'UNK'
  universals.each do |u,v|
    if v.keys.all?{|f| features.has_key?(f) && features[f].include?(v[f])} then
      features[:IPA_Core] = u.to_s
    end
  end # Check for a regular vowel or consonant symbol first
  diphthongs.each do |u,v|
    if v.keys.all?{|f| features.has_key?(f) && features[f].include?(v[f])} then
      features[:IPA_Core] = u.to_s
    end
  end # If a matching dipthong is found, that takes precedence
end
seg_head.unshift("IPA_Core")

########################################################
# Process languages
# For each language, determine its inventory
#   1. non-syllabic segments are copied over
#   2. syllabic segments get their tones appended as features
#
gpi = {}   # global phone inventory
gpitones = {} # global tone set
l2p = {}   # language-to-phones dictionary
# INPUT #2: <language>/Values.csv
Dir.glob('*/Values.csv').each do |fname|
  language = fname.gsub(/\/.*/,'');
  p "Cataloguing segments in #{language}"

  # BFA: values is in eighth column
  values=CSV.read(fname,'r:UTF-8').collect{|row| row[7].gsub(/ .*/,'').to_sym};
  values.shift;

  tones = []
  syllabics = []
  inventory = {}
  values.each_with_index do |segment,rindex|
    unless segments.has_key?(segment)
      p "HELP! #{rindex}th Segment #{segment} not available in segments.csv"
      exit;
    end
    # Separately collect tones, syllabics, and non-syllabics
    if segments[segment][:tone]=='+' then
      tones << segment.to_s
      gpitones[segment] = segment.to_s
    else
      inventory[segment] = segments[segment]
      gpi[segment] = segments[segment]
    end
    if segments[segment][:syllabic] == '+' then
      syllabics << segment
    end
  end

  # Create tone-annotated syllabic segments
  syllabics.each do |segment|
    tones.each do |tone|
      tonedseg = (segment.to_s + tone).to_sym
      segfeats = segments[segment].keys.collect{|f| [f,segments[segment][f]]}.to_h   # deep copy
      segfeats[:tone]='+'  # delete the "tone" feature
      segfeats[tone.to_sym] = '+'  # Add this tone as a 'feature'
      inventory[tonedseg] = segfeats  # Add the toned syllabic to language..
      gpi[tonedseg] = segfeats   # and to universal set
    end
  end
      
  # Print <language>/<language>_segments.csv
  CSV.open("#{language}/#{language}_segments.csv",'w:UTF-8',{:col_sep => "\t",:quote_char => '"'}) do |csv|
    csv << (row = (['IPA']+seg_head+tones));
    inventory.keys.sort.each do |segment|
      csv << (row = ([segment.to_s]+(seg_head+tones).map{|f| inventory[segment][f.to_sym]}))
    end
  end

  # Add to language-to-phones map
  l2p[language] = inventory.keys;

  # Print <language>/<language>_segments.html
  File.open("#{language}/#{language}_segments.html","w:UTF-8") do |html|
    html.print "<html><head><meta charset=\"UTF-8\"></head><body bgcolor=\"#ffffff\">\n"
    html.print "<h1>#{language} Segment Inventory</h1>\n"
    html.print "<p>Table created automatically on #{Date.today} "
    html.print "by Mark Hasegawa-Johnson based on a phone inventory from "
    html.print "<a href=\"http://phoible.org/\">phoible</a>.  You can also "
    html.print "download the <a href=\"#{language}_segments.csv\">CSV</a>.</p>\n"
    html.print "<table border=1>\n"
    row = ['IPA']+seg_head+tones;
    html.print "<tr><th>",row.join('</th><th>'),"</th></tr>\n"
    inventory.keys.sort.each do |segment|
      html.print "<tr>\n<td>#{segment}"
      html.print "(<a href=\"http://phoible.org/parameters/#{inventory[segment][:FID]}\">phoible</a>)</td>\n"
      row = (seg_head+tones).map{|f| inventory[segment][f.to_sym]}
      html.print '<td>',row.join('</td><td>'),"</td>\n"
      html.print '</tr>',"\n"
    end
    html.print "</table>\n</body>\n</html>\n"
  end
end

###################################################################
# Create a sorted universal phone inventory, and output a single spreadsheet

# Read the features in a useful sort order; create f2n and v2n maps
features = File.readlines("_config/features.txt").collect{|x| x.chomp.to_sym} +
           gpitones.keys

# Sort the gpi in order of features and vals
gpikeys = gpi.keys.sort{|a,b|
  (feat = features.find{|f| gpi[a][f] != gpi[b][f]} and gpi[a][feat] <=> gpi[b][feat]) or 0
}
p2n = gpikeys.map.with_index{|s,n| [s,n]}.to_h  #phone-to-index mapping

# Create the global phone inventory
#html = File.open("universal/universal_segments.html","w:UTF-8");
#html.print "<html><head><meta charset=\"UTF-8\"></head><body bgcolor=\"#ffffff\">\n"
#html.print "<h1>Universal Segment Inventory</h1>\n"
#html.print "<p>Table created automatically on #{Date.today} "
#html.print "by Mark Hasegawa-Johnson based on a phone inventory from "
#html.print "<a href=\"http://phoible.org/\">phoible</a>.  You can also "
#html.print "download the <a href=\"universal_segments.csv\">CSV</a>.</p>\n"
#html.print "<table border=1>\n"
#CSV.open("universal/universal_segments.csv",'w:UTF-8',{:col_sep => "\t",:quote_char => '"'}) do |csv|
  # First, output IPA symbols, IPA core, and primary articulators
#  csv << (row = (['IPA'] + gpikeys.collect{|segment| segment.to_s}))
#  html.print "<tr><td>",row.join('</td><td>'),"</td></tr>\n"
#  csv << (row = (['IPA Core'] + gpikeys.collect{|segment| gpi[segment][:IPA_Core]}))
#  html.print "<tr><td>",row.join('</td><td>'),"</td></tr>\n"
#  csv << (row = (['Place'] + gpikeys.collect{|segment| gpi[segment][:Place]}))
#  html.print "<tr><td>",row.join('</td><td>'),"</td></tr>\n"
  
  # Second, output one line for each distinctive feature
#  html.print "<tr><td>Features</td></tr>"
#  features.each do |feature|
#    csv << (row = ([feature.to_s] + gpikeys.collect{|segment| gpi[segment][feature]}))
#    html.print "<tr><th>",row.join('</th><th>'),"</th></tr>\n"
#  end

  # Third, output one line for each language
#  html.print "<tr><td>Languages</td></tr>"
#  l2p.keys.sort.each do |language|
#    row = [language]
#    l2p[language].each do |segment|
#      unless p2n.has_key?(segment) then
#        p "HELP! #{language} segment #{segment} not in the p2n key"
#        exit;
#      end
#      if row[p2n[segment]+1] then
#        row[p2n[segment]+1] = row[p2n[segment]+1] + "," + segment;
#      else
#        row[p2n[segment]+1] = segment;
#      end
#    end
#    csv << row;
#    html.print "<tr><td>",row.join('</td><td>'),"</td></tr>\n"
#  end
#end
#html.print "</table>\n</body>\n</html>\n"
#html.close


    

