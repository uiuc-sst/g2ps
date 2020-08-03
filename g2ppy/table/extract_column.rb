#!/usr/bin/ruby
# extract_column: extract specified column from the first HTML table in a file
require 'Nokogiri'

if ARGV.size < 2 then
   puts "USAGE: extract_column.rb filename columnumber"
  exit
end

fname = ARGV[0];              # filename
lname = fname.gsub(/_.*/,''); # language name
targetcol = ARGV[1].to_i;     # target column

open(fname) do |f|
  doc = Nokogiri::HTML(f)

  # Get the column, and print it to stdout
  doc.xpath("//div//table//tr").each do |row|
    kids = row.xpath(".//td")
    if kids.size > targetcol then
      text=kids[targetcol].content.gsub(/\([^\)]+\)/,'').gsub(/\s+/,' ').split(/[\s;,\/]+/);
      text.each do |t|
        unless t == lname then
          unless t.match(/^$/) then
            puts t.sub(/^\s+/,'')+"\r\n";
          end
        end
      end
    end
  end
end

