########################################
# 2. Re-order the fields to desired order

# Create list of html fields: known fields in known order, then add what's left
htmlhead=['Language Name','ISO 639-1','ISO 639-3','Segments','Segments Source','Orthography','Orthography Source','Dictionary','Dictionary Source','Swadesh','Swadesh Source','SBS','SBS Source','Wikitexts','Wikitexts Source']

csvhead2i = csvhead.map.with_index{|x,n| [x,n]}.to_h
htmlhead2i = htmlhead.map.with_index{|x,n| [x,n]}.to_h
csvi2htmli = {}
csvhead2i.each do |x,n|
  if htmlhead2i.has_key?(x) then
    # Create mapping from CSV index to HTML index of this field name
    csvi2htmli[n] = htmlhead2i[x]
  else
    # Append this field name to the HTML header, and store its index
    htmlhead2i[x] = htmlhead.size
    csvi2htmli[n] = htmlhead.size
    htmlhead << x 
  end
end

##############

  # Header row
  f.print '<tr>'
  csvhead.each_with_index do |fieldname,n|
    if fieldname.match(/Source/) then
      f.print ' (Source) </th>'
    else
      f.print "<th> #{fieldname} "
      unless ((n == htmlhead.size-1) || htmlhead[n+1].match(/Source/))
        f.print '</th>'
      end
    end
  end
  f.print "</tr>\n"
  
  # Every other row
  csvdat.each_with_index do |row,m|
    f.print '<tr>'
    htmlhead.each_with_index do |fieldname,n|
      fieldval = row[htmli2csvi[n]]
      if fieldname.match(/Source/) then
        f.print " (#{fieldval}) </td>"
      else
        f.print "<td> #{fieldval} "
        unless ((n == htmlfields.size-1) || htmlfields[n+1].match(/Source/))
          f.print '</td>'
        end
      end
    end
    f.print "</tr>\n"
  end
  f.print "</table>\n</body>\n</html>\n"
end
