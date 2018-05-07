  
      
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
    f.print htmlfooter
  end
