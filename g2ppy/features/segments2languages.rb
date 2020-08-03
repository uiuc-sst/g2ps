#!/usr/bin/ruby
# Create an inventory CSV for each language specifying distinctive features.
# INPUT #1: segments.csv, distinctive features of all segments used on phoible.
# INPUT #2: <language>/Values.csv for each language, listing its segments
# OUTPUT: <language>/segments.csv, giving distinctive features of segments
#
# Mark Hasegawa-Johnson
# Written March 11, 2015
#
require 'CSV'

# Read the segments.csv file
INPUT1 = 'segments.csv';
segments = CSV.read(INPUT1,'r:UTF-8',{:col_sep => "\t",:quote_char => '"'})
seg_head = segments.shift;

# Read the placeofarticulation.txt definitions.  Order matters, hence array
ordered_places = []
f = File.new("placeofarticulation.txt",'r:UTF-8');
f.each {|line| ordered_places.push(line.chomp.chomp.split) }
f.close

# Read universal feature sets: consonants and vowels
consonants = CSV.read('consonants.txt','r:UTF-8');
con_head = consonants.shift;
vowels = CSV.read('vowels.txt','r:UTF-8',{:col_sep => "\t"});
vow_head = vowels.shift;

# Find the indices into seg_head of each distinctive feature
unless iseg_str = seg_head.find_index{|f| f == 'stress'} then
  p "No stress!"
  exit
end
iseg_con = con_head[2..-1].collect do |f|
  n=seg_head.find_index{|b| b==f}
  unless n then
    p "HELP! consonants.txt feature #{f} not found"
    exit
  end
  n
end
iseg_vow = vow_head[2..-1].collect do |f|
  n=seg_head.find_index{|b| b==f}
  unless n then
    p "HELP! vowels.txt feature #{f} not found"
    exit
  end
  n
end

# Global hash from segment ID to its distinctive feature vector
vectors = {}
poa = {}
universal = {}
segments.each do |row|
  segment=row[0]  # BFA: IPA label in first column
  vectors[segment] = row

  # Try to find its primary articulator from its symbol
  poa[segment]=false
  p = ordered_places.find{|b| segment.include?(b[0])}
  if p then
    poa[segment] = p[1]
  else
    p "HELP! Segment #{segment} undefined primary articulator"
    exit
  end

  # Try to find its universal phone from feature vector
  universal[segment]=false
  if vectors[segment][iseg_str].include?('+') then
    # Last-best order: keep whichever is the last to match.  
    vowels.each do |df|
      if [0..(iseg_vow.length-1)].all? do |n|
           df[n+2] == nil ||
             vectors[segment][iseg_vow[n]].include?(df[n+2])
         end then
        universal[segment] = df[0];
      end
    end
  elsif poa[segment] != 'F0' then
    consonants.each do |df|
      if poa[segment] == df[1] then
        if (0..(iseg_con.length-1)).all? do |n|
             df[n+2] == nil ||
               vectors[segment][iseg_con[n]].include?(df[n+2])
           end then
          universal[segment] = df[0]
        end
      end
    end
  end
  unless universal[segment] then
    p "HELP! Universal not found for segment #{segment}"
    exit
  end
end

# global-phone-inventory and languages-to-phones map
gpi = {}
l2p = {}

# INPUT #2: <language>/Values.csv
Dir.glob('*/Values.csv').each do |fname|
  language = fname.gsub(/\/.*/,'');
  p "Cataloguing segments in #{language}"

  values = CSV.read(fname,'r:UTF-8');
  values_head = values.shift;

  inventory = {}
  values.each_with_index do |row,rindex|
    # BFA: values is in eighth column
    ldep_segment = row[7]
    segment = ldep_segment.gsub(/ .*/,''); # eliminate all past first space
    unless vectors.has_key?(segment)
      p "HELP! #{rindex}th Segment #{segment} not available in segments.csv"
      exit;
    end
    inventory[segment] = vectors[segment]
  end
  
  # Print <language>/<language>_segments.csv
  CSV.open("#{language}/#{language}_segments.csv",'w:UTF-8',{:col_sep => "\t",:quote_char => '"'}) do |csv|
    csv << seg_head;
    inventory.keys.sort.each do |segment|
      csv << inventory[segment]
      # Add to global phone inventory if not already there
      gpi[segment] = segment;
    end
  end

  # Add to language-to-phones map
  l2p[language] = inventory.keys;

  # Print <language>/<language>_segments.html
  File.open("#{language}/#{language}_segments.html","w") do |f|
    f.print "<html><body bgcolor=\"#ffffff\">\n"
    f.print "<h1>#{language} Segment Inventory</h1>\n"
    f.print "<p>Table created automatically on #{Date.today} "
    f.print "by Mark Hasegawa-Johnson based on a phone inventory from "
    f.print "<a href=\"http://phoible.org/\">phoible</a>.  You can also "
    f.print "download the <a href=\"#{language}_segments.csv\">CSV</a>.</p>\n"
    f.print "<table border=1>\n"
    f.print "<tr>\n<th>",seg_head.join('</th><th>'),"</th></tr>\n"
    inventory.keys.sort.each do |segment|
      f.print "<tr>\n<td>#{inventory[segment][0]}</td>\n"
      f.print "<td><a href=\"http://phoible.org/parameters/#{inventory[segment][1]}\">phoible</a></td>\n"
      f.print '<td>',inventory[segment][2..-1].join('</td><td>'),'</td>',"\n"
      f.print '</tr>',"\n"
    end
    f.print "</table>\n</body>\n</html>\n"
  end
end

###################################################################
# Create a sorted universal phone inventory, and output a single spreadsheet

# Read the features in a useful sort order; create f2n and v2n maps
features = File.readlines("features.txt").collect{|x| x.chomp};
f2n = {};
features.each_with_index {|f,n| f2n[f]=n; }
v2n = {'-'=>'0','-,-,+'=>'1','-,+,-'=>'2','-,+'=>'3','-,+,+'=>'4',' '=>'5','+,-,-'=>'6','+,-'=>'7','+,-,+'=>'8','+,+,-'=>'9','+'=>'A'};
n2v = v2n.invert;

# Create a codeword for each segment, then sort the codewords
c2p = {}
gpi.keys.each do |segment|
  codeword = "2"*seg_head.length;
  seg_head.each_with_index do |f,i|
    if f2n.has_key?(f) then
      v = (vectors[segment][i]) ? vectors[segment][i] : ' ';
      unless v2n.has_key?(v)
        p "HELP! Segment #{segment} feature #{f} value /#{v}/ unknown"
        exit;
      end
      codeword[f2n[f]]=v2n[v];
    end
  end
  unless c2p.has_key?(codeword) then
    c2p[codeword] = []
  end
  c2p[codeword] << segment;
end

# Create the global mapping from phones to indices
codewords = c2p.keys.sort;
p2n = {}
c2n = {}
codewords.each_with_index do |c,n|
  c2p[c].each {|p| p2n[p] = n; }
  c2n[c] = n;
end

# Create a sorted universalsymbols.txt file
File.open("universalsymbols.txt","w:UTF-8") do |f|
  codewords.each do |c|
    f.print c2p[c].join(","),","
  end
end
    
# Create the global phone inventory
CSV.open("global_phone_inventory.csv",'w:UTF-8',{:col_sep => "\t",:quote_char => '"'}) do |csv|
  # First, output one line for each distinctive feature
  features.each_with_index do |feature,featdex|
    row = [feature]
    codewords.each do |c|
      row[c2n[c]+1] = n2v[c[featdex]]
    end
    csv << row;
  end

  # Second, output the universal set, and primary articulators
  row = ['Primary Articulator']
  codewords.each do |c|
    unless poa.has_key?(c2p[c][0])
      p "Segment #{c2p[c][0]} undefined primary articulator"
      exit
    end
    row[c2n[c]+1] = poa[c2p[c][0]][0]
  end
  csv << row
  row = ['Universal']
  codewords.each do |c|
    unless universal.has_key?(c2p[c][0])
      p "Segment #{c2p[c][0]} undefined universal symbol"
      exit
    end
    row[c2n[c]+1] = universal[c2p[c][0]][0]
  end
  csv << row
  row = ['Specific']
  codewords.each do |c|
    row[c2n[c]+1] = c2p[c].join(",")
  end
  csv << row
  
  # Third, output one line for each language
  l2p.keys.sort.each do |language|
    row = [language]
    l2p[language].each do |segment|
      unless p2n.has_key?(segment) then
        p "HELP! #{language} segment #{segment} not in the p2n key"
        exit;
      end
      if row[p2n[segment]+1] then
        row[p2n[segment]+1] = row[p2n[segment]+1] + "," + segment;
      else
        row[p2n[segment]+1] = segment;
      end
    end
    csv << row;
  end
end

    

