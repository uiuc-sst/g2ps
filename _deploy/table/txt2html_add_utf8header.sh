#!/bin/sh
for f in `ls */*.txt */*/*.txt`; do
    g=`echo $f | sed 's/\.txt/\.html/'`;
    if [ ! -e $g -o $f -nt $g ]; then
	echo "Creating or updating ${g} from ${f}"
	echo '<html><head><meta http-equiv="Content-Type" content="text/html;charset=UTF-8"></head><body bgcolor="#ffffff"><pre>' > $g;
	chmod 644 $g;
	cat $f >> $g;
	echo '</pre></body></html>' >> $g;
    fi
done
