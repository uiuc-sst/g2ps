#!/usr/bin/ruby
# Compute a matrix of inter-phone distances (negative log confusion probabilities).
# INPUT: segments2.csv, distinctive features of all segments used on phoible.
# OUTPUT: confusion_costs.csv: cost for confusion between each pair
#
# Mark Hasegawa-Johnson
# Written Nov 19, 2017
#
require 'csv'
require 'json'

# Read the segments.csv files
segments = {}
seg_head = []
feats=['advanced tongue root','anterior','approximant','back','click','consonantal','constricted glottis','continuant','coronal','delayed release','distributed','dorsal','epilaryngeal source','fortis','front','high','labial','labiodental','lateral','long','low','lowered larynx implosive','nasal','periodic glottal source','raised larynx ejective','retracted tongue root','round','short','sonorant','spread glottis','stress','strident','syllabic','tap','tense','tone','trill']										
Dir.glob('../_config/segments2.txt').each do |input1|
  STDERR.puts('Reading file '+input1)
  csv = CSV.read(input1,'r:UTF-8',{:col_sep => "\t",:quote_char => '"'})
  seg_head = csv.shift;
  csv.each do |row|
    ipa = row.shift
    if ipa then
      s = ipa.to_sym
      row.shift # FID
      row.shift # phone class
      row.shift # manner class
      segments[s] = row  # all the rest of the feature values
    else
      puts "Row first element is nil: #{s}\t#{row}\n"
    end
  end
end

# Compute inter-segment distance matrix
distances = {}
STDERR.puts("Computing distances for #{segments.length} segments:")
nseg = 0
segments.each do |s1,feats1|
  STDERR.print("#{nseg}/#{segments.length} #{s1}...")
  nseg = nseg+1
  distances[s1] = {}
  segments.each do |s2,feats2|
    d = 0
    feats1.zip(feats2).each do |f1,f2|
      if f1 != f2 then
        d = d+1
      end
    end
    distances[s1][s2] = d
  end
end
STDERR.puts('')
STDERR.puts('Done computing distances, now generating confusion_costs.json')

# Print confusion_costs.txt
allsegs = segments.keys().sort()
File.open("confusion_costs.json",'w:UTF-8') do |f|
  f.puts JSON.generate(distances)
end

