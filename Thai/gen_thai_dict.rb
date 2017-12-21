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
        'อ'=>2,'ฮ'=>1,'ไ'=>1}

# IPA of onset consonant
ocipa = {'ก'=>'k','ข'=>'kʰ','ฃ'=>'kʰ','ค'=>'kʰ','ฅ'=>'kʰ','ฆ'=>'kʰ','ง'=>'ŋ',
        'จ'=>'tɕ','ฉ'=>'tɕʰ','ช'=>'tɕʰ','ซ'=>'s','ฌ'=>'tɕʰ','ญ'=>'j',
        'ฎ'=>'d','ฏ'=>'t','ฐ'=>'tʰ','ฑ'=>'tʰ','ฒ'=>'tʰ','ณ'=>'n',
        'ด'=>'d','ต'=>'t','ถ'=>'tʰ','ท'=>'tʰ','ธ'=>'tʰ','น'=>'n',
        'บ'=>'b','ป'=>'p','ผ'=>'pʰ','ฝ'=>'f',
        'พ'=>'pʰ','ฟ'=>'f','ภ'=>'pʰ','ม'=>'m',
        'ย'=>'j','ร'=>'r','ล'=>'l','ว'=>'w',
        'ศ'=>'s','ษ'=>'s','ส'=>'s','ห'=>'h','ฬ'=>'l',
        'อ'=>'ʔ','ฮ'=>'h','ไ'=>'h'};

# IPA of coda consonant
ccipa = {''=>'',
         'ก'=>'k','ข'=>'k','ฃ'=>'k','ค'=>'k','ฅ'=>'k','ฆ'=>'k','ง'=>'ŋ',
        'จ'=>'t','ฉ'=>'','ช'=>'t','ซ'=>'t','ฌ'=>'','ญ'=>'n',
        'ฎ'=>'t','ฏ'=>'t','ฐ'=>'t','ฑ'=>'t','ฒ'=>'t','ณ'=>'n',
        'ด'=>'t','ต'=>'t','ถ'=>'t','ท'=>'t','ธ'=>'t','น'=>'n',
        'บ'=>'p','ป'=>'p','ผ'=>'','ฝ'=>'',
        'พ'=>'p','ฟ'=>'p','ภ'=>'p','ม'=>'m',
        'ย'=>'','ร'=>'n','ล'=>'n','ว'=>'',
        'ศ'=>'t','ษ'=>'t','ส'=>'t','ห'=>'','ฬ'=>'n',
        'อ'=>'','ฮ'=>'','ไ'=>'h'};

# manner class of consonant: 0=none, 1=sonorant, 2=plosive
manner = {'k'=>2,'ŋ'=>1,'t'=>2,'n'=>1,'p'=>2,'m'=>1,''=>0}

# vowel diacritics
vds = ['','ั','ิ','ึ','ุ','ี','ื','ู','็'];
# firstvowels
fvs=['','เ','แ','โ','ใ','ไ'];
# main vowel symbols
mvs =['','า','อ','ย','ว','ฤ','ฦ'];

# vowel terminating symbols
vts = ['','ะ','ๅ','ว','ย'];

# tones
tonemarked = {''=>[],'่'=>['˦˨','˩','˩'],'้'=>['˥','˦˨','˦˨'],
              '๊'=>['','˥',''],'๋'=>['','˩˦','']}
tonedeadlong = ['˦˨','˩','˩']
tonelive = ['˧','˧','˩˦']
tonedeadshort = ['˥','˩','˩']

#######################################################################
# Main loop: create grapheme and phoneme strings
# Grapheme string includes, in order:
#  (1) first vowel, (2) onset consonant,(3) vowel diacritic,
# (4) tone diacritic, (5) main vowel, (6) 
# Phoneme string includes (1) onset consonant, (2) vowel,
#
maindict={}

# (1) first vowel 
fvs.each do |fv|
  # (2) onset consonant
  cclass.each do |oc,cclass|
    # (3) vowel diacritic
    vds.each do |vd|
      # (4) tone diacritic
      tonemarked.each do |td,ipatones|
        # (5) main vowel
        mvs.each do |mv|
          # (6) Vowel terminating symbol
          vts.each do |vt|
            vkey=fv+vd+mv+vt
            if vipa.has_key?(vkey) then
              vowel = vipa[vkey]
              
              # (7) coda consonant
              ccipa.each do |ccg,ccp|
                # open syllable inherent vowel is a, not o
                vowel = ((vkey=='' && ccg=='') ? 'a' : vowel)
                # determine the tone, based on duration of vowel & coda
                vowdur = (vowel.match(/ː/) ? 1 : 0)
                if ipatones.length > 1 then
                  tone = ipatones[cclass-1]
                elsif ((manner[ccp]==2) && vowdur) then
                  tone = tonedeadlong[cclass-1] # long vowel, coda plosive
                elsif ((manner[ccp]==1) || vowdur) then
                  tone = tonelive[cclass-1] # long vowel, coda sonorant
                else # short vowel
                  tone = tonedeadshort[cclass-1]
                end
                
                grapheme = [fv,oc,vd,td,mv,vt,ccg].join('')
                phoneme = [ocipa[oc],vowel+tone,ccp].join(' ')
                maindict[grapheme] = phoneme
              end # ccipa each
            end # if vipa.has_key
          end # vowel termination index
        end # main vowel index
      end # tone diacritic index
    end # vowel diacritic index
  end # onset consonant index
end # first vowel index

maindict.each do |grapheme,phoneme|
  puts grapheme+" "+phoneme
end
