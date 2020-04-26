#!/usr/bin/ruby
require 'FST'
require 'CSV'

if ARGIN.size < 2 then
  p "USAGE: validate.rb <languagename>"
  p "Check to make sure that files in <languagename> match standards"
  exit
end
lang = ARGIN[0]

# Read the input files
endings=[]
filename=[]
ifst=0; endings[ifst]='orthographic_fst.txt';
idict=1; endings[idict]='orthographic_dict.txt';
iswad=2; endings[iswad]='swadesh_list.txt';
ifeat=3; endings[ifeat]='segments.csv';
endings.each_index do |i|
  filename[i] = lang + '/' + lang + '_' + endings[i];
end

# Read the CSV if it exists
if File.exist?(filename[ifeat]) then
  f = CSV.read(filename[ifeat]);
  fsegs = {}
  f.each do |row|
    fsegs[row[0]] = true
  end
else
  STDERR.print "#{filename[ifeat]} does not exist"
  fsegs = false
end

# Start an array for the orthographic characters
ochars = {}

# Verify the FST if it exists:
unless File.exist?(filename[ifst]) then
  STDERR.print "#{filename[ifst]} does not exist"
else
  STDERR.print "Validating #{filename[ifst]}.........."
  #  (1) it should parse,
  unless fst = FST.read(filename[ifst]) then
    STDERR.print "#{filename[ifst]}: Unable to parse FST"
  else
    fst.arc.each_index do |i|
      #  (2) the string on each first arc should be just one char
      if fst.arc[i].istr.length > 1
        STDERR.print "#{filename[ifst]} arc #{i} istr <#{fst.arc[i].istr}> is more than one character"
      else
        # (otherwise, store the character)
        ochars[fst.arc[i].istr] = true
      end
      #  (3) the string on each output arc should be a phone in the fsegs
      if fsegs then
        unless fsegs.has_key?(fst.arc[i].ostr) then
          STDERR.print "#{filename[ifst] arc #{i} ostr <#{fst.arc[i].ostr}> is not in #{filename[ifeat]}"
        end
      end
    end
  end
end
STDERR.print "\n"

# Verify the dictionary if it exists:
unless File.exist?(filename[idict]) then
  STDERR.print "#{filename[idict]} does not exist"
else
  STDERR.print "Validating #{filename[idict]}.........."
  File.readlines(filename[idict]) do |line|
    next if line.match(/^$/)
    next if line.match(/^#/)
    phones = line.chomp.split
    word = phones.shift!
    # (1) Every phone should be a phone of the language
    if fsegs then 
      phones.each do |phone|
        unless fsegs.has_key?(phone) then
          STDERR.print "#{filename[idict]} phone /#{phone}/ is not in #{filename[ifeat]}"
        end
      end
    end
    # Store all characters in the word as orthography of the language
    chars = word.split(//)
    chars.each{|x| ochars[x] = true }
  end
end
STDERR.print "\n"

# Verify the Swadesh list if it exists:
unless File.exist?(filename[iswad]) then
  STDERR.print "#{filename[iswad]} does not exist"
else
  STDERR.print "Validating #{filename[iswad]}.........."
  File.readlines(filename[iswad]) do |line|
    next if line.match(/^$/)
    next if line.match(/^#/)
    word = line.chomp.split.shift
    # (1) Every character in every Swadesh word must exist in the FST or dictionary
    chars = word.split(//)
    chars.each do |x|
      unless ochars.has_key?(x) then
        STDERR.print "#{filename[iswad]} word #{word} char <#{x}> not in #{filename[ifst]} or #{filename[idict]}"
      end
    end
  end
end

    
    
  
