## Modifying ZIM Files

#### The Larger Picture
* Kiwix scrapes many useful sources, but sometimes the chunks are too big for IIAB.
* Using the zimdump program, the highly compressed ZIM files can be flattened into a file tree, modified, and then re-packaged as a ZIM file.
* This Notebook has a collection of tools which help in the above process.


#### How to Use this notebook
* There are install steps that only need to happen once. The cells containing these steps are set to "Raw" in the right most dropdown so that they do not execute automatically each time the notebook starts.
* The following bash script successfully installed zimtools on Ubuntu 20.04.It only needs to be run once. I think it's easier to do it from the command line, with tab completion. The script is at  
/opt/iiab/iiab-factory/content/kiwix/generic/install-zim-tools.sh. 
```
./install-zim-tools.sh
```

### Declare input and output environment
* The ZIM file names tend to be long and hard to remember. The PROJECT_NAME, initialized below, is used to create output path names. All of the output of the zimdump program is placed in /library/www/html/zimtest/\<PROJECT_NAME\>. All if the intermediate downloads, and data, are placed in /library/working/kiwix/\<PROJECT_NAME\>. If you use the IIAB Admin Console to download ZIMS, you will find them in /library/zims/content/.


```python
# -*- coding: utf-8 -*-
import os,sys

# Declare a short project name (ZIM files are often long strings), and declare the full path of input ZIM
PROJECT_NAME = 'teded'
ZIM_PATH = '/library/www/html/teded/teded_en_all_2020-06.zim'
if not os.path.exists(ZIM_PATH):
    print('%s path not found. Quitting. . .')
    sys.exit(2)
os.makedirs('library/www/html/zimtest/%s'%PROJECT_NAME)
os.makedirs('library/working/kivix/%s'%PROJECT_NAME)

```
%%bash
'./de_namespace.sh