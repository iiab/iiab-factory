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
<PREFIX>
├── new-zim
├── tree
├── working
└── zim-src
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
* Wanted VIM bindings to edit cells, but jupyterlab version installed by conda was too old for jupyter-vim extenion. Wound up deleting old version with conda, and used pip to install both.
* Jupyterlab seems to make the current directory its root. I created a notebook directory, and aways start jupyter lab from my home directiry
* Discovered that I could enable writing by non-root group in the iiab-factory repo, and continue to use git for version control. Needed to make symbolic link from ~/miniconda to iiab-factory.
* Reminder: Start jupyterlab in console via "jupyter lab --no-browser", and then pasteing the html link displayed into my browser.

#### Declare input and output
* The ZIM file names tend to be long and hard to remember. The PROJECT_NAME, initialized below, is used to create path names. All of the output of the zimdump program is placed in \<home\>/zimtest/\<PROJECT_NAME\>/tree. All if the intermediate downloads, and data, are placed in \<home\>/zimtest/\<PROJECT_NAME\>/working. If you use the IIAB Admin Console to download ZIMS, you will find them in /library/zims/content/.


```python
# -*- coding: utf-8 -*-
import os,sys
import json
import youtube_dl
import pprint as pprint

# Declare a short project name (ZIM files are often long strings
#PROJECT_NAME = 'ted-kiwix'
PROJECT_NAME = 'teded'
PREFIX = os.environ.get('ZIM_PREFIX','/ext/zims')
TARGET_SIZE =10000000000  #10GB
# Input the full path of the downloaded ZIM file
ZIM_PATH = '%s/%s/zim-src/teded_en_all_2021-01.zim'%(PREFIX,PROJECT_NAME,) 
# The rest of the paths are computed and represent the standard layout
# Jupyter sets a working director as part of it's setup. We need it's value
HOME = os.environ['HOME']
WORKING_DIR = PREFIX + '/' + PROJECT_NAME + '/working'
PROJECT_DIR = PREFIX + '/' + PROJECT_NAME + '/tree'
OUTPUT_DIR = PREFIX + '/' + PROJECT_NAME + '/output_tree'
SOURCE_DIR = PREFIX + '/' + PROJECT_NAME + '/zim-src'
dir_list = ['output_tree','tree','working/video_json','zim-src']
for f in dir_list: 
    if not os.path.isdir(PREFIX + '/' + PROJECT_NAME +'/' + f):
       os.makedirs(PREFIX + '/' + PROJECT_NAME +'/' + f)

# abort if the input file cannot be found
if not os.path.exists(ZIM_PATH):
    print('%s path not found. Quitting. . .'%ZIM_PATH)
    exit

```


```python
print('This is the PREFIX:%s'%PREFIX)
```

    This is the PREFIX:/home/ghunt/zimtest



```python
# First we need to get a current copy of the script
dest = PREFIX
%cp /opt/iiab/iiab-factory/content/kiwix/de-namespace.sh {dest} 
```


```python
# The following command will zimdump to the "tree" directory
#  Despite the name, removing namespaces seems unnecessary, and more complex
# It will return without doing anything if the "tree' is not empty
progname = HOME + '/zimtest/de-namespace.sh'
!{progname} {ZIM_PATH} {PROJECT_NAME}
```

    + set -e
    + '[' 2 -lt 2 ']'
    + '[' '!' -f /home/ghunt/zimtest/teded/zim-src/teded_en_all_2021-01.zim ']'
    ++ ls /home/ghunt/zimtest/teded/tree
    ++ wc -l
    + contents=6
    + '[' 6 -ne 0 ']'
    + echo 'The /home/ghunt/zimtest/teded/tree is not empty. Delete if you want to repeat this step.'
    The /home/ghunt/zimtest/teded/tree is not empty. Delete if you want to repeat this step.
    + exit 0


* The next step is a manual one that you will need to do with your browser. That is: to verify that after the namespace directories were removed, and all of the html links have been adjusted correctly. Point your browser to <hostname>/zimtest/\<PROJECT_NAME\>/tree.
* If everything is working, it's time to go fetch the information about each video from youtube.


```python
ydl = youtube_dl.YoutubeDL()

downloaded = 0
skipped = 0
# Create a list of youtube id's
yt_id_list = os.listdir(PROJECT_DIR + '/I/videos/')
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

    1811 skipped and 0 downloaded


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

    the_power_of_nature  7
    the_basics_of_quantum_mechanics  11
    ted_ed_loves_trees  8
    mind_matters  48
    student_voices_from_tedtalksed  3
    ecofying_cities  13
    tedyouth_talks  41
    the_artist_s_palette  20
    creative_writing_workshop_campyoutube_withme  11
    even_more_ted_ed_originals  160
    new_ted_ed_originals  948
    our_changing_climate  43
    the_writer_s_workshop  27
    can_you_solve_this_riddle  56
    ted_ed_riddles_season_3  7
    moments_of_vision  12
    hone_your_media_literacy_skills  11
    ted_ed_riddles_season_1  8
    making_the_invisible_visible  9
    visualizing_data  11
    math_in_real_life  85
    exploring_the_senses  10
    out_of_this_world  43
    government_declassified  37
    think_like_a_coder_campyoutube_withme  13
    reading_between_the_lines  55
    the_world_s_people_and_places  134
    the_works_of_william_shakespeare  9
    the_world_of_sports  12
    elections_in_the_united_states  9
    awesome_nature  128
    the_great_thanksgiving_car_ride  8
    the_wonders_of_earth  13
    humans_vs_viruses  18
    before_and_after_einstein  47
    understanding_genetics  12
    how_things_work  70
    cern_space_time_101  3
    questions_no_one_yet_knows_the_answers_to  8
    ted_ed_riddles_season_2  8
    cyber_influence_power  29
    playing_with_language  26
    inventions_that_shaped_history  48
    facing_our_ugly_history  3
    the_big_questions  30
    think_like_a_coder  11
    love_actually  6
    there_s_a_poem_for_that_season_1  12
    mysteries_of_vernacular  26
    behind_the_curtain  30
    troubleshooting_the_world  86
    national_teacher_day  19
    myths_from_around_the_world  35
    superhero_science  7
    ted_ed_professional_development  5
    discovering_the_deep  28
    more_money_more_problems  9
    well_behaved_women_seldom_make_history  37
    getting_under_our_skin  163
    math_of_the_impossible  13
    history_vs  11
    brain_discoveries  13
    more_book_recommendations_from_ted_ed  38
    more_ted_ed_originals  174
    integrated_photonics  3
    a_day_in_the_life  14
    the_way_we_think  50
    ted_ed_weekend_student_talks  26
    animation_basics  12
    you_are_what_you_eat  15
    ted_ed_riddles_season_4  9
    uploads_from_ted_ed  1763
    actions_and_reactions  48
    Number of Videos in all categories -- perhaps used more than once:4975


#### The following Cell is subroutines and can be left minimized


```python
from pprint import pprint
from pymediainfo import MediaInfo

def mediainfo_dict(path):
    try:
        minfo = MediaInfo.parse(path)
    except:
        print('mediainfo_dict. file not found: %s'%path)
        return {}
    return minfo.to_data()

def select_info(path):
    global data
    data = mediainfo_dict(path)
    rtn = {}
    for index in range(len(data['tracks'])):
        track = data['tracks'][index]
        if track['kind_of_stream'] == 'General':
            rtn['file_size'] = track.get('file_size',0)
            rtn['bit_rate'] = track.get('overall_bit_rate',0)
            rtn['time'] = track['other_duration'][0]
        if track['kind_of_stream'] == 'Audio':
            rtn['a_stream'] = track.get('stream_size',0)
            rtn['a_rate'] = track.get('maximum_bit_rate',0)
            rtn['a_channels'] = track.get('channel_s',0)
        if track['kind_of_stream'] == 'Video':
            rtn['v_stream'] = track.get('stream_size',0)
            rtn['v_format'] = track['other_format'][0]
            rtn['v_rate'] = track.get('bit_rate',0)
            rtn['v_frame_rate'] = track.get('frame_rate',0)
            rtn['v_width'] = track.get('width',0)
            rtn['v_height'] = track.get('height',0)
    return rtn
```


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
def age_in_years(upload_date):
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
            'yt_id TEXT UNIQUE, zim_size INTEGER, view_count INTEGER, age INTEGER, '\
            'views_per_year INTEGER, upload_date TEXT, duration TEXT, '\
            'height INTEGER, width INTEGER,'\
            'bit_rate TEXT, format TEXT, '\
            'average_rating REAL,slug TEXT,title TEXT)'
    db.c.execute(sql)
    
db = Sqlite(WORKING_DIR + '/zim_video_info.sqlite')
initialize_db()
for yt_id in iter(yt_id_list):
     
    # fetch data from assets/data.js
    zim_data = get_zim_data(yt_id)
    if len(zim_data) == 0: 
        print('get_zim_data returned no data for %s'%yt_id)
        continue
    slug = zim_data['slug']
    
    # We already have youtube data for every video, use it 
    data = get_video_json(WORKING_DIR + "/video_json/" + yt_id + '.json')
    if len(data) == 0:
        print('get_video_json returned no data for %s'%yt_id)
        continue
    vsize = data.get('filesize',0)
    view_count = data['view_count']
    upload_date = data['upload_date']
    average_rating = data['average_rating']
    title = data['title']
    # calculate the views_per_year since it was uploaded
    age = round(age_in_years(upload_date))
    views_per_year = int(view_count / age)
        
    # interogate the video itself
    filename = PROJECT_DIR + '/I/videos/' + yt_id + '/video.webm'
    vsize = os.path.getsize(filename)
    selected_data = select_info(filename)
    if len(selected_data) == 0:
        duration = "not found"
        bit_rate = "" 
        v_format = ""
    else:
        duration = selected_data['time']
        bit_rate = selected_data['bit_rate']
        v_format = selected_data['v_format']
        v_height = selected_data['v_height']
        v_width = selected_data['v_width']
    
    # colums names: yt_id,zim_size,view_count,views_per_year,upload_date,duration,
    #         bit_rate, format,average_rating,slug
    sql = 'INSERT OR REPLACE INTO video_info VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    db.c.execute(sql,[yt_id,vsize,view_count,round(age),views_per_year,upload_date, \
                      duration,v_height,v_width,bit_rate,v_format,average_rating,slug,title, ])
db.conn.commit()
```

    Expecting value: line 1 column 1 (char 0)
    
    get_video_json returned no data for 9mcuIc5O-DE
    Expecting value: line 1 column 1 (char 0)
    
    get_video_json returned no data for XSb-pIloOFc



```python
print(yt_id,vsize,view_count,views_per_year,upload_date, \
                      duration,bit_rate,v_format,average_rating,slug,round(age))
```

    I2apGYUX7Q0 16108773 2871418 287141 20120311 6 min 3 s 354180 VP8 4.7891874 why_can_t_we_see_evidence_of_alien_life 10

sqlite_db = WORKING_DIR + '/zim_video_info.sqlite'
!sqlite3 {sqlite_db} '.headers on' 'select * from video_info limit 2'
#### Select the cutoff using view count and total size
* Order the videos by view count. Then select the sum line in the that has the target sum.


```python
import pandas as pd
from IPython.display import display 

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

sql = 'select slug,zim_size,views_per_year,view_count,duration,upload_date,'\
       'bit_rate from video_info order by views_per_year desc'
tot_sum = 0
db.c.execute(sql)
rows = db.c.fetchall()
row_list = []
boundary_views_per_year = 0
for row in rows:
    tot_sum += row['zim_size']
    row_list.append([row['slug'][:60],human_readable(row['zim_size']),\
                              human_readable(tot_sum),human_readable(row['view_count']),\
                              human_readable(row['views_per_year']),\
                              row['upload_date'],row['duration'],row['bit_rate']])
    if tot_sum > TARGET_SIZE and boundary_views_per_year == 0:
        boundary_views_per_year = row['views_per_year']
"""
sql = 'select slug,zim_size,views_per_year,view_count,duration,upload_date,'\
       'format,width,height,bit_rate from video_info order by views_per_year desc'
db.c.execute(sql)
rows = db.c.fetchall()
print('%60s %6s %6s %6s %6s %8s %8s'%('Name','Size','Sum','Views','Views','Date  ','Duration'))
print('%60s %6s %6s %6s %6s %8s %8s'%('','','','','/ yr','',''))
for row in rows:
    tot_sum += row['zim_size']
    print('%60s %6s %6s %6s %6s %8s %8s'%(row['slug'][:60],human_readable(row['zim_size']),\
                              human_readable(tot_sum),human_readable(row['view_count']),\
                              human_readable(row['views_per_year']),\
                              row['upload_date'],row['duration']))
"""
#df = pd.read_sql(sql,db.conn)
df = pd.DataFrame(row_list,columns=['Name','Size','Sum','Views','Views','Date','Duration','Bit Rate'])
display(df)
```


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Name</th>
      <th>Size</th>
      <th>Sum</th>
      <th>Views</th>
      <th>Views</th>
      <th>Date</th>
      <th>Duration</th>
      <th>Bit Rate</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>can_you_solve_the_prisoner_hat_riddle_alex_gen...</td>
      <td>6.65M</td>
      <td>6.65M</td>
      <td>19.6M</td>
      <td>3.27M</td>
      <td>20151005</td>
      <td>4 min 34 s</td>
      <td>203320</td>
    </tr>
    <tr>
      <th>1</th>
      <td>how_thor_got_his_hammer_scott_a_mellor</td>
      <td>8.02M</td>
      <td>14.7M</td>
      <td>9.68M</td>
      <td>3.23M</td>
      <td>20190107</td>
      <td>4 min 51 s</td>
      <td>230522</td>
    </tr>
    <tr>
      <th>2</th>
      <td>which_is_stronger_glue_or_tape_elizabeth_cox</td>
      <td>12.6M</td>
      <td>27.3M</td>
      <td>10.8M</td>
      <td>2.71M</td>
      <td>20180430</td>
      <td>4 min 50 s</td>
      <td>363555</td>
    </tr>
    <tr>
      <th>3</th>
      <td>what_are_those_floaty_things_in_your_eye_micha...</td>
      <td>6.76M</td>
      <td>34.0M</td>
      <td>18.6M</td>
      <td>2.66M</td>
      <td>20141201</td>
      <td>4 min 4 s</td>
      <td>231795</td>
    </tr>
    <tr>
      <th>4</th>
      <td>is_marijuana_bad_for_your_brain_anees_bahji</td>
      <td>12.1M</td>
      <td>46.2M</td>
      <td>4.89M</td>
      <td>2.45M</td>
      <td>20191202</td>
      <td>6 min 43 s</td>
      <td>252501</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>1804</th>
      <td>there_are_no_scraps_of_men_alberto_cairo</td>
      <td>36.4M</td>
      <td>25.8G</td>
      <td>1.07K</td>
      <td>121</td>
      <td>20130815</td>
      <td>19 min 2 s</td>
      <td>267252</td>
    </tr>
    <tr>
      <th>1805</th>
      <td>an_unexpected_place_of_healing_ramona_pierson</td>
      <td>33.8M</td>
      <td>25.9G</td>
      <td>1.01K</td>
      <td>114</td>
      <td>20130815</td>
      <td>11 min 12 s</td>
      <td>421916</td>
    </tr>
    <tr>
      <th>1806</th>
      <td>digital_humanitarianism_paul_conneally</td>
      <td>17.6M</td>
      <td>25.9G</td>
      <td>0.99K</td>
      <td>112</td>
      <td>20130626</td>
      <td>10 min 57 s</td>
      <td>225048</td>
    </tr>
    <tr>
      <th>1807</th>
      <td>the_economic_case_for_preschool_timothy_bartik</td>
      <td>31.1M</td>
      <td>25.9G</td>
      <td>706</td>
      <td>78.0</td>
      <td>20130815</td>
      <td>15 min 48 s</td>
      <td>275169</td>
    </tr>
    <tr>
      <th>1808</th>
      <td>let_s_crowdsource_the_world_s_goals_jamie_drum...</td>
      <td>26.6M</td>
      <td>25.9G</td>
      <td>687</td>
      <td>76.0</td>
      <td>20130628</td>
      <td>12 min 10 s</td>
      <td>305476</td>
    </tr>
  </tbody>
</table>
<p>1809 rows × 8 columns</p>
</div>



```python
sql = 'select yt_id,views_per_year from video_info order by views_per_year desc limit 5'
db.c.execute(sql)
rows = db.c.fetchall()
outstr = '{\n'
for row in rows:
    outstr += '  {%s:{"creator":"IIAB"}},\n'%(row['yt_id'])
outstr = outstr[:-2] + '\n}'
print(outstr)

with open(HOME + '/zimtest/' + PROJECT_NAME + '/id_list.sh','w') as fp:
    fp.write(outstr)
```

    {
      {N5vJSNXPEwA:{"creator":"IIAB"}},
      {Qytj-DbXMKQ:{"creator":"IIAB"}},
      {HHuTrcXNxOk:{"creator":"IIAB"}},
      {Y6e_m9iq-4Q:{"creator":"IIAB"}},
      {Nlcr1jd_Tok:{"creator":"IIAB"}}
    }


* Now determine the video ID's that we want in our new zim


```python
print('We will include videos with views_per_year greater than %s'%boundary_views_per_year)
wanted_ids = []
sql = 'SELECT yt_id, title from video_info where views_per_year > ?'
db.c.execute(sql,[boundary_views_per_year,])
rows = db.c.fetchall()
for row in rows:
    wanted_ids.append(row['yt_id'])

with open(HOME + '/zimtest/' + PROJECT_NAME + '/wanted_list.csv','w') as fp:
    for row in rows:
        fp.write('%s,%s\n'%(row['yt_id'],row['title'],))
```

    We will include videos with views_per_year greater than 131166


* Now let's start building up the output directory



```python
import shutil
# copy the default top level directories (these were in the zim's "-" directory )
#cpy_dirs = ['assets','cache','channels']
cpy_dirs = ['M','-','A']
for d in cpy_dirs:
    shutil.rmtree(os.path.join(OUTPUT_DIR,d))
    os.makedirs(os.path.join(OUTPUT_DIR,d))
    src = os.path.join(PROJECT_DIR,d)
    dest = os.path.join(OUTPUT_DIR,d)
    shutil.copytree(src,dest,dirs_exist_ok=True, symlinks=True)
```


```python
# Copy the videos selected by the wanted_ids list to output file
for f in wanted_ids:
    if not os.path.isdir(os.path.join(OUTPUT_DIR,'I/videos',f)):
        os.makedirs(os.path.join(OUTPUT_DIR,'I/videos',f))
    src = os.path.join(PROJECT_DIR,'I/videos',f)
    dest = os.path.join(OUTPUT_DIR,'I/videos',f)
    shutil.copytree(src,dest,dirs_exist_ok=True)
```


```python
# Copy the parts of the I directory that are not videos
src_list = os.listdir(PROJECT_DIR + '/I/')
for item in src_list:
    if item.find('videos') != -1: continue
    src = os.path.join(PROJECT_DIR,'I',item)
    if os.path.isdir(src):
        shutil.copytree(src,OUTPUT_DIR + '/I/' + item,dirs_exist_ok=True,)
    else:
        shutil.copyfile(src,OUTPUT_DIR + '/I/' + item)
```


```python
src
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

```


```python
    playlist = 'PLs2auPpToJpb6MeiaKEIpkdSWeBVgvC_p'
    CHANNEL = 'UCljl2cmQMgzlTkeJqJier7g'
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
# -*- coding: utf-8 -*-

# Sample Python code for youtube.playlists.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
A_CHANNEL =  'UC4a-Gbdw7vOaccHmFo40b9g'

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.Aj
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file =  '/home/ghunt/ghunt_google.json'

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.playlists().list(
       [A_CHANNEL,] 
    )
    response = request.execute()

    print(response)

if __name__ == "__main__":
    main()
```


    ---------------------------------------------------------------------------

    FileNotFoundError                         Traceback (most recent call last)

    <ipython-input-1-4d5db08f780f> in <module>
         38 
         39 if __name__ == "__main__":
    ---> 40     main()
    

    <ipython-input-1-4d5db08f780f> in main()
         24 
         25     # Get credentials and create an API client
    ---> 26     flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
         27         client_secrets_file, scopes)
         28     credentials = flow.run_console()


    ~/miniconda3/lib/python3.9/site-packages/google_auth_oauthlib/flow.py in from_client_secrets_file(cls, client_secrets_file, scopes, **kwargs)
        201             Flow: The constructed Flow instance.
        202         """
    --> 203         with open(client_secrets_file, "r") as json_file:
        204             client_config = json.load(json_file)
        205 


    FileNotFoundError: [Errno 2] No such file or directory: '/home/ghunt/ghunt_google.json'



```python

```


```python

```


```python

```
