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
PROJECT_NAME = 'teded'
# Input the full path of the downloaded ZIM file
ZIM_PATH = '/home/ghunt/zimtest/teded/zim-src/teded_en_all_2020-06.zim'

# The rest of the paths are computed and represent the standard layout
# Jupyter sets a working director as part of it's setup. We need it's value
HOME = os.environ['HOME']
WORKING_DIR = HOME + '/zimtest/' + PROJECT_NAME + '/working'
PROJECT_DIR = HOME + '/zimtest/' + PROJECT_NAME + '/tree'
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
    ++ ls /home/ghunt/zimtest/teded/tree
    ++ wc -l
    + contents=1742
    + '[' 1742 -ne 0 ']'
    + echo 'The /home/ghunt/zimtest/teded/tree is not empty. Delete if you want to repeat this step.'
    The /home/ghunt/zimtest/teded/tree is not empty. Delete if you want to repeat this step.
    + exit 0


* The next step is a manual one that you will need to do with your browser. That is: to verify that after the namespace directories were removed, and all of the html links have been adjusted correctly. Point your browser to <hostname>/zimtest/\<PROJECT_NAME\>/tree.
* If everything is working, it's time to go fetch the information about each video from youtube.


```python

```


```python
ydl = youtube_dl.YoutubeDL()

downloaded = 0
skipped = 0
# Create a list of youtube id's
yt_id_list = os.listdir(PROJECT_DIR + '/videos/')
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


```python
def get_assets_data():
    outstr = ''
    data = {}
    with open(PROJECT_DIR + '/assets/data.js', 'r') as fp:
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
tot=0
for cat in zim_category_js:
    tot += len(zim_category_js[cat])
    print(cat, len(zim_category_js[cat]))
print('Number of Videos in all categories -- perhaps used more than once:%d'%tot)
```

    actions_and_reactions  48
    humans_vs_viruses  17
    the_world_of_sports  12
    a_day_in_the_life  11
    even_more_ted_ed_originals  160
    math_in_real_life  84
    moments_of_vision  12
    the_way_we_think  38
    superhero_science  7
    ted_ed_riddles_season_1  8
    love_actually  6
    the_wonders_of_earth  13
    ted_ed_weekend_student_talks  26
    everyone_has_a_story  16
    ted_ed_riddles_season_2  8
    ted_ed_riddles_season_4  9
    awesome_nature  146
    the_big_questions  42
    math_of_the_impossible  12
    the_artist_s_palette  19
    animation_basics  12
    getting_under_our_skin  151
    questions_no_one_yet_knows_the_answers_to  8
    think_like_a_coder  9
    uploads_from_ted_ed  1680
    new_ted_ed_originals  864
    exploring_the_senses  10
    hone_your_media_literacy_skills  7
    well_behaved_women_seldom_make_history  36
    student_voices_from_tedtalksed  3
    mind_matters  44
    out_of_this_world  41
    behind_the_curtain  30
    government_declassified  33
    inventions_that_shaped_history  46
    brain_discoveries  13
    reading_between_the_lines  54
    visualizing_data  11
    integrated_photonics  3
    playing_with_language  38
    mysteries_of_vernacular  26
    how_things_work  77
    can_you_solve_this_riddle  49
    the_works_of_william_shakespeare  9
    the_basics_of_quantum_mechanics  10
    cern_space_time_101  3
    ted_ed_loves_trees  8
    facing_our_ugly_history  3
    the_great_thanksgiving_car_ride  8
    understanding_genetics  12
    more_book_recommendations_from_ted_ed  37
    tedyouth_talks  41
    ted_ed_professional_development  5
    ted_ed_riddles_season_3  7
    history_vs  11
    you_are_what_you_eat  13
    our_changing_climate  29
    the_power_of_nature  6
    the_writer_s_workshop  25
    troubleshooting_the_world  86
    before_and_after_einstein  47
    more_money_more_problems  8
    ecofying_cities  10
    the_world_s_people_and_places  125
    more_ted_ed_originals  174
    making_the_invisible_visible  9
    there_s_a_poem_for_that_season_1  12
    cyber_influence_power  29
    discovering_the_deep  28
    national_teacher_day  19
    Number of Videos in all categories -- perhaps used more than once:4713



```python
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
    return os.path.getsize(PROJECT_DIR + '/videos/' + yt_id + '/video.webm')

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

def initialize_db():
    sql = 'CREATE TABLE IF NOT EXISTS video_info ('\
            'yt_id TEXT UNIQUE, zim_size INTEGER, view_count INTEGER, average_rating REAL,slug TEXT)'
    db.c.execute(sql)

db = Sqlite(WORKING_DIR + '/zim_video_info.sqlite')
initialize_db()
yt_id_list = os.listdir(WORKING_DIR + '/video_json/' )
for yt_id in iter(yt_id_list):
    zim_data = get_zim_data(yt_id[:-5])
    slug = zim_data['slug']
    data = get_video_json(WORKING_DIR + "/video_json/" + yt_id)
    if len(data) == 0:continue
    vsize = video_size(yt_id[:-5])
    view_count = data['view_count']
    average_rating = data['average_rating']
    sql = 'INSERT OR REPLACE INTO video_info VALUES (?,?,?,?,?)'
    db.c.execute(sql,[yt_id[:-5],vsize,view_count,average_rating,slug])
db.conn.commit()
```

    Expecting value: line 1 column 1 (char 0)
    
    Expecting value: line 1 column 1 (char 0)
    



```python
sqlite_db = WORKING_DIR + '/zim_video_info.sqlite'
!sqlite3 {sqlite_db} '.headers on' 'select * from video_info limit 2'
```

    yt_id|zim_size|view_count|average_rating|slug
    eFCk3qWmCoo|29780783|13594|4.9529409|how_arduino_is_open_sourcing_imagination_massimo_banzi
    0Wb5obt7QO0|15978414|6924|4.9375|how_we_found_the_giant_squid_edith_widder



```python

```
