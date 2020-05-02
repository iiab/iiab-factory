#!/usr/bin/env python3
# Translate video closed caption strings into another language

import sys,os
import re
from googletrans import Translator
translator = Translator()

target_langs = ['es','fr','en']
#target_langs = ['es']

if len(sys.argv) == 1:
   print('Please include the file to translate as first parameter')
   sys.exit(1)

curdir = os.getcwd()
if not os.path.exists(f'{curdir}/output'):
   os.mkdir(f'{curdir}/output')

if not os.path.exists(sys.argv[1]):
   print('{} not found'.format(sys.argv[1]))          
   sys.exit(1)
basename = os.path.basename(sys.argv[1])
basename = basename.split('.')[0]

for lang in target_langs:
   if os.path.exists(f'output/{basename}.{lang}.vtt'):
      continue
   num = 1
   with open(f'output/{basename}.{lang}.vtt','w') as outfh:
      outfh.write("WEBVTT\n")
      outfh.write("Kind: captions\n")
      outfh.write(f"Language: {lang}\n\n")
      with open(sys.argv[1]) as fh:
         lines = fh.readlines()
         for line in lines:
            if line[:4] == 'WEBV': continue
            if line[:4] == 'Kind': continue
            if line[:4] == 'Lang': continue
            if line.rstrip() == '':
               outfh.write(line + '\n')
               continue
            if re.match(r'\d\d:\d\d',line):
               outfh.write(line)
               continue
            print(line)
            tline = translator.translate(line, dest=lang, src="en")
            outfh.write(tline.text+'\n')
