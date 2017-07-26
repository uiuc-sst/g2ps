#!/usr/bin/ruby
# convert the languages.csv file to an index.html file with dictionaries

unless ARGV.size >= 2 then
  print "USAGE: csv2html_languages.rb ../_config/languages3.csv ../index.html\n"
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

# 3. Create the HTML file

htmlfilename = ARGV[1];

File.open(htmlfilename,"w:UTF-8") do |f|
  f.print "<HTML>\n<HEAD>\n";
  f.print '<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">',"\n"
  f.print "</HEAD>\n<BODY>\n"
  f.print '<html><body bgcolor="#ffffff">',"\n"
  f.print "<h1>Segment Inventories, Orthographies, Dictionaries and Text</h1>\n"
  f.print "<p>All text files are UTF-8.  If they fail to display, try opening a command window and typing `export LC_ALL=en_US.UTF-8`</p>\n"
  f.print "<table border=1>\n"

  # Header row
  f.print '<tr>'
  csvhead.each_with_index do |fieldname,n|
    unless fieldname.match(/\(/) then f.print '<th>'; end
    f.print ' ',fieldname
    unless fieldname.match(/\-\s*$/) then f.print '</th>'; end
  end
  f.print "</tr>\n"
  
  # Every other row
  csvdat.each_with_index do |row,m|
    f.print '<tr>'
    csvhead.each_with_index do |fieldname,n|
      fieldval = row[n]
      if fieldname.match(/\(/) then
        if fieldval && fieldval.size > 0 then
          targets = fieldval.split(/;/).map{|x| "<a href=\"#{x}\">#{fieldname.gsub(/[\(\)]/,'')}</a>"}
          f.print '(',targets.join(';'),')'
        end
        f.print "</td>"
      elsif fieldname.match(/-\s*$/) then
        f.print "<td>"
        if fieldval && fieldval.size > 0 then
          targets = fieldval.split(/;/).map{|x| "<a href=\"#{x}\">#{row[0]} #{fieldname.sub(/-/,'')}</a>"}
          f.print targets.join(';'), " - "
        end
      else
        f.print "<td>#{fieldval}</td>"
      end
    end
    f.print "</tr>\n"
  end
  f.print "</table>\n</body>\n</html>\n"
end
