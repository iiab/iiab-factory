## Modifying ZIM Files

#### The Larger Picture
* Kiwix scrapes many useful sources, but sometimes the chunks are too big for IIAB.
* Using the zimdump program, the highly compressed ZIM files can be flattened into a file tree, modified, and then re-packaged as a ZIM file.
* This Notebook has a collection of tools which help in the above process.


#### How to Use this notebook
* There are install steps that only need to happen once. The cells containing these steps are set to "Raw" in the right most dropdown so that they do not execute automatically each time the notebook starts.
* The following bash script successfully installed zimtools on Ubuntu 20.04.It only needs to be run once. I think it's easier to do it from the command line, with tab completion. In a terminal, do the following:

```
cd /opt/iiab/iiab-factory/content/kiwix/generic/ 
sudo ./install-zim-tools.sh
```

* **Some conventions**: Jupyter does not want to run as root. We will create a file structure that exists in the users home directory -- so the application will be able to write all the files it needs to function.
```
<home directory>
├── new_zim
├── tree
└── working
```
In general terms, this program will dump the zim data into "tree", modify it, gather additional data into "working"
, and create a ZIM file in "new_zim"
* For testing purposes, the user will need to link from the server's document root to her home directory (so that the nginx http server in IIAB will serve the candidate in "tree):

```
cd
mkdir -p zimtest
ln -s /home/<user name>/zimtest /library/www/html/zimtest 
```


#### Installation Notes to myself
* Installing on Windows 10 insider preview WSL2. Used https://towardsdatascience.com/configuring-jupyter-notebook-in-windows-subsystem-linux-wsl2-c757893e9d69.
* First tried installing miniconda, and then installing jupyterlab with it.
* Wanted VIM bindings to edit cells, but jupyterlab version insralled by conda was too old for jupyter-vim extenion. Wound up deleting old version with conda, and used pip to install both.
* Jupyterlab seems to make the current directory its root. I created a notebook directory, and aways start jupyter lab from my home directiry
* Discovered that I could enable writing by non-root group in the iiab-factory repo, and continue to use git for version control. Needed to make symbolic link from ~/miniconda to iiab-factory.
* Reminder: Start jupyterlav in console via "jupyter lab --no-browser", and then pasteing the html link displayed into my browser.

#### Declare input and output
* The ZIM file names tend to be long and hard to remember. The PROJECT_NAME, initialized below, is used to create path names. All of the output of the zimdump program is placed in \<home\>/zimtest/\<PROJECT_NAME\>/tree. All if the intermediate downloads, and data, are placed in \<home\>/zimtest/\<PROJECT_NAME\>/working. If you use the IIAB Admin Console to download ZIMS, you will find them in /library/zims/content/.


```python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os,sys
import json
import youtube_dl
import pprint as pprint

# Declare a short project name (ZIM files are often long strings
#PROJECT_NAME = 'ted-kiwix'
PROJECT_NAME = 'ted-kiwix'
# Input the full path of the downloaded ZIM file
ZIM_PATH = '/home/ghunt/zimtest/teded/zim-src/teded_en_all_2020-06.zim'

# The rest of the paths are computed and represent the standard layout
# Jupyter sets a working director as part of it's setup. We need it's value
HOME = os.environ['HOME']
WORKING_DIR = HOME + '/zimtest/' + PROJECT_NAME + '/working'
PROJECT_DIR = HOME + '/zimtest/' + PROJECT_NAME + '/tree'
OUTPUT_DIR = HOME + '/zimtest/' + PROJECT_NAME + '/new-zim'
dir_list = ['new-zim','tree','working/video_json']
for f in dir_list: 
    if not os.path.isdir(HOME + '/zimtest/' + PROJECT_NAME +'/' + f):
       os.makedirs(HOME + '/zimtest/' + PROJECT_NAME +'/' + f)

# abort if the input file cannot be found
if not os.path.exists(ZIM_PATH):
    print('%s path not found. Quitting. . .'%ZIM_PATH)
    exit

```


```python
# First we need to get a current copy of the script
dest = HOME + '/zimtest'
%cp /opt/iiab/iiab-factory/content/kiwix/de-namespace.sh {dest} 
```


```python
# The following command will zimdump to the "tree" directory
#   and remove the namespace directories
# It will return without doing anything if the "tree' is not empty
progname = HOME + '/zimtest/de-namespace.sh'
!{progname} {ZIM_PATH} {PROJECT_NAME}
```

    + set -e
    + '[' 2 -lt 2 ']'
    + '[' '!' -f /home/ghunt/zimtest/teded/zim-src/teded_en_all_2020-06.zim ']'
    ++ ls /home/ghunt/zimtest/ted-kiwix/tree
    ++ wc -l
    + contents=3
    + '[' 3 -ne 0 ']'
    + echo 'The /home/ghunt/zimtest/ted-kiwix/tree is not empty. Delete if you want to repeat this step.'
    The /home/ghunt/zimtest/ted-kiwix/tree is not empty. Delete if you want to repeat this step.
    + exit 0


* The next step is a manual one that you will need to do with your browser. That is: to verify that after the namespace directories were removed, and all of the html links have been adjusted correctly. Point your browser to <hostname>/zimtest/\<PROJECT_NAME\>/tree.
* If everything is working, it's time to go fetch the information about each video from youtube.


```python
ydl = youtube_dl.YoutubeDL()

downloaded = 0
skipped = 0
# Create a list of youtube id's
yt_id_list = os.listdir(PROJECT_DIR + '/-/videos/')
for yt_id in iter(yt_id_list):
    if os.path.exists(WORKING_DIR + '/video_json/' + yt_id + '.json'):
        # skip over items that are already downloadd
        skipped += 1
        continue
    with ydl:
       result = ydl.extract_info(
                'http://www.youtube.com/watch?v=%s'%yt_id,
                download=False # We just want to extract the info
                )
       downloaded += 1

    with open(WORKING_DIR + '/video_json/' + yt_id + '.json','w') as fp:
        fp.write(json.dumps(result))
    #pprint.pprint(result['upload_date'],result['view_count'])
print('%s skipped and %s downloaded'%(skipped,downloaded))
```

#### Playlist Navigation to Videos
* On the home page there is a drop down selector which lists about 70 cateegories (or playlists).
* The value from that drop down is used to pick an entry in "-/assets/data.js", which in turn specifies the playlist of yourtube ID"s that are displayed when a selection is made.


```python
def get_assets_data():
    # the file <root>/assets/data.js holds the category to video mappings
    outstr = ''
    data = {}
    with open(PROJECT_DIR + '/-/assets/data.js', 'r') as fp:
    #with open(OUTPUT_DIR + '/I/assets/data.js', 'r') as fp:
        while True:
            line = fp.readline()
            if not line:
                break
            if line.startswith('var'):
                if len(outstr) > 1:
                    # clip off the trailing semicolon
                    outstr = outstr[:-2]
                    try:
                        data[cat] = json.loads(outstr)
                    except Exception:
                        print('Parse error: %s'%outstr[:80])
                        exit
                cat = line[9:-4]
                outstr = '['
            else:
                outstr += line
    return data

zim_category_js = get_assets_data()

def get_zim_data(yt_id):
    rtn_dict = {}
    for cat in zim_category_js:
        for video in range(len(zim_category_js[cat])):
            if zim_category_js[cat][video]['id'] == yt_id:
                rtn_dict = zim_category_js[cat][video]
                break
        if len(rtn_dict) > 0: break
    return rtn_dict
```


```python
# enable this cell if you want summarize each category, and get a total of videos
#   including those that are in more than one categofy
tot=0
for cat in zim_category_js:
    tot += len(zim_category_js[cat])
    print(cat, len(zim_category_js[cat]))
print('Number of Videos in all categories -- perhaps used more than once:%d'%tot)
```

#### The following Cell is subroutines and can be left minimized


```python
import datetime
from pprint import pprint
from pymediainfo import MediaInfo

class VideoInfo(object):
    def __init__(self,ted_root):
        self.ted_root = ted_root

    def mediainfo_dict(self,path):
        if path[0] != "/":
            path = os.path.join(self.ted_root,path)
        try:
            minfo = MediaInfo.parse(path)
        except:
            return {}
        return minfo.to_data()

    def select_info(self,path):
        global data
        if path[0] != "/":
            path = os.path.join(self.ted_root,path)
        data = self.mediainfo_dict(path)
        if len(data) == 0:
            return {}
        rtn = {}
        for index in range(len(data['tracks'])):
            track = data['tracks'][index]
            if track['kind_of_stream'] == 'General':
                rtn['file_size'] = track['file_size']
                rtn['bit_rate'] = track['overall_bit_rate']
                rtn['time'] = track['other_duration'][0]
            if track['kind_of_stream'] == 'Audio':
                rtn['a_stream'] = track['stream_size']
                rtn['a_rate'] = track['maximum_bit_rate']
                rtn['a_channels'] = track['channel_s']
            if track['kind_of_stream'] == 'Video':
                rtn['v_stream'] = track['stream_size']
                rtn['v_format'] = track['other_format'][0]
                rtn['v_rate'] = track['bit_rate']
                rtn['v_frame_rate'] = track['frame_rate']
        return rtn

import sqlite3
class Sqlite():
   def __init__(self, filename):
      self.conn = sqlite3.connect(filename)
      self.conn.row_factory = sqlite3.Row
      self.conn.text_factory = str
      self.c = self.conn.cursor()
    
   def __del__(self):
      self.conn.commit()
      self.c.close()
      del self.conn

def get_video_json(path):
    with open(path,'r') as fp:
        try:
            jsonstr = fp.read()
            #print(path)
            modules = json.loads(jsonstr.strip())
        except Exception as e:
            print(e)
            print(jsonstr[:80])
            return {}
    return modules

def video_size(yt_id):
    return os.path.getsize(PROJECT_DIR + '/-/videos/' + yt_id + '/video.webm')

def make_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def download_file(url,todir):
    local_filename = url.split('/')[-1]
    r = requests.get(url)
    f = open(todir + '/' + local_filename, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024):
        if chunk:
            f.write(chunk)
    f.close()
    
from datetime import datetime
def calc_views_per_year(upload_date,views):
    uploaded_dt = datetime.strptime(upload_date,"%Y%m%d")
    now_dt = datetime.now()
    days_delta = now_dt - uploaded_dt
    years = days_delta.days/365 + 1
    return years
```

#### Create a sqlite database which collects Data about each Video
* We've already downloaded the data from YouTube for each Video. So get the items that are interesing to us. Such as size,date uploaded to youtube,view count


```python
def initialize_db():
    sql = 'CREATE TABLE IF NOT EXISTS video_info ('\
            'yt_id TEXT UNIQUE, zim_size INTEGER, view_count INTEGER, '\
            'views_per_year INTEGER, upload_date TEXT, duration TEXT, '\
            'bit_rate TEXT, format TEXT, '\
            'average_rating REAL,slug TEXT)'
    db.c.execute(sql)
    
db = Sqlite(WORKING_DIR + '/zim_video_info.sqlite')
initialize_db()
vinfo = VideoInfo(PROJECT_DIR)
yt_id_list = os.listdir(PROJECT_DIR + '/-/videos/' )
for yt_id in iter(yt_id_list):
    
    # fetch data from assets/data.js
    zim_data = get_zim_data(yt_id)
    if len(zim_data) == 0: continue
    slug = zim_data['slug']
    # We already have youtube data for every video, use it 
    data = get_video_json(WORKING_DIR + "/video_json/" + yt_id + '.json')
    if len(data) == 0:continue
    print('got here')
    exit
    vsize = data.get('filesize',0)
    view_count = data['view_count']
    upload_date = data['upload_date']
    average_rating = data['average_rating']
    # calculate the views_per_year since it was uploaded
    views_per_year = calc_views_per_year(upload_date,view_count)
        
    # interogate the video itself
    selected_data = vinfo.select_info(PROJECT_DIR + '/-/videos/' + yt_id + '/video.webm')
    if len(selected_data) == 0:
        duration = "not found"
        bit_rate = "" 
        formaat = ""
    else:
        duration = selected_data['time']
        bit_rate = str(selected_data['bit_rate'])
        format = selected_data['v_format']
    
    # colums names: yt_id,zim_size,view_count,views_per_year,upload_date,duration,
    #         bit_rate, format,average_rating,slug
    sql = 'INSERT OR REPLACE INTO video_info VALUES (?,?,?,?,?,?,?,?,?,?)'
    db.c.execute(sql,[yt_id,vsize,view_count,views_per_year,upload_date, \
                      duration,bit_rate,format,average_rating,slug, ])
db.conn.commit()
```

    got here



    ---------------------------------------------------------------------------

    InterfaceError                            Traceback (most recent call last)

    <ipython-input-57-d2be1efc8ec0> in <module>
         43     #         bit_rate, format,average_rating,slug
         44     sql = 'INSERT OR REPLACE INTO video_info VALUES (?,?,?,?,?,?,?,?,?,?)'
    ---> 45     db.c.execute(sql,[yt_id,vsize,view_count,views_per_year,upload_date, \
         46                       duration,bit_rate,format,average_rating,slug, ])
         47 db.conn.commit()


    InterfaceError: Error binding parameter 7 - probably unsupported type.



```python
bit_rate
```




    ''




```python
sqlite_db = WORKING_DIR + '/zim_video_info.sqlite'
!sqlite3 {sqlite_db} '.headers on' 'select * from video_info limit 2'
```

#### Select the cutoff using view count and total size
* Order the videos by view count. Then select the sum line in the that has the target sum.


```python
def human_readable(num):
    # return 3 significant digits and unit specifier
    num = float(num)
    units = [ '','K','M','G']
    for i in range(4):
        if num<10.0:
            return "%.2f%s"%(num,units[i])
        if num<100.0:
            return "%.1f%s"%(num,units[i])
        if num < 1000.0:
            return "%.0f%s"%(num,units[i])
        num /= 1024.0

sql = 'select slug,zim_size,view_count from video_info order by view_count desc'
tot_sum = 0
db.c.execute(sql)
rows = db.c.fetchall()
print('%60s %6s %6s %6s'%('Name','Size','Sum','Views'))
for row in rows:
    tot_sum += row['zim_size']
    print('%60s %6s %6s %6s'%(row['slug'][:60],human_readable(row['zim_size']),\
                              human_readable(tot_sum),human_readable(row['view_count']),))
```


```python

```

* Enter the view count minimum, which will generate a list of wanted youtube id's.


```python
views_min = 375000
print(type(views_min))
wanted_ids = []
sql = 'SELECT yt_id from video_info where view_count > ?'
db.c.execute(sql,[views_min,])
rows = db.c.fetchall()
for row in rows:
    wanted_ids.append(row['yt_id'])
```

* Now let's start building up the output directory



```python
import shutil
# copy the default top level directories (these were in the zim's "-" directory )
cpy_dirs = ['assets','cache','channels']
for d in cpy_dirs:
    if not os.isdir(os.path.join(OUTPUT_DIR,d))
        os.makedirs(os.path.join(OUTPUT_DIR,d))
    src = os.path.join(PROJECT_DIR,d)
    dest = os.path.join(OUTPUT_DIR,d)
    shutil.copytree(src,dest,dirs_exist_ok=True)
```


```python
# Copy the videos selected by the wanted_ids list to output file
for f in wanted_ids:
    if not os.path.isdir(os.path.join(OUTPUT_DIR,'-/videos',f)):
        os.makedirs(os.path.join(OUTPUT_DIR,'-/videos',f))
    src = os.path.join(PROJECT_DIR,'-/videos',f)
    dest = os.path.join(OUTPUT_DIR,'-/videos',f)
    shutil.copytree(src,dest,dirs_exist_ok=True)
```


```python
# Grab the meta data from the original zim "M" directory 
#   and create a script for zimwriterfs
def get_file_value(path):
    with open(path,'r') as fp:
        
        try:
            return fp.read()
        except:
            return ""
meta_file_names = []        


```


```python
# Copy the top level html files 
for f in iter(os.listdir(PROJECT_DIR)):
    if os.path.isfile(os.path.join(PROJECT_DIR,f)):
        src = os.path.join(PROJECT_DIR,f)
        !cp {src} {OUTPUT_DIR}
```


```python
# Write a new mapping from categories to vides (with some removed)
outstr = ''
for cat in zim_category_js:
    outstr += 'var json_%s = [\n'%cat
    for video in range(len(zim_category_js[cat])):
        if zim_category_js[cat][video].get('id','') in wanted_ids:
            outstr += json.dumps(zim_category_js[cat][video],indent=1)
            outstr += ','
    outstr = outstr[:-1]
    outstr += '];\n'
with open(OUTPUT_DIR + '/-/assets/data.js','w') as fp:
    fp.write(outstr)

```


```python
# Create a template for a script to run zimwriterfs
mk_zim_cmd = """
zimwriterfs --language=eng\
            --welcome=home.html\
            --favicon=./favicon.jpg\
            --title=teded_en_med\
            --description=\"TED-Ed Videos from YouTube Channel\"\
            --creator='Youtube Channel “TED-Ed”'\
            --publisher=IIAB\
            --name=TED-Ed\
             %s %s.zim"""%(OUTPUT_DIR,PROJECT_NAME)
with open(HOME + '/zimtest/' + PROJECT_NAME + '-zimwriter-cmd.sh','w') as fp:
    fp.write(mk_zim_cmd)
```


```python

```


```python

```
