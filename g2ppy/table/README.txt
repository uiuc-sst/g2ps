This directory contains code to generate and validate a table in which each row is a language, and 
each column is a different sort of data, e.g., G2Ps, dictionaries, texts, and wordlists.

csv2html_languages.rb: generate index.html from languages3.csv
check_urls.py: check that each URL in the table is still valid
txt2html_add_utf8header.sh: for each language, add HTML header and footer to its symbol table
validate_phoneset.py: check that the phones in each language match phoible
