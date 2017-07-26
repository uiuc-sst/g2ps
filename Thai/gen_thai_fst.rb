#!/usr/bin/ruby
# coding: utf-8

USAGE="gen_thai_fst.rb > out.fst.txt\
  Generate a reference orthography FST for Thai.\
  I write code for this because Thai orthography is \
  too complicated to keep in my head."

# vowel IPA chart
vipa = {''=>'o','ะ'=>'a','ั'=>'a','ิ'=>'i','ิ'=>'i','ึ'=>'ɯ','ึ'=>'ɯ',
        'ุ'=>'u','ุ'=>'u','เะ'=>'e','เ็'=>'e','แะ'=>'ɛ','แ็'=>'ɛ',
        'โะ'=>'o','เาะ'=>'ɔ','็อ'=>'ɔ',
        'า'=>'aː','ี'=>'iː','ือ'=>'ɯː','ื'=>'ɯː',
        'ู'=>'uː','เ'=>'eː','แ'=>'ɛː','โ'=>'oː','อ'=>'ɔː','็'=>'ɔː',
        'เอ'=>'ɤː','เิ'=>'ɤː','เอ'=>'ɤː','เอะ'=>'ɤʔ','เียะ'=>'iaʔ','เือะ'=>'ɯaʔ',
        'ัวะ'=>'uaʔ','ิว'=>'iu','เ็ว'=>'eu','เีย'=>'ia','เือ'=>'ɯa',
        'ัว'=>'ua','ว'=>'ua','เว'=>'eːu','แว'=>'ɛːu','าว'=>'aːu',
        'เียว'=>'iau','ัย'=>'ai','ใ'=>'ai','ไ'=>'ai','ไย'=>'ai','าย'=>'aːi',
        '็อย'=>'ɔi','อย'=>'ɔːi','โย'=>'oːi','ุย'=>'ui','เย'=>'ɤːi','วย'=>'uai',
        'เือย'=>'ɯai','ำ'=>'am','ฤ'=>'rɯ','ฦ'=>'lɯ','ฤๅ'=>'rɯː','ฦๅ'=>'lɯː'};

# consonant class
cclass={'ก'=>2,'ข'=>3,'ฃ'=>3,'ค'=>1,'ฅ'=>1,'ฆ'=>1,'ง'=>1,
        'จ'=>2,'ฉ'=>3,'ช'=>1,'ซ'=>1,'ฌ'=>1,'ญ'=>1,
        'ฎ'=>2,'ฏ'=>2,'ฐ'=>3,'ฑ'=>1,'ฒ'=>1,'ณ'=>1,
        'ด'=>2,'ต'=>2,'ถ'=>3,'ท'=>1,'ธ'=>1,'น'=>1,
        'บ'=>2,'ป'=>2,'ผ'=>3,'ฝ'=>3,
        'พ'=>1,'ฟ'=>1,'ภ'=>1,'ม'=>1,
        'ย'=>1,'ร'=>1,'ล'=>1,'ว'=>1,
        'ศ'=>3,'ษ'=>3,'ส'=>3,'ห'=>3,'ฬ'=>1,
        'อ'=>2,'ฮ'=>1};

# IPA of onset consonant
ocipa = {'ก'=>'k','ข'=>'kʰ','ฃ'=>'kʰ','ค'=>'kʰ','ฅ'=>'kʰ','ฆ'=>'kʰ','ง'=>'ŋ',
        'จ'=>'tɕ','ฉ'=>'tɕʰ','ช'=>'tɕʰ','ซ'=>'s','ฌ'=>'tɕʰ','ญ'=>'j',
        'ฎ'=>'d','ฏ'=>'t','ฐ'=>'tʰ','ฑ'=>'tʰ','ฒ'=>'tʰ','ณ'=>'n',
        'ด'=>'d','ต'=>'t','ถ'=>'tʰ','ท'=>'tʰ','ธ'=>'tʰ','น'=>'n',
        'บ'=>'b','ป'=>'p','ผ'=>'pʰ','ฝ'=>'f',
        'พ'=>'pʰ','ฟ'=>'f','ภ'=>'pʰ','ม'=>'m',
        'ย'=>'j','ร'=>'r','ล'=>'l','ว'=>'w',
        'ศ'=>'s','ษ'=>'s','ส'=>'s','ห'=>'h','ฬ'=>'l',
        'อ'=>'ʔ','ฮ'=>'h'};

# IPA of coda consonant
ccipa = {'ก'=>'k','ข'=>'k','ฃ'=>'k','ค'=>'k','ฅ'=>'k','ฆ'=>'k','ง'=>'ŋ',
        'จ'=>'t','ฉ'=>'eps','ช'=>'t','ซ'=>'t','ฌ'=>'eps','ญ'=>'n',
        'ฎ'=>'t','ฏ'=>'t','ฐ'=>'t','ฑ'=>'t','ฒ'=>'t','ณ'=>'n',
        'ด'=>'t','ต'=>'t','ถ'=>'t','ท'=>'t','ธ'=>'t','น'=>'n',
        'บ'=>'p','ป'=>'p','ผ'=>'eps','ฝ'=>'eps',
        'พ'=>'p','ฟ'=>'p','ภ'=>'p','ม'=>'m',
        'ย'=>'eps','ร'=>'n','ล'=>'n','ว'=>'eps',
        'ศ'=>'t','ษ'=>'t','ส'=>'t','ห'=>'eps','ฬ'=>'n',
        'อ'=>'eps','ฮ'=>'eps',
        'eps'=>'eps'};
# manner class of consonant: 0=none, 1=sonorant, 2=plosive
manner = {'k'=>2,'ŋ'=>1,'t'=>2,'n'=>1,'p'=>2,'m'=>1,'eps'=>0}

# vowel diacritics
vds = ['','ั','ิ','ึ','ุ','ี','ื','ู','็'];
# tone diacritics
tds = ['','่','้','๊','๋'];
# firstvowels
fvs=['','เ','แ','โ','ใ','ไ'];
# main vowel symbols
mvs =['','า','อ','ย','ว','ฤ','ฦ'];

# vowel terminating symbols
vts = ['','ะ','ๅ','ว','ย'];

# tones
tonemarked = [[],['˦˨','˩˩','˩˩'],['˥˥','˦˨','˦˨'],['','˥˥',''],['','˩˦','']]
tonedeadlong = ['˦˨','˩˩','˩˩']
tonelive = ['˧˧','˧˧','˩˦']
tonedeadshort = ['˥˥','˩˩','˩˩']

# transitions from 0 to an initial vowel
1.upto(fvs.length) do |fvi|
  puts "0000000 #{fvi}000000 #{fvs[fvi]} eps"
end

# first vowel index = first state index
0.upto(fvs.length-1) do |fvi|
  # onset consonant index = second state index
  0.upto(3) do |oci|
    # for each onset consonant including 0, do all onset consonants
    cclass.each do |con,cla|
      state0 = sprintf("%d%d0000",fvi,oci);
      state1 = sprintf("%d%d0000",fvi,cla);
      puts "#{state0} #{state1} #{con} #{ocipa[con]}"
    end
    # if we've seen an onset consonant, then diacritics are possible
    if oci > 0 then
      # vowel diacritic index = third state index
      0.upto(vds.length-1) do |vdi|
        # tone diacritic index = fourth state index
        0.upto(tds.length-1) do |tdi|
          # vowel diacritic edges
          1.upto(vds.length-1) do |vde|
            state0 = sprintf("%d%d%d%d00",fvi,oci,vdi,tdi);
            state1 = sprintf("%d%d%d%d00",fvi,oci,vde,tdi);
            puts "#{state0} #{state1}  #{vds[vde]} eps"
          end
          # tone diacritic edges
          1.upto(tds.length-1) do |tde|
            state0 = sprintf("%d%d%d%d00",fvi,oci,vdi,tdi);
            state1 = sprintf("%d%d%d%d00",fvi,oci,vdi,tde);
            puts "#{state0} #{state1}  #{tds[tde]} eps"
          end
          # main vowel symbol
          1.upto(mvs.length-1) do |mvi|
            state0 = sprintf("%d%d%d%d00",fvi,oci,vdi,tdi);
            state1 = sprintf("%d%d%d%d%d0",fvi,oci,vdi,tdi,mvi);
            puts "#{state0} #{state1} #{mvs[mvi]} eps"
          end
          0.upto(mvs.length-1) do |mvi|
            # Completed vowel
            0.upto(vts.length-1) do |vti|
              state0 = sprintf("%d%d%d%d%d0",fvi,oci,vdi,tdi,mvi);
              state1 = sprintf("%d%d%d%d%d%d",fvi,oci,vdi,tdi,mvi,vti);
              vkey="#{fvs[fvi]}#{vds[vdi]}#{mvs[mvi]}#{vts[vti]}"
              if vipa.has_key?(vkey) then
                v = vipa[vkey]
                
                # coda consonant
                ccipa.each do |grapheme,phoneme|
                  vowdur = (v.match(/ː/) ? 1 : 0)
                  if tdi > 0 then  # tone index specified
                    tone = tonemarked[tdi][oci]
                  elsif ((manner[phoneme]==2) && (v.match(/ː/))) then
                    tone = tonedeadlong[oci]
                  elsif ((manner[phoneme]==1) || (v.match(/ː/))) then
                    tone = tonelive[oci]
                  else
                    tone = tonedeadshort[oci]
                  end
                  vt = (vts[vti] == '') ? 'eps' : vts[vti];
                  # open syllable inherent vowel is a, not o
                  if (vkey=='' && grapheme=='eps') then 
                    puts "#{state0} #{state1} #{vt} a#{tone}"
                  else
                    puts "#{state0} #{state1} #{vt} #{v}#{tone}"
                  end
                  puts "#{state1} 0000000 #{grapheme} #{phoneme}"
                end # ccipa each
              end # if vipa.has_key
            end # vowel termination index
          end # main vowel index
        end # tone diacritic index
      end # vowel diacritic index
    end # if oci > 1
  end # onset consonant index
end # first vowel index


