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
# Input the full path of the downloaded ZIM file
ZIM_PATH = '%s/%s/zim-src/teded_en_all_2021-01.zim'%(PREFIX,PROJECT_NAME,) 
# The rest of the paths are computed and represent the standard layout
# Jupyter sets a working director as part of it's setup. We need it's value
HOME = os.environ['HOME']
WORKING_DIR = PREFIX + '/' + PROJECT_NAME + '/working'
PROJECT_DIR = PREFIX + '/' + PROJECT_NAME + '/tree'
OUTPUT_DIR = PREFIX + '/' + PROJECT_NAME + '/new-zim'
SOURCE_DIR = PREFIX + '/' + PROJECT_NAME + '/zim-src'
dir_list = ['new-zim','tree','working/video_json','zim-src']
for f in dir_list: 
    if not os.path.isdir(PREFIX + '/' + PROJECT_NAME +'/' + f):
       os.makedirs(PREFIX + '/' + PROJECT_NAME +'/' + f)

# abort if the input file cannot be found
if not os.path.exists(ZIM_PATH):
    print('%s path not found. Quitting. . .'%ZIM_PATH)
    exit

```

    /home/ghunt/zimtest/teded/zim-src/teded_en_all_2021-01.zim path not found. Quitting. . .



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
    + contents=0
    + '[' 0 -ne 0 ']'
    + rm -rf /home/ghunt/zimtest/teded/tree
    + mkdir -p /home/ghunt/zimtest/teded/tree
    + echo 'This de-namespace file reminds you that this folder will be overwritten?'
    + zimdump dump --dir=/home/ghunt/zimtest/teded/tree /home/ghunt/zimtest/teded/zim-src/teded_en_all_2021-01.zim
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

    [youtube] CMQLdJa64Wk: Downloading webpage
    [youtube] D-2p86FvqF4: Downloading webpage
    [youtube] 4nZ9gNGZwO0: Downloading webpage
    [youtube] nZP7pb_t4oA: Downloading webpage
    [youtube] uMNwUh0X5eI: Downloading webpage
    [youtube] M0VWroX0gZA: Downloading webpage
    [youtube] iePEw_cHp8s: Downloading webpage
    [youtube] 2_CNihv5PCs: Downloading webpage
    [youtube] vPtzpjC7TF4: Downloading webpage
    [youtube] 4KQeu_mTYTQ: Downloading webpage
    [youtube] NCPTbfQyMt8: Downloading webpage
    [youtube] VixAX2IzaE4: Downloading webpage
    [youtube] ovl_XbgmCbw: Downloading webpage
    [youtube] qWyLtYrTLYo: Downloading webpage
    [youtube] 5y0pcLkD7-I: Downloading webpage
    [youtube] 3hxE7Af98AI: Downloading webpage
    [youtube] rLL-y2WLE14: Downloading webpage
    [youtube] 0O_boW9YA7I: Downloading webpage
    [youtube] dcZ0BXJYlUA: Downloading webpage
    [youtube] e0uyu9vdd2g: Downloading webpage
    [youtube] ZsiHrK9DvvQ: Downloading webpage
    [youtube] tuZcS2Flabw: Downloading webpage
    [youtube] YiydsMxOdM8: Downloading webpage
    [youtube] Q6ZEf6UZyco: Downloading webpage
    [youtube] hz6GULbowAk: Downloading webpage
    [youtube] 8HLtFv_KqoE: Downloading webpage
    [youtube] Gh3BRfXwmsE: Downloading webpage
    [youtube] Iu4OdhjnN4I: Downloading webpage
    [youtube] y4BDnlUQ3CA: Downloading webpage
    [youtube] NTeOhj6dxsU: Downloading webpage
    [youtube] g12bxfYVhMk: Downloading webpage
    [youtube] jRvxnpfCDSo: Downloading webpage
    [youtube] rn1mjuVXNEI: Downloading webpage
    [youtube] 9GMbRG9CZJw: Downloading webpage
    [youtube] XJasV-itdoc: Downloading webpage
    [youtube] rI9yUJl00Ik: Downloading webpage
    [youtube] O5dXz1Tq_Yg: Downloading webpage
    [youtube] D89ngRr4uZg: Downloading webpage
    [youtube] 6d_dtVTs4CM: Downloading webpage
    [youtube] EidLGwyYpBE: Downloading webpage
    [youtube] 6aKUQr4YTgE: Downloading webpage
    [youtube] QkZCPMVgR4g: Downloading webpage
    [youtube] PaxVCsnox_4: Downloading webpage
    [youtube] wy0mU-SbOrw: Downloading webpage
    [youtube] 8Poklx9Ifz4: Downloading webpage
    [youtube] _8kV4FHSdNA: Downloading webpage
    [youtube] s6TXDFp1EcM: Downloading webpage
    [youtube] K_r-kMJjh8Y: Downloading webpage
    [youtube] 3_fjEc4aQVk: Downloading webpage
    [youtube] GLQos7-Vq8M: Downloading webpage
    [youtube] Xu2euaQGzDQ: Downloading webpage
    [youtube] eAQ1Ee5kTMQ: Downloading webpage
    [youtube] sshUgVo8r3U: Downloading webpage
    [youtube] lN7Fmt1i5TI: Downloading webpage
    [youtube] tbkiYideS-4: Downloading webpage
    [youtube] B5vEfuLS2Qc: Downloading webpage
    [youtube] L9rkQJ91VOE: Downloading webpage
    [youtube] IzFObkVRSV0: Downloading webpage
    [youtube] RQW3zC5QaY4: Downloading webpage
    [youtube] hNNqht30TDo: Downloading webpage
    [youtube] XBk9KywTIgk: Downloading webpage
    [youtube] lawx8YoLEIY: Downloading webpage
    [youtube] VrqBX-Tck2A: Downloading webpage
    [youtube] auhrB0bSTEo: Downloading webpage
    [youtube] lz0lQ58QMzQ: Downloading webpage
    [youtube] TnsCsR2wDdk: Downloading webpage
    [youtube] M7cIc7IAN6U: Downloading webpage
    [youtube] esvycD1O3cM: Downloading webpage
    [youtube] F_ssj7-8rYg: Downloading webpage
    [youtube] itEXhxjOPjk: Downloading webpage
    [youtube] lmYQMJi30aw: Downloading webpage
    [youtube] W8O131s31Rg: Downloading webpage
    [youtube] GmtcxWswrB8: Downloading webpage
    [youtube] xFqecEtdGZ0: Downloading webpage
    [youtube] LQwZwKS9RPs: Downloading webpage
    [youtube] RFi6ISTjkR4: Downloading webpage
    [youtube] zC8abuKnr90: Downloading webpage
    [youtube] 9iAn6Jdb-ig: Downloading webpage
    [youtube] hk9c7sJ08Bg: Downloading webpage
    [youtube] 74WQgNa3OsQ: Downloading webpage
    [youtube] W5w75eGTnag: Downloading webpage
    [youtube] 40ehHbdi95o: Downloading webpage
    [youtube] 4eGFMw3U1ts: Downloading webpage
    [youtube] emyi4z-O0ls: Downloading webpage
    1727 skipped and 84 downloaded


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
            'average_rating REAL,slug TEXT)'
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
    sql = 'INSERT OR REPLACE INTO video_info VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'
    db.c.execute(sql,[yt_id,vsize,view_count,round(age),views_per_year,upload_date, \
                      duration,v_height,v_width,bit_rate,v_format,average_rating,slug, ])
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
for row in rows:
    tot_sum += row['zim_size']
    row_list.append([row['slug'][:60],human_readable(row['zim_size']),\
                              human_readable(tot_sum),human_readable(row['view_count']),\
                              human_readable(row['views_per_year']),\
                              row['upload_date'],row['duration'],row['bit_rate']])
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
      <th>5</th>
      <td>the_infinite_hotel_paradox_jeff_dekofsky</td>
      <td>9.92M</td>
      <td>56.1M</td>
      <td>19.1M</td>
      <td>2.39M</td>
      <td>20140116</td>
      <td>5 min 59 s</td>
      <td>231157</td>
    </tr>
    <tr>
      <th>6</th>
      <td>can_you_solve_the_bridge_riddle_alex_gendler</td>
      <td>6.09M</td>
      <td>62.2M</td>
      <td>16.6M</td>
      <td>2.38M</td>
      <td>20150901</td>
      <td>3 min 49 s</td>
      <td>222600</td>
    </tr>
    <tr>
      <th>7</th>
      <td>a_brie_f_history_of_cheese_paul_kindstedt</td>
      <td>7.95M</td>
      <td>70.1M</td>
      <td>7.05M</td>
      <td>2.35M</td>
      <td>20181213</td>
      <td>5 min 33 s</td>
      <td>200043</td>
    </tr>
    <tr>
      <th>8</th>
      <td>why_don_t_perpetual_motion_machines_ever_work_...</td>
      <td>16.6M</td>
      <td>86.7M</td>
      <td>11.0M</td>
      <td>2.20M</td>
      <td>20170605</td>
      <td>5 min 30 s</td>
      <td>420432</td>
    </tr>
    <tr>
      <th>9</th>
      <td>can_you_solve_the_wizard_standoff_riddle_dan_f...</td>
      <td>8.15M</td>
      <td>94.9M</td>
      <td>8.75M</td>
      <td>2.19M</td>
      <td>20180522</td>
      <td>5 min 25 s</td>
      <td>210105</td>
    </tr>
    <tr>
      <th>10</th>
      <td>history_s_worst_nun_theresa_a_yugar</td>
      <td>13.6M</td>
      <td>109M</td>
      <td>4.29M</td>
      <td>2.14M</td>
      <td>20191121</td>
      <td>4 min 46 s</td>
      <td>399725</td>
    </tr>
    <tr>
      <th>11</th>
      <td>questions_no_one_knows_the_answers_to_full_ver...</td>
      <td>34.0M</td>
      <td>143M</td>
      <td>21.4M</td>
      <td>2.14M</td>
      <td>20120317</td>
      <td>12 min 7 s</td>
      <td>392272</td>
    </tr>
    <tr>
      <th>12</th>
      <td>the_tale_of_the_doctor_who_defied_death_iseult...</td>
      <td>9.68M</td>
      <td>152M</td>
      <td>4.23M</td>
      <td>2.11M</td>
      <td>20200312</td>
      <td>5 min 27 s</td>
      <td>248250</td>
    </tr>
    <tr>
      <th>13</th>
      <td>the_language_of_lying_noah_zandan</td>
      <td>8.93M</td>
      <td>161M</td>
      <td>14.4M</td>
      <td>2.06M</td>
      <td>20141103</td>
      <td>5 min 41 s</td>
      <td>219233</td>
    </tr>
    <tr>
      <th>14</th>
      <td>what_makes_muscles_grow_jeffrey_siegel</td>
      <td>6.63M</td>
      <td>168M</td>
      <td>11.9M</td>
      <td>1.99M</td>
      <td>20151103</td>
      <td>4 min 19 s</td>
      <td>214096</td>
    </tr>
    <tr>
      <th>15</th>
      <td>how_do_cigarettes_affect_the_body_krishna_sudhir</td>
      <td>12.7M</td>
      <td>180M</td>
      <td>5.85M</td>
      <td>1.95M</td>
      <td>20180913</td>
      <td>5 min 20 s</td>
      <td>333076</td>
    </tr>
    <tr>
      <th>16</th>
      <td>can_you_solve_the_three_gods_riddle_alex_gendler</td>
      <td>7.41M</td>
      <td>188M</td>
      <td>9.52M</td>
      <td>1.90M</td>
      <td>20170221</td>
      <td>4 min 53 s</td>
      <td>211551</td>
    </tr>
    <tr>
      <th>17</th>
      <td>a_day_in_the_life_of_a_roman_soldier_robert_ga...</td>
      <td>9.16M</td>
      <td>197M</td>
      <td>7.59M</td>
      <td>1.90M</td>
      <td>20180329</td>
      <td>4 min 59 s</td>
      <td>256325</td>
    </tr>
    <tr>
      <th>18</th>
      <td>the_surprising_effects_of_pregnancy</td>
      <td>19.8M</td>
      <td>217M</td>
      <td>1.77M</td>
      <td>1.77M</td>
      <td>20201001</td>
      <td>5 min 45 s</td>
      <td>481988</td>
    </tr>
    <tr>
      <th>19</th>
      <td>can_you_solve_the_virus_riddle_lisa_winer</td>
      <td>9.66M</td>
      <td>227M</td>
      <td>8.58M</td>
      <td>1.72M</td>
      <td>20170403</td>
      <td>5 min 12 s</td>
      <td>259588</td>
    </tr>
    <tr>
      <th>20</th>
      <td>can_you_solve_einsteins_riddle_dan_van_der_vieren</td>
      <td>8.86M</td>
      <td>235M</td>
      <td>10.3M</td>
      <td>1.71M</td>
      <td>20151130</td>
      <td>5 min 12 s</td>
      <td>238125</td>
    </tr>
    <tr>
      <th>21</th>
      <td>how_to_practice_effectively_for_just_about_any...</td>
      <td>9.17M</td>
      <td>245M</td>
      <td>8.50M</td>
      <td>1.70M</td>
      <td>20170227</td>
      <td>4 min 49 s</td>
      <td>266215</td>
    </tr>
    <tr>
      <th>22</th>
      <td>why_incompetent_people_think_they_re_amazing_d...</td>
      <td>10.9M</td>
      <td>255M</td>
      <td>6.66M</td>
      <td>1.66M</td>
      <td>20171109</td>
      <td>5 min 7 s</td>
      <td>296888</td>
    </tr>
    <tr>
      <th>23</th>
      <td>can_you_solve_the_prisoner_boxes_riddle_yossi_...</td>
      <td>9.44M</td>
      <td>265M</td>
      <td>8.26M</td>
      <td>1.65M</td>
      <td>20161003</td>
      <td>4 min 51 s</td>
      <td>271188</td>
    </tr>
    <tr>
      <th>24</th>
      <td>can_you_solve_the_famously_difficult_green_eye...</td>
      <td>8.05M</td>
      <td>273M</td>
      <td>11.5M</td>
      <td>1.64M</td>
      <td>20150616</td>
      <td>4 min 41 s</td>
      <td>239440</td>
    </tr>
    <tr>
      <th>25</th>
      <td>the_myth_of_arachne_iseult_gillespie</td>
      <td>9.15M</td>
      <td>282M</td>
      <td>6.46M</td>
      <td>1.61M</td>
      <td>20180208</td>
      <td>4 min 29 s</td>
      <td>285103</td>
    </tr>
    <tr>
      <th>26</th>
      <td>the_myth_of_pandoras_box_iseult_gillespie</td>
      <td>10.9M</td>
      <td>293M</td>
      <td>4.73M</td>
      <td>1.58M</td>
      <td>20190115</td>
      <td>4 min 9 s</td>
      <td>366786</td>
    </tr>
    <tr>
      <th>27</th>
      <td>what_would_happen_if_you_didnt_drink_water_mia...</td>
      <td>8.75M</td>
      <td>302M</td>
      <td>9.38M</td>
      <td>1.56M</td>
      <td>20160329</td>
      <td>4 min 51 s</td>
      <td>251579</td>
    </tr>
    <tr>
      <th>28</th>
      <td>what_would_happen_if_you_didnt_sleep_claudia_a...</td>
      <td>7.82M</td>
      <td>310M</td>
      <td>9.24M</td>
      <td>1.54M</td>
      <td>20151112</td>
      <td>4 min 34 s</td>
      <td>238868</td>
    </tr>
    <tr>
      <th>29</th>
      <td>can_you_solve_the_locker_riddle_lisa_winer</td>
      <td>6.77M</td>
      <td>316M</td>
      <td>9.20M</td>
      <td>1.53M</td>
      <td>20160328</td>
      <td>3 min 49 s</td>
      <td>247586</td>
    </tr>
    <tr>
      <th>30</th>
      <td>the_myth_of_sisyphus_alex_gendler</td>
      <td>9.76M</td>
      <td>326M</td>
      <td>4.48M</td>
      <td>1.49M</td>
      <td>20181113</td>
      <td>4 min 56 s</td>
      <td>275698</td>
    </tr>
    <tr>
      <th>31</th>
      <td>can_you_solve_the_pirate_riddle_alex_gendler</td>
      <td>9.00M</td>
      <td>335M</td>
      <td>7.46M</td>
      <td>1.49M</td>
      <td>20170501</td>
      <td>5 min 23 s</td>
      <td>233364</td>
    </tr>
    <tr>
      <th>32</th>
      <td>how_your_digestive_system_works_emma_bryce</td>
      <td>6.85M</td>
      <td>342M</td>
      <td>5.85M</td>
      <td>1.46M</td>
      <td>20171214</td>
      <td>4 min 56 s</td>
      <td>193787</td>
    </tr>
    <tr>
      <th>33</th>
      <td>the_myth_of_cupid_and_psyche_brendan_pelsue</td>
      <td>16.4M</td>
      <td>358M</td>
      <td>7.31M</td>
      <td>1.46M</td>
      <td>20170803</td>
      <td>5 min 32 s</td>
      <td>414573</td>
    </tr>
    <tr>
      <th>34</th>
      <td>what_really_happened_during_the_salem_witch_tr...</td>
      <td>10.1M</td>
      <td>368M</td>
      <td>2.92M</td>
      <td>1.46M</td>
      <td>20200504</td>
      <td>5 min 30 s</td>
      <td>257018</td>
    </tr>
    <tr>
      <th>35</th>
      <td>the_loathsome_lethal_mosquito_rose_eveleth</td>
      <td>4.87M</td>
      <td>373M</td>
      <td>11.6M</td>
      <td>1.45M</td>
      <td>20131202</td>
      <td>2 min 39 s</td>
      <td>255716</td>
    </tr>
    <tr>
      <th>36</th>
      <td>which_is_better_soap_or_hand_sanitizer_alex_ro...</td>
      <td>14.0M</td>
      <td>387M</td>
      <td>2.90M</td>
      <td>1.45M</td>
      <td>20200505</td>
      <td>6 min 14 s</td>
      <td>313038</td>
    </tr>
    <tr>
      <th>37</th>
      <td>does_time_exist_andrew_zimmerman_jones</td>
      <td>15.1M</td>
      <td>402M</td>
      <td>4.33M</td>
      <td>1.44M</td>
      <td>20181023</td>
      <td>5 min 15 s</td>
      <td>401662</td>
    </tr>
    <tr>
      <th>38</th>
      <td>how_the_food_you_eat_affects_your_brain_mia_na...</td>
      <td>14.6M</td>
      <td>417M</td>
      <td>8.64M</td>
      <td>1.44M</td>
      <td>20160621</td>
      <td>4 min 52 s</td>
      <td>418643</td>
    </tr>
    <tr>
      <th>39</th>
      <td>the_myth_of_hercules_12_labors_in_8_bits_alex_...</td>
      <td>23.8M</td>
      <td>441M</td>
      <td>4.30M</td>
      <td>1.43M</td>
      <td>20180925</td>
      <td>7 min 50 s</td>
      <td>423995</td>
    </tr>
    <tr>
      <th>40</th>
      <td>can_you_solve_the_unstoppable_blob_riddle_dan_...</td>
      <td>5.70M</td>
      <td>447M</td>
      <td>4.28M</td>
      <td>1.43M</td>
      <td>20190318</td>
      <td>3 min 42 s</td>
      <td>215233</td>
    </tr>
    <tr>
      <th>41</th>
      <td>the_myth_of_thor_s_journey_to_the_land_of_gian...</td>
      <td>7.63M</td>
      <td>454M</td>
      <td>5.69M</td>
      <td>1.42M</td>
      <td>20180222</td>
      <td>5 min 17 s</td>
      <td>201517</td>
    </tr>
    <tr>
      <th>42</th>
      <td>a_brief_history_of_chess_alex_gendler</td>
      <td>9.53M</td>
      <td>464M</td>
      <td>4.26M</td>
      <td>1.42M</td>
      <td>20190912</td>
      <td>5 min 39 s</td>
      <td>235364</td>
    </tr>
    <tr>
      <th>43</th>
      <td>why_do_cats_act_so_weird_tony_buffington</td>
      <td>11.9M</td>
      <td>476M</td>
      <td>8.42M</td>
      <td>1.40M</td>
      <td>20160426</td>
      <td>4 min 57 s</td>
      <td>335884</td>
    </tr>
    <tr>
      <th>44</th>
      <td>when_is_a_pandemic_over</td>
      <td>15.3M</td>
      <td>491M</td>
      <td>2.80M</td>
      <td>1.40M</td>
      <td>20200601</td>
      <td>5 min 52 s</td>
      <td>364654</td>
    </tr>
    <tr>
      <th>45</th>
      <td>the_myth_of_prometheus_iseult_gillespie</td>
      <td>8.23M</td>
      <td>499M</td>
      <td>5.57M</td>
      <td>1.39M</td>
      <td>20171114</td>
      <td>4 min 46 s</td>
      <td>240890</td>
    </tr>
    <tr>
      <th>46</th>
      <td>why_can_t_you_divide_by_zero_ted_ed</td>
      <td>7.70M</td>
      <td>507M</td>
      <td>5.56M</td>
      <td>1.39M</td>
      <td>20180423</td>
      <td>4 min 50 s</td>
      <td>222058</td>
    </tr>
    <tr>
      <th>47</th>
      <td>a_brief_history_of_alcohol_rod_phillips</td>
      <td>8.92M</td>
      <td>516M</td>
      <td>2.76M</td>
      <td>1.38M</td>
      <td>20200102</td>
      <td>5 min 20 s</td>
      <td>233540</td>
    </tr>
    <tr>
      <th>48</th>
      <td>who_were_the_vestal_virgins_and_what_was_their...</td>
      <td>12.8M</td>
      <td>529M</td>
      <td>6.85M</td>
      <td>1.37M</td>
      <td>20170530</td>
      <td>4 min 32 s</td>
      <td>394672</td>
    </tr>
    <tr>
      <th>49</th>
      <td>the_tragic_myth_of_orpheus_and_eurydice_brenda...</td>
      <td>7.92M</td>
      <td>537M</td>
      <td>5.43M</td>
      <td>1.36M</td>
      <td>20180111</td>
      <td>4 min 41 s</td>
      <td>236402</td>
    </tr>
    <tr>
      <th>50</th>
      <td>einstein_s_twin_paradox_explained_amber_stuver</td>
      <td>11.7M</td>
      <td>548M</td>
      <td>2.71M</td>
      <td>1.36M</td>
      <td>20190926</td>
      <td>6 min 15 s</td>
      <td>262501</td>
    </tr>
    <tr>
      <th>51</th>
      <td>can_you_solve_the_temple_riddle_dennis_e_shasha</td>
      <td>6.70M</td>
      <td>555M</td>
      <td>8.12M</td>
      <td>1.35M</td>
      <td>20160201</td>
      <td>4 min 12 s</td>
      <td>222307</td>
    </tr>
    <tr>
      <th>52</th>
      <td>can_you_solve_the_egg_drop_riddle_yossi_elran</td>
      <td>8.41M</td>
      <td>563M</td>
      <td>5.38M</td>
      <td>1.34M</td>
      <td>20171107</td>
      <td>4 min 46 s</td>
      <td>246132</td>
    </tr>
    <tr>
      <th>53</th>
      <td>the_tale_of_the_boy_who_tricked_the_devil_iseu...</td>
      <td>17.9M</td>
      <td>581M</td>
      <td>2.69M</td>
      <td>1.34M</td>
      <td>20200707</td>
      <td>5 min 25 s</td>
      <td>461178</td>
    </tr>
    <tr>
      <th>54</th>
      <td>what_happens_to_our_bodies_after_we_die_farnaz...</td>
      <td>8.41M</td>
      <td>590M</td>
      <td>6.66M</td>
      <td>1.33M</td>
      <td>20161013</td>
      <td>4 min 40 s</td>
      <td>251430</td>
    </tr>
    <tr>
      <th>55</th>
      <td>can_you_solve_the_counterfeit_coin_riddle_jenn...</td>
      <td>9.45M</td>
      <td>599M</td>
      <td>6.66M</td>
      <td>1.33M</td>
      <td>20170103</td>
      <td>4 min 34 s</td>
      <td>289009</td>
    </tr>
    <tr>
      <th>56</th>
      <td>the_chinese_myth_of_the_immortal_white_snake_s...</td>
      <td>7.80M</td>
      <td>607M</td>
      <td>3.96M</td>
      <td>1.32M</td>
      <td>20190507</td>
      <td>4 min 0 s</td>
      <td>272051</td>
    </tr>
    <tr>
      <th>57</th>
      <td>how_does_alcohol_make_you_drunk_judy_grisel</td>
      <td>8.19M</td>
      <td>615M</td>
      <td>2.62M</td>
      <td>1.31M</td>
      <td>20200409</td>
      <td>5 min 25 s</td>
      <td>210996</td>
    </tr>
    <tr>
      <th>58</th>
      <td>how_does_anesthesia_work_steven_zheng</td>
      <td>8.05M</td>
      <td>623M</td>
      <td>7.82M</td>
      <td>1.30M</td>
      <td>20151207</td>
      <td>4 min 55 s</td>
      <td>228275</td>
    </tr>
    <tr>
      <th>59</th>
      <td>the_benefits_of_a_bilingual_brain_mia_nacamulli</td>
      <td>11.5M</td>
      <td>635M</td>
      <td>9.09M</td>
      <td>1.30M</td>
      <td>20150623</td>
      <td>5 min 3 s</td>
      <td>316540</td>
    </tr>
    <tr>
      <th>60</th>
      <td>which_type_of_milk_is_best_for_you_jonathan_j_...</td>
      <td>19.1M</td>
      <td>654M</td>
      <td>1.28M</td>
      <td>1.28M</td>
      <td>20201020</td>
      <td>5 min 25 s</td>
      <td>490630</td>
    </tr>
    <tr>
      <th>61</th>
      <td>the_myth_of_king_midas_and_his_golden_touch_is...</td>
      <td>16.3M</td>
      <td>670M</td>
      <td>5.03M</td>
      <td>1.26M</td>
      <td>20180305</td>
      <td>5 min 4 s</td>
      <td>448247</td>
    </tr>
    <tr>
      <th>62</th>
      <td>can_you_solve_the_passcode_riddle_ganesh_pai</td>
      <td>7.16M</td>
      <td>677M</td>
      <td>7.48M</td>
      <td>1.25M</td>
      <td>20160707</td>
      <td>4 min 7 s</td>
      <td>242297</td>
    </tr>
    <tr>
      <th>63</th>
      <td>how_does_the_rorschach_inkblot_test_work_damio...</td>
      <td>12.9M</td>
      <td>690M</td>
      <td>3.71M</td>
      <td>1.24M</td>
      <td>20190305</td>
      <td>4 min 57 s</td>
      <td>364256</td>
    </tr>
    <tr>
      <th>64</th>
      <td>how_sugar_affects_the_brain_nicole_avena</td>
      <td>16.5M</td>
      <td>707M</td>
      <td>9.83M</td>
      <td>1.23M</td>
      <td>20140107</td>
      <td>5 min 2 s</td>
      <td>457297</td>
    </tr>
    <tr>
      <th>65</th>
      <td>why_doesnt_the_leaning_tower_of_pisa_fall_over...</td>
      <td>9.48M</td>
      <td>716M</td>
      <td>2.45M</td>
      <td>1.22M</td>
      <td>20191203</td>
      <td>5 min 5 s</td>
      <td>260234</td>
    </tr>
    <tr>
      <th>66</th>
      <td>the_history_of_the_world_according_to_cats_eva...</td>
      <td>11.9M</td>
      <td>728M</td>
      <td>3.67M</td>
      <td>1.22M</td>
      <td>20190103</td>
      <td>4 min 34 s</td>
      <td>365181</td>
    </tr>
    <tr>
      <th>67</th>
      <td>cannibalism_in_the_animal_kingdom_bill_schutt</td>
      <td>9.64M</td>
      <td>738M</td>
      <td>4.89M</td>
      <td>1.22M</td>
      <td>20180319</td>
      <td>4 min 57 s</td>
      <td>271969</td>
    </tr>
    <tr>
      <th>68</th>
      <td>the_psychology_of_narcissism_w_keith_campbell</td>
      <td>8.95M</td>
      <td>747M</td>
      <td>7.33M</td>
      <td>1.22M</td>
      <td>20160223</td>
      <td>5 min 9 s</td>
      <td>242921</td>
    </tr>
    <tr>
      <th>69</th>
      <td>mating_frenzies_sperm_hoards_and_brood_raids_t...</td>
      <td>12.0M</td>
      <td>759M</td>
      <td>2.35M</td>
      <td>1.17M</td>
      <td>20200116</td>
      <td>5 min 18 s</td>
      <td>315691</td>
    </tr>
    <tr>
      <th>70</th>
      <td>how_playing_an_instrument_benefits_your_brain_...</td>
      <td>8.59M</td>
      <td>767M</td>
      <td>9.14M</td>
      <td>1.14M</td>
      <td>20140722</td>
      <td>4 min 44 s</td>
      <td>252935</td>
    </tr>
    <tr>
      <th>71</th>
      <td>the_rise_and_fall_of_the_berlin_wall_konrad_h_...</td>
      <td>9.52M</td>
      <td>777M</td>
      <td>5.70M</td>
      <td>1.14M</td>
      <td>20170816</td>
      <td>6 min 25 s</td>
      <td>207028</td>
    </tr>
    <tr>
      <th>72</th>
      <td>how_does_a_jellyfish_sting_neosha_s_kashef</td>
      <td>7.51M</td>
      <td>784M</td>
      <td>7.97M</td>
      <td>1.14M</td>
      <td>20150810</td>
      <td>4 min 16 s</td>
      <td>246040</td>
    </tr>
    <tr>
      <th>73</th>
      <td>what_if_there_were_1_trillion_more_trees_jean_...</td>
      <td>24.6M</td>
      <td>809M</td>
      <td>1.14M</td>
      <td>1.14M</td>
      <td>20201027</td>
      <td>5 min 43 s</td>
      <td>600935</td>
    </tr>
    <tr>
      <th>74</th>
      <td>how_does_the_stock_market_work_oliver_elfenbaum</td>
      <td>9.18M</td>
      <td>818M</td>
      <td>3.41M</td>
      <td>1.14M</td>
      <td>20190429</td>
      <td>4 min 29 s</td>
      <td>285826</td>
    </tr>
    <tr>
      <th>75</th>
      <td>5_tips_to_improve_your_critical_thinking_saman...</td>
      <td>6.79M</td>
      <td>825M</td>
      <td>6.82M</td>
      <td>1.14M</td>
      <td>20160315</td>
      <td>4 min 29 s</td>
      <td>210868</td>
    </tr>
    <tr>
      <th>76</th>
      <td>from_slave_to_rebel_gladiator_the_life_of_spar...</td>
      <td>19.2M</td>
      <td>844M</td>
      <td>3.40M</td>
      <td>1.13M</td>
      <td>20181217</td>
      <td>5 min 15 s</td>
      <td>510502</td>
    </tr>
    <tr>
      <th>77</th>
      <td>the_benefits_of_good_posture_murat_dalkilinc</td>
      <td>5.78M</td>
      <td>850M</td>
      <td>7.89M</td>
      <td>1.13M</td>
      <td>20150730</td>
      <td>4 min 26 s</td>
      <td>181845</td>
    </tr>
    <tr>
      <th>78</th>
      <td>what_is_depression_helen_m_farrell</td>
      <td>7.12M</td>
      <td>857M</td>
      <td>6.74M</td>
      <td>1.12M</td>
      <td>20151215</td>
      <td>4 min 28 s</td>
      <td>222220</td>
    </tr>
    <tr>
      <th>79</th>
      <td>how_did_hitler_rise_to_power_alex_gendler_and_...</td>
      <td>11.7M</td>
      <td>869M</td>
      <td>6.73M</td>
      <td>1.12M</td>
      <td>20160718</td>
      <td>5 min 36 s</td>
      <td>291419</td>
    </tr>
    <tr>
      <th>80</th>
      <td>a_glimpse_of_teenage_life_in_ancient_rome_ray_...</td>
      <td>15.9M</td>
      <td>884M</td>
      <td>10.1M</td>
      <td>1.12M</td>
      <td>20121029</td>
      <td>6 min 34 s</td>
      <td>338988</td>
    </tr>
    <tr>
      <th>81</th>
      <td>the_worlds_most_mysterious_book_stephen_bax</td>
      <td>9.37M</td>
      <td>894M</td>
      <td>5.58M</td>
      <td>1.12M</td>
      <td>20170525</td>
      <td>4 min 42 s</td>
      <td>277935</td>
    </tr>
    <tr>
      <th>82</th>
      <td>3_tips_to_boost_your_confidence_ted_ed</td>
      <td>9.28M</td>
      <td>903M</td>
      <td>6.66M</td>
      <td>1.11M</td>
      <td>20151006</td>
      <td>4 min 16 s</td>
      <td>303550</td>
    </tr>
    <tr>
      <th>83</th>
      <td>can_you_solve_the_frog_riddle_derek_abbott</td>
      <td>6.91M</td>
      <td>910M</td>
      <td>6.61M</td>
      <td>1.10M</td>
      <td>20160229</td>
      <td>4 min 30 s</td>
      <td>214519</td>
    </tr>
    <tr>
      <th>84</th>
      <td>the_unexpected_math_behind_van_gogh_s_starry_n...</td>
      <td>14.7M</td>
      <td>925M</td>
      <td>7.69M</td>
      <td>1.10M</td>
      <td>20141030</td>
      <td>4 min 38 s</td>
      <td>442796</td>
    </tr>
    <tr>
      <th>85</th>
      <td>the_myth_of_icarus_and_daedalus_amy_adkins</td>
      <td>15.2M</td>
      <td>940M</td>
      <td>5.47M</td>
      <td>1.09M</td>
      <td>20170313</td>
      <td>5 min 8 s</td>
      <td>412881</td>
    </tr>
    <tr>
      <th>86</th>
      <td>a_day_in_the_life_of_an_ancient_egyptian_docto...</td>
      <td>7.03M</td>
      <td>947M</td>
      <td>4.35M</td>
      <td>1.09M</td>
      <td>20180719</td>
      <td>4 min 33 s</td>
      <td>215513</td>
    </tr>
    <tr>
      <th>87</th>
      <td>the_myth_behind_the_chinese_zodiac_megan_campi...</td>
      <td>6.53M</td>
      <td>953M</td>
      <td>5.42M</td>
      <td>1.08M</td>
      <td>20170126</td>
      <td>4 min 22 s</td>
      <td>208587</td>
    </tr>
    <tr>
      <th>88</th>
      <td>the_atlantic_slave_trade_what_too_few_textbook...</td>
      <td>10.8M</td>
      <td>964M</td>
      <td>7.55M</td>
      <td>1.08M</td>
      <td>20141222</td>
      <td>5 min 38 s</td>
      <td>268910</td>
    </tr>
    <tr>
      <th>89</th>
      <td>the_philosophy_of_stoicism_massimo_pigliucci</td>
      <td>10.3M</td>
      <td>975M</td>
      <td>5.38M</td>
      <td>1.08M</td>
      <td>20170619</td>
      <td>5 min 29 s</td>
      <td>263369</td>
    </tr>
    <tr>
      <th>90</th>
      <td>historys_deadliest_colors_j_v_maranto</td>
      <td>14.5M</td>
      <td>989M</td>
      <td>5.36M</td>
      <td>1.07M</td>
      <td>20170522</td>
      <td>5 min 13 s</td>
      <td>388236</td>
    </tr>
    <tr>
      <th>91</th>
      <td>how_to_spot_a_pyramid_scheme_stacie_bosley</td>
      <td>7.23M</td>
      <td>996M</td>
      <td>3.20M</td>
      <td>1.07M</td>
      <td>20190402</td>
      <td>5 min 1 s</td>
      <td>201096</td>
    </tr>
    <tr>
      <th>92</th>
      <td>are_the_illuminati_real_chip_berlet</td>
      <td>7.43M</td>
      <td>0.98G</td>
      <td>2.11M</td>
      <td>1.05M</td>
      <td>20191031</td>
      <td>4 min 57 s</td>
      <td>209406</td>
    </tr>
    <tr>
      <th>93</th>
      <td>can_you_solve_the_river_crossing_riddle_lisa_w...</td>
      <td>8.29M</td>
      <td>0.99G</td>
      <td>5.16M</td>
      <td>1.03M</td>
      <td>20161101</td>
      <td>4 min 18 s</td>
      <td>269439</td>
    </tr>
    <tr>
      <th>94</th>
      <td>what_is_schizophrenia_anees_bahji</td>
      <td>10.5M</td>
      <td>1.00G</td>
      <td>2.06M</td>
      <td>1.03M</td>
      <td>20200326</td>
      <td>5 min 32 s</td>
      <td>263947</td>
    </tr>
    <tr>
      <th>95</th>
      <td>is_life_meaningless_and_other_absurd_questions...</td>
      <td>18.8M</td>
      <td>1.02G</td>
      <td>1.02M</td>
      <td>1.02M</td>
      <td>20200921</td>
      <td>6 min 12 s</td>
      <td>424156</td>
    </tr>
    <tr>
      <th>96</th>
      <td>can_you_solve_the_airplane_riddle_judd_a_schorr</td>
      <td>9.30M</td>
      <td>1.03G</td>
      <td>5.09M</td>
      <td>1.02M</td>
      <td>20161201</td>
      <td>4 min 37 s</td>
      <td>281440</td>
    </tr>
    <tr>
      <th>97</th>
      <td>the_history_of_chocolate_deanna_pucciarelli</td>
      <td>8.67M</td>
      <td>1.03G</td>
      <td>5.07M</td>
      <td>1.01M</td>
      <td>20170316</td>
      <td>4 min 40 s</td>
      <td>259184</td>
    </tr>
    <tr>
      <th>98</th>
      <td>hawking_s_black_hole_paradox_explained_fabio_p...</td>
      <td>11.2M</td>
      <td>1.05G</td>
      <td>2.00M</td>
      <td>1.00M</td>
      <td>20191022</td>
      <td>5 min 37 s</td>
      <td>277718</td>
    </tr>
    <tr>
      <th>99</th>
      <td>can_you_solve_the_ragnarok_riddle_dan_finkel</td>
      <td>22.4M</td>
      <td>1.07G</td>
      <td>1.99M</td>
      <td>0.99M</td>
      <td>20200630</td>
      <td>5 min 14 s</td>
      <td>596885</td>
    </tr>
    <tr>
      <th>100</th>
      <td>the_legend_of_annapurna_hindu_goddess_of_nouri...</td>
      <td>8.40M</td>
      <td>1.08G</td>
      <td>1.97M</td>
      <td>0.98M</td>
      <td>20200213</td>
      <td>5 min 8 s</td>
      <td>228237</td>
    </tr>
    <tr>
      <th>101</th>
      <td>the_bug_that_poops_candy_george_zaidan</td>
      <td>14.1M</td>
      <td>1.09G</td>
      <td>1.95M</td>
      <td>999K</td>
      <td>20200414</td>
      <td>4 min 46 s</td>
      <td>411775</td>
    </tr>
    <tr>
      <th>102</th>
      <td>why_do_women_have_periods</td>
      <td>7.05M</td>
      <td>1.10G</td>
      <td>5.86M</td>
      <td>999K</td>
      <td>20151019</td>
      <td>4 min 45 s</td>
      <td>207328</td>
    </tr>
    <tr>
      <th>103</th>
      <td>why_are_some_people_left_handed_daniel_m_abrams</td>
      <td>8.22M</td>
      <td>1.10G</td>
      <td>6.77M</td>
      <td>990K</td>
      <td>20150203</td>
      <td>5 min 6 s</td>
      <td>224816</td>
    </tr>
    <tr>
      <th>104</th>
      <td>why_do_we_itch_emma_bryce</td>
      <td>13.6M</td>
      <td>1.12G</td>
      <td>4.83M</td>
      <td>988K</td>
      <td>20170411</td>
      <td>4 min 43 s</td>
      <td>401577</td>
    </tr>
    <tr>
      <th>105</th>
      <td>is_human_evolution_speeding_up_or_slowing_down...</td>
      <td>21.1M</td>
      <td>1.14G</td>
      <td>985K</td>
      <td>985K</td>
      <td>20200922</td>
      <td>5 min 47 s</td>
      <td>508012</td>
    </tr>
    <tr>
      <th>106</th>
      <td>can_you_solve_the_penniless_pilgrim_riddle_dan...</td>
      <td>6.60M</td>
      <td>1.14G</td>
      <td>3.84M</td>
      <td>983K</td>
      <td>20180604</td>
      <td>4 min 44 s</td>
      <td>194477</td>
    </tr>
    <tr>
      <th>107</th>
      <td>the_three_different_ways_mammals_give_birth_ka...</td>
      <td>8.55M</td>
      <td>1.15G</td>
      <td>4.77M</td>
      <td>977K</td>
      <td>20170417</td>
      <td>4 min 49 s</td>
      <td>247973</td>
    </tr>
    <tr>
      <th>108</th>
      <td>the_surprising_reason_our_muscles_get_tired_ch...</td>
      <td>10.6M</td>
      <td>1.16G</td>
      <td>2.84M</td>
      <td>971K</td>
      <td>20190418</td>
      <td>4 min 24 s</td>
      <td>335690</td>
    </tr>
    <tr>
      <th>109</th>
      <td>what_makes_something_kafkaesque_noah_tavlin</td>
      <td>19.7M</td>
      <td>1.18G</td>
      <td>5.68M</td>
      <td>970K</td>
      <td>20160620</td>
      <td>5 min 3 s</td>
      <td>542919</td>
    </tr>
    <tr>
      <th>110</th>
      <td>can_you_solve_the_fish_riddle_steve_wyborney</td>
      <td>8.49M</td>
      <td>1.19G</td>
      <td>4.71M</td>
      <td>964K</td>
      <td>20170626</td>
      <td>4 min 49 s</td>
      <td>246020</td>
    </tr>
    <tr>
      <th>111</th>
      <td>how_does_laser_eye_surgery_work_dan_reinstein</td>
      <td>12.1M</td>
      <td>1.20G</td>
      <td>1.87M</td>
      <td>960K</td>
      <td>20191119</td>
      <td>5 min 36 s</td>
      <td>302445</td>
    </tr>
    <tr>
      <th>112</th>
      <td>what_would_happen_if_every_human_suddenly_disa...</td>
      <td>9.30M</td>
      <td>1.21G</td>
      <td>2.77M</td>
      <td>946K</td>
      <td>20180917</td>
      <td>5 min 21 s</td>
      <td>242701</td>
    </tr>
    <tr>
      <th>113</th>
      <td>the_egyptian_book_of_the_dead_a_guidebook_for_...</td>
      <td>7.39M</td>
      <td>1.22G</td>
      <td>4.62M</td>
      <td>945K</td>
      <td>20161031</td>
      <td>4 min 31 s</td>
      <td>228300</td>
    </tr>
    <tr>
      <th>114</th>
      <td>history_vs_cleopatra_alex_gendler</td>
      <td>7.53M</td>
      <td>1.23G</td>
      <td>4.61M</td>
      <td>943K</td>
      <td>20170202</td>
      <td>4 min 27 s</td>
      <td>236257</td>
    </tr>
    <tr>
      <th>115</th>
      <td>the_five_major_world_religions_john_bellaimey</td>
      <td>36.6M</td>
      <td>1.26G</td>
      <td>7.32M</td>
      <td>937K</td>
      <td>20131114</td>
      <td>11 min 9 s</td>
      <td>457821</td>
    </tr>
    <tr>
      <th>116</th>
      <td>how_do_tornadoes_form_james_spann</td>
      <td>8.52M</td>
      <td>1.27G</td>
      <td>7.31M</td>
      <td>936K</td>
      <td>20140819</td>
      <td>4 min 11 s</td>
      <td>283772</td>
    </tr>
    <tr>
      <th>117</th>
      <td>history_through_the_eyes_of_a_chicken_chris_a_...</td>
      <td>14.1M</td>
      <td>1.28G</td>
      <td>2.73M</td>
      <td>932K</td>
      <td>20181011</td>
      <td>5 min 11 s</td>
      <td>379106</td>
    </tr>
    <tr>
      <th>118</th>
      <td>the_dark_history_of_bananas_john_soluri</td>
      <td>17.6M</td>
      <td>1.30G</td>
      <td>925K</td>
      <td>925K</td>
      <td>20201102</td>
      <td>6 min 2 s</td>
      <td>406317</td>
    </tr>
    <tr>
      <th>119</th>
      <td>four_sisters_in_ancient_rome_ray_laurence</td>
      <td>17.2M</td>
      <td>1.32G</td>
      <td>8.04M</td>
      <td>915K</td>
      <td>20130514</td>
      <td>8 min 38 s</td>
      <td>278555</td>
    </tr>
    <tr>
      <th>120</th>
      <td>the_greek_myth_of_talos_the_first_robot_adrien...</td>
      <td>8.36M</td>
      <td>1.33G</td>
      <td>1.79M</td>
      <td>914K</td>
      <td>20191024</td>
      <td>4 min 6 s</td>
      <td>285057</td>
    </tr>
    <tr>
      <th>121</th>
      <td>how_to_manage_your_time_more_effectively_accor...</td>
      <td>7.65M</td>
      <td>1.33G</td>
      <td>3.54M</td>
      <td>906K</td>
      <td>20180102</td>
      <td>5 min 9 s</td>
      <td>206995</td>
    </tr>
    <tr>
      <th>122</th>
      <td>where_does_gold_come_from_david_lunney</td>
      <td>9.66M</td>
      <td>1.34G</td>
      <td>5.23M</td>
      <td>892K</td>
      <td>20151008</td>
      <td>4 min 34 s</td>
      <td>295244</td>
    </tr>
    <tr>
      <th>123</th>
      <td>a_brief_history_of_cannibalism_bill_schutt</td>
      <td>8.18M</td>
      <td>1.35G</td>
      <td>2.60M</td>
      <td>889K</td>
      <td>20190725</td>
      <td>4 min 49 s</td>
      <td>237166</td>
    </tr>
    <tr>
      <th>124</th>
      <td>the_rise_and_fall_of_the_byzantine_empire_leon...</td>
      <td>8.15M</td>
      <td>1.36G</td>
      <td>3.47M</td>
      <td>888K</td>
      <td>20180409</td>
      <td>5 min 20 s</td>
      <td>213168</td>
    </tr>
    <tr>
      <th>125</th>
      <td>why_do_we_dream_amy_adkins</td>
      <td>13.5M</td>
      <td>1.37G</td>
      <td>5.13M</td>
      <td>876K</td>
      <td>20151210</td>
      <td>5 min 37 s</td>
      <td>336435</td>
    </tr>
    <tr>
      <th>126</th>
      <td>the_fascinating_history_of_cemeteries_keith_eg...</td>
      <td>9.83M</td>
      <td>1.38G</td>
      <td>2.57M</td>
      <td>876K</td>
      <td>20181030</td>
      <td>5 min 18 s</td>
      <td>258633</td>
    </tr>
    <tr>
      <th>127</th>
      <td>what_happens_during_a_heart_attack_krishna_sudhir</td>
      <td>8.09M</td>
      <td>1.39G</td>
      <td>4.26M</td>
      <td>873K</td>
      <td>20170214</td>
      <td>4 min 53 s</td>
      <td>231065</td>
    </tr>
    <tr>
      <th>128</th>
      <td>why_sitting_is_bad_for_you_murat_dalkilinc</td>
      <td>8.20M</td>
      <td>1.40G</td>
      <td>5.86M</td>
      <td>858K</td>
      <td>20150305</td>
      <td>5 min 4 s</td>
      <td>225552</td>
    </tr>
    <tr>
      <th>129</th>
      <td>history_vs_che_guevara_alex_gendler</td>
      <td>11.8M</td>
      <td>1.41G</td>
      <td>3.35M</td>
      <td>856K</td>
      <td>20171127</td>
      <td>6 min 7 s</td>
      <td>270019</td>
    </tr>
    <tr>
      <th>130</th>
      <td>why_should_you_read_dune_by_frank_herbert_dan_...</td>
      <td>12.1M</td>
      <td>1.42G</td>
      <td>1.67M</td>
      <td>856K</td>
      <td>20191217</td>
      <td>5 min 5 s</td>
      <td>332203</td>
    </tr>
    <tr>
      <th>131</th>
      <td>how_to_stay_calm_under_pressure_noa_kageyama_a...</td>
      <td>8.06M</td>
      <td>1.43G</td>
      <td>3.33M</td>
      <td>851K</td>
      <td>20180521</td>
      <td>4 min 28 s</td>
      <td>251865</td>
    </tr>
    <tr>
      <th>132</th>
      <td>can_you_solve_the_secret_sauce_riddle_alex_gen...</td>
      <td>7.29M</td>
      <td>1.44G</td>
      <td>1.65M</td>
      <td>847K</td>
      <td>20190916</td>
      <td>4 min 42 s</td>
      <td>216842</td>
    </tr>
    <tr>
      <th>133</th>
      <td>how_does_money_laundering_work_delena_d_spann</td>
      <td>11.9M</td>
      <td>1.45G</td>
      <td>4.10M</td>
      <td>839K</td>
      <td>20170523</td>
      <td>4 min 46 s</td>
      <td>347158</td>
    </tr>
    <tr>
      <th>134</th>
      <td>the_great_conspiracy_against_julius_caesar_kat...</td>
      <td>10.4M</td>
      <td>1.46G</td>
      <td>5.72M</td>
      <td>837K</td>
      <td>20141218</td>
      <td>5 min 57 s</td>
      <td>243912</td>
    </tr>
    <tr>
      <th>135</th>
      <td>mansa_musa_one_of_the_wealthiest_people_who_ev...</td>
      <td>12.4M</td>
      <td>1.47G</td>
      <td>5.72M</td>
      <td>837K</td>
      <td>20150518</td>
      <td>3 min 54 s</td>
      <td>442551</td>
    </tr>
    <tr>
      <th>136</th>
      <td>why_do_animals_have_such_different_lifespans_j...</td>
      <td>7.36M</td>
      <td>1.48G</td>
      <td>4.02M</td>
      <td>823K</td>
      <td>20170404</td>
      <td>4 min 56 s</td>
      <td>208185</td>
    </tr>
    <tr>
      <th>137</th>
      <td>how_tsunamis_work_alex_gendler</td>
      <td>8.95M</td>
      <td>1.49G</td>
      <td>6.41M</td>
      <td>820K</td>
      <td>20140424</td>
      <td>3 min 36 s</td>
      <td>346809</td>
    </tr>
    <tr>
      <th>138</th>
      <td>the_rise_and_fall_of_the_mongol_empire_anne_f_...</td>
      <td>12.1M</td>
      <td>1.50G</td>
      <td>2.39M</td>
      <td>817K</td>
      <td>20190829</td>
      <td>5 min 0 s</td>
      <td>337089</td>
    </tr>
    <tr>
      <th>139</th>
      <td>the_history_of_tea_shunan_teng</td>
      <td>7.57M</td>
      <td>1.50G</td>
      <td>3.98M</td>
      <td>815K</td>
      <td>20170516</td>
      <td>4 min 57 s</td>
      <td>213100</td>
    </tr>
    <tr>
      <th>140</th>
      <td>the_mysterious_life_and_death_of_rasputin_eden...</td>
      <td>8.68M</td>
      <td>1.51G</td>
      <td>1.58M</td>
      <td>810K</td>
      <td>20200107</td>
      <td>5 min 13 s</td>
      <td>232458</td>
    </tr>
    <tr>
      <th>141</th>
      <td>licking_bees_and_pulping_trees_the_reign_of_a_...</td>
      <td>10.9M</td>
      <td>1.52G</td>
      <td>1.58M</td>
      <td>809K</td>
      <td>20200128</td>
      <td>5 min 22 s</td>
      <td>285109</td>
    </tr>
    <tr>
      <th>142</th>
      <td>why_are_sloths_so_slow_kenny_coogan</td>
      <td>7.71M</td>
      <td>1.53G</td>
      <td>3.95M</td>
      <td>809K</td>
      <td>20170425</td>
      <td>5 min 14 s</td>
      <td>205509</td>
    </tr>
    <tr>
      <th>143</th>
      <td>can_you_solve_the_stolen_rubies_riddle_dennis_...</td>
      <td>10.1M</td>
      <td>1.54G</td>
      <td>2.36M</td>
      <td>805K</td>
      <td>20181025</td>
      <td>4 min 50 s</td>
      <td>291487</td>
    </tr>
    <tr>
      <th>144</th>
      <td>why_isn_t_the_world_covered_in_poop_eleanor_sl...</td>
      <td>7.34M</td>
      <td>1.55G</td>
      <td>3.10M</td>
      <td>793K</td>
      <td>20180326</td>
      <td>4 min 57 s</td>
      <td>206978</td>
    </tr>
    <tr>
      <th>145</th>
      <td>what_makes_a_hero_matthew_winkler</td>
      <td>11.4M</td>
      <td>1.56G</td>
      <td>6.93M</td>
      <td>789K</td>
      <td>20121204</td>
      <td>4 min 33 s</td>
      <td>349729</td>
    </tr>
    <tr>
      <th>146</th>
      <td>the_cambodian_myth_of_lightning_thunder_and_ra...</td>
      <td>11.6M</td>
      <td>1.57G</td>
      <td>3.07M</td>
      <td>785K</td>
      <td>20180410</td>
      <td>4 min 37 s</td>
      <td>350555</td>
    </tr>
    <tr>
      <th>147</th>
      <td>how_does_asthma_work_christopher_e_gaw</td>
      <td>8.91M</td>
      <td>1.58G</td>
      <td>3.83M</td>
      <td>785K</td>
      <td>20170511</td>
      <td>5 min 9 s</td>
      <td>241743</td>
    </tr>
    <tr>
      <th>148</th>
      <td>meet_the_tardigrade_the_toughest_animal_on_ear...</td>
      <td>7.11M</td>
      <td>1.59G</td>
      <td>3.82M</td>
      <td>783K</td>
      <td>20170321</td>
      <td>4 min 9 s</td>
      <td>239330</td>
    </tr>
    <tr>
      <th>149</th>
      <td>can_you_solve_the_control_room_riddle_dennis_s...</td>
      <td>6.73M</td>
      <td>1.59G</td>
      <td>4.58M</td>
      <td>781K</td>
      <td>20160531</td>
      <td>4 min 0 s</td>
      <td>234752</td>
    </tr>
    <tr>
      <th>150</th>
      <td>can_you_solve_the_dragon_jousting_riddle_alex_...</td>
      <td>9.13M</td>
      <td>1.60G</td>
      <td>1.51M</td>
      <td>771K</td>
      <td>20200109</td>
      <td>5 min 3 s</td>
      <td>252744</td>
    </tr>
    <tr>
      <th>151</th>
      <td>whats_that_ringing_in_your_ears_marc_fagelson</td>
      <td>22.4M</td>
      <td>1.62G</td>
      <td>1.50M</td>
      <td>770K</td>
      <td>20200817</td>
      <td>5 min 38 s</td>
      <td>553928</td>
    </tr>
    <tr>
      <th>152</th>
      <td>why_the_metric_system_matters_matt_anticole</td>
      <td>7.17M</td>
      <td>1.63G</td>
      <td>4.51M</td>
      <td>770K</td>
      <td>20160721</td>
      <td>5 min 7 s</td>
      <td>195807</td>
    </tr>
    <tr>
      <th>153</th>
      <td>schrodinger_s_cat_a_thought_experiment_in_quan...</td>
      <td>6.93M</td>
      <td>1.64G</td>
      <td>5.25M</td>
      <td>768K</td>
      <td>20141014</td>
      <td>4 min 37 s</td>
      <td>209453</td>
    </tr>
    <tr>
      <th>154</th>
      <td>can_you_solve_the_dark_coin_riddle_lisa_winer</td>
      <td>9.85M</td>
      <td>1.65G</td>
      <td>3.00M</td>
      <td>768K</td>
      <td>20180122</td>
      <td>5 min 25 s</td>
      <td>253715</td>
    </tr>
    <tr>
      <th>155</th>
      <td>can_you_solve_the_seven_planets_riddle_edwin_f...</td>
      <td>9.29M</td>
      <td>1.66G</td>
      <td>2.98M</td>
      <td>762K</td>
      <td>20180226</td>
      <td>6 min 0 s</td>
      <td>215979</td>
    </tr>
    <tr>
      <th>156</th>
      <td>what_makes_the_great_wall_of_china_so_extraord...</td>
      <td>6.95M</td>
      <td>1.66G</td>
      <td>4.45M</td>
      <td>759K</td>
      <td>20150917</td>
      <td>4 min 29 s</td>
      <td>216424</td>
    </tr>
    <tr>
      <th>157</th>
      <td>the_myth_of_loki_and_the_deadly_mistletoe_iseu...</td>
      <td>22.2M</td>
      <td>1.68G</td>
      <td>756K</td>
      <td>756K</td>
      <td>20201201</td>
      <td>5 min 28 s</td>
      <td>565703</td>
    </tr>
    <tr>
      <th>158</th>
      <td>what_causes_headaches_dan_kwartler</td>
      <td>9.18M</td>
      <td>1.69G</td>
      <td>2.94M</td>
      <td>754K</td>
      <td>20180412</td>
      <td>5 min 31 s</td>
      <td>232353</td>
    </tr>
    <tr>
      <th>159</th>
      <td>can_you_solve_the_multiplying_rabbits_riddle_a...</td>
      <td>7.66M</td>
      <td>1.70G</td>
      <td>2.20M</td>
      <td>752K</td>
      <td>20190110</td>
      <td>4 min 38 s</td>
      <td>230780</td>
    </tr>
    <tr>
      <th>160</th>
      <td>why_is_it_so_hard_to_cure_cancer_kyuson_yun</td>
      <td>14.5M</td>
      <td>1.72G</td>
      <td>2.91M</td>
      <td>746K</td>
      <td>20171010</td>
      <td>5 min 22 s</td>
      <td>377318</td>
    </tr>
    <tr>
      <th>161</th>
      <td>why_do_people_join_cults_janja_lalich</td>
      <td>12.4M</td>
      <td>1.73G</td>
      <td>3.63M</td>
      <td>744K</td>
      <td>20170612</td>
      <td>6 min 26 s</td>
      <td>269558</td>
    </tr>
    <tr>
      <th>162</th>
      <td>can_you_solve_the_secret_werewolf_riddle_dan_f...</td>
      <td>7.43M</td>
      <td>1.73G</td>
      <td>2.18M</td>
      <td>744K</td>
      <td>20181108</td>
      <td>4 min 28 s</td>
      <td>231813</td>
    </tr>
    <tr>
      <th>163</th>
      <td>the_wars_that_inspired_game_of_thrones_alex_ge...</td>
      <td>11.0M</td>
      <td>1.75G</td>
      <td>5.07M</td>
      <td>741K</td>
      <td>20150511</td>
      <td>6 min 0 s</td>
      <td>256213</td>
    </tr>
    <tr>
      <th>164</th>
      <td>can_you_solve_the_leonardo_da_vinci_riddle_tan...</td>
      <td>7.97M</td>
      <td>1.75G</td>
      <td>2.89M</td>
      <td>741K</td>
      <td>20180823</td>
      <td>5 min 7 s</td>
      <td>217113</td>
    </tr>
    <tr>
      <th>165</th>
      <td>why_do_we_cry_the_three_types_of_tears_alex_ge...</td>
      <td>7.77M</td>
      <td>1.76G</td>
      <td>5.74M</td>
      <td>734K</td>
      <td>20140226</td>
      <td>3 min 58 s</td>
      <td>273566</td>
    </tr>
    <tr>
      <th>166</th>
      <td>does_your_vote_count_the_electoral_college_exp...</td>
      <td>11.1M</td>
      <td>1.77G</td>
      <td>6.44M</td>
      <td>732K</td>
      <td>20121101</td>
      <td>5 min 21 s</td>
      <td>289045</td>
    </tr>
    <tr>
      <th>167</th>
      <td>can_you_solve_the_jail_break_riddle_dan_finkel</td>
      <td>7.25M</td>
      <td>1.78G</td>
      <td>2.14M</td>
      <td>732K</td>
      <td>20190226</td>
      <td>3 min 24 s</td>
      <td>297630</td>
    </tr>
    <tr>
      <th>168</th>
      <td>how_we_conquered_the_deadly_smallpox_virus_sim...</td>
      <td>9.12M</td>
      <td>1.79G</td>
      <td>5.66M</td>
      <td>725K</td>
      <td>20131028</td>
      <td>4 min 33 s</td>
      <td>279453</td>
    </tr>
    <tr>
      <th>169</th>
      <td>the_japanese_folktale_of_the_selfish_scholar_i...</td>
      <td>14.7M</td>
      <td>1.80G</td>
      <td>724K</td>
      <td>724K</td>
      <td>20200914</td>
      <td>4 min 59 s</td>
      <td>410348</td>
    </tr>
    <tr>
      <th>170</th>
      <td>would_you_sacrifice_one_person_to_save_five_el...</td>
      <td>7.06M</td>
      <td>1.81G</td>
      <td>3.52M</td>
      <td>721K</td>
      <td>20170112</td>
      <td>4 min 55 s</td>
      <td>200237</td>
    </tr>
    <tr>
      <th>171</th>
      <td>what_causes_kidney_stones_arash_shadman</td>
      <td>6.68M</td>
      <td>1.82G</td>
      <td>3.51M</td>
      <td>719K</td>
      <td>20170703</td>
      <td>5 min 14 s</td>
      <td>178090</td>
    </tr>
    <tr>
      <th>172</th>
      <td>how_the_world_s_longest_underwater_tunnel_was_...</td>
      <td>9.61M</td>
      <td>1.83G</td>
      <td>1.40M</td>
      <td>717K</td>
      <td>20200330</td>
      <td>5 min 37 s</td>
      <td>238742</td>
    </tr>
    <tr>
      <th>173</th>
      <td>why_is_vermeer_s_girl_with_the_pearl_earring_c...</td>
      <td>8.37M</td>
      <td>1.83G</td>
      <td>3.50M</td>
      <td>716K</td>
      <td>20161018</td>
      <td>4 min 33 s</td>
      <td>256329</td>
    </tr>
    <tr>
      <th>174</th>
      <td>how_do_solar_panels_work_richard_komp</td>
      <td>7.14M</td>
      <td>1.84G</td>
      <td>4.17M</td>
      <td>712K</td>
      <td>20160105</td>
      <td>4 min 58 s</td>
      <td>200564</td>
    </tr>
    <tr>
      <th>175</th>
      <td>why_the_octopus_brain_is_so_extraordinary_clau...</td>
      <td>7.17M</td>
      <td>1.85G</td>
      <td>4.17M</td>
      <td>711K</td>
      <td>20151203</td>
      <td>4 min 16 s</td>
      <td>234624</td>
    </tr>
    <tr>
      <th>176</th>
      <td>what_causes_cavities_mel_rosenberg</td>
      <td>9.96M</td>
      <td>1.86G</td>
      <td>3.46M</td>
      <td>708K</td>
      <td>20161017</td>
      <td>5 min 0 s</td>
      <td>278404</td>
    </tr>
    <tr>
      <th>177</th>
      <td>the_greatest_mathematician_that_never_lived_pr...</td>
      <td>16.1M</td>
      <td>1.87G</td>
      <td>1.38M</td>
      <td>707K</td>
      <td>20200706</td>
      <td>5 min 12 s</td>
      <td>432858</td>
    </tr>
    <tr>
      <th>178</th>
      <td>what_is_bipolar_disorder_helen_m_farrell</td>
      <td>8.08M</td>
      <td>1.88G</td>
      <td>3.44M</td>
      <td>704K</td>
      <td>20170209</td>
      <td>5 min 57 s</td>
      <td>189243</td>
    </tr>
    <tr>
      <th>179</th>
      <td>can_you_solve_the_riddle_and_escape_hades_dan_...</td>
      <td>15.3M</td>
      <td>1.90G</td>
      <td>702K</td>
      <td>702K</td>
      <td>20201013</td>
      <td>4 min 59 s</td>
      <td>429178</td>
    </tr>
    <tr>
      <th>180</th>
      <td>can_you_solve_the_sea_monster_riddle_dan_finkel</td>
      <td>12.4M</td>
      <td>1.91G</td>
      <td>1.37M</td>
      <td>701K</td>
      <td>20200402</td>
      <td>5 min 27 s</td>
      <td>316868</td>
    </tr>
    <tr>
      <th>181</th>
      <td>can_you_solve_the_false_positive_riddle_alex_g...</td>
      <td>10.4M</td>
      <td>1.92G</td>
      <td>2.73M</td>
      <td>699K</td>
      <td>20180508</td>
      <td>5 min 19 s</td>
      <td>273022</td>
    </tr>
    <tr>
      <th>182</th>
      <td>history_vs_genghis_khan_alex_gendler</td>
      <td>10.4M</td>
      <td>1.93G</td>
      <td>4.77M</td>
      <td>698K</td>
      <td>20150702</td>
      <td>6 min 6 s</td>
      <td>239129</td>
    </tr>
    <tr>
      <th>183</th>
      <td>can_you_solve_the_cheating_royal_riddle_dan_katz</td>
      <td>19.3M</td>
      <td>1.95G</td>
      <td>1.36M</td>
      <td>695K</td>
      <td>20200811</td>
      <td>5 min 48 s</td>
      <td>463125</td>
    </tr>
    <tr>
      <th>184</th>
      <td>the_dark_ages_how_dark_were_they_really_crash_...</td>
      <td>29.8M</td>
      <td>1.98G</td>
      <td>6.78M</td>
      <td>695K</td>
      <td>20120426</td>
      <td>12 min 7 s</td>
      <td>343656</td>
    </tr>
    <tr>
      <th>185</th>
      <td>where_did_russia_come_from_alex_gendler</td>
      <td>13.9M</td>
      <td>1.99G</td>
      <td>4.06M</td>
      <td>693K</td>
      <td>20151013</td>
      <td>5 min 19 s</td>
      <td>365700</td>
    </tr>
    <tr>
      <th>186</th>
      <td>mary_s_room_a_philosophical_thought_experiment...</td>
      <td>6.90M</td>
      <td>2.00G</td>
      <td>3.38M</td>
      <td>692K</td>
      <td>20170124</td>
      <td>4 min 51 s</td>
      <td>198213</td>
    </tr>
    <tr>
      <th>187</th>
      <td>ancient_romes_most_notorious_doctor_ramon_glazov</td>
      <td>8.17M</td>
      <td>2.00G</td>
      <td>2.02M</td>
      <td>689K</td>
      <td>20190718</td>
      <td>5 min 10 s</td>
      <td>220500</td>
    </tr>
    <tr>
      <th>188</th>
      <td>no_one_can_figure_out_how_eels_have_sex_lucy_c...</td>
      <td>22.0M</td>
      <td>2.03G</td>
      <td>1.34M</td>
      <td>684K</td>
      <td>20200727</td>
      <td>6 min 1 s</td>
      <td>509397</td>
    </tr>
    <tr>
      <th>189</th>
      <td>how_to_build_a_fictional_world_kate_messner</td>
      <td>10.1M</td>
      <td>2.04G</td>
      <td>5.33M</td>
      <td>682K</td>
      <td>20140109</td>
      <td>5 min 24 s</td>
      <td>262371</td>
    </tr>
    <tr>
      <th>190</th>
      <td>how_stress_affects_your_brain_madhumita_murgia</td>
      <td>7.50M</td>
      <td>2.04G</td>
      <td>4.00M</td>
      <td>682K</td>
      <td>20151109</td>
      <td>4 min 15 s</td>
      <td>246334</td>
    </tr>
    <tr>
      <th>191</th>
      <td>can_you_solve_the_time_travel_riddle_dan_finkel</td>
      <td>8.14M</td>
      <td>2.05G</td>
      <td>1.97M</td>
      <td>674K</td>
      <td>20181204</td>
      <td>4 min 31 s</td>
      <td>251309</td>
    </tr>
    <tr>
      <th>192</th>
      <td>the_history_of_the_cuban_missile_crisis_matthe...</td>
      <td>9.69M</td>
      <td>2.06G</td>
      <td>3.29M</td>
      <td>673K</td>
      <td>20160926</td>
      <td>4 min 51 s</td>
      <td>278808</td>
    </tr>
    <tr>
      <th>193</th>
      <td>can_you_solve_the_rogue_ai_riddle_dan_finkel</td>
      <td>9.02M</td>
      <td>2.07G</td>
      <td>2.62M</td>
      <td>671K</td>
      <td>20180807</td>
      <td>5 min 12 s</td>
      <td>242285</td>
    </tr>
    <tr>
      <th>194</th>
      <td>can_you_outsmart_this_logical_fallacy_alex_gen...</td>
      <td>6.02M</td>
      <td>2.07G</td>
      <td>1.31M</td>
      <td>670K</td>
      <td>20191125</td>
      <td>3 min 44 s</td>
      <td>224813</td>
    </tr>
    <tr>
      <th>195</th>
      <td>the_egyptian_myth_of_isis_and_the_seven_scorpi...</td>
      <td>8.66M</td>
      <td>2.08G</td>
      <td>1.31M</td>
      <td>669K</td>
      <td>20200302</td>
      <td>3 min 34 s</td>
      <td>339052</td>
    </tr>
    <tr>
      <th>196</th>
      <td>why_should_you_read_tolstoy_s_war_and_peace_br...</td>
      <td>10.4M</td>
      <td>2.09G</td>
      <td>3.26M</td>
      <td>668K</td>
      <td>20170427</td>
      <td>5 min 9 s</td>
      <td>281961</td>
    </tr>
    <tr>
      <th>197</th>
      <td>the_philosophy_of_cynicism_william_d_desmond</td>
      <td>10.2M</td>
      <td>2.10G</td>
      <td>1.30M</td>
      <td>666K</td>
      <td>20191219</td>
      <td>5 min 25 s</td>
      <td>261607</td>
    </tr>
    <tr>
      <th>198</th>
      <td>cell_vs_virus_a_battle_for_health_shannon_stiles</td>
      <td>10.1M</td>
      <td>2.11G</td>
      <td>5.19M</td>
      <td>665K</td>
      <td>20140417</td>
      <td>3 min 58 s</td>
      <td>354423</td>
    </tr>
    <tr>
      <th>199</th>
      <td>what_causes_panic_attacks_and_how_can_you_prev...</td>
      <td>17.4M</td>
      <td>2.13G</td>
      <td>662K</td>
      <td>662K</td>
      <td>20201008</td>
      <td>5 min 22 s</td>
      <td>451370</td>
    </tr>
    <tr>
      <th>200</th>
      <td>why_isnt_the_netherlands_underwater_stefan_al</td>
      <td>10.3M</td>
      <td>2.14G</td>
      <td>1.29M</td>
      <td>662K</td>
      <td>20200324</td>
      <td>5 min 23 s</td>
      <td>266917</td>
    </tr>
    <tr>
      <th>201</th>
      <td>how_do_pregnancy_tests_work_tien_nguyen</td>
      <td>8.90M</td>
      <td>2.15G</td>
      <td>4.51M</td>
      <td>660K</td>
      <td>20150707</td>
      <td>4 min 33 s</td>
      <td>273222</td>
    </tr>
    <tr>
      <th>202</th>
      <td>how_stress_affects_your_body_sharon_horesh_ber...</td>
      <td>8.32M</td>
      <td>2.16G</td>
      <td>3.85M</td>
      <td>658K</td>
      <td>20151022</td>
      <td>4 min 42 s</td>
      <td>247274</td>
    </tr>
    <tr>
      <th>203</th>
      <td>the_egyptian_myth_of_the_death_of_osiris_alex_...</td>
      <td>20.5M</td>
      <td>2.18G</td>
      <td>1.28M</td>
      <td>656K</td>
      <td>20200716</td>
      <td>4 min 14 s</td>
      <td>675110</td>
    </tr>
    <tr>
      <th>204</th>
      <td>what_is_imposter_syndrome_and_how_can_you_comb...</td>
      <td>6.54M</td>
      <td>2.18G</td>
      <td>2.56M</td>
      <td>655K</td>
      <td>20180828</td>
      <td>4 min 18 s</td>
      <td>211885</td>
    </tr>
    <tr>
      <th>205</th>
      <td>can_you_solve_the_alice_in_wonderland_riddle_a...</td>
      <td>16.9M</td>
      <td>2.20G</td>
      <td>652K</td>
      <td>652K</td>
      <td>20201117</td>
      <td>5 min 4 s</td>
      <td>464370</td>
    </tr>
    <tr>
      <th>206</th>
      <td>a_day_in_the_life_of_an_ancient_athenian_rober...</td>
      <td>10.1M</td>
      <td>2.21G</td>
      <td>2.55M</td>
      <td>652K</td>
      <td>20180315</td>
      <td>5 min 1 s</td>
      <td>281366</td>
    </tr>
    <tr>
      <th>207</th>
      <td>the_myth_of_loki_and_the_master_builder_alex_g...</td>
      <td>7.81M</td>
      <td>2.22G</td>
      <td>1.26M</td>
      <td>647K</td>
      <td>20191114</td>
      <td>4 min 37 s</td>
      <td>236430</td>
    </tr>
    <tr>
      <th>208</th>
      <td>platos_allegory_of_the_cave_alex_gendler</td>
      <td>13.0M</td>
      <td>2.23G</td>
      <td>4.41M</td>
      <td>645K</td>
      <td>20150317</td>
      <td>4 min 32 s</td>
      <td>400088</td>
    </tr>
    <tr>
      <th>209</th>
      <td>platos_best_and_worst_ideas_wisecrack</td>
      <td>9.76M</td>
      <td>2.24G</td>
      <td>3.14M</td>
      <td>644K</td>
      <td>20161025</td>
      <td>4 min 48 s</td>
      <td>283444</td>
    </tr>
    <tr>
      <th>210</th>
      <td>is_it_bad_to_hold_your_pee_heba_shaheed</td>
      <td>6.40M</td>
      <td>2.25G</td>
      <td>3.13M</td>
      <td>641K</td>
      <td>20161010</td>
      <td>3 min 58 s</td>
      <td>225478</td>
    </tr>
    <tr>
      <th>211</th>
      <td>why_should_you_read_lord_of_the_flies_by_willi...</td>
      <td>12.0M</td>
      <td>2.26G</td>
      <td>1.25M</td>
      <td>641K</td>
      <td>20191212</td>
      <td>4 min 47 s</td>
      <td>349681</td>
    </tr>
    <tr>
      <th>212</th>
      <td>can_you_solve_the_trolls_paradox_riddle_dan_fi...</td>
      <td>10.2M</td>
      <td>2.27G</td>
      <td>1.87M</td>
      <td>638K</td>
      <td>20181220</td>
      <td>3 min 44 s</td>
      <td>382273</td>
    </tr>
    <tr>
      <th>213</th>
      <td>why_do_we_love_a_philosophical_inquiry_skye_c_...</td>
      <td>9.31M</td>
      <td>2.28G</td>
      <td>3.74M</td>
      <td>637K</td>
      <td>20160211</td>
      <td>5 min 44 s</td>
      <td>226578</td>
    </tr>
    <tr>
      <th>214</th>
      <td>can_you_solve_the_vampire_hunter_riddle_dan_fi...</td>
      <td>5.88M</td>
      <td>2.28G</td>
      <td>1.86M</td>
      <td>636K</td>
      <td>20190128</td>
      <td>3 min 51 s</td>
      <td>213322</td>
    </tr>
    <tr>
      <th>215</th>
      <td>a_brief_history_of_dogs_david_ian_howe</td>
      <td>9.68M</td>
      <td>2.29G</td>
      <td>1.86M</td>
      <td>634K</td>
      <td>20190326</td>
      <td>4 min 58 s</td>
      <td>272177</td>
    </tr>
    <tr>
      <th>216</th>
      <td>why_should_you_listen_to_vivaldi_s_four_season...</td>
      <td>8.74M</td>
      <td>2.30G</td>
      <td>3.08M</td>
      <td>631K</td>
      <td>20161024</td>
      <td>4 min 19 s</td>
      <td>282930</td>
    </tr>
    <tr>
      <th>217</th>
      <td>why_should_you_read_fahrenheit_451_iseult_gill...</td>
      <td>9.36M</td>
      <td>2.31G</td>
      <td>1.83M</td>
      <td>626K</td>
      <td>20190122</td>
      <td>4 min 35 s</td>
      <td>284909</td>
    </tr>
    <tr>
      <th>218</th>
      <td>the_science_of_attraction_dawn_maslar</td>
      <td>6.78M</td>
      <td>2.32G</td>
      <td>4.88M</td>
      <td>624K</td>
      <td>20140508</td>
      <td>4 min 33 s</td>
      <td>208023</td>
    </tr>
    <tr>
      <th>219</th>
      <td>8_traits_of_successful_people_richard_st_john</td>
      <td>19.1M</td>
      <td>2.33G</td>
      <td>5.49M</td>
      <td>624K</td>
      <td>20130405</td>
      <td>7 min 17 s</td>
      <td>367133</td>
    </tr>
    <tr>
      <th>220</th>
      <td>history_vs_napoleon_bonaparte_alex_gendler</td>
      <td>8.85M</td>
      <td>2.34G</td>
      <td>3.64M</td>
      <td>621K</td>
      <td>20160204</td>
      <td>5 min 21 s</td>
      <td>230960</td>
    </tr>
    <tr>
      <th>221</th>
      <td>can_you_solve_the_cuddly_duddly_fuddly_wuddly_...</td>
      <td>6.06M</td>
      <td>2.35G</td>
      <td>1.82M</td>
      <td>621K</td>
      <td>20190425</td>
      <td>3 min 34 s</td>
      <td>237212</td>
    </tr>
    <tr>
      <th>222</th>
      <td>what_s_the_difference_between_accuracy_and_pre...</td>
      <td>7.40M</td>
      <td>2.36G</td>
      <td>4.23M</td>
      <td>619K</td>
      <td>20150414</td>
      <td>4 min 52 s</td>
      <td>212350</td>
    </tr>
    <tr>
      <th>223</th>
      <td>where_do_superstitions_come_from_stuart_vyse</td>
      <td>8.38M</td>
      <td>2.36G</td>
      <td>3.00M</td>
      <td>614K</td>
      <td>20170309</td>
      <td>5 min 10 s</td>
      <td>226507</td>
    </tr>
    <tr>
      <th>224</th>
      <td>how_a_wound_heals_itself_sarthak_sinha</td>
      <td>7.79M</td>
      <td>2.37G</td>
      <td>4.18M</td>
      <td>611K</td>
      <td>20141110</td>
      <td>4 min 0 s</td>
      <td>271113</td>
    </tr>
    <tr>
      <th>225</th>
      <td>just_how_small_is_an_atom</td>
      <td>14.7M</td>
      <td>2.39G</td>
      <td>5.96M</td>
      <td>610K</td>
      <td>20120416</td>
      <td>5 min 27 s</td>
      <td>374947</td>
    </tr>
    <tr>
      <th>226</th>
      <td>why_elephants_never_forget_alex_gendler</td>
      <td>8.72M</td>
      <td>2.40G</td>
      <td>4.16M</td>
      <td>608K</td>
      <td>20141113</td>
      <td>5 min 22 s</td>
      <td>226857</td>
    </tr>
    <tr>
      <th>227</th>
      <td>how_does_your_immune_system_work_emma_bryce</td>
      <td>9.65M</td>
      <td>2.40G</td>
      <td>2.37M</td>
      <td>606K</td>
      <td>20180108</td>
      <td>5 min 22 s</td>
      <td>251123</td>
    </tr>
    <tr>
      <th>228</th>
      <td>can_you_solve_the_giant_iron_riddle_alex_gendler</td>
      <td>5.39M</td>
      <td>2.41G</td>
      <td>1.77M</td>
      <td>605K</td>
      <td>20181127</td>
      <td>3 min 37 s</td>
      <td>208055</td>
    </tr>
    <tr>
      <th>229</th>
      <td>the_greatest_ted_talk_ever_sold_morgan_spurlock</td>
      <td>38.9M</td>
      <td>2.45G</td>
      <td>5.31M</td>
      <td>605K</td>
      <td>20130315</td>
      <td>19 min 28 s</td>
      <td>279660</td>
    </tr>
    <tr>
      <th>230</th>
      <td>how_do_carbohydrates_impact_your_health_richar...</td>
      <td>8.69M</td>
      <td>2.46G</td>
      <td>3.54M</td>
      <td>605K</td>
      <td>20160111</td>
      <td>5 min 10 s</td>
      <td>234749</td>
    </tr>
    <tr>
      <th>231</th>
      <td>how_does_chemotherapy_work_hyunsoo_joshua_no</td>
      <td>12.9M</td>
      <td>2.47G</td>
      <td>1.17M</td>
      <td>601K</td>
      <td>20191205</td>
      <td>5 min 25 s</td>
      <td>331869</td>
    </tr>
    <tr>
      <th>232</th>
      <td>the_treadmill_s_dark_and_twisted_past_conor_he...</td>
      <td>14.6M</td>
      <td>2.48G</td>
      <td>3.52M</td>
      <td>600K</td>
      <td>20150922</td>
      <td>4 min 9 s</td>
      <td>491475</td>
    </tr>
    <tr>
      <th>233</th>
      <td>can_we_create_the_perfect_farm_brent_loken</td>
      <td>31.1M</td>
      <td>2.51G</td>
      <td>594K</td>
      <td>594K</td>
      <td>20201012</td>
      <td>7 min 9 s</td>
      <td>607459</td>
    </tr>
    <tr>
      <th>234</th>
      <td>how_to_recognize_a_dystopia_alex_gendler</td>
      <td>20.0M</td>
      <td>2.53G</td>
      <td>2.90M</td>
      <td>594K</td>
      <td>20161115</td>
      <td>5 min 55 s</td>
      <td>470751</td>
    </tr>
    <tr>
      <th>235</th>
      <td>how_the_food_you_eat_affects_your_gut_shilpa_r...</td>
      <td>12.3M</td>
      <td>2.55G</td>
      <td>2.90M</td>
      <td>594K</td>
      <td>20170323</td>
      <td>5 min 9 s</td>
      <td>334262</td>
    </tr>
    <tr>
      <th>236</th>
      <td>zen_koans_unsolvable_enigmas_designed_to_break...</td>
      <td>14.2M</td>
      <td>2.56G</td>
      <td>2.32M</td>
      <td>593K</td>
      <td>20180816</td>
      <td>4 min 57 s</td>
      <td>401648</td>
    </tr>
    <tr>
      <th>237</th>
      <td>why_is_cotton_in_everything_michael_r_stiff</td>
      <td>10.4M</td>
      <td>2.57G</td>
      <td>1.15M</td>
      <td>591K</td>
      <td>20200123</td>
      <td>4 min 53 s</td>
      <td>297875</td>
    </tr>
    <tr>
      <th>238</th>
      <td>the_life_cycle_of_a_cup_of_coffee_a_j_jacobs</td>
      <td>20.9M</td>
      <td>2.59G</td>
      <td>591K</td>
      <td>591K</td>
      <td>20210104</td>
      <td>5 min 4 s</td>
      <td>573958</td>
    </tr>
    <tr>
      <th>239</th>
      <td>what_makes_tattoos_permanent_claudia_aguirre</td>
      <td>8.82M</td>
      <td>2.60G</td>
      <td>4.61M</td>
      <td>590K</td>
      <td>20140710</td>
      <td>4 min 25 s</td>
      <td>279187</td>
    </tr>
    <tr>
      <th>240</th>
      <td>how_much_of_what_you_see_is_a_hallucination_el...</td>
      <td>12.7M</td>
      <td>2.61G</td>
      <td>2.30M</td>
      <td>589K</td>
      <td>20180626</td>
      <td>5 min 49 s</td>
      <td>304025</td>
    </tr>
    <tr>
      <th>241</th>
      <td>what_s_the_fastest_way_to_alphabetize_your_boo...</td>
      <td>6.22M</td>
      <td>2.62G</td>
      <td>2.87M</td>
      <td>589K</td>
      <td>20161128</td>
      <td>4 min 38 s</td>
      <td>187427</td>
    </tr>
    <tr>
      <th>242</th>
      <td>the_dangers_of_mixing_drugs_celine_valery</td>
      <td>14.3M</td>
      <td>2.63G</td>
      <td>1.15M</td>
      <td>587K</td>
      <td>20191112</td>
      <td>5 min 3 s</td>
      <td>396383</td>
    </tr>
    <tr>
      <th>243</th>
      <td>how_does_caffeine_keep_us_awake_hanan_qasim</td>
      <td>8.05M</td>
      <td>2.64G</td>
      <td>2.86M</td>
      <td>586K</td>
      <td>20170717</td>
      <td>5 min 14 s</td>
      <td>214393</td>
    </tr>
    <tr>
      <th>244</th>
      <td>can_you_solve_the_monster_duel_riddle_alex_gen...</td>
      <td>16.3M</td>
      <td>2.65G</td>
      <td>585K</td>
      <td>585K</td>
      <td>20201208</td>
      <td>5 min 35 s</td>
      <td>408341</td>
    </tr>
    <tr>
      <th>245</th>
      <td>the_myth_of_the_sampo_an_infinite_source_of_fo...</td>
      <td>11.9M</td>
      <td>2.67G</td>
      <td>1.14M</td>
      <td>585K</td>
      <td>20190923</td>
      <td>5 min 15 s</td>
      <td>316864</td>
    </tr>
    <tr>
      <th>246</th>
      <td>can_you_solve_the_worlds_most_evil_wizard_ridd...</td>
      <td>8.54M</td>
      <td>2.67G</td>
      <td>1.14M</td>
      <td>584K</td>
      <td>20200519</td>
      <td>5 min 16 s</td>
      <td>226546</td>
    </tr>
    <tr>
      <th>247</th>
      <td>how_do_fish_make_electricity_eleanor_nelsen</td>
      <td>10.4M</td>
      <td>2.68G</td>
      <td>2.28M</td>
      <td>584K</td>
      <td>20171130</td>
      <td>5 min 14 s</td>
      <td>277670</td>
    </tr>
    <tr>
      <th>248</th>
      <td>will_there_ever_be_a_mile_high_skyscraper_stef...</td>
      <td>9.17M</td>
      <td>2.69G</td>
      <td>1.71M</td>
      <td>584K</td>
      <td>20190207</td>
      <td>5 min 4 s</td>
      <td>252600</td>
    </tr>
    <tr>
      <th>249</th>
      <td>everything_changed_when_the_fire_crystal_got_s...</td>
      <td>9.03M</td>
      <td>2.70G</td>
      <td>1.14M</td>
      <td>582K</td>
      <td>20200206</td>
      <td>4 min 21 s</td>
      <td>289975</td>
    </tr>
    <tr>
      <th>250</th>
      <td>debunking_the_myths_of_ocd_natascha_m_santos</td>
      <td>9.04M</td>
      <td>2.71G</td>
      <td>3.97M</td>
      <td>581K</td>
      <td>20150519</td>
      <td>4 min 50 s</td>
      <td>260782</td>
    </tr>
    <tr>
      <th>251</th>
      <td>the_rise_and_fall_of_the_inca_empire_gordon_mc...</td>
      <td>14.5M</td>
      <td>2.73G</td>
      <td>2.27M</td>
      <td>580K</td>
      <td>20180212</td>
      <td>5 min 45 s</td>
      <td>353357</td>
    </tr>
    <tr>
      <th>252</th>
      <td>how_do_steroids_affect_your_muscles_and_the_re...</td>
      <td>18.1M</td>
      <td>2.74G</td>
      <td>580K</td>
      <td>580K</td>
      <td>20201109</td>
      <td>5 min 48 s</td>
      <td>435686</td>
    </tr>
    <tr>
      <th>253</th>
      <td>can_you_solve_the_giant_cat_army_riddle_dan_fi...</td>
      <td>9.01M</td>
      <td>2.75G</td>
      <td>2.26M</td>
      <td>578K</td>
      <td>20180611</td>
      <td>5 min 19 s</td>
      <td>236786</td>
    </tr>
    <tr>
      <th>254</th>
      <td>what_yoga_does_to_your_body_and_brain_krishna_...</td>
      <td>19.4M</td>
      <td>2.77G</td>
      <td>1.13M</td>
      <td>577K</td>
      <td>20200618</td>
      <td>6 min 1 s</td>
      <td>451724</td>
    </tr>
    <tr>
      <th>255</th>
      <td>can_you_solve_the_killer_robo_ants_riddle_dan_...</td>
      <td>9.24M</td>
      <td>2.78G</td>
      <td>1.69M</td>
      <td>576K</td>
      <td>20181009</td>
      <td>4 min 51 s</td>
      <td>265715</td>
    </tr>
    <tr>
      <th>256</th>
      <td>how_do_animals_experience_pain_robyn_j_crook</td>
      <td>7.80M</td>
      <td>2.79G</td>
      <td>2.81M</td>
      <td>576K</td>
      <td>20170117</td>
      <td>5 min 6 s</td>
      <td>213685</td>
    </tr>
    <tr>
      <th>257</th>
      <td>what_is_a_coronavirus_elizabeth_cox</td>
      <td>8.85M</td>
      <td>2.80G</td>
      <td>1.13M</td>
      <td>576K</td>
      <td>20200514</td>
      <td>5 min 15 s</td>
      <td>235401</td>
    </tr>
    <tr>
      <th>258</th>
      <td>should_you_trust_unanimous_decisions_derek_abbott</td>
      <td>6.56M</td>
      <td>2.80G</td>
      <td>3.37M</td>
      <td>575K</td>
      <td>20160418</td>
      <td>4 min 2 s</td>
      <td>226579</td>
    </tr>
    <tr>
      <th>259</th>
      <td>why_do_humans_have_a_third_eyelid_dorsa_amir</td>
      <td>8.01M</td>
      <td>2.81G</td>
      <td>1.12M</td>
      <td>573K</td>
      <td>20191111</td>
      <td>4 min 35 s</td>
      <td>243613</td>
    </tr>
    <tr>
      <th>260</th>
      <td>why_should_you_read_one_hundred_years_of_solit...</td>
      <td>14.1M</td>
      <td>2.82G</td>
      <td>2.23M</td>
      <td>571K</td>
      <td>20180830</td>
      <td>5 min 30 s</td>
      <td>357661</td>
    </tr>
    <tr>
      <th>261</th>
      <td>the_dark_history_of_iq_tests_stefan_c_dombrowski</td>
      <td>12.8M</td>
      <td>2.84G</td>
      <td>1.12M</td>
      <td>571K</td>
      <td>20200427</td>
      <td>6 min 9 s</td>
      <td>289565</td>
    </tr>
    <tr>
      <th>262</th>
      <td>why_are_there_so_many_insects_murry_gans</td>
      <td>7.45M</td>
      <td>2.84G</td>
      <td>3.34M</td>
      <td>571K</td>
      <td>20160301</td>
      <td>4 min 43 s</td>
      <td>220791</td>
    </tr>
    <tr>
      <th>263</th>
      <td>the_immortal_cells_of_henrietta_lacks_robin_bu...</td>
      <td>9.48M</td>
      <td>2.85G</td>
      <td>3.34M</td>
      <td>570K</td>
      <td>20160208</td>
      <td>4 min 26 s</td>
      <td>298869</td>
    </tr>
    <tr>
      <th>264</th>
      <td>what_is_entropy_jeff_phillips</td>
      <td>7.75M</td>
      <td>2.86G</td>
      <td>2.77M</td>
      <td>568K</td>
      <td>20170509</td>
      <td>5 min 19 s</td>
      <td>203721</td>
    </tr>
    <tr>
      <th>265</th>
      <td>can_you_solve_the_buried_treasure_riddle_danie...</td>
      <td>9.47M</td>
      <td>2.87G</td>
      <td>2.19M</td>
      <td>561K</td>
      <td>20180322</td>
      <td>5 min 2 s</td>
      <td>262431</td>
    </tr>
    <tr>
      <th>266</th>
      <td>the_chinese_myth_of_the_meddling_monk_shunan_teng</td>
      <td>8.00M</td>
      <td>2.88G</td>
      <td>1.63M</td>
      <td>556K</td>
      <td>20190523</td>
      <td>4 min 3 s</td>
      <td>275288</td>
    </tr>
    <tr>
      <th>267</th>
      <td>what_causes_insomnia_dan_kwartler</td>
      <td>7.39M</td>
      <td>2.89G</td>
      <td>2.17M</td>
      <td>555K</td>
      <td>20180614</td>
      <td>5 min 11 s</td>
      <td>199195</td>
    </tr>
    <tr>
      <th>268</th>
      <td>the_history_of_the_world_according_to_corn_chr...</td>
      <td>14.0M</td>
      <td>2.90G</td>
      <td>1.08M</td>
      <td>551K</td>
      <td>20191126</td>
      <td>5 min 22 s</td>
      <td>363404</td>
    </tr>
    <tr>
      <th>269</th>
      <td>why_should_you_read_macbeth_brendan_pelsue</td>
      <td>10.5M</td>
      <td>2.91G</td>
      <td>2.13M</td>
      <td>544K</td>
      <td>20171102</td>
      <td>6 min 8 s</td>
      <td>238878</td>
    </tr>
    <tr>
      <th>270</th>
      <td>why_do_your_knuckles_pop_eleanor_nelsen</td>
      <td>12.1M</td>
      <td>2.92G</td>
      <td>3.68M</td>
      <td>539K</td>
      <td>20150505</td>
      <td>4 min 21 s</td>
      <td>387577</td>
    </tr>
    <tr>
      <th>271</th>
      <td>how_high_can_you_count_on_your_fingers_spoiler...</td>
      <td>9.61M</td>
      <td>2.93G</td>
      <td>2.63M</td>
      <td>538K</td>
      <td>20161215</td>
      <td>4 min 29 s</td>
      <td>298981</td>
    </tr>
    <tr>
      <th>272</th>
      <td>why_should_you_read_crime_and_punishment_alex_...</td>
      <td>8.22M</td>
      <td>2.94G</td>
      <td>1.57M</td>
      <td>536K</td>
      <td>20190514</td>
      <td>4 min 45 s</td>
      <td>241227</td>
    </tr>
    <tr>
      <th>273</th>
      <td>how_did_dracula_become_the_world_s_most_famous...</td>
      <td>10.5M</td>
      <td>2.95G</td>
      <td>2.61M</td>
      <td>535K</td>
      <td>20170420</td>
      <td>5 min 5 s</td>
      <td>287952</td>
    </tr>
    <tr>
      <th>274</th>
      <td>the_most_successful_pirate_of_all_time_dian_mu...</td>
      <td>8.43M</td>
      <td>2.96G</td>
      <td>2.08M</td>
      <td>531K</td>
      <td>20180402</td>
      <td>5 min 16 s</td>
      <td>223681</td>
    </tr>
    <tr>
      <th>275</th>
      <td>the_journey_to_pluto_the_farthest_world_ever_e...</td>
      <td>8.63M</td>
      <td>2.97G</td>
      <td>2.07M</td>
      <td>530K</td>
      <td>20180517</td>
      <td>6 min 9 s</td>
      <td>195832</td>
    </tr>
    <tr>
      <th>276</th>
      <td>what_is_the_heisenberg_uncertainty_principle_c...</td>
      <td>5.96M</td>
      <td>2.97G</td>
      <td>3.62M</td>
      <td>529K</td>
      <td>20140916</td>
      <td>4 min 43 s</td>
      <td>176200</td>
    </tr>
    <tr>
      <th>277</th>
      <td>at_what_moment_are_you_dead_randall_hayes</td>
      <td>9.25M</td>
      <td>2.98G</td>
      <td>3.61M</td>
      <td>528K</td>
      <td>20141211</td>
      <td>5 min 33 s</td>
      <td>232681</td>
    </tr>
    <tr>
      <th>278</th>
      <td>how_blood_pressure_works_wilfred_manzano</td>
      <td>8.16M</td>
      <td>2.99G</td>
      <td>3.59M</td>
      <td>525K</td>
      <td>20150723</td>
      <td>4 min 31 s</td>
      <td>252241</td>
    </tr>
    <tr>
      <th>279</th>
      <td>the_prison_break_think_like_a_coder_ep_1</td>
      <td>14.0M</td>
      <td>3.00G</td>
      <td>1.02M</td>
      <td>524K</td>
      <td>20190930</td>
      <td>6 min 50 s</td>
      <td>285711</td>
    </tr>
    <tr>
      <th>280</th>
      <td>where_did_english_come_from_claire_bowern</td>
      <td>9.49M</td>
      <td>3.01G</td>
      <td>3.58M</td>
      <td>523K</td>
      <td>20150716</td>
      <td>4 min 53 s</td>
      <td>271197</td>
    </tr>
    <tr>
      <th>281</th>
      <td>the_benefits_of_a_good_night_s_sleep_shai_marcu</td>
      <td>11.3M</td>
      <td>3.02G</td>
      <td>3.58M</td>
      <td>523K</td>
      <td>20150105</td>
      <td>5 min 44 s</td>
      <td>275712</td>
    </tr>
    <tr>
      <th>282</th>
      <td>a_day_in_the_life_of_a_celtic_druid_philip_fre...</td>
      <td>15.0M</td>
      <td>3.04G</td>
      <td>1.02M</td>
      <td>520K</td>
      <td>20190917</td>
      <td>4 min 30 s</td>
      <td>464225</td>
    </tr>
    <tr>
      <th>283</th>
      <td>how_do_vitamins_work_ginnie_trinh_nguyen</td>
      <td>9.07M</td>
      <td>3.05G</td>
      <td>3.55M</td>
      <td>520K</td>
      <td>20141006</td>
      <td>4 min 43 s</td>
      <td>267870</td>
    </tr>
    <tr>
      <th>284</th>
      <td>can_you_solve_the_alien_probe_riddle_dan_finkel</td>
      <td>8.42M</td>
      <td>3.05G</td>
      <td>1.52M</td>
      <td>519K</td>
      <td>20180924</td>
      <td>5 min 8 s</td>
      <td>228816</td>
    </tr>
    <tr>
      <th>285</th>
      <td>is_telekinesis_real_emma_bryce</td>
      <td>8.68M</td>
      <td>3.06G</td>
      <td>3.54M</td>
      <td>518K</td>
      <td>20140930</td>
      <td>5 min 22 s</td>
      <td>225726</td>
    </tr>
    <tr>
      <th>286</th>
      <td>did_the_amazons_really_exist_adrienne_mayor</td>
      <td>14.0M</td>
      <td>3.08G</td>
      <td>2.01M</td>
      <td>516K</td>
      <td>20180618</td>
      <td>5 min 5 s</td>
      <td>383778</td>
    </tr>
    <tr>
      <th>287</th>
      <td>is_fire_a_solid_a_liquid_or_a_gas_elizabeth_cox</td>
      <td>9.93M</td>
      <td>3.09G</td>
      <td>1.50M</td>
      <td>512K</td>
      <td>20181105</td>
      <td>4 min 34 s</td>
      <td>303456</td>
    </tr>
    <tr>
      <th>288</th>
      <td>how_squids_outsmart_their_predators_carly_anne...</td>
      <td>9.54M</td>
      <td>3.09G</td>
      <td>2.00M</td>
      <td>511K</td>
      <td>20180514</td>
      <td>5 min 12 s</td>
      <td>256263</td>
    </tr>
    <tr>
      <th>289</th>
      <td>what_causes_body_odor_mel_rosenberg</td>
      <td>6.32M</td>
      <td>3.10G</td>
      <td>1.99M</td>
      <td>510K</td>
      <td>20180405</td>
      <td>4 min 28 s</td>
      <td>197352</td>
    </tr>
    <tr>
      <th>290</th>
      <td>the_sonic_boom_problem_katerina_kaouri</td>
      <td>11.3M</td>
      <td>3.11G</td>
      <td>3.48M</td>
      <td>509K</td>
      <td>20150210</td>
      <td>5 min 43 s</td>
      <td>276574</td>
    </tr>
    <tr>
      <th>291</th>
      <td>why_do_competitors_open_their_stores_next_to_o...</td>
      <td>8.49M</td>
      <td>3.12G</td>
      <td>4.47M</td>
      <td>509K</td>
      <td>20121001</td>
      <td>4 min 6 s</td>
      <td>289270</td>
    </tr>
    <tr>
      <th>292</th>
      <td>a_brief_history_of_goths_dan_adams</td>
      <td>11.8M</td>
      <td>3.13G</td>
      <td>2.48M</td>
      <td>509K</td>
      <td>20170518</td>
      <td>5 min 30 s</td>
      <td>299688</td>
    </tr>
    <tr>
      <th>293</th>
      <td>the_rise_and_fall_of_the_assyrian_empire_maria...</td>
      <td>12.1M</td>
      <td>3.14G</td>
      <td>1.98M</td>
      <td>508K</td>
      <td>20180424</td>
      <td>5 min 15 s</td>
      <td>322355</td>
    </tr>
    <tr>
      <th>294</th>
      <td>how_to_outsmart_the_prisoners_dilemma_lucas_hu...</td>
      <td>22.9M</td>
      <td>3.17G</td>
      <td>0.99M</td>
      <td>507K</td>
      <td>20200827</td>
      <td>5 min 44 s</td>
      <td>557530</td>
    </tr>
    <tr>
      <th>295</th>
      <td>how_to_write_descriptively_nalo_hopkinson</td>
      <td>12.1M</td>
      <td>3.18G</td>
      <td>2.96M</td>
      <td>505K</td>
      <td>20151116</td>
      <td>4 min 41 s</td>
      <td>361267</td>
    </tr>
    <tr>
      <th>296</th>
      <td>how_to_make_a_mummy_len_bloch</td>
      <td>7.41M</td>
      <td>3.19G</td>
      <td>3.43M</td>
      <td>501K</td>
      <td>20150618</td>
      <td>4 min 45 s</td>
      <td>217959</td>
    </tr>
    <tr>
      <th>297</th>
      <td>the_amazing_ways_plants_defend_themselves_vale...</td>
      <td>11.5M</td>
      <td>3.20G</td>
      <td>2.45M</td>
      <td>501K</td>
      <td>20170828</td>
      <td>6 min 11 s</td>
      <td>258932</td>
    </tr>
    <tr>
      <th>298</th>
      <td>how_rollercoasters_affect_your_body_brian_d_avery</td>
      <td>9.21M</td>
      <td>3.21G</td>
      <td>1.47M</td>
      <td>500K</td>
      <td>20181029</td>
      <td>5 min 1 s</td>
      <td>255750</td>
    </tr>
    <tr>
      <th>299</th>
      <td>if_superpowers_were_real_immortality_joy_lin</td>
      <td>14.3M</td>
      <td>3.22G</td>
      <td>4.40M</td>
      <td>500K</td>
      <td>20130627</td>
      <td>4 min 29 s</td>
      <td>445553</td>
    </tr>
    <tr>
      <th>300</th>
      <td>how_parasites_change_their_host_s_behavior_jaa...</td>
      <td>10.1M</td>
      <td>3.23G</td>
      <td>3.42M</td>
      <td>500K</td>
      <td>20150309</td>
      <td>5 min 13 s</td>
      <td>270641</td>
    </tr>
    <tr>
      <th>301</th>
      <td>the_pharaoh_that_wouldn_t_be_forgotten_kate_green</td>
      <td>9.09M</td>
      <td>3.24G</td>
      <td>3.41M</td>
      <td>499K</td>
      <td>20141215</td>
      <td>4 min 33 s</td>
      <td>278778</td>
    </tr>
    <tr>
      <th>302</th>
      <td>the_myth_of_oisin_and_the_land_of_eternal_yout...</td>
      <td>8.19M</td>
      <td>3.25G</td>
      <td>1.94M</td>
      <td>496K</td>
      <td>20180118</td>
      <td>3 min 49 s</td>
      <td>299610</td>
    </tr>
    <tr>
      <th>303</th>
      <td>what_caused_the_french_revolution_tom_mullaney</td>
      <td>13.9M</td>
      <td>3.26G</td>
      <td>2.40M</td>
      <td>491K</td>
      <td>20161027</td>
      <td>5 min 38 s</td>
      <td>344588</td>
    </tr>
    <tr>
      <th>304</th>
      <td>the_myth_of_the_stolen_eyeballs_nathan_d_horowitz</td>
      <td>23.6M</td>
      <td>3.28G</td>
      <td>490K</td>
      <td>490K</td>
      <td>20201005</td>
      <td>5 min 29 s</td>
      <td>600130</td>
    </tr>
    <tr>
      <th>305</th>
      <td>what_is_the_tragedy_of_the_commons_nicholas_am...</td>
      <td>12.4M</td>
      <td>3.29G</td>
      <td>1.91M</td>
      <td>490K</td>
      <td>20171121</td>
      <td>4 min 57 s</td>
      <td>347956</td>
    </tr>
    <tr>
      <th>306</th>
      <td>how_to_unboil_an_egg_eleanor_nelsen</td>
      <td>7.29M</td>
      <td>3.30G</td>
      <td>3.34M</td>
      <td>488K</td>
      <td>20150423</td>
      <td>4 min 9 s</td>
      <td>244867</td>
    </tr>
    <tr>
      <th>307</th>
      <td>how_to_read_music_tim_hansen</td>
      <td>8.54M</td>
      <td>3.31G</td>
      <td>4.28M</td>
      <td>487K</td>
      <td>20130718</td>
      <td>5 min 23 s</td>
      <td>221446</td>
    </tr>
    <tr>
      <th>308</th>
      <td>history_vs_vladimir_lenin_alex_gendler</td>
      <td>15.9M</td>
      <td>3.33G</td>
      <td>3.80M</td>
      <td>486K</td>
      <td>20140407</td>
      <td>6 min 42 s</td>
      <td>330920</td>
    </tr>
    <tr>
      <th>309</th>
      <td>the_scientific_origins_of_the_minotaur_matt_ka...</td>
      <td>10.4M</td>
      <td>3.34G</td>
      <td>3.31M</td>
      <td>485K</td>
      <td>20150720</td>
      <td>4 min 40 s</td>
      <td>309884</td>
    </tr>
    <tr>
      <th>310</th>
      <td>can_you_solve_the_death_race_riddle_alex_gendler</td>
      <td>13.6M</td>
      <td>3.35G</td>
      <td>969K</td>
      <td>485K</td>
      <td>20200303</td>
      <td>5 min 50 s</td>
      <td>325183</td>
    </tr>
    <tr>
      <th>311</th>
      <td>string_theory_brian_greene</td>
      <td>37.8M</td>
      <td>3.39G</td>
      <td>4.25M</td>
      <td>484K</td>
      <td>20130809</td>
      <td>19 min 9 s</td>
      <td>276050</td>
    </tr>
    <tr>
      <th>312</th>
      <td>the_art_forger_who_tricked_the_nazis_noah_charney</td>
      <td>10.4M</td>
      <td>3.40G</td>
      <td>967K</td>
      <td>483K</td>
      <td>20200406</td>
      <td>5 min 16 s</td>
      <td>274779</td>
    </tr>
    <tr>
      <th>313</th>
      <td>the_genius_of_marie_curie_shohini_ghose</td>
      <td>9.06M</td>
      <td>3.40G</td>
      <td>2.35M</td>
      <td>482K</td>
      <td>20170608</td>
      <td>5 min 3 s</td>
      <td>250600</td>
    </tr>
    <tr>
      <th>314</th>
      <td>your_body_vs_implants_kaitlyn_sadtler</td>
      <td>11.4M</td>
      <td>3.42G</td>
      <td>1.41M</td>
      <td>480K</td>
      <td>20190617</td>
      <td>4 min 39 s</td>
      <td>342493</td>
    </tr>
    <tr>
      <th>315</th>
      <td>history_vs_christopher_columbus_alex_gendler</td>
      <td>10.0M</td>
      <td>3.43G</td>
      <td>3.28M</td>
      <td>480K</td>
      <td>20141013</td>
      <td>5 min 54 s</td>
      <td>237036</td>
    </tr>
    <tr>
      <th>316</th>
      <td>what_really_happens_to_the_plastic_you_throw_a...</td>
      <td>6.68M</td>
      <td>3.43G</td>
      <td>3.28M</td>
      <td>480K</td>
      <td>20150421</td>
      <td>4 min 6 s</td>
      <td>226971</td>
    </tr>
    <tr>
      <th>317</th>
      <td>can_you_solve_the_sorting_hat_riddle_dan_katz_...</td>
      <td>20.2M</td>
      <td>3.45G</td>
      <td>958K</td>
      <td>479K</td>
      <td>20200901</td>
      <td>5 min 59 s</td>
      <td>472247</td>
    </tr>
    <tr>
      <th>318</th>
      <td>how_the_normans_changed_the_history_of_europe_...</td>
      <td>13.3M</td>
      <td>3.47G</td>
      <td>1.87M</td>
      <td>479K</td>
      <td>20180809</td>
      <td>5 min 19 s</td>
      <td>348292</td>
    </tr>
    <tr>
      <th>319</th>
      <td>exponential_growth_how_folding_paper_can_get_y...</td>
      <td>6.30M</td>
      <td>3.47G</td>
      <td>4.67M</td>
      <td>478K</td>
      <td>20120419</td>
      <td>3 min 48 s</td>
      <td>231126</td>
    </tr>
    <tr>
      <th>320</th>
      <td>are_you_a_body_with_a_mind_or_a_mind_with_a_bo...</td>
      <td>10.6M</td>
      <td>3.48G</td>
      <td>1.87M</td>
      <td>478K</td>
      <td>20170925</td>
      <td>6 min 9 s</td>
      <td>239714</td>
    </tr>
    <tr>
      <th>321</th>
      <td>the_real_story_behind_archimedes_eureka_armand...</td>
      <td>10.3M</td>
      <td>3.49G</td>
      <td>3.26M</td>
      <td>477K</td>
      <td>20150313</td>
      <td>4 min 41 s</td>
      <td>305797</td>
    </tr>
    <tr>
      <th>322</th>
      <td>how_does_your_body_process_medicine_celine_valery</td>
      <td>9.04M</td>
      <td>3.50G</td>
      <td>2.32M</td>
      <td>475K</td>
      <td>20170515</td>
      <td>4 min 12 s</td>
      <td>300131</td>
    </tr>
    <tr>
      <th>323</th>
      <td>a_day_in_the_life_of_a_mongolian_queen_anne_f_...</td>
      <td>7.17M</td>
      <td>3.51G</td>
      <td>1.39M</td>
      <td>475K</td>
      <td>20190117</td>
      <td>4 min 23 s</td>
      <td>228161</td>
    </tr>
    <tr>
      <th>324</th>
      <td>why_dont_poisonous_animals_poison_themselves_r...</td>
      <td>9.25M</td>
      <td>3.52G</td>
      <td>1.85M</td>
      <td>473K</td>
      <td>20180705</td>
      <td>5 min 9 s</td>
      <td>250897</td>
    </tr>
    <tr>
      <th>325</th>
      <td>why_do_we_harvest_horseshoe_crab_blood_elizabe...</td>
      <td>7.50M</td>
      <td>3.52G</td>
      <td>1.85M</td>
      <td>473K</td>
      <td>20170921</td>
      <td>4 min 45 s</td>
      <td>220589</td>
    </tr>
    <tr>
      <th>326</th>
      <td>how_the_monkey_king_escaped_the_underworld_shu...</td>
      <td>15.4M</td>
      <td>3.54G</td>
      <td>943K</td>
      <td>472K</td>
      <td>20200407</td>
      <td>4 min 57 s</td>
      <td>434545</td>
    </tr>
    <tr>
      <th>327</th>
      <td>history_vs_sigmund_freud_todd_dufresne</td>
      <td>8.79M</td>
      <td>3.55G</td>
      <td>943K</td>
      <td>471K</td>
      <td>20200331</td>
      <td>5 min 54 s</td>
      <td>208325</td>
    </tr>
    <tr>
      <th>328</th>
      <td>the_power_of_the_placebo_effect_emma_bryce</td>
      <td>8.45M</td>
      <td>3.56G</td>
      <td>2.75M</td>
      <td>470K</td>
      <td>20160404</td>
      <td>4 min 37 s</td>
      <td>255563</td>
    </tr>
    <tr>
      <th>329</th>
      <td>this_is_sparta_fierce_warriors_of_the_ancient_...</td>
      <td>8.43M</td>
      <td>3.56G</td>
      <td>2.75M</td>
      <td>469K</td>
      <td>20160308</td>
      <td>4 min 27 s</td>
      <td>264020</td>
    </tr>
    <tr>
      <th>330</th>
      <td>what_causes_opioid_addiction_and_why_is_it_so_...</td>
      <td>19.1M</td>
      <td>3.58G</td>
      <td>934K</td>
      <td>467K</td>
      <td>20200507</td>
      <td>8 min 21 s</td>
      <td>319253</td>
    </tr>
    <tr>
      <th>331</th>
      <td>game_theory_challenge_can_you_predict_human_be...</td>
      <td>5.95M</td>
      <td>3.59G</td>
      <td>933K</td>
      <td>467K</td>
      <td>20191105</td>
      <td>4 min 58 s</td>
      <td>167356</td>
    </tr>
    <tr>
      <th>332</th>
      <td>the_rise_and_fall_of_historys_first_empire_sor...</td>
      <td>23.9M</td>
      <td>3.61G</td>
      <td>465K</td>
      <td>465K</td>
      <td>20201015</td>
      <td>5 min 37 s</td>
      <td>594549</td>
    </tr>
    <tr>
      <th>333</th>
      <td>how_fast_is_the_speed_of_thought_seena_mathew</td>
      <td>20.8M</td>
      <td>3.63G</td>
      <td>465K</td>
      <td>465K</td>
      <td>20201116</td>
      <td>5 min 16 s</td>
      <td>551945</td>
    </tr>
    <tr>
      <th>334</th>
      <td>how_aspirin_was_discovered_krishna_sudhir</td>
      <td>11.6M</td>
      <td>3.64G</td>
      <td>1.81M</td>
      <td>463K</td>
      <td>20171002</td>
      <td>5 min 44 s</td>
      <td>283832</td>
    </tr>
    <tr>
      <th>335</th>
      <td>why_doesnt_anything_stick_to_teflon_ashwini_bh...</td>
      <td>8.67M</td>
      <td>3.65G</td>
      <td>2.26M</td>
      <td>462K</td>
      <td>20161213</td>
      <td>4 min 44 s</td>
      <td>255853</td>
    </tr>
    <tr>
      <th>336</th>
      <td>the_evolution_of_animal_genitalia_menno_schilt...</td>
      <td>13.2M</td>
      <td>3.66G</td>
      <td>2.25M</td>
      <td>462K</td>
      <td>20170424</td>
      <td>5 min 35 s</td>
      <td>330464</td>
    </tr>
    <tr>
      <th>337</th>
      <td>how_fast_can_a_vaccine_be_made_dan_kwartler</td>
      <td>20.4M</td>
      <td>3.68G</td>
      <td>918K</td>
      <td>459K</td>
      <td>20200615</td>
      <td>5 min 51 s</td>
      <td>487359</td>
    </tr>
    <tr>
      <th>338</th>
      <td>how_do_personality_tests_work_merve_emre</td>
      <td>19.5M</td>
      <td>3.70G</td>
      <td>459K</td>
      <td>459K</td>
      <td>20201222</td>
      <td>4 min 56 s</td>
      <td>552955</td>
    </tr>
    <tr>
      <th>339</th>
      <td>a_brief_history_of_banned_numbers_alessandra_king</td>
      <td>7.66M</td>
      <td>3.71G</td>
      <td>1.79M</td>
      <td>458K</td>
      <td>20170926</td>
      <td>4 min 42 s</td>
      <td>227643</td>
    </tr>
    <tr>
      <th>340</th>
      <td>the_incredible_history_of_china_s_terracotta_w...</td>
      <td>7.41M</td>
      <td>3.72G</td>
      <td>3.13M</td>
      <td>457K</td>
      <td>20150630</td>
      <td>4 min 31 s</td>
      <td>228952</td>
    </tr>
    <tr>
      <th>341</th>
      <td>why_is_meningitis_so_dangerous_melvin_sanicas</td>
      <td>9.77M</td>
      <td>3.73G</td>
      <td>1.34M</td>
      <td>457K</td>
      <td>20181119</td>
      <td>4 min 53 s</td>
      <td>278915</td>
    </tr>
    <tr>
      <th>342</th>
      <td>ugly_history_witch_hunts_brian_a_pavlac</td>
      <td>13.9M</td>
      <td>3.74G</td>
      <td>1.33M</td>
      <td>454K</td>
      <td>20190611</td>
      <td>5 min 25 s</td>
      <td>357559</td>
    </tr>
    <tr>
      <th>343</th>
      <td>what_is_dyslexia_kelli_sandman_hurley</td>
      <td>7.51M</td>
      <td>3.75G</td>
      <td>3.97M</td>
      <td>451K</td>
      <td>20130715</td>
      <td>4 min 34 s</td>
      <td>229785</td>
    </tr>
    <tr>
      <th>344</th>
      <td>can_you_outsmart_a_troll_by_thinking_like_one_...</td>
      <td>18.4M</td>
      <td>3.77G</td>
      <td>451K</td>
      <td>451K</td>
      <td>20201029</td>
      <td>5 min 0 s</td>
      <td>515018</td>
    </tr>
    <tr>
      <th>345</th>
      <td>why_should_you_read_james_joyce_s_ulysses_sam_...</td>
      <td>18.6M</td>
      <td>3.79G</td>
      <td>1.76M</td>
      <td>451K</td>
      <td>20171024</td>
      <td>5 min 58 s</td>
      <td>435685</td>
    </tr>
    <tr>
      <th>346</th>
      <td>dna_hot_pockets_the_longest_word_ever_crash_co...</td>
      <td>44.7M</td>
      <td>3.83G</td>
      <td>4.39M</td>
      <td>449K</td>
      <td>20120409</td>
      <td>14 min 7 s</td>
      <td>442626</td>
    </tr>
    <tr>
      <th>347</th>
      <td>titan_of_terror_the_dark_imagination_of_h_p_lo...</td>
      <td>8.52M</td>
      <td>3.84G</td>
      <td>1.31M</td>
      <td>448K</td>
      <td>20190423</td>
      <td>4 min 46 s</td>
      <td>249408</td>
    </tr>
    <tr>
      <th>348</th>
      <td>the_surprising_reason_you_feel_awful_when_you_...</td>
      <td>7.36M</td>
      <td>3.84G</td>
      <td>2.60M</td>
      <td>443K</td>
      <td>20160419</td>
      <td>5 min 0 s</td>
      <td>205352</td>
    </tr>
    <tr>
      <th>349</th>
      <td>can_you_solve_the_rebel_supplies_riddle_alex_g...</td>
      <td>8.80M</td>
      <td>3.85G</td>
      <td>1.72M</td>
      <td>441K</td>
      <td>20180910</td>
      <td>5 min 17 s</td>
      <td>232135</td>
    </tr>
    <tr>
      <th>350</th>
      <td>what_machiavellian_really_means_pazit_cahlon_a...</td>
      <td>7.85M</td>
      <td>3.86G</td>
      <td>1.29M</td>
      <td>441K</td>
      <td>20190325</td>
      <td>5 min 9 s</td>
      <td>213085</td>
    </tr>
    <tr>
      <th>351</th>
      <td>ethical_dilemma_the_burger_murders_george_sied...</td>
      <td>21.9M</td>
      <td>3.88G</td>
      <td>881K</td>
      <td>441K</td>
      <td>20200728</td>
      <td>5 min 45 s</td>
      <td>531881</td>
    </tr>
    <tr>
      <th>352</th>
      <td>the_surprising_reasons_animals_play_dead_tiern...</td>
      <td>7.38M</td>
      <td>3.89G</td>
      <td>1.71M</td>
      <td>437K</td>
      <td>20180416</td>
      <td>4 min 46 s</td>
      <td>215946</td>
    </tr>
    <tr>
      <th>353</th>
      <td>the_aztec_myth_of_the_unlikeliest_sun_god_kay_...</td>
      <td>12.1M</td>
      <td>3.90G</td>
      <td>1.28M</td>
      <td>436K</td>
      <td>20190509</td>
      <td>4 min 12 s</td>
      <td>403978</td>
    </tr>
    <tr>
      <th>354</th>
      <td>jellyfish_predate_dinosaurs_how_have_they_surv...</td>
      <td>11.0M</td>
      <td>3.91G</td>
      <td>2.13M</td>
      <td>436K</td>
      <td>20170328</td>
      <td>5 min 25 s</td>
      <td>282283</td>
    </tr>
    <tr>
      <th>355</th>
      <td>why_is_herodotus_called_the_father_of_history_...</td>
      <td>7.87M</td>
      <td>3.92G</td>
      <td>1.68M</td>
      <td>430K</td>
      <td>20171211</td>
      <td>5 min 2 s</td>
      <td>218705</td>
    </tr>
    <tr>
      <th>356</th>
      <td>how_do_viruses_jump_from_animals_to_humans_ben...</td>
      <td>10.4M</td>
      <td>3.93G</td>
      <td>1.26M</td>
      <td>430K</td>
      <td>20190808</td>
      <td>5 min 4 s</td>
      <td>286057</td>
    </tr>
    <tr>
      <th>357</th>
      <td>why_is_glass_transparent_mark_miodownik</td>
      <td>6.71M</td>
      <td>3.94G</td>
      <td>3.35M</td>
      <td>429K</td>
      <td>20140204</td>
      <td>4 min 7 s</td>
      <td>227234</td>
    </tr>
    <tr>
      <th>358</th>
      <td>history_vs_henry_viii_mark_robinson_and_alex_g...</td>
      <td>7.82M</td>
      <td>3.94G</td>
      <td>1.25M</td>
      <td>427K</td>
      <td>20181112</td>
      <td>5 min 24 s</td>
      <td>201892</td>
    </tr>
    <tr>
      <th>359</th>
      <td>would_you_opt_for_a_life_with_no_pain_hayley_l...</td>
      <td>6.52M</td>
      <td>3.95G</td>
      <td>2.50M</td>
      <td>426K</td>
      <td>20151117</td>
      <td>4 min 9 s</td>
      <td>219454</td>
    </tr>
    <tr>
      <th>360</th>
      <td>what_is_mccarthyism_and_how_did_it_happen_elle...</td>
      <td>9.78M</td>
      <td>3.96G</td>
      <td>2.08M</td>
      <td>425K</td>
      <td>20170314</td>
      <td>5 min 42 s</td>
      <td>239690</td>
    </tr>
    <tr>
      <th>361</th>
      <td>how_to_use_rhetoric_to_get_what_you_want_camil...</td>
      <td>6.38M</td>
      <td>3.97G</td>
      <td>2.07M</td>
      <td>425K</td>
      <td>20160920</td>
      <td>4 min 29 s</td>
      <td>198869</td>
    </tr>
    <tr>
      <th>362</th>
      <td>which_bag_should_you_use_luka_seamus_wright_an...</td>
      <td>14.6M</td>
      <td>3.98G</td>
      <td>423K</td>
      <td>423K</td>
      <td>20201119</td>
      <td>4 min 52 s</td>
      <td>418995</td>
    </tr>
    <tr>
      <th>363</th>
      <td>exploring_other_dimensions_alex_rosenthal_and_...</td>
      <td>8.57M</td>
      <td>3.99G</td>
      <td>3.69M</td>
      <td>420K</td>
      <td>20130717</td>
      <td>4 min 48 s</td>
      <td>249156</td>
    </tr>
    <tr>
      <th>364</th>
      <td>are_ghost_ships_real_peter_b_campbell</td>
      <td>11.7M</td>
      <td>4.00G</td>
      <td>2.05M</td>
      <td>419K</td>
      <td>20170228</td>
      <td>5 min 0 s</td>
      <td>325562</td>
    </tr>
    <tr>
      <th>365</th>
      <td>how_do_nuclear_power_plants_work_m_v_ramana_an...</td>
      <td>11.5M</td>
      <td>4.01G</td>
      <td>2.02M</td>
      <td>414K</td>
      <td>20170508</td>
      <td>8 min 6 s</td>
      <td>199164</td>
    </tr>
    <tr>
      <th>366</th>
      <td>history_vs_richard_nixon_alex_gendler</td>
      <td>9.98M</td>
      <td>4.02G</td>
      <td>2.83M</td>
      <td>413K</td>
      <td>20150212</td>
      <td>5 min 39 s</td>
      <td>246222</td>
    </tr>
    <tr>
      <th>367</th>
      <td>what_happens_during_a_stroke_vaibhav_goswami</td>
      <td>10.5M</td>
      <td>4.03G</td>
      <td>1.61M</td>
      <td>412K</td>
      <td>20180201</td>
      <td>4 min 59 s</td>
      <td>294616</td>
    </tr>
    <tr>
      <th>368</th>
      <td>jabberwocky_one_of_literature_s_best_bits_of_n...</td>
      <td>10.7M</td>
      <td>4.04G</td>
      <td>412K</td>
      <td>412K</td>
      <td>20200917</td>
      <td>2 min 10 s</td>
      <td>690097</td>
    </tr>
    <tr>
      <th>369</th>
      <td>is_time_travel_possible_colin_stuart</td>
      <td>11.5M</td>
      <td>4.05G</td>
      <td>3.21M</td>
      <td>411K</td>
      <td>20131021</td>
      <td>5 min 3 s</td>
      <td>318690</td>
    </tr>
    <tr>
      <th>370</th>
      <td>what_happens_when_you_remove_the_hippocampus_s...</td>
      <td>7.69M</td>
      <td>4.06G</td>
      <td>3.21M</td>
      <td>411K</td>
      <td>20140826</td>
      <td>5 min 25 s</td>
      <td>198430</td>
    </tr>
    <tr>
      <th>371</th>
      <td>why_do_airlines_sell_too_many_tickets_nina_kli...</td>
      <td>6.11M</td>
      <td>4.07G</td>
      <td>2.00M</td>
      <td>410K</td>
      <td>20161220</td>
      <td>4 min 59 s</td>
      <td>171303</td>
    </tr>
    <tr>
      <th>372</th>
      <td>how_many_ways_are_there_to_prove_the_pythagore...</td>
      <td>7.39M</td>
      <td>4.07G</td>
      <td>2.00M</td>
      <td>410K</td>
      <td>20170911</td>
      <td>5 min 16 s</td>
      <td>195953</td>
    </tr>
    <tr>
      <th>373</th>
      <td>a_day_in_the_life_of_a_teenage_samurai_constan...</td>
      <td>36.1M</td>
      <td>4.11G</td>
      <td>817K</td>
      <td>408K</td>
      <td>20200622</td>
      <td>5 min 30 s</td>
      <td>918011</td>
    </tr>
    <tr>
      <th>374</th>
      <td>can_a_black_hole_be_destroyed_fabio_pacucci</td>
      <td>16.3M</td>
      <td>4.12G</td>
      <td>1.19M</td>
      <td>406K</td>
      <td>20190516</td>
      <td>5 min 6 s</td>
      <td>445075</td>
    </tr>
    <tr>
      <th>375</th>
      <td>what_really_happened_to_the_library_of_alexand...</td>
      <td>8.42M</td>
      <td>4.13G</td>
      <td>1.58M</td>
      <td>406K</td>
      <td>20180814</td>
      <td>4 min 52 s</td>
      <td>241730</td>
    </tr>
    <tr>
      <th>376</th>
      <td>is_there_any_truth_to_the_king_arthur_legends_...</td>
      <td>15.0M</td>
      <td>4.15G</td>
      <td>1.58M</td>
      <td>405K</td>
      <td>20180911</td>
      <td>5 min 42 s</td>
      <td>366928</td>
    </tr>
    <tr>
      <th>377</th>
      <td>the_history_of_marriage_alex_gendler</td>
      <td>8.24M</td>
      <td>4.16G</td>
      <td>3.17M</td>
      <td>405K</td>
      <td>20140213</td>
      <td>4 min 43 s</td>
      <td>243441</td>
    </tr>
    <tr>
      <th>378</th>
      <td>human_sperm_vs_the_sperm_whale_aatish_bhatia</td>
      <td>10.1M</td>
      <td>4.17G</td>
      <td>3.16M</td>
      <td>404K</td>
      <td>20130923</td>
      <td>4 min 17 s</td>
      <td>330327</td>
    </tr>
    <tr>
      <th>379</th>
      <td>the_hidden_treasures_of_timbuktu_elizabeth_cox</td>
      <td>20.6M</td>
      <td>4.19G</td>
      <td>402K</td>
      <td>402K</td>
      <td>20201022</td>
      <td>5 min 34 s</td>
      <td>516745</td>
    </tr>
    <tr>
      <th>380</th>
      <td>the_wacky_history_of_cell_theory_lauren_royal_...</td>
      <td>15.4M</td>
      <td>4.20G</td>
      <td>3.90M</td>
      <td>400K</td>
      <td>20120604</td>
      <td>6 min 11 s</td>
      <td>347113</td>
    </tr>
    <tr>
      <th>381</th>
      <td>will_we_ever_be_able_to_teleport_sajan_saini</td>
      <td>17.3M</td>
      <td>4.22G</td>
      <td>1.95M</td>
      <td>399K</td>
      <td>20170731</td>
      <td>5 min 37 s</td>
      <td>430268</td>
    </tr>
    <tr>
      <th>382</th>
      <td>how_to_make_your_writing_suspenseful_victoria_...</td>
      <td>8.44M</td>
      <td>4.23G</td>
      <td>1.55M</td>
      <td>397K</td>
      <td>20171031</td>
      <td>4 min 35 s</td>
      <td>257022</td>
    </tr>
    <tr>
      <th>383</th>
      <td>the_science_of_spiciness_rose_eveleth</td>
      <td>6.03M</td>
      <td>4.23G</td>
      <td>3.09M</td>
      <td>396K</td>
      <td>20140310</td>
      <td>3 min 54 s</td>
      <td>215829</td>
    </tr>
    <tr>
      <th>384</th>
      <td>can_you_solve_the_honeybee_riddle_dan_finkel</td>
      <td>17.3M</td>
      <td>4.25G</td>
      <td>788K</td>
      <td>394K</td>
      <td>20200730</td>
      <td>5 min 32 s</td>
      <td>435013</td>
    </tr>
    <tr>
      <th>385</th>
      <td>the_taino_myth_of_the_cursed_creator_bill_keegan</td>
      <td>10.9M</td>
      <td>4.26G</td>
      <td>783K</td>
      <td>392K</td>
      <td>20191104</td>
      <td>3 min 45 s</td>
      <td>404119</td>
    </tr>
    <tr>
      <th>386</th>
      <td>what_percentage_of_your_brain_do_you_use_richa...</td>
      <td>8.93M</td>
      <td>4.27G</td>
      <td>3.05M</td>
      <td>391K</td>
      <td>20140130</td>
      <td>5 min 15 s</td>
      <td>237677</td>
    </tr>
    <tr>
      <th>387</th>
      <td>the_hidden_meanings_of_yin_and_yang_john_bella...</td>
      <td>13.5M</td>
      <td>4.28G</td>
      <td>3.43M</td>
      <td>390K</td>
      <td>20130802</td>
      <td>4 min 9 s</td>
      <td>456381</td>
    </tr>
    <tr>
      <th>388</th>
      <td>can_you_survive_nuclear_fallout_brooke_buddeme...</td>
      <td>8.90M</td>
      <td>4.29G</td>
      <td>1.14M</td>
      <td>390K</td>
      <td>20190108</td>
      <td>5 min 24 s</td>
      <td>230137</td>
    </tr>
    <tr>
      <th>389</th>
      <td>where_do_math_symbols_come_from_john_david_wal...</td>
      <td>10.6M</td>
      <td>4.30G</td>
      <td>1.52M</td>
      <td>389K</td>
      <td>20171030</td>
      <td>4 min 29 s</td>
      <td>330083</td>
    </tr>
    <tr>
      <th>390</th>
      <td>football_physics_the_impossible_free_kick_erez...</td>
      <td>7.58M</td>
      <td>4.31G</td>
      <td>2.66M</td>
      <td>389K</td>
      <td>20150615</td>
      <td>3 min 32 s</td>
      <td>299407</td>
    </tr>
    <tr>
      <th>391</th>
      <td>check_your_intuition_the_birthday_problem_davi...</td>
      <td>13.3M</td>
      <td>4.32G</td>
      <td>1.87M</td>
      <td>383K</td>
      <td>20170504</td>
      <td>5 min 6 s</td>
      <td>365573</td>
    </tr>
    <tr>
      <th>392</th>
      <td>the_myth_of_jason_and_the_argonauts_iseult_gil...</td>
      <td>13.5M</td>
      <td>4.33G</td>
      <td>1.12M</td>
      <td>382K</td>
      <td>20190827</td>
      <td>5 min 14 s</td>
      <td>359008</td>
    </tr>
    <tr>
      <th>393</th>
      <td>the_magic_of_vedic_math_gaurav_tekriwal</td>
      <td>19.2M</td>
      <td>4.35G</td>
      <td>3.36M</td>
      <td>382K</td>
      <td>20130416</td>
      <td>9 min 44 s</td>
      <td>275425</td>
    </tr>
    <tr>
      <th>394</th>
      <td>can_100_renewable_energy_power_the_world_feder...</td>
      <td>9.36M</td>
      <td>4.36G</td>
      <td>1.49M</td>
      <td>382K</td>
      <td>20171207</td>
      <td>5 min 54 s</td>
      <td>221829</td>
    </tr>
    <tr>
      <th>395</th>
      <td>the_science_of_skin_color_angela_koine_flynn</td>
      <td>9.01M</td>
      <td>4.37G</td>
      <td>2.23M</td>
      <td>381K</td>
      <td>20160216</td>
      <td>4 min 53 s</td>
      <td>257855</td>
    </tr>
    <tr>
      <th>396</th>
      <td>the_physics_of_the_hardest_move_in_ballet_arle...</td>
      <td>7.90M</td>
      <td>4.38G</td>
      <td>2.23M</td>
      <td>380K</td>
      <td>20160322</td>
      <td>4 min 16 s</td>
      <td>258071</td>
    </tr>
    <tr>
      <th>397</th>
      <td>what_happens_if_you_cut_down_all_of_a_city_s_t...</td>
      <td>14.9M</td>
      <td>4.39G</td>
      <td>756K</td>
      <td>378K</td>
      <td>20200424</td>
      <td>5 min 25 s</td>
      <td>383483</td>
    </tr>
    <tr>
      <th>398</th>
      <td>a_day_in_the_life_of_an_ancient_babylonian_bus...</td>
      <td>22.4M</td>
      <td>4.41G</td>
      <td>378K</td>
      <td>378K</td>
      <td>20210107</td>
      <td>4 min 46 s</td>
      <td>656852</td>
    </tr>
    <tr>
      <th>399</th>
      <td>how_computer_memory_works_kanawat_senanan</td>
      <td>13.2M</td>
      <td>4.43G</td>
      <td>2.21M</td>
      <td>377K</td>
      <td>20160510</td>
      <td>5 min 4 s</td>
      <td>363807</td>
    </tr>
    <tr>
      <th>400</th>
      <td>how_do_investors_choose_stocks_richard_coffin</td>
      <td>15.1M</td>
      <td>4.44G</td>
      <td>376K</td>
      <td>376K</td>
      <td>20201110</td>
      <td>5 min 1 s</td>
      <td>421043</td>
    </tr>
    <tr>
      <th>401</th>
      <td>what_causes_constipation_heba_shaheed</td>
      <td>5.30M</td>
      <td>4.45G</td>
      <td>1.46M</td>
      <td>375K</td>
      <td>20180507</td>
      <td>3 min 32 s</td>
      <td>209213</td>
    </tr>
    <tr>
      <th>402</th>
      <td>the_life_cycle_of_a_t_shirt_angel_chang</td>
      <td>12.3M</td>
      <td>4.46G</td>
      <td>1.82M</td>
      <td>373K</td>
      <td>20170905</td>
      <td>6 min 3 s</td>
      <td>283126</td>
    </tr>
    <tr>
      <th>403</th>
      <td>how_a_single_celled_organism_almost_wiped_out_...</td>
      <td>7.87M</td>
      <td>4.47G</td>
      <td>2.19M</td>
      <td>373K</td>
      <td>20160811</td>
      <td>4 min 13 s</td>
      <td>260691</td>
    </tr>
    <tr>
      <th>404</th>
      <td>three_ways_the_universe_could_end_venus_keus</td>
      <td>7.53M</td>
      <td>4.47G</td>
      <td>1.09M</td>
      <td>373K</td>
      <td>20190219</td>
      <td>4 min 46 s</td>
      <td>220333</td>
    </tr>
    <tr>
      <th>405</th>
      <td>how_to_spot_a_misleading_graph_lea_gaslowitz</td>
      <td>8.34M</td>
      <td>4.48G</td>
      <td>1.82M</td>
      <td>372K</td>
      <td>20170706</td>
      <td>4 min 9 s</td>
      <td>280321</td>
    </tr>
    <tr>
      <th>406</th>
      <td>how_one_scientist_averted_a_national_health_cr...</td>
      <td>13.0M</td>
      <td>4.50G</td>
      <td>1.45M</td>
      <td>372K</td>
      <td>20180607</td>
      <td>5 min 31 s</td>
      <td>328150</td>
    </tr>
    <tr>
      <th>407</th>
      <td>why_should_you_read_the_handmaid_s_tale_naomi_...</td>
      <td>11.2M</td>
      <td>4.51G</td>
      <td>1.45M</td>
      <td>372K</td>
      <td>20180308</td>
      <td>5 min 4 s</td>
      <td>308771</td>
    </tr>
    <tr>
      <th>408</th>
      <td>the_princess_who_rewrote_history_leonora_neville</td>
      <td>7.54M</td>
      <td>4.51G</td>
      <td>1.09M</td>
      <td>372K</td>
      <td>20181022</td>
      <td>4 min 57 s</td>
      <td>212489</td>
    </tr>
    <tr>
      <th>409</th>
      <td>why_should_you_read_virginia_woolf_iseult_gill...</td>
      <td>15.7M</td>
      <td>4.53G</td>
      <td>1.45M</td>
      <td>371K</td>
      <td>20171005</td>
      <td>6 min 2 s</td>
      <td>363000</td>
    </tr>
    <tr>
      <th>410</th>
      <td>why_can_t_some_birds_fly_gillian_gibb</td>
      <td>6.71M</td>
      <td>4.54G</td>
      <td>1.08M</td>
      <td>367K</td>
      <td>20181018</td>
      <td>4 min 31 s</td>
      <td>206979</td>
    </tr>
    <tr>
      <th>411</th>
      <td>the_worlds_largest_organism_alex_rosenthal</td>
      <td>23.3M</td>
      <td>4.56G</td>
      <td>366K</td>
      <td>366K</td>
      <td>20201207</td>
      <td>6 min 27 s</td>
      <td>505085</td>
    </tr>
    <tr>
      <th>412</th>
      <td>the_wild_world_of_carnivorous_plants_kenny_coogan</td>
      <td>7.90M</td>
      <td>4.57G</td>
      <td>1.07M</td>
      <td>366K</td>
      <td>20190411</td>
      <td>5 min 10 s</td>
      <td>213259</td>
    </tr>
    <tr>
      <th>413</th>
      <td>why_do_you_get_a_fever_when_you_re_sick_christ...</td>
      <td>19.7M</td>
      <td>4.59G</td>
      <td>366K</td>
      <td>366K</td>
      <td>20201112</td>
      <td>5 min 37 s</td>
      <td>490166</td>
    </tr>
    <tr>
      <th>414</th>
      <td>how_do_ventilators_work_alex_gendler</td>
      <td>12.1M</td>
      <td>4.60G</td>
      <td>731K</td>
      <td>365K</td>
      <td>20200521</td>
      <td>5 min 41 s</td>
      <td>297437</td>
    </tr>
    <tr>
      <th>415</th>
      <td>why_is_mount_everest_so_tall_michele_koppes</td>
      <td>7.35M</td>
      <td>4.60G</td>
      <td>2.13M</td>
      <td>364K</td>
      <td>20160407</td>
      <td>4 min 52 s</td>
      <td>210967</td>
    </tr>
    <tr>
      <th>416</th>
      <td>how_smart_are_dolphins_lori_marino</td>
      <td>9.95M</td>
      <td>4.61G</td>
      <td>2.49M</td>
      <td>364K</td>
      <td>20150831</td>
      <td>4 min 50 s</td>
      <td>286775</td>
    </tr>
    <tr>
      <th>417</th>
      <td>vampires_folklore_fantasy_and_fact_michael_molina</td>
      <td>11.5M</td>
      <td>4.63G</td>
      <td>2.84M</td>
      <td>364K</td>
      <td>20131029</td>
      <td>6 min 56 s</td>
      <td>232617</td>
    </tr>
    <tr>
      <th>418</th>
      <td>how_does_your_body_know_you_re_full_hilary_coller</td>
      <td>8.23M</td>
      <td>4.63G</td>
      <td>1.42M</td>
      <td>364K</td>
      <td>20171113</td>
      <td>4 min 33 s</td>
      <td>252834</td>
    </tr>
    <tr>
      <th>419</th>
      <td>sex_determination_more_complicated_than_you_th...</td>
      <td>17.4M</td>
      <td>4.65G</td>
      <td>3.54M</td>
      <td>363K</td>
      <td>20120423</td>
      <td>5 min 45 s</td>
      <td>423093</td>
    </tr>
    <tr>
      <th>420</th>
      <td>how_do_crystals_work_graham_baird</td>
      <td>12.4M</td>
      <td>4.66G</td>
      <td>1.06M</td>
      <td>362K</td>
      <td>20190618</td>
      <td>5 min 6 s</td>
      <td>339964</td>
    </tr>
    <tr>
      <th>421</th>
      <td>why_should_you_read_edgar_allan_poe_scott_peeples</td>
      <td>12.5M</td>
      <td>4.67G</td>
      <td>1.06M</td>
      <td>362K</td>
      <td>20180918</td>
      <td>4 min 55 s</td>
      <td>353516</td>
    </tr>
    <tr>
      <th>422</th>
      <td>the_imaginary_king_who_changed_the_real_world_...</td>
      <td>12.1M</td>
      <td>4.69G</td>
      <td>715K</td>
      <td>357K</td>
      <td>20200319</td>
      <td>5 min 33 s</td>
      <td>305647</td>
    </tr>
    <tr>
      <th>423</th>
      <td>the_maya_myth_of_the_morning_star</td>
      <td>8.79M</td>
      <td>4.69G</td>
      <td>713K</td>
      <td>356K</td>
      <td>20191021</td>
      <td>4 min 35 s</td>
      <td>267260</td>
    </tr>
    <tr>
      <th>424</th>
      <td>the_wicked_wit_of_jane_austen_iseult_gillespie</td>
      <td>15.8M</td>
      <td>4.71G</td>
      <td>1.04M</td>
      <td>356K</td>
      <td>20190321</td>
      <td>5 min 0 s</td>
      <td>440091</td>
    </tr>
    <tr>
      <th>425</th>
      <td>why_should_you_read_dantes_divine_comedy_sheil...</td>
      <td>12.2M</td>
      <td>4.72G</td>
      <td>712K</td>
      <td>356K</td>
      <td>20191010</td>
      <td>5 min 9 s</td>
      <td>330116</td>
    </tr>
    <tr>
      <th>426</th>
      <td>poison_vs_venom_what_s_the_difference_rose_eve...</td>
      <td>7.73M</td>
      <td>4.73G</td>
      <td>2.78M</td>
      <td>356K</td>
      <td>20140220</td>
      <td>3 min 55 s</td>
      <td>275734</td>
    </tr>
    <tr>
      <th>427</th>
      <td>building_the_world_s_largest_and_most_controve...</td>
      <td>22.3M</td>
      <td>4.75G</td>
      <td>354K</td>
      <td>354K</td>
      <td>20201210</td>
      <td>5 min 37 s</td>
      <td>555728</td>
    </tr>
    <tr>
      <th>428</th>
      <td>why_do_we_hiccup_john_cameron</td>
      <td>10.1M</td>
      <td>4.76G</td>
      <td>2.07M</td>
      <td>354K</td>
      <td>20160728</td>
      <td>4 min 49 s</td>
      <td>292224</td>
    </tr>
    <tr>
      <th>429</th>
      <td>why_are_we_so_attached_to_our_things_christian...</td>
      <td>8.22M</td>
      <td>4.77G</td>
      <td>1.72M</td>
      <td>353K</td>
      <td>20161227</td>
      <td>4 min 34 s</td>
      <td>251527</td>
    </tr>
    <tr>
      <th>430</th>
      <td>how_the_heart_actually_pumps_blood_edmond_hui</td>
      <td>6.19M</td>
      <td>4.78G</td>
      <td>2.75M</td>
      <td>353K</td>
      <td>20140520</td>
      <td>4 min 27 s</td>
      <td>194216</td>
    </tr>
    <tr>
      <th>431</th>
      <td>what_is_deja_vu_what_is_deja_vu_michael_molina</td>
      <td>5.50M</td>
      <td>4.78G</td>
      <td>3.09M</td>
      <td>352K</td>
      <td>20130828</td>
      <td>3 min 54 s</td>
      <td>196415</td>
    </tr>
    <tr>
      <th>432</th>
      <td>what_orwellian_really_means_noah_tavlin</td>
      <td>18.6M</td>
      <td>4.80G</td>
      <td>2.06M</td>
      <td>351K</td>
      <td>20151001</td>
      <td>5 min 31 s</td>
      <td>471142</td>
    </tr>
    <tr>
      <th>433</th>
      <td>what_happened_when_we_all_stopped_narrated_by_...</td>
      <td>6.08M</td>
      <td>4.80G</td>
      <td>703K</td>
      <td>351K</td>
      <td>20200604</td>
      <td>3 min 15 s</td>
      <td>260626</td>
    </tr>
    <tr>
      <th>434</th>
      <td>the_strange_case_of_the_cyclops_sheep_tien_nguyen</td>
      <td>6.87M</td>
      <td>4.81G</td>
      <td>1.37M</td>
      <td>351K</td>
      <td>20171003</td>
      <td>4 min 40 s</td>
      <td>205550</td>
    </tr>
    <tr>
      <th>435</th>
      <td>the_surprising_cause_of_stomach_ulcers_rusha_modi</td>
      <td>11.6M</td>
      <td>4.82G</td>
      <td>1.37M</td>
      <td>350K</td>
      <td>20170928</td>
      <td>5 min 34 s</td>
      <td>290682</td>
    </tr>
    <tr>
      <th>436</th>
      <td>can_you_outsmart_the_fallacy_that_fooled_a_gen...</td>
      <td>19.7M</td>
      <td>4.84G</td>
      <td>700K</td>
      <td>350K</td>
      <td>20200810</td>
      <td>5 min 30 s</td>
      <td>499940</td>
    </tr>
    <tr>
      <th>437</th>
      <td>claws_vs_nails_matthew_borths</td>
      <td>7.38M</td>
      <td>4.85G</td>
      <td>700K</td>
      <td>350K</td>
      <td>20191029</td>
      <td>5 min 10 s</td>
      <td>199593</td>
    </tr>
    <tr>
      <th>438</th>
      <td>how_smart_are_orangutans_lu_gao</td>
      <td>6.85M</td>
      <td>4.86G</td>
      <td>2.05M</td>
      <td>349K</td>
      <td>20160830</td>
      <td>4 min 32 s</td>
      <td>211187</td>
    </tr>
    <tr>
      <th>439</th>
      <td>the_mathematical_secrets_of_pascals_triangle_w...</td>
      <td>6.80M</td>
      <td>4.86G</td>
      <td>2.04M</td>
      <td>348K</td>
      <td>20150915</td>
      <td>4 min 49 s</td>
      <td>196970</td>
    </tr>
    <tr>
      <th>440</th>
      <td>why_do_blood_types_matter_natalie_s_hodge</td>
      <td>9.45M</td>
      <td>4.87G</td>
      <td>2.37M</td>
      <td>347K</td>
      <td>20150629</td>
      <td>4 min 41 s</td>
      <td>281815</td>
    </tr>
    <tr>
      <th>441</th>
      <td>the_arctic_vs_the_antarctic_camille_seaman</td>
      <td>6.20M</td>
      <td>4.88G</td>
      <td>3.05M</td>
      <td>347K</td>
      <td>20130819</td>
      <td>4 min 24 s</td>
      <td>196997</td>
    </tr>
    <tr>
      <th>442</th>
      <td>what_is_zeno_s_dichotomy_paradox_colm_kelleher</td>
      <td>8.55M</td>
      <td>4.89G</td>
      <td>3.04M</td>
      <td>346K</td>
      <td>20130415</td>
      <td>4 min 11 s</td>
      <td>285321</td>
    </tr>
    <tr>
      <th>443</th>
      <td>how_does_the_nobel_peace_prize_work_adeline_cu...</td>
      <td>11.7M</td>
      <td>4.90G</td>
      <td>1.69M</td>
      <td>346K</td>
      <td>20161006</td>
      <td>6 min 14 s</td>
      <td>261487</td>
    </tr>
    <tr>
      <th>444</th>
      <td>the_mysterious_science_of_pain_joshua_w_pate</td>
      <td>10.8M</td>
      <td>4.91G</td>
      <td>1.01M</td>
      <td>345K</td>
      <td>20190520</td>
      <td>5 min 2 s</td>
      <td>299754</td>
    </tr>
    <tr>
      <th>445</th>
      <td>a_day_in_the_life_of_an_aztec_midwife_kay_read</td>
      <td>7.59M</td>
      <td>4.92G</td>
      <td>690K</td>
      <td>345K</td>
      <td>20200512</td>
      <td>4 min 35 s</td>
      <td>231125</td>
    </tr>
    <tr>
      <th>446</th>
      <td>how_can_you_change_someone_s_mind_hint_facts_a...</td>
      <td>10.5M</td>
      <td>4.93G</td>
      <td>1.34M</td>
      <td>344K</td>
      <td>20180726</td>
      <td>4 min 39 s</td>
      <td>314710</td>
    </tr>
    <tr>
      <th>447</th>
      <td>inside_the_killer_whale_matriarchy_darren_croft</td>
      <td>13.1M</td>
      <td>4.94G</td>
      <td>1.00M</td>
      <td>343K</td>
      <td>20181211</td>
      <td>5 min 3 s</td>
      <td>362626</td>
    </tr>
    <tr>
      <th>448</th>
      <td>what_does_this_symbol_actually_mean_adrian_tre...</td>
      <td>8.34M</td>
      <td>4.95G</td>
      <td>1.67M</td>
      <td>342K</td>
      <td>20170105</td>
      <td>4 min 10 s</td>
      <td>279085</td>
    </tr>
    <tr>
      <th>449</th>
      <td>what_is_a_calorie_emma_bryce</td>
      <td>5.65M</td>
      <td>4.95G</td>
      <td>2.32M</td>
      <td>340K</td>
      <td>20150713</td>
      <td>4 min 11 s</td>
      <td>188710</td>
    </tr>
    <tr>
      <th>450</th>
      <td>the_science_behind_the_myth_homer_s_odyssey_ma...</td>
      <td>6.50M</td>
      <td>4.96G</td>
      <td>1.99M</td>
      <td>339K</td>
      <td>20151110</td>
      <td>4 min 31 s</td>
      <td>200586</td>
    </tr>
    <tr>
      <th>451</th>
      <td>the_meaning_of_life_according_to_simone_de_bea...</td>
      <td>12.3M</td>
      <td>4.97G</td>
      <td>678K</td>
      <td>339K</td>
      <td>20200310</td>
      <td>5 min 10 s</td>
      <td>330890</td>
    </tr>
    <tr>
      <th>452</th>
      <td>what_makes_tuberculosis_tb_the_world_s_most_in...</td>
      <td>7.24M</td>
      <td>4.98G</td>
      <td>0.99M</td>
      <td>339K</td>
      <td>20190627</td>
      <td>5 min 17 s</td>
      <td>191307</td>
    </tr>
    <tr>
      <th>453</th>
      <td>the_murder_of_ancient_alexandria_s_greatest_sc...</td>
      <td>13.5M</td>
      <td>4.99G</td>
      <td>0.99M</td>
      <td>338K</td>
      <td>20190801</td>
      <td>5 min 4 s</td>
      <td>371743</td>
    </tr>
    <tr>
      <th>454</th>
      <td>who_am_i_a_philosophical_inquiry_amy_adkins</td>
      <td>10.6M</td>
      <td>5.00G</td>
      <td>2.31M</td>
      <td>338K</td>
      <td>20150811</td>
      <td>4 min 58 s</td>
      <td>299056</td>
    </tr>
    <tr>
      <th>455</th>
      <td>the_paradox_of_value_akshita_agarwal</td>
      <td>7.73M</td>
      <td>5.01G</td>
      <td>1.98M</td>
      <td>338K</td>
      <td>20160829</td>
      <td>3 min 45 s</td>
      <td>287741</td>
    </tr>
    <tr>
      <th>456</th>
      <td>how_does_impeachment_work_alex_gendler</td>
      <td>11.3M</td>
      <td>5.02G</td>
      <td>1.64M</td>
      <td>337K</td>
      <td>20170824</td>
      <td>5 min 12 s</td>
      <td>304335</td>
    </tr>
    <tr>
      <th>457</th>
      <td>are_elvish_klingon_dothraki_and_na_vi_real_lan...</td>
      <td>8.70M</td>
      <td>5.03G</td>
      <td>2.62M</td>
      <td>336K</td>
      <td>20130926</td>
      <td>5 min 20 s</td>
      <td>227807</td>
    </tr>
    <tr>
      <th>458</th>
      <td>vultures_the_acid_puking_plague_busting_heroes...</td>
      <td>9.34M</td>
      <td>5.04G</td>
      <td>665K</td>
      <td>333K</td>
      <td>20200224</td>
      <td>5 min 5 s</td>
      <td>256151</td>
    </tr>
    <tr>
      <th>459</th>
      <td>the_ferocious_predatory_dinosaurs_of_cretaceou...</td>
      <td>8.82M</td>
      <td>5.05G</td>
      <td>1.62M</td>
      <td>333K</td>
      <td>20170606</td>
      <td>4 min 19 s</td>
      <td>284886</td>
    </tr>
    <tr>
      <th>460</th>
      <td>are_we_living_in_a_simulation_zohreh_davoudi</td>
      <td>5.98M</td>
      <td>5.05G</td>
      <td>665K</td>
      <td>332K</td>
      <td>20191008</td>
      <td>4 min 23 s</td>
      <td>190104</td>
    </tr>
    <tr>
      <th>461</th>
      <td>why_should_you_read_don_quixote_ilan_stavans</td>
      <td>11.9M</td>
      <td>5.06G</td>
      <td>993K</td>
      <td>331K</td>
      <td>20181008</td>
      <td>5 min 38 s</td>
      <td>296197</td>
    </tr>
    <tr>
      <th>462</th>
      <td>why_do_some_people_go_bald_sarthak_sinha</td>
      <td>7.62M</td>
      <td>5.07G</td>
      <td>2.25M</td>
      <td>329K</td>
      <td>20150825</td>
      <td>4 min 48 s</td>
      <td>221230</td>
    </tr>
    <tr>
      <th>463</th>
      <td>what_causes_antibiotic_resistance_kevin_wu</td>
      <td>8.13M</td>
      <td>5.08G</td>
      <td>2.57M</td>
      <td>329K</td>
      <td>20140807</td>
      <td>4 min 34 s</td>
      <td>248307</td>
    </tr>
    <tr>
      <th>464</th>
      <td>the_most_groundbreaking_scientist_you_ve_never...</td>
      <td>6.87M</td>
      <td>5.09G</td>
      <td>2.56M</td>
      <td>328K</td>
      <td>20131001</td>
      <td>4 min 32 s</td>
      <td>211103</td>
    </tr>
    <tr>
      <th>465</th>
      <td>why_is_ketchup_so_hard_to_pour_george_zaidan</td>
      <td>10.0M</td>
      <td>5.10G</td>
      <td>2.56M</td>
      <td>328K</td>
      <td>20140408</td>
      <td>4 min 28 s</td>
      <td>312501</td>
    </tr>
    <tr>
      <th>466</th>
      <td>what_causes_an_economic_recession_richard_coffin</td>
      <td>7.43M</td>
      <td>5.10G</td>
      <td>656K</td>
      <td>328K</td>
      <td>20191015</td>
      <td>5 min 4 s</td>
      <td>205039</td>
    </tr>
    <tr>
      <th>467</th>
      <td>the_strange_history_of_the_world_s_most_stolen...</td>
      <td>23.4M</td>
      <td>5.13G</td>
      <td>327K</td>
      <td>327K</td>
      <td>20201221</td>
      <td>5 min 37 s</td>
      <td>581735</td>
    </tr>
    <tr>
      <th>468</th>
      <td>how_your_muscular_system_works_emma_bryce</td>
      <td>8.63M</td>
      <td>5.13G</td>
      <td>1.27M</td>
      <td>326K</td>
      <td>20171026</td>
      <td>4 min 44 s</td>
      <td>254300</td>
    </tr>
    <tr>
      <th>469</th>
      <td>how_to_defeat_a_dragon_with_math_garth_sundem</td>
      <td>8.27M</td>
      <td>5.14G</td>
      <td>2.86M</td>
      <td>325K</td>
      <td>20130115</td>
      <td>3 min 46 s</td>
      <td>306652</td>
    </tr>
    <tr>
      <th>470</th>
      <td>how_to_understand_power_eric_liu</td>
      <td>14.7M</td>
      <td>5.16G</td>
      <td>2.22M</td>
      <td>325K</td>
      <td>20141104</td>
      <td>7 min 1 s</td>
      <td>292751</td>
    </tr>
    <tr>
      <th>471</th>
      <td>can_you_outsmart_the_fallacy_that_started_a_wi...</td>
      <td>16.8M</td>
      <td>5.17G</td>
      <td>324K</td>
      <td>324K</td>
      <td>20201026</td>
      <td>4 min 23 s</td>
      <td>534032</td>
    </tr>
    <tr>
      <th>472</th>
      <td>what_makes_a_poem_a_poem_melissa_kovacs</td>
      <td>15.5M</td>
      <td>5.19G</td>
      <td>1.58M</td>
      <td>324K</td>
      <td>20170320</td>
      <td>5 min 19 s</td>
      <td>405613</td>
    </tr>
    <tr>
      <th>473</th>
      <td>what_gives_a_dollar_bill_its_value_doug_levinson</td>
      <td>7.24M</td>
      <td>5.20G</td>
      <td>2.53M</td>
      <td>324K</td>
      <td>20140623</td>
      <td>3 min 51 s</td>
      <td>262357</td>
    </tr>
    <tr>
      <th>474</th>
      <td>the_true_story_of_sacajawea_karen_mensing</td>
      <td>5.88M</td>
      <td>5.20G</td>
      <td>2.84M</td>
      <td>323K</td>
      <td>20130808</td>
      <td>3 min 40 s</td>
      <td>223908</td>
    </tr>
    <tr>
      <th>475</th>
      <td>should_we_eat_bugs_emma_bryce</td>
      <td>10.2M</td>
      <td>5.21G</td>
      <td>2.52M</td>
      <td>322K</td>
      <td>20140102</td>
      <td>4 min 51 s</td>
      <td>294474</td>
    </tr>
    <tr>
      <th>476</th>
      <td>the_chemistry_of_cookies_stephanie_warren</td>
      <td>6.33M</td>
      <td>5.22G</td>
      <td>2.51M</td>
      <td>322K</td>
      <td>20131119</td>
      <td>4 min 29 s</td>
      <td>197001</td>
    </tr>
    <tr>
      <th>477</th>
      <td>history_vs_augustus_peta_greenfield_alex_gendler</td>
      <td>8.30M</td>
      <td>5.23G</td>
      <td>1.25M</td>
      <td>321K</td>
      <td>20180717</td>
      <td>5 min 10 s</td>
      <td>224473</td>
    </tr>
    <tr>
      <th>478</th>
      <td>turbulence_one_of_the_great_unsolved_mysteries...</td>
      <td>13.1M</td>
      <td>5.24G</td>
      <td>961K</td>
      <td>320K</td>
      <td>20190415</td>
      <td>5 min 27 s</td>
      <td>335017</td>
    </tr>
    <tr>
      <th>479</th>
      <td>ugly_history_japanese_american_incarceration_c...</td>
      <td>9.86M</td>
      <td>5.25G</td>
      <td>639K</td>
      <td>320K</td>
      <td>20191001</td>
      <td>5 min 45 s</td>
      <td>239245</td>
    </tr>
    <tr>
      <th>480</th>
      <td>what_if_cracks_in_concrete_could_fix_themselve...</td>
      <td>8.21M</td>
      <td>5.26G</td>
      <td>957K</td>
      <td>319K</td>
      <td>20181016</td>
      <td>4 min 39 s</td>
      <td>246712</td>
    </tr>
    <tr>
      <th>481</th>
      <td>light_seconds_light_years_light_centuries_how_...</td>
      <td>16.7M</td>
      <td>5.27G</td>
      <td>2.18M</td>
      <td>319K</td>
      <td>20141009</td>
      <td>5 min 29 s</td>
      <td>425445</td>
    </tr>
    <tr>
      <th>482</th>
      <td>can_you_solve_the_multiverse_rescue_mission_ri...</td>
      <td>13.3M</td>
      <td>5.28G</td>
      <td>955K</td>
      <td>318K</td>
      <td>20190815</td>
      <td>4 min 24 s</td>
      <td>421021</td>
    </tr>
    <tr>
      <th>483</th>
      <td>what_s_invisible_more_than_you_think_john_lloyd</td>
      <td>19.8M</td>
      <td>5.30G</td>
      <td>2.76M</td>
      <td>314K</td>
      <td>20120926</td>
      <td>8 min 47 s</td>
      <td>314261</td>
    </tr>
    <tr>
      <th>484</th>
      <td>the_irish_myth_of_the_giant_s_causeway_iseult_...</td>
      <td>7.27M</td>
      <td>5.31G</td>
      <td>1.23M</td>
      <td>314K</td>
      <td>20180612</td>
      <td>3 min 48 s</td>
      <td>266537</td>
    </tr>
    <tr>
      <th>485</th>
      <td>why_does_your_voice_change_as_you_get_older_sh...</td>
      <td>11.9M</td>
      <td>5.32G</td>
      <td>1.22M</td>
      <td>312K</td>
      <td>20180802</td>
      <td>5 min 5 s</td>
      <td>325483</td>
    </tr>
    <tr>
      <th>486</th>
      <td>how_do_ocean_currents_work_jennifer_verduin</td>
      <td>10.2M</td>
      <td>5.33G</td>
      <td>937K</td>
      <td>312K</td>
      <td>20190131</td>
      <td>4 min 33 s</td>
      <td>311859</td>
    </tr>
    <tr>
      <th>487</th>
      <td>oxygens_surprisingly_complex_journey_through_y...</td>
      <td>10.3M</td>
      <td>5.34G</td>
      <td>1.52M</td>
      <td>311K</td>
      <td>20170413</td>
      <td>5 min 9 s</td>
      <td>278473</td>
    </tr>
    <tr>
      <th>488</th>
      <td>the_life_cycle_of_a_neutron_star_david_lunney</td>
      <td>11.0M</td>
      <td>5.35G</td>
      <td>931K</td>
      <td>310K</td>
      <td>20181120</td>
      <td>5 min 16 s</td>
      <td>292525</td>
    </tr>
    <tr>
      <th>489</th>
      <td>how_do_hard_drives_work_kanawat_senanan</td>
      <td>17.8M</td>
      <td>5.37G</td>
      <td>1.82M</td>
      <td>310K</td>
      <td>20151029</td>
      <td>5 min 11 s</td>
      <td>479501</td>
    </tr>
    <tr>
      <th>490</th>
      <td>what_causes_bad_breath_mel_rosenberg</td>
      <td>8.75M</td>
      <td>5.38G</td>
      <td>2.11M</td>
      <td>309K</td>
      <td>20150331</td>
      <td>4 min 13 s</td>
      <td>289444</td>
    </tr>
    <tr>
      <th>491</th>
      <td>did_ancient_troy_really_exist_einav_zamir_dembin</td>
      <td>9.00M</td>
      <td>5.39G</td>
      <td>1.20M</td>
      <td>308K</td>
      <td>20180731</td>
      <td>4 min 37 s</td>
      <td>271638</td>
    </tr>
    <tr>
      <th>492</th>
      <td>how_do_you_decide_where_to_go_in_a_zombie_apoc...</td>
      <td>5.98M</td>
      <td>5.39G</td>
      <td>2.70M</td>
      <td>307K</td>
      <td>20130603</td>
      <td>3 min 37 s</td>
      <td>229947</td>
    </tr>
    <tr>
      <th>493</th>
      <td>the_complex_geometry_of_islamic_design_eric_broug</td>
      <td>17.1M</td>
      <td>5.41G</td>
      <td>2.08M</td>
      <td>304K</td>
      <td>20150514</td>
      <td>5 min 6 s</td>
      <td>467155</td>
    </tr>
    <tr>
      <th>494</th>
      <td>what_is_the_universe_expanding_into_sajan_saini</td>
      <td>12.3M</td>
      <td>5.42G</td>
      <td>1.18M</td>
      <td>303K</td>
      <td>20180906</td>
      <td>6 min 6 s</td>
      <td>281061</td>
    </tr>
    <tr>
      <th>495</th>
      <td>why_is_pneumonia_so_dangerous_eve_gaus_and_van...</td>
      <td>15.3M</td>
      <td>5.44G</td>
      <td>302K</td>
      <td>302K</td>
      <td>20201130</td>
      <td>4 min 27 s</td>
      <td>479330</td>
    </tr>
    <tr>
      <th>496</th>
      <td>the_otherworldly_creatures_in_the_ocean_s_deep...</td>
      <td>7.37M</td>
      <td>5.45G</td>
      <td>1.76M</td>
      <td>301K</td>
      <td>20160524</td>
      <td>5 min 2 s</td>
      <td>204415</td>
    </tr>
    <tr>
      <th>497</th>
      <td>whats_the_big_deal_with_gluten_william_d_chey</td>
      <td>7.71M</td>
      <td>5.45G</td>
      <td>2.04M</td>
      <td>299K</td>
      <td>20150602</td>
      <td>5 min 17 s</td>
      <td>204054</td>
    </tr>
    <tr>
      <th>498</th>
      <td>how_pandemics_spread</td>
      <td>18.7M</td>
      <td>5.47G</td>
      <td>2.90M</td>
      <td>297K</td>
      <td>20120311</td>
      <td>7 min 59 s</td>
      <td>327374</td>
    </tr>
    <tr>
      <th>499</th>
      <td>how_does_fracking_work_mia_nacamulli</td>
      <td>8.50M</td>
      <td>5.48G</td>
      <td>1.45M</td>
      <td>297K</td>
      <td>20170713</td>
      <td>6 min 3 s</td>
      <td>195944</td>
    </tr>
    <tr>
      <th>500</th>
      <td>which_voting_system_is_the_best_alex_gendler</td>
      <td>18.0M</td>
      <td>5.50G</td>
      <td>589K</td>
      <td>294K</td>
      <td>20200611</td>
      <td>5 min 32 s</td>
      <td>454439</td>
    </tr>
    <tr>
      <th>501</th>
      <td>frida_kahlo_the_woman_behind_the_legend_iseult...</td>
      <td>11.5M</td>
      <td>5.51G</td>
      <td>883K</td>
      <td>294K</td>
      <td>20190328</td>
      <td>4 min 6 s</td>
      <td>391551</td>
    </tr>
    <tr>
      <th>502</th>
      <td>how_big_is_infinity_dennis_wildfogel</td>
      <td>11.5M</td>
      <td>5.52G</td>
      <td>2.87M</td>
      <td>294K</td>
      <td>20120806</td>
      <td>7 min 12 s</td>
      <td>223855</td>
    </tr>
    <tr>
      <th>503</th>
      <td>the_science_of_milk_jonathan_j_o_sullivan</td>
      <td>9.02M</td>
      <td>5.53G</td>
      <td>1.43M</td>
      <td>293K</td>
      <td>20170131</td>
      <td>5 min 23 s</td>
      <td>233789</td>
    </tr>
    <tr>
      <th>504</th>
      <td>the_secret_student_resistance_to_hitler_iseult...</td>
      <td>9.19M</td>
      <td>5.54G</td>
      <td>876K</td>
      <td>292K</td>
      <td>20190903</td>
      <td>5 min 32 s</td>
      <td>231949</td>
    </tr>
    <tr>
      <th>505</th>
      <td>the_problem_with_the_u_s_bail_system_camilo_ra...</td>
      <td>23.8M</td>
      <td>5.56G</td>
      <td>292K</td>
      <td>292K</td>
      <td>20200929</td>
      <td>6 min 29 s</td>
      <td>513377</td>
    </tr>
    <tr>
      <th>506</th>
      <td>why_should_you_read_kurt_vonnegut_mia_nacamulli</td>
      <td>10.6M</td>
      <td>5.57G</td>
      <td>875K</td>
      <td>292K</td>
      <td>20181129</td>
      <td>5 min 23 s</td>
      <td>276133</td>
    </tr>
    <tr>
      <th>507</th>
      <td>how_memories_form_and_how_we_lose_them_cathari...</td>
      <td>7.48M</td>
      <td>5.58G</td>
      <td>1.71M</td>
      <td>291K</td>
      <td>20150924</td>
      <td>4 min 19 s</td>
      <td>241678</td>
    </tr>
    <tr>
      <th>508</th>
      <td>how_languages_evolve_alex_gendler</td>
      <td>7.30M</td>
      <td>5.59G</td>
      <td>2.27M</td>
      <td>291K</td>
      <td>20140527</td>
      <td>4 min 2 s</td>
      <td>252462</td>
    </tr>
    <tr>
      <th>509</th>
      <td>the_road_not_taken_by_robert_frost</td>
      <td>3.83M</td>
      <td>5.59G</td>
      <td>868K</td>
      <td>289K</td>
      <td>20190202</td>
      <td>2 min 11 s</td>
      <td>244770</td>
    </tr>
    <tr>
      <th>510</th>
      <td>why_is_biodiversity_so_important_kim_preshoff</td>
      <td>10.6M</td>
      <td>5.60G</td>
      <td>1.98M</td>
      <td>289K</td>
      <td>20150420</td>
      <td>4 min 18 s</td>
      <td>343694</td>
    </tr>
    <tr>
      <th>511</th>
      <td>who_is_sherlock_holmes_neil_mccaw</td>
      <td>8.34M</td>
      <td>5.61G</td>
      <td>1.69M</td>
      <td>289K</td>
      <td>20160505</td>
      <td>4 min 53 s</td>
      <td>238458</td>
    </tr>
    <tr>
      <th>512</th>
      <td>why_its_so_hard_to_cure_hiv_aids_janet_iwasa</td>
      <td>7.72M</td>
      <td>5.61G</td>
      <td>1.97M</td>
      <td>288K</td>
      <td>20150316</td>
      <td>4 min 30 s</td>
      <td>239262</td>
    </tr>
    <tr>
      <th>513</th>
      <td>einstein_s_miracle_year_larry_lagerstrom</td>
      <td>7.55M</td>
      <td>5.62G</td>
      <td>1.96M</td>
      <td>286K</td>
      <td>20150106</td>
      <td>5 min 15 s</td>
      <td>200786</td>
    </tr>
    <tr>
      <th>514</th>
      <td>one_of_the_most_difficult_words_to_translate_k...</td>
      <td>6.00M</td>
      <td>5.63G</td>
      <td>1.68M</td>
      <td>286K</td>
      <td>20160906</td>
      <td>3 min 47 s</td>
      <td>221461</td>
    </tr>
    <tr>
      <th>515</th>
      <td>how_tall_can_a_tree_grow_valentin_hammoudi</td>
      <td>8.21M</td>
      <td>5.64G</td>
      <td>858K</td>
      <td>286K</td>
      <td>20190314</td>
      <td>4 min 45 s</td>
      <td>241682</td>
    </tr>
    <tr>
      <th>516</th>
      <td>what_causes_heartburn_rusha_modi</td>
      <td>11.5M</td>
      <td>5.65G</td>
      <td>854K</td>
      <td>285K</td>
      <td>20181101</td>
      <td>4 min 54 s</td>
      <td>328618</td>
    </tr>
    <tr>
      <th>517</th>
      <td>are_all_of_your_memories_real_daniel_l_schacter</td>
      <td>18.5M</td>
      <td>5.67G</td>
      <td>569K</td>
      <td>284K</td>
      <td>20200908</td>
      <td>5 min 17 s</td>
      <td>488441</td>
    </tr>
    <tr>
      <th>518</th>
      <td>what_is_a_butt_tuba_and_why_is_it_in_medieval_...</td>
      <td>6.83M</td>
      <td>5.67G</td>
      <td>853K</td>
      <td>284K</td>
      <td>20190416</td>
      <td>4 min 40 s</td>
      <td>204038</td>
    </tr>
    <tr>
      <th>519</th>
      <td>the_deadly_irony_of_gunpowder_eric_rosado</td>
      <td>8.75M</td>
      <td>5.68G</td>
      <td>2.22M</td>
      <td>284K</td>
      <td>20131104</td>
      <td>3 min 24 s</td>
      <td>358482</td>
    </tr>
    <tr>
      <th>520</th>
      <td>can_you_solve_the_dark_matter_fuel_riddle_dan_...</td>
      <td>7.74M</td>
      <td>5.69G</td>
      <td>850K</td>
      <td>283K</td>
      <td>20190716</td>
      <td>4 min 24 s</td>
      <td>245125</td>
    </tr>
    <tr>
      <th>521</th>
      <td>how_one_piece_of_legislation_divided_a_nation_...</td>
      <td>13.8M</td>
      <td>5.70G</td>
      <td>2.20M</td>
      <td>282K</td>
      <td>20140211</td>
      <td>6 min 2 s</td>
      <td>320340</td>
    </tr>
    <tr>
      <th>522</th>
      <td>how_far_is_a_second</td>
      <td>2.58M</td>
      <td>5.70G</td>
      <td>2.75M</td>
      <td>281K</td>
      <td>20120407</td>
      <td>1 min 29 s</td>
      <td>242908</td>
    </tr>
    <tr>
      <th>523</th>
      <td>what_is_the_coldest_thing_in_the_world_lina_ma...</td>
      <td>5.77M</td>
      <td>5.71G</td>
      <td>1.10M</td>
      <td>281K</td>
      <td>20180710</td>
      <td>4 min 25 s</td>
      <td>181878</td>
    </tr>
    <tr>
      <th>524</th>
      <td>how_do_glasses_help_us_see_andrew_bastawrous_a...</td>
      <td>11.8M</td>
      <td>5.72G</td>
      <td>1.65M</td>
      <td>281K</td>
      <td>20160405</td>
      <td>4 min 23 s</td>
      <td>376959</td>
    </tr>
    <tr>
      <th>525</th>
      <td>history_through_the_eyes_of_the_potato_leo_bea...</td>
      <td>7.60M</td>
      <td>5.73G</td>
      <td>1.64M</td>
      <td>281K</td>
      <td>20151214</td>
      <td>3 min 46 s</td>
      <td>281361</td>
    </tr>
    <tr>
      <th>526</th>
      <td>why_can_t_we_see_evidence_of_alien_life</td>
      <td>15.4M</td>
      <td>5.74G</td>
      <td>2.74M</td>
      <td>280K</td>
      <td>20120311</td>
      <td>6 min 3 s</td>
      <td>354180</td>
    </tr>
    <tr>
      <th>527</th>
      <td>how_do_vaccines_work_kelwalin_dhanasarnsombut</td>
      <td>6.41M</td>
      <td>5.75G</td>
      <td>1.92M</td>
      <td>280K</td>
      <td>20150112</td>
      <td>4 min 35 s</td>
      <td>195446</td>
    </tr>
    <tr>
      <th>528</th>
      <td>when_will_the_next_ice_age_happen_lorraine_lis...</td>
      <td>8.03M</td>
      <td>5.76G</td>
      <td>1.09M</td>
      <td>280K</td>
      <td>20180510</td>
      <td>5 min 6 s</td>
      <td>219726</td>
    </tr>
    <tr>
      <th>529</th>
      <td>do_larger_animals_take_longer_to_pee_david_l_hu</td>
      <td>14.2M</td>
      <td>5.77G</td>
      <td>279K</td>
      <td>279K</td>
      <td>20201105</td>
      <td>4 min 46 s</td>
      <td>415304</td>
    </tr>
    <tr>
      <th>530</th>
      <td>how_simple_ideas_lead_to_scientific_discoveries</td>
      <td>14.9M</td>
      <td>5.79G</td>
      <td>2.72M</td>
      <td>278K</td>
      <td>20120313</td>
      <td>7 min 31 s</td>
      <td>275800</td>
    </tr>
    <tr>
      <th>531</th>
      <td>how_mendel_s_pea_plants_helped_us_understand_g...</td>
      <td>5.11M</td>
      <td>5.79G</td>
      <td>2.44M</td>
      <td>277K</td>
      <td>20130312</td>
      <td>3 min 6 s</td>
      <td>230041</td>
    </tr>
    <tr>
      <th>532</th>
      <td>how_do_you_know_you_exist_james_zucker</td>
      <td>6.00M</td>
      <td>5.80G</td>
      <td>2.16M</td>
      <td>277K</td>
      <td>20140814</td>
      <td>3 min 2 s</td>
      <td>276422</td>
    </tr>
    <tr>
      <th>533</th>
      <td>the_most_colorful_gemstones_on_earth_jeff_deko...</td>
      <td>30.6M</td>
      <td>5.83G</td>
      <td>276K</td>
      <td>276K</td>
      <td>20201203</td>
      <td>5 min 55 s</td>
      <td>722427</td>
    </tr>
    <tr>
      <th>534</th>
      <td>why_do_honeybees_love_hexagons_zack_patterson_...</td>
      <td>8.57M</td>
      <td>5.84G</td>
      <td>2.15M</td>
      <td>275K</td>
      <td>20140610</td>
      <td>3 min 58 s</td>
      <td>302106</td>
    </tr>
    <tr>
      <th>535</th>
      <td>how_to_make_your_writing_funnier_cheri_steinke...</td>
      <td>8.83M</td>
      <td>5.84G</td>
      <td>1.60M</td>
      <td>273K</td>
      <td>20160209</td>
      <td>5 min 6 s</td>
      <td>241892</td>
    </tr>
    <tr>
      <th>536</th>
      <td>why_do_people_fear_the_wrong_things_gerd_giger...</td>
      <td>8.68M</td>
      <td>5.85G</td>
      <td>546K</td>
      <td>273K</td>
      <td>20200225</td>
      <td>4 min 40 s</td>
      <td>259361</td>
    </tr>
    <tr>
      <th>537</th>
      <td>how_big_is_the_ocean_scott_gass</td>
      <td>7.83M</td>
      <td>5.86G</td>
      <td>2.40M</td>
      <td>273K</td>
      <td>20130624</td>
      <td>5 min 25 s</td>
      <td>202002</td>
    </tr>
    <tr>
      <th>538</th>
      <td>the_origin_of_countless_conspiracy_theories_pa...</td>
      <td>10.7M</td>
      <td>5.87G</td>
      <td>1.60M</td>
      <td>273K</td>
      <td>20160519</td>
      <td>4 min 35 s</td>
      <td>324702</td>
    </tr>
    <tr>
      <th>539</th>
      <td>making_a_ted_ed_lesson_bringing_a_pop_up_book_...</td>
      <td>15.1M</td>
      <td>5.89G</td>
      <td>2.12M</td>
      <td>272K</td>
      <td>20140910</td>
      <td>6 min 12 s</td>
      <td>340772</td>
    </tr>
    <tr>
      <th>540</th>
      <td>why_do_we_feel_nostalgia_clay_routledge</td>
      <td>7.37M</td>
      <td>5.89G</td>
      <td>1.32M</td>
      <td>271K</td>
      <td>20161121</td>
      <td>4 min 8 s</td>
      <td>248505</td>
    </tr>
    <tr>
      <th>541</th>
      <td>the_myth_of_jason_medea_and_the_golden_fleece_...</td>
      <td>21.0M</td>
      <td>5.91G</td>
      <td>542K</td>
      <td>271K</td>
      <td>20200721</td>
      <td>4 min 46 s</td>
      <td>616026</td>
    </tr>
    <tr>
      <th>542</th>
      <td>why_should_you_read_charles_dickens_iseult_gil...</td>
      <td>16.6M</td>
      <td>5.93G</td>
      <td>1.06M</td>
      <td>270K</td>
      <td>20171221</td>
      <td>5 min 16 s</td>
      <td>439827</td>
    </tr>
    <tr>
      <th>543</th>
      <td>the_rise_and_fall_of_the_celtic_warriors_phili...</td>
      <td>16.6M</td>
      <td>5.95G</td>
      <td>540K</td>
      <td>270K</td>
      <td>20200720</td>
      <td>5 min 11 s</td>
      <td>447525</td>
    </tr>
    <tr>
      <th>544</th>
      <td>history_vs_andrew_jackson_james_fester</td>
      <td>7.65M</td>
      <td>5.95G</td>
      <td>2.11M</td>
      <td>270K</td>
      <td>20140121</td>
      <td>4 min 53 s</td>
      <td>218796</td>
    </tr>
    <tr>
      <th>545</th>
      <td>why_do_people_get_so_anxious_about_math_orly_r...</td>
      <td>6.01M</td>
      <td>5.96G</td>
      <td>1.32M</td>
      <td>270K</td>
      <td>20170327</td>
      <td>4 min 36 s</td>
      <td>182653</td>
    </tr>
    <tr>
      <th>546</th>
      <td>could_the_earth_be_swallowed_by_a_black_hole_f...</td>
      <td>16.1M</td>
      <td>5.97G</td>
      <td>804K</td>
      <td>268K</td>
      <td>20180920</td>
      <td>5 min 10 s</td>
      <td>433990</td>
    </tr>
    <tr>
      <th>547</th>
      <td>the_history_of_tattoos_addison_anderson</td>
      <td>10.3M</td>
      <td>5.98G</td>
      <td>1.83M</td>
      <td>268K</td>
      <td>20140918</td>
      <td>5 min 16 s</td>
      <td>272587</td>
    </tr>
    <tr>
      <th>548</th>
      <td>dark_matter_the_matter_we_can_t_see_james_gillies</td>
      <td>22.0M</td>
      <td>6.01G</td>
      <td>2.34M</td>
      <td>267K</td>
      <td>20130503</td>
      <td>5 min 34 s</td>
      <td>550882</td>
    </tr>
    <tr>
      <th>549</th>
      <td>the_accident_that_changed_the_world_allison_ra...</td>
      <td>7.87M</td>
      <td>6.01G</td>
      <td>533K</td>
      <td>266K</td>
      <td>20200210</td>
      <td>4 min 50 s</td>
      <td>227421</td>
    </tr>
    <tr>
      <th>550</th>
      <td>how_bones_make_blood_melody_smith</td>
      <td>7.43M</td>
      <td>6.02G</td>
      <td>532K</td>
      <td>266K</td>
      <td>20200127</td>
      <td>4 min 42 s</td>
      <td>220663</td>
    </tr>
    <tr>
      <th>551</th>
      <td>the_silk_road_connecting_the_ancient_world_thr...</td>
      <td>9.08M</td>
      <td>6.03G</td>
      <td>2.06M</td>
      <td>264K</td>
      <td>20140603</td>
      <td>5 min 19 s</td>
      <td>238531</td>
    </tr>
    <tr>
      <th>552</th>
      <td>what_is_consciousness_michael_s_a_graziano</td>
      <td>7.85M</td>
      <td>6.04G</td>
      <td>792K</td>
      <td>264K</td>
      <td>20190211</td>
      <td>5 min 12 s</td>
      <td>211104</td>
    </tr>
    <tr>
      <th>553</th>
      <td>how_much_of_human_history_is_on_the_bottom_of_...</td>
      <td>9.33M</td>
      <td>6.05G</td>
      <td>1.29M</td>
      <td>264K</td>
      <td>20161020</td>
      <td>4 min 45 s</td>
      <td>274169</td>
    </tr>
    <tr>
      <th>554</th>
      <td>how_does_your_brain_respond_to_pain_karen_d_davis</td>
      <td>9.89M</td>
      <td>6.06G</td>
      <td>2.06M</td>
      <td>264K</td>
      <td>20140602</td>
      <td>4 min 57 s</td>
      <td>278563</td>
    </tr>
    <tr>
      <th>555</th>
      <td>a_different_way_to_visualize_rhythm_john_varney</td>
      <td>9.61M</td>
      <td>6.07G</td>
      <td>1.80M</td>
      <td>264K</td>
      <td>20141020</td>
      <td>5 min 22 s</td>
      <td>250046</td>
    </tr>
    <tr>
      <th>556</th>
      <td>does_grammar_matter_andreea_s_calude</td>
      <td>7.88M</td>
      <td>6.07G</td>
      <td>1.54M</td>
      <td>262K</td>
      <td>20160412</td>
      <td>4 min 38 s</td>
      <td>237470</td>
    </tr>
    <tr>
      <th>557</th>
      <td>could_we_harness_the_power_of_a_black_hole_fab...</td>
      <td>23.2M</td>
      <td>6.10G</td>
      <td>261K</td>
      <td>261K</td>
      <td>20201019</td>
      <td>5 min 41 s</td>
      <td>570366</td>
    </tr>
    <tr>
      <th>558</th>
      <td>what_can_dna_tests_really_tell_us_about_our_an...</td>
      <td>21.9M</td>
      <td>6.12G</td>
      <td>522K</td>
      <td>261K</td>
      <td>20200609</td>
      <td>6 min 44 s</td>
      <td>453982</td>
    </tr>
    <tr>
      <th>559</th>
      <td>what_happens_when_you_have_a_concussion_cliffo...</td>
      <td>10.3M</td>
      <td>6.13G</td>
      <td>1.27M</td>
      <td>261K</td>
      <td>20170727</td>
      <td>6 min 15 s</td>
      <td>231336</td>
    </tr>
    <tr>
      <th>560</th>
      <td>why_is_yawning_contagious_claudia_aguirre</td>
      <td>10.5M</td>
      <td>6.14G</td>
      <td>2.03M</td>
      <td>260K</td>
      <td>20131107</td>
      <td>4 min 28 s</td>
      <td>327368</td>
    </tr>
    <tr>
      <th>561</th>
      <td>from_pacifist_to_spy_wwiis_surprising_secret_a...</td>
      <td>9.21M</td>
      <td>6.15G</td>
      <td>779K</td>
      <td>260K</td>
      <td>20190806</td>
      <td>4 min 30 s</td>
      <td>285915</td>
    </tr>
    <tr>
      <th>562</th>
      <td>a_day_in_the_life_of_a_peruvian_shaman_gabriel...</td>
      <td>7.63M</td>
      <td>6.15G</td>
      <td>517K</td>
      <td>259K</td>
      <td>20200604</td>
      <td>4 min 39 s</td>
      <td>228764</td>
    </tr>
    <tr>
      <th>563</th>
      <td>what_do_all_languages_have_in_common_cameron_m...</td>
      <td>14.9M</td>
      <td>6.17G</td>
      <td>517K</td>
      <td>259K</td>
      <td>20200629</td>
      <td>5 min 18 s</td>
      <td>393303</td>
    </tr>
    <tr>
      <th>564</th>
      <td>volcanic_eruption_explained_steven_anderson</td>
      <td>21.7M</td>
      <td>6.19G</td>
      <td>517K</td>
      <td>258K</td>
      <td>20200713</td>
      <td>5 min 33 s</td>
      <td>545566</td>
    </tr>
    <tr>
      <th>565</th>
      <td>what_happens_when_your_dna_is_damaged_monica_m...</td>
      <td>7.65M</td>
      <td>6.20G</td>
      <td>1.51M</td>
      <td>258K</td>
      <td>20150921</td>
      <td>4 min 58 s</td>
      <td>215204</td>
    </tr>
    <tr>
      <th>566</th>
      <td>how_do_dogs_see_with_their_noses_alexandra_hor...</td>
      <td>10.1M</td>
      <td>6.21G</td>
      <td>1.76M</td>
      <td>258K</td>
      <td>20150202</td>
      <td>4 min 27 s</td>
      <td>316657</td>
    </tr>
    <tr>
      <th>567</th>
      <td>what_are_the_universal_human_rights_benedetta_...</td>
      <td>12.0M</td>
      <td>6.22G</td>
      <td>1.51M</td>
      <td>258K</td>
      <td>20151015</td>
      <td>4 min 46 s</td>
      <td>350559</td>
    </tr>
    <tr>
      <th>568</th>
      <td>michio_kaku_what_is_deja_vu_big_think</td>
      <td>6.56M</td>
      <td>6.23G</td>
      <td>2.51M</td>
      <td>257K</td>
      <td>20111115</td>
      <td>3 min 0 s</td>
      <td>305396</td>
    </tr>
    <tr>
      <th>569</th>
      <td>three_anti_social_skills_to_improve_your_writi...</td>
      <td>6.89M</td>
      <td>6.23G</td>
      <td>2.26M</td>
      <td>257K</td>
      <td>20121120</td>
      <td>3 min 44 s</td>
      <td>257357</td>
    </tr>
    <tr>
      <th>570</th>
      <td>a_day_in_the_life_of_an_ancient_greek_architec...</td>
      <td>20.3M</td>
      <td>6.25G</td>
      <td>256K</td>
      <td>256K</td>
      <td>20200915</td>
      <td>5 min 33 s</td>
      <td>511554</td>
    </tr>
    <tr>
      <th>571</th>
      <td>what_is_metallic_glass_ashwini_bharathula</td>
      <td>6.04M</td>
      <td>6.26G</td>
      <td>1.49M</td>
      <td>255K</td>
      <td>20160317</td>
      <td>4 min 33 s</td>
      <td>185320</td>
    </tr>
    <tr>
      <th>572</th>
      <td>the_last_living_members_of_an_extinct_species_...</td>
      <td>16.3M</td>
      <td>6.27G</td>
      <td>509K</td>
      <td>255K</td>
      <td>20200813</td>
      <td>5 min 31 s</td>
      <td>412351</td>
    </tr>
    <tr>
      <th>573</th>
      <td>is_radiation_dangerous_matt_anticole</td>
      <td>9.42M</td>
      <td>6.28G</td>
      <td>1.48M</td>
      <td>252K</td>
      <td>20160314</td>
      <td>5 min 20 s</td>
      <td>246234</td>
    </tr>
    <tr>
      <th>574</th>
      <td>should_you_trust_your_first_impression_peter_m...</td>
      <td>9.92M</td>
      <td>6.29G</td>
      <td>2.21M</td>
      <td>252K</td>
      <td>20130815</td>
      <td>4 min 38 s</td>
      <td>299193</td>
    </tr>
    <tr>
      <th>575</th>
      <td>what_does_the_liver_do_emma_bryce</td>
      <td>5.81M</td>
      <td>6.30G</td>
      <td>1.72M</td>
      <td>252K</td>
      <td>20141125</td>
      <td>3 min 24 s</td>
      <td>238546</td>
    </tr>
    <tr>
      <th>576</th>
      <td>how_did_polynesian_wayfinders_navigate_the_pac...</td>
      <td>18.1M</td>
      <td>6.32G</td>
      <td>0.98M</td>
      <td>251K</td>
      <td>20171017</td>
      <td>5 min 31 s</td>
      <td>458990</td>
    </tr>
    <tr>
      <th>577</th>
      <td>music_and_math_the_genius_of_beethoven_natalya...</td>
      <td>10.2M</td>
      <td>6.33G</td>
      <td>1.96M</td>
      <td>251K</td>
      <td>20140909</td>
      <td>4 min 19 s</td>
      <td>329805</td>
    </tr>
    <tr>
      <th>578</th>
      <td>the_breathtaking_courage_of_harriet_tubman_jan...</td>
      <td>8.17M</td>
      <td>6.33G</td>
      <td>0.98M</td>
      <td>251K</td>
      <td>20180724</td>
      <td>4 min 48 s</td>
      <td>237647</td>
    </tr>
    <tr>
      <th>579</th>
      <td>one_of_the_most_epic_engineering_feats_in_hist...</td>
      <td>17.9M</td>
      <td>6.35G</td>
      <td>501K</td>
      <td>251K</td>
      <td>20200211</td>
      <td>5 min 15 s</td>
      <td>476010</td>
    </tr>
    <tr>
      <th>580</th>
      <td>why_are_sharks_so_awesome_tierney_thys</td>
      <td>12.3M</td>
      <td>6.36G</td>
      <td>1.22M</td>
      <td>250K</td>
      <td>20161107</td>
      <td>4 min 35 s</td>
      <td>373598</td>
    </tr>
    <tr>
      <th>581</th>
      <td>what_s_so_special_about_viking_ships_jan_bill</td>
      <td>13.0M</td>
      <td>6.38G</td>
      <td>499K</td>
      <td>250K</td>
      <td>20200121</td>
      <td>4 min 57 s</td>
      <td>366011</td>
    </tr>
    <tr>
      <th>582</th>
      <td>the_myth_of_ireland_s_two_greatest_warriors_is...</td>
      <td>18.0M</td>
      <td>6.39G</td>
      <td>496K</td>
      <td>248K</td>
      <td>20200806</td>
      <td>4 min 47 s</td>
      <td>524914</td>
    </tr>
    <tr>
      <th>583</th>
      <td>the_science_of_static_electricity_anuradha_bha...</td>
      <td>6.29M</td>
      <td>6.40G</td>
      <td>1.69M</td>
      <td>247K</td>
      <td>20150409</td>
      <td>3 min 38 s</td>
      <td>241309</td>
    </tr>
    <tr>
      <th>584</th>
      <td>how_is_power_divided_in_the_united_states_gove...</td>
      <td>5.20M</td>
      <td>6.41G</td>
      <td>2.17M</td>
      <td>247K</td>
      <td>20130412</td>
      <td>3 min 49 s</td>
      <td>190146</td>
    </tr>
    <tr>
      <th>585</th>
      <td>how_the_world_s_first_metro_system_was_built_c...</td>
      <td>8.97M</td>
      <td>6.41G</td>
      <td>987K</td>
      <td>247K</td>
      <td>20180419</td>
      <td>4 min 57 s</td>
      <td>253170</td>
    </tr>
    <tr>
      <th>586</th>
      <td>why_should_you_read_kafka_on_the_shore_iseult_...</td>
      <td>14.2M</td>
      <td>6.43G</td>
      <td>740K</td>
      <td>247K</td>
      <td>20190820</td>
      <td>4 min 40 s</td>
      <td>425851</td>
    </tr>
    <tr>
      <th>587</th>
      <td>how_batteries_work_adam_jacobson</td>
      <td>6.38M</td>
      <td>6.43G</td>
      <td>1.68M</td>
      <td>245K</td>
      <td>20150521</td>
      <td>4 min 19 s</td>
      <td>206272</td>
    </tr>
    <tr>
      <th>588</th>
      <td>myths_and_misconceptions_about_evolution_alex_...</td>
      <td>7.18M</td>
      <td>6.44G</td>
      <td>2.15M</td>
      <td>245K</td>
      <td>20130708</td>
      <td>4 min 22 s</td>
      <td>229741</td>
    </tr>
    <tr>
      <th>589</th>
      <td>newtons_three_body_problem_explained_fabio_pac...</td>
      <td>17.6M</td>
      <td>6.46G</td>
      <td>487K</td>
      <td>244K</td>
      <td>20200803</td>
      <td>5 min 30 s</td>
      <td>446756</td>
    </tr>
    <tr>
      <th>590</th>
      <td>how_do_lungs_work_emma_bryce</td>
      <td>5.98M</td>
      <td>6.46G</td>
      <td>1.66M</td>
      <td>243K</td>
      <td>20141124</td>
      <td>3 min 21 s</td>
      <td>248975</td>
    </tr>
    <tr>
      <th>591</th>
      <td>can_we_eat_to_starve_cancer_william_li</td>
      <td>35.4M</td>
      <td>6.50G</td>
      <td>1.90M</td>
      <td>243K</td>
      <td>20140408</td>
      <td>20 min 1 s</td>
      <td>247191</td>
    </tr>
    <tr>
      <th>592</th>
      <td>how_can_we_solve_the_antibiotic_resistance_cri...</td>
      <td>11.9M</td>
      <td>6.51G</td>
      <td>485K</td>
      <td>242K</td>
      <td>20200316</td>
      <td>6 min 22 s</td>
      <td>262120</td>
    </tr>
    <tr>
      <th>593</th>
      <td>the_race_to_decode_a_mysterious_language_susan...</td>
      <td>15.6M</td>
      <td>6.53G</td>
      <td>484K</td>
      <td>242K</td>
      <td>20200714</td>
      <td>4 min 44 s</td>
      <td>459549</td>
    </tr>
    <tr>
      <th>594</th>
      <td>the_psychology_behind_irrational_decisions_sar...</td>
      <td>6.80M</td>
      <td>6.53G</td>
      <td>1.42M</td>
      <td>242K</td>
      <td>20160512</td>
      <td>4 min 38 s</td>
      <td>204781</td>
    </tr>
    <tr>
      <th>595</th>
      <td>the_complicated_history_of_surfing_scott_laderman</td>
      <td>14.1M</td>
      <td>6.55G</td>
      <td>966K</td>
      <td>242K</td>
      <td>20171116</td>
      <td>5 min 39 s</td>
      <td>347513</td>
    </tr>
    <tr>
      <th>596</th>
      <td>whats_the_smallest_thing_in_the_universe_jonat...</td>
      <td>10.2M</td>
      <td>6.56G</td>
      <td>721K</td>
      <td>240K</td>
      <td>20181115</td>
      <td>5 min 20 s</td>
      <td>266131</td>
    </tr>
    <tr>
      <th>597</th>
      <td>why_should_you_read_sylvia_plath_iseult_gillespie</td>
      <td>10.9M</td>
      <td>6.57G</td>
      <td>720K</td>
      <td>240K</td>
      <td>20190307</td>
      <td>4 min 45 s</td>
      <td>319231</td>
    </tr>
    <tr>
      <th>598</th>
      <td>what_we_know_and_don_t_know_about_ebola_alex_g...</td>
      <td>8.20M</td>
      <td>6.57G</td>
      <td>1.64M</td>
      <td>239K</td>
      <td>20141204</td>
      <td>4 min 0 s</td>
      <td>286350</td>
    </tr>
    <tr>
      <th>599</th>
      <td>what_is_fat_george_zaidan</td>
      <td>7.34M</td>
      <td>6.58G</td>
      <td>2.09M</td>
      <td>237K</td>
      <td>20130522</td>
      <td>4 min 21 s</td>
      <td>235320</td>
    </tr>
    <tr>
      <th>600</th>
      <td>the_akune_brothers_siblings_on_opposite_sides_...</td>
      <td>12.8M</td>
      <td>6.59G</td>
      <td>1.62M</td>
      <td>237K</td>
      <td>20150721</td>
      <td>4 min 53 s</td>
      <td>364769</td>
    </tr>
    <tr>
      <th>601</th>
      <td>is_math_discovered_or_invented_jeff_dekofsky</td>
      <td>14.1M</td>
      <td>6.61G</td>
      <td>1.61M</td>
      <td>235K</td>
      <td>20141027</td>
      <td>5 min 10 s</td>
      <td>380034</td>
    </tr>
    <tr>
      <th>602</th>
      <td>ugly_history_the_1937_haitian_massacre_edward_...</td>
      <td>17.8M</td>
      <td>6.63G</td>
      <td>939K</td>
      <td>235K</td>
      <td>20180125</td>
      <td>5 min 39 s</td>
      <td>440233</td>
    </tr>
    <tr>
      <th>603</th>
      <td>can_you_solve_the_mondrian_squares_riddle_gord...</td>
      <td>5.64M</td>
      <td>6.63G</td>
      <td>938K</td>
      <td>235K</td>
      <td>20180628</td>
      <td>4 min 45 s</td>
      <td>165899</td>
    </tr>
    <tr>
      <th>604</th>
      <td>the_resistance_think_like_a_coder_ep_2</td>
      <td>11.9M</td>
      <td>6.64G</td>
      <td>468K</td>
      <td>234K</td>
      <td>20191014</td>
      <td>6 min 9 s</td>
      <td>268835</td>
    </tr>
    <tr>
      <th>605</th>
      <td>who_owns_the_wilderness_elyse_cox</td>
      <td>20.1M</td>
      <td>6.66G</td>
      <td>234K</td>
      <td>234K</td>
      <td>20201006</td>
      <td>5 min 12 s</td>
      <td>539412</td>
    </tr>
    <tr>
      <th>606</th>
      <td>the_spear_wielding_stork_who_revolutionized_sc...</td>
      <td>20.7M</td>
      <td>6.68G</td>
      <td>232K</td>
      <td>232K</td>
      <td>20201217</td>
      <td>5 min 41 s</td>
      <td>508965</td>
    </tr>
    <tr>
      <th>607</th>
      <td>population_pyramids_powerful_predictors_of_the...</td>
      <td>10.9M</td>
      <td>6.69G</td>
      <td>1.81M</td>
      <td>232K</td>
      <td>20140505</td>
      <td>5 min 1 s</td>
      <td>304509</td>
    </tr>
    <tr>
      <th>608</th>
      <td>do_animals_have_language_michele_bishop</td>
      <td>7.90M</td>
      <td>6.70G</td>
      <td>1.58M</td>
      <td>232K</td>
      <td>20150910</td>
      <td>4 min 54 s</td>
      <td>225065</td>
    </tr>
    <tr>
      <th>609</th>
      <td>group_theory_101_how_to_play_a_rubiks_cube_lik...</td>
      <td>7.58M</td>
      <td>6.71G</td>
      <td>1.36M</td>
      <td>232K</td>
      <td>20151102</td>
      <td>4 min 36 s</td>
      <td>230116</td>
    </tr>
    <tr>
      <th>610</th>
      <td>why_should_you_read_hamlet_iseult_gillespie</td>
      <td>10.8M</td>
      <td>6.72G</td>
      <td>695K</td>
      <td>232K</td>
      <td>20190625</td>
      <td>5 min 8 s</td>
      <td>292202</td>
    </tr>
    <tr>
      <th>611</th>
      <td>the_psychology_of_post_traumatic_stress_disord...</td>
      <td>22.0M</td>
      <td>6.74G</td>
      <td>926K</td>
      <td>231K</td>
      <td>20180625</td>
      <td>5 min 12 s</td>
      <td>590275</td>
    </tr>
    <tr>
      <th>612</th>
      <td>a_brief_history_of_plastic</td>
      <td>17.1M</td>
      <td>6.76G</td>
      <td>462K</td>
      <td>231K</td>
      <td>20200910</td>
      <td>5 min 40 s</td>
      <td>420857</td>
    </tr>
    <tr>
      <th>613</th>
      <td>is_there_a_disease_that_makes_us_love_cats_jaa...</td>
      <td>9.03M</td>
      <td>6.77G</td>
      <td>1.35M</td>
      <td>231K</td>
      <td>20160623</td>
      <td>5 min 5 s</td>
      <td>247834</td>
    </tr>
    <tr>
      <th>614</th>
      <td>why_do_our_bodies_age_monica_menesini</td>
      <td>8.17M</td>
      <td>6.77G</td>
      <td>1.35M</td>
      <td>231K</td>
      <td>20160609</td>
      <td>5 min 9 s</td>
      <td>221412</td>
    </tr>
    <tr>
      <th>615</th>
      <td>how_do_blood_transfusions_work_bill_schutt</td>
      <td>14.4M</td>
      <td>6.79G</td>
      <td>461K</td>
      <td>231K</td>
      <td>20200218</td>
      <td>4 min 51 s</td>
      <td>414188</td>
    </tr>
    <tr>
      <th>616</th>
      <td>how_in_vitro_fertilization_ivf_works_nassim_as...</td>
      <td>14.5M</td>
      <td>6.80G</td>
      <td>1.57M</td>
      <td>230K</td>
      <td>20150507</td>
      <td>6 min 42 s</td>
      <td>302138</td>
    </tr>
    <tr>
      <th>617</th>
      <td>why_should_you_read_the_god_of_small_things_by...</td>
      <td>11.6M</td>
      <td>6.81G</td>
      <td>460K</td>
      <td>230K</td>
      <td>20190924</td>
      <td>4 min 31 s</td>
      <td>357337</td>
    </tr>
    <tr>
      <th>618</th>
      <td>making_sense_of_irrational_numbers_ganesh_pai</td>
      <td>5.69M</td>
      <td>6.82G</td>
      <td>1.35M</td>
      <td>230K</td>
      <td>20160523</td>
      <td>4 min 40 s</td>
      <td>170177</td>
    </tr>
    <tr>
      <th>619</th>
      <td>the_secrets_of_mozarts_magic_flute_joshua_borths</td>
      <td>7.25M</td>
      <td>6.83G</td>
      <td>1.12M</td>
      <td>230K</td>
      <td>20161122</td>
      <td>5 min 47 s</td>
      <td>174846</td>
    </tr>
    <tr>
      <th>620</th>
      <td>the_science_of_skin_emma_bryce</td>
      <td>7.01M</td>
      <td>6.83G</td>
      <td>913K</td>
      <td>228K</td>
      <td>20180312</td>
      <td>5 min 10 s</td>
      <td>189365</td>
    </tr>
    <tr>
      <th>621</th>
      <td>comma_story_terisa_folaron</td>
      <td>7.47M</td>
      <td>6.84G</td>
      <td>2.00M</td>
      <td>228K</td>
      <td>20130709</td>
      <td>4 min 59 s</td>
      <td>209450</td>
    </tr>
    <tr>
      <th>622</th>
      <td>could_we_actually_live_on_mars_mari_foroutan</td>
      <td>8.45M</td>
      <td>6.85G</td>
      <td>1.56M</td>
      <td>228K</td>
      <td>20150824</td>
      <td>4 min 29 s</td>
      <td>262787</td>
    </tr>
    <tr>
      <th>623</th>
      <td>everything_you_need_to_know_to_read_homer_s_od...</td>
      <td>10.2M</td>
      <td>6.86G</td>
      <td>1.11M</td>
      <td>228K</td>
      <td>20170130</td>
      <td>4 min 56 s</td>
      <td>288913</td>
    </tr>
    <tr>
      <th>624</th>
      <td>how_do_your_hormones_work_emma_bryce</td>
      <td>9.95M</td>
      <td>6.87G</td>
      <td>910K</td>
      <td>227K</td>
      <td>20180621</td>
      <td>5 min 3 s</td>
      <td>274881</td>
    </tr>
    <tr>
      <th>625</th>
      <td>how_do_executive_orders_work_christina_greer</td>
      <td>8.88M</td>
      <td>6.88G</td>
      <td>908K</td>
      <td>227K</td>
      <td>20170918</td>
      <td>4 min 46 s</td>
      <td>259628</td>
    </tr>
    <tr>
      <th>626</th>
      <td>the_difference_between_classical_and_operant_c...</td>
      <td>6.51M</td>
      <td>6.88G</td>
      <td>2.00M</td>
      <td>227K</td>
      <td>20130307</td>
      <td>4 min 12 s</td>
      <td>216233</td>
    </tr>
    <tr>
      <th>627</th>
      <td>what_is_dust_made_of_michael_marder</td>
      <td>10.1M</td>
      <td>6.89G</td>
      <td>908K</td>
      <td>227K</td>
      <td>20180524</td>
      <td>4 min 33 s</td>
      <td>310860</td>
    </tr>
    <tr>
      <th>628</th>
      <td>the_truth_about_bats_amy_wray</td>
      <td>15.6M</td>
      <td>6.91G</td>
      <td>1.55M</td>
      <td>226K</td>
      <td>20141216</td>
      <td>5 min 47 s</td>
      <td>377023</td>
    </tr>
    <tr>
      <th>629</th>
      <td>earworms_those_songs_that_get_stuck_in_your_he...</td>
      <td>8.60M</td>
      <td>6.92G</td>
      <td>1.54M</td>
      <td>225K</td>
      <td>20150326</td>
      <td>4 min 45 s</td>
      <td>252971</td>
    </tr>
    <tr>
      <th>630</th>
      <td>think_like_a_coder_teaser_trailer</td>
      <td>2.39M</td>
      <td>6.92G</td>
      <td>448K</td>
      <td>224K</td>
      <td>20190921</td>
      <td>56 s 63 ms</td>
      <td>357781</td>
    </tr>
    <tr>
      <th>631</th>
      <td>how_does_hibernation_work_sheena_lee_faherty</td>
      <td>9.83M</td>
      <td>6.93G</td>
      <td>889K</td>
      <td>222K</td>
      <td>20180503</td>
      <td>4 min 48 s</td>
      <td>285565</td>
    </tr>
    <tr>
      <th>632</th>
      <td>ted_ed_is_on_patreon_we_need_your_help_to_revo...</td>
      <td>5.87M</td>
      <td>6.93G</td>
      <td>1.08M</td>
      <td>222K</td>
      <td>20170815</td>
      <td>1 min 51 s</td>
      <td>443496</td>
    </tr>
    <tr>
      <th>633</th>
      <td>the_colossal_consequences_of_supervolcanoes_al...</td>
      <td>12.1M</td>
      <td>6.95G</td>
      <td>1.73M</td>
      <td>222K</td>
      <td>20140609</td>
      <td>4 min 50 s</td>
      <td>348279</td>
    </tr>
    <tr>
      <th>634</th>
      <td>getting_started_as_a_dj_mixing_mashups_and_dig...</td>
      <td>32.6M</td>
      <td>6.98G</td>
      <td>1.73M</td>
      <td>221K</td>
      <td>20140303</td>
      <td>10 min 36 s</td>
      <td>430313</td>
    </tr>
    <tr>
      <th>635</th>
      <td>if_superpowers_were_real_super_strength_joy_lin</td>
      <td>12.9M</td>
      <td>6.99G</td>
      <td>1.94M</td>
      <td>221K</td>
      <td>20130628</td>
      <td>4 min 4 s</td>
      <td>440326</td>
    </tr>
    <tr>
      <th>636</th>
      <td>inside_your_computer_bettina_bair</td>
      <td>6.95M</td>
      <td>7.00G</td>
      <td>1.94M</td>
      <td>221K</td>
      <td>20130701</td>
      <td>4 min 11 s</td>
      <td>231519</td>
    </tr>
    <tr>
      <th>637</th>
      <td>why_do_we_sweat_john_murnan</td>
      <td>10.3M</td>
      <td>7.01G</td>
      <td>880K</td>
      <td>220K</td>
      <td>20180515</td>
      <td>4 min 47 s</td>
      <td>299775</td>
    </tr>
    <tr>
      <th>638</th>
      <td>how_does_cancer_spread_through_the_body_ivan_s...</td>
      <td>9.36M</td>
      <td>7.02G</td>
      <td>1.49M</td>
      <td>219K</td>
      <td>20141120</td>
      <td>4 min 43 s</td>
      <td>277570</td>
    </tr>
    <tr>
      <th>639</th>
      <td>a_quantum_thought_experiment_matteo_fadel</td>
      <td>20.4M</td>
      <td>7.04G</td>
      <td>218K</td>
      <td>218K</td>
      <td>20201214</td>
      <td>4 min 58 s</td>
      <td>573489</td>
    </tr>
    <tr>
      <th>640</th>
      <td>the_brilliance_of_bioluminescence_leslie_kenna</td>
      <td>6.52M</td>
      <td>7.04G</td>
      <td>1.91M</td>
      <td>218K</td>
      <td>20130515</td>
      <td>4 min 8 s</td>
      <td>220094</td>
    </tr>
    <tr>
      <th>641</th>
      <td>first_person_vs_second_person_vs_third_person_...</td>
      <td>18.3M</td>
      <td>7.06G</td>
      <td>435K</td>
      <td>217K</td>
      <td>20200625</td>
      <td>5 min 19 s</td>
      <td>481980</td>
    </tr>
    <tr>
      <th>642</th>
      <td>could_we_create_dark_matter_rolf_landua</td>
      <td>11.2M</td>
      <td>7.07G</td>
      <td>1.06M</td>
      <td>217K</td>
      <td>20170817</td>
      <td>5 min 48 s</td>
      <td>270590</td>
    </tr>
    <tr>
      <th>643</th>
      <td>an_athlete_uses_physics_to_shatter_world_recor...</td>
      <td>5.59M</td>
      <td>7.08G</td>
      <td>1.69M</td>
      <td>216K</td>
      <td>20140218</td>
      <td>3 min 50 s</td>
      <td>203434</td>
    </tr>
    <tr>
      <th>644</th>
      <td>master_the_art_of_public_speaking_with_ted_mas...</td>
      <td>5.27M</td>
      <td>7.08G</td>
      <td>429K</td>
      <td>214K</td>
      <td>20200104</td>
      <td>1 min 40 s</td>
      <td>441658</td>
    </tr>
    <tr>
      <th>645</th>
      <td>if_superpowers_were_real_flight_joy_lin</td>
      <td>20.6M</td>
      <td>7.10G</td>
      <td>1.87M</td>
      <td>212K</td>
      <td>20130628</td>
      <td>5 min 10 s</td>
      <td>557211</td>
    </tr>
    <tr>
      <th>646</th>
      <td>how_turtle_shells_evolved_twice_judy_cebra_thomas</td>
      <td>9.08M</td>
      <td>7.11G</td>
      <td>636K</td>
      <td>212K</td>
      <td>20190730</td>
      <td>4 min 45 s</td>
      <td>267336</td>
    </tr>
    <tr>
      <th>647</th>
      <td>why_certain_naturally_occurring_wildfires_are_...</td>
      <td>8.56M</td>
      <td>7.12G</td>
      <td>1.24M</td>
      <td>211K</td>
      <td>20160202</td>
      <td>4 min 20 s</td>
      <td>275176</td>
    </tr>
    <tr>
      <th>648</th>
      <td>the_ethical_dilemma_of_self_driving_cars_patri...</td>
      <td>14.7M</td>
      <td>7.13G</td>
      <td>1.24M</td>
      <td>211K</td>
      <td>20151208</td>
      <td>4 min 15 s</td>
      <td>483914</td>
    </tr>
    <tr>
      <th>649</th>
      <td>rhapsody_on_the_proof_of_pi_4</td>
      <td>21.3M</td>
      <td>7.15G</td>
      <td>2.06M</td>
      <td>211K</td>
      <td>20120405</td>
      <td>5 min 54 s</td>
      <td>503864</td>
    </tr>
    <tr>
      <th>650</th>
      <td>what_is_a_vector_david_huynh</td>
      <td>5.96M</td>
      <td>7.16G</td>
      <td>1.03M</td>
      <td>211K</td>
      <td>20160913</td>
      <td>4 min 40 s</td>
      <td>178070</td>
    </tr>
    <tr>
      <th>651</th>
      <td>does_the_wonderful_wizard_of_oz_have_a_hidden_...</td>
      <td>8.28M</td>
      <td>7.17G</td>
      <td>1.03M</td>
      <td>210K</td>
      <td>20170306</td>
      <td>4 min 43 s</td>
      <td>245185</td>
    </tr>
    <tr>
      <th>652</th>
      <td>when_is_water_safe_to_drink_mia_nacamulli</td>
      <td>11.6M</td>
      <td>7.18G</td>
      <td>1.03M</td>
      <td>210K</td>
      <td>20170807</td>
      <td>5 min 23 s</td>
      <td>300099</td>
    </tr>
    <tr>
      <th>653</th>
      <td>the_threat_of_invasive_species_jennifer_klos</td>
      <td>8.62M</td>
      <td>7.19G</td>
      <td>1.23M</td>
      <td>210K</td>
      <td>20160503</td>
      <td>4 min 45 s</td>
      <td>252766</td>
    </tr>
    <tr>
      <th>654</th>
      <td>should_we_get_rid_of_standardized_testing_arlo...</td>
      <td>10.2M</td>
      <td>7.20G</td>
      <td>840K</td>
      <td>210K</td>
      <td>20170919</td>
      <td>5 min 40 s</td>
      <td>251645</td>
    </tr>
    <tr>
      <th>655</th>
      <td>nature_s_smallest_factory_the_calvin_cycle_cat...</td>
      <td>9.70M</td>
      <td>7.21G</td>
      <td>1.64M</td>
      <td>210K</td>
      <td>20140401</td>
      <td>5 min 37 s</td>
      <td>241170</td>
    </tr>
    <tr>
      <th>656</th>
      <td>da_vinci_s_vitruvian_man_of_math_james_earle</td>
      <td>6.30M</td>
      <td>7.21G</td>
      <td>1.84M</td>
      <td>210K</td>
      <td>20130711</td>
      <td>3 min 20 s</td>
      <td>263010</td>
    </tr>
    <tr>
      <th>657</th>
      <td>situational_irony_the_opposite_of_what_you_thi...</td>
      <td>5.88M</td>
      <td>7.22G</td>
      <td>1.84M</td>
      <td>210K</td>
      <td>20121213</td>
      <td>3 min 11 s</td>
      <td>257342</td>
    </tr>
    <tr>
      <th>658</th>
      <td>this_one_weird_trick_will_help_you_spot_clickb...</td>
      <td>8.37M</td>
      <td>7.23G</td>
      <td>626K</td>
      <td>209K</td>
      <td>20190606</td>
      <td>5 min 37 s</td>
      <td>208123</td>
    </tr>
    <tr>
      <th>659</th>
      <td>what_can_schrodinger_s_cat_teach_us_about_quan...</td>
      <td>16.4M</td>
      <td>7.24G</td>
      <td>1.63M</td>
      <td>208K</td>
      <td>20140821</td>
      <td>5 min 23 s</td>
      <td>425805</td>
    </tr>
    <tr>
      <th>660</th>
      <td>the_fish_that_walk_on_land_noah_r_bressman</td>
      <td>17.7M</td>
      <td>7.26G</td>
      <td>416K</td>
      <td>208K</td>
      <td>20200831</td>
      <td>5 min 46 s</td>
      <td>428434</td>
    </tr>
    <tr>
      <th>661</th>
      <td>the_fascinating_science_behind_phantom_limbs_j...</td>
      <td>12.2M</td>
      <td>7.27G</td>
      <td>620K</td>
      <td>207K</td>
      <td>20181004</td>
      <td>5 min 14 s</td>
      <td>327085</td>
    </tr>
    <tr>
      <th>662</th>
      <td>when_will_the_next_mass_extinction_occur_borth...</td>
      <td>12.7M</td>
      <td>7.29G</td>
      <td>1.21M</td>
      <td>206K</td>
      <td>20160121</td>
      <td>5 min 0 s</td>
      <td>353769</td>
    </tr>
    <tr>
      <th>663</th>
      <td>how_do_you_know_if_you_have_a_virus_cella_wright</td>
      <td>10.7M</td>
      <td>7.30G</td>
      <td>411K</td>
      <td>206K</td>
      <td>20200518</td>
      <td>5 min 4 s</td>
      <td>295593</td>
    </tr>
    <tr>
      <th>664</th>
      <td>performing_brain_surgery_without_a_scalpel_hyu...</td>
      <td>17.4M</td>
      <td>7.31G</td>
      <td>205K</td>
      <td>205K</td>
      <td>20200928</td>
      <td>5 min 17 s</td>
      <td>460526</td>
    </tr>
    <tr>
      <th>665</th>
      <td>the_hidden_network_that_makes_the_internet_pos...</td>
      <td>12.9M</td>
      <td>7.33G</td>
      <td>616K</td>
      <td>205K</td>
      <td>20190422</td>
      <td>5 min 19 s</td>
      <td>338358</td>
    </tr>
    <tr>
      <th>666</th>
      <td>the_moral_roots_of_liberals_and_conservatives_...</td>
      <td>35.6M</td>
      <td>7.36G</td>
      <td>1.80M</td>
      <td>204K</td>
      <td>20121231</td>
      <td>18 min 39 s</td>
      <td>266359</td>
    </tr>
    <tr>
      <th>667</th>
      <td>how_close_are_we_to_eradicating_hiv_philip_a_chan</td>
      <td>11.3M</td>
      <td>7.37G</td>
      <td>612K</td>
      <td>204K</td>
      <td>20190610</td>
      <td>4 min 53 s</td>
      <td>322805</td>
    </tr>
    <tr>
      <th>668</th>
      <td>inside_the_ant_colony_deborah_m_gordon</td>
      <td>12.4M</td>
      <td>7.38G</td>
      <td>1.59M</td>
      <td>203K</td>
      <td>20140708</td>
      <td>4 min 46 s</td>
      <td>361888</td>
    </tr>
    <tr>
      <th>669</th>
      <td>the_genius_of_mendeleev_s_periodic_table_lou_s...</td>
      <td>7.03M</td>
      <td>7.39G</td>
      <td>1.78M</td>
      <td>203K</td>
      <td>20121121</td>
      <td>4 min 24 s</td>
      <td>223382</td>
    </tr>
    <tr>
      <th>670</th>
      <td>why_are_earthquakes_so_hard_to_predict_jean_ba...</td>
      <td>9.91M</td>
      <td>7.40G</td>
      <td>609K</td>
      <td>203K</td>
      <td>20190408</td>
      <td>4 min 53 s</td>
      <td>282837</td>
    </tr>
    <tr>
      <th>671</th>
      <td>what_happens_when_continents_collide_juan_d_ca...</td>
      <td>13.3M</td>
      <td>7.41G</td>
      <td>1.39M</td>
      <td>203K</td>
      <td>20150818</td>
      <td>4 min 57 s</td>
      <td>374288</td>
    </tr>
    <tr>
      <th>672</th>
      <td>how_do_contraceptives_work_nwhunter</td>
      <td>6.60M</td>
      <td>7.42G</td>
      <td>0.99M</td>
      <td>202K</td>
      <td>20160919</td>
      <td>4 min 20 s</td>
      <td>212333</td>
    </tr>
    <tr>
      <th>673</th>
      <td>the_first_and_last_king_of_haiti_marlene_daut</td>
      <td>8.84M</td>
      <td>7.43G</td>
      <td>404K</td>
      <td>202K</td>
      <td>20191007</td>
      <td>5 min 10 s</td>
      <td>239029</td>
    </tr>
    <tr>
      <th>674</th>
      <td>how_magellan_circumnavigated_the_globe_ewandro...</td>
      <td>15.8M</td>
      <td>7.44G</td>
      <td>0.98M</td>
      <td>201K</td>
      <td>20170330</td>
      <td>5 min 52 s</td>
      <td>376604</td>
    </tr>
    <tr>
      <th>675</th>
      <td>how_playing_sports_benefits_your_body_and_your...</td>
      <td>8.94M</td>
      <td>7.45G</td>
      <td>1.18M</td>
      <td>201K</td>
      <td>20160628</td>
      <td>3 min 46 s</td>
      <td>331048</td>
    </tr>
    <tr>
      <th>676</th>
      <td>how_fast_are_you_moving_right_now_tucker_hiatt</td>
      <td>16.2M</td>
      <td>7.47G</td>
      <td>1.57M</td>
      <td>201K</td>
      <td>20140127</td>
      <td>6 min 9 s</td>
      <td>368825</td>
    </tr>
    <tr>
      <th>677</th>
      <td>the_last_banana_a_thought_experiment_in_probab...</td>
      <td>8.23M</td>
      <td>7.48G</td>
      <td>1.37M</td>
      <td>200K</td>
      <td>20150223</td>
      <td>4 min 9 s</td>
      <td>276683</td>
    </tr>
    <tr>
      <th>678</th>
      <td>the_chaotic_brilliance_of_artist_jean_michel_b...</td>
      <td>11.5M</td>
      <td>7.49G</td>
      <td>599K</td>
      <td>200K</td>
      <td>20190228</td>
      <td>4 min 32 s</td>
      <td>354734</td>
    </tr>
    <tr>
      <th>679</th>
      <td>everything_you_need_to_know_to_read_frankenste...</td>
      <td>9.18M</td>
      <td>7.50G</td>
      <td>993K</td>
      <td>199K</td>
      <td>20170223</td>
      <td>5 min 1 s</td>
      <td>255827</td>
    </tr>
    <tr>
      <th>680</th>
      <td>what_is_phantom_traffic_and_why_is_it_ruining_...</td>
      <td>10.0M</td>
      <td>7.51G</td>
      <td>397K</td>
      <td>198K</td>
      <td>20200528</td>
      <td>4 min 53 s</td>
      <td>287329</td>
    </tr>
    <tr>
      <th>681</th>
      <td>how_interpreters_juggle_two_languages_at_once_...</td>
      <td>15.2M</td>
      <td>7.52G</td>
      <td>1.16M</td>
      <td>197K</td>
      <td>20160607</td>
      <td>4 min 55 s</td>
      <td>430212</td>
    </tr>
    <tr>
      <th>682</th>
      <td>what_happens_when_you_die_a_poetic_inquiry</td>
      <td>11.0M</td>
      <td>7.53G</td>
      <td>197K</td>
      <td>197K</td>
      <td>20201215</td>
      <td>2 min 29 s</td>
      <td>617600</td>
    </tr>
    <tr>
      <th>683</th>
      <td>the_ancient_origins_of_the_olympics_armand_d_a...</td>
      <td>9.25M</td>
      <td>7.54G</td>
      <td>1.34M</td>
      <td>196K</td>
      <td>20150903</td>
      <td>3 min 19 s</td>
      <td>388879</td>
    </tr>
    <tr>
      <th>684</th>
      <td>whats_the_difference_between_a_scientific_law_...</td>
      <td>9.55M</td>
      <td>7.55G</td>
      <td>1.15M</td>
      <td>196K</td>
      <td>20151119</td>
      <td>5 min 11 s</td>
      <td>256905</td>
    </tr>
    <tr>
      <th>685</th>
      <td>the_romans_flooded_the_colosseum_for_sea_battl...</td>
      <td>7.65M</td>
      <td>7.56G</td>
      <td>589K</td>
      <td>196K</td>
      <td>20190624</td>
      <td>4 min 19 s</td>
      <td>247698</td>
    </tr>
    <tr>
      <th>686</th>
      <td>how_to_use_a_semicolon_emma_bryce</td>
      <td>5.84M</td>
      <td>7.56G</td>
      <td>1.34M</td>
      <td>195K</td>
      <td>20150706</td>
      <td>3 min 35 s</td>
      <td>227480</td>
    </tr>
    <tr>
      <th>687</th>
      <td>the_rise_of_modern_populism_takis_s_pappas</td>
      <td>23.5M</td>
      <td>7.59G</td>
      <td>391K</td>
      <td>195K</td>
      <td>20200820</td>
      <td>6 min 21 s</td>
      <td>516161</td>
    </tr>
    <tr>
      <th>688</th>
      <td>why_should_you_read_moby_dick_sascha_morrell</td>
      <td>13.7M</td>
      <td>7.60G</td>
      <td>391K</td>
      <td>195K</td>
      <td>20200526</td>
      <td>5 min 58 s</td>
      <td>320999</td>
    </tr>
    <tr>
      <th>689</th>
      <td>whats_so_great_about_the_great_lakes_cheri_dob...</td>
      <td>10.8M</td>
      <td>7.61G</td>
      <td>975K</td>
      <td>195K</td>
      <td>20170110</td>
      <td>4 min 46 s</td>
      <td>315689</td>
    </tr>
    <tr>
      <th>690</th>
      <td>can_the_ocean_run_out_of_oxygen_kate_slabosky</td>
      <td>26.4M</td>
      <td>7.64G</td>
      <td>389K</td>
      <td>195K</td>
      <td>20200818</td>
      <td>6 min 20 s</td>
      <td>581678</td>
    </tr>
    <tr>
      <th>691</th>
      <td>how_one_journalist_risked_her_life_to_hold_mur...</td>
      <td>8.26M</td>
      <td>7.64G</td>
      <td>584K</td>
      <td>195K</td>
      <td>20190204</td>
      <td>4 min 49 s</td>
      <td>239380</td>
    </tr>
    <tr>
      <th>692</th>
      <td>everything_you_need_to_know_to_read_the_canter...</td>
      <td>8.15M</td>
      <td>7.65G</td>
      <td>580K</td>
      <td>193K</td>
      <td>20181002</td>
      <td>4 min 35 s</td>
      <td>248028</td>
    </tr>
    <tr>
      <th>693</th>
      <td>the_world_machine_think_like_a_coder_ep_10</td>
      <td>54.9M</td>
      <td>7.70G</td>
      <td>193K</td>
      <td>193K</td>
      <td>20200924</td>
      <td>12 min 9 s</td>
      <td>631128</td>
    </tr>
    <tr>
      <th>694</th>
      <td>who_s_at_risk_for_colon_cancer_amit_h_sachdev_...</td>
      <td>7.69M</td>
      <td>7.71G</td>
      <td>771K</td>
      <td>193K</td>
      <td>20180104</td>
      <td>4 min 43 s</td>
      <td>227730</td>
    </tr>
    <tr>
      <th>695</th>
      <td>it_s_a_church_it_s_a_mosque_it_s_hagia_sophia_...</td>
      <td>14.3M</td>
      <td>7.73G</td>
      <td>1.50M</td>
      <td>192K</td>
      <td>20140714</td>
      <td>5 min 11 s</td>
      <td>385298</td>
    </tr>
    <tr>
      <th>696</th>
      <td>prohibition_banning_alcohol_was_a_bad_idea_rod...</td>
      <td>20.2M</td>
      <td>7.75G</td>
      <td>382K</td>
      <td>191K</td>
      <td>20200709</td>
      <td>5 min 12 s</td>
      <td>542519</td>
    </tr>
    <tr>
      <th>697</th>
      <td>notes_of_a_native_son_the_world_according_to_j...</td>
      <td>7.73M</td>
      <td>7.75G</td>
      <td>573K</td>
      <td>191K</td>
      <td>20190212</td>
      <td>4 min 13 s</td>
      <td>255416</td>
    </tr>
    <tr>
      <th>698</th>
      <td>why_should_you_read_waiting_for_godot_iseult_g...</td>
      <td>10.1M</td>
      <td>7.76G</td>
      <td>572K</td>
      <td>191K</td>
      <td>20181015</td>
      <td>5 min 3 s</td>
      <td>278940</td>
    </tr>
    <tr>
      <th>699</th>
      <td>are_we_running_out_of_clean_water_balsher_sing...</td>
      <td>16.5M</td>
      <td>7.78G</td>
      <td>571K</td>
      <td>190K</td>
      <td>20181206</td>
      <td>5 min 18 s</td>
      <td>434315</td>
    </tr>
    <tr>
      <th>700</th>
      <td>why_do_you_need_to_get_a_flu_shot_every_year_m...</td>
      <td>8.94M</td>
      <td>7.79G</td>
      <td>761K</td>
      <td>190K</td>
      <td>20171120</td>
      <td>5 min 11 s</td>
      <td>240599</td>
    </tr>
    <tr>
      <th>701</th>
      <td>why_do_whales_sing_stephanie_sardelis</td>
      <td>9.43M</td>
      <td>7.80G</td>
      <td>947K</td>
      <td>189K</td>
      <td>20161110</td>
      <td>5 min 12 s</td>
      <td>252795</td>
    </tr>
    <tr>
      <th>702</th>
      <td>the_2400_year_search_for_the_atom_theresa_doud</td>
      <td>8.42M</td>
      <td>7.81G</td>
      <td>1.29M</td>
      <td>189K</td>
      <td>20141208</td>
      <td>5 min 22 s</td>
      <td>219308</td>
    </tr>
    <tr>
      <th>703</th>
      <td>how_miscommunication_happens_and_how_to_avoid_...</td>
      <td>8.33M</td>
      <td>7.81G</td>
      <td>1.10M</td>
      <td>188K</td>
      <td>20160222</td>
      <td>4 min 32 s</td>
      <td>256309</td>
    </tr>
    <tr>
      <th>704</th>
      <td>vermicomposting_how_worms_can_reduce_our_waste...</td>
      <td>6.59M</td>
      <td>7.82G</td>
      <td>1.65M</td>
      <td>188K</td>
      <td>20130626</td>
      <td>4 min 29 s</td>
      <td>205448</td>
    </tr>
    <tr>
      <th>705</th>
      <td>why_is_this_painting_so_shocking_iseult_gillespie</td>
      <td>10.2M</td>
      <td>7.83G</td>
      <td>563K</td>
      <td>188K</td>
      <td>20190430</td>
      <td>5 min 15 s</td>
      <td>270873</td>
    </tr>
    <tr>
      <th>706</th>
      <td>how_the_konigsberg_bridge_problem_changed_math...</td>
      <td>7.79M</td>
      <td>7.84G</td>
      <td>1.10M</td>
      <td>188K</td>
      <td>20160901</td>
      <td>4 min 38 s</td>
      <td>234408</td>
    </tr>
    <tr>
      <th>707</th>
      <td>how_x_rays_see_through_your_skin_ge_wang</td>
      <td>8.37M</td>
      <td>7.85G</td>
      <td>1.28M</td>
      <td>187K</td>
      <td>20150622</td>
      <td>4 min 42 s</td>
      <td>249053</td>
    </tr>
    <tr>
      <th>708</th>
      <td>insults_by_shakespeare</td>
      <td>12.9M</td>
      <td>7.86G</td>
      <td>1.83M</td>
      <td>187K</td>
      <td>20120504</td>
      <td>6 min 23 s</td>
      <td>281205</td>
    </tr>
    <tr>
      <th>709</th>
      <td>where_did_earths_water_come_from_zachary_metz</td>
      <td>6.17M</td>
      <td>7.86G</td>
      <td>1.28M</td>
      <td>187K</td>
      <td>20150323</td>
      <td>3 min 52 s</td>
      <td>222764</td>
    </tr>
    <tr>
      <th>710</th>
      <td>why_havent_we_cured_arthritis_kaitlyn_sadtler_...</td>
      <td>6.52M</td>
      <td>7.87G</td>
      <td>374K</td>
      <td>187K</td>
      <td>20191107</td>
      <td>4 min 24 s</td>
      <td>206459</td>
    </tr>
    <tr>
      <th>711</th>
      <td>grammar_s_great_divide_the_oxford_comma_ted_ed</td>
      <td>6.93M</td>
      <td>7.88G</td>
      <td>1.46M</td>
      <td>186K</td>
      <td>20140317</td>
      <td>3 min 25 s</td>
      <td>283354</td>
    </tr>
    <tr>
      <th>712</th>
      <td>why_people_fall_for_misinformation_joseph_isaac</td>
      <td>19.2M</td>
      <td>7.90G</td>
      <td>372K</td>
      <td>186K</td>
      <td>20200903</td>
      <td>5 min 15 s</td>
      <td>509235</td>
    </tr>
    <tr>
      <th>713</th>
      <td>why_do_buildings_fall_in_earthquakes_vicki_v_may</td>
      <td>11.3M</td>
      <td>7.91G</td>
      <td>1.27M</td>
      <td>186K</td>
      <td>20150126</td>
      <td>4 min 51 s</td>
      <td>324626</td>
    </tr>
    <tr>
      <th>714</th>
      <td>if_superpowers_were_real_super_speed_joy_lin</td>
      <td>17.0M</td>
      <td>7.92G</td>
      <td>1.64M</td>
      <td>186K</td>
      <td>20130628</td>
      <td>4 min 50 s</td>
      <td>491915</td>
    </tr>
    <tr>
      <th>715</th>
      <td>you_are_your_microbes_jessica_green_and_karen_...</td>
      <td>8.29M</td>
      <td>7.93G</td>
      <td>1.63M</td>
      <td>186K</td>
      <td>20130107</td>
      <td>3 min 45 s</td>
      <td>308963</td>
    </tr>
    <tr>
      <th>716</th>
      <td>the_greatest_machine_that_never_was_john_graha...</td>
      <td>21.4M</td>
      <td>7.95G</td>
      <td>1.63M</td>
      <td>185K</td>
      <td>20130619</td>
      <td>12 min 14 s</td>
      <td>243943</td>
    </tr>
    <tr>
      <th>717</th>
      <td>urbanization_and_the_future_of_cities_vance_kite</td>
      <td>8.36M</td>
      <td>7.96G</td>
      <td>1.62M</td>
      <td>184K</td>
      <td>20130912</td>
      <td>4 min 8 s</td>
      <td>282777</td>
    </tr>
    <tr>
      <th>718</th>
      <td>are_food_preservatives_bad_for_you_eleanor_nelsen</td>
      <td>7.47M</td>
      <td>7.97G</td>
      <td>918K</td>
      <td>184K</td>
      <td>20161108</td>
      <td>4 min 52 s</td>
      <td>214041</td>
    </tr>
    <tr>
      <th>719</th>
      <td>the_secret_language_of_trees_camille_defrenne_...</td>
      <td>8.80M</td>
      <td>7.98G</td>
      <td>547K</td>
      <td>182K</td>
      <td>20190701</td>
      <td>4 min 33 s</td>
      <td>269552</td>
    </tr>
    <tr>
      <th>720</th>
      <td>how_this_disease_changes_the_shape_of_your_cel...</td>
      <td>11.2M</td>
      <td>7.99G</td>
      <td>547K</td>
      <td>182K</td>
      <td>20190506</td>
      <td>4 min 40 s</td>
      <td>334997</td>
    </tr>
    <tr>
      <th>721</th>
      <td>what_are_gravitational_waves_amber_l_stuver</td>
      <td>7.34M</td>
      <td>8.00G</td>
      <td>727K</td>
      <td>182K</td>
      <td>20170914</td>
      <td>5 min 24 s</td>
      <td>189577</td>
    </tr>
    <tr>
      <th>722</th>
      <td>where_do_new_words_come_from_marcel_danesi</td>
      <td>9.27M</td>
      <td>8.00G</td>
      <td>905K</td>
      <td>181K</td>
      <td>20170907</td>
      <td>5 min 43 s</td>
      <td>226651</td>
    </tr>
    <tr>
      <th>723</th>
      <td>the_furnace_bots_think_like_a_coder_ep_3</td>
      <td>11.3M</td>
      <td>8.02G</td>
      <td>360K</td>
      <td>180K</td>
      <td>20191118</td>
      <td>6 min 11 s</td>
      <td>256414</td>
    </tr>
    <tr>
      <th>724</th>
      <td>how_to_biohack_your_cells_to_fight_cancer_greg...</td>
      <td>24.5M</td>
      <td>8.04G</td>
      <td>539K</td>
      <td>180K</td>
      <td>20190409</td>
      <td>8 min 0 s</td>
      <td>427206</td>
    </tr>
    <tr>
      <th>725</th>
      <td>how_do_geckos_defy_gravity_eleanor_nelsen</td>
      <td>7.93M</td>
      <td>8.05G</td>
      <td>1.23M</td>
      <td>179K</td>
      <td>20150330</td>
      <td>4 min 29 s</td>
      <td>247211</td>
    </tr>
    <tr>
      <th>726</th>
      <td>how_exactly_does_binary_code_work_jose_americo...</td>
      <td>8.37M</td>
      <td>8.06G</td>
      <td>712K</td>
      <td>178K</td>
      <td>20180712</td>
      <td>4 min 39 s</td>
      <td>251190</td>
    </tr>
    <tr>
      <th>727</th>
      <td>why_the_solar_system_can_exist</td>
      <td>3.58M</td>
      <td>8.06G</td>
      <td>1.73M</td>
      <td>177K</td>
      <td>20120503</td>
      <td>2 min 6 s</td>
      <td>237445</td>
    </tr>
    <tr>
      <th>728</th>
      <td>why_is_being_scared_so_fun_margee_kerr</td>
      <td>10.8M</td>
      <td>8.07G</td>
      <td>1.03M</td>
      <td>177K</td>
      <td>20160421</td>
      <td>4 min 28 s</td>
      <td>338370</td>
    </tr>
    <tr>
      <th>729</th>
      <td>what_happens_when_you_get_heat_stroke_douglas_...</td>
      <td>6.07M</td>
      <td>8.08G</td>
      <td>1.38M</td>
      <td>176K</td>
      <td>20140721</td>
      <td>3 min 53 s</td>
      <td>217954</td>
    </tr>
    <tr>
      <th>730</th>
      <td>how_small_are_we_in_the_scale_of_the_universe_...</td>
      <td>9.16M</td>
      <td>8.08G</td>
      <td>875K</td>
      <td>175K</td>
      <td>20170213</td>
      <td>4 min 7 s</td>
      <td>310452</td>
    </tr>
    <tr>
      <th>731</th>
      <td>why_are_human_bodies_asymmetrical_leo_q_wan</td>
      <td>8.05M</td>
      <td>8.09G</td>
      <td>1.02M</td>
      <td>175K</td>
      <td>20160125</td>
      <td>4 min 18 s</td>
      <td>261470</td>
    </tr>
    <tr>
      <th>732</th>
      <td>eye_vs_camera_michael_mauser</td>
      <td>13.3M</td>
      <td>8.11G</td>
      <td>1.19M</td>
      <td>174K</td>
      <td>20150406</td>
      <td>4 min 56 s</td>
      <td>377782</td>
    </tr>
    <tr>
      <th>733</th>
      <td>a_3d_atlas_of_the_universe_carter_emmart</td>
      <td>18.8M</td>
      <td>8.12G</td>
      <td>1.53M</td>
      <td>174K</td>
      <td>20130308</td>
      <td>6 min 57 s</td>
      <td>377033</td>
    </tr>
    <tr>
      <th>734</th>
      <td>the_law_of_conservation_of_mass_todd_ramsey</td>
      <td>8.86M</td>
      <td>8.13G</td>
      <td>1.19M</td>
      <td>174K</td>
      <td>20150226</td>
      <td>4 min 36 s</td>
      <td>268991</td>
    </tr>
    <tr>
      <th>735</th>
      <td>how_many_ways_can_you_arrange_a_deck_of_cards_...</td>
      <td>5.19M</td>
      <td>8.14G</td>
      <td>1.35M</td>
      <td>173K</td>
      <td>20140327</td>
      <td>3 min 41 s</td>
      <td>196224</td>
    </tr>
    <tr>
      <th>736</th>
      <td>what_s_an_algorithm_david_j_malan</td>
      <td>7.77M</td>
      <td>8.14G</td>
      <td>1.52M</td>
      <td>173K</td>
      <td>20130520</td>
      <td>4 min 57 s</td>
      <td>219358</td>
    </tr>
    <tr>
      <th>737</th>
      <td>whats_a_squillo_and_why_do_opera_singers_need_...</td>
      <td>16.3M</td>
      <td>8.16G</td>
      <td>346K</td>
      <td>173K</td>
      <td>20200309</td>
      <td>5 min 12 s</td>
      <td>437255</td>
    </tr>
    <tr>
      <th>738</th>
      <td>the_math_behind_michael_jordans_legendary_hang...</td>
      <td>6.10M</td>
      <td>8.17G</td>
      <td>1.17M</td>
      <td>172K</td>
      <td>20150604</td>
      <td>3 min 45 s</td>
      <td>227250</td>
    </tr>
    <tr>
      <th>739</th>
      <td>the_secret_messages_of_viking_runestones_jesse...</td>
      <td>6.43M</td>
      <td>8.17G</td>
      <td>343K</td>
      <td>171K</td>
      <td>20200220</td>
      <td>4 min 34 s</td>
      <td>196482</td>
    </tr>
    <tr>
      <th>740</th>
      <td>inside_the_minds_of_animals_bryan_b_rasmussen</td>
      <td>9.40M</td>
      <td>8.18G</td>
      <td>1.17M</td>
      <td>171K</td>
      <td>20150714</td>
      <td>5 min 12 s</td>
      <td>252436</td>
    </tr>
    <tr>
      <th>741</th>
      <td>you_are_more_transparent_than_you_think_sajan_...</td>
      <td>9.69M</td>
      <td>8.19G</td>
      <td>512K</td>
      <td>171K</td>
      <td>20190604</td>
      <td>5 min 22 s</td>
      <td>252061</td>
    </tr>
    <tr>
      <th>742</th>
      <td>evolutions_great_mystery_michael_corballis</td>
      <td>17.5M</td>
      <td>8.21G</td>
      <td>341K</td>
      <td>171K</td>
      <td>20200824</td>
      <td>4 min 42 s</td>
      <td>518454</td>
    </tr>
    <tr>
      <th>743</th>
      <td>the_train_heist_think_like_a_coder_ep_4</td>
      <td>14.6M</td>
      <td>8.22G</td>
      <td>341K</td>
      <td>171K</td>
      <td>20191209</td>
      <td>5 min 59 s</td>
      <td>341613</td>
    </tr>
    <tr>
      <th>744</th>
      <td>the_secret_life_of_plankton</td>
      <td>18.3M</td>
      <td>8.24G</td>
      <td>1.66M</td>
      <td>170K</td>
      <td>20120402</td>
      <td>6 min 1 s</td>
      <td>423318</td>
    </tr>
    <tr>
      <th>745</th>
      <td>how_do_drugs_affect_the_brain_sara_garofalo</td>
      <td>9.52M</td>
      <td>8.25G</td>
      <td>849K</td>
      <td>170K</td>
      <td>20170629</td>
      <td>5 min 4 s</td>
      <td>262329</td>
    </tr>
    <tr>
      <th>746</th>
      <td>the_turing_test_can_a_computer_pass_for_a_huma...</td>
      <td>11.1M</td>
      <td>8.26G</td>
      <td>0.99M</td>
      <td>169K</td>
      <td>20160425</td>
      <td>4 min 42 s</td>
      <td>330797</td>
    </tr>
    <tr>
      <th>747</th>
      <td>how_false_news_can_spread_noah_tavlin</td>
      <td>6.63M</td>
      <td>8.27G</td>
      <td>1.16M</td>
      <td>169K</td>
      <td>20150827</td>
      <td>3 min 41 s</td>
      <td>251151</td>
    </tr>
    <tr>
      <th>748</th>
      <td>how_do_we_smell_rose_eveleth</td>
      <td>8.22M</td>
      <td>8.28G</td>
      <td>1.32M</td>
      <td>169K</td>
      <td>20131219</td>
      <td>4 min 19 s</td>
      <td>265698</td>
    </tr>
    <tr>
      <th>749</th>
      <td>the_basics_of_the_higgs_boson_dave_barney_and_...</td>
      <td>8.81M</td>
      <td>8.28G</td>
      <td>1.48M</td>
      <td>169K</td>
      <td>20130503</td>
      <td>6 min 29 s</td>
      <td>189703</td>
    </tr>
    <tr>
      <th>750</th>
      <td>will_the_ocean_ever_run_out_of_fish_ayana_eliz...</td>
      <td>8.77M</td>
      <td>8.29G</td>
      <td>841K</td>
      <td>168K</td>
      <td>20170810</td>
      <td>4 min 27 s</td>
      <td>275311</td>
    </tr>
    <tr>
      <th>751</th>
      <td>how_big_is_a_mole_not_the_animal_the_other_one...</td>
      <td>8.84M</td>
      <td>8.30G</td>
      <td>1.64M</td>
      <td>168K</td>
      <td>20120911</td>
      <td>4 min 32 s</td>
      <td>272652</td>
    </tr>
    <tr>
      <th>752</th>
      <td>how_do_animals_see_in_the_dark_anna_stockl</td>
      <td>12.7M</td>
      <td>8.31G</td>
      <td>0.98M</td>
      <td>168K</td>
      <td>20160825</td>
      <td>4 min 22 s</td>
      <td>404974</td>
    </tr>
    <tr>
      <th>753</th>
      <td>a_brief_history_of_melancholy_courtney_stephens</td>
      <td>8.22M</td>
      <td>8.32G</td>
      <td>1.14M</td>
      <td>167K</td>
      <td>20141002</td>
      <td>5 min 28 s</td>
      <td>209700</td>
    </tr>
    <tr>
      <th>754</th>
      <td>how_crispr_lets_you_edit_dna_andrea_m_henle</td>
      <td>8.32M</td>
      <td>8.33G</td>
      <td>500K</td>
      <td>167K</td>
      <td>20190124</td>
      <td>5 min 28 s</td>
      <td>212242</td>
    </tr>
    <tr>
      <th>755</th>
      <td>is_the_weather_actually_becoming_more_extreme_...</td>
      <td>20.6M</td>
      <td>8.35G</td>
      <td>333K</td>
      <td>166K</td>
      <td>20200825</td>
      <td>5 min 21 s</td>
      <td>537412</td>
    </tr>
    <tr>
      <th>756</th>
      <td>lets_plant_20_million_trees_together_teamtrees</td>
      <td>2.39M</td>
      <td>8.35G</td>
      <td>332K</td>
      <td>166K</td>
      <td>20191025</td>
      <td>1 min 0 s</td>
      <td>333994</td>
    </tr>
    <tr>
      <th>757</th>
      <td>is_it_possible_to_create_a_perfect_vacuum_rolf...</td>
      <td>18.3M</td>
      <td>8.37G</td>
      <td>827K</td>
      <td>165K</td>
      <td>20170912</td>
      <td>4 min 31 s</td>
      <td>566018</td>
    </tr>
    <tr>
      <th>758</th>
      <td>this_sea_creature_breathes_through_its_butt_ce...</td>
      <td>11.5M</td>
      <td>8.38G</td>
      <td>330K</td>
      <td>165K</td>
      <td>20200430</td>
      <td>5 min 2 s</td>
      <td>317272</td>
    </tr>
    <tr>
      <th>759</th>
      <td>the_wildly_complex_anatomy_of_a_sneaker_angel_...</td>
      <td>9.13M</td>
      <td>8.39G</td>
      <td>329K</td>
      <td>165K</td>
      <td>20200423</td>
      <td>5 min 22 s</td>
      <td>237628</td>
    </tr>
    <tr>
      <th>760</th>
      <td>would_winning_the_lottery_make_you_happier_raj...</td>
      <td>7.85M</td>
      <td>8.40G</td>
      <td>822K</td>
      <td>164K</td>
      <td>20170207</td>
      <td>4 min 35 s</td>
      <td>238865</td>
    </tr>
    <tr>
      <th>761</th>
      <td>why_are_there_so_many_types_of_apples_theresa_...</td>
      <td>6.49M</td>
      <td>8.40G</td>
      <td>821K</td>
      <td>164K</td>
      <td>20160922</td>
      <td>4 min 27 s</td>
      <td>203115</td>
    </tr>
    <tr>
      <th>762</th>
      <td>do_politics_make_us_irrational_jay_van_bavel</td>
      <td>13.2M</td>
      <td>8.42G</td>
      <td>328K</td>
      <td>164K</td>
      <td>20200204</td>
      <td>5 min 36 s</td>
      <td>328806</td>
    </tr>
    <tr>
      <th>763</th>
      <td>what_is_epigenetics_carlos_guerrero_bosagna</td>
      <td>11.0M</td>
      <td>8.43G</td>
      <td>985K</td>
      <td>164K</td>
      <td>20160627</td>
      <td>5 min 2 s</td>
      <td>304045</td>
    </tr>
    <tr>
      <th>764</th>
      <td>the_truth_about_electroconvulsive_therapy_ect_...</td>
      <td>8.03M</td>
      <td>8.44G</td>
      <td>492K</td>
      <td>164K</td>
      <td>20190114</td>
      <td>4 min 23 s</td>
      <td>255547</td>
    </tr>
    <tr>
      <th>765</th>
      <td>how_many_universes_are_there_chris_anderson</td>
      <td>15.2M</td>
      <td>8.45G</td>
      <td>1.60M</td>
      <td>164K</td>
      <td>20120311</td>
      <td>4 min 42 s</td>
      <td>450893</td>
    </tr>
    <tr>
      <th>766</th>
      <td>what_you_might_not_know_about_the_declaration_...</td>
      <td>7.85M</td>
      <td>8.46G</td>
      <td>1.28M</td>
      <td>164K</td>
      <td>20140701</td>
      <td>3 min 37 s</td>
      <td>302019</td>
    </tr>
    <tr>
      <th>767</th>
      <td>how_do_cancer_cells_behave_differently_from_he...</td>
      <td>11.7M</td>
      <td>8.47G</td>
      <td>1.44M</td>
      <td>164K</td>
      <td>20121205</td>
      <td>3 min 50 s</td>
      <td>427043</td>
    </tr>
    <tr>
      <th>768</th>
      <td>the_mysterious_origins_of_life_on_earth_luka_s...</td>
      <td>11.0M</td>
      <td>8.48G</td>
      <td>489K</td>
      <td>163K</td>
      <td>20190826</td>
      <td>4 min 56 s</td>
      <td>312629</td>
    </tr>
    <tr>
      <th>769</th>
      <td>the_ballet_that_incited_a_riot_iseult_gillespie</td>
      <td>11.4M</td>
      <td>8.49G</td>
      <td>326K</td>
      <td>163K</td>
      <td>20200114</td>
      <td>5 min 2 s</td>
      <td>314652</td>
    </tr>
    <tr>
      <th>770</th>
      <td>aphasia_the_disorder_that_makes_you_lose_your_...</td>
      <td>14.1M</td>
      <td>8.51G</td>
      <td>813K</td>
      <td>163K</td>
      <td>20160915</td>
      <td>5 min 10 s</td>
      <td>381478</td>
    </tr>
    <tr>
      <th>771</th>
      <td>the_survival_of_the_sea_turtle</td>
      <td>7.90M</td>
      <td>8.51G</td>
      <td>1.59M</td>
      <td>162K</td>
      <td>20120723</td>
      <td>4 min 25 s</td>
      <td>249844</td>
    </tr>
    <tr>
      <th>772</th>
      <td>how_menstruation_works_emma_bryce</td>
      <td>8.57M</td>
      <td>8.52G</td>
      <td>973K</td>
      <td>162K</td>
      <td>20160112</td>
      <td>4 min 11 s</td>
      <td>286128</td>
    </tr>
    <tr>
      <th>773</th>
      <td>how_close_are_we_to_uploading_our_minds_michae...</td>
      <td>8.59M</td>
      <td>8.53G</td>
      <td>324K</td>
      <td>162K</td>
      <td>20191028</td>
      <td>5 min 5 s</td>
      <td>235820</td>
    </tr>
    <tr>
      <th>774</th>
      <td>the_history_of_the_barometer_and_how_it_works_...</td>
      <td>6.07M</td>
      <td>8.54G</td>
      <td>1.27M</td>
      <td>162K</td>
      <td>20140728</td>
      <td>4 min 45 s</td>
      <td>178364</td>
    </tr>
    <tr>
      <th>775</th>
      <td>the_beneficial_bacteria_that_make_delicious_fo...</td>
      <td>7.20M</td>
      <td>8.54G</td>
      <td>973K</td>
      <td>162K</td>
      <td>20160119</td>
      <td>4 min 39 s</td>
      <td>216201</td>
    </tr>
    <tr>
      <th>776</th>
      <td>who_was_the_world_s_first_author_soraya_field_...</td>
      <td>9.72M</td>
      <td>8.55G</td>
      <td>324K</td>
      <td>162K</td>
      <td>20200323</td>
      <td>4 min 55 s</td>
      <td>275963</td>
    </tr>
    <tr>
      <th>777</th>
      <td>how_do_your_kidneys_work_emma_bryce</td>
      <td>6.69M</td>
      <td>8.56G</td>
      <td>1.10M</td>
      <td>162K</td>
      <td>20150209</td>
      <td>3 min 54 s</td>
      <td>239239</td>
    </tr>
    <tr>
      <th>778</th>
      <td>what_is_verbal_irony_christopher_warner</td>
      <td>8.04M</td>
      <td>8.57G</td>
      <td>1.41M</td>
      <td>161K</td>
      <td>20130313</td>
      <td>3 min 28 s</td>
      <td>323139</td>
    </tr>
    <tr>
      <th>779</th>
      <td>why_shakespeare_loved_iambic_pentameter_david_...</td>
      <td>10.3M</td>
      <td>8.58G</td>
      <td>1.10M</td>
      <td>161K</td>
      <td>20150127</td>
      <td>5 min 21 s</td>
      <td>268319</td>
    </tr>
    <tr>
      <th>780</th>
      <td>does_stress_affect_your_memory_elizabeth_cox</td>
      <td>8.10M</td>
      <td>8.58G</td>
      <td>642K</td>
      <td>160K</td>
      <td>20180904</td>
      <td>4 min 43 s</td>
      <td>239597</td>
    </tr>
    <tr>
      <th>781</th>
      <td>how_to_speed_up_chemical_reactions_and_get_a_d...</td>
      <td>11.1M</td>
      <td>8.60G</td>
      <td>1.56M</td>
      <td>159K</td>
      <td>20120618</td>
      <td>4 min 55 s</td>
      <td>314945</td>
    </tr>
    <tr>
      <th>782</th>
      <td>why_should_you_read_virgil_s_aeneid_mark_robinson</td>
      <td>17.1M</td>
      <td>8.61G</td>
      <td>634K</td>
      <td>158K</td>
      <td>20171019</td>
      <td>5 min 35 s</td>
      <td>428358</td>
    </tr>
    <tr>
      <th>783</th>
      <td>why_do_we_kiss_under_mistletoe_carlos_reif</td>
      <td>6.59M</td>
      <td>8.62G</td>
      <td>792K</td>
      <td>158K</td>
      <td>20161222</td>
      <td>4 min 41 s</td>
      <td>196324</td>
    </tr>
    <tr>
      <th>784</th>
      <td>why_do_we_have_to_wear_sunscreen_kevin_p_boyd</td>
      <td>8.69M</td>
      <td>8.63G</td>
      <td>1.39M</td>
      <td>158K</td>
      <td>20130806</td>
      <td>5 min 1 s</td>
      <td>241891</td>
    </tr>
    <tr>
      <th>785</th>
      <td>what_happened_to_antimatter_rolf_landua</td>
      <td>14.4M</td>
      <td>8.64G</td>
      <td>1.39M</td>
      <td>158K</td>
      <td>20130503</td>
      <td>5 min 16 s</td>
      <td>380859</td>
    </tr>
    <tr>
      <th>786</th>
      <td>how_does_your_body_know_what_time_it_is_marco_...</td>
      <td>7.91M</td>
      <td>8.65G</td>
      <td>789K</td>
      <td>158K</td>
      <td>20161208</td>
      <td>5 min 8 s</td>
      <td>215342</td>
    </tr>
    <tr>
      <th>787</th>
      <td>the_mystery_of_motion_sickness_rose_eveleth</td>
      <td>5.10M</td>
      <td>8.65G</td>
      <td>1.23M</td>
      <td>158K</td>
      <td>20140113</td>
      <td>3 min 9 s</td>
      <td>225385</td>
    </tr>
    <tr>
      <th>788</th>
      <td>why_is_this_painting_so_captivating_james_earl...</td>
      <td>6.89M</td>
      <td>8.66G</td>
      <td>943K</td>
      <td>157K</td>
      <td>20160310</td>
      <td>3 min 52 s</td>
      <td>248903</td>
    </tr>
    <tr>
      <th>789</th>
      <td>the_evolution_of_the_human_eye_joshua_harvey</td>
      <td>7.25M</td>
      <td>8.67G</td>
      <td>1.07M</td>
      <td>156K</td>
      <td>20150108</td>
      <td>4 min 43 s</td>
      <td>214936</td>
    </tr>
    <tr>
      <th>790</th>
      <td>secrets_of_the_x_chromosome_robin_ball</td>
      <td>6.36M</td>
      <td>8.67G</td>
      <td>778K</td>
      <td>156K</td>
      <td>20170418</td>
      <td>5 min 5 s</td>
      <td>174294</td>
    </tr>
    <tr>
      <th>791</th>
      <td>how_many_verb_tenses_are_there_in_english_anna...</td>
      <td>9.51M</td>
      <td>8.68G</td>
      <td>622K</td>
      <td>156K</td>
      <td>20171106</td>
      <td>4 min 27 s</td>
      <td>298828</td>
    </tr>
    <tr>
      <th>792</th>
      <td>a_day_in_the_life_of_a_cossack_warrior_alex_ge...</td>
      <td>14.2M</td>
      <td>8.70G</td>
      <td>466K</td>
      <td>155K</td>
      <td>20190822</td>
      <td>4 min 47 s</td>
      <td>414450</td>
    </tr>
    <tr>
      <th>793</th>
      <td>why_should_you_read_a_midsummer_night_s_dream_...</td>
      <td>13.0M</td>
      <td>8.71G</td>
      <td>459K</td>
      <td>153K</td>
      <td>20181203</td>
      <td>4 min 42 s</td>
      <td>386143</td>
    </tr>
    <tr>
      <th>794</th>
      <td>the_hidden_life_of_rosa_parks_riche_d_richardson</td>
      <td>11.7M</td>
      <td>8.72G</td>
      <td>306K</td>
      <td>153K</td>
      <td>20200413</td>
      <td>4 min 59 s</td>
      <td>327525</td>
    </tr>
    <tr>
      <th>795</th>
      <td>einstein_s_brilliant_mistake_entangled_states_...</td>
      <td>8.45M</td>
      <td>8.73G</td>
      <td>1.05M</td>
      <td>153K</td>
      <td>20141016</td>
      <td>5 min 9 s</td>
      <td>229215</td>
    </tr>
    <tr>
      <th>796</th>
      <td>who_was_confucius_bryan_w_van_norden</td>
      <td>10.6M</td>
      <td>8.74G</td>
      <td>915K</td>
      <td>153K</td>
      <td>20151027</td>
      <td>4 min 29 s</td>
      <td>331382</td>
    </tr>
    <tr>
      <th>797</th>
      <td>whats_a_smartphone_made_of_kim_preshoff</td>
      <td>10.9M</td>
      <td>8.75G</td>
      <td>457K</td>
      <td>152K</td>
      <td>20181001</td>
      <td>4 min 55 s</td>
      <td>308374</td>
    </tr>
    <tr>
      <th>798</th>
      <td>why_should_you_read_the_master_and_margarita_a...</td>
      <td>7.97M</td>
      <td>8.76G</td>
      <td>455K</td>
      <td>152K</td>
      <td>20190530</td>
      <td>4 min 32 s</td>
      <td>245499</td>
    </tr>
    <tr>
      <th>799</th>
      <td>why_does_ice_float_in_water_george_zaidan_and_...</td>
      <td>8.04M</td>
      <td>8.77G</td>
      <td>1.18M</td>
      <td>151K</td>
      <td>20131022</td>
      <td>3 min 55 s</td>
      <td>286052</td>
    </tr>
    <tr>
      <th>800</th>
      <td>how_statistics_can_be_misleading_mark_liddell</td>
      <td>10.0M</td>
      <td>8.78G</td>
      <td>907K</td>
      <td>151K</td>
      <td>20160114</td>
      <td>4 min 18 s</td>
      <td>324519</td>
    </tr>
    <tr>
      <th>801</th>
      <td>how_long_will_human_impacts_last_david_biello</td>
      <td>8.98M</td>
      <td>8.78G</td>
      <td>597K</td>
      <td>149K</td>
      <td>20171204</td>
      <td>5 min 29 s</td>
      <td>229031</td>
    </tr>
    <tr>
      <th>802</th>
      <td>how_do_our_brains_process_speech_gareth_gaskell</td>
      <td>23.4M</td>
      <td>8.81G</td>
      <td>297K</td>
      <td>149K</td>
      <td>20200723</td>
      <td>4 min 53 s</td>
      <td>668567</td>
    </tr>
    <tr>
      <th>803</th>
      <td>what_color_is_tuesday_exploring_synesthesia_ri...</td>
      <td>9.95M</td>
      <td>8.82G</td>
      <td>1.30M</td>
      <td>148K</td>
      <td>20130610</td>
      <td>3 min 56 s</td>
      <td>353267</td>
    </tr>
    <tr>
      <th>804</th>
      <td>the_big_beaked_rock_munching_fish_that_protect...</td>
      <td>24.2M</td>
      <td>8.84G</td>
      <td>296K</td>
      <td>148K</td>
      <td>20200804</td>
      <td>5 min 4 s</td>
      <td>665186</td>
    </tr>
    <tr>
      <th>805</th>
      <td>if_superpowers_were_real_invisibility_joy_lin</td>
      <td>13.4M</td>
      <td>8.85G</td>
      <td>1.28M</td>
      <td>146K</td>
      <td>20130627</td>
      <td>4 min 32 s</td>
      <td>411431</td>
    </tr>
    <tr>
      <th>806</th>
      <td>why_is_nasa_sending_a_spacecraft_to_a_metal_wo...</td>
      <td>8.76M</td>
      <td>8.86G</td>
      <td>584K</td>
      <td>146K</td>
      <td>20180129</td>
      <td>4 min 19 s</td>
      <td>282789</td>
    </tr>
    <tr>
      <th>807</th>
      <td>how_the_sandwich_was_invented_moments_of_visio...</td>
      <td>3.90M</td>
      <td>8.87G</td>
      <td>729K</td>
      <td>146K</td>
      <td>20161103</td>
      <td>1 min 48 s</td>
      <td>301704</td>
    </tr>
    <tr>
      <th>808</th>
      <td>how_did_teeth_evolve_peter_s_ungar</td>
      <td>12.0M</td>
      <td>8.88G</td>
      <td>583K</td>
      <td>146K</td>
      <td>20180205</td>
      <td>4 min 44 s</td>
      <td>352162</td>
    </tr>
    <tr>
      <th>809</th>
      <td>the_fundamentals_of_space_time_part_1_andrew_p...</td>
      <td>7.99M</td>
      <td>8.89G</td>
      <td>1.13M</td>
      <td>145K</td>
      <td>20140324</td>
      <td>5 min 5 s</td>
      <td>219064</td>
    </tr>
    <tr>
      <th>810</th>
      <td>the_chasm_think_like_a_coder_ep_6</td>
      <td>16.3M</td>
      <td>8.90G</td>
      <td>287K</td>
      <td>144K</td>
      <td>20200130</td>
      <td>6 min 40 s</td>
      <td>340350</td>
    </tr>
    <tr>
      <th>811</th>
      <td>the_death_of_the_universe_renee_hlozek</td>
      <td>6.52M</td>
      <td>8.91G</td>
      <td>1.12M</td>
      <td>144K</td>
      <td>20131212</td>
      <td>4 min 38 s</td>
      <td>195892</td>
    </tr>
    <tr>
      <th>812</th>
      <td>can_animals_be_deceptive_eldridge_adams</td>
      <td>7.42M</td>
      <td>8.92G</td>
      <td>429K</td>
      <td>143K</td>
      <td>20181218</td>
      <td>4 min 55 s</td>
      <td>210258</td>
    </tr>
    <tr>
      <th>813</th>
      <td>introducing_earth_school</td>
      <td>2.24M</td>
      <td>8.92G</td>
      <td>285K</td>
      <td>143K</td>
      <td>20200422</td>
      <td>54 s 450 ms</td>
      <td>344408</td>
    </tr>
    <tr>
      <th>814</th>
      <td>if_superpowers_were_real_body_mass_joy_lin</td>
      <td>21.6M</td>
      <td>8.94G</td>
      <td>1.25M</td>
      <td>143K</td>
      <td>20130627</td>
      <td>6 min 44 s</td>
      <td>447858</td>
    </tr>
    <tr>
      <th>815</th>
      <td>a_3_minute_guide_to_the_bill_of_rights_belinda...</td>
      <td>7.50M</td>
      <td>8.95G</td>
      <td>1.25M</td>
      <td>142K</td>
      <td>20121030</td>
      <td>3 min 34 s</td>
      <td>293798</td>
    </tr>
    <tr>
      <th>816</th>
      <td>the_left_brain_vs_right_brain_myth_elizabeth_w...</td>
      <td>12.2M</td>
      <td>8.96G</td>
      <td>711K</td>
      <td>142K</td>
      <td>20170724</td>
      <td>4 min 11 s</td>
      <td>407057</td>
    </tr>
    <tr>
      <th>817</th>
      <td>the_tower_of_epiphany_think_like_a_coder_ep_7</td>
      <td>19.5M</td>
      <td>8.98G</td>
      <td>284K</td>
      <td>142K</td>
      <td>20200227</td>
      <td>8 min 13 s</td>
      <td>331411</td>
    </tr>
    <tr>
      <th>818</th>
      <td>what_is_love_brad_troeger</td>
      <td>14.7M</td>
      <td>8.99G</td>
      <td>1.25M</td>
      <td>142K</td>
      <td>20130909</td>
      <td>4 min 59 s</td>
      <td>410001</td>
    </tr>
    <tr>
      <th>819</th>
      <td>how_far_would_you_have_to_go_to_escape_gravity...</td>
      <td>10.8M</td>
      <td>9.00G</td>
      <td>425K</td>
      <td>142K</td>
      <td>20181106</td>
      <td>4 min 55 s</td>
      <td>307285</td>
    </tr>
    <tr>
      <th>820</th>
      <td>why_is_aristophanes_called_the_father_of_comed...</td>
      <td>11.0M</td>
      <td>9.01G</td>
      <td>566K</td>
      <td>141K</td>
      <td>20180821</td>
      <td>5 min 11 s</td>
      <td>295465</td>
    </tr>
    <tr>
      <th>821</th>
      <td>how_to_see_more_and_care_less_the_art_of_georg...</td>
      <td>18.0M</td>
      <td>9.03G</td>
      <td>281K</td>
      <td>141K</td>
      <td>20200608</td>
      <td>4 min 59 s</td>
      <td>504213</td>
    </tr>
    <tr>
      <th>822</th>
      <td>the_science_of_smog_kim_preshoff</td>
      <td>8.11M</td>
      <td>9.04G</td>
      <td>699K</td>
      <td>140K</td>
      <td>20170831</td>
      <td>5 min 43 s</td>
      <td>198053</td>
    </tr>
    <tr>
      <th>823</th>
      <td>caffeine</td>
      <td>12.8M</td>
      <td>9.05G</td>
      <td>1.36M</td>
      <td>139K</td>
      <td>20120327</td>
      <td>4 min 30 s</td>
      <td>396289</td>
    </tr>
    <tr>
      <th>824</th>
      <td>what_does_it_mean_to_be_a_refugee_benedetta_be...</td>
      <td>8.78M</td>
      <td>9.06G</td>
      <td>831K</td>
      <td>139K</td>
      <td>20160616</td>
      <td>5 min 42 s</td>
      <td>215014</td>
    </tr>
    <tr>
      <th>825</th>
      <td>the_coin_flip_conundrum_po_shen_loh</td>
      <td>7.01M</td>
      <td>9.07G</td>
      <td>554K</td>
      <td>139K</td>
      <td>20180215</td>
      <td>4 min 22 s</td>
      <td>224487</td>
    </tr>
    <tr>
      <th>826</th>
      <td>what_is_hpv_and_how_can_you_protect_yourself_f...</td>
      <td>5.88M</td>
      <td>9.07G</td>
      <td>415K</td>
      <td>138K</td>
      <td>20190709</td>
      <td>4 min 27 s</td>
      <td>183994</td>
    </tr>
    <tr>
      <th>827</th>
      <td>one_is_one_or_is_it</td>
      <td>5.82M</td>
      <td>9.08G</td>
      <td>1.35M</td>
      <td>138K</td>
      <td>20120521</td>
      <td>3 min 54 s</td>
      <td>208221</td>
    </tr>
    <tr>
      <th>828</th>
      <td>how_mucus_keeps_us_healthy_katharina_ribbeck</td>
      <td>7.94M</td>
      <td>9.08G</td>
      <td>823K</td>
      <td>137K</td>
      <td>20151105</td>
      <td>4 min 7 s</td>
      <td>268450</td>
    </tr>
    <tr>
      <th>829</th>
      <td>the_science_of_stage_fright_and_how_to_overcom...</td>
      <td>11.4M</td>
      <td>9.10G</td>
      <td>1.07M</td>
      <td>137K</td>
      <td>20131008</td>
      <td>4 min 7 s</td>
      <td>386020</td>
    </tr>
    <tr>
      <th>830</th>
      <td>there_may_be_extraterrestrial_life_in_our_sola...</td>
      <td>12.8M</td>
      <td>9.11G</td>
      <td>411K</td>
      <td>137K</td>
      <td>20190620</td>
      <td>5 min 16 s</td>
      <td>339177</td>
    </tr>
    <tr>
      <th>831</th>
      <td>ted_ed_youtube_channel_teaser</td>
      <td>4.46M</td>
      <td>9.11G</td>
      <td>1.20M</td>
      <td>137K</td>
      <td>20130402</td>
      <td>1 min 26 s</td>
      <td>434655</td>
    </tr>
    <tr>
      <th>832</th>
      <td>working_backward_to_solve_problems_maurice_ashley</td>
      <td>13.9M</td>
      <td>9.13G</td>
      <td>1.20M</td>
      <td>136K</td>
      <td>20130311</td>
      <td>5 min 56 s</td>
      <td>326695</td>
    </tr>
    <tr>
      <th>833</th>
      <td>the_sexual_deception_of_orchids_anne_gaskett</td>
      <td>11.7M</td>
      <td>9.14G</td>
      <td>408K</td>
      <td>136K</td>
      <td>20190214</td>
      <td>5 min 24 s</td>
      <td>301694</td>
    </tr>
    <tr>
      <th>834</th>
      <td>the_artists_think_like_a_coder_ep_5</td>
      <td>14.2M</td>
      <td>9.15G</td>
      <td>269K</td>
      <td>134K</td>
      <td>20200113</td>
      <td>6 min 41 s</td>
      <td>295727</td>
    </tr>
    <tr>
      <th>835</th>
      <td>who_built_great_zimbabwe_and_why_breeanna_elliott</td>
      <td>8.88M</td>
      <td>9.16G</td>
      <td>671K</td>
      <td>134K</td>
      <td>20170622</td>
      <td>5 min 6 s</td>
      <td>242656</td>
    </tr>
    <tr>
      <th>836</th>
      <td>the_gauntlet_think_like_a_coder_ep_8</td>
      <td>20.3M</td>
      <td>9.18G</td>
      <td>268K</td>
      <td>134K</td>
      <td>20200416</td>
      <td>8 min 16 s</td>
      <td>343069</td>
    </tr>
    <tr>
      <th>837</th>
      <td>an_anti_hero_of_one_s_own_tim_adams</td>
      <td>9.86M</td>
      <td>9.19G</td>
      <td>1.18M</td>
      <td>134K</td>
      <td>20121113</td>
      <td>4 min 10 s</td>
      <td>329992</td>
    </tr>
    <tr>
      <th>838</th>
      <td>who_won_the_space_race_jeff_steers</td>
      <td>9.93M</td>
      <td>9.20G</td>
      <td>1.17M</td>
      <td>134K</td>
      <td>20130814</td>
      <td>4 min 46 s</td>
      <td>290354</td>
    </tr>
    <tr>
      <th>839</th>
      <td>the_origins_of_ballet_jennifer_tortorello_and_...</td>
      <td>8.08M</td>
      <td>9.21G</td>
      <td>801K</td>
      <td>134K</td>
      <td>20160307</td>
      <td>4 min 37 s</td>
      <td>244575</td>
    </tr>
    <tr>
      <th>840</th>
      <td>why_should_you_read_shakespeares_the_tempest_i...</td>
      <td>12.0M</td>
      <td>9.22G</td>
      <td>399K</td>
      <td>133K</td>
      <td>20190205</td>
      <td>4 min 57 s</td>
      <td>337818</td>
    </tr>
    <tr>
      <th>841</th>
      <td>how_to_grow_a_bone_nina_tandon</td>
      <td>7.72M</td>
      <td>9.23G</td>
      <td>918K</td>
      <td>131K</td>
      <td>20150625</td>
      <td>4 min 36 s</td>
      <td>234387</td>
    </tr>
    <tr>
      <th>842</th>
      <td>the_past_present_and_future_of_the_bubonic_pla...</td>
      <td>6.58M</td>
      <td>9.23G</td>
      <td>1.02M</td>
      <td>131K</td>
      <td>20140818</td>
      <td>4 min 12 s</td>
      <td>218572</td>
    </tr>
    <tr>
      <th>843</th>
      <td>how_to_spot_a_counterfeit_bill_tien_nguyen</td>
      <td>8.01M</td>
      <td>9.24G</td>
      <td>913K</td>
      <td>130K</td>
      <td>20150416</td>
      <td>4 min 5 s</td>
      <td>274381</td>
    </tr>
    <tr>
      <th>844</th>
      <td>how_to_set_the_table_anna_post</td>
      <td>4.52M</td>
      <td>9.25G</td>
      <td>1.14M</td>
      <td>130K</td>
      <td>20130626</td>
      <td>3 min 26 s</td>
      <td>183704</td>
    </tr>
    <tr>
      <th>845</th>
      <td>how_do_scars_form_sarthak_sinha</td>
      <td>6.02M</td>
      <td>9.25G</td>
      <td>910K</td>
      <td>130K</td>
      <td>20141111</td>
      <td>3 min 41 s</td>
      <td>227887</td>
    </tr>
    <tr>
      <th>846</th>
      <td>who_decides_what_art_means_hayley_levitt</td>
      <td>6.96M</td>
      <td>9.26G</td>
      <td>389K</td>
      <td>130K</td>
      <td>20181126</td>
      <td>4 min 18 s</td>
      <td>225799</td>
    </tr>
    <tr>
      <th>847</th>
      <td>the_mathematics_of_sidewalk_illusions_fumiko_f...</td>
      <td>13.4M</td>
      <td>9.27G</td>
      <td>648K</td>
      <td>130K</td>
      <td>20170123</td>
      <td>4 min 54 s</td>
      <td>382575</td>
    </tr>
    <tr>
      <th>848</th>
      <td>how_optical_illusions_trick_your_brain_nathan_...</td>
      <td>13.3M</td>
      <td>9.28G</td>
      <td>1.01M</td>
      <td>129K</td>
      <td>20140812</td>
      <td>5 min 18 s</td>
      <td>349392</td>
    </tr>
    <tr>
      <th>849</th>
      <td>whats_the_point_e_of_ballet_ming_luke</td>
      <td>13.0M</td>
      <td>9.30G</td>
      <td>258K</td>
      <td>129K</td>
      <td>20200420</td>
      <td>5 min 9 s</td>
      <td>352955</td>
    </tr>
    <tr>
      <th>850</th>
      <td>real_life_sunken_cities_peter_campbell</td>
      <td>10.0M</td>
      <td>9.31G</td>
      <td>774K</td>
      <td>129K</td>
      <td>20160804</td>
      <td>4 min 30 s</td>
      <td>310046</td>
    </tr>
    <tr>
      <th>851</th>
      <td>what_is_alzheimer_s_disease_ivan_seah_yu_jun</td>
      <td>8.69M</td>
      <td>9.31G</td>
      <td>1.01M</td>
      <td>129K</td>
      <td>20140403</td>
      <td>3 min 49 s</td>
      <td>317797</td>
    </tr>
    <tr>
      <th>852</th>
      <td>the_science_of_hearing_douglas_l_oliver</td>
      <td>8.76M</td>
      <td>9.32G</td>
      <td>514K</td>
      <td>129K</td>
      <td>20180619</td>
      <td>5 min 16 s</td>
      <td>232092</td>
    </tr>
    <tr>
      <th>853</th>
      <td>the_lovable_and_lethal_sea_lion_claire_simeone</td>
      <td>8.83M</td>
      <td>9.33G</td>
      <td>385K</td>
      <td>128K</td>
      <td>20190528</td>
      <td>4 min 36 s</td>
      <td>268120</td>
    </tr>
    <tr>
      <th>854</th>
      <td>a_brief_history_of_numerical_systems_alessandr...</td>
      <td>6.81M</td>
      <td>9.34G</td>
      <td>640K</td>
      <td>128K</td>
      <td>20170119</td>
      <td>5 min 7 s</td>
      <td>185938</td>
    </tr>
    <tr>
      <th>855</th>
      <td>in_on_a_secret_that_s_dramatic_irony_christoph...</td>
      <td>4.57M</td>
      <td>9.34G</td>
      <td>1.12M</td>
      <td>127K</td>
      <td>20130129</td>
      <td>2 min 49 s</td>
      <td>225952</td>
    </tr>
    <tr>
      <th>856</th>
      <td>what_is_obesity_mia_nacamulli</td>
      <td>8.40M</td>
      <td>9.35G</td>
      <td>764K</td>
      <td>127K</td>
      <td>20160630</td>
      <td>5 min 10 s</td>
      <td>226890</td>
    </tr>
    <tr>
      <th>857</th>
      <td>why_should_you_read_toni_morrisons_beloved_yen...</td>
      <td>20.9M</td>
      <td>9.37G</td>
      <td>127K</td>
      <td>127K</td>
      <td>20210105</td>
      <td>5 min 6 s</td>
      <td>572912</td>
    </tr>
    <tr>
      <th>858</th>
      <td>what_in_the_world_is_topological_quantum_matte...</td>
      <td>7.40M</td>
      <td>9.38G</td>
      <td>507K</td>
      <td>127K</td>
      <td>20171023</td>
      <td>5 min 2 s</td>
      <td>205363</td>
    </tr>
    <tr>
      <th>859</th>
      <td>hacking_bacteria_to_fight_cancer_tal_danino</td>
      <td>11.5M</td>
      <td>9.39G</td>
      <td>250K</td>
      <td>125K</td>
      <td>20191210</td>
      <td>5 min 10 s</td>
      <td>309540</td>
    </tr>
    <tr>
      <th>860</th>
      <td>the_life_legacy_assassination_of_an_african_re...</td>
      <td>18.6M</td>
      <td>9.41G</td>
      <td>248K</td>
      <td>124K</td>
      <td>20200203</td>
      <td>5 min 31 s</td>
      <td>471040</td>
    </tr>
    <tr>
      <th>861</th>
      <td>inside_okcupid_the_math_of_online_dating_chris...</td>
      <td>16.5M</td>
      <td>9.42G</td>
      <td>1.09M</td>
      <td>124K</td>
      <td>20130213</td>
      <td>7 min 30 s</td>
      <td>307938</td>
    </tr>
    <tr>
      <th>862</th>
      <td>what_happened_to_trial_by_jury_suja_a_thomas</td>
      <td>7.02M</td>
      <td>9.43G</td>
      <td>616K</td>
      <td>123K</td>
      <td>20170302</td>
      <td>4 min 11 s</td>
      <td>234359</td>
    </tr>
    <tr>
      <th>863</th>
      <td>can_steroids_save_your_life_anees_bahji</td>
      <td>18.8M</td>
      <td>9.45G</td>
      <td>246K</td>
      <td>123K</td>
      <td>20200617</td>
      <td>5 min 31 s</td>
      <td>475344</td>
    </tr>
    <tr>
      <th>864</th>
      <td>rosalind_franklin_dna_s_unsung_hero_claudio_l_...</td>
      <td>7.82M</td>
      <td>9.46G</td>
      <td>737K</td>
      <td>123K</td>
      <td>20160711</td>
      <td>4 min 9 s</td>
      <td>262854</td>
    </tr>
    <tr>
      <th>865</th>
      <td>why_don_t_oil_and_water_mix_john_pollard</td>
      <td>14.7M</td>
      <td>9.47G</td>
      <td>981K</td>
      <td>123K</td>
      <td>20131010</td>
      <td>5 min 2 s</td>
      <td>407202</td>
    </tr>
    <tr>
      <th>866</th>
      <td>what_are_mini_brains_madeline_lancaster</td>
      <td>6.85M</td>
      <td>9.48G</td>
      <td>488K</td>
      <td>122K</td>
      <td>20180116</td>
      <td>4 min 44 s</td>
      <td>201828</td>
    </tr>
    <tr>
      <th>867</th>
      <td>is_there_a_limit_to_technological_progress_cle...</td>
      <td>8.32M</td>
      <td>9.49G</td>
      <td>608K</td>
      <td>122K</td>
      <td>20161219</td>
      <td>4 min 46 s</td>
      <td>243367</td>
    </tr>
    <tr>
      <th>868</th>
      <td>nasas_first_software_engineer_margaret_hamilto...</td>
      <td>10.1M</td>
      <td>9.50G</td>
      <td>243K</td>
      <td>121K</td>
      <td>20200305</td>
      <td>5 min 9 s</td>
      <td>273518</td>
    </tr>
    <tr>
      <th>869</th>
      <td>on_reading_the_koran_lesley_hazleton</td>
      <td>13.7M</td>
      <td>9.51G</td>
      <td>1.07M</td>
      <td>121K</td>
      <td>20130825</td>
      <td>9 min 33 s</td>
      <td>199560</td>
    </tr>
    <tr>
      <th>870</th>
      <td>the_neuroscience_of_imagination_andrey_vyshedskiy</td>
      <td>17.5M</td>
      <td>9.53G</td>
      <td>606K</td>
      <td>121K</td>
      <td>20161212</td>
      <td>4 min 48 s</td>
      <td>509488</td>
    </tr>
    <tr>
      <th>871</th>
      <td>how_do_we_know_what_color_dinosaurs_were_len_b...</td>
      <td>7.76M</td>
      <td>9.53G</td>
      <td>727K</td>
      <td>121K</td>
      <td>20160104</td>
      <td>4 min 23 s</td>
      <td>247276</td>
    </tr>
    <tr>
      <th>872</th>
      <td>are_naked_mole_rats_the_strangest_mammals_thom...</td>
      <td>9.09M</td>
      <td>9.54G</td>
      <td>484K</td>
      <td>121K</td>
      <td>20180529</td>
      <td>4 min 46 s</td>
      <td>266393</td>
    </tr>
    <tr>
      <th>873</th>
      <td>what_are_stem_cells_craig_a_kohn</td>
      <td>6.30M</td>
      <td>9.55G</td>
      <td>1.06M</td>
      <td>121K</td>
      <td>20130910</td>
      <td>4 min 10 s</td>
      <td>210664</td>
    </tr>
    <tr>
      <th>874</th>
      <td>is_light_a_particle_or_a_wave_colm_kelleher</td>
      <td>10.4M</td>
      <td>9.56G</td>
      <td>1.06M</td>
      <td>120K</td>
      <td>20130117</td>
      <td>4 min 23 s</td>
      <td>331736</td>
    </tr>
    <tr>
      <th>875</th>
      <td>the_infinite_life_of_pi_reynaldo_lopes</td>
      <td>6.66M</td>
      <td>9.57G</td>
      <td>1.06M</td>
      <td>120K</td>
      <td>20130710</td>
      <td>3 min 44 s</td>
      <td>249057</td>
    </tr>
    <tr>
      <th>876</th>
      <td>how_does_the_thyroid_manage_your_metabolism_em...</td>
      <td>7.16M</td>
      <td>9.57G</td>
      <td>836K</td>
      <td>119K</td>
      <td>20150302</td>
      <td>3 min 36 s</td>
      <td>277373</td>
    </tr>
    <tr>
      <th>877</th>
      <td>how_transistors_work_gokul_j_krishnan</td>
      <td>6.48M</td>
      <td>9.58G</td>
      <td>711K</td>
      <td>119K</td>
      <td>20160606</td>
      <td>4 min 53 s</td>
      <td>185562</td>
    </tr>
    <tr>
      <th>878</th>
      <td>could_human_civilization_spread_across_the_who...</td>
      <td>8.02M</td>
      <td>9.59G</td>
      <td>591K</td>
      <td>118K</td>
      <td>20160929</td>
      <td>4 min 33 s</td>
      <td>246195</td>
    </tr>
    <tr>
      <th>879</th>
      <td>the_art_of_the_metaphor_jane_hirshfield</td>
      <td>9.29M</td>
      <td>9.60G</td>
      <td>1.04M</td>
      <td>118K</td>
      <td>20120924</td>
      <td>5 min 38 s</td>
      <td>230204</td>
    </tr>
    <tr>
      <th>880</th>
      <td>sugar_hiding_in_plain_sight_robert_lustig</td>
      <td>9.30M</td>
      <td>9.61G</td>
      <td>943K</td>
      <td>118K</td>
      <td>20140331</td>
      <td>4 min 3 s</td>
      <td>320149</td>
    </tr>
    <tr>
      <th>881</th>
      <td>the_factory_think_like_a_coder_ep_9</td>
      <td>41.0M</td>
      <td>9.65G</td>
      <td>235K</td>
      <td>118K</td>
      <td>20200623</td>
      <td>10 min 0 s</td>
      <td>572919</td>
    </tr>
    <tr>
      <th>882</th>
      <td>the_simple_story_of_photosynthesis_and_food_am...</td>
      <td>8.50M</td>
      <td>9.65G</td>
      <td>1.03M</td>
      <td>117K</td>
      <td>20130305</td>
      <td>4 min 0 s</td>
      <td>296124</td>
    </tr>
    <tr>
      <th>883</th>
      <td>try_something_new_for_30_days_matt_cutts</td>
      <td>5.88M</td>
      <td>9.66G</td>
      <td>1.02M</td>
      <td>116K</td>
      <td>20130405</td>
      <td>3 min 27 s</td>
      <td>237907</td>
    </tr>
    <tr>
      <th>884</th>
      <td>particles_and_waves_the_central_mystery_of_qua...</td>
      <td>7.11M</td>
      <td>9.67G</td>
      <td>813K</td>
      <td>116K</td>
      <td>20140915</td>
      <td>4 min 51 s</td>
      <td>204493</td>
    </tr>
    <tr>
      <th>885</th>
      <td>how_did_english_evolve_kate_gardoqui</td>
      <td>15.5M</td>
      <td>9.68G</td>
      <td>1.02M</td>
      <td>116K</td>
      <td>20121127</td>
      <td>5 min 4 s</td>
      <td>427739</td>
    </tr>
    <tr>
      <th>886</th>
      <td>how_did_clouds_get_their_names_richard_hamblyn</td>
      <td>9.26M</td>
      <td>9.69G</td>
      <td>691K</td>
      <td>115K</td>
      <td>20151124</td>
      <td>5 min 6 s</td>
      <td>253330</td>
    </tr>
    <tr>
      <th>887</th>
      <td>biodiesel_the_afterlife_of_oil_natascia_radice</td>
      <td>7.48M</td>
      <td>9.70G</td>
      <td>920K</td>
      <td>115K</td>
      <td>20140123</td>
      <td>4 min 14 s</td>
      <td>246695</td>
    </tr>
    <tr>
      <th>888</th>
      <td>the_city_of_walls_constantinople_lars_brownworth</td>
      <td>6.94M</td>
      <td>9.70G</td>
      <td>1.01M</td>
      <td>115K</td>
      <td>20121018</td>
      <td>4 min 16 s</td>
      <td>226928</td>
    </tr>
    <tr>
      <th>889</th>
      <td>music_as_a_language_victor_wooten</td>
      <td>15.5M</td>
      <td>9.72G</td>
      <td>1.11M</td>
      <td>113K</td>
      <td>20120813</td>
      <td>4 min 59 s</td>
      <td>432814</td>
    </tr>
    <tr>
      <th>890</th>
      <td>the_upside_of_isolated_civilizations_jason_shi...</td>
      <td>8.37M</td>
      <td>9.73G</td>
      <td>1.00M</td>
      <td>113K</td>
      <td>20130328</td>
      <td>4 min 7 s</td>
      <td>283792</td>
    </tr>
    <tr>
      <th>891</th>
      <td>how_to_grow_a_glacier_m_jackson</td>
      <td>8.76M</td>
      <td>9.74G</td>
      <td>340K</td>
      <td>113K</td>
      <td>20190404</td>
      <td>5 min 19 s</td>
      <td>229836</td>
    </tr>
    <tr>
      <th>892</th>
      <td>why_we_love_repetition_in_music_elizabeth_hell...</td>
      <td>8.06M</td>
      <td>9.74G</td>
      <td>903K</td>
      <td>113K</td>
      <td>20140902</td>
      <td>4 min 31 s</td>
      <td>248926</td>
    </tr>
    <tr>
      <th>893</th>
      <td>does_stress_cause_pimples_claudia_aguirre</td>
      <td>6.20M</td>
      <td>9.75G</td>
      <td>0.99M</td>
      <td>113K</td>
      <td>20121115</td>
      <td>3 min 54 s</td>
      <td>221838</td>
    </tr>
    <tr>
      <th>894</th>
      <td>how_do_us_supreme_court_justices_get_appointed...</td>
      <td>8.46M</td>
      <td>9.76G</td>
      <td>562K</td>
      <td>112K</td>
      <td>20161117</td>
      <td>4 min 25 s</td>
      <td>267021</td>
    </tr>
    <tr>
      <th>895</th>
      <td>why_are_fish_fish_shaped_lauren_sallan</td>
      <td>11.9M</td>
      <td>9.77G</td>
      <td>449K</td>
      <td>112K</td>
      <td>20180417</td>
      <td>4 min 56 s</td>
      <td>336209</td>
    </tr>
    <tr>
      <th>896</th>
      <td>did_shakespeare_write_his_plays_natalya_st_cla...</td>
      <td>6.64M</td>
      <td>9.78G</td>
      <td>784K</td>
      <td>112K</td>
      <td>20150224</td>
      <td>4 min 6 s</td>
      <td>226224</td>
    </tr>
    <tr>
      <th>897</th>
      <td>how_one_scientist_took_on_the_chemical_industr...</td>
      <td>12.0M</td>
      <td>9.79G</td>
      <td>224K</td>
      <td>112K</td>
      <td>20200317</td>
      <td>5 min 22 s</td>
      <td>311392</td>
    </tr>
    <tr>
      <th>898</th>
      <td>how_do_birds_learn_to_sing_partha_p_mitra</td>
      <td>11.3M</td>
      <td>9.80G</td>
      <td>448K</td>
      <td>112K</td>
      <td>20180220</td>
      <td>5 min 38 s</td>
      <td>281542</td>
    </tr>
    <tr>
      <th>899</th>
      <td>how_to_sequence_the_human_genome_mark_j_kiel</td>
      <td>12.7M</td>
      <td>9.81G</td>
      <td>885K</td>
      <td>111K</td>
      <td>20131209</td>
      <td>5 min 4 s</td>
      <td>349410</td>
    </tr>
    <tr>
      <th>900</th>
      <td>how_to_3d_print_human_tissue_taneka_jones</td>
      <td>7.60M</td>
      <td>9.82G</td>
      <td>221K</td>
      <td>110K</td>
      <td>20191017</td>
      <td>5 min 11 s</td>
      <td>204783</td>
    </tr>
    <tr>
      <th>901</th>
      <td>the_mighty_mathematics_of_the_lever_andy_peter...</td>
      <td>7.27M</td>
      <td>9.83G</td>
      <td>772K</td>
      <td>110K</td>
      <td>20141118</td>
      <td>4 min 45 s</td>
      <td>213970</td>
    </tr>
    <tr>
      <th>902</th>
      <td>the_electrifying_speeches_of_sojourner_truth_d...</td>
      <td>9.68M</td>
      <td>9.84G</td>
      <td>220K</td>
      <td>110K</td>
      <td>20200428</td>
      <td>4 min 39 s</td>
      <td>290846</td>
    </tr>
    <tr>
      <th>903</th>
      <td>surviving_a_nuclear_attack_irwin_redlener</td>
      <td>44.7M</td>
      <td>9.88G</td>
      <td>990K</td>
      <td>110K</td>
      <td>20130125</td>
      <td>25 min 21 s</td>
      <td>246392</td>
    </tr>
    <tr>
      <th>904</th>
      <td>calculating_the_odds_of_intelligent_alien_life...</td>
      <td>20.3M</td>
      <td>9.90G</td>
      <td>1.07M</td>
      <td>110K</td>
      <td>20120702</td>
      <td>7 min 27 s</td>
      <td>381128</td>
    </tr>
    <tr>
      <th>905</th>
      <td>explore_cave_paintings_in_this_360deg_animated...</td>
      <td>4.55M</td>
      <td>9.90G</td>
      <td>438K</td>
      <td>109K</td>
      <td>20171012</td>
      <td>3 min 0 s</td>
      <td>211761</td>
    </tr>
    <tr>
      <th>906</th>
      <td>how_the_bra_was_invented_moments_of_vision_1_j...</td>
      <td>3.36M</td>
      <td>9.91G</td>
      <td>654K</td>
      <td>109K</td>
      <td>20160712</td>
      <td>1 min 42 s</td>
      <td>275304</td>
    </tr>
    <tr>
      <th>907</th>
      <td>what_creates_a_total_solar_eclipse_andy_cohen</td>
      <td>5.99M</td>
      <td>9.91G</td>
      <td>979K</td>
      <td>109K</td>
      <td>20130722</td>
      <td>3 min 45 s</td>
      <td>222513</td>
    </tr>
    <tr>
      <th>908</th>
      <td>can_you_spot_the_problem_with_these_headlines_...</td>
      <td>9.34M</td>
      <td>9.92G</td>
      <td>326K</td>
      <td>109K</td>
      <td>20190521</td>
      <td>5 min 0 s</td>
      <td>260552</td>
    </tr>
    <tr>
      <th>909</th>
      <td>deep_ocean_mysteries_and_wonders_david_gallo</td>
      <td>22.5M</td>
      <td>9.94G</td>
      <td>1.05M</td>
      <td>108K</td>
      <td>20120312</td>
      <td>8 min 27 s</td>
      <td>372262</td>
    </tr>
    <tr>
      <th>910</th>
      <td>how_taking_a_bath_led_to_archimedes_principle_...</td>
      <td>8.23M</td>
      <td>9.95G</td>
      <td>1.05M</td>
      <td>107K</td>
      <td>20120906</td>
      <td>3 min 0 s</td>
      <td>382338</td>
    </tr>
    <tr>
      <th>911</th>
      <td>why_do_we_pass_gas_purna_kashyap</td>
      <td>13.2M</td>
      <td>9.97G</td>
      <td>854K</td>
      <td>107K</td>
      <td>20140908</td>
      <td>4 min 57 s</td>
      <td>372733</td>
    </tr>
    <tr>
      <th>912</th>
      <td>the_high_stakes_race_to_make_quantum_computers...</td>
      <td>9.41M</td>
      <td>9.97G</td>
      <td>320K</td>
      <td>107K</td>
      <td>20190813</td>
      <td>5 min 15 s</td>
      <td>249913</td>
    </tr>
    <tr>
      <th>913</th>
      <td>how_heavy_is_air_dan_quinn</td>
      <td>9.90M</td>
      <td>9.98G</td>
      <td>852K</td>
      <td>106K</td>
      <td>20140707</td>
      <td>3 min 18 s</td>
      <td>417908</td>
    </tr>
    <tr>
      <th>914</th>
      <td>the_beauty_of_data_visualization_david_mccandless</td>
      <td>31.2M</td>
      <td>10.0G</td>
      <td>956K</td>
      <td>106K</td>
      <td>20121123</td>
      <td>18 min 17 s</td>
      <td>238737</td>
    </tr>
    <tr>
      <th>915</th>
      <td>how_do_focus_groups_work_hector_lanz</td>
      <td>9.05M</td>
      <td>10.0G</td>
      <td>530K</td>
      <td>106K</td>
      <td>20170410</td>
      <td>4 min 46 s</td>
      <td>265383</td>
    </tr>
    <tr>
      <th>916</th>
      <td>beware_of_nominalizations_aka_zombie_nouns_hel...</td>
      <td>11.3M</td>
      <td>10.0G</td>
      <td>951K</td>
      <td>106K</td>
      <td>20121031</td>
      <td>5 min 4 s</td>
      <td>312508</td>
    </tr>
    <tr>
      <th>917</th>
      <td>how_to_spot_a_fad_diet_mia_nacamulli</td>
      <td>7.10M</td>
      <td>10.0G</td>
      <td>632K</td>
      <td>105K</td>
      <td>20160411</td>
      <td>4 min 33 s</td>
      <td>217488</td>
    </tr>
    <tr>
      <th>918</th>
      <td>what_makes_neon_signs_glow_a_360deg_animation_...</td>
      <td>9.23M</td>
      <td>10.1G</td>
      <td>211K</td>
      <td>105K</td>
      <td>20190919</td>
      <td>4 min 51 s</td>
      <td>266068</td>
    </tr>
    <tr>
      <th>919</th>
      <td>the_beginning_of_the_universe_for_beginners_to...</td>
      <td>5.87M</td>
      <td>10.1G</td>
      <td>944K</td>
      <td>105K</td>
      <td>20130409</td>
      <td>3 min 41 s</td>
      <td>222555</td>
    </tr>
    <tr>
      <th>920</th>
      <td>the_end_of_history_illusion_bence_nanay</td>
      <td>5.94M</td>
      <td>10.1G</td>
      <td>314K</td>
      <td>105K</td>
      <td>20180927</td>
      <td>4 min 22 s</td>
      <td>189697</td>
    </tr>
    <tr>
      <th>921</th>
      <td>how_does_your_smartphone_know_your_location_wi...</td>
      <td>9.32M</td>
      <td>10.1G</td>
      <td>730K</td>
      <td>104K</td>
      <td>20150129</td>
      <td>5 min 2 s</td>
      <td>258126</td>
    </tr>
    <tr>
      <th>922</th>
      <td>newton_s_3_laws_with_a_bicycle_joshua_manley</td>
      <td>10.6M</td>
      <td>10.1G</td>
      <td>937K</td>
      <td>104K</td>
      <td>20120919</td>
      <td>3 min 32 s</td>
      <td>417159</td>
    </tr>
    <tr>
      <th>923</th>
      <td>what_is_the_biggest_single_celled_organism_mur...</td>
      <td>6.89M</td>
      <td>10.1G</td>
      <td>624K</td>
      <td>104K</td>
      <td>20160818</td>
      <td>4 min 6 s</td>
      <td>234829</td>
    </tr>
    <tr>
      <th>924</th>
      <td>five_fingers_of_evolution_paul_andersen</td>
      <td>10.5M</td>
      <td>10.1G</td>
      <td>1.01M</td>
      <td>104K</td>
      <td>20120507</td>
      <td>5 min 23 s</td>
      <td>272225</td>
    </tr>
    <tr>
      <th>925</th>
      <td>can_wildlife_adapt_to_climate_change_erin_east...</td>
      <td>10.7M</td>
      <td>10.1G</td>
      <td>619K</td>
      <td>103K</td>
      <td>20160303</td>
      <td>4 min 46 s</td>
      <td>312290</td>
    </tr>
    <tr>
      <th>926</th>
      <td>how_art_can_help_you_analyze_amy_e_herman</td>
      <td>7.45M</td>
      <td>10.1G</td>
      <td>815K</td>
      <td>102K</td>
      <td>20131004</td>
      <td>4 min 49 s</td>
      <td>215847</td>
    </tr>
    <tr>
      <th>927</th>
      <td>can_you_find_the_next_number_in_this_sequence_...</td>
      <td>6.83M</td>
      <td>10.1G</td>
      <td>506K</td>
      <td>101K</td>
      <td>20170720</td>
      <td>4 min 0 s</td>
      <td>238106</td>
    </tr>
    <tr>
      <th>928</th>
      <td>how_to_squeeze_electricity_out_of_crystals_ash...</td>
      <td>13.1M</td>
      <td>10.1G</td>
      <td>505K</td>
      <td>101K</td>
      <td>20170620</td>
      <td>4 min 55 s</td>
      <td>370510</td>
    </tr>
    <tr>
      <th>929</th>
      <td>how_do_self_driving_cars_see_sajan_saini</td>
      <td>9.03M</td>
      <td>10.1G</td>
      <td>303K</td>
      <td>101K</td>
      <td>20190513</td>
      <td>5 min 24 s</td>
      <td>233635</td>
    </tr>
    <tr>
      <th>930</th>
      <td>why_is_the_us_constitution_so_hard_to_amend_pe...</td>
      <td>8.32M</td>
      <td>10.2G</td>
      <td>601K</td>
      <td>100K</td>
      <td>20160516</td>
      <td>4 min 17 s</td>
      <td>271328</td>
    </tr>
    <tr>
      <th>931</th>
      <td>a_reality_check_on_renewables_david_mackay</td>
      <td>33.4M</td>
      <td>10.2G</td>
      <td>901K</td>
      <td>100K</td>
      <td>20130626</td>
      <td>18 min 34 s</td>
      <td>251449</td>
    </tr>
    <tr>
      <th>932</th>
      <td>why_should_you_read_midnights_children_iseult_...</td>
      <td>19.5M</td>
      <td>10.2G</td>
      <td>300K</td>
      <td>99.9K</td>
      <td>20190910</td>
      <td>5 min 55 s</td>
      <td>460134</td>
    </tr>
    <tr>
      <th>933</th>
      <td>a_brief_history_of_video_games_part_i_safwat_s...</td>
      <td>6.97M</td>
      <td>10.2G</td>
      <td>898K</td>
      <td>99.8K</td>
      <td>20130813</td>
      <td>4 min 45 s</td>
      <td>204542</td>
    </tr>
    <tr>
      <th>934</th>
      <td>eli_the_eel_a_mysterious_migration_james_prosek</td>
      <td>6.61M</td>
      <td>10.2G</td>
      <td>798K</td>
      <td>99.7K</td>
      <td>20140210</td>
      <td>4 min 38 s</td>
      <td>198824</td>
    </tr>
    <tr>
      <th>935</th>
      <td>why_sex</td>
      <td>12.5M</td>
      <td>10.2G</td>
      <td>997K</td>
      <td>99.7K</td>
      <td>20120501</td>
      <td>4 min 52 s</td>
      <td>356627</td>
    </tr>
    <tr>
      <th>936</th>
      <td>how_do_germs_spread_and_why_do_they_make_us_si...</td>
      <td>6.55M</td>
      <td>10.2G</td>
      <td>697K</td>
      <td>99.6K</td>
      <td>20141021</td>
      <td>5 min 6 s</td>
      <td>179273</td>
    </tr>
    <tr>
      <th>937</th>
      <td>cell_membranes_are_way_more_complicated_than_y...</td>
      <td>14.6M</td>
      <td>10.3G</td>
      <td>498K</td>
      <td>99.5K</td>
      <td>20170821</td>
      <td>5 min 20 s</td>
      <td>381433</td>
    </tr>
    <tr>
      <th>938</th>
      <td>the_exceptional_life_of_benjamin_banneker_rose...</td>
      <td>6.56M</td>
      <td>10.3G</td>
      <td>497K</td>
      <td>99.3K</td>
      <td>20170216</td>
      <td>3 min 36 s</td>
      <td>254282</td>
    </tr>
    <tr>
      <th>939</th>
      <td>what_did_democracy_really_mean_in_athens_melis...</td>
      <td>19.0M</td>
      <td>10.3G</td>
      <td>694K</td>
      <td>99.1K</td>
      <td>20150324</td>
      <td>4 min 51 s</td>
      <td>547410</td>
    </tr>
    <tr>
      <th>940</th>
      <td>how_exposing_anonymous_companies_could_cut_dow...</td>
      <td>10.1M</td>
      <td>10.3G</td>
      <td>592K</td>
      <td>98.6K</td>
      <td>20151201</td>
      <td>4 min 6 s</td>
      <td>342028</td>
    </tr>
    <tr>
      <th>941</th>
      <td>is_graffiti_art_or_vandalism_kelly_wall</td>
      <td>15.2M</td>
      <td>10.3G</td>
      <td>590K</td>
      <td>98.3K</td>
      <td>20160908</td>
      <td>4 min 31 s</td>
      <td>468771</td>
    </tr>
    <tr>
      <th>942</th>
      <td>how_to_fossilize_yourself_phoebe_a_cohen</td>
      <td>8.15M</td>
      <td>10.3G</td>
      <td>784K</td>
      <td>98.0K</td>
      <td>20140106</td>
      <td>5 min 13 s</td>
      <td>218149</td>
    </tr>
    <tr>
      <th>943</th>
      <td>the_physics_of_surfing_nick_pizzo</td>
      <td>11.1M</td>
      <td>10.3G</td>
      <td>293K</td>
      <td>97.7K</td>
      <td>20190311</td>
      <td>4 min 40 s</td>
      <td>332485</td>
    </tr>
    <tr>
      <th>944</th>
      <td>buffalo_buffalo_buffalo_one_word_sentences_and...</td>
      <td>5.00M</td>
      <td>10.3G</td>
      <td>681K</td>
      <td>97.3K</td>
      <td>20150817</td>
      <td>3 min 27 s</td>
      <td>202025</td>
    </tr>
    <tr>
      <th>945</th>
      <td>how_to_choose_your_news_damon_brown</td>
      <td>6.41M</td>
      <td>10.3G</td>
      <td>777K</td>
      <td>97.2K</td>
      <td>20140605</td>
      <td>4 min 48 s</td>
      <td>186729</td>
    </tr>
    <tr>
      <th>946</th>
      <td>how_we_see_color_colm_kelleher</td>
      <td>10.7M</td>
      <td>10.3G</td>
      <td>873K</td>
      <td>97.0K</td>
      <td>20130108</td>
      <td>3 min 43 s</td>
      <td>401484</td>
    </tr>
    <tr>
      <th>947</th>
      <td>when_to_use_apostrophes_laura_mcclure</td>
      <td>5.63M</td>
      <td>10.3G</td>
      <td>678K</td>
      <td>96.9K</td>
      <td>20150727</td>
      <td>3 min 13 s</td>
      <td>243497</td>
    </tr>
    <tr>
      <th>948</th>
      <td>would_you_live_on_the_moon_alex_gendler</td>
      <td>9.05M</td>
      <td>10.4G</td>
      <td>387K</td>
      <td>96.8K</td>
      <td>20180605</td>
      <td>4 min 51 s</td>
      <td>260904</td>
    </tr>
    <tr>
      <th>949</th>
      <td>the_incredible_collaboration_behind_the_intern...</td>
      <td>9.79M</td>
      <td>10.4G</td>
      <td>580K</td>
      <td>96.6K</td>
      <td>20150929</td>
      <td>4 min 57 s</td>
      <td>276361</td>
    </tr>
    <tr>
      <th>950</th>
      <td>what_is_the_world_wide_web_twila_camp</td>
      <td>6.02M</td>
      <td>10.4G</td>
      <td>771K</td>
      <td>96.4K</td>
      <td>20140512</td>
      <td>3 min 54 s</td>
      <td>215284</td>
    </tr>
    <tr>
      <th>951</th>
      <td>the_opposites_game</td>
      <td>13.1M</td>
      <td>10.4G</td>
      <td>288K</td>
      <td>96.0K</td>
      <td>20190603</td>
      <td>4 min 40 s</td>
      <td>390097</td>
    </tr>
    <tr>
      <th>952</th>
      <td>a_guide_to_the_energy_of_the_earth_joshua_m_sn...</td>
      <td>9.00M</td>
      <td>10.4G</td>
      <td>768K</td>
      <td>96.0K</td>
      <td>20140630</td>
      <td>4 min 43 s</td>
      <td>266239</td>
    </tr>
    <tr>
      <th>953</th>
      <td>why_the_insect_brain_is_so_incredible_anna_stockl</td>
      <td>12.0M</td>
      <td>10.4G</td>
      <td>576K</td>
      <td>95.9K</td>
      <td>20160414</td>
      <td>4 min 22 s</td>
      <td>383920</td>
    </tr>
    <tr>
      <th>954</th>
      <td>how_the_band_aid_was_invented_moments_of_visio...</td>
      <td>3.05M</td>
      <td>10.4G</td>
      <td>575K</td>
      <td>95.9K</td>
      <td>20160912</td>
      <td>1 min 44 s</td>
      <td>244281</td>
    </tr>
    <tr>
      <th>955</th>
      <td>climate_change_earth_s_giant_game_of_tetris_jo...</td>
      <td>4.57M</td>
      <td>10.4G</td>
      <td>765K</td>
      <td>95.6K</td>
      <td>20140422</td>
      <td>2 min 48 s</td>
      <td>227971</td>
    </tr>
    <tr>
      <th>956</th>
      <td>the_fundamentals_of_space_time_part_2_andrew_p...</td>
      <td>8.17M</td>
      <td>10.4G</td>
      <td>763K</td>
      <td>95.3K</td>
      <td>20140501</td>
      <td>4 min 49 s</td>
      <td>236248</td>
    </tr>
    <tr>
      <th>957</th>
      <td>how_do_we_separate_the_seemingly_inseparable_i...</td>
      <td>6.67M</td>
      <td>10.4G</td>
      <td>568K</td>
      <td>94.7K</td>
      <td>20160509</td>
      <td>4 min 23 s</td>
      <td>212098</td>
    </tr>
    <tr>
      <th>958</th>
      <td>how_to_master_your_sense_of_smell_alexandra_ho...</td>
      <td>9.71M</td>
      <td>10.4G</td>
      <td>473K</td>
      <td>94.7K</td>
      <td>20170109</td>
      <td>4 min 33 s</td>
      <td>297829</td>
    </tr>
    <tr>
      <th>959</th>
      <td>are_spotty_fruits_and_vegetables_safe_to_eat_e...</td>
      <td>7.13M</td>
      <td>10.4G</td>
      <td>565K</td>
      <td>94.1K</td>
      <td>20160822</td>
      <td>4 min 8 s</td>
      <td>240767</td>
    </tr>
    <tr>
      <th>960</th>
      <td>what_causes_economic_bubbles_prateek_singh</td>
      <td>9.45M</td>
      <td>10.5G</td>
      <td>657K</td>
      <td>93.8K</td>
      <td>20150504</td>
      <td>4 min 16 s</td>
      <td>308870</td>
    </tr>
    <tr>
      <th>961</th>
      <td>questions_no_one_knows_the_answers_to</td>
      <td>4.20M</td>
      <td>10.5G</td>
      <td>936K</td>
      <td>93.6K</td>
      <td>20120311</td>
      <td>2 min 10 s</td>
      <td>269290</td>
    </tr>
    <tr>
      <th>962</th>
      <td>all_the_world_s_a_stage_by_william_shakespeare</td>
      <td>5.65M</td>
      <td>10.5G</td>
      <td>279K</td>
      <td>93.1K</td>
      <td>20190202</td>
      <td>2 min 34 s</td>
      <td>306591</td>
    </tr>
    <tr>
      <th>963</th>
      <td>the_power_of_creative_constraints_brandon_rodr...</td>
      <td>7.08M</td>
      <td>10.5G</td>
      <td>463K</td>
      <td>92.6K</td>
      <td>20170613</td>
      <td>5 min 9 s</td>
      <td>191786</td>
    </tr>
    <tr>
      <th>964</th>
      <td>the_terrors_of_sleep_paralysis_ami_angelowicz</td>
      <td>10.7M</td>
      <td>10.5G</td>
      <td>827K</td>
      <td>91.9K</td>
      <td>20130725</td>
      <td>4 min 48 s</td>
      <td>309710</td>
    </tr>
    <tr>
      <th>965</th>
      <td>what_is_leukemia_danilo_allegra_and_dania_pugg...</td>
      <td>7.89M</td>
      <td>10.5G</td>
      <td>642K</td>
      <td>91.7K</td>
      <td>20150430</td>
      <td>4 min 32 s</td>
      <td>243226</td>
    </tr>
    <tr>
      <th>966</th>
      <td>kabuki_the_people_s_dramatic_art_amanda_mattes</td>
      <td>7.30M</td>
      <td>10.5G</td>
      <td>732K</td>
      <td>91.5K</td>
      <td>20130930</td>
      <td>4 min 15 s</td>
      <td>240204</td>
    </tr>
    <tr>
      <th>967</th>
      <td>what_does_the_pancreas_do_emma_bryce</td>
      <td>7.01M</td>
      <td>10.5G</td>
      <td>639K</td>
      <td>91.3K</td>
      <td>20150219</td>
      <td>3 min 20 s</td>
      <td>293328</td>
    </tr>
    <tr>
      <th>968</th>
      <td>the_story_behind_the_boston_tea_party_ben_labaree</td>
      <td>10.0M</td>
      <td>10.5G</td>
      <td>818K</td>
      <td>90.9K</td>
      <td>20130318</td>
      <td>3 min 47 s</td>
      <td>369164</td>
    </tr>
    <tr>
      <th>969</th>
      <td>how_do_you_know_whom_to_trust_ram_neta</td>
      <td>10.2M</td>
      <td>10.5G</td>
      <td>818K</td>
      <td>90.9K</td>
      <td>20130430</td>
      <td>4 min 34 s</td>
      <td>312370</td>
    </tr>
    <tr>
      <th>970</th>
      <td>first_kiss_by_tim_seibles</td>
      <td>5.95M</td>
      <td>10.5G</td>
      <td>270K</td>
      <td>90.2K</td>
      <td>20190401</td>
      <td>2 min 37 s</td>
      <td>317207</td>
    </tr>
    <tr>
      <th>971</th>
      <td>the_uncertain_location_of_electrons_george_zai...</td>
      <td>5.84M</td>
      <td>10.5G</td>
      <td>720K</td>
      <td>90.0K</td>
      <td>20131014</td>
      <td>3 min 46 s</td>
      <td>216082</td>
    </tr>
    <tr>
      <th>972</th>
      <td>romance_and_revolution_the_poetry_of_pablo_ner...</td>
      <td>15.3M</td>
      <td>10.5G</td>
      <td>269K</td>
      <td>89.7K</td>
      <td>20190723</td>
      <td>4 min 49 s</td>
      <td>442094</td>
    </tr>
    <tr>
      <th>973</th>
      <td>should_we_be_looking_for_life_elsewhere_in_the...</td>
      <td>8.84M</td>
      <td>10.6G</td>
      <td>537K</td>
      <td>89.5K</td>
      <td>20160725</td>
      <td>4 min 35 s</td>
      <td>269483</td>
    </tr>
    <tr>
      <th>974</th>
      <td>how_do_schools_of_fish_swim_in_harmony_nathan_...</td>
      <td>13.9M</td>
      <td>10.6G</td>
      <td>535K</td>
      <td>89.1K</td>
      <td>20160331</td>
      <td>6 min 6 s</td>
      <td>317546</td>
    </tr>
    <tr>
      <th>975</th>
      <td>solving_the_puzzle_of_the_periodic_table_eric_...</td>
      <td>9.56M</td>
      <td>10.6G</td>
      <td>797K</td>
      <td>88.6K</td>
      <td>20121212</td>
      <td>4 min 18 s</td>
      <td>310720</td>
    </tr>
    <tr>
      <th>976</th>
      <td>the_evolution_of_the_book_julie_dreyfuss</td>
      <td>12.1M</td>
      <td>10.6G</td>
      <td>530K</td>
      <td>88.3K</td>
      <td>20160613</td>
      <td>4 min 17 s</td>
      <td>395824</td>
    </tr>
    <tr>
      <th>977</th>
      <td>infinity_according_to_jorge_luis_borges_ilan_s...</td>
      <td>7.98M</td>
      <td>10.6G</td>
      <td>264K</td>
      <td>88.2K</td>
      <td>20190711</td>
      <td>4 min 42 s</td>
      <td>236712</td>
    </tr>
    <tr>
      <th>978</th>
      <td>where_do_genes_come_from_carl_zimmer</td>
      <td>8.08M</td>
      <td>10.6G</td>
      <td>614K</td>
      <td>87.7K</td>
      <td>20140922</td>
      <td>4 min 23 s</td>
      <td>257485</td>
    </tr>
    <tr>
      <th>979</th>
      <td>why_should_you_read_flannery_oconnor_iseult_gi...</td>
      <td>7.06M</td>
      <td>10.6G</td>
      <td>263K</td>
      <td>87.6K</td>
      <td>20190129</td>
      <td>4 min 11 s</td>
      <td>235426</td>
    </tr>
    <tr>
      <th>980</th>
      <td>why_are_blue_whales_so_enormous_asha_de_vos</td>
      <td>11.7M</td>
      <td>10.6G</td>
      <td>787K</td>
      <td>87.4K</td>
      <td>20130225</td>
      <td>5 min 20 s</td>
      <td>305900</td>
    </tr>
    <tr>
      <th>981</th>
      <td>how_north_america_got_its_shape_peter_j_haproff</td>
      <td>8.40M</td>
      <td>10.6G</td>
      <td>524K</td>
      <td>87.3K</td>
      <td>20160705</td>
      <td>4 min 57 s</td>
      <td>237192</td>
    </tr>
    <tr>
      <th>982</th>
      <td>the_pleasure_of_poetic_pattern_david_silverstein</td>
      <td>8.93M</td>
      <td>10.6G</td>
      <td>523K</td>
      <td>87.2K</td>
      <td>20160602</td>
      <td>4 min 46 s</td>
      <td>261231</td>
    </tr>
    <tr>
      <th>983</th>
      <td>the_higgs_field_explained_don_lincoln</td>
      <td>11.4M</td>
      <td>10.7G</td>
      <td>785K</td>
      <td>87.2K</td>
      <td>20130827</td>
      <td>3 min 18 s</td>
      <td>480930</td>
    </tr>
    <tr>
      <th>984</th>
      <td>diagnosing_a_zombie_brain_and_body_part_one_ti...</td>
      <td>6.56M</td>
      <td>10.7G</td>
      <td>783K</td>
      <td>87.0K</td>
      <td>20121022</td>
      <td>3 min 46 s</td>
      <td>243356</td>
    </tr>
    <tr>
      <th>985</th>
      <td>sunlight_is_way_older_than_you_think_sten_oden...</td>
      <td>7.77M</td>
      <td>10.7G</td>
      <td>609K</td>
      <td>87.0K</td>
      <td>20150512</td>
      <td>4 min 36 s</td>
      <td>235490</td>
    </tr>
    <tr>
      <th>986</th>
      <td>a_clever_way_to_estimate_enormous_numbers_mich...</td>
      <td>10.1M</td>
      <td>10.7G</td>
      <td>865K</td>
      <td>86.5K</td>
      <td>20120912</td>
      <td>4 min 14 s</td>
      <td>334110</td>
    </tr>
    <tr>
      <th>987</th>
      <td>got_seeds_just_add_bleach_acid_and_sandpaper_m...</td>
      <td>4.99M</td>
      <td>10.7G</td>
      <td>778K</td>
      <td>86.5K</td>
      <td>20130716</td>
      <td>3 min 35 s</td>
      <td>194739</td>
    </tr>
    <tr>
      <th>988</th>
      <td>the_last_chief_of_the_comanches_and_the_fall_o...</td>
      <td>22.7M</td>
      <td>10.7G</td>
      <td>173K</td>
      <td>86.4K</td>
      <td>20200702</td>
      <td>6 min 24 s</td>
      <td>494908</td>
    </tr>
    <tr>
      <th>989</th>
      <td>what_s_hidden_among_the_tallest_trees_on_earth...</td>
      <td>11.6M</td>
      <td>10.7G</td>
      <td>685K</td>
      <td>85.6K</td>
      <td>20140805</td>
      <td>4 min 46 s</td>
      <td>339053</td>
    </tr>
    <tr>
      <th>990</th>
      <td>how_braille_was_invented_moments_of_vision_9_j...</td>
      <td>2.98M</td>
      <td>10.7G</td>
      <td>428K</td>
      <td>85.6K</td>
      <td>20170307</td>
      <td>1 min 49 s</td>
      <td>228320</td>
    </tr>
    <tr>
      <th>991</th>
      <td>if_matter_falls_down_does_antimatter_fall_up_c...</td>
      <td>7.29M</td>
      <td>10.7G</td>
      <td>597K</td>
      <td>85.2K</td>
      <td>20140929</td>
      <td>2 min 54 s</td>
      <td>351122</td>
    </tr>
    <tr>
      <th>992</th>
      <td>the_infamous_and_ingenious_ho_chi_minh_trail_c...</td>
      <td>13.7M</td>
      <td>10.7G</td>
      <td>762K</td>
      <td>84.6K</td>
      <td>20130314</td>
      <td>3 min 54 s</td>
      <td>488654</td>
    </tr>
    <tr>
      <th>993</th>
      <td>how_blue_jeans_were_invented_moments_of_vision...</td>
      <td>3.82M</td>
      <td>10.7G</td>
      <td>422K</td>
      <td>84.3K</td>
      <td>20170406</td>
      <td>1 min 56 s</td>
      <td>275174</td>
    </tr>
    <tr>
      <th>994</th>
      <td>why_should_you_read_the_joy_luck_club_by_amy_t...</td>
      <td>6.08M</td>
      <td>10.7G</td>
      <td>168K</td>
      <td>84.0K</td>
      <td>20191216</td>
      <td>3 min 52 s</td>
      <td>219692</td>
    </tr>
    <tr>
      <th>995</th>
      <td>could_your_brain_repair_itself_ralitsa_petrova</td>
      <td>6.33M</td>
      <td>10.8G</td>
      <td>586K</td>
      <td>83.7K</td>
      <td>20150427</td>
      <td>3 min 59 s</td>
      <td>221390</td>
    </tr>
    <tr>
      <th>996</th>
      <td>the_strengths_and_weaknesses_of_acids_and_base...</td>
      <td>6.84M</td>
      <td>10.8G</td>
      <td>667K</td>
      <td>83.3K</td>
      <td>20131024</td>
      <td>3 min 47 s</td>
      <td>252196</td>
    </tr>
    <tr>
      <th>997</th>
      <td>underwater_farms_vs_climate_change_ayana_eliza...</td>
      <td>12.2M</td>
      <td>10.8G</td>
      <td>250K</td>
      <td>83.3K</td>
      <td>20190613</td>
      <td>4 min 30 s</td>
      <td>378839</td>
    </tr>
    <tr>
      <th>998</th>
      <td>a_brief_history_of_plural_word_s_john_mcwhorter</td>
      <td>8.01M</td>
      <td>10.8G</td>
      <td>748K</td>
      <td>83.2K</td>
      <td>20130722</td>
      <td>4 min 26 s</td>
      <td>252219</td>
    </tr>
    <tr>
      <th>999</th>
      <td>why_wasnt_the_bill_of_rights_originally_in_the...</td>
      <td>9.62M</td>
      <td>10.8G</td>
      <td>497K</td>
      <td>82.8K</td>
      <td>20160614</td>
      <td>4 min 32 s</td>
      <td>295939</td>
    </tr>
    <tr>
      <th>1000</th>
      <td>logarithms_explained_steve_kelly</td>
      <td>5.67M</td>
      <td>10.8G</td>
      <td>825K</td>
      <td>82.5K</td>
      <td>20120820</td>
      <td>3 min 33 s</td>
      <td>222367</td>
    </tr>
    <tr>
      <th>1001</th>
      <td>your_body_language_shapes_who_you_are_amy_cuddy</td>
      <td>54.3M</td>
      <td>10.8G</td>
      <td>739K</td>
      <td>82.1K</td>
      <td>20130608</td>
      <td>21 min 2 s</td>
      <td>360965</td>
    </tr>
    <tr>
      <th>1002</th>
      <td>the_case_of_the_missing_fractals_alex_rosentha...</td>
      <td>21.3M</td>
      <td>10.9G</td>
      <td>654K</td>
      <td>81.8K</td>
      <td>20140429</td>
      <td>4 min 52 s</td>
      <td>610241</td>
    </tr>
    <tr>
      <th>1003</th>
      <td>why_are_manhole_covers_round_marc_chamberland</td>
      <td>6.85M</td>
      <td>10.9G</td>
      <td>571K</td>
      <td>81.6K</td>
      <td>20150413</td>
      <td>3 min 34 s</td>
      <td>267879</td>
    </tr>
    <tr>
      <th>1004</th>
      <td>the_cockroach_beatbox</td>
      <td>15.2M</td>
      <td>10.9G</td>
      <td>809K</td>
      <td>80.9K</td>
      <td>20120311</td>
      <td>6 min 15 s</td>
      <td>340135</td>
    </tr>
    <tr>
      <th>1005</th>
      <td>how_we_think_complex_cells_evolved_adam_jacobson</td>
      <td>9.84M</td>
      <td>10.9G</td>
      <td>565K</td>
      <td>80.7K</td>
      <td>20150217</td>
      <td>5 min 41 s</td>
      <td>241402</td>
    </tr>
    <tr>
      <th>1006</th>
      <td>how_do_brain_scans_work_john_borghi_and_elizab...</td>
      <td>9.10M</td>
      <td>10.9G</td>
      <td>323K</td>
      <td>80.7K</td>
      <td>20180426</td>
      <td>4 min 59 s</td>
      <td>254478</td>
    </tr>
    <tr>
      <th>1007</th>
      <td>the_historic_womens_suffrage_march_on_washingt...</td>
      <td>10.7M</td>
      <td>10.9G</td>
      <td>241K</td>
      <td>80.2K</td>
      <td>20190304</td>
      <td>4 min 54 s</td>
      <td>306453</td>
    </tr>
    <tr>
      <th>1008</th>
      <td>is_dna_the_future_of_data_storage_leo_bear_mcg...</td>
      <td>18.0M</td>
      <td>10.9G</td>
      <td>318K</td>
      <td>79.5K</td>
      <td>20171009</td>
      <td>5 min 29 s</td>
      <td>457158</td>
    </tr>
    <tr>
      <th>1009</th>
      <td>how_the_popsicle_was_invented_moments_of_visio...</td>
      <td>3.61M</td>
      <td>10.9G</td>
      <td>396K</td>
      <td>79.2K</td>
      <td>20170502</td>
      <td>1 min 50 s</td>
      <td>272955</td>
    </tr>
    <tr>
      <th>1010</th>
      <td>the_most_lightning_struck_place_on_earth_graem...</td>
      <td>7.34M</td>
      <td>10.9G</td>
      <td>474K</td>
      <td>79.0K</td>
      <td>20160128</td>
      <td>3 min 40 s</td>
      <td>279840</td>
    </tr>
    <tr>
      <th>1011</th>
      <td>gerrymandering_how_drawing_jagged_lines_can_im...</td>
      <td>7.17M</td>
      <td>11.0G</td>
      <td>706K</td>
      <td>78.4K</td>
      <td>20121025</td>
      <td>3 min 52 s</td>
      <td>258485</td>
    </tr>
    <tr>
      <th>1012</th>
      <td>the_case_of_the_vanishing_honeybees_emma_bryce</td>
      <td>11.5M</td>
      <td>11.0G</td>
      <td>623K</td>
      <td>77.8K</td>
      <td>20140318</td>
      <td>3 min 46 s</td>
      <td>426722</td>
    </tr>
    <tr>
      <th>1013</th>
      <td>what_is_color_colm_kelleher</td>
      <td>7.20M</td>
      <td>11.0G</td>
      <td>699K</td>
      <td>77.7K</td>
      <td>20121218</td>
      <td>3 min 9 s</td>
      <td>319153</td>
    </tr>
    <tr>
      <th>1014</th>
      <td>the_second_coming_by_william_butler_yeats</td>
      <td>2.32M</td>
      <td>11.0G</td>
      <td>232K</td>
      <td>77.2K</td>
      <td>20190202</td>
      <td>1 min 56 s</td>
      <td>167551</td>
    </tr>
    <tr>
      <th>1015</th>
      <td>how_atoms_bond_george_zaidan_and_charles_morton</td>
      <td>5.04M</td>
      <td>11.0G</td>
      <td>615K</td>
      <td>76.9K</td>
      <td>20131015</td>
      <td>3 min 33 s</td>
      <td>197944</td>
    </tr>
    <tr>
      <th>1016</th>
      <td>how_the_bendy_straw_was_invented_moments_of_vi...</td>
      <td>3.05M</td>
      <td>11.0G</td>
      <td>384K</td>
      <td>76.7K</td>
      <td>20170601</td>
      <td>1 min 39 s</td>
      <td>256895</td>
    </tr>
    <tr>
      <th>1017</th>
      <td>how_do_we_study_the_stars_yuan_sen_ting</td>
      <td>9.96M</td>
      <td>11.0G</td>
      <td>531K</td>
      <td>75.8K</td>
      <td>20141007</td>
      <td>4 min 45 s</td>
      <td>293096</td>
    </tr>
    <tr>
      <th>1018</th>
      <td>the_pangaea_pop_up_michael_molina</td>
      <td>6.78M</td>
      <td>11.0G</td>
      <td>605K</td>
      <td>75.6K</td>
      <td>20140203</td>
      <td>4 min 25 s</td>
      <td>213873</td>
    </tr>
    <tr>
      <th>1019</th>
      <td>why_is_it_so_hard_to_cure_als_fernando_g_vieira</td>
      <td>10.4M</td>
      <td>11.0G</td>
      <td>302K</td>
      <td>75.6K</td>
      <td>20180531</td>
      <td>5 min 21 s</td>
      <td>271265</td>
    </tr>
    <tr>
      <th>1020</th>
      <td>light_waves_visible_and_invisible_lucianne_wal...</td>
      <td>12.0M</td>
      <td>11.0G</td>
      <td>599K</td>
      <td>74.9K</td>
      <td>20130919</td>
      <td>5 min 57 s</td>
      <td>281208</td>
    </tr>
    <tr>
      <th>1021</th>
      <td>radioactivity_expect_the_unexpected_steve_weat...</td>
      <td>9.30M</td>
      <td>11.0G</td>
      <td>674K</td>
      <td>74.9K</td>
      <td>20121210</td>
      <td>4 min 15 s</td>
      <td>305283</td>
    </tr>
    <tr>
      <th>1022</th>
      <td>accents_by_denice_frohman</td>
      <td>9.39M</td>
      <td>11.0G</td>
      <td>224K</td>
      <td>74.8K</td>
      <td>20190502</td>
      <td>2 min 31 s</td>
      <td>518754</td>
    </tr>
    <tr>
      <th>1023</th>
      <td>from_the_top_of_the_food_chain_down_rewilding_...</td>
      <td>10.1M</td>
      <td>11.0G</td>
      <td>598K</td>
      <td>74.7K</td>
      <td>20140313</td>
      <td>5 min 27 s</td>
      <td>259410</td>
    </tr>
    <tr>
      <th>1024</th>
      <td>how_to_build_a_dark_matter_detector_jenna_saffin</td>
      <td>11.5M</td>
      <td>11.1G</td>
      <td>299K</td>
      <td>74.7K</td>
      <td>20180501</td>
      <td>4 min 32 s</td>
      <td>353866</td>
    </tr>
    <tr>
      <th>1025</th>
      <td>the_history_of_african_american_social_dance_c...</td>
      <td>17.2M</td>
      <td>11.1G</td>
      <td>373K</td>
      <td>74.5K</td>
      <td>20160927</td>
      <td>4 min 52 s</td>
      <td>492857</td>
    </tr>
    <tr>
      <th>1026</th>
      <td>could_a_breathalyzer_detect_cancer_julian_burs...</td>
      <td>7.64M</td>
      <td>11.1G</td>
      <td>148K</td>
      <td>74.1K</td>
      <td>20200106</td>
      <td>4 min 39 s</td>
      <td>228917</td>
    </tr>
    <tr>
      <th>1027</th>
      <td>the_moon_illusion_andrew_vanden_heuvel</td>
      <td>8.19M</td>
      <td>11.1G</td>
      <td>667K</td>
      <td>74.1K</td>
      <td>20130903</td>
      <td>4 min 8 s</td>
      <td>276211</td>
    </tr>
    <tr>
      <th>1028</th>
      <td>rethinking_thinking_trevor_maber</td>
      <td>13.7M</td>
      <td>11.1G</td>
      <td>659K</td>
      <td>73.3K</td>
      <td>20121015</td>
      <td>5 min 32 s</td>
      <td>345515</td>
    </tr>
    <tr>
      <th>1029</th>
      <td>reasons_for_the_seasons_rebecca_kaplan</td>
      <td>8.67M</td>
      <td>11.1G</td>
      <td>659K</td>
      <td>73.2K</td>
      <td>20130523</td>
      <td>5 min 20 s</td>
      <td>226891</td>
    </tr>
    <tr>
      <th>1030</th>
      <td>for_estefani_poem_by_aracelis_girmay</td>
      <td>13.8M</td>
      <td>11.1G</td>
      <td>146K</td>
      <td>73.1K</td>
      <td>20191003</td>
      <td>3 min 27 s</td>
      <td>558298</td>
    </tr>
    <tr>
      <th>1031</th>
      <td>a_brief_history_of_religion_in_art_ted_ed</td>
      <td>14.8M</td>
      <td>11.1G</td>
      <td>585K</td>
      <td>73.1K</td>
      <td>20140616</td>
      <td>4 min 37 s</td>
      <td>448221</td>
    </tr>
    <tr>
      <th>1032</th>
      <td>the_dangerous_race_for_the_south_pole_elizabet...</td>
      <td>7.29M</td>
      <td>11.1G</td>
      <td>217K</td>
      <td>72.5K</td>
      <td>20181210</td>
      <td>4 min 47 s</td>
      <td>212753</td>
    </tr>
    <tr>
      <th>1033</th>
      <td>why_it_pays_to_work_hard_richard_st_john</td>
      <td>15.8M</td>
      <td>11.2G</td>
      <td>652K</td>
      <td>72.4K</td>
      <td>20130405</td>
      <td>6 min 22 s</td>
      <td>346011</td>
    </tr>
    <tr>
      <th>1034</th>
      <td>solid_liquid_gas_and_plasma_michael_murillo</td>
      <td>15.6M</td>
      <td>11.2G</td>
      <td>504K</td>
      <td>72.0K</td>
      <td>20150728</td>
      <td>3 min 51 s</td>
      <td>565272</td>
    </tr>
    <tr>
      <th>1035</th>
      <td>how_a_few_scientists_transformed_the_way_we_th...</td>
      <td>9.78M</td>
      <td>11.2G</td>
      <td>431K</td>
      <td>71.9K</td>
      <td>20151020</td>
      <td>4 min 38 s</td>
      <td>294010</td>
    </tr>
    <tr>
      <th>1036</th>
      <td>looks_aren_t_everything_believe_me_i_m_a_model...</td>
      <td>19.4M</td>
      <td>11.2G</td>
      <td>643K</td>
      <td>71.5K</td>
      <td>20130526</td>
      <td>9 min 37 s</td>
      <td>282114</td>
    </tr>
    <tr>
      <th>1037</th>
      <td>why_do_hospitals_have_particle_accelerators_pe...</td>
      <td>6.70M</td>
      <td>11.2G</td>
      <td>214K</td>
      <td>71.2K</td>
      <td>20190319</td>
      <td>4 min 46 s</td>
      <td>196278</td>
    </tr>
    <tr>
      <th>1038</th>
      <td>how_polarity_makes_water_behave_strangely_chri...</td>
      <td>7.16M</td>
      <td>11.2G</td>
      <td>640K</td>
      <td>71.2K</td>
      <td>20130204</td>
      <td>3 min 51 s</td>
      <td>259055</td>
    </tr>
    <tr>
      <th>1039</th>
      <td>life_of_an_astronaut_jerry_carr</td>
      <td>8.86M</td>
      <td>11.2G</td>
      <td>640K</td>
      <td>71.1K</td>
      <td>20130130</td>
      <td>4 min 51 s</td>
      <td>255228</td>
    </tr>
    <tr>
      <th>1040</th>
      <td>how_super_glue_was_invented_moments_of_vision_...</td>
      <td>3.37M</td>
      <td>11.2G</td>
      <td>355K</td>
      <td>71.0K</td>
      <td>20170206</td>
      <td>1 min 53 s</td>
      <td>249211</td>
    </tr>
    <tr>
      <th>1041</th>
      <td>do_we_really_need_pesticides_fernan_perez_galvez</td>
      <td>10.1M</td>
      <td>11.2G</td>
      <td>353K</td>
      <td>70.5K</td>
      <td>20161114</td>
      <td>5 min 17 s</td>
      <td>265837</td>
    </tr>
    <tr>
      <th>1042</th>
      <td>why_should_you_read_sci_fi_superstar_octavia_e...</td>
      <td>9.27M</td>
      <td>11.3G</td>
      <td>212K</td>
      <td>70.5K</td>
      <td>20190225</td>
      <td>4 min 14 s</td>
      <td>305861</td>
    </tr>
    <tr>
      <th>1043</th>
      <td>why_aren_t_we_only_using_solar_power_alexandro...</td>
      <td>10.8M</td>
      <td>11.3G</td>
      <td>564K</td>
      <td>70.5K</td>
      <td>20140619</td>
      <td>4 min 42 s</td>
      <td>320787</td>
    </tr>
    <tr>
      <th>1044</th>
      <td>what_aristotle_and_joshua_bell_can_teach_us_ab...</td>
      <td>9.96M</td>
      <td>11.3G</td>
      <td>634K</td>
      <td>70.4K</td>
      <td>20130114</td>
      <td>4 min 39 s</td>
      <td>298692</td>
    </tr>
    <tr>
      <th>1045</th>
      <td>to_make_use_of_water_by_safia_elhillo</td>
      <td>4.22M</td>
      <td>11.3G</td>
      <td>211K</td>
      <td>70.4K</td>
      <td>20190202</td>
      <td>2 min 4 s</td>
      <td>284904</td>
    </tr>
    <tr>
      <th>1046</th>
      <td>how_coffee_got_quicker_moments_of_vision_2_jes...</td>
      <td>4.18M</td>
      <td>11.3G</td>
      <td>421K</td>
      <td>70.1K</td>
      <td>20160808</td>
      <td>1 min 47 s</td>
      <td>325320</td>
    </tr>
    <tr>
      <th>1047</th>
      <td>what_triggers_a_chemical_reaction_kareem_jarrah</td>
      <td>6.09M</td>
      <td>11.3G</td>
      <td>489K</td>
      <td>69.8K</td>
      <td>20150120</td>
      <td>3 min 45 s</td>
      <td>226765</td>
    </tr>
    <tr>
      <th>1048</th>
      <td>the_battle_of_the_greek_tragedies_melanie_sirof</td>
      <td>13.7M</td>
      <td>11.3G</td>
      <td>488K</td>
      <td>69.8K</td>
      <td>20150601</td>
      <td>5 min 6 s</td>
      <td>373425</td>
    </tr>
    <tr>
      <th>1049</th>
      <td>the_science_of_symmetry_colm_kelleher</td>
      <td>15.5M</td>
      <td>11.3G</td>
      <td>556K</td>
      <td>69.4K</td>
      <td>20140513</td>
      <td>5 min 8 s</td>
      <td>421108</td>
    </tr>
    <tr>
      <th>1050</th>
      <td>how_the_stethoscope_was_invented_moments_of_vi...</td>
      <td>3.79M</td>
      <td>11.3G</td>
      <td>347K</td>
      <td>69.4K</td>
      <td>20161229</td>
      <td>1 min 48 s</td>
      <td>293893</td>
    </tr>
    <tr>
      <th>1051</th>
      <td>dead_stuff_the_secret_ingredient_in_our_food_c...</td>
      <td>8.00M</td>
      <td>11.3G</td>
      <td>555K</td>
      <td>69.3K</td>
      <td>20140320</td>
      <td>3 min 50 s</td>
      <td>290847</td>
    </tr>
    <tr>
      <th>1052</th>
      <td>why_do_animals_form_swarms_maria_r_d_orsogna</td>
      <td>18.5M</td>
      <td>11.3G</td>
      <td>272K</td>
      <td>68.0K</td>
      <td>20171218</td>
      <td>4 min 5 s</td>
      <td>632474</td>
    </tr>
    <tr>
      <th>1053</th>
      <td>pixar_the_math_behind_the_movies_tony_derose</td>
      <td>15.8M</td>
      <td>11.4G</td>
      <td>544K</td>
      <td>67.9K</td>
      <td>20140325</td>
      <td>7 min 33 s</td>
      <td>293169</td>
    </tr>
    <tr>
      <th>1054</th>
      <td>what_can_you_learn_from_ancient_skeletons_farn...</td>
      <td>8.48M</td>
      <td>11.4G</td>
      <td>339K</td>
      <td>67.8K</td>
      <td>20170615</td>
      <td>4 min 7 s</td>
      <td>287761</td>
    </tr>
    <tr>
      <th>1055</th>
      <td>the_dust_bunnies_that_built_our_planet_lorin_s...</td>
      <td>12.9M</td>
      <td>11.4G</td>
      <td>203K</td>
      <td>67.7K</td>
      <td>20190905</td>
      <td>5 min 30 s</td>
      <td>326650</td>
    </tr>
    <tr>
      <th>1056</th>
      <td>why_is_there_a_b_in_doubt_gina_cooke</td>
      <td>4.63M</td>
      <td>11.4G</td>
      <td>605K</td>
      <td>67.2K</td>
      <td>20121217</td>
      <td>3 min 27 s</td>
      <td>186961</td>
    </tr>
    <tr>
      <th>1057</th>
      <td>an_unsung_hero_of_the_civil_rights_movement_ch...</td>
      <td>9.65M</td>
      <td>11.4G</td>
      <td>201K</td>
      <td>67.1K</td>
      <td>20190221</td>
      <td>4 min 29 s</td>
      <td>300600</td>
    </tr>
    <tr>
      <th>1058</th>
      <td>how_the_rubber_glove_was_invented_moments_of_v...</td>
      <td>3.30M</td>
      <td>11.4G</td>
      <td>335K</td>
      <td>67.0K</td>
      <td>20161011</td>
      <td>1 min 34 s</td>
      <td>292312</td>
    </tr>
    <tr>
      <th>1059</th>
      <td>could_we_survive_prolonged_space_travel_lisa_nip</td>
      <td>12.7M</td>
      <td>11.4G</td>
      <td>335K</td>
      <td>66.9K</td>
      <td>20161004</td>
      <td>4 min 55 s</td>
      <td>361178</td>
    </tr>
    <tr>
      <th>1060</th>
      <td>how_did_feathers_evolve_carl_zimmer</td>
      <td>6.93M</td>
      <td>11.4G</td>
      <td>598K</td>
      <td>66.4K</td>
      <td>20130502</td>
      <td>3 min 26 s</td>
      <td>281039</td>
    </tr>
    <tr>
      <th>1061</th>
      <td>the_race_to_sequence_the_human_genome_tien_nguyen</td>
      <td>10.8M</td>
      <td>11.4G</td>
      <td>393K</td>
      <td>65.4K</td>
      <td>20151012</td>
      <td>4 min 59 s</td>
      <td>304255</td>
    </tr>
    <tr>
      <th>1062</th>
      <td>the_first_asteroid_ever_discovered_carrie_nugent</td>
      <td>7.50M</td>
      <td>11.4G</td>
      <td>262K</td>
      <td>65.4K</td>
      <td>20171016</td>
      <td>5 min 5 s</td>
      <td>206250</td>
    </tr>
    <tr>
      <th>1063</th>
      <td>which_sunscreen_should_you_choose_mary_poffenroth</td>
      <td>8.04M</td>
      <td>11.4G</td>
      <td>392K</td>
      <td>65.4K</td>
      <td>20160801</td>
      <td>4 min 39 s</td>
      <td>241155</td>
    </tr>
    <tr>
      <th>1064</th>
      <td>the_fundamentals_of_space_time_part_3_andrew_p...</td>
      <td>5.63M</td>
      <td>11.4G</td>
      <td>521K</td>
      <td>65.1K</td>
      <td>20140522</td>
      <td>3 min 26 s</td>
      <td>228460</td>
    </tr>
    <tr>
      <th>1065</th>
      <td>everyday_leadership_drew_dudley</td>
      <td>12.9M</td>
      <td>11.5G</td>
      <td>585K</td>
      <td>65.0K</td>
      <td>20130815</td>
      <td>6 min 14 s</td>
      <td>288385</td>
    </tr>
    <tr>
      <th>1066</th>
      <td>how_much_does_a_video_weigh_michael_stevens_of...</td>
      <td>15.4M</td>
      <td>11.5G</td>
      <td>581K</td>
      <td>64.5K</td>
      <td>20130424</td>
      <td>7 min 20 s</td>
      <td>292834</td>
    </tr>
    <tr>
      <th>1067</th>
      <td>feedback_loops_how_nature_gets_its_rhythms_anj...</td>
      <td>14.5M</td>
      <td>11.5G</td>
      <td>516K</td>
      <td>64.5K</td>
      <td>20140825</td>
      <td>5 min 10 s</td>
      <td>393132</td>
    </tr>
    <tr>
      <th>1068</th>
      <td>the_science_of_snowflakes_marusa_bradac</td>
      <td>7.73M</td>
      <td>11.5G</td>
      <td>386K</td>
      <td>64.3K</td>
      <td>20151222</td>
      <td>4 min 29 s</td>
      <td>240560</td>
    </tr>
    <tr>
      <th>1069</th>
      <td>is_there_a_reproducibility_crisis_in_science_m...</td>
      <td>9.31M</td>
      <td>11.5G</td>
      <td>321K</td>
      <td>64.3K</td>
      <td>20161205</td>
      <td>4 min 46 s</td>
      <td>273054</td>
    </tr>
    <tr>
      <th>1070</th>
      <td>the_nutritionist_by_andrea_gibson</td>
      <td>8.67M</td>
      <td>11.5G</td>
      <td>193K</td>
      <td>64.3K</td>
      <td>20190202</td>
      <td>4 min 44 s</td>
      <td>255304</td>
    </tr>
    <tr>
      <th>1071</th>
      <td>what_is_chemical_equilibrium_george_zaidan_and...</td>
      <td>8.02M</td>
      <td>11.5G</td>
      <td>575K</td>
      <td>63.9K</td>
      <td>20130723</td>
      <td>3 min 24 s</td>
      <td>328688</td>
    </tr>
    <tr>
      <th>1072</th>
      <td>animation_basics_the_art_of_timing_and_spacing...</td>
      <td>12.2M</td>
      <td>11.5G</td>
      <td>509K</td>
      <td>63.6K</td>
      <td>20140128</td>
      <td>6 min 42 s</td>
      <td>253563</td>
    </tr>
    <tr>
      <th>1073</th>
      <td>are_there_universal_expressions_of_emotion_sop...</td>
      <td>8.79M</td>
      <td>11.5G</td>
      <td>254K</td>
      <td>63.5K</td>
      <td>20180703</td>
      <td>4 min 51 s</td>
      <td>253434</td>
    </tr>
    <tr>
      <th>1074</th>
      <td>how_brass_instruments_work_al_cannon</td>
      <td>12.8M</td>
      <td>11.6G</td>
      <td>443K</td>
      <td>63.3K</td>
      <td>20150407</td>
      <td>4 min 11 s</td>
      <td>427559</td>
    </tr>
    <tr>
      <th>1075</th>
      <td>when_to_use_me_myself_and_i_emma_bryce</td>
      <td>5.59M</td>
      <td>11.6G</td>
      <td>379K</td>
      <td>63.2K</td>
      <td>20150914</td>
      <td>2 min 56 s</td>
      <td>266086</td>
    </tr>
    <tr>
      <th>1076</th>
      <td>are_shakespeare_s_plays_encoded_within_pi</td>
      <td>12.2M</td>
      <td>11.6G</td>
      <td>629K</td>
      <td>62.9K</td>
      <td>20120313</td>
      <td>3 min 45 s</td>
      <td>452530</td>
    </tr>
    <tr>
      <th>1077</th>
      <td>the_weird_and_wonderful_metamorphosis_of_the_b...</td>
      <td>10.4M</td>
      <td>11.6G</td>
      <td>251K</td>
      <td>62.9K</td>
      <td>20180301</td>
      <td>5 min 2 s</td>
      <td>289367</td>
    </tr>
    <tr>
      <th>1078</th>
      <td>is_there_a_center_of_the_universe_marjee_chmie...</td>
      <td>9.33M</td>
      <td>11.6G</td>
      <td>562K</td>
      <td>62.5K</td>
      <td>20130625</td>
      <td>4 min 13 s</td>
      <td>308445</td>
    </tr>
    <tr>
      <th>1079</th>
      <td>corruption_wealth_and_beauty_the_history_of_th...</td>
      <td>11.4M</td>
      <td>11.6G</td>
      <td>498K</td>
      <td>62.3K</td>
      <td>20140904</td>
      <td>4 min 50 s</td>
      <td>328886</td>
    </tr>
    <tr>
      <th>1080</th>
      <td>overcoming_obstacles_steven_claunch</td>
      <td>11.5M</td>
      <td>11.6G</td>
      <td>558K</td>
      <td>62.0K</td>
      <td>20130821</td>
      <td>4 min 22 s</td>
      <td>368332</td>
    </tr>
    <tr>
      <th>1081</th>
      <td>is_there_a_difference_between_art_and_craft_la...</td>
      <td>12.2M</td>
      <td>11.6G</td>
      <td>489K</td>
      <td>61.2K</td>
      <td>20140306</td>
      <td>5 min 30 s</td>
      <td>309666</td>
    </tr>
    <tr>
      <th>1082</th>
      <td>what_is_abstract_expressionism_sarah_rosenthal</td>
      <td>15.2M</td>
      <td>11.6G</td>
      <td>364K</td>
      <td>60.7K</td>
      <td>20160428</td>
      <td>4 min 49 s</td>
      <td>440451</td>
    </tr>
    <tr>
      <th>1083</th>
      <td>why_do_people_have_seasonal_allergies_eleanor_...</td>
      <td>15.2M</td>
      <td>11.7G</td>
      <td>364K</td>
      <td>60.7K</td>
      <td>20160526</td>
      <td>5 min 1 s</td>
      <td>422154</td>
    </tr>
    <tr>
      <th>1084</th>
      <td>harvey_milk_s_radical_vision_of_equality_lilli...</td>
      <td>9.26M</td>
      <td>11.7G</td>
      <td>182K</td>
      <td>60.6K</td>
      <td>20190312</td>
      <td>5 min 23 s</td>
      <td>240418</td>
    </tr>
    <tr>
      <th>1085</th>
      <td>music_and_creativity_in_ancient_greece_tim_hansen</td>
      <td>9.58M</td>
      <td>11.7G</td>
      <td>483K</td>
      <td>60.4K</td>
      <td>20131203</td>
      <td>4 min 45 s</td>
      <td>280906</td>
    </tr>
    <tr>
      <th>1086</th>
      <td>how_computers_translate_human_language_ioannis...</td>
      <td>11.6M</td>
      <td>11.7G</td>
      <td>360K</td>
      <td>60.0K</td>
      <td>20151026</td>
      <td>4 min 44 s</td>
      <td>340501</td>
    </tr>
    <tr>
      <th>1087</th>
      <td>become_a_slam_poet_in_five_steps_gayle_danley</td>
      <td>11.5M</td>
      <td>11.7G</td>
      <td>534K</td>
      <td>59.3K</td>
      <td>20130327</td>
      <td>3 min 31 s</td>
      <td>457431</td>
    </tr>
    <tr>
      <th>1088</th>
      <td>the_chemical_reaction_that_feeds_the_world_dan...</td>
      <td>10.7M</td>
      <td>11.7G</td>
      <td>471K</td>
      <td>58.8K</td>
      <td>20131118</td>
      <td>5 min 18 s</td>
      <td>281083</td>
    </tr>
    <tr>
      <th>1089</th>
      <td>why_tragedies_are_alluring_david_e_rivas</td>
      <td>9.11M</td>
      <td>11.7G</td>
      <td>411K</td>
      <td>58.8K</td>
      <td>20150709</td>
      <td>4 min 25 s</td>
      <td>287473</td>
    </tr>
    <tr>
      <th>1090</th>
      <td>the_effects_of_underwater_pressure_on_the_body...</td>
      <td>6.97M</td>
      <td>11.7G</td>
      <td>411K</td>
      <td>58.7K</td>
      <td>20150402</td>
      <td>4 min 2 s</td>
      <td>241322</td>
    </tr>
    <tr>
      <th>1091</th>
      <td>how_to_create_cleaner_coal_emma_bryce</td>
      <td>9.86M</td>
      <td>11.7G</td>
      <td>410K</td>
      <td>58.6K</td>
      <td>20141209</td>
      <td>5 min 53 s</td>
      <td>234056</td>
    </tr>
    <tr>
      <th>1092</th>
      <td>the_fight_for_the_right_to_vote_in_the_united_...</td>
      <td>6.60M</td>
      <td>11.7G</td>
      <td>469K</td>
      <td>58.6K</td>
      <td>20131105</td>
      <td>4 min 30 s</td>
      <td>204627</td>
    </tr>
    <tr>
      <th>1093</th>
      <td>what_happens_if_you_guess_leigh_nataro</td>
      <td>7.57M</td>
      <td>11.7G</td>
      <td>582K</td>
      <td>58.2K</td>
      <td>20120831</td>
      <td>5 min 27 s</td>
      <td>193994</td>
    </tr>
    <tr>
      <th>1094</th>
      <td>pizza_physics_new_york_style_colm_kelleher</td>
      <td>7.80M</td>
      <td>11.8G</td>
      <td>516K</td>
      <td>57.4K</td>
      <td>20121206</td>
      <td>3 min 57 s</td>
      <td>275298</td>
    </tr>
    <tr>
      <th>1095</th>
      <td>the_many_meanings_of_michelangelo_s_statue_of_...</td>
      <td>5.54M</td>
      <td>11.8G</td>
      <td>459K</td>
      <td>57.4K</td>
      <td>20140715</td>
      <td>3 min 18 s</td>
      <td>234366</td>
    </tr>
    <tr>
      <th>1096</th>
      <td>how_misused_modifiers_can_hurt_your_writing_em...</td>
      <td>5.25M</td>
      <td>11.8G</td>
      <td>400K</td>
      <td>57.2K</td>
      <td>20150908</td>
      <td>3 min 20 s</td>
      <td>219291</td>
    </tr>
    <tr>
      <th>1097</th>
      <td>the_controversial_origins_of_the_encyclopedia_...</td>
      <td>12.6M</td>
      <td>11.8G</td>
      <td>341K</td>
      <td>56.9K</td>
      <td>20160218</td>
      <td>5 min 20 s</td>
      <td>329169</td>
    </tr>
    <tr>
      <th>1098</th>
      <td>how_quantum_mechanics_explains_global_warming_...</td>
      <td>17.5M</td>
      <td>11.8G</td>
      <td>455K</td>
      <td>56.9K</td>
      <td>20140717</td>
      <td>5 min 0 s</td>
      <td>489583</td>
    </tr>
    <tr>
      <th>1099</th>
      <td>a_simple_way_to_tell_insects_apart_anika_hazra</td>
      <td>6.46M</td>
      <td>11.8G</td>
      <td>226K</td>
      <td>56.5K</td>
      <td>20180403</td>
      <td>4 min 6 s</td>
      <td>220080</td>
    </tr>
    <tr>
      <th>1100</th>
      <td>how_smudge_proof_lipstick_was_invented_moments...</td>
      <td>4.12M</td>
      <td>11.8G</td>
      <td>283K</td>
      <td>56.5K</td>
      <td>20161206</td>
      <td>2 min 5 s</td>
      <td>275583</td>
    </tr>
    <tr>
      <th>1101</th>
      <td>ode_to_the_only_black_kid_in_the_class_poem_by...</td>
      <td>1.76M</td>
      <td>11.8G</td>
      <td>169K</td>
      <td>56.3K</td>
      <td>20190909</td>
      <td>1 min 8 s</td>
      <td>213864</td>
    </tr>
    <tr>
      <th>1102</th>
      <td>can_robots_be_creative_gil_weinberg</td>
      <td>8.49M</td>
      <td>11.8G</td>
      <td>393K</td>
      <td>56.1K</td>
      <td>20150319</td>
      <td>5 min 26 s</td>
      <td>218139</td>
    </tr>
    <tr>
      <th>1103</th>
      <td>new_colossus_by_emma_lazarus</td>
      <td>1.98M</td>
      <td>11.8G</td>
      <td>168K</td>
      <td>56.0K</td>
      <td>20190702</td>
      <td>1 min 24 s</td>
      <td>195780</td>
    </tr>
    <tr>
      <th>1104</th>
      <td>what_is_the_universe_made_of_dennis_wildfogel</td>
      <td>11.3M</td>
      <td>11.8G</td>
      <td>445K</td>
      <td>55.7K</td>
      <td>20140225</td>
      <td>4 min 4 s</td>
      <td>387456</td>
    </tr>
    <tr>
      <th>1105</th>
      <td>why_do_we_have_museums_j_v_maranto</td>
      <td>11.7M</td>
      <td>11.8G</td>
      <td>386K</td>
      <td>55.1K</td>
      <td>20150205</td>
      <td>5 min 43 s</td>
      <td>285807</td>
    </tr>
    <tr>
      <th>1106</th>
      <td>the_popularity_plight_and_poop_of_penguins_dya...</td>
      <td>12.8M</td>
      <td>11.9G</td>
      <td>437K</td>
      <td>54.6K</td>
      <td>20131217</td>
      <td>5 min 23 s</td>
      <td>331254</td>
    </tr>
    <tr>
      <th>1107</th>
      <td>the_suns_surprising_movement_across_the_sky_go...</td>
      <td>7.46M</td>
      <td>11.9G</td>
      <td>327K</td>
      <td>54.6K</td>
      <td>20151221</td>
      <td>4 min 22 s</td>
      <td>238001</td>
    </tr>
    <tr>
      <th>1108</th>
      <td>can_machines_read_your_emotions_kostas_karpouzis</td>
      <td>7.50M</td>
      <td>11.9G</td>
      <td>273K</td>
      <td>54.6K</td>
      <td>20161129</td>
      <td>4 min 38 s</td>
      <td>225772</td>
    </tr>
    <tr>
      <th>1109</th>
      <td>how_to_live_to_be_100_dan_buettner</td>
      <td>32.8M</td>
      <td>11.9G</td>
      <td>491K</td>
      <td>54.5K</td>
      <td>20130417</td>
      <td>19 min 39 s</td>
      <td>233345</td>
    </tr>
    <tr>
      <th>1110</th>
      <td>not_all_scientific_studies_are_created_equal_d...</td>
      <td>6.23M</td>
      <td>11.9G</td>
      <td>436K</td>
      <td>54.5K</td>
      <td>20140428</td>
      <td>4 min 26 s</td>
      <td>196301</td>
    </tr>
    <tr>
      <th>1111</th>
      <td>the_power_of_a_great_introduction_carolyn_mohr</td>
      <td>10.4M</td>
      <td>11.9G</td>
      <td>490K</td>
      <td>54.4K</td>
      <td>20120927</td>
      <td>4 min 42 s</td>
      <td>310052</td>
    </tr>
    <tr>
      <th>1112</th>
      <td>why_the_shape_of_your_screen_matters_brian_ger...</td>
      <td>5.26M</td>
      <td>11.9G</td>
      <td>539K</td>
      <td>53.9K</td>
      <td>20120913</td>
      <td>3 min 32 s</td>
      <td>208032</td>
    </tr>
    <tr>
      <th>1113</th>
      <td>why_neutrinos_matter_silvia_bravo_gallart</td>
      <td>6.62M</td>
      <td>11.9G</td>
      <td>373K</td>
      <td>53.3K</td>
      <td>20150428</td>
      <td>4 min 40 s</td>
      <td>198301</td>
    </tr>
    <tr>
      <th>1114</th>
      <td>the_making_of_the_american_constitution_judy_w...</td>
      <td>7.78M</td>
      <td>11.9G</td>
      <td>479K</td>
      <td>53.2K</td>
      <td>20121023</td>
      <td>3 min 57 s</td>
      <td>274884</td>
    </tr>
    <tr>
      <th>1115</th>
      <td>the_power_of_passion_richard_st_john</td>
      <td>15.5M</td>
      <td>11.9G</td>
      <td>479K</td>
      <td>53.2K</td>
      <td>20130405</td>
      <td>6 min 54 s</td>
      <td>313957</td>
    </tr>
    <tr>
      <th>1116</th>
      <td>walking_on_eggs_sick_science_069</td>
      <td>2.07M</td>
      <td>12.0G</td>
      <td>532K</td>
      <td>53.2K</td>
      <td>20120104</td>
      <td>1 min 5 s</td>
      <td>265593</td>
    </tr>
    <tr>
      <th>1117</th>
      <td>how_to_visualize_one_part_per_million_kim_pres...</td>
      <td>5.68M</td>
      <td>12.0G</td>
      <td>318K</td>
      <td>53.0K</td>
      <td>20160815</td>
      <td>2 min 27 s</td>
      <td>323338</td>
    </tr>
    <tr>
      <th>1118</th>
      <td>how_inventions_change_history_for_better_and_f...</td>
      <td>12.5M</td>
      <td>12.0G</td>
      <td>476K</td>
      <td>52.8K</td>
      <td>20121017</td>
      <td>5 min 14 s</td>
      <td>335235</td>
    </tr>
    <tr>
      <th>1119</th>
      <td>how_fiction_can_change_reality_jessica_wise</td>
      <td>8.99M</td>
      <td>12.0G</td>
      <td>528K</td>
      <td>52.8K</td>
      <td>20120823</td>
      <td>4 min 29 s</td>
      <td>280363</td>
    </tr>
    <tr>
      <th>1120</th>
      <td>will_future_spacecraft_fit_in_our_pockets_dhon...</td>
      <td>8.31M</td>
      <td>12.0G</td>
      <td>369K</td>
      <td>52.8K</td>
      <td>20150528</td>
      <td>4 min 36 s</td>
      <td>251798</td>
    </tr>
    <tr>
      <th>1121</th>
      <td>big_data_tim_smith</td>
      <td>12.9M</td>
      <td>12.0G</td>
      <td>474K</td>
      <td>52.7K</td>
      <td>20130503</td>
      <td>6 min 7 s</td>
      <td>294694</td>
    </tr>
    <tr>
      <th>1122</th>
      <td>learning_from_smallpox_how_to_eradicate_a_dise...</td>
      <td>9.37M</td>
      <td>12.0G</td>
      <td>366K</td>
      <td>52.3K</td>
      <td>20150310</td>
      <td>5 min 44 s</td>
      <td>227851</td>
    </tr>
    <tr>
      <th>1123</th>
      <td>can_plants_talk_to_each_other_richard_karban</td>
      <td>14.5M</td>
      <td>12.0G</td>
      <td>312K</td>
      <td>52.0K</td>
      <td>20160502</td>
      <td>4 min 38 s</td>
      <td>438726</td>
    </tr>
    <tr>
      <th>1124</th>
      <td>four_ways_to_understand_the_earth_s_age_joshua...</td>
      <td>10.1M</td>
      <td>12.0G</td>
      <td>465K</td>
      <td>51.7K</td>
      <td>20130829</td>
      <td>3 min 44 s</td>
      <td>379037</td>
    </tr>
    <tr>
      <th>1125</th>
      <td>what_is_a_gift_economy_alex_gendler</td>
      <td>7.23M</td>
      <td>12.0G</td>
      <td>356K</td>
      <td>50.8K</td>
      <td>20141223</td>
      <td>4 min 5 s</td>
      <td>246746</td>
    </tr>
    <tr>
      <th>1126</th>
      <td>ted_invites_the_class_of_2020_to_give_a_ted_talk</td>
      <td>3.54M</td>
      <td>12.0G</td>
      <td>100.0K</td>
      <td>50.0K</td>
      <td>20200511</td>
      <td>1 min 43 s</td>
      <td>288073</td>
    </tr>
    <tr>
      <th>1127</th>
      <td>how_i_responded_to_sexism_in_gaming_with_empat...</td>
      <td>10.8M</td>
      <td>12.1G</td>
      <td>347K</td>
      <td>49.6K</td>
      <td>20150526</td>
      <td>6 min 59 s</td>
      <td>215348</td>
    </tr>
    <tr>
      <th>1128</th>
      <td>is_our_universe_the_only_universe_brian_greene</td>
      <td>44.1M</td>
      <td>12.1G</td>
      <td>446K</td>
      <td>49.5K</td>
      <td>20130419</td>
      <td>21 min 47 s</td>
      <td>282929</td>
    </tr>
    <tr>
      <th>1129</th>
      <td>what_s_the_definition_of_comedy_banana_addison...</td>
      <td>7.20M</td>
      <td>12.1G</td>
      <td>439K</td>
      <td>48.8K</td>
      <td>20130730</td>
      <td>4 min 50 s</td>
      <td>207745</td>
    </tr>
    <tr>
      <th>1130</th>
      <td>the_coelacanth_a_living_fossil_of_a_fish_erin_...</td>
      <td>10.7M</td>
      <td>12.1G</td>
      <td>385K</td>
      <td>48.2K</td>
      <td>20140729</td>
      <td>4 min 16 s</td>
      <td>348930</td>
    </tr>
    <tr>
      <th>1131</th>
      <td>the_power_of_simple_words_terin_izil</td>
      <td>3.90M</td>
      <td>12.1G</td>
      <td>476K</td>
      <td>47.6K</td>
      <td>20120311</td>
      <td>2 min 1 s</td>
      <td>269234</td>
    </tr>
    <tr>
      <th>1132</th>
      <td>the_punishable_perils_of_plagiarism_melissa_hu...</td>
      <td>8.44M</td>
      <td>12.1G</td>
      <td>428K</td>
      <td>47.6K</td>
      <td>20130614</td>
      <td>3 min 47 s</td>
      <td>311870</td>
    </tr>
    <tr>
      <th>1133</th>
      <td>the_true_story_of_true_gina_cooke</td>
      <td>16.2M</td>
      <td>12.1G</td>
      <td>380K</td>
      <td>47.4K</td>
      <td>20131216</td>
      <td>4 min 27 s</td>
      <td>507111</td>
    </tr>
    <tr>
      <th>1134</th>
      <td>the_microbial_jungles_all_over_the_place_and_y...</td>
      <td>10.3M</td>
      <td>12.2G</td>
      <td>284K</td>
      <td>47.4K</td>
      <td>20160517</td>
      <td>5 min 10 s</td>
      <td>278806</td>
    </tr>
    <tr>
      <th>1135</th>
      <td>electric_vocabulary</td>
      <td>12.9M</td>
      <td>12.2G</td>
      <td>467K</td>
      <td>46.7K</td>
      <td>20120716</td>
      <td>6 min 56 s</td>
      <td>259706</td>
    </tr>
    <tr>
      <th>1136</th>
      <td>dna_the_book_of_you_joe_hanson</td>
      <td>13.5M</td>
      <td>12.2G</td>
      <td>418K</td>
      <td>46.4K</td>
      <td>20121126</td>
      <td>4 min 28 s</td>
      <td>422447</td>
    </tr>
    <tr>
      <th>1137</th>
      <td>tycho_brahe_the_scandalous_astronomer_dan_wenkel</td>
      <td>11.4M</td>
      <td>12.2G</td>
      <td>370K</td>
      <td>46.2K</td>
      <td>20140612</td>
      <td>4 min 7 s</td>
      <td>386405</td>
    </tr>
    <tr>
      <th>1138</th>
      <td>what_s_below_the_tip_of_the_iceberg_camille_se...</td>
      <td>8.67M</td>
      <td>12.2G</td>
      <td>416K</td>
      <td>46.2K</td>
      <td>20130724</td>
      <td>4 min 51 s</td>
      <td>249876</td>
    </tr>
    <tr>
      <th>1139</th>
      <td>birth_of_a_nickname_john_mcwhorter</td>
      <td>7.97M</td>
      <td>12.2G</td>
      <td>369K</td>
      <td>46.1K</td>
      <td>20130924</td>
      <td>4 min 56 s</td>
      <td>225681</td>
    </tr>
    <tr>
      <th>1140</th>
      <td>how_to_organize_add_and_multiply_matrices_bill...</td>
      <td>7.01M</td>
      <td>12.2G</td>
      <td>413K</td>
      <td>45.9K</td>
      <td>20130304</td>
      <td>4 min 40 s</td>
      <td>210006</td>
    </tr>
    <tr>
      <th>1141</th>
      <td>the_operating_system_of_life_george_zaidan_and...</td>
      <td>7.67M</td>
      <td>12.2G</td>
      <td>366K</td>
      <td>45.8K</td>
      <td>20131111</td>
      <td>4 min 0 s</td>
      <td>267476</td>
    </tr>
    <tr>
      <th>1142</th>
      <td>introducing_ted_ed_lessons_worth_sharing</td>
      <td>6.73M</td>
      <td>12.2G</td>
      <td>457K</td>
      <td>45.7K</td>
      <td>20120312</td>
      <td>2 min 11 s</td>
      <td>429640</td>
    </tr>
    <tr>
      <th>1143</th>
      <td>the_historical_audacity_of_the_louisiana_purch...</td>
      <td>11.2M</td>
      <td>12.2G</td>
      <td>412K</td>
      <td>45.7K</td>
      <td>20130207</td>
      <td>3 min 38 s</td>
      <td>428893</td>
    </tr>
    <tr>
      <th>1144</th>
      <td>the_importance_of_focus_richard_st_john</td>
      <td>13.8M</td>
      <td>12.2G</td>
      <td>411K</td>
      <td>45.7K</td>
      <td>20130306</td>
      <td>5 min 54 s</td>
      <td>325811</td>
    </tr>
    <tr>
      <th>1145</th>
      <td>how_people_rationalize_fraud_kelly_richmond_pope</td>
      <td>13.4M</td>
      <td>12.3G</td>
      <td>317K</td>
      <td>45.3K</td>
      <td>20150608</td>
      <td>4 min 34 s</td>
      <td>408911</td>
    </tr>
    <tr>
      <th>1146</th>
      <td>gyotaku_the_ancient_japanese_art_of_printing_f...</td>
      <td>9.13M</td>
      <td>12.3G</td>
      <td>406K</td>
      <td>45.2K</td>
      <td>20130530</td>
      <td>3 min 37 s</td>
      <td>352680</td>
    </tr>
    <tr>
      <th>1147</th>
      <td>what_is_an_aurora_michael_molina</td>
      <td>12.8M</td>
      <td>12.3G</td>
      <td>402K</td>
      <td>44.6K</td>
      <td>20130703</td>
      <td>4 min 9 s</td>
      <td>431851</td>
    </tr>
    <tr>
      <th>1148</th>
      <td>how_ancient_art_influenced_modern_art_felipe_g...</td>
      <td>13.9M</td>
      <td>12.3G</td>
      <td>268K</td>
      <td>44.6K</td>
      <td>20160225</td>
      <td>4 min 50 s</td>
      <td>402937</td>
    </tr>
    <tr>
      <th>1149</th>
      <td>the_contributions_of_female_explorers_courtney...</td>
      <td>9.09M</td>
      <td>12.3G</td>
      <td>399K</td>
      <td>44.4K</td>
      <td>20130612</td>
      <td>4 min 25 s</td>
      <td>287489</td>
    </tr>
    <tr>
      <th>1150</th>
      <td>the_physics_of_playing_guitar_oscar_fernando_p...</td>
      <td>15.3M</td>
      <td>12.3G</td>
      <td>306K</td>
      <td>43.7K</td>
      <td>20150813</td>
      <td>4 min 54 s</td>
      <td>434227</td>
    </tr>
    <tr>
      <th>1151</th>
      <td>fresh_water_scarcity_an_introduction_to_the_pr...</td>
      <td>4.98M</td>
      <td>12.3G</td>
      <td>392K</td>
      <td>43.5K</td>
      <td>20130214</td>
      <td>3 min 38 s</td>
      <td>191013</td>
    </tr>
    <tr>
      <th>1152</th>
      <td>attack_of_the_killer_algae_eric_noel_munoz</td>
      <td>7.21M</td>
      <td>12.3G</td>
      <td>348K</td>
      <td>43.5K</td>
      <td>20140624</td>
      <td>3 min 23 s</td>
      <td>297125</td>
    </tr>
    <tr>
      <th>1153</th>
      <td>three_months_after_by_cristin_o_keefe_aptowicz</td>
      <td>2.85M</td>
      <td>12.3G</td>
      <td>129K</td>
      <td>43.1K</td>
      <td>20190202</td>
      <td>1 min 24 s</td>
      <td>281973</td>
    </tr>
    <tr>
      <th>1154</th>
      <td>the_poet_who_painted_with_his_words_genevieve_emy</td>
      <td>8.16M</td>
      <td>12.3G</td>
      <td>258K</td>
      <td>42.9K</td>
      <td>20160321</td>
      <td>4 min 15 s</td>
      <td>267820</td>
    </tr>
    <tr>
      <th>1155</th>
      <td>the_fundamental_theorem_of_arithmetic_computer...</td>
      <td>8.53M</td>
      <td>12.4G</td>
      <td>429K</td>
      <td>42.9K</td>
      <td>20120327</td>
      <td>3 min 51 s</td>
      <td>309353</td>
    </tr>
    <tr>
      <th>1156</th>
      <td>a_needle_in_countless_haystacks_finding_habita...</td>
      <td>15.8M</td>
      <td>12.4G</td>
      <td>386K</td>
      <td>42.9K</td>
      <td>20121108</td>
      <td>5 min 10 s</td>
      <td>426963</td>
    </tr>
    <tr>
      <th>1157</th>
      <td>how_does_an_atom_smashing_particle_accelerator...</td>
      <td>6.99M</td>
      <td>12.4G</td>
      <td>385K</td>
      <td>42.8K</td>
      <td>20130418</td>
      <td>3 min 35 s</td>
      <td>272013</td>
    </tr>
    <tr>
      <th>1158</th>
      <td>how_spontaneous_brain_activity_keeps_you_alive...</td>
      <td>9.08M</td>
      <td>12.4G</td>
      <td>298K</td>
      <td>42.6K</td>
      <td>20150113</td>
      <td>5 min 17 s</td>
      <td>239599</td>
    </tr>
    <tr>
      <th>1159</th>
      <td>forget_shopping_soon_you_ll_download_your_new_...</td>
      <td>16.3M</td>
      <td>12.4G</td>
      <td>254K</td>
      <td>42.3K</td>
      <td>20151217</td>
      <td>6 min 22 s</td>
      <td>357099</td>
    </tr>
    <tr>
      <th>1160</th>
      <td>how_science_fiction_can_help_predict_the_futur...</td>
      <td>17.6M</td>
      <td>12.4G</td>
      <td>254K</td>
      <td>42.3K</td>
      <td>20160126</td>
      <td>5 min 21 s</td>
      <td>458576</td>
    </tr>
    <tr>
      <th>1161</th>
      <td>the_world_s_english_mania_jay_walker</td>
      <td>10.2M</td>
      <td>12.4G</td>
      <td>375K</td>
      <td>41.7K</td>
      <td>20130301</td>
      <td>4 min 31 s</td>
      <td>315837</td>
    </tr>
    <tr>
      <th>1162</th>
      <td>cicadas_the_dormant_army_beneath_your_feet_ros...</td>
      <td>5.00M</td>
      <td>12.4G</td>
      <td>375K</td>
      <td>41.7K</td>
      <td>20130905</td>
      <td>2 min 45 s</td>
      <td>254070</td>
    </tr>
    <tr>
      <th>1163</th>
      <td>gravity_and_the_human_body_jay_buckey</td>
      <td>7.82M</td>
      <td>12.4G</td>
      <td>375K</td>
      <td>41.6K</td>
      <td>20130826</td>
      <td>4 min 45 s</td>
      <td>229721</td>
    </tr>
    <tr>
      <th>1164</th>
      <td>how_to_speak_monkey_the_language_of_cotton_top...</td>
      <td>11.5M</td>
      <td>12.5G</td>
      <td>332K</td>
      <td>41.5K</td>
      <td>20140626</td>
      <td>5 min 13 s</td>
      <td>306784</td>
    </tr>
    <tr>
      <th>1165</th>
      <td>haptography_digitizing_our_sense_of_touch_kath...</td>
      <td>13.9M</td>
      <td>12.5G</td>
      <td>373K</td>
      <td>41.4K</td>
      <td>20130325</td>
      <td>6 min 28 s</td>
      <td>299471</td>
    </tr>
    <tr>
      <th>1166</th>
      <td>the_chemistry_of_cold_packs_john_pollard</td>
      <td>8.04M</td>
      <td>12.5G</td>
      <td>330K</td>
      <td>41.3K</td>
      <td>20140911</td>
      <td>4 min 31 s</td>
      <td>248649</td>
    </tr>
    <tr>
      <th>1167</th>
      <td>the_science_of_macaroni_salad_what_s_in_a_mixt...</td>
      <td>7.48M</td>
      <td>12.5G</td>
      <td>368K</td>
      <td>40.9K</td>
      <td>20130731</td>
      <td>3 min 56 s</td>
      <td>265113</td>
    </tr>
    <tr>
      <th>1168</th>
      <td>a_poetic_experiment_walt_whitman_interpreted_b...</td>
      <td>10.1M</td>
      <td>12.5G</td>
      <td>286K</td>
      <td>40.9K</td>
      <td>20150820</td>
      <td>3 min 28 s</td>
      <td>408406</td>
    </tr>
    <tr>
      <th>1169</th>
      <td>how_to_turn_protest_into_powerful_change_eric_liu</td>
      <td>10.0M</td>
      <td>12.5G</td>
      <td>242K</td>
      <td>40.4K</td>
      <td>20160714</td>
      <td>4 min 56 s</td>
      <td>283482</td>
    </tr>
    <tr>
      <th>1170</th>
      <td>ted_ed_website_tour</td>
      <td>7.12M</td>
      <td>12.5G</td>
      <td>401K</td>
      <td>40.1K</td>
      <td>20120425</td>
      <td>3 min 7 s</td>
      <td>318764</td>
    </tr>
    <tr>
      <th>1171</th>
      <td>learn_to_read_chinese_with_ease_shaolan</td>
      <td>8.99M</td>
      <td>12.5G</td>
      <td>318K</td>
      <td>39.7K</td>
      <td>20131203</td>
      <td>6 min 14 s</td>
      <td>201682</td>
    </tr>
    <tr>
      <th>1172</th>
      <td>lessons_from_auschwitz_the_power_of_our_words_...</td>
      <td>3.24M</td>
      <td>12.5G</td>
      <td>318K</td>
      <td>39.7K</td>
      <td>20140425</td>
      <td>1 min 20 s</td>
      <td>337558</td>
    </tr>
    <tr>
      <th>1173</th>
      <td>the_invisible_motion_of_still_objects_ran_tivony</td>
      <td>10.6M</td>
      <td>12.5G</td>
      <td>238K</td>
      <td>39.6K</td>
      <td>20160324</td>
      <td>4 min 43 s</td>
      <td>312520</td>
    </tr>
    <tr>
      <th>1174</th>
      <td>shakespearean_dating_tips_anthony_john_peters</td>
      <td>4.48M</td>
      <td>12.5G</td>
      <td>356K</td>
      <td>39.6K</td>
      <td>20130822</td>
      <td>2 min 24 s</td>
      <td>261043</td>
    </tr>
    <tr>
      <th>1175</th>
      <td>the_case_against_good_and_bad_marlee_neel</td>
      <td>10.4M</td>
      <td>12.5G</td>
      <td>396K</td>
      <td>39.6K</td>
      <td>20120709</td>
      <td>4 min 52 s</td>
      <td>298091</td>
    </tr>
    <tr>
      <th>1176</th>
      <td>how_algorithms_shape_our_world_kevin_slavin</td>
      <td>37.2M</td>
      <td>12.6G</td>
      <td>356K</td>
      <td>39.6K</td>
      <td>20121125</td>
      <td>15 min 23 s</td>
      <td>338300</td>
    </tr>
    <tr>
      <th>1177</th>
      <td>an_introduction_to_mathematical_theorems_scott...</td>
      <td>9.47M</td>
      <td>12.6G</td>
      <td>384K</td>
      <td>38.4K</td>
      <td>20120910</td>
      <td>4 min 38 s</td>
      <td>285345</td>
    </tr>
    <tr>
      <th>1178</th>
      <td>could_a_blind_eye_regenerate_david_davila</td>
      <td>8.95M</td>
      <td>12.6G</td>
      <td>266K</td>
      <td>38.0K</td>
      <td>20150115</td>
      <td>4 min 6 s</td>
      <td>304160</td>
    </tr>
    <tr>
      <th>1179</th>
      <td>illuminating_photography_from_camera_obscura_t...</td>
      <td>7.92M</td>
      <td>12.6G</td>
      <td>341K</td>
      <td>37.9K</td>
      <td>20130228</td>
      <td>4 min 49 s</td>
      <td>229619</td>
    </tr>
    <tr>
      <th>1180</th>
      <td>disappearing_frogs_kerry_m_kriger</td>
      <td>5.68M</td>
      <td>12.6G</td>
      <td>300K</td>
      <td>37.6K</td>
      <td>20130916</td>
      <td>3 min 47 s</td>
      <td>209838</td>
    </tr>
    <tr>
      <th>1181</th>
      <td>why_do_americans_vote_on_tuesdays</td>
      <td>7.96M</td>
      <td>12.6G</td>
      <td>375K</td>
      <td>37.5K</td>
      <td>20120410</td>
      <td>3 min 27 s</td>
      <td>322153</td>
    </tr>
    <tr>
      <th>1182</th>
      <td>how_containerization_shaped_the_modern_world</td>
      <td>11.4M</td>
      <td>12.6G</td>
      <td>374K</td>
      <td>37.4K</td>
      <td>20120311</td>
      <td>4 min 46 s</td>
      <td>333944</td>
    </tr>
    <tr>
      <th>1183</th>
      <td>what_cameras_see_that_our_eyes_don_t_bill_shri...</td>
      <td>6.84M</td>
      <td>12.6G</td>
      <td>336K</td>
      <td>37.3K</td>
      <td>20130410</td>
      <td>3 min 19 s</td>
      <td>287253</td>
    </tr>
    <tr>
      <th>1184</th>
      <td>how_bacteria_talk_bonnie_bassler</td>
      <td>40.1M</td>
      <td>12.7G</td>
      <td>334K</td>
      <td>37.1K</td>
      <td>20130209</td>
      <td>18 min 11 s</td>
      <td>308585</td>
    </tr>
    <tr>
      <th>1185</th>
      <td>what_did_dogs_teach_humans_about_diabetes_dunc...</td>
      <td>6.39M</td>
      <td>12.7G</td>
      <td>295K</td>
      <td>36.8K</td>
      <td>20140828</td>
      <td>3 min 47 s</td>
      <td>236103</td>
    </tr>
    <tr>
      <th>1186</th>
      <td>why_do_americans_and_canadians_celebrate_labor...</td>
      <td>13.1M</td>
      <td>12.7G</td>
      <td>328K</td>
      <td>36.4K</td>
      <td>20130830</td>
      <td>4 min 12 s</td>
      <td>436499</td>
    </tr>
    <tr>
      <th>1187</th>
      <td>ideasthesia_how_do_ideas_feel_danko_nikolic</td>
      <td>8.36M</td>
      <td>12.7G</td>
      <td>254K</td>
      <td>36.2K</td>
      <td>20141106</td>
      <td>5 min 37 s</td>
      <td>207704</td>
    </tr>
    <tr>
      <th>1188</th>
      <td>the_best_stats_you_ve_ever_seen_hans_rosling</td>
      <td>36.0M</td>
      <td>12.7G</td>
      <td>322K</td>
      <td>35.8K</td>
      <td>20130713</td>
      <td>19 min 53 s</td>
      <td>252895</td>
    </tr>
    <tr>
      <th>1189</th>
      <td>how_plants_tell_time_dasha_savage</td>
      <td>7.16M</td>
      <td>12.7G</td>
      <td>250K</td>
      <td>35.7K</td>
      <td>20150611</td>
      <td>4 min 19 s</td>
      <td>231754</td>
    </tr>
    <tr>
      <th>1190</th>
      <td>under_the_hood_the_chemistry_of_cars_cynthia_c...</td>
      <td>6.16M</td>
      <td>12.8G</td>
      <td>282K</td>
      <td>35.2K</td>
      <td>20140724</td>
      <td>4 min 33 s</td>
      <td>188475</td>
    </tr>
    <tr>
      <th>1191</th>
      <td>where_we_get_our_fresh_water_christiana_z_peppard</td>
      <td>6.66M</td>
      <td>12.8G</td>
      <td>314K</td>
      <td>34.9K</td>
      <td>20130212</td>
      <td>3 min 46 s</td>
      <td>247068</td>
    </tr>
    <tr>
      <th>1192</th>
      <td>rapid_prototyping_google_glass_tom_chi</td>
      <td>19.1M</td>
      <td>12.8G</td>
      <td>314K</td>
      <td>34.9K</td>
      <td>20130122</td>
      <td>8 min 8 s</td>
      <td>328481</td>
    </tr>
    <tr>
      <th>1193</th>
      <td>the_twisting_tale_of_dna_judith_hauck</td>
      <td>12.6M</td>
      <td>12.8G</td>
      <td>313K</td>
      <td>34.8K</td>
      <td>20121003</td>
      <td>4 min 26 s</td>
      <td>396889</td>
    </tr>
    <tr>
      <th>1194</th>
      <td>how_does_math_guide_our_ships_at_sea_george_ch...</td>
      <td>9.91M</td>
      <td>12.8G</td>
      <td>309K</td>
      <td>34.3K</td>
      <td>20121011</td>
      <td>4 min 18 s</td>
      <td>320904</td>
    </tr>
    <tr>
      <th>1195</th>
      <td>the_time_value_of_money_german_nande</td>
      <td>5.93M</td>
      <td>12.8G</td>
      <td>268K</td>
      <td>33.5K</td>
      <td>20140703</td>
      <td>3 min 36 s</td>
      <td>229641</td>
    </tr>
    <tr>
      <th>1196</th>
      <td>where_did_the_earth_come_from</td>
      <td>10.5M</td>
      <td>12.8G</td>
      <td>367K</td>
      <td>33.4K</td>
      <td>20110512</td>
      <td>3 min 56 s</td>
      <td>370343</td>
    </tr>
    <tr>
      <th>1197</th>
      <td>how_do_nerves_work_elliot_krane</td>
      <td>11.9M</td>
      <td>12.8G</td>
      <td>332K</td>
      <td>33.2K</td>
      <td>20120809</td>
      <td>4 min 59 s</td>
      <td>334445</td>
    </tr>
    <tr>
      <th>1198</th>
      <td>is_space_trying_to_kill_us_ron_shaneyfelt</td>
      <td>6.67M</td>
      <td>12.8G</td>
      <td>295K</td>
      <td>32.8K</td>
      <td>20130528</td>
      <td>3 min 30 s</td>
      <td>265918</td>
    </tr>
    <tr>
      <th>1199</th>
      <td>the_cancer_gene_we_all_have_michael_windelspecht</td>
      <td>6.82M</td>
      <td>12.8G</td>
      <td>261K</td>
      <td>32.6K</td>
      <td>20140519</td>
      <td>3 min 18 s</td>
      <td>288044</td>
    </tr>
    <tr>
      <th>1200</th>
      <td>the_great_brain_debate_ted_altschuler</td>
      <td>13.4M</td>
      <td>12.9G</td>
      <td>227K</td>
      <td>32.4K</td>
      <td>20141117</td>
      <td>5 min 19 s</td>
      <td>352426</td>
    </tr>
    <tr>
      <th>1201</th>
      <td>all_of_the_energy_in_the_universe_is_george_za...</td>
      <td>10.7M</td>
      <td>12.9G</td>
      <td>258K</td>
      <td>32.2K</td>
      <td>20131112</td>
      <td>3 min 51 s</td>
      <td>389272</td>
    </tr>
    <tr>
      <th>1202</th>
      <td>making_sense_of_spelling_gina_cooke</td>
      <td>6.93M</td>
      <td>12.9G</td>
      <td>289K</td>
      <td>32.1K</td>
      <td>20120925</td>
      <td>4 min 18 s</td>
      <td>225193</td>
    </tr>
    <tr>
      <th>1203</th>
      <td>from_aaliyah_to_jay_z_captured_moments_in_hip_...</td>
      <td>12.2M</td>
      <td>12.9G</td>
      <td>254K</td>
      <td>31.7K</td>
      <td>20140515</td>
      <td>6 min 20 s</td>
      <td>269385</td>
    </tr>
    <tr>
      <th>1204</th>
      <td>let_s_make_history_by_recording_it_storycorps_...</td>
      <td>7.31M</td>
      <td>12.9G</td>
      <td>190K</td>
      <td>31.6K</td>
      <td>20151123</td>
      <td>3 min 17 s</td>
      <td>309669</td>
    </tr>
    <tr>
      <th>1205</th>
      <td>how_life_begins_in_the_deep_ocean</td>
      <td>18.1M</td>
      <td>12.9G</td>
      <td>316K</td>
      <td>31.6K</td>
      <td>20120514</td>
      <td>6 min 1 s</td>
      <td>418860</td>
    </tr>
    <tr>
      <th>1206</th>
      <td>what_we_can_learn_from_galaxies_far_far_away_h...</td>
      <td>13.7M</td>
      <td>12.9G</td>
      <td>247K</td>
      <td>30.8K</td>
      <td>20140227</td>
      <td>6 min 43 s</td>
      <td>285138</td>
    </tr>
    <tr>
      <th>1207</th>
      <td>the_world_needs_all_kinds_of_minds_temple_grandin</td>
      <td>48.2M</td>
      <td>13.0G</td>
      <td>276K</td>
      <td>30.7K</td>
      <td>20130210</td>
      <td>19 min 43 s</td>
      <td>341717</td>
    </tr>
    <tr>
      <th>1208</th>
      <td>the_history_of_our_world_in_18_minutes_david_c...</td>
      <td>35.7M</td>
      <td>13.0G</td>
      <td>274K</td>
      <td>30.4K</td>
      <td>20130315</td>
      <td>17 min 40 s</td>
      <td>282719</td>
    </tr>
    <tr>
      <th>1209</th>
      <td>the_hidden_worlds_within_natural_history_museu...</td>
      <td>7.12M</td>
      <td>13.0G</td>
      <td>212K</td>
      <td>30.2K</td>
      <td>20141202</td>
      <td>4 min 26 s</td>
      <td>223802</td>
    </tr>
    <tr>
      <th>1210</th>
      <td>how_to_think_about_gravity_jon_bergmann</td>
      <td>8.26M</td>
      <td>13.0G</td>
      <td>272K</td>
      <td>30.2K</td>
      <td>20120917</td>
      <td>4 min 43 s</td>
      <td>244111</td>
    </tr>
    <tr>
      <th>1211</th>
      <td>what_light_can_teach_us_about_the_universe_pet...</td>
      <td>10.5M</td>
      <td>13.0G</td>
      <td>236K</td>
      <td>29.6K</td>
      <td>20140731</td>
      <td>4 min 6 s</td>
      <td>358098</td>
    </tr>
    <tr>
      <th>1212</th>
      <td>rnai_slicing_dicing_and_serving_your_cells_ale...</td>
      <td>7.38M</td>
      <td>13.0G</td>
      <td>262K</td>
      <td>29.1K</td>
      <td>20130812</td>
      <td>4 min 7 s</td>
      <td>250092</td>
    </tr>
    <tr>
      <th>1213</th>
      <td>the_carbon_cycle_nathaniel_manning</td>
      <td>9.35M</td>
      <td>13.0G</td>
      <td>260K</td>
      <td>28.9K</td>
      <td>20121002</td>
      <td>3 min 54 s</td>
      <td>334483</td>
    </tr>
    <tr>
      <th>1214</th>
      <td>what_is_the_shape_of_a_molecule_george_zaidan_...</td>
      <td>5.74M</td>
      <td>13.0G</td>
      <td>231K</td>
      <td>28.9K</td>
      <td>20131017</td>
      <td>3 min 47 s</td>
      <td>211980</td>
    </tr>
    <tr>
      <th>1215</th>
      <td>poetic_stickup_put_the_financial_aid_in_the_bag</td>
      <td>11.9M</td>
      <td>13.1G</td>
      <td>286K</td>
      <td>28.6K</td>
      <td>20120321</td>
      <td>5 min 4 s</td>
      <td>326385</td>
    </tr>
    <tr>
      <th>1216</th>
      <td>how_the_language_you_speak_affects_your_thoughts</td>
      <td>16.7M</td>
      <td>13.1G</td>
      <td>143K</td>
      <td>28.6K</td>
      <td>20170427</td>
      <td>8 min 45 s</td>
      <td>266569</td>
    </tr>
    <tr>
      <th>1217</th>
      <td>dear_subscribers</td>
      <td>8.46M</td>
      <td>13.1G</td>
      <td>255K</td>
      <td>28.3K</td>
      <td>20130319</td>
      <td>2 min 42 s</td>
      <td>435543</td>
    </tr>
    <tr>
      <th>1218</th>
      <td>diagnosing_a_zombie_brain_and_behavior_part_tw...</td>
      <td>6.01M</td>
      <td>13.1G</td>
      <td>253K</td>
      <td>28.1K</td>
      <td>20121024</td>
      <td>3 min 43 s</td>
      <td>225552</td>
    </tr>
    <tr>
      <th>1219</th>
      <td>would_you_weigh_less_in_an_elevator_carol_hedden</td>
      <td>8.40M</td>
      <td>13.1G</td>
      <td>252K</td>
      <td>28.0K</td>
      <td>20121119</td>
      <td>3 min 35 s</td>
      <td>326830</td>
    </tr>
    <tr>
      <th>1220</th>
      <td>how_breathing_works_nirvair_kaur</td>
      <td>10.1M</td>
      <td>13.1G</td>
      <td>252K</td>
      <td>28.0K</td>
      <td>20121004</td>
      <td>5 min 18 s</td>
      <td>267174</td>
    </tr>
    <tr>
      <th>1221</th>
      <td>et_is_probably_out_there_get_ready_seth_shostak</td>
      <td>31.7M</td>
      <td>13.1G</td>
      <td>252K</td>
      <td>28.0K</td>
      <td>20130821</td>
      <td>18 min 40 s</td>
      <td>236910</td>
    </tr>
    <tr>
      <th>1222</th>
      <td>a_curable_condition_that_causes_blindness_andr...</td>
      <td>5.69M</td>
      <td>13.1G</td>
      <td>167K</td>
      <td>27.8K</td>
      <td>20150928</td>
      <td>4 min 22 s</td>
      <td>182240</td>
    </tr>
    <tr>
      <th>1223</th>
      <td>the_nurdles_quest_for_ocean_domination_kim_pre...</td>
      <td>9.76M</td>
      <td>13.2G</td>
      <td>221K</td>
      <td>27.6K</td>
      <td>20140804</td>
      <td>4 min 54 s</td>
      <td>278230</td>
    </tr>
    <tr>
      <th>1224</th>
      <td>who_controls_the_world_james_b_glattfelder</td>
      <td>25.8M</td>
      <td>13.2G</td>
      <td>245K</td>
      <td>27.2K</td>
      <td>20130515</td>
      <td>14 min 10 s</td>
      <td>254057</td>
    </tr>
    <tr>
      <th>1225</th>
      <td>let_s_talk_about_dying_peter_saul</td>
      <td>22.7M</td>
      <td>13.2G</td>
      <td>242K</td>
      <td>26.9K</td>
      <td>20130609</td>
      <td>13 min 19 s</td>
      <td>237867</td>
    </tr>
    <tr>
      <th>1226</th>
      <td>the_secret_lives_of_baby_fish_amy_mcdermott</td>
      <td>10.4M</td>
      <td>13.2G</td>
      <td>211K</td>
      <td>26.4K</td>
      <td>20140811</td>
      <td>3 min 58 s</td>
      <td>366549</td>
    </tr>
    <tr>
      <th>1227</th>
      <td>who_is_alexander_von_humboldt_george_mehler</td>
      <td>9.36M</td>
      <td>13.2G</td>
      <td>238K</td>
      <td>26.4K</td>
      <td>20130402</td>
      <td>4 min 21 s</td>
      <td>300395</td>
    </tr>
    <tr>
      <th>1228</th>
      <td>india_s_invisible_innovation_nirmalya_kumar</td>
      <td>24.6M</td>
      <td>13.2G</td>
      <td>235K</td>
      <td>26.1K</td>
      <td>20130821</td>
      <td>15 min 12 s</td>
      <td>226136</td>
    </tr>
    <tr>
      <th>1229</th>
      <td>why_i_m_a_weekday_vegetarian_graham_hill</td>
      <td>8.79M</td>
      <td>13.3G</td>
      <td>233K</td>
      <td>25.9K</td>
      <td>20130222</td>
      <td>4 min 4 s</td>
      <td>301646</td>
    </tr>
    <tr>
      <th>1230</th>
      <td>making_a_ted_ed_lesson_visualizing_big_ideas</td>
      <td>10.7M</td>
      <td>13.3G</td>
      <td>207K</td>
      <td>25.9K</td>
      <td>20131125</td>
      <td>5 min 3 s</td>
      <td>296649</td>
    </tr>
    <tr>
      <th>1231</th>
      <td>if_superpowers_were_real_which_would_you_choos...</td>
      <td>6.26M</td>
      <td>13.3G</td>
      <td>230K</td>
      <td>25.6K</td>
      <td>20130627</td>
      <td>2 min 21 s</td>
      <td>371856</td>
    </tr>
    <tr>
      <th>1232</th>
      <td>how_to_detect_a_supernova_samantha_kuula</td>
      <td>10.5M</td>
      <td>13.3G</td>
      <td>178K</td>
      <td>25.4K</td>
      <td>20150609</td>
      <td>4 min 41 s</td>
      <td>313972</td>
    </tr>
    <tr>
      <th>1233</th>
      <td>symbiosis_a_surprising_tale_of_species_coopera...</td>
      <td>6.18M</td>
      <td>13.3G</td>
      <td>251K</td>
      <td>25.1K</td>
      <td>20120313</td>
      <td>2 min 22 s</td>
      <td>362835</td>
    </tr>
    <tr>
      <th>1234</th>
      <td>how_i_discovered_dna_james_watson</td>
      <td>34.2M</td>
      <td>13.3G</td>
      <td>222K</td>
      <td>24.7K</td>
      <td>20130726</td>
      <td>20 min 14 s</td>
      <td>236598</td>
    </tr>
    <tr>
      <th>1235</th>
      <td>want_to_be_an_activist_start_with_your_toys_mc...</td>
      <td>15.9M</td>
      <td>13.3G</td>
      <td>197K</td>
      <td>24.6K</td>
      <td>20140129</td>
      <td>5 min 21 s</td>
      <td>414447</td>
    </tr>
    <tr>
      <th>1236</th>
      <td>how_movies_teach_manhood_colin_stokes</td>
      <td>23.3M</td>
      <td>13.4G</td>
      <td>219K</td>
      <td>24.3K</td>
      <td>20130522</td>
      <td>12 min 56 s</td>
      <td>251534</td>
    </tr>
    <tr>
      <th>1237</th>
      <td>what_is_chirality_and_how_did_it_get_in_my_mol...</td>
      <td>8.29M</td>
      <td>13.4G</td>
      <td>217K</td>
      <td>24.1K</td>
      <td>20120920</td>
      <td>5 min 4 s</td>
      <td>228349</td>
    </tr>
    <tr>
      <th>1238</th>
      <td>from_dna_to_silly_putty_the_diverse_world_of_p...</td>
      <td>13.1M</td>
      <td>13.4G</td>
      <td>192K</td>
      <td>24.0K</td>
      <td>20131210</td>
      <td>4 min 59 s</td>
      <td>366441</td>
    </tr>
    <tr>
      <th>1239</th>
      <td>how_does_work_work_peter_bohacek</td>
      <td>13.5M</td>
      <td>13.4G</td>
      <td>215K</td>
      <td>23.9K</td>
      <td>20121129</td>
      <td>4 min 30 s</td>
      <td>419040</td>
    </tr>
    <tr>
      <th>1240</th>
      <td>mysteries_of_vernacular_odd_jessica_oreck_and_...</td>
      <td>2.67M</td>
      <td>13.4G</td>
      <td>190K</td>
      <td>23.7K</td>
      <td>20131205</td>
      <td>1 min 51 s</td>
      <td>200475</td>
    </tr>
    <tr>
      <th>1241</th>
      <td>the_game_changing_amniotic_egg_april_tucker</td>
      <td>10.7M</td>
      <td>13.4G</td>
      <td>208K</td>
      <td>23.1K</td>
      <td>20130618</td>
      <td>4 min 29 s</td>
      <td>333432</td>
    </tr>
    <tr>
      <th>1242</th>
      <td>beach_bodies_in_spoken_word_david_fasanya_and_...</td>
      <td>11.1M</td>
      <td>13.4G</td>
      <td>207K</td>
      <td>22.9K</td>
      <td>20130227</td>
      <td>3 min 32 s</td>
      <td>437175</td>
    </tr>
    <tr>
      <th>1243</th>
      <td>equality_sports_and_title_ix_erin_buzuvis_and_...</td>
      <td>9.10M</td>
      <td>13.4G</td>
      <td>204K</td>
      <td>22.6K</td>
      <td>20130619</td>
      <td>4 min 34 s</td>
      <td>277886</td>
    </tr>
    <tr>
      <th>1244</th>
      <td>is_our_climate_headed_for_a_mathematical_tippi...</td>
      <td>8.10M</td>
      <td>13.4G</td>
      <td>158K</td>
      <td>22.6K</td>
      <td>20141023</td>
      <td>4 min 10 s</td>
      <td>271567</td>
    </tr>
    <tr>
      <th>1245</th>
      <td>making_waves_the_power_of_concentration_gradie...</td>
      <td>9.82M</td>
      <td>13.4G</td>
      <td>178K</td>
      <td>22.3K</td>
      <td>20140304</td>
      <td>5 min 19 s</td>
      <td>257914</td>
    </tr>
    <tr>
      <th>1246</th>
      <td>the_surprising_and_invisible_signatures_of_sea...</td>
      <td>19.3M</td>
      <td>13.5G</td>
      <td>133K</td>
      <td>22.2K</td>
      <td>20160107</td>
      <td>6 min 37 s</td>
      <td>407343</td>
    </tr>
    <tr>
      <th>1247</th>
      <td>cloudy_climate_change_how_clouds_affect_earth_...</td>
      <td>19.7M</td>
      <td>13.5G</td>
      <td>154K</td>
      <td>22.0K</td>
      <td>20140925</td>
      <td>6 min 39 s</td>
      <td>414388</td>
    </tr>
    <tr>
      <th>1248</th>
      <td>a_host_of_heroes_april_gudenrath</td>
      <td>13.9M</td>
      <td>13.5G</td>
      <td>197K</td>
      <td>21.9K</td>
      <td>20130429</td>
      <td>4 min 53 s</td>
      <td>396469</td>
    </tr>
    <tr>
      <th>1249</th>
      <td>mining_literature_for_deeper_meanings_amy_e_ha...</td>
      <td>7.89M</td>
      <td>13.5G</td>
      <td>196K</td>
      <td>21.8K</td>
      <td>20130531</td>
      <td>4 min 12 s</td>
      <td>262178</td>
    </tr>
    <tr>
      <th>1250</th>
      <td>the_science_of_macaroni_salad_what_s_in_a_mole...</td>
      <td>7.34M</td>
      <td>13.5G</td>
      <td>194K</td>
      <td>21.6K</td>
      <td>20130816</td>
      <td>3 min 14 s</td>
      <td>316079</td>
    </tr>
    <tr>
      <th>1251</th>
      <td>the_key_to_media_s_hidden_codes_ben_beaton</td>
      <td>19.2M</td>
      <td>13.5G</td>
      <td>214K</td>
      <td>21.4K</td>
      <td>20120529</td>
      <td>5 min 59 s</td>
      <td>449016</td>
    </tr>
    <tr>
      <th>1252</th>
      <td>the_tribes_we_lead_seth_godin</td>
      <td>34.8M</td>
      <td>13.6G</td>
      <td>190K</td>
      <td>21.1K</td>
      <td>20130303</td>
      <td>17 min 26 s</td>
      <td>279202</td>
    </tr>
    <tr>
      <th>1253</th>
      <td>why_the_arctic_is_climate_change_s_canary_in_t...</td>
      <td>7.75M</td>
      <td>13.6G</td>
      <td>147K</td>
      <td>21.1K</td>
      <td>20150122</td>
      <td>3 min 58 s</td>
      <td>272129</td>
    </tr>
    <tr>
      <th>1254</th>
      <td>the_oddities_of_the_first_american_election_ke...</td>
      <td>14.8M</td>
      <td>13.6G</td>
      <td>188K</td>
      <td>20.8K</td>
      <td>20121105</td>
      <td>4 min 6 s</td>
      <td>502147</td>
    </tr>
    <tr>
      <th>1255</th>
      <td>write_your_story_change_history_brad_meltzer</td>
      <td>14.9M</td>
      <td>13.6G</td>
      <td>186K</td>
      <td>20.7K</td>
      <td>20130116</td>
      <td>8 min 57 s</td>
      <td>232021</td>
    </tr>
    <tr>
      <th>1256</th>
      <td>beatboxing_101_beat_nyc</td>
      <td>20.4M</td>
      <td>13.6G</td>
      <td>186K</td>
      <td>20.7K</td>
      <td>20130702</td>
      <td>6 min 8 s</td>
      <td>464645</td>
    </tr>
    <tr>
      <th>1257</th>
      <td>how_to_fool_a_gps_todd_humphreys</td>
      <td>29.0M</td>
      <td>13.6G</td>
      <td>183K</td>
      <td>20.4K</td>
      <td>20130626</td>
      <td>15 min 45 s</td>
      <td>257550</td>
    </tr>
    <tr>
      <th>1258</th>
      <td>making_sense_of_how_life_fits_together_bobbi_s...</td>
      <td>7.42M</td>
      <td>13.7G</td>
      <td>183K</td>
      <td>20.3K</td>
      <td>20130423</td>
      <td>4 min 52 s</td>
      <td>212755</td>
    </tr>
    <tr>
      <th>1259</th>
      <td>how_cosmic_rays_help_us_understand_the_univers...</td>
      <td>16.4M</td>
      <td>13.7G</td>
      <td>141K</td>
      <td>20.2K</td>
      <td>20140923</td>
      <td>4 min 39 s</td>
      <td>493159</td>
    </tr>
    <tr>
      <th>1260</th>
      <td>start_a_ted_ed_club_today</td>
      <td>4.62M</td>
      <td>13.7G</td>
      <td>160K</td>
      <td>20.0K</td>
      <td>20140114</td>
      <td>2 min 21 s</td>
      <td>274330</td>
    </tr>
    <tr>
      <th>1261</th>
      <td>how_social_media_can_make_history_clay_shirky</td>
      <td>31.6M</td>
      <td>13.7G</td>
      <td>180K</td>
      <td>20.0K</td>
      <td>20121116</td>
      <td>15 min 48 s</td>
      <td>279206</td>
    </tr>
    <tr>
      <th>1262</th>
      <td>how_to_stop_being_bored_and_start_being_bold</td>
      <td>29.8M</td>
      <td>13.7G</td>
      <td>79.7K</td>
      <td>19.9K</td>
      <td>20180126</td>
      <td>9 min 57 s</td>
      <td>418431</td>
    </tr>
    <tr>
      <th>1263</th>
      <td>bird_migration_a_perilous_journey_alyssa_klavans</td>
      <td>7.10M</td>
      <td>13.7G</td>
      <td>159K</td>
      <td>19.9K</td>
      <td>20130917</td>
      <td>4 min 9 s</td>
      <td>238688</td>
    </tr>
    <tr>
      <th>1264</th>
      <td>what_adults_can_learn_from_kids_adora_svitak</td>
      <td>16.5M</td>
      <td>13.8G</td>
      <td>176K</td>
      <td>19.6K</td>
      <td>20130222</td>
      <td>8 min 12 s</td>
      <td>280505</td>
    </tr>
    <tr>
      <th>1265</th>
      <td>insights_into_cell_membranes_via_dish_detergen...</td>
      <td>6.72M</td>
      <td>13.8G</td>
      <td>176K</td>
      <td>19.5K</td>
      <td>20130226</td>
      <td>3 min 49 s</td>
      <td>245953</td>
    </tr>
    <tr>
      <th>1266</th>
      <td>what_if_we_could_look_inside_human_brains_mora...</td>
      <td>13.9M</td>
      <td>13.8G</td>
      <td>175K</td>
      <td>19.5K</td>
      <td>20130131</td>
      <td>3 min 55 s</td>
      <td>496663</td>
    </tr>
    <tr>
      <th>1267</th>
      <td>pros_and_cons_of_public_opinion_polls_jason_ro...</td>
      <td>6.46M</td>
      <td>13.8G</td>
      <td>174K</td>
      <td>19.3K</td>
      <td>20130517</td>
      <td>4 min 24 s</td>
      <td>204720</td>
    </tr>
    <tr>
      <th>1268</th>
      <td>free_falling_in_outer_space_matt_j_carlson</td>
      <td>4.53M</td>
      <td>13.8G</td>
      <td>172K</td>
      <td>19.1K</td>
      <td>20130706</td>
      <td>2 min 58 s</td>
      <td>213123</td>
    </tr>
    <tr>
      <th>1269</th>
      <td>the_power_of_introverts_susan_cain</td>
      <td>35.7M</td>
      <td>13.8G</td>
      <td>172K</td>
      <td>19.1K</td>
      <td>20121225</td>
      <td>19 min 3 s</td>
      <td>261737</td>
    </tr>
    <tr>
      <th>1270</th>
      <td>network_theory_marc_samet</td>
      <td>6.86M</td>
      <td>13.8G</td>
      <td>171K</td>
      <td>19.0K</td>
      <td>20130123</td>
      <td>3 min 30 s</td>
      <td>273978</td>
    </tr>
    <tr>
      <th>1271</th>
      <td>stroke_of_insight_jill_bolte_taylor</td>
      <td>44.4M</td>
      <td>13.9G</td>
      <td>168K</td>
      <td>18.7K</td>
      <td>20121114</td>
      <td>18 min 41 s</td>
      <td>331900</td>
    </tr>
    <tr>
      <th>1272</th>
      <td>how_did_trains_standardize_time_in_the_united_...</td>
      <td>7.29M</td>
      <td>13.9G</td>
      <td>167K</td>
      <td>18.5K</td>
      <td>20130205</td>
      <td>3 min 34 s</td>
      <td>285247</td>
    </tr>
    <tr>
      <th>1273</th>
      <td>the_real_origin_of_the_franchise_sir_harold_evans</td>
      <td>16.9M</td>
      <td>13.9G</td>
      <td>185K</td>
      <td>18.5K</td>
      <td>20120326</td>
      <td>5 min 48 s</td>
      <td>406074</td>
    </tr>
    <tr>
      <th>1274</th>
      <td>networking_for_the_networking_averse_lisa_gree...</td>
      <td>7.31M</td>
      <td>13.9G</td>
      <td>166K</td>
      <td>18.5K</td>
      <td>20130403</td>
      <td>3 min 30 s</td>
      <td>290962</td>
    </tr>
    <tr>
      <th>1275</th>
      <td>rhythm_in_a_box_the_story_of_the_cajon_drum_pa...</td>
      <td>10.6M</td>
      <td>13.9G</td>
      <td>125K</td>
      <td>17.9K</td>
      <td>20150303</td>
      <td>3 min 29 s</td>
      <td>424252</td>
    </tr>
    <tr>
      <th>1276</th>
      <td>activation_energy_kickstarting_chemical_reacti...</td>
      <td>8.80M</td>
      <td>13.9G</td>
      <td>157K</td>
      <td>17.5K</td>
      <td>20130109</td>
      <td>3 min 22 s</td>
      <td>363656</td>
    </tr>
    <tr>
      <th>1277</th>
      <td>your_brain_on_video_games_daphne_bavelier</td>
      <td>28.8M</td>
      <td>14.0G</td>
      <td>156K</td>
      <td>17.3K</td>
      <td>20130327</td>
      <td>17 min 57 s</td>
      <td>224482</td>
    </tr>
    <tr>
      <th>1278</th>
      <td>speech_acts_constative_and_performative_collee...</td>
      <td>9.02M</td>
      <td>14.0G</td>
      <td>138K</td>
      <td>17.2K</td>
      <td>20131003</td>
      <td>3 min 57 s</td>
      <td>319395</td>
    </tr>
    <tr>
      <th>1279</th>
      <td>the_history_of_keeping_time_karen_mensing</td>
      <td>9.31M</td>
      <td>14.0G</td>
      <td>169K</td>
      <td>16.9K</td>
      <td>20120816</td>
      <td>3 min 47 s</td>
      <td>343231</td>
    </tr>
    <tr>
      <th>1280</th>
      <td>sunflowers_and_fibonacci_numberphile</td>
      <td>17.5M</td>
      <td>14.0G</td>
      <td>169K</td>
      <td>16.9K</td>
      <td>20120410</td>
      <td>5 min 25 s</td>
      <td>450142</td>
    </tr>
    <tr>
      <th>1281</th>
      <td>how_bees_help_plants_have_sex_fernanda_s_valdo...</td>
      <td>8.59M</td>
      <td>14.0G</td>
      <td>134K</td>
      <td>16.8K</td>
      <td>20140617</td>
      <td>5 min 25 s</td>
      <td>221673</td>
    </tr>
    <tr>
      <th>1282</th>
      <td>what_on_earth_is_spin_brian_jones</td>
      <td>12.1M</td>
      <td>14.0G</td>
      <td>148K</td>
      <td>16.5K</td>
      <td>20130529</td>
      <td>3 min 56 s</td>
      <td>430028</td>
    </tr>
    <tr>
      <th>1283</th>
      <td>the_happy_secret_to_better_work_shawn_achor</td>
      <td>23.2M</td>
      <td>14.0G</td>
      <td>147K</td>
      <td>16.3K</td>
      <td>20130616</td>
      <td>12 min 20 s</td>
      <td>262314</td>
    </tr>
    <tr>
      <th>1284</th>
      <td>could_comets_be_the_source_of_life_on_earth_ju...</td>
      <td>7.00M</td>
      <td>14.0G</td>
      <td>114K</td>
      <td>16.3K</td>
      <td>20141028</td>
      <td>3 min 37 s</td>
      <td>270026</td>
    </tr>
    <tr>
      <th>1285</th>
      <td>animation_basics_the_optical_illusion_of_motio...</td>
      <td>14.6M</td>
      <td>14.1G</td>
      <td>147K</td>
      <td>16.3K</td>
      <td>20130713</td>
      <td>5 min 11 s</td>
      <td>392709</td>
    </tr>
    <tr>
      <th>1286</th>
      <td>slowing_down_time_in_writing_film_aaron_sitze</td>
      <td>13.8M</td>
      <td>14.1G</td>
      <td>145K</td>
      <td>16.2K</td>
      <td>20130124</td>
      <td>5 min 59 s</td>
      <td>321535</td>
    </tr>
    <tr>
      <th>1287</th>
      <td>mosquitos_malaria_and_education_bill_gates</td>
      <td>61.1M</td>
      <td>14.1G</td>
      <td>145K</td>
      <td>16.2K</td>
      <td>20130222</td>
      <td>20 min 20 s</td>
      <td>420122</td>
    </tr>
    <tr>
      <th>1288</th>
      <td>the_magic_of_qr_codes_in_the_classroom_karen_m...</td>
      <td>8.90M</td>
      <td>14.1G</td>
      <td>143K</td>
      <td>15.9K</td>
      <td>20130620</td>
      <td>5 min 17 s</td>
      <td>235072</td>
    </tr>
    <tr>
      <th>1289</th>
      <td>how_life_came_to_land_tierney_thys</td>
      <td>17.8M</td>
      <td>14.1G</td>
      <td>142K</td>
      <td>15.7K</td>
      <td>20121107</td>
      <td>5 min 27 s</td>
      <td>455612</td>
    </tr>
    <tr>
      <th>1290</th>
      <td>inventing_the_american_presidency_kenneth_c_davis</td>
      <td>9.96M</td>
      <td>14.2G</td>
      <td>140K</td>
      <td>15.6K</td>
      <td>20130218</td>
      <td>4 min 0 s</td>
      <td>346818</td>
    </tr>
    <tr>
      <th>1291</th>
      <td>silk_the_ancient_material_of_the_future_fioren...</td>
      <td>15.9M</td>
      <td>14.2G</td>
      <td>139K</td>
      <td>15.4K</td>
      <td>20130322</td>
      <td>9 min 40 s</td>
      <td>229758</td>
    </tr>
    <tr>
      <th>1292</th>
      <td>my_glacier_cave_discoveries_eddy_cartaya</td>
      <td>16.7M</td>
      <td>14.2G</td>
      <td>123K</td>
      <td>15.3K</td>
      <td>20131211</td>
      <td>8 min 2 s</td>
      <td>290311</td>
    </tr>
    <tr>
      <th>1293</th>
      <td>the_abc_s_of_gas_avogadro_boyle_charles_brian_...</td>
      <td>6.01M</td>
      <td>14.2G</td>
      <td>137K</td>
      <td>15.2K</td>
      <td>20121009</td>
      <td>2 min 49 s</td>
      <td>297930</td>
    </tr>
    <tr>
      <th>1294</th>
      <td>a_trip_through_space_to_calculate_distance_hea...</td>
      <td>6.01M</td>
      <td>14.2G</td>
      <td>137K</td>
      <td>15.2K</td>
      <td>20130906</td>
      <td>3 min 46 s</td>
      <td>222492</td>
    </tr>
    <tr>
      <th>1295</th>
      <td>why_you_will_fail_to_have_a_great_career_larry...</td>
      <td>41.2M</td>
      <td>14.2G</td>
      <td>137K</td>
      <td>15.2K</td>
      <td>20130815</td>
      <td>15 min 15 s</td>
      <td>378045</td>
    </tr>
    <tr>
      <th>1296</th>
      <td>animation_basics_homemade_special_effects_ted_ed</td>
      <td>10.4M</td>
      <td>14.3G</td>
      <td>134K</td>
      <td>14.9K</td>
      <td>20130516</td>
      <td>4 min 18 s</td>
      <td>337018</td>
    </tr>
    <tr>
      <th>1297</th>
      <td>mysteries_of_vernacular_lady_jessica_oreck_and...</td>
      <td>2.94M</td>
      <td>14.3G</td>
      <td>119K</td>
      <td>14.9K</td>
      <td>20131121</td>
      <td>2 min 7 s</td>
      <td>193686</td>
    </tr>
    <tr>
      <th>1298</th>
      <td>euclid_s_puzzling_parallel_postulate_jeff_deko...</td>
      <td>6.13M</td>
      <td>14.3G</td>
      <td>132K</td>
      <td>14.7K</td>
      <td>20130326</td>
      <td>3 min 36 s</td>
      <td>238053</td>
    </tr>
    <tr>
      <th>1299</th>
      <td>let_s_talk_about_sex_john_bohannon_and_black_l...</td>
      <td>30.3M</td>
      <td>14.3G</td>
      <td>130K</td>
      <td>14.5K</td>
      <td>20121203</td>
      <td>10 min 42 s</td>
      <td>395814</td>
    </tr>
    <tr>
      <th>1300</th>
      <td>it_s_time_to_question_bio_engineering_paul_roo...</td>
      <td>29.3M</td>
      <td>14.3G</td>
      <td>130K</td>
      <td>14.4K</td>
      <td>20130815</td>
      <td>19 min 42 s</td>
      <td>207846</td>
    </tr>
    <tr>
      <th>1301</th>
      <td>evolution_in_a_big_city</td>
      <td>11.5M</td>
      <td>14.3G</td>
      <td>144K</td>
      <td>14.4K</td>
      <td>20120311</td>
      <td>5 min 15 s</td>
      <td>306060</td>
    </tr>
    <tr>
      <th>1302</th>
      <td>adhd_finding_what_works_for_me</td>
      <td>26.0M</td>
      <td>14.4G</td>
      <td>57.0K</td>
      <td>14.2K</td>
      <td>20180223</td>
      <td>12 min 1 s</td>
      <td>302943</td>
    </tr>
    <tr>
      <th>1303</th>
      <td>why_extremophiles_bode_well_for_life_beyond_ea...</td>
      <td>7.56M</td>
      <td>14.4G</td>
      <td>112K</td>
      <td>14.0K</td>
      <td>20131007</td>
      <td>3 min 59 s</td>
      <td>264157</td>
    </tr>
    <tr>
      <th>1304</th>
      <td>printing_a_human_kidney_anthony_atala</td>
      <td>39.3M</td>
      <td>14.4G</td>
      <td>126K</td>
      <td>14.0K</td>
      <td>20130315</td>
      <td>16 min 54 s</td>
      <td>325233</td>
    </tr>
    <tr>
      <th>1305</th>
      <td>how_farming_planted_seeds_for_the_internet_pat...</td>
      <td>6.56M</td>
      <td>14.4G</td>
      <td>122K</td>
      <td>13.6K</td>
      <td>20130321</td>
      <td>3 min 58 s</td>
      <td>230930</td>
    </tr>
    <tr>
      <th>1306</th>
      <td>how_to_take_a_great_picture_carolina_molinari</td>
      <td>4.93M</td>
      <td>14.4G</td>
      <td>122K</td>
      <td>13.6K</td>
      <td>20130729</td>
      <td>2 min 57 s</td>
      <td>233505</td>
    </tr>
    <tr>
      <th>1307</th>
      <td>don_t_insist_on_english_patricia_ryan</td>
      <td>16.4M</td>
      <td>14.4G</td>
      <td>122K</td>
      <td>13.5K</td>
      <td>20130725</td>
      <td>10 min 35 s</td>
      <td>216201</td>
    </tr>
    <tr>
      <th>1308</th>
      <td>your_elusive_creative_genius_elizabeth_gilbert</td>
      <td>40.2M</td>
      <td>14.5G</td>
      <td>121K</td>
      <td>13.5K</td>
      <td>20130322</td>
      <td>19 min 31 s</td>
      <td>287598</td>
    </tr>
    <tr>
      <th>1309</th>
      <td>string_theory_and_the_hidden_structures_of_the...</td>
      <td>15.7M</td>
      <td>14.5G</td>
      <td>120K</td>
      <td>13.4K</td>
      <td>20130422</td>
      <td>7 min 52 s</td>
      <td>278853</td>
    </tr>
    <tr>
      <th>1310</th>
      <td>tales_of_passion_isabel_allende</td>
      <td>29.3M</td>
      <td>14.5G</td>
      <td>120K</td>
      <td>13.3K</td>
      <td>20130106</td>
      <td>18 min 30 s</td>
      <td>221259</td>
    </tr>
    <tr>
      <th>1311</th>
      <td>the_mysterious_workings_of_the_adolescent_brai...</td>
      <td>31.1M</td>
      <td>14.5G</td>
      <td>116K</td>
      <td>12.9K</td>
      <td>20130601</td>
      <td>14 min 26 s</td>
      <td>300984</td>
    </tr>
    <tr>
      <th>1312</th>
      <td>want_to_be_happier_stay_in_the_moment_matt_kil...</td>
      <td>18.3M</td>
      <td>14.6G</td>
      <td>115K</td>
      <td>12.8K</td>
      <td>20130329</td>
      <td>10 min 16 s</td>
      <td>248765</td>
    </tr>
    <tr>
      <th>1313</th>
      <td>cern_s_supercollider_brian_cox</td>
      <td>26.8M</td>
      <td>14.6G</td>
      <td>115K</td>
      <td>12.7K</td>
      <td>20121208</td>
      <td>14 min 56 s</td>
      <td>250730</td>
    </tr>
    <tr>
      <th>1314</th>
      <td>greeting_the_world_in_peace_jackie_jenkins</td>
      <td>9.34M</td>
      <td>14.6G</td>
      <td>124K</td>
      <td>12.4K</td>
      <td>20120904</td>
      <td>3 min 17 s</td>
      <td>397307</td>
    </tr>
    <tr>
      <th>1315</th>
      <td>inside_a_cartoonist_s_world_liza_donnelly</td>
      <td>12.4M</td>
      <td>14.6G</td>
      <td>112K</td>
      <td>12.4K</td>
      <td>20121211</td>
      <td>4 min 22 s</td>
      <td>395603</td>
    </tr>
    <tr>
      <th>1316</th>
      <td>curiosity_discovery_and_gecko_feet_robert_full</td>
      <td>13.7M</td>
      <td>14.6G</td>
      <td>111K</td>
      <td>12.4K</td>
      <td>20121220</td>
      <td>9 min 9 s</td>
      <td>209252</td>
    </tr>
    <tr>
      <th>1317</th>
      <td>why_do_we_see_illusions_mark_changizi</td>
      <td>15.5M</td>
      <td>14.6G</td>
      <td>111K</td>
      <td>12.3K</td>
      <td>20130320</td>
      <td>7 min 21 s</td>
      <td>295071</td>
    </tr>
    <tr>
      <th>1318</th>
      <td>the_story_behind_your_glasses_eva_timothy</td>
      <td>12.4M</td>
      <td>14.6G</td>
      <td>111K</td>
      <td>12.3K</td>
      <td>20121008</td>
      <td>4 min 16 s</td>
      <td>406220</td>
    </tr>
    <tr>
      <th>1319</th>
      <td>describing_the_invisible_properties_of_gas_bri...</td>
      <td>7.12M</td>
      <td>14.7G</td>
      <td>111K</td>
      <td>12.3K</td>
      <td>20121010</td>
      <td>3 min 25 s</td>
      <td>290069</td>
    </tr>
    <tr>
      <th>1320</th>
      <td>the_emergence_of_drama_as_a_literary_art_mindy...</td>
      <td>7.41M</td>
      <td>14.7G</td>
      <td>111K</td>
      <td>12.3K</td>
      <td>20130605</td>
      <td>3 min 46 s</td>
      <td>274216</td>
    </tr>
    <tr>
      <th>1321</th>
      <td>pavlovian_reactions_aren_t_just_for_dogs_benja...</td>
      <td>12.0M</td>
      <td>14.7G</td>
      <td>110K</td>
      <td>12.2K</td>
      <td>20130426</td>
      <td>3 min 53 s</td>
      <td>431174</td>
    </tr>
    <tr>
      <th>1322</th>
      <td>an_exercise_in_time_perception_matt_danzico</td>
      <td>10.3M</td>
      <td>14.7G</td>
      <td>110K</td>
      <td>12.2K</td>
      <td>20130611</td>
      <td>5 min 24 s</td>
      <td>265165</td>
    </tr>
    <tr>
      <th>1323</th>
      <td>strange_answers_to_the_psychopath_test_jon_ronson</td>
      <td>32.7M</td>
      <td>14.7G</td>
      <td>110K</td>
      <td>12.2K</td>
      <td>20130507</td>
      <td>18 min 1 s</td>
      <td>253248</td>
    </tr>
    <tr>
      <th>1324</th>
      <td>magical_metals_how_shape_memory_alloys_work_ai...</td>
      <td>10.0M</td>
      <td>14.7G</td>
      <td>109K</td>
      <td>12.1K</td>
      <td>20120918</td>
      <td>4 min 45 s</td>
      <td>293812</td>
    </tr>
    <tr>
      <th>1325</th>
      <td>mysteries_of_vernacular_robot_jessica_oreck_an...</td>
      <td>3.26M</td>
      <td>14.7G</td>
      <td>92.2K</td>
      <td>11.5K</td>
      <td>20131031</td>
      <td>2 min 17 s</td>
      <td>198590</td>
    </tr>
    <tr>
      <th>1326</th>
      <td>distant_time_and_the_hint_of_a_multiverse_sean...</td>
      <td>26.5M</td>
      <td>14.8G</td>
      <td>103K</td>
      <td>11.4K</td>
      <td>20130808</td>
      <td>15 min 54 s</td>
      <td>232916</td>
    </tr>
    <tr>
      <th>1327</th>
      <td>a_digital_reimagining_of_gettysburg_anne_knowles</td>
      <td>15.6M</td>
      <td>14.8G</td>
      <td>90.7K</td>
      <td>11.3K</td>
      <td>20140526</td>
      <td>9 min 3 s</td>
      <td>241189</td>
    </tr>
    <tr>
      <th>1328</th>
      <td>the_networked_beauty_of_forests_suzanne_simard</td>
      <td>22.0M</td>
      <td>14.8G</td>
      <td>88.5K</td>
      <td>11.1K</td>
      <td>20140414</td>
      <td>7 min 23 s</td>
      <td>416281</td>
    </tr>
    <tr>
      <th>1329</th>
      <td>how_photography_connects_us_david_griffin</td>
      <td>21.2M</td>
      <td>14.8G</td>
      <td>98.0K</td>
      <td>10.9K</td>
      <td>20130101</td>
      <td>14 min 56 s</td>
      <td>198053</td>
    </tr>
    <tr>
      <th>1330</th>
      <td>distorting_madonna_in_medieval_art_james_earle</td>
      <td>5.58M</td>
      <td>14.8G</td>
      <td>97.7K</td>
      <td>10.9K</td>
      <td>20130219</td>
      <td>3 min 10 s</td>
      <td>245888</td>
    </tr>
    <tr>
      <th>1331</th>
      <td>parasite_tales_the_jewel_wasp_s_zombie_slave_c...</td>
      <td>15.8M</td>
      <td>14.8G</td>
      <td>97.6K</td>
      <td>10.8K</td>
      <td>20130128</td>
      <td>7 min 11 s</td>
      <td>307048</td>
    </tr>
    <tr>
      <th>1332</th>
      <td>science_can_answer_moral_questions_sam_harris</td>
      <td>47.2M</td>
      <td>14.9G</td>
      <td>97.4K</td>
      <td>10.8K</td>
      <td>20130216</td>
      <td>23 min 37 s</td>
      <td>279305</td>
    </tr>
    <tr>
      <th>1333</th>
      <td>does_racism_affect_how_you_vote_nate_silver</td>
      <td>15.5M</td>
      <td>14.9G</td>
      <td>97.1K</td>
      <td>10.8K</td>
      <td>20130302</td>
      <td>9 min 13 s</td>
      <td>235044</td>
    </tr>
    <tr>
      <th>1334</th>
      <td>actually_the_world_isn_t_flat_pankaj_ghemawat</td>
      <td>41.9M</td>
      <td>14.9G</td>
      <td>95.6K</td>
      <td>10.6K</td>
      <td>20130525</td>
      <td>17 min 3 s</td>
      <td>343616</td>
    </tr>
    <tr>
      <th>1335</th>
      <td>on_positive_psychology_martin_seligman</td>
      <td>42.8M</td>
      <td>15.0G</td>
      <td>94.9K</td>
      <td>10.5K</td>
      <td>20130706</td>
      <td>23 min 45 s</td>
      <td>252096</td>
    </tr>
    <tr>
      <th>1336</th>
      <td>pruney_fingers_a_gripping_story_mark_changizi</td>
      <td>9.86M</td>
      <td>15.0G</td>
      <td>93.8K</td>
      <td>10.4K</td>
      <td>20130521</td>
      <td>4 min 21 s</td>
      <td>316977</td>
    </tr>
    <tr>
      <th>1337</th>
      <td>see_yemen_through_my_eyes_nadia_al_sakkaf</td>
      <td>26.1M</td>
      <td>15.0G</td>
      <td>93.1K</td>
      <td>10.3K</td>
      <td>20121226</td>
      <td>13 min 38 s</td>
      <td>266914</td>
    </tr>
    <tr>
      <th>1338</th>
      <td>is_equality_enough</td>
      <td>14.0M</td>
      <td>15.0G</td>
      <td>51.6K</td>
      <td>10.3K</td>
      <td>20170720</td>
      <td>7 min 46 s</td>
      <td>250720</td>
    </tr>
    <tr>
      <th>1339</th>
      <td>are_video_games_actually_good_for_you</td>
      <td>13.5M</td>
      <td>15.0G</td>
      <td>51.4K</td>
      <td>10.3K</td>
      <td>20170518</td>
      <td>8 min 18 s</td>
      <td>226939</td>
    </tr>
    <tr>
      <th>1340</th>
      <td>all_your_devices_can_be_hacked_avi_rubin</td>
      <td>24.9M</td>
      <td>15.1G</td>
      <td>92.4K</td>
      <td>10.3K</td>
      <td>20130612</td>
      <td>16 min 56 s</td>
      <td>205251</td>
    </tr>
    <tr>
      <th>1341</th>
      <td>a_tap_dancer_s_craft_andrew_nemr</td>
      <td>13.4M</td>
      <td>15.1G</td>
      <td>91.7K</td>
      <td>10.2K</td>
      <td>20121219</td>
      <td>5 min 50 s</td>
      <td>319961</td>
    </tr>
    <tr>
      <th>1342</th>
      <td>dark_matter_how_does_it_explain_a_star_s_speed...</td>
      <td>5.78M</td>
      <td>15.1G</td>
      <td>91.0K</td>
      <td>10.1K</td>
      <td>20121112</td>
      <td>3 min 16 s</td>
      <td>247194</td>
    </tr>
    <tr>
      <th>1343</th>
      <td>connected_but_alone_sherry_turkle</td>
      <td>34.2M</td>
      <td>15.1G</td>
      <td>90.7K</td>
      <td>10.1K</td>
      <td>20130419</td>
      <td>19 min 48 s</td>
      <td>241348</td>
    </tr>
    <tr>
      <th>1344</th>
      <td>the_weird_wonderful_world_of_bioluminescence_e...</td>
      <td>20.8M</td>
      <td>15.1G</td>
      <td>90.6K</td>
      <td>10.1K</td>
      <td>20130329</td>
      <td>12 min 45 s</td>
      <td>228074</td>
    </tr>
    <tr>
      <th>1345</th>
      <td>defining_cyberwarfare_in_hopes_of_preventing_i...</td>
      <td>7.67M</td>
      <td>15.1G</td>
      <td>90.3K</td>
      <td>10.0K</td>
      <td>20130820</td>
      <td>3 min 49 s</td>
      <td>280414</td>
    </tr>
    <tr>
      <th>1346</th>
      <td>the_mystery_of_chronic_pain_elliot_krane</td>
      <td>16.0M</td>
      <td>15.2G</td>
      <td>89.8K</td>
      <td>9.98K</td>
      <td>20130331</td>
      <td>8 min 14 s</td>
      <td>271372</td>
    </tr>
    <tr>
      <th>1347</th>
      <td>math_class_needs_a_makeover_dan_meyer</td>
      <td>18.7M</td>
      <td>15.2G</td>
      <td>89.4K</td>
      <td>9.93K</td>
      <td>20130801</td>
      <td>11 min 39 s</td>
      <td>223834</td>
    </tr>
    <tr>
      <th>1348</th>
      <td>what_s_wrong_with_our_food_system_birke_baehr</td>
      <td>8.37M</td>
      <td>15.2G</td>
      <td>88.9K</td>
      <td>9.88K</td>
      <td>20130816</td>
      <td>5 min 14 s</td>
      <td>223242</td>
    </tr>
    <tr>
      <th>1349</th>
      <td>how_i_learned_to_organize_my_scatterbrain</td>
      <td>30.4M</td>
      <td>15.2G</td>
      <td>39.4K</td>
      <td>9.85K</td>
      <td>20180419</td>
      <td>13 min 4 s</td>
      <td>324592</td>
    </tr>
    <tr>
      <th>1350</th>
      <td>put_those_smartphones_away_great_tips_for_maki...</td>
      <td>19.0M</td>
      <td>15.2G</td>
      <td>88.4K</td>
      <td>9.82K</td>
      <td>20130528</td>
      <td>6 min 21 s</td>
      <td>417367</td>
    </tr>
    <tr>
      <th>1351</th>
      <td>underwater_astonishments_david_gallo</td>
      <td>13.3M</td>
      <td>15.2G</td>
      <td>87.6K</td>
      <td>9.74K</td>
      <td>20130111</td>
      <td>5 min 24 s</td>
      <td>342647</td>
    </tr>
    <tr>
      <th>1352</th>
      <td>the_power_of_vulnerability_brene_brown</td>
      <td>32.3M</td>
      <td>15.3G</td>
      <td>87.6K</td>
      <td>9.73K</td>
      <td>20130710</td>
      <td>20 min 19 s</td>
      <td>222434</td>
    </tr>
    <tr>
      <th>1353</th>
      <td>the_neurons_that_shaped_civilization_vs_ramach...</td>
      <td>13.9M</td>
      <td>15.3G</td>
      <td>87.3K</td>
      <td>9.70K</td>
      <td>20130831</td>
      <td>7 min 43 s</td>
      <td>252270</td>
    </tr>
    <tr>
      <th>1354</th>
      <td>sending_a_sundial_to_mars_bill_nye</td>
      <td>13.0M</td>
      <td>15.3G</td>
      <td>87.1K</td>
      <td>9.68K</td>
      <td>20121016</td>
      <td>7 min 49 s</td>
      <td>231886</td>
    </tr>
    <tr>
      <th>1355</th>
      <td>taking_imagination_seriously_janet_echelman</td>
      <td>27.4M</td>
      <td>15.3G</td>
      <td>86.6K</td>
      <td>9.62K</td>
      <td>20130811</td>
      <td>10 min 29 s</td>
      <td>364930</td>
    </tr>
    <tr>
      <th>1356</th>
      <td>how_great_leaders_inspire_action_simon_sinek</td>
      <td>55.7M</td>
      <td>15.4G</td>
      <td>86.4K</td>
      <td>9.59K</td>
      <td>20130626</td>
      <td>18 min 4 s</td>
      <td>430397</td>
    </tr>
    <tr>
      <th>1357</th>
      <td>the_future_of_lying_jeff_hancock</td>
      <td>54.2M</td>
      <td>15.4G</td>
      <td>85.8K</td>
      <td>9.53K</td>
      <td>20130403</td>
      <td>18 min 31 s</td>
      <td>408947</td>
    </tr>
    <tr>
      <th>1358</th>
      <td>capturing_authentic_narratives_michele_weldon</td>
      <td>7.14M</td>
      <td>15.4G</td>
      <td>93.2K</td>
      <td>9.32K</td>
      <td>20120827</td>
      <td>3 min 18 s</td>
      <td>301848</td>
    </tr>
    <tr>
      <th>1359</th>
      <td>ted_ed_clubs_celebrating_and_amplifying_studen...</td>
      <td>5.79M</td>
      <td>15.5G</td>
      <td>46.5K</td>
      <td>9.30K</td>
      <td>20170301</td>
      <td>2 min 12 s</td>
      <td>367470</td>
    </tr>
    <tr>
      <th>1360</th>
      <td>a_call_to_invention_diy_speaker_edition_willia...</td>
      <td>21.0M</td>
      <td>15.5G</td>
      <td>83.4K</td>
      <td>9.27K</td>
      <td>20130404</td>
      <td>6 min 48 s</td>
      <td>431743</td>
    </tr>
    <tr>
      <th>1361</th>
      <td>mysteries_of_vernacular_yankee_jessica_oreck_a...</td>
      <td>2.83M</td>
      <td>15.5G</td>
      <td>74.1K</td>
      <td>9.27K</td>
      <td>20131126</td>
      <td>1 min 54 s</td>
      <td>206764</td>
    </tr>
    <tr>
      <th>1362</th>
      <td>let_s_use_video_to_reinvent_education_salman_khan</td>
      <td>36.3M</td>
      <td>15.5G</td>
      <td>82.9K</td>
      <td>9.22K</td>
      <td>20130316</td>
      <td>20 min 27 s</td>
      <td>248306</td>
    </tr>
    <tr>
      <th>1363</th>
      <td>how_to_track_a_tornado_karen_kosiba</td>
      <td>14.1M</td>
      <td>15.5G</td>
      <td>73.2K</td>
      <td>9.15K</td>
      <td>20140421</td>
      <td>5 min 44 s</td>
      <td>343910</td>
    </tr>
    <tr>
      <th>1364</th>
      <td>making_a_ted_ed_lesson_animation</td>
      <td>13.2M</td>
      <td>15.5G</td>
      <td>82.0K</td>
      <td>9.11K</td>
      <td>20130527</td>
      <td>5 min 7 s</td>
      <td>360221</td>
    </tr>
    <tr>
      <th>1365</th>
      <td>biofuels_and_bioprospecting_for_beginners_crai...</td>
      <td>9.67M</td>
      <td>15.5G</td>
      <td>81.3K</td>
      <td>9.04K</td>
      <td>20130513</td>
      <td>3 min 52 s</td>
      <td>348488</td>
    </tr>
    <tr>
      <th>1366</th>
      <td>on_exploring_the_oceans_robert_ballard</td>
      <td>32.3M</td>
      <td>15.6G</td>
      <td>80.1K</td>
      <td>8.90K</td>
      <td>20130105</td>
      <td>18 min 16 s</td>
      <td>247208</td>
    </tr>
    <tr>
      <th>1367</th>
      <td>how_two_decisions_led_me_to_olympic_glory_stev...</td>
      <td>9.62M</td>
      <td>15.6G</td>
      <td>88.5K</td>
      <td>8.85K</td>
      <td>20120730</td>
      <td>4 min 1 s</td>
      <td>333558</td>
    </tr>
    <tr>
      <th>1368</th>
      <td>america_s_native_prisoners_of_war_aaron_huey</td>
      <td>24.2M</td>
      <td>15.6G</td>
      <td>79.3K</td>
      <td>8.81K</td>
      <td>20130913</td>
      <td>15 min 27 s</td>
      <td>218861</td>
    </tr>
    <tr>
      <th>1369</th>
      <td>a_teen_just_trying_to_figure_it_out_tavi_gevinson</td>
      <td>13.2M</td>
      <td>15.6G</td>
      <td>78.8K</td>
      <td>8.75K</td>
      <td>20130821</td>
      <td>7 min 30 s</td>
      <td>245342</td>
    </tr>
    <tr>
      <th>1370</th>
      <td>gridiron_physics_scalars_and_vectors_michelle_...</td>
      <td>10.8M</td>
      <td>15.6G</td>
      <td>78.6K</td>
      <td>8.73K</td>
      <td>20130220</td>
      <td>4 min 48 s</td>
      <td>312534</td>
    </tr>
    <tr>
      <th>1371</th>
      <td>measuring_what_makes_life_worthwhile_chip_conley</td>
      <td>30.8M</td>
      <td>15.7G</td>
      <td>77.7K</td>
      <td>8.64K</td>
      <td>20121227</td>
      <td>17 min 39 s</td>
      <td>243413</td>
    </tr>
    <tr>
      <th>1372</th>
      <td>hiv_and_flu_the_vaccine_strategy_seth_berkley</td>
      <td>48.5M</td>
      <td>15.7G</td>
      <td>77.2K</td>
      <td>8.58K</td>
      <td>20130308</td>
      <td>21 min 5 s</td>
      <td>321671</td>
    </tr>
    <tr>
      <th>1373</th>
      <td>deep_sea_diving_in_a_wheelchair_sue_austin</td>
      <td>26.6M</td>
      <td>15.7G</td>
      <td>68.5K</td>
      <td>8.56K</td>
      <td>20131211</td>
      <td>9 min 38 s</td>
      <td>385274</td>
    </tr>
    <tr>
      <th>1374</th>
      <td>cleaning_our_oceans_a_big_plan_for_a_big_problem</td>
      <td>27.3M</td>
      <td>15.8G</td>
      <td>33.1K</td>
      <td>8.28K</td>
      <td>20180309</td>
      <td>10 min 52 s</td>
      <td>351284</td>
    </tr>
    <tr>
      <th>1375</th>
      <td>what_makes_us_feel_good_about_our_work_dan_ariely</td>
      <td>31.8M</td>
      <td>15.8G</td>
      <td>65.8K</td>
      <td>8.23K</td>
      <td>20131206</td>
      <td>20 min 26 s</td>
      <td>217404</td>
    </tr>
    <tr>
      <th>1376</th>
      <td>conserving_our_spectacular_vulnerable_coral_re...</td>
      <td>7.22M</td>
      <td>15.8G</td>
      <td>73.2K</td>
      <td>8.14K</td>
      <td>20130103</td>
      <td>3 min 14 s</td>
      <td>311472</td>
    </tr>
    <tr>
      <th>1377</th>
      <td>on_spaghetti_sauce_malcolm_gladwell</td>
      <td>40.2M</td>
      <td>15.8G</td>
      <td>72.7K</td>
      <td>8.08K</td>
      <td>20130706</td>
      <td>17 min 33 s</td>
      <td>319792</td>
    </tr>
    <tr>
      <th>1378</th>
      <td>questioning_the_universe_stephen_hawking</td>
      <td>19.1M</td>
      <td>15.9G</td>
      <td>72.6K</td>
      <td>8.07K</td>
      <td>20130114</td>
      <td>10 min 15 s</td>
      <td>260906</td>
    </tr>
    <tr>
      <th>1379</th>
      <td>the_sweaty_teacher_s_lament_justin_lamb</td>
      <td>9.95M</td>
      <td>15.9G</td>
      <td>64.4K</td>
      <td>8.05K</td>
      <td>20140506</td>
      <td>3 min 10 s</td>
      <td>438543</td>
    </tr>
    <tr>
      <th>1380</th>
      <td>mysteries_of_vernacular_zero_jessica_oreck_and...</td>
      <td>2.82M</td>
      <td>15.9G</td>
      <td>72.3K</td>
      <td>8.04K</td>
      <td>20130801</td>
      <td>2 min 5 s</td>
      <td>187565</td>
    </tr>
    <tr>
      <th>1381</th>
      <td>our_loss_of_wisdom_barry_schwartz</td>
      <td>63.2M</td>
      <td>15.9G</td>
      <td>72.1K</td>
      <td>8.01K</td>
      <td>20130202</td>
      <td>21 min 19 s</td>
      <td>414572</td>
    </tr>
    <tr>
      <th>1382</th>
      <td>breaking_the_illusion_of_skin_color_nina_jablo...</td>
      <td>26.8M</td>
      <td>16.0G</td>
      <td>71.6K</td>
      <td>7.96K</td>
      <td>20121224</td>
      <td>14 min 45 s</td>
      <td>254064</td>
    </tr>
    <tr>
      <th>1383</th>
      <td>mysteries_of_vernacular_ukulele_jessica_oreck_...</td>
      <td>2.69M</td>
      <td>16.0G</td>
      <td>63.3K</td>
      <td>7.91K</td>
      <td>20131018</td>
      <td>2 min 0 s</td>
      <td>187487</td>
    </tr>
    <tr>
      <th>1384</th>
      <td>math_is_everywhere</td>
      <td>8.18M</td>
      <td>16.0G</td>
      <td>31.4K</td>
      <td>7.85K</td>
      <td>20180227</td>
      <td>4 min 16 s</td>
      <td>267587</td>
    </tr>
    <tr>
      <th>1385</th>
      <td>why_work_doesn_t_happen_at_work_jason_fried</td>
      <td>24.0M</td>
      <td>16.0G</td>
      <td>69.4K</td>
      <td>7.71K</td>
      <td>20130710</td>
      <td>15 min 20 s</td>
      <td>218690</td>
    </tr>
    <tr>
      <th>1386</th>
      <td>dance_vs_powerpoint_a_modest_proposal_john_boh...</td>
      <td>31.7M</td>
      <td>16.0G</td>
      <td>69.3K</td>
      <td>7.70K</td>
      <td>20121128</td>
      <td>11 min 17 s</td>
      <td>393196</td>
    </tr>
    <tr>
      <th>1387</th>
      <td>the_family_structure_of_elephants_caitlin_o_co...</td>
      <td>16.6M</td>
      <td>16.0G</td>
      <td>61.1K</td>
      <td>7.63K</td>
      <td>20140415</td>
      <td>8 min 11 s</td>
      <td>282615</td>
    </tr>
    <tr>
      <th>1388</th>
      <td>the_linguistic_genius_of_babies_patricia_kuhl</td>
      <td>15.9M</td>
      <td>16.1G</td>
      <td>67.5K</td>
      <td>7.50K</td>
      <td>20130710</td>
      <td>10 min 17 s</td>
      <td>215850</td>
    </tr>
    <tr>
      <th>1389</th>
      <td>how_to_find_the_true_face_of_leonardo_siegfrie...</td>
      <td>6.53M</td>
      <td>16.1G</td>
      <td>67.1K</td>
      <td>7.46K</td>
      <td>20130113</td>
      <td>4 min 21 s</td>
      <td>209754</td>
    </tr>
    <tr>
      <th>1390</th>
      <td>we_need_to_talk_about_an_injustice_bryan_steve...</td>
      <td>41.9M</td>
      <td>16.1G</td>
      <td>66.8K</td>
      <td>7.43K</td>
      <td>20130412</td>
      <td>23 min 41 s</td>
      <td>247107</td>
    </tr>
    <tr>
      <th>1391</th>
      <td>your_genes_are_not_your_fate_dean_ornish</td>
      <td>4.86M</td>
      <td>16.1G</td>
      <td>66.7K</td>
      <td>7.42K</td>
      <td>20130117</td>
      <td>3 min 14 s</td>
      <td>209655</td>
    </tr>
    <tr>
      <th>1392</th>
      <td>dissecting_botticelli_s_adoration_of_the_magi_...</td>
      <td>7.88M</td>
      <td>16.1G</td>
      <td>66.5K</td>
      <td>7.39K</td>
      <td>20130617</td>
      <td>3 min 11 s</td>
      <td>345261</td>
    </tr>
    <tr>
      <th>1393</th>
      <td>historical_role_models_amy_bissetta</td>
      <td>5.19M</td>
      <td>16.1G</td>
      <td>66.1K</td>
      <td>7.34K</td>
      <td>20130507</td>
      <td>2 min 36 s</td>
      <td>278412</td>
    </tr>
    <tr>
      <th>1394</th>
      <td>i_listen_to_color_neil_harbisson</td>
      <td>24.6M</td>
      <td>16.1G</td>
      <td>65.5K</td>
      <td>7.28K</td>
      <td>20130621</td>
      <td>9 min 36 s</td>
      <td>358497</td>
    </tr>
    <tr>
      <th>1395</th>
      <td>how_curiosity_got_us_to_mars_bobak_ferdowsi</td>
      <td>12.3M</td>
      <td>16.2G</td>
      <td>65.4K</td>
      <td>7.27K</td>
      <td>20130211</td>
      <td>6 min 13 s</td>
      <td>275674</td>
    </tr>
    <tr>
      <th>1396</th>
      <td>phenology_and_nature_s_shifting_rhythms_regina...</td>
      <td>6.93M</td>
      <td>16.2G</td>
      <td>64.6K</td>
      <td>7.17K</td>
      <td>20130110</td>
      <td>3 min 41 s</td>
      <td>262785</td>
    </tr>
    <tr>
      <th>1397</th>
      <td>listening_to_shame_brene_brown</td>
      <td>40.4M</td>
      <td>16.2G</td>
      <td>64.1K</td>
      <td>7.12K</td>
      <td>20130719</td>
      <td>20 min 38 s</td>
      <td>273469</td>
    </tr>
    <tr>
      <th>1398</th>
      <td>could_your_language_affect_your_ability_to_sav...</td>
      <td>25.0M</td>
      <td>16.2G</td>
      <td>56.7K</td>
      <td>7.09K</td>
      <td>20131203</td>
      <td>12 min 12 s</td>
      <td>286107</td>
    </tr>
    <tr>
      <th>1399</th>
      <td>mysteries_of_vernacular_clue_jessica_oreck</td>
      <td>3.72M</td>
      <td>16.2G</td>
      <td>63.3K</td>
      <td>7.04K</td>
      <td>20130401</td>
      <td>1 min 58 s</td>
      <td>263125</td>
    </tr>
    <tr>
      <th>1400</th>
      <td>folding_way_new_origami_robert_lang</td>
      <td>30.5M</td>
      <td>16.3G</td>
      <td>62.4K</td>
      <td>6.93K</td>
      <td>20121209</td>
      <td>15 min 56 s</td>
      <td>267185</td>
    </tr>
    <tr>
      <th>1401</th>
      <td>making_a_ted_ed_lesson_animating_zombies</td>
      <td>9.24M</td>
      <td>16.3G</td>
      <td>61.9K</td>
      <td>6.88K</td>
      <td>20130714</td>
      <td>5 min 6 s</td>
      <td>252972</td>
    </tr>
    <tr>
      <th>1402</th>
      <td>how_to_make_work_life_balance_work_nigel_marsh</td>
      <td>21.7M</td>
      <td>16.3G</td>
      <td>61.5K</td>
      <td>6.84K</td>
      <td>20130808</td>
      <td>10 min 4 s</td>
      <td>300468</td>
    </tr>
    <tr>
      <th>1403</th>
      <td>self_assembly_the_power_of_organizing_the_unor...</td>
      <td>6.34M</td>
      <td>16.3G</td>
      <td>60.3K</td>
      <td>6.70K</td>
      <td>20130408</td>
      <td>3 min 41 s</td>
      <td>239825</td>
    </tr>
    <tr>
      <th>1404</th>
      <td>how_one_teenager_unearthed_baseball_s_untold_h...</td>
      <td>13.5M</td>
      <td>16.3G</td>
      <td>53.4K</td>
      <td>6.67K</td>
      <td>20140206</td>
      <td>5 min 55 s</td>
      <td>318551</td>
    </tr>
    <tr>
      <th>1405</th>
      <td>how_whales_breathe_communicate_and_fart_with_t...</td>
      <td>16.1M</td>
      <td>16.3G</td>
      <td>53.3K</td>
      <td>6.66K</td>
      <td>20140410</td>
      <td>6 min 24 s</td>
      <td>350359</td>
    </tr>
    <tr>
      <th>1406</th>
      <td>3_things_i_learned_while_my_plane_crashed_ric_...</td>
      <td>9.01M</td>
      <td>16.3G</td>
      <td>58.9K</td>
      <td>6.55K</td>
      <td>20130315</td>
      <td>5 min 2 s</td>
      <td>249690</td>
    </tr>
    <tr>
      <th>1407</th>
      <td>make_robots_smarter_ayanna_howard</td>
      <td>19.2M</td>
      <td>16.4G</td>
      <td>58.0K</td>
      <td>6.45K</td>
      <td>20130206</td>
      <td>6 min 18 s</td>
      <td>426613</td>
    </tr>
    <tr>
      <th>1408</th>
      <td>the_danger_of_science_denial_michael_specter</td>
      <td>36.6M</td>
      <td>16.4G</td>
      <td>57.9K</td>
      <td>6.43K</td>
      <td>20130223</td>
      <td>16 min 29 s</td>
      <td>310085</td>
    </tr>
    <tr>
      <th>1409</th>
      <td>how_giant_sea_creatures_eat_tiny_sea_creatures...</td>
      <td>13.0M</td>
      <td>16.4G</td>
      <td>57.9K</td>
      <td>6.43K</td>
      <td>20130509</td>
      <td>6 min 21 s</td>
      <td>286137</td>
    </tr>
    <tr>
      <th>1410</th>
      <td>why_is_x_the_unknown_terry_moore</td>
      <td>6.43M</td>
      <td>16.4G</td>
      <td>57.8K</td>
      <td>6.42K</td>
      <td>20130507</td>
      <td>3 min 57 s</td>
      <td>227505</td>
    </tr>
    <tr>
      <th>1411</th>
      <td>visualizing_the_world_s_twitter_data_jer_thorp</td>
      <td>14.6M</td>
      <td>16.4G</td>
      <td>57.8K</td>
      <td>6.42K</td>
      <td>20130221</td>
      <td>5 min 41 s</td>
      <td>358842</td>
    </tr>
    <tr>
      <th>1412</th>
      <td>mysteries_of_vernacular_quarantine_jessica_ore...</td>
      <td>3.45M</td>
      <td>16.4G</td>
      <td>57.4K</td>
      <td>6.38K</td>
      <td>20130704</td>
      <td>2 min 10 s</td>
      <td>222271</td>
    </tr>
    <tr>
      <th>1413</th>
      <td>stories_legacies_of_who_we_are_awele_makeba</td>
      <td>20.8M</td>
      <td>16.4G</td>
      <td>63.2K</td>
      <td>6.32K</td>
      <td>20120312</td>
      <td>9 min 1 s</td>
      <td>321740</td>
    </tr>
    <tr>
      <th>1414</th>
      <td>is_the_obesity_crisis_hiding_a_bigger_problem_...</td>
      <td>38.9M</td>
      <td>16.5G</td>
      <td>56.6K</td>
      <td>6.29K</td>
      <td>20130823</td>
      <td>16 min 1 s</td>
      <td>339151</td>
    </tr>
    <tr>
      <th>1415</th>
      <td>tracking_grizzly_bears_from_space_david_laskin</td>
      <td>11.5M</td>
      <td>16.5G</td>
      <td>56.4K</td>
      <td>6.27K</td>
      <td>20130604</td>
      <td>4 min 14 s</td>
      <td>379461</td>
    </tr>
    <tr>
      <th>1416</th>
      <td>learning_from_past_presidents_doris_kearns_goo...</td>
      <td>29.6M</td>
      <td>16.5G</td>
      <td>56.3K</td>
      <td>6.26K</td>
      <td>20130121</td>
      <td>19 min 16 s</td>
      <td>214859</td>
    </tr>
    <tr>
      <th>1417</th>
      <td>a_plant_s_eye_view_michael_pollan</td>
      <td>45.5M</td>
      <td>16.6G</td>
      <td>55.6K</td>
      <td>6.18K</td>
      <td>20130112</td>
      <td>17 min 29 s</td>
      <td>363797</td>
    </tr>
    <tr>
      <th>1418</th>
      <td>the_human_and_the_honeybee_dino_martins</td>
      <td>13.5M</td>
      <td>16.6G</td>
      <td>55.0K</td>
      <td>6.12K</td>
      <td>20130629</td>
      <td>6 min 24 s</td>
      <td>293414</td>
    </tr>
    <tr>
      <th>1419</th>
      <td>early_forensics_and_crime_solving_chemists_deb...</td>
      <td>15.9M</td>
      <td>16.6G</td>
      <td>54.8K</td>
      <td>6.08K</td>
      <td>20130401</td>
      <td>7 min 50 s</td>
      <td>283264</td>
    </tr>
    <tr>
      <th>1420</th>
      <td>less_stuff_more_happiness_graham_hill</td>
      <td>8.50M</td>
      <td>16.6G</td>
      <td>54.5K</td>
      <td>6.05K</td>
      <td>20130412</td>
      <td>5 min 49 s</td>
      <td>203889</td>
    </tr>
    <tr>
      <th>1421</th>
      <td>mysteries_of_vernacular_assassin_jessica_oreck</td>
      <td>3.34M</td>
      <td>16.6G</td>
      <td>54.4K</td>
      <td>6.05K</td>
      <td>20130403</td>
      <td>1 min 56 s</td>
      <td>239794</td>
    </tr>
    <tr>
      <th>1422</th>
      <td>the_pattern_behind_self_deception_michael_shermer</td>
      <td>32.1M</td>
      <td>16.6G</td>
      <td>53.3K</td>
      <td>5.92K</td>
      <td>20130308</td>
      <td>19 min 1 s</td>
      <td>235771</td>
    </tr>
    <tr>
      <th>1423</th>
      <td>how_architecture_helped_music_evolve_david_byrne</td>
      <td>31.4M</td>
      <td>16.7G</td>
      <td>53.0K</td>
      <td>5.88K</td>
      <td>20130308</td>
      <td>16 min 0 s</td>
      <td>274349</td>
    </tr>
    <tr>
      <th>1424</th>
      <td>averting_the_climate_crisis_al_gore</td>
      <td>48.8M</td>
      <td>16.7G</td>
      <td>52.7K</td>
      <td>5.85K</td>
      <td>20130510</td>
      <td>16 min 14 s</td>
      <td>419804</td>
    </tr>
    <tr>
      <th>1425</th>
      <td>mysteries_of_vernacular_bewilder_jessica_oreck...</td>
      <td>3.08M</td>
      <td>16.7G</td>
      <td>52.6K</td>
      <td>5.85K</td>
      <td>20130823</td>
      <td>1 min 54 s</td>
      <td>225144</td>
    </tr>
    <tr>
      <th>1426</th>
      <td>how_art_gives_shape_to_cultural_change_thelma_...</td>
      <td>19.5M</td>
      <td>16.7G</td>
      <td>52.3K</td>
      <td>5.81K</td>
      <td>20130224</td>
      <td>12 min 28 s</td>
      <td>218197</td>
    </tr>
    <tr>
      <th>1427</th>
      <td>time_lapse_proof_of_extreme_ice_loss_james_balog</td>
      <td>45.5M</td>
      <td>16.8G</td>
      <td>51.7K</td>
      <td>5.75K</td>
      <td>20130817</td>
      <td>19 min 19 s</td>
      <td>329537</td>
    </tr>
    <tr>
      <th>1428</th>
      <td>mysteries_of_vernacular_earwig_jessica_oreck_a...</td>
      <td>3.50M</td>
      <td>16.8G</td>
      <td>51.7K</td>
      <td>5.75K</td>
      <td>20130510</td>
      <td>2 min 15 s</td>
      <td>215702</td>
    </tr>
    <tr>
      <th>1429</th>
      <td>ashton_cofer_a_young_inventor_s_plan_to_recycl...</td>
      <td>11.2M</td>
      <td>16.8G</td>
      <td>28.5K</td>
      <td>5.71K</td>
      <td>20170420</td>
      <td>6 min 5 s</td>
      <td>256708</td>
    </tr>
    <tr>
      <th>1430</th>
      <td>visualizing_hidden_worlds_inside_your_body_dee...</td>
      <td>12.0M</td>
      <td>16.8G</td>
      <td>51.0K</td>
      <td>5.67K</td>
      <td>20130306</td>
      <td>6 min 5 s</td>
      <td>274646</td>
    </tr>
    <tr>
      <th>1431</th>
      <td>a_40_year_plan_for_energy_amory_lovins</td>
      <td>41.3M</td>
      <td>16.9G</td>
      <td>50.2K</td>
      <td>5.58K</td>
      <td>20130427</td>
      <td>27 min 4 s</td>
      <td>213547</td>
    </tr>
    <tr>
      <th>1432</th>
      <td>the_hidden_power_of_smiling_ron_gutman</td>
      <td>15.4M</td>
      <td>16.9G</td>
      <td>49.6K</td>
      <td>5.51K</td>
      <td>20130322</td>
      <td>7 min 26 s</td>
      <td>288691</td>
    </tr>
    <tr>
      <th>1433</th>
      <td>why_i_must_speak_out_about_climate_change_jame...</td>
      <td>28.7M</td>
      <td>16.9G</td>
      <td>49.6K</td>
      <td>5.51K</td>
      <td>20130412</td>
      <td>17 min 51 s</td>
      <td>225067</td>
    </tr>
    <tr>
      <th>1434</th>
      <td>different_ways_of_knowing_daniel_tammet</td>
      <td>16.6M</td>
      <td>16.9G</td>
      <td>49.2K</td>
      <td>5.47K</td>
      <td>20130405</td>
      <td>10 min 53 s</td>
      <td>212537</td>
    </tr>
    <tr>
      <th>1435</th>
      <td>earth_s_mass_extinction_peter_ward</td>
      <td>29.1M</td>
      <td>16.9G</td>
      <td>49.1K</td>
      <td>5.46K</td>
      <td>20130201</td>
      <td>19 min 38 s</td>
      <td>207002</td>
    </tr>
    <tr>
      <th>1436</th>
      <td>true_success_john_wooden</td>
      <td>53.9M</td>
      <td>17.0G</td>
      <td>49.0K</td>
      <td>5.44K</td>
      <td>20130824</td>
      <td>17 min 39 s</td>
      <td>426929</td>
    </tr>
    <tr>
      <th>1437</th>
      <td>how_state_budgets_are_breaking_us_schools_bill...</td>
      <td>18.3M</td>
      <td>17.0G</td>
      <td>48.8K</td>
      <td>5.42K</td>
      <td>20130309</td>
      <td>11 min 31 s</td>
      <td>221824</td>
    </tr>
    <tr>
      <th>1438</th>
      <td>click_your_fortune_episode_1_demo</td>
      <td>5.03M</td>
      <td>17.0G</td>
      <td>47.1K</td>
      <td>5.23K</td>
      <td>20130807</td>
      <td>3 min 23 s</td>
      <td>207421</td>
    </tr>
    <tr>
      <th>1439</th>
      <td>the_bottom_billion_paul_collier</td>
      <td>37.6M</td>
      <td>17.1G</td>
      <td>46.9K</td>
      <td>5.21K</td>
      <td>20130116</td>
      <td>16 min 52 s</td>
      <td>311842</td>
    </tr>
    <tr>
      <th>1440</th>
      <td>mysteries_of_vernacular_gorgeous_jessica_oreck...</td>
      <td>3.17M</td>
      <td>17.1G</td>
      <td>46.8K</td>
      <td>5.20K</td>
      <td>20130621</td>
      <td>2 min 0 s</td>
      <td>221689</td>
    </tr>
    <tr>
      <th>1441</th>
      <td>making_a_ted_ed_lesson_synesthesia_and_playing...</td>
      <td>9.15M</td>
      <td>17.1G</td>
      <td>46.7K</td>
      <td>5.19K</td>
      <td>20130707</td>
      <td>4 min 6 s</td>
      <td>310969</td>
    </tr>
    <tr>
      <th>1442</th>
      <td>the_birth_of_a_word_deb_roy</td>
      <td>43.2M</td>
      <td>17.1G</td>
      <td>46.6K</td>
      <td>5.18K</td>
      <td>20121201</td>
      <td>21 min 7 s</td>
      <td>286091</td>
    </tr>
    <tr>
      <th>1443</th>
      <td>high_altitude_wind_energy_from_kites_saul_grif...</td>
      <td>11.2M</td>
      <td>17.1G</td>
      <td>46.6K</td>
      <td>5.17K</td>
      <td>20130222</td>
      <td>5 min 22 s</td>
      <td>291330</td>
    </tr>
    <tr>
      <th>1444</th>
      <td>what_we_learned_from_5_million_books_erez_lieb...</td>
      <td>21.7M</td>
      <td>17.1G</td>
      <td>45.6K</td>
      <td>5.07K</td>
      <td>20130714</td>
      <td>14 min 8 s</td>
      <td>214460</td>
    </tr>
    <tr>
      <th>1445</th>
      <td>toy_tiles_that_talk_to_each_other_david_merrill</td>
      <td>17.9M</td>
      <td>17.2G</td>
      <td>45.6K</td>
      <td>5.07K</td>
      <td>20130222</td>
      <td>7 min 12 s</td>
      <td>347872</td>
    </tr>
    <tr>
      <th>1446</th>
      <td>our_buggy_moral_code_dan_ariely</td>
      <td>39.5M</td>
      <td>17.2G</td>
      <td>45.4K</td>
      <td>5.05K</td>
      <td>20130203</td>
      <td>16 min 51 s</td>
      <td>327980</td>
    </tr>
    <tr>
      <th>1447</th>
      <td>mysteries_of_vernacular_noise_jessica_oreck</td>
      <td>3.50M</td>
      <td>17.2G</td>
      <td>45.4K</td>
      <td>5.04K</td>
      <td>20130405</td>
      <td>2 min 1 s</td>
      <td>240737</td>
    </tr>
    <tr>
      <th>1448</th>
      <td>the_shape_shifting_future_of_the_mobile_phone_...</td>
      <td>8.23M</td>
      <td>17.2G</td>
      <td>44.4K</td>
      <td>4.94K</td>
      <td>20130728</td>
      <td>4 min 15 s</td>
      <td>270107</td>
    </tr>
    <tr>
      <th>1449</th>
      <td>are_we_ready_for_neo_evolution_harvey_fineberg</td>
      <td>28.5M</td>
      <td>17.2G</td>
      <td>44.4K</td>
      <td>4.93K</td>
      <td>20130324</td>
      <td>17 min 21 s</td>
      <td>229412</td>
    </tr>
    <tr>
      <th>1450</th>
      <td>the_post_crisis_consumer_john_gerzema</td>
      <td>24.9M</td>
      <td>17.3G</td>
      <td>44.3K</td>
      <td>4.92K</td>
      <td>20130605</td>
      <td>16 min 34 s</td>
      <td>209647</td>
    </tr>
    <tr>
      <th>1451</th>
      <td>the_art_of_choosing_sheena_iyengar</td>
      <td>40.0M</td>
      <td>17.3G</td>
      <td>43.9K</td>
      <td>4.88K</td>
      <td>20130824</td>
      <td>24 min 8 s</td>
      <td>231704</td>
    </tr>
    <tr>
      <th>1452</th>
      <td>why_videos_go_viral_kevin_allocca</td>
      <td>13.9M</td>
      <td>17.3G</td>
      <td>43.4K</td>
      <td>4.82K</td>
      <td>20121117</td>
      <td>7 min 20 s</td>
      <td>264959</td>
    </tr>
    <tr>
      <th>1453</th>
      <td>beware_online_filter_bubbles_eli_pariser</td>
      <td>16.3M</td>
      <td>17.3G</td>
      <td>43.4K</td>
      <td>4.82K</td>
      <td>20130322</td>
      <td>9 min 4 s</td>
      <td>250650</td>
    </tr>
    <tr>
      <th>1454</th>
      <td>creative_houses_from_reclaimed_stuff_dan_phillips</td>
      <td>33.1M</td>
      <td>17.4G</td>
      <td>43.0K</td>
      <td>4.77K</td>
      <td>20130717</td>
      <td>17 min 57 s</td>
      <td>257371</td>
    </tr>
    <tr>
      <th>1455</th>
      <td>mysteries_of_vernacular_pants_jessica_oreck</td>
      <td>3.38M</td>
      <td>17.4G</td>
      <td>42.7K</td>
      <td>4.74K</td>
      <td>20130402</td>
      <td>2 min 2 s</td>
      <td>231243</td>
    </tr>
    <tr>
      <th>1456</th>
      <td>yup_i_built_a_nuclear_fusion_reactor_taylor_wi...</td>
      <td>8.14M</td>
      <td>17.4G</td>
      <td>42.7K</td>
      <td>4.74K</td>
      <td>20130719</td>
      <td>20 min 28 s</td>
      <td>55566</td>
    </tr>
    <tr>
      <th>1457</th>
      <td>moral_behavior_in_animals_frans_de_waal</td>
      <td>36.4M</td>
      <td>17.4G</td>
      <td>42.2K</td>
      <td>4.68K</td>
      <td>20130703</td>
      <td>16 min 52 s</td>
      <td>301732</td>
    </tr>
    <tr>
      <th>1458</th>
      <td>pop_an_ollie_and_innovate_rodney_mullen</td>
      <td>48.2M</td>
      <td>17.5G</td>
      <td>42.1K</td>
      <td>4.67K</td>
      <td>20130821</td>
      <td>18 min 19 s</td>
      <td>367814</td>
    </tr>
    <tr>
      <th>1459</th>
      <td>bring_ted_to_the_classroom_with_ted_ed_clubs</td>
      <td>2.33M</td>
      <td>17.5G</td>
      <td>32.5K</td>
      <td>4.64K</td>
      <td>20150819</td>
      <td>1 min 13 s</td>
      <td>264132</td>
    </tr>
    <tr>
      <th>1460</th>
      <td>making_a_ted_ed_lesson_two_ways_to_animate_sla...</td>
      <td>15.0M</td>
      <td>17.5G</td>
      <td>41.5K</td>
      <td>4.61K</td>
      <td>20130720</td>
      <td>5 min 24 s</td>
      <td>388069</td>
    </tr>
    <tr>
      <th>1461</th>
      <td>the_real_goal_equal_pay_for_equal_play</td>
      <td>16.5M</td>
      <td>17.5G</td>
      <td>23.0K</td>
      <td>4.60K</td>
      <td>20170308</td>
      <td>9 min 45 s</td>
      <td>236610</td>
    </tr>
    <tr>
      <th>1462</th>
      <td>shedding_light_on_dark_matter_patricia_burchat</td>
      <td>26.7M</td>
      <td>17.5G</td>
      <td>41.4K</td>
      <td>4.60K</td>
      <td>20121130</td>
      <td>17 min 8 s</td>
      <td>217763</td>
    </tr>
    <tr>
      <th>1463</th>
      <td>toward_a_new_understanding_of_mental_illness_t...</td>
      <td>22.1M</td>
      <td>17.5G</td>
      <td>41.4K</td>
      <td>4.60K</td>
      <td>20130707</td>
      <td>13 min 6 s</td>
      <td>235693</td>
    </tr>
    <tr>
      <th>1464</th>
      <td>redefining_the_dictionary_erin_mckean</td>
      <td>29.9M</td>
      <td>17.6G</td>
      <td>41.2K</td>
      <td>4.58K</td>
      <td>20121228</td>
      <td>15 min 54 s</td>
      <td>262529</td>
    </tr>
    <tr>
      <th>1465</th>
      <td>a_new_way_to_diagnose_autism_ami_klin</td>
      <td>37.7M</td>
      <td>17.6G</td>
      <td>40.6K</td>
      <td>4.51K</td>
      <td>20130602</td>
      <td>19 min 44 s</td>
      <td>266639</td>
    </tr>
    <tr>
      <th>1466</th>
      <td>planning_for_the_end_of_oil_richard_sears</td>
      <td>20.1M</td>
      <td>17.6G</td>
      <td>40.3K</td>
      <td>4.48K</td>
      <td>20130301</td>
      <td>6 min 52 s</td>
      <td>408288</td>
    </tr>
    <tr>
      <th>1467</th>
      <td>seeing_a_sustainable_future_alex_steffen</td>
      <td>15.3M</td>
      <td>17.6G</td>
      <td>40.3K</td>
      <td>4.48K</td>
      <td>20121207</td>
      <td>10 min 13 s</td>
      <td>209074</td>
    </tr>
    <tr>
      <th>1468</th>
      <td>mysteries_of_vernacular_dynamite_jessica_oreck...</td>
      <td>3.53M</td>
      <td>17.6G</td>
      <td>40.0K</td>
      <td>4.45K</td>
      <td>20130607</td>
      <td>2 min 15 s</td>
      <td>217585</td>
    </tr>
    <tr>
      <th>1469</th>
      <td>sublimation_mit_digital_lab_techniques_manual</td>
      <td>8.96M</td>
      <td>17.6G</td>
      <td>52.9K</td>
      <td>4.41K</td>
      <td>20100204</td>
      <td>6 min 7 s</td>
      <td>204240</td>
    </tr>
    <tr>
      <th>1470</th>
      <td>mysteries_of_vernacular_x_ray_jessica_oreck_an...</td>
      <td>2.58M</td>
      <td>17.6G</td>
      <td>39.6K</td>
      <td>4.40K</td>
      <td>20130805</td>
      <td>1 min 58 s</td>
      <td>182017</td>
    </tr>
    <tr>
      <th>1471</th>
      <td>building_a_culture_of_success_mark_wilson</td>
      <td>15.1M</td>
      <td>17.7G</td>
      <td>39.6K</td>
      <td>4.40K</td>
      <td>20130621</td>
      <td>8 min 54 s</td>
      <td>237303</td>
    </tr>
    <tr>
      <th>1472</th>
      <td>mysteries_of_vernacular_tuxedo_jessica_oreck</td>
      <td>3.59M</td>
      <td>17.7G</td>
      <td>39.5K</td>
      <td>4.39K</td>
      <td>20130501</td>
      <td>2 min 4 s</td>
      <td>242019</td>
    </tr>
    <tr>
      <th>1473</th>
      <td>on_being_a_woman_and_a_diplomat_madeleine_albr...</td>
      <td>28.9M</td>
      <td>17.7G</td>
      <td>38.8K</td>
      <td>4.31K</td>
      <td>20130817</td>
      <td>12 min 59 s</td>
      <td>310727</td>
    </tr>
    <tr>
      <th>1474</th>
      <td>the_surprising_science_of_happiness_nancy_etcoff</td>
      <td>24.1M</td>
      <td>17.7G</td>
      <td>38.7K</td>
      <td>4.30K</td>
      <td>20130713</td>
      <td>14 min 21 s</td>
      <td>234277</td>
    </tr>
    <tr>
      <th>1475</th>
      <td>the_search_for_other_earth_like_planets_olivie...</td>
      <td>13.7M</td>
      <td>17.7G</td>
      <td>38.6K</td>
      <td>4.29K</td>
      <td>20130425</td>
      <td>6 min 20 s</td>
      <td>301988</td>
    </tr>
    <tr>
      <th>1476</th>
      <td>the_3_a_s_of_awesome_neil_pasricha</td>
      <td>41.3M</td>
      <td>17.8G</td>
      <td>38.5K</td>
      <td>4.28K</td>
      <td>20130825</td>
      <td>17 min 33 s</td>
      <td>329118</td>
    </tr>
    <tr>
      <th>1477</th>
      <td>how_economic_inequality_harms_societies_richar...</td>
      <td>31.0M</td>
      <td>17.8G</td>
      <td>38.1K</td>
      <td>4.23K</td>
      <td>20130809</td>
      <td>16 min 54 s</td>
      <td>256618</td>
    </tr>
    <tr>
      <th>1478</th>
      <td>mysteries_of_vernacular_miniature_jessica_oreck</td>
      <td>3.84M</td>
      <td>17.8G</td>
      <td>38.0K</td>
      <td>4.22K</td>
      <td>20130419</td>
      <td>2 min 3 s</td>
      <td>260401</td>
    </tr>
    <tr>
      <th>1479</th>
      <td>on_being_wrong_kathryn_schulz</td>
      <td>35.0M</td>
      <td>17.8G</td>
      <td>37.9K</td>
      <td>4.21K</td>
      <td>20130315</td>
      <td>17 min 51 s</td>
      <td>274054</td>
    </tr>
    <tr>
      <th>1480</th>
      <td>medicine_s_future_there_s_an_app_for_that_dani...</td>
      <td>25.1M</td>
      <td>17.9G</td>
      <td>37.2K</td>
      <td>4.13K</td>
      <td>20130623</td>
      <td>18 min 21 s</td>
      <td>191097</td>
    </tr>
    <tr>
      <th>1481</th>
      <td>detention_or_eco_club_choosing_your_future_jua...</td>
      <td>9.35M</td>
      <td>17.9G</td>
      <td>37.0K</td>
      <td>4.11K</td>
      <td>20130104</td>
      <td>6 min 38 s</td>
      <td>197075</td>
    </tr>
    <tr>
      <th>1482</th>
      <td>erin_mckean_the_joy_of_lexicography</td>
      <td>32.7M</td>
      <td>17.9G</td>
      <td>61.6K</td>
      <td>4.10K</td>
      <td>20070830</td>
      <td>17 min 47 s</td>
      <td>256868</td>
    </tr>
    <tr>
      <th>1483</th>
      <td>fractals_and_the_art_of_roughness_benoit_mande...</td>
      <td>34.0M</td>
      <td>17.9G</td>
      <td>36.6K</td>
      <td>4.07K</td>
      <td>20130308</td>
      <td>17 min 9 s</td>
      <td>276766</td>
    </tr>
    <tr>
      <th>1484</th>
      <td>a_warm_embrace_that_saves_lives_jane_chen</td>
      <td>8.86M</td>
      <td>17.9G</td>
      <td>36.3K</td>
      <td>4.04K</td>
      <td>20130810</td>
      <td>4 min 46 s</td>
      <td>259472</td>
    </tr>
    <tr>
      <th>1485</th>
      <td>how_to_learn_from_mistakes_diana_laufenberg</td>
      <td>21.9M</td>
      <td>18.0G</td>
      <td>36.3K</td>
      <td>4.03K</td>
      <td>20130818</td>
      <td>10 min 5 s</td>
      <td>303316</td>
    </tr>
    <tr>
      <th>1486</th>
      <td>how_to_restore_a_rainforest_willie_smits</td>
      <td>40.2M</td>
      <td>18.0G</td>
      <td>36.2K</td>
      <td>4.02K</td>
      <td>20130222</td>
      <td>20 min 39 s</td>
      <td>271884</td>
    </tr>
    <tr>
      <th>1487</th>
      <td>how_i_fell_in_love_with_a_fish_dan_barber</td>
      <td>39.0M</td>
      <td>18.0G</td>
      <td>36.1K</td>
      <td>4.01K</td>
      <td>20130215</td>
      <td>19 min 32 s</td>
      <td>278938</td>
    </tr>
    <tr>
      <th>1488</th>
      <td>announcing_ted_ed_espanol</td>
      <td>2.06M</td>
      <td>18.1G</td>
      <td>27.8K</td>
      <td>3.96K</td>
      <td>20150415</td>
      <td>34 s 387 ms</td>
      <td>503601</td>
    </tr>
    <tr>
      <th>1489</th>
      <td>are_we_born_to_run_christopher_mcdougall</td>
      <td>45.3M</td>
      <td>18.1G</td>
      <td>35.7K</td>
      <td>3.96K</td>
      <td>20130808</td>
      <td>15 min 52 s</td>
      <td>398833</td>
    </tr>
    <tr>
      <th>1490</th>
      <td>mysteries_of_vernacular_window_jessica_oreck_a...</td>
      <td>3.31M</td>
      <td>18.1G</td>
      <td>35.5K</td>
      <td>3.94K</td>
      <td>20130613</td>
      <td>1 min 56 s</td>
      <td>237607</td>
    </tr>
    <tr>
      <th>1491</th>
      <td>the_lost_art_of_democratic_debate_michael_sandel</td>
      <td>54.1M</td>
      <td>18.2G</td>
      <td>35.1K</td>
      <td>3.90K</td>
      <td>20130323</td>
      <td>19 min 42 s</td>
      <td>384055</td>
    </tr>
    <tr>
      <th>1492</th>
      <td>mysteries_of_vernacular_sarcophagus_jessica_or...</td>
      <td>2.57M</td>
      <td>18.2G</td>
      <td>35.0K</td>
      <td>3.89K</td>
      <td>20130726</td>
      <td>1 min 37 s</td>
      <td>222513</td>
    </tr>
    <tr>
      <th>1493</th>
      <td>navigating_our_global_future_ian_goldin</td>
      <td>12.2M</td>
      <td>18.2G</td>
      <td>34.9K</td>
      <td>3.87K</td>
      <td>20130817</td>
      <td>7 min 6 s</td>
      <td>239213</td>
    </tr>
    <tr>
      <th>1494</th>
      <td>mysteries_of_vernacular_venom_jessica_oreck_an...</td>
      <td>3.18M</td>
      <td>18.2G</td>
      <td>34.7K</td>
      <td>3.86K</td>
      <td>20130607</td>
      <td>2 min 2 s</td>
      <td>218680</td>
    </tr>
    <tr>
      <th>1495</th>
      <td>mysteries_of_vernacular_keister_jessica_oreck_...</td>
      <td>2.86M</td>
      <td>18.2G</td>
      <td>34.6K</td>
      <td>3.85K</td>
      <td>20130809</td>
      <td>2 min 0 s</td>
      <td>199205</td>
    </tr>
    <tr>
      <th>1496</th>
      <td>the_security_mirage_bruce_schneier</td>
      <td>40.7M</td>
      <td>18.2G</td>
      <td>34.2K</td>
      <td>3.80K</td>
      <td>20130612</td>
      <td>21 min 5 s</td>
      <td>269594</td>
    </tr>
    <tr>
      <th>1497</th>
      <td>mysteries_of_vernacular_inaugurate_jessica_oreck</td>
      <td>3.45M</td>
      <td>18.2G</td>
      <td>34.1K</td>
      <td>3.79K</td>
      <td>20130524</td>
      <td>2 min 7 s</td>
      <td>226434</td>
    </tr>
    <tr>
      <th>1498</th>
      <td>txtng_is_killing_language_jk_john_mcwhorter</td>
      <td>27.1M</td>
      <td>18.2G</td>
      <td>34.0K</td>
      <td>3.78K</td>
      <td>20130830</td>
      <td>13 min 51 s</td>
      <td>273812</td>
    </tr>
    <tr>
      <th>1499</th>
      <td>how_will_ted_ed_celebrate_its_1000000th_subscr...</td>
      <td>2.80M</td>
      <td>18.2G</td>
      <td>26.4K</td>
      <td>3.77K</td>
      <td>20150114</td>
      <td>49 s 399 ms</td>
      <td>476062</td>
    </tr>
    <tr>
      <th>1500</th>
      <td>the_other_inconvenient_truth_jonathan_foley</td>
      <td>29.5M</td>
      <td>18.3G</td>
      <td>33.7K</td>
      <td>3.75K</td>
      <td>20130821</td>
      <td>17 min 46 s</td>
      <td>232333</td>
    </tr>
    <tr>
      <th>1501</th>
      <td>redefining_the_f_word</td>
      <td>13.2M</td>
      <td>18.3G</td>
      <td>14.9K</td>
      <td>3.73K</td>
      <td>20171207</td>
      <td>7 min 57 s</td>
      <td>231159</td>
    </tr>
    <tr>
      <th>1502</th>
      <td>every_city_needs_healthy_honey_bees_noah_wilso...</td>
      <td>28.1M</td>
      <td>18.3G</td>
      <td>33.5K</td>
      <td>3.72K</td>
      <td>20130414</td>
      <td>12 min 42 s</td>
      <td>308617</td>
    </tr>
    <tr>
      <th>1503</th>
      <td>the_mathematics_of_history_jean_baptiste_michel</td>
      <td>7.24M</td>
      <td>18.3G</td>
      <td>33.4K</td>
      <td>3.71K</td>
      <td>20130504</td>
      <td>4 min 26 s</td>
      <td>228333</td>
    </tr>
    <tr>
      <th>1504</th>
      <td>my_seven_species_of_robot_dennis_hong</td>
      <td>30.5M</td>
      <td>18.3G</td>
      <td>32.8K</td>
      <td>3.64K</td>
      <td>20130815</td>
      <td>16 min 15 s</td>
      <td>262051</td>
    </tr>
    <tr>
      <th>1505</th>
      <td>digging_for_humanity_s_origins_louise_leakey</td>
      <td>31.1M</td>
      <td>18.4G</td>
      <td>32.8K</td>
      <td>3.64K</td>
      <td>20130120</td>
      <td>15 min 33 s</td>
      <td>279313</td>
    </tr>
    <tr>
      <th>1506</th>
      <td>exciting_news_from_ted_ed</td>
      <td>5.13M</td>
      <td>18.4G</td>
      <td>32.7K</td>
      <td>3.63K</td>
      <td>20130423</td>
      <td>2 min 13 s</td>
      <td>321970</td>
    </tr>
    <tr>
      <th>1507</th>
      <td>mysteries_of_vernacular_fizzle_jessica_oreck_a...</td>
      <td>2.65M</td>
      <td>18.4G</td>
      <td>32.7K</td>
      <td>3.63K</td>
      <td>20130719</td>
      <td>1 min 50 s</td>
      <td>201366</td>
    </tr>
    <tr>
      <th>1508</th>
      <td>dare_to_educate_afghan_girls_shabana_basij_rasikh</td>
      <td>21.9M</td>
      <td>18.4G</td>
      <td>32.4K</td>
      <td>3.60K</td>
      <td>20130421</td>
      <td>9 min 36 s</td>
      <td>318495</td>
    </tr>
    <tr>
      <th>1509</th>
      <td>building_the_seed_cathedral_thomas_heatherwick</td>
      <td>31.9M</td>
      <td>18.4G</td>
      <td>32.2K</td>
      <td>3.58K</td>
      <td>20130330</td>
      <td>16 min 52 s</td>
      <td>264434</td>
    </tr>
    <tr>
      <th>1510</th>
      <td>mysteries_of_vernacular_jade_jessica_oreck_and...</td>
      <td>3.39M</td>
      <td>18.4G</td>
      <td>32.2K</td>
      <td>3.57K</td>
      <td>20130712</td>
      <td>2 min 7 s</td>
      <td>222928</td>
    </tr>
    <tr>
      <th>1511</th>
      <td>hey_science_teachers_make_it_fun_tyler_dewitt</td>
      <td>28.3M</td>
      <td>18.5G</td>
      <td>31.7K</td>
      <td>3.53K</td>
      <td>20130422</td>
      <td>14 min 10 s</td>
      <td>278826</td>
    </tr>
    <tr>
      <th>1512</th>
      <td>a_rosetta_stone_for_the_indus_script_rajesh_rao</td>
      <td>27.9M</td>
      <td>18.5G</td>
      <td>31.6K</td>
      <td>3.51K</td>
      <td>20130405</td>
      <td>17 min 1 s</td>
      <td>229095</td>
    </tr>
    <tr>
      <th>1513</th>
      <td>why_eyewitnesses_get_it_wrong_scott_fraser</td>
      <td>43.1M</td>
      <td>18.5G</td>
      <td>31.5K</td>
      <td>3.50K</td>
      <td>20130703</td>
      <td>18 min 26 s</td>
      <td>326937</td>
    </tr>
    <tr>
      <th>1514</th>
      <td>ted_prize_wish_protect_our_oceans_sylvia_earle</td>
      <td>55.7M</td>
      <td>18.6G</td>
      <td>31.4K</td>
      <td>3.49K</td>
      <td>20121221</td>
      <td>18 min 11 s</td>
      <td>427644</td>
    </tr>
    <tr>
      <th>1515</th>
      <td>faith_versus_tradition_in_islam_mustafa_akyol</td>
      <td>27.2M</td>
      <td>18.6G</td>
      <td>31.3K</td>
      <td>3.47K</td>
      <td>20130808</td>
      <td>17 min 11 s</td>
      <td>221245</td>
    </tr>
    <tr>
      <th>1516</th>
      <td>symmetry_reality_s_riddle_marcus_du_sautoy</td>
      <td>40.1M</td>
      <td>18.7G</td>
      <td>31.2K</td>
      <td>3.46K</td>
      <td>20130817</td>
      <td>18 min 19 s</td>
      <td>306129</td>
    </tr>
    <tr>
      <th>1517</th>
      <td>how_to_use_a_paper_towel_joe_smith</td>
      <td>11.2M</td>
      <td>18.7G</td>
      <td>31.1K</td>
      <td>3.45K</td>
      <td>20130821</td>
      <td>4 min 31 s</td>
      <td>345786</td>
    </tr>
    <tr>
      <th>1518</th>
      <td>your_brain_on_improv_charles_limb</td>
      <td>29.6M</td>
      <td>18.7G</td>
      <td>30.2K</td>
      <td>3.35K</td>
      <td>20130703</td>
      <td>16 min 31 s</td>
      <td>250849</td>
    </tr>
    <tr>
      <th>1519</th>
      <td>the_quest_to_understand_consciousness_antonio_...</td>
      <td>31.8M</td>
      <td>18.7G</td>
      <td>30.1K</td>
      <td>3.35K</td>
      <td>20130412</td>
      <td>18 min 42 s</td>
      <td>237419</td>
    </tr>
    <tr>
      <th>1520</th>
      <td>mysteries_of_vernacular_hearse_jessica_oreck</td>
      <td>3.73M</td>
      <td>18.7G</td>
      <td>30.0K</td>
      <td>3.34K</td>
      <td>20130404</td>
      <td>2 min 13 s</td>
      <td>233758</td>
    </tr>
    <tr>
      <th>1521</th>
      <td>meet_julia_delmedico</td>
      <td>5.45M</td>
      <td>18.7G</td>
      <td>29.9K</td>
      <td>3.33K</td>
      <td>20130508</td>
      <td>2 min 16 s</td>
      <td>335476</td>
    </tr>
    <tr>
      <th>1522</th>
      <td>feats_of_memory_anyone_can_do_joshua_foer</td>
      <td>33.5M</td>
      <td>18.8G</td>
      <td>29.9K</td>
      <td>3.32K</td>
      <td>20130426</td>
      <td>20 min 28 s</td>
      <td>228373</td>
    </tr>
    <tr>
      <th>1523</th>
      <td>building_a_museum_of_museums_on_the_web_amit_sood</td>
      <td>9.86M</td>
      <td>18.8G</td>
      <td>29.6K</td>
      <td>3.28K</td>
      <td>20130322</td>
      <td>5 min 35 s</td>
      <td>246467</td>
    </tr>
    <tr>
      <th>1524</th>
      <td>why_domestic_violence_victims_don_t_leave_lesl...</td>
      <td>33.8M</td>
      <td>18.8G</td>
      <td>28.9K</td>
      <td>3.21K</td>
      <td>20130520</td>
      <td>15 min 59 s</td>
      <td>295118</td>
    </tr>
    <tr>
      <th>1525</th>
      <td>high_tech_art_with_a_sense_of_humor_aparna_rao</td>
      <td>12.7M</td>
      <td>18.8G</td>
      <td>28.6K</td>
      <td>3.18K</td>
      <td>20121202</td>
      <td>8 min 20 s</td>
      <td>212280</td>
    </tr>
    <tr>
      <th>1526</th>
      <td>404_the_story_of_a_page_not_found_renny_gleeson</td>
      <td>7.71M</td>
      <td>18.8G</td>
      <td>28.4K</td>
      <td>3.16K</td>
      <td>20130426</td>
      <td>4 min 7 s</td>
      <td>261323</td>
    </tr>
    <tr>
      <th>1527</th>
      <td>healthier_men_one_moustache_at_a_time_adam_garone</td>
      <td>47.6M</td>
      <td>18.9G</td>
      <td>27.6K</td>
      <td>3.07K</td>
      <td>20130407</td>
      <td>16 min 41 s</td>
      <td>398646</td>
    </tr>
    <tr>
      <th>1528</th>
      <td>behind_the_great_firewall_of_china_michael_anti</td>
      <td>35.3M</td>
      <td>18.9G</td>
      <td>27.5K</td>
      <td>3.06K</td>
      <td>20130622</td>
      <td>18 min 51 s</td>
      <td>261494</td>
    </tr>
    <tr>
      <th>1529</th>
      <td>the_beautiful_math_of_coral_margaret_wertheim</td>
      <td>28.2M</td>
      <td>18.9G</td>
      <td>27.2K</td>
      <td>3.02K</td>
      <td>20121124</td>
      <td>15 min 31 s</td>
      <td>253591</td>
    </tr>
    <tr>
      <th>1530</th>
      <td>will_our_kids_be_a_different_species_juan_enri...</td>
      <td>27.3M</td>
      <td>19.0G</td>
      <td>26.9K</td>
      <td>2.98K</td>
      <td>20130821</td>
      <td>16 min 48 s</td>
      <td>227190</td>
    </tr>
    <tr>
      <th>1531</th>
      <td>the_demise_of_guys_philip_zimbardo</td>
      <td>8.43M</td>
      <td>19.0G</td>
      <td>26.4K</td>
      <td>2.94K</td>
      <td>20121216</td>
      <td>4 min 46 s</td>
      <td>246622</td>
    </tr>
    <tr>
      <th>1532</th>
      <td>the_art_of_asking_amanda_palmer</td>
      <td>29.5M</td>
      <td>19.0G</td>
      <td>26.3K</td>
      <td>2.92K</td>
      <td>20130830</td>
      <td>13 min 47 s</td>
      <td>299166</td>
    </tr>
    <tr>
      <th>1533</th>
      <td>the_business_logic_of_sustainability_ray_anderson</td>
      <td>33.2M</td>
      <td>19.0G</td>
      <td>26.3K</td>
      <td>2.92K</td>
      <td>20130301</td>
      <td>15 min 51 s</td>
      <td>292528</td>
    </tr>
    <tr>
      <th>1534</th>
      <td>building_a_dinosaur_from_a_chicken_jack_horner</td>
      <td>25.4M</td>
      <td>19.1G</td>
      <td>26.1K</td>
      <td>2.89K</td>
      <td>20130329</td>
      <td>16 min 36 s</td>
      <td>213581</td>
    </tr>
    <tr>
      <th>1535</th>
      <td>what_you_don_t_know_about_marriage_jenna_mccarthy</td>
      <td>18.1M</td>
      <td>19.1G</td>
      <td>25.8K</td>
      <td>2.87K</td>
      <td>20130815</td>
      <td>11 min 17 s</td>
      <td>223675</td>
    </tr>
    <tr>
      <th>1536</th>
      <td>making_a_ted_ed_lesson_concept_and_design</td>
      <td>9.81M</td>
      <td>19.1G</td>
      <td>25.7K</td>
      <td>2.85K</td>
      <td>20130527</td>
      <td>3 min 16 s</td>
      <td>419305</td>
    </tr>
    <tr>
      <th>1537</th>
      <td>the_good_news_of_the_decade_hans_rosling</td>
      <td>29.8M</td>
      <td>19.1G</td>
      <td>25.6K</td>
      <td>2.85K</td>
      <td>20130811</td>
      <td>15 min 34 s</td>
      <td>267590</td>
    </tr>
    <tr>
      <th>1538</th>
      <td>imaging_at_a_trillion_frames_per_second_ramesh...</td>
      <td>20.9M</td>
      <td>19.1G</td>
      <td>25.6K</td>
      <td>2.85K</td>
      <td>20130621</td>
      <td>11 min 1 s</td>
      <td>264272</td>
    </tr>
    <tr>
      <th>1539</th>
      <td>your_brain_is_more_than_a_bag_of_chemicals_dav...</td>
      <td>29.0M</td>
      <td>19.2G</td>
      <td>25.3K</td>
      <td>2.81K</td>
      <td>20130512</td>
      <td>15 min 25 s</td>
      <td>263161</td>
    </tr>
    <tr>
      <th>1540</th>
      <td>the_myth_of_the_gay_agenda_lz_granderson</td>
      <td>44.1M</td>
      <td>19.2G</td>
      <td>25.3K</td>
      <td>2.81K</td>
      <td>20130821</td>
      <td>17 min 51 s</td>
      <td>345626</td>
    </tr>
    <tr>
      <th>1541</th>
      <td>meet_melissa_perez</td>
      <td>5.01M</td>
      <td>19.2G</td>
      <td>25.2K</td>
      <td>2.80K</td>
      <td>20130508</td>
      <td>2 min 33 s</td>
      <td>273246</td>
    </tr>
    <tr>
      <th>1542</th>
      <td>4_lessons_from_robots_about_being_human_ken_go...</td>
      <td>29.5M</td>
      <td>19.2G</td>
      <td>23.9K</td>
      <td>2.65K</td>
      <td>20130707</td>
      <td>17 min 9 s</td>
      <td>240620</td>
    </tr>
    <tr>
      <th>1543</th>
      <td>why_we_need_to_go_back_to_mars_joel_levine</td>
      <td>27.5M</td>
      <td>19.3G</td>
      <td>23.8K</td>
      <td>2.65K</td>
      <td>20130801</td>
      <td>16 min 14 s</td>
      <td>236628</td>
    </tr>
    <tr>
      <th>1544</th>
      <td>do_the_green_thing_andy_hobsbawm</td>
      <td>6.83M</td>
      <td>19.3G</td>
      <td>23.7K</td>
      <td>2.63K</td>
      <td>20130126</td>
      <td>3 min 55 s</td>
      <td>243104</td>
    </tr>
    <tr>
      <th>1545</th>
      <td>the_el_sistema_music_revolution_jose_antonio_a...</td>
      <td>36.7M</td>
      <td>19.3G</td>
      <td>23.6K</td>
      <td>2.63K</td>
      <td>20130222</td>
      <td>17 min 24 s</td>
      <td>294714</td>
    </tr>
    <tr>
      <th>1546</th>
      <td>ladies_and_gentlemen_the_hobart_shakespeareans</td>
      <td>28.0M</td>
      <td>19.3G</td>
      <td>23.6K</td>
      <td>2.62K</td>
      <td>20130516</td>
      <td>10 min 9 s</td>
      <td>385532</td>
    </tr>
    <tr>
      <th>1547</th>
      <td>ted_ed_clubs_presents_ted_ed_weekend</td>
      <td>8.88M</td>
      <td>19.4G</td>
      <td>13.0K</td>
      <td>2.60K</td>
      <td>20170223</td>
      <td>3 min 32 s</td>
      <td>349973</td>
    </tr>
    <tr>
      <th>1548</th>
      <td>superhero_training_what_you_can_do_right_now</td>
      <td>31.8M</td>
      <td>19.4G</td>
      <td>10.3K</td>
      <td>2.58K</td>
      <td>20180301</td>
      <td>10 min 20 s</td>
      <td>430204</td>
    </tr>
    <tr>
      <th>1549</th>
      <td>music_and_emotion_through_time_michael_tilson_...</td>
      <td>38.8M</td>
      <td>19.4G</td>
      <td>23.2K</td>
      <td>2.58K</td>
      <td>20130426</td>
      <td>20 min 13 s</td>
      <td>268043</td>
    </tr>
    <tr>
      <th>1550</th>
      <td>my_backyard_got_way_cooler_when_i_added_a_dragon</td>
      <td>13.3M</td>
      <td>19.4G</td>
      <td>10.2K</td>
      <td>2.56K</td>
      <td>20171108</td>
      <td>7 min 15 s</td>
      <td>255953</td>
    </tr>
    <tr>
      <th>1551</th>
      <td>the_walk_from_no_to_yes_william_ury</td>
      <td>36.8M</td>
      <td>19.5G</td>
      <td>22.9K</td>
      <td>2.54K</td>
      <td>20130818</td>
      <td>18 min 45 s</td>
      <td>274642</td>
    </tr>
    <tr>
      <th>1552</th>
      <td>doodlers_unite_sunni_brown</td>
      <td>10.0M</td>
      <td>19.5G</td>
      <td>22.8K</td>
      <td>2.54K</td>
      <td>20130405</td>
      <td>5 min 50 s</td>
      <td>240327</td>
    </tr>
    <tr>
      <th>1553</th>
      <td>how_to_spot_a_liar_pamela_meyer</td>
      <td>31.3M</td>
      <td>19.5G</td>
      <td>22.8K</td>
      <td>2.53K</td>
      <td>20130809</td>
      <td>18 min 50 s</td>
      <td>232342</td>
    </tr>
    <tr>
      <th>1554</th>
      <td>retrofitting_suburbia_ellen_dunham_jones</td>
      <td>35.5M</td>
      <td>19.5G</td>
      <td>22.8K</td>
      <td>2.53K</td>
      <td>20121214</td>
      <td>19 min 24 s</td>
      <td>255441</td>
    </tr>
    <tr>
      <th>1555</th>
      <td>meet_shayna_cody</td>
      <td>3.82M</td>
      <td>19.5G</td>
      <td>22.5K</td>
      <td>2.50K</td>
      <td>20130508</td>
      <td>1 min 36 s</td>
      <td>332825</td>
    </tr>
    <tr>
      <th>1556</th>
      <td>losing_everything_david_hoffman</td>
      <td>11.2M</td>
      <td>19.6G</td>
      <td>22.4K</td>
      <td>2.49K</td>
      <td>20130119</td>
      <td>5 min 6 s</td>
      <td>305637</td>
    </tr>
    <tr>
      <th>1557</th>
      <td>the_hidden_beauty_of_pollination_louie_schwart...</td>
      <td>24.1M</td>
      <td>19.6G</td>
      <td>22.1K</td>
      <td>2.46K</td>
      <td>20130322</td>
      <td>7 min 40 s</td>
      <td>438713</td>
    </tr>
    <tr>
      <th>1558</th>
      <td>how_poachers_became_caretakers_john_kasaona</td>
      <td>27.9M</td>
      <td>19.6G</td>
      <td>17.0K</td>
      <td>2.42K</td>
      <td>20150210</td>
      <td>15 min 46 s</td>
      <td>247644</td>
    </tr>
    <tr>
      <th>1559</th>
      <td>archeology_from_space_sarah_parcak</td>
      <td>9.71M</td>
      <td>19.6G</td>
      <td>21.7K</td>
      <td>2.41K</td>
      <td>20130507</td>
      <td>5 min 20 s</td>
      <td>254358</td>
    </tr>
    <tr>
      <th>1560</th>
      <td>the_equation_for_reaching_your_dreams</td>
      <td>25.3M</td>
      <td>19.6G</td>
      <td>9.64K</td>
      <td>2.41K</td>
      <td>20180508</td>
      <td>9 min 22 s</td>
      <td>376297</td>
    </tr>
    <tr>
      <th>1561</th>
      <td>facing_the_real_me_looking_in_the_mirror_with_...</td>
      <td>28.9M</td>
      <td>19.7G</td>
      <td>9.45K</td>
      <td>2.36K</td>
      <td>20180209</td>
      <td>11 min 25 s</td>
      <td>353722</td>
    </tr>
    <tr>
      <th>1562</th>
      <td>be_you_ty_over_beauty</td>
      <td>21.9M</td>
      <td>19.7G</td>
      <td>11.8K</td>
      <td>2.36K</td>
      <td>20170823</td>
      <td>10 min 25 s</td>
      <td>294117</td>
    </tr>
    <tr>
      <th>1563</th>
      <td>let_s_raise_kids_to_be_entrepreneurs_cameron_h...</td>
      <td>34.9M</td>
      <td>19.7G</td>
      <td>21.2K</td>
      <td>2.36K</td>
      <td>20130801</td>
      <td>19 min 36 s</td>
      <td>248691</td>
    </tr>
    <tr>
      <th>1564</th>
      <td>how_a_fly_flies_michael_dickinson</td>
      <td>26.6M</td>
      <td>19.8G</td>
      <td>21.0K</td>
      <td>2.33K</td>
      <td>20130508</td>
      <td>15 min 55 s</td>
      <td>233311</td>
    </tr>
    <tr>
      <th>1565</th>
      <td>making_sense_of_a_visible_quantum_object_aaron...</td>
      <td>15.7M</td>
      <td>19.8G</td>
      <td>21.0K</td>
      <td>2.33K</td>
      <td>20130329</td>
      <td>7 min 51 s</td>
      <td>278908</td>
    </tr>
    <tr>
      <th>1566</th>
      <td>the_sound_the_universe_makes_janna_levin</td>
      <td>36.3M</td>
      <td>19.8G</td>
      <td>20.9K</td>
      <td>2.32K</td>
      <td>20130315</td>
      <td>17 min 43 s</td>
      <td>286008</td>
    </tr>
    <tr>
      <th>1567</th>
      <td>a_light_switch_for_neurons_ed_boyden</td>
      <td>42.0M</td>
      <td>19.8G</td>
      <td>20.7K</td>
      <td>2.30K</td>
      <td>20130406</td>
      <td>18 min 24 s</td>
      <td>319230</td>
    </tr>
    <tr>
      <th>1568</th>
      <td>what_do_babies_think_alison_gopnik</td>
      <td>38.1M</td>
      <td>19.9G</td>
      <td>20.5K</td>
      <td>2.28K</td>
      <td>20130809</td>
      <td>18 min 29 s</td>
      <td>288298</td>
    </tr>
    <tr>
      <th>1569</th>
      <td>how_mr_condom_made_thailand_a_better_place_mec...</td>
      <td>24.8M</td>
      <td>19.9G</td>
      <td>20.5K</td>
      <td>2.27K</td>
      <td>20130710</td>
      <td>13 min 50 s</td>
      <td>250547</td>
    </tr>
    <tr>
      <th>1570</th>
      <td>a_future_beyond_traffic_gridlock_bill_ford</td>
      <td>29.2M</td>
      <td>19.9G</td>
      <td>20.3K</td>
      <td>2.26K</td>
      <td>20130413</td>
      <td>16 min 48 s</td>
      <td>242971</td>
    </tr>
    <tr>
      <th>1571</th>
      <td>praising_slowness_carl_honore</td>
      <td>60.5M</td>
      <td>20.0G</td>
      <td>20.3K</td>
      <td>2.26K</td>
      <td>20130726</td>
      <td>19 min 17 s</td>
      <td>438294</td>
    </tr>
    <tr>
      <th>1572</th>
      <td>overcoming_the_scientific_divide_aaron_reedy</td>
      <td>13.3M</td>
      <td>20.0G</td>
      <td>19.9K</td>
      <td>2.21K</td>
      <td>20130620</td>
      <td>7 min 56 s</td>
      <td>234252</td>
    </tr>
    <tr>
      <th>1573</th>
      <td>image_recognition_that_triggers_augmented_real...</td>
      <td>21.2M</td>
      <td>20.0G</td>
      <td>19.9K</td>
      <td>2.21K</td>
      <td>20130629</td>
      <td>8 min 4 s</td>
      <td>366527</td>
    </tr>
    <tr>
      <th>1574</th>
      <td>how_benjamin_button_got_his_face_ed_ulbrich</td>
      <td>38.8M</td>
      <td>20.1G</td>
      <td>19.6K</td>
      <td>2.18K</td>
      <td>20130222</td>
      <td>18 min 4 s</td>
      <td>299736</td>
    </tr>
    <tr>
      <th>1575</th>
      <td>teachers_need_real_feedback_bill_gates</td>
      <td>24.7M</td>
      <td>20.1G</td>
      <td>19.5K</td>
      <td>2.17K</td>
      <td>20130816</td>
      <td>10 min 24 s</td>
      <td>332070</td>
    </tr>
    <tr>
      <th>1576</th>
      <td>could_a_saturn_moon_harbor_life_carolyn_porco</td>
      <td>7.68M</td>
      <td>20.1G</td>
      <td>19.5K</td>
      <td>2.17K</td>
      <td>20130301</td>
      <td>3 min 26 s</td>
      <td>311432</td>
    </tr>
    <tr>
      <th>1577</th>
      <td>social_animal_david_brooks</td>
      <td>35.9M</td>
      <td>20.1G</td>
      <td>19.3K</td>
      <td>2.15K</td>
      <td>20130317</td>
      <td>18 min 43 s</td>
      <td>268172</td>
    </tr>
    <tr>
      <th>1578</th>
      <td>what_s_so_funny_about_mental_illness_ruby_wax</td>
      <td>27.3M</td>
      <td>20.2G</td>
      <td>19.3K</td>
      <td>2.15K</td>
      <td>20130524</td>
      <td>8 min 45 s</td>
      <td>435748</td>
    </tr>
    <tr>
      <th>1579</th>
      <td>a_new_ecosystem_for_electric_cars_shai_agassi</td>
      <td>36.8M</td>
      <td>20.2G</td>
      <td>19.2K</td>
      <td>2.13K</td>
      <td>20130301</td>
      <td>18 min 3 s</td>
      <td>284745</td>
    </tr>
    <tr>
      <th>1580</th>
      <td>tour_the_solar_system_from_home_jon_nguyen</td>
      <td>12.3M</td>
      <td>20.2G</td>
      <td>19.2K</td>
      <td>2.13K</td>
      <td>20130821</td>
      <td>7 min 53 s</td>
      <td>218200</td>
    </tr>
    <tr>
      <th>1581</th>
      <td>four_principles_for_the_open_world_don_tapscott</td>
      <td>42.3M</td>
      <td>20.2G</td>
      <td>18.9K</td>
      <td>2.10K</td>
      <td>20130208</td>
      <td>17 min 50 s</td>
      <td>331450</td>
    </tr>
    <tr>
      <th>1582</th>
      <td>supercharged_motorcycle_design_yves_behar</td>
      <td>4.62M</td>
      <td>20.3G</td>
      <td>18.6K</td>
      <td>2.07K</td>
      <td>20130301</td>
      <td>2 min 20 s</td>
      <td>275658</td>
    </tr>
    <tr>
      <th>1583</th>
      <td>the_beautiful_tricks_of_flowers_jonathan_drori</td>
      <td>21.6M</td>
      <td>20.3G</td>
      <td>18.4K</td>
      <td>2.04K</td>
      <td>20130831</td>
      <td>13 min 48 s</td>
      <td>218518</td>
    </tr>
    <tr>
      <th>1584</th>
      <td>artificial_justice_would_robots_make_good_judges</td>
      <td>14.1M</td>
      <td>20.3G</td>
      <td>8.12K</td>
      <td>2.03K</td>
      <td>20180320</td>
      <td>6 min 37 s</td>
      <td>297082</td>
    </tr>
    <tr>
      <th>1585</th>
      <td>battling_bad_science_ben_goldacre</td>
      <td>30.4M</td>
      <td>20.3G</td>
      <td>18.0K</td>
      <td>2.00K</td>
      <td>20130809</td>
      <td>14 min 19 s</td>
      <td>296319</td>
    </tr>
    <tr>
      <th>1586</th>
      <td>a_tale_of_mental_illness_from_the_inside_elyn_...</td>
      <td>34.2M</td>
      <td>20.4G</td>
      <td>17.9K</td>
      <td>1.99K</td>
      <td>20130628</td>
      <td>14 min 52 s</td>
      <td>321311</td>
    </tr>
    <tr>
      <th>1587</th>
      <td>lessons_from_fashion_s_free_culture_johanna_bl...</td>
      <td>20.7M</td>
      <td>20.4G</td>
      <td>17.5K</td>
      <td>1.94K</td>
      <td>20130801</td>
      <td>15 min 36 s</td>
      <td>185231</td>
    </tr>
    <tr>
      <th>1588</th>
      <td>from_mach_20_glider_to_humming_bird_drone_regi...</td>
      <td>44.8M</td>
      <td>20.4G</td>
      <td>17.3K</td>
      <td>1.92K</td>
      <td>20130420</td>
      <td>25 min 1 s</td>
      <td>250328</td>
    </tr>
    <tr>
      <th>1589</th>
      <td>a_navy_admiral_s_thoughts_on_global_security_j...</td>
      <td>37.4M</td>
      <td>20.5G</td>
      <td>17.3K</td>
      <td>1.92K</td>
      <td>20130621</td>
      <td>16 min 34 s</td>
      <td>315783</td>
    </tr>
    <tr>
      <th>1590</th>
      <td>cheese_dogs_and_a_pill_to_kill_mosquitoes_and_...</td>
      <td>22.9M</td>
      <td>20.5G</td>
      <td>17.2K</td>
      <td>1.91K</td>
      <td>20130602</td>
      <td>10 min 20 s</td>
      <td>308858</td>
    </tr>
    <tr>
      <th>1591</th>
      <td>the_earth_is_full_paul_gilding</td>
      <td>26.8M</td>
      <td>20.5G</td>
      <td>17.1K</td>
      <td>1.91K</td>
      <td>20130412</td>
      <td>16 min 46 s</td>
      <td>223583</td>
    </tr>
    <tr>
      <th>1592</th>
      <td>making_a_ted_ed_lesson_creative_process</td>
      <td>10.3M</td>
      <td>20.5G</td>
      <td>17.1K</td>
      <td>1.90K</td>
      <td>20130527</td>
      <td>4 min 14 s</td>
      <td>340153</td>
    </tr>
    <tr>
      <th>1593</th>
      <td>dare_to_disagree_margaret_heffernan</td>
      <td>21.2M</td>
      <td>20.5G</td>
      <td>16.8K</td>
      <td>1.86K</td>
      <td>20130614</td>
      <td>8 min 44 s</td>
      <td>338197</td>
    </tr>
    <tr>
      <th>1594</th>
      <td>unintended_consequences_edward_tenner</td>
      <td>24.9M</td>
      <td>20.6G</td>
      <td>16.6K</td>
      <td>1.85K</td>
      <td>20130405</td>
      <td>16 min 10 s</td>
      <td>215511</td>
    </tr>
    <tr>
      <th>1595</th>
      <td>a_saudi_woman_who_dared_to_drive_manal_al_sharif</td>
      <td>33.2M</td>
      <td>20.6G</td>
      <td>16.5K</td>
      <td>1.83K</td>
      <td>20130823</td>
      <td>14 min 19 s</td>
      <td>324242</td>
    </tr>
    <tr>
      <th>1596</th>
      <td>why_libya_s_revolution_didn_t_work_and_what_mi...</td>
      <td>28.5M</td>
      <td>20.6G</td>
      <td>16.5K</td>
      <td>1.83K</td>
      <td>20130612</td>
      <td>9 min 47 s</td>
      <td>406967</td>
    </tr>
    <tr>
      <th>1597</th>
      <td>distant_time_and_the_hint_of_a_multiverse_sean...</td>
      <td>26.5M</td>
      <td>20.6G</td>
      <td>16.4K</td>
      <td>1.82K</td>
      <td>20130703</td>
      <td>15 min 54 s</td>
      <td>232937</td>
    </tr>
    <tr>
      <th>1598</th>
      <td>making_a_car_for_blind_drivers_dennis_hong</td>
      <td>20.6M</td>
      <td>20.7G</td>
      <td>16.4K</td>
      <td>1.82K</td>
      <td>20130329</td>
      <td>9 min 8 s</td>
      <td>315273</td>
    </tr>
    <tr>
      <th>1599</th>
      <td>atheism_2_0_alain_de_botton</td>
      <td>46.6M</td>
      <td>20.7G</td>
      <td>16.4K</td>
      <td>1.82K</td>
      <td>20130726</td>
      <td>19 min 20 s</td>
      <td>337177</td>
    </tr>
    <tr>
      <th>1600</th>
      <td>why_global_jihad_is_losing_bobby_ghosh</td>
      <td>30.8M</td>
      <td>20.7G</td>
      <td>16.0K</td>
      <td>1.78K</td>
      <td>20130619</td>
      <td>16 min 31 s</td>
      <td>260866</td>
    </tr>
    <tr>
      <th>1601</th>
      <td>tribal_leadership_david_logan</td>
      <td>34.7M</td>
      <td>20.8G</td>
      <td>16.0K</td>
      <td>1.78K</td>
      <td>20130717</td>
      <td>16 min 39 s</td>
      <td>291576</td>
    </tr>
    <tr>
      <th>1602</th>
      <td>how_your_mom_s_advice_could_save_the_human_race</td>
      <td>23.3M</td>
      <td>20.8G</td>
      <td>7.11K</td>
      <td>1.78K</td>
      <td>20180329</td>
      <td>9 min 22 s</td>
      <td>348020</td>
    </tr>
    <tr>
      <th>1603</th>
      <td>the_true_power_of_the_performing_arts_ben_cameron</td>
      <td>27.2M</td>
      <td>20.8G</td>
      <td>15.7K</td>
      <td>1.74K</td>
      <td>20130906</td>
      <td>12 min 44 s</td>
      <td>298569</td>
    </tr>
    <tr>
      <th>1604</th>
      <td>the_rise_of_human_computer_cooperation_shyam_s...</td>
      <td>20.1M</td>
      <td>20.8G</td>
      <td>15.6K</td>
      <td>1.73K</td>
      <td>20130615</td>
      <td>12 min 12 s</td>
      <td>229802</td>
    </tr>
    <tr>
      <th>1605</th>
      <td>we_need_a_moral_operating_system_damon_horowitz</td>
      <td>43.7M</td>
      <td>20.9G</td>
      <td>15.6K</td>
      <td>1.73K</td>
      <td>20130808</td>
      <td>16 min 18 s</td>
      <td>374997</td>
    </tr>
    <tr>
      <th>1606</th>
      <td>let_s_simplify_legal_jargon_alan_siegel</td>
      <td>9.12M</td>
      <td>20.9G</td>
      <td>15.4K</td>
      <td>1.71K</td>
      <td>20130218</td>
      <td>4 min 57 s</td>
      <td>257483</td>
    </tr>
    <tr>
      <th>1607</th>
      <td>a_cinematic_journey_through_visual_effects_don...</td>
      <td>20.5M</td>
      <td>20.9G</td>
      <td>15.3K</td>
      <td>1.70K</td>
      <td>20130519</td>
      <td>6 min 54 s</td>
      <td>414682</td>
    </tr>
    <tr>
      <th>1608</th>
      <td>your_online_life_permanent_as_a_tattoo_juan_en...</td>
      <td>8.77M</td>
      <td>20.9G</td>
      <td>15.3K</td>
      <td>1.70K</td>
      <td>20130830</td>
      <td>6 min 0 s</td>
      <td>203838</td>
    </tr>
    <tr>
      <th>1609</th>
      <td>the_game_layer_on_top_of_the_world_seth_prieba...</td>
      <td>22.2M</td>
      <td>20.9G</td>
      <td>15.2K</td>
      <td>1.68K</td>
      <td>20130906</td>
      <td>12 min 22 s</td>
      <td>250475</td>
    </tr>
    <tr>
      <th>1610</th>
      <td>what_doctors_don_t_know_about_the_drugs_they_p...</td>
      <td>29.1M</td>
      <td>21.0G</td>
      <td>15.1K</td>
      <td>1.68K</td>
      <td>20130531</td>
      <td>13 min 29 s</td>
      <td>302064</td>
    </tr>
    <tr>
      <th>1611</th>
      <td>meet_shahruz_ghaemi</td>
      <td>4.58M</td>
      <td>21.0G</td>
      <td>15.1K</td>
      <td>1.67K</td>
      <td>20130514</td>
      <td>1 min 58 s</td>
      <td>323596</td>
    </tr>
    <tr>
      <th>1612</th>
      <td>natural_pest_control_using_bugs_shimon_steinberg</td>
      <td>29.6M</td>
      <td>21.0G</td>
      <td>15.1K</td>
      <td>1.67K</td>
      <td>20130913</td>
      <td>15 min 23 s</td>
      <td>269280</td>
    </tr>
    <tr>
      <th>1613</th>
      <td>women_should_represent_women_in_media_megan_ka...</td>
      <td>21.3M</td>
      <td>21.0G</td>
      <td>15.0K</td>
      <td>1.67K</td>
      <td>20130821</td>
      <td>10 min 31 s</td>
      <td>283062</td>
    </tr>
    <tr>
      <th>1614</th>
      <td>why_democracy_matters_rory_stewart</td>
      <td>24.9M</td>
      <td>21.0G</td>
      <td>15.0K</td>
      <td>1.66K</td>
      <td>20130605</td>
      <td>13 min 41 s</td>
      <td>253958</td>
    </tr>
    <tr>
      <th>1615</th>
      <td>one_way_to_create_a_more_inclusive_school</td>
      <td>16.7M</td>
      <td>21.1G</td>
      <td>8.22K</td>
      <td>1.64K</td>
      <td>20170726</td>
      <td>8 min 18 s</td>
      <td>281139</td>
    </tr>
    <tr>
      <th>1616</th>
      <td>the_moral_dangers_of_non_lethal_weapons_stephe...</td>
      <td>52.0M</td>
      <td>21.1G</td>
      <td>14.8K</td>
      <td>1.64K</td>
      <td>20130714</td>
      <td>17 min 32 s</td>
      <td>414497</td>
    </tr>
    <tr>
      <th>1617</th>
      <td>the_science_behind_a_climate_headline_rachel_pike</td>
      <td>7.32M</td>
      <td>21.1G</td>
      <td>14.7K</td>
      <td>1.64K</td>
      <td>20130809</td>
      <td>4 min 13 s</td>
      <td>242298</td>
    </tr>
    <tr>
      <th>1618</th>
      <td>protecting_the_brain_against_concussion_kim_go...</td>
      <td>18.6M</td>
      <td>21.1G</td>
      <td>14.5K</td>
      <td>1.61K</td>
      <td>20130816</td>
      <td>9 min 21 s</td>
      <td>278317</td>
    </tr>
    <tr>
      <th>1619</th>
      <td>how_youtube_thinks_about_copyright_margaret_go...</td>
      <td>11.6M</td>
      <td>21.2G</td>
      <td>14.0K</td>
      <td>1.55K</td>
      <td>20130308</td>
      <td>5 min 46 s</td>
      <td>281131</td>
    </tr>
    <tr>
      <th>1620</th>
      <td>the_emergence_of_4d_printing_skylar_tibbits</td>
      <td>15.8M</td>
      <td>21.2G</td>
      <td>13.8K</td>
      <td>1.53K</td>
      <td>20130823</td>
      <td>8 min 26 s</td>
      <td>262146</td>
    </tr>
    <tr>
      <th>1621</th>
      <td>how_arduino_is_open_sourcing_imagination_massi...</td>
      <td>28.4M</td>
      <td>21.2G</td>
      <td>13.3K</td>
      <td>1.47K</td>
      <td>20130705</td>
      <td>15 min 46 s</td>
      <td>251734</td>
    </tr>
    <tr>
      <th>1622</th>
      <td>the_beautiful_nano_details_of_our_world_gary_g...</td>
      <td>18.9M</td>
      <td>21.2G</td>
      <td>11.8K</td>
      <td>1.47K</td>
      <td>20131211</td>
      <td>12 min 6 s</td>
      <td>218716</td>
    </tr>
    <tr>
      <th>1623</th>
      <td>how_to_use_experts_and_when_not_to_noreena_hertz</td>
      <td>37.2M</td>
      <td>21.3G</td>
      <td>13.2K</td>
      <td>1.46K</td>
      <td>20130824</td>
      <td>18 min 18 s</td>
      <td>283674</td>
    </tr>
    <tr>
      <th>1624</th>
      <td>religions_and_babies_hans_rosling</td>
      <td>22.2M</td>
      <td>21.3G</td>
      <td>13.1K</td>
      <td>1.46K</td>
      <td>20130821</td>
      <td>13 min 20 s</td>
      <td>232701</td>
    </tr>
    <tr>
      <th>1625</th>
      <td>the_evolution_of_the_human_head</td>
      <td>13.8M</td>
      <td>21.3G</td>
      <td>16.0K</td>
      <td>1.45K</td>
      <td>20110131</td>
      <td>5 min 3 s</td>
      <td>381886</td>
    </tr>
    <tr>
      <th>1626</th>
      <td>the_generation_that_s_remaking_china_yang_lan</td>
      <td>33.6M</td>
      <td>21.3G</td>
      <td>13.1K</td>
      <td>1.45K</td>
      <td>20130809</td>
      <td>17 min 14 s</td>
      <td>272635</td>
    </tr>
    <tr>
      <th>1627</th>
      <td>trust_morality_and_oxytocin_paul_zak</td>
      <td>37.0M</td>
      <td>21.4G</td>
      <td>12.7K</td>
      <td>1.42K</td>
      <td>20130809</td>
      <td>16 min 34 s</td>
      <td>312175</td>
    </tr>
    <tr>
      <th>1628</th>
      <td>how_i_m_preparing_to_get_alzheimer_s_alanna_sh...</td>
      <td>12.8M</td>
      <td>21.4G</td>
      <td>12.2K</td>
      <td>1.36K</td>
      <td>20130628</td>
      <td>20 min 28 s</td>
      <td>87115</td>
    </tr>
    <tr>
      <th>1629</th>
      <td>how_to_solve_traffic_jams_jonas_eliasson</td>
      <td>16.4M</td>
      <td>21.4G</td>
      <td>12.1K</td>
      <td>1.34K</td>
      <td>20130415</td>
      <td>8 min 27 s</td>
      <td>271048</td>
    </tr>
    <tr>
      <th>1630</th>
      <td>inside_an_antarctic_time_machine_lee_hotz</td>
      <td>14.9M</td>
      <td>21.4G</td>
      <td>11.8K</td>
      <td>1.31K</td>
      <td>20130810</td>
      <td>9 min 45 s</td>
      <td>213908</td>
    </tr>
    <tr>
      <th>1631</th>
      <td>using_unanswered_questions_to_teach_john_gensic</td>
      <td>8.99M</td>
      <td>21.4G</td>
      <td>11.8K</td>
      <td>1.31K</td>
      <td>20130620</td>
      <td>5 min 24 s</td>
      <td>232293</td>
    </tr>
    <tr>
      <th>1632</th>
      <td>a_future_lit_by_solar_energy</td>
      <td>34.4M</td>
      <td>21.4G</td>
      <td>5.18K</td>
      <td>1.29K</td>
      <td>20180202</td>
      <td>13 min 0 s</td>
      <td>369954</td>
    </tr>
    <tr>
      <th>1633</th>
      <td>a_global_culture_to_fight_extremism_maajid_nawaz</td>
      <td>43.1M</td>
      <td>21.5G</td>
      <td>11.3K</td>
      <td>1.25K</td>
      <td>20121215</td>
      <td>17 min 53 s</td>
      <td>336616</td>
    </tr>
    <tr>
      <th>1634</th>
      <td>a_radical_experiment_in_empathy_sam_richards</td>
      <td>31.9M</td>
      <td>21.5G</td>
      <td>11.2K</td>
      <td>1.24K</td>
      <td>20130815</td>
      <td>18 min 7 s</td>
      <td>246436</td>
    </tr>
    <tr>
      <th>1635</th>
      <td>want_to_help_someone_shut_up_and_listen_ernest...</td>
      <td>36.4M</td>
      <td>21.5G</td>
      <td>11.1K</td>
      <td>1.24K</td>
      <td>20130619</td>
      <td>17 min 9 s</td>
      <td>296501</td>
    </tr>
    <tr>
      <th>1636</th>
      <td>the_journey_across_the_high_wire_philippe_petit</td>
      <td>32.7M</td>
      <td>21.6G</td>
      <td>11.1K</td>
      <td>1.24K</td>
      <td>20130507</td>
      <td>19 min 7 s</td>
      <td>239274</td>
    </tr>
    <tr>
      <th>1637</th>
      <td>greening_the_ghetto_majora_carter</td>
      <td>50.5M</td>
      <td>21.6G</td>
      <td>11.1K</td>
      <td>1.23K</td>
      <td>20130727</td>
      <td>18 min 33 s</td>
      <td>380625</td>
    </tr>
    <tr>
      <th>1638</th>
      <td>gaming_for_understanding_brenda_brathwaite</td>
      <td>15.4M</td>
      <td>21.6G</td>
      <td>11.0K</td>
      <td>1.22K</td>
      <td>20130821</td>
      <td>9 min 23 s</td>
      <td>229294</td>
    </tr>
    <tr>
      <th>1639</th>
      <td>toward_a_science_of_simplicity_george_whitesides</td>
      <td>34.4M</td>
      <td>21.7G</td>
      <td>11.0K</td>
      <td>1.22K</td>
      <td>20130222</td>
      <td>19 min 5 s</td>
      <td>251848</td>
    </tr>
    <tr>
      <th>1640</th>
      <td>how_can_technology_transform_the_human_body_lu...</td>
      <td>8.98M</td>
      <td>21.7G</td>
      <td>11.0K</td>
      <td>1.22K</td>
      <td>20130419</td>
      <td>3 min 59 s</td>
      <td>314142</td>
    </tr>
    <tr>
      <th>1641</th>
      <td>agile_programming_for_your_family_bruce_feiler</td>
      <td>38.5M</td>
      <td>21.7G</td>
      <td>9.69K</td>
      <td>1.21K</td>
      <td>20131203</td>
      <td>18 min 0 s</td>
      <td>299156</td>
    </tr>
    <tr>
      <th>1642</th>
      <td>are_droids_taking_our_jobs_andrew_mcafee</td>
      <td>28.5M</td>
      <td>21.8G</td>
      <td>10.8K</td>
      <td>1.20K</td>
      <td>20130829</td>
      <td>14 min 7 s</td>
      <td>282235</td>
    </tr>
    <tr>
      <th>1643</th>
      <td>the_real_reason_for_brains_daniel_wolpert</td>
      <td>34.9M</td>
      <td>21.8G</td>
      <td>10.6K</td>
      <td>1.17K</td>
      <td>20130809</td>
      <td>19 min 59 s</td>
      <td>243708</td>
    </tr>
    <tr>
      <th>1644</th>
      <td>can_we_domesticate_germs_paul_ewald</td>
      <td>29.9M</td>
      <td>21.8G</td>
      <td>10.5K</td>
      <td>1.17K</td>
      <td>20130115</td>
      <td>17 min 49 s</td>
      <td>234283</td>
    </tr>
    <tr>
      <th>1645</th>
      <td>the_optimism_bias_tali_sharot</td>
      <td>30.9M</td>
      <td>21.8G</td>
      <td>10.4K</td>
      <td>1.16K</td>
      <td>20130426</td>
      <td>17 min 40 s</td>
      <td>244040</td>
    </tr>
    <tr>
      <th>1646</th>
      <td>the_key_to_growth_race_with_the_machines_erik_...</td>
      <td>19.7M</td>
      <td>21.9G</td>
      <td>10.4K</td>
      <td>1.15K</td>
      <td>20130830</td>
      <td>11 min 59 s</td>
      <td>229894</td>
    </tr>
    <tr>
      <th>1647</th>
      <td>our_failing_schools_enough_is_enough_geoffrey_...</td>
      <td>50.1M</td>
      <td>21.9G</td>
      <td>10.3K</td>
      <td>1.14K</td>
      <td>20130816</td>
      <td>17 min 10 s</td>
      <td>407577</td>
    </tr>
    <tr>
      <th>1648</th>
      <td>telling_my_whole_story_when_many_cultures_make...</td>
      <td>38.6M</td>
      <td>22.0G</td>
      <td>4.47K</td>
      <td>1.12K</td>
      <td>20171121</td>
      <td>12 min 54 s</td>
      <td>418407</td>
    </tr>
    <tr>
      <th>1649</th>
      <td>animating_a_photo_real_digital_face_paul_debevec</td>
      <td>10.2M</td>
      <td>22.0G</td>
      <td>10.0K</td>
      <td>1.12K</td>
      <td>20130717</td>
      <td>6 min 6 s</td>
      <td>233506</td>
    </tr>
    <tr>
      <th>1650</th>
      <td>click_your_fortune_episode_2_demo</td>
      <td>4.97M</td>
      <td>22.0G</td>
      <td>9.98K</td>
      <td>1.11K</td>
      <td>20130807</td>
      <td>3 min 25 s</td>
      <td>203185</td>
    </tr>
    <tr>
      <th>1651</th>
      <td>a_map_of_the_brain_allan_jones</td>
      <td>35.0M</td>
      <td>22.0G</td>
      <td>9.91K</td>
      <td>1.10K</td>
      <td>20130809</td>
      <td>15 min 21 s</td>
      <td>318298</td>
    </tr>
    <tr>
      <th>1652</th>
      <td>learning_from_a_barefoot_movement_bunker_roy</td>
      <td>37.1M</td>
      <td>22.0G</td>
      <td>9.79K</td>
      <td>1.09K</td>
      <td>20130809</td>
      <td>19 min 7 s</td>
      <td>271252</td>
    </tr>
    <tr>
      <th>1653</th>
      <td>ancient_wonders_captured_in_3d_ben_kacyra</td>
      <td>29.8M</td>
      <td>22.1G</td>
      <td>9.46K</td>
      <td>1.05K</td>
      <td>20130809</td>
      <td>12 min 20 s</td>
      <td>338199</td>
    </tr>
    <tr>
      <th>1654</th>
      <td>a_critical_examination_of_the_technology_in_ou...</td>
      <td>12.7M</td>
      <td>22.1G</td>
      <td>9.37K</td>
      <td>1.04K</td>
      <td>20130625</td>
      <td>7 min 19 s</td>
      <td>242377</td>
    </tr>
    <tr>
      <th>1655</th>
      <td>reinventing_the_encyclopedia_game_rives</td>
      <td>24.2M</td>
      <td>22.1G</td>
      <td>9.33K</td>
      <td>1.04K</td>
      <td>20130828</td>
      <td>10 min 45 s</td>
      <td>314044</td>
    </tr>
    <tr>
      <th>1656</th>
      <td>building_a_theater_that_remakes_itself_joshua_...</td>
      <td>30.5M</td>
      <td>22.1G</td>
      <td>9.09K</td>
      <td>1.01K</td>
      <td>20130717</td>
      <td>18 min 42 s</td>
      <td>228033</td>
    </tr>
    <tr>
      <th>1657</th>
      <td>sex_needs_a_new_metaphor_here_s_one_al_vernacchio</td>
      <td>13.8M</td>
      <td>22.1G</td>
      <td>9.05K</td>
      <td>1.00K</td>
      <td>20130816</td>
      <td>8 min 24 s</td>
      <td>229060</td>
    </tr>
    <tr>
      <th>1658</th>
      <td>how_we_ll_stop_polio_for_good_bruce_aylward</td>
      <td>38.7M</td>
      <td>22.2G</td>
      <td>8.95K</td>
      <td>0.99K</td>
      <td>20130329</td>
      <td>23 min 9 s</td>
      <td>233639</td>
    </tr>
    <tr>
      <th>1659</th>
      <td>hire_the_hackers_misha_glenny</td>
      <td>41.5M</td>
      <td>22.2G</td>
      <td>8.93K</td>
      <td>0.99K</td>
      <td>20130816</td>
      <td>18 min 39 s</td>
      <td>310865</td>
    </tr>
    <tr>
      <th>1660</th>
      <td>perspective_is_everything_rory_sutherland</td>
      <td>36.0M</td>
      <td>22.3G</td>
      <td>8.80K</td>
      <td>0.98K</td>
      <td>20130821</td>
      <td>18 min 24 s</td>
      <td>273360</td>
    </tr>
    <tr>
      <th>1661</th>
      <td>the_secret_of_the_bat_genome_emma_teeling</td>
      <td>32.3M</td>
      <td>22.3G</td>
      <td>8.64K</td>
      <td>983</td>
      <td>20130605</td>
      <td>16 min 25 s</td>
      <td>274800</td>
    </tr>
    <tr>
      <th>1662</th>
      <td>meet_global_corruption_s_hidden_players_charmi...</td>
      <td>31.3M</td>
      <td>22.3G</td>
      <td>8.50K</td>
      <td>966</td>
      <td>20130823</td>
      <td>14 min 30 s</td>
      <td>301933</td>
    </tr>
    <tr>
      <th>1663</th>
      <td>what_is_the_internet_really_andrew_blum</td>
      <td>17.1M</td>
      <td>22.3G</td>
      <td>8.48K</td>
      <td>964</td>
      <td>20130531</td>
      <td>8 min 44 s</td>
      <td>273898</td>
    </tr>
    <tr>
      <th>1664</th>
      <td>a_giant_bubble_for_debate_liz_diller</td>
      <td>18.5M</td>
      <td>22.4G</td>
      <td>8.45K</td>
      <td>961</td>
      <td>20130419</td>
      <td>12 min 6 s</td>
      <td>213318</td>
    </tr>
    <tr>
      <th>1665</th>
      <td>the_4_commandments_of_cities_eduardo_paes</td>
      <td>22.6M</td>
      <td>22.4G</td>
      <td>8.42K</td>
      <td>958</td>
      <td>20130712</td>
      <td>12 min 21 s</td>
      <td>255936</td>
    </tr>
    <tr>
      <th>1666</th>
      <td>we_need_better_drugs_now_francis_collins</td>
      <td>25.9M</td>
      <td>22.4G</td>
      <td>8.16K</td>
      <td>927</td>
      <td>20130830</td>
      <td>14 min 40 s</td>
      <td>246468</td>
    </tr>
    <tr>
      <th>1667</th>
      <td>trusting_the_ensemble_charles_hazlewood</td>
      <td>52.0M</td>
      <td>22.5G</td>
      <td>8.14K</td>
      <td>925</td>
      <td>20130809</td>
      <td>19 min 36 s</td>
      <td>370692</td>
    </tr>
    <tr>
      <th>1668</th>
      <td>what_fear_can_teach_us_karen_thompson_walker</td>
      <td>25.4M</td>
      <td>22.5G</td>
      <td>8.11K</td>
      <td>922</td>
      <td>20130517</td>
      <td>11 min 30 s</td>
      <td>308880</td>
    </tr>
    <tr>
      <th>1669</th>
      <td>what_we_re_learning_from_online_education_daph...</td>
      <td>40.9M</td>
      <td>22.5G</td>
      <td>7.91K</td>
      <td>900</td>
      <td>20130614</td>
      <td>20 min 40 s</td>
      <td>276498</td>
    </tr>
    <tr>
      <th>1670</th>
      <td>what_we_re_learning_from_5000_brains_read_mont...</td>
      <td>26.2M</td>
      <td>22.5G</td>
      <td>7.91K</td>
      <td>899</td>
      <td>20130531</td>
      <td>13 min 23 s</td>
      <td>273477</td>
    </tr>
    <tr>
      <th>1671</th>
      <td>weaving_narratives_in_museum_galleries_thomas_...</td>
      <td>34.8M</td>
      <td>22.6G</td>
      <td>7.91K</td>
      <td>899</td>
      <td>20130511</td>
      <td>16 min 36 s</td>
      <td>293218</td>
    </tr>
    <tr>
      <th>1672</th>
      <td>mining_minerals_from_seawater_damian_palin</td>
      <td>4.76M</td>
      <td>22.6G</td>
      <td>7.77K</td>
      <td>884</td>
      <td>20130705</td>
      <td>3 min 1 s</td>
      <td>220164</td>
    </tr>
    <tr>
      <th>1673</th>
      <td>how_poachers_became_caretakers_john_kasaona_gl...</td>
      <td>28.4M</td>
      <td>22.6G</td>
      <td>7.64K</td>
      <td>869</td>
      <td>20130310</td>
      <td>15 min 46 s</td>
      <td>251742</td>
    </tr>
    <tr>
      <th>1674</th>
      <td>shape_shifting_dinosaurs_jack_horner</td>
      <td>36.1M</td>
      <td>22.6G</td>
      <td>7.35K</td>
      <td>836</td>
      <td>20130815</td>
      <td>18 min 22 s</td>
      <td>274186</td>
    </tr>
    <tr>
      <th>1675</th>
      <td>texting_that_saves_lives_nancy_lublin</td>
      <td>12.3M</td>
      <td>22.7G</td>
      <td>7.30K</td>
      <td>830</td>
      <td>20130712</td>
      <td>5 min 24 s</td>
      <td>317881</td>
    </tr>
    <tr>
      <th>1676</th>
      <td>click_your_fortune_episode_3_demo</td>
      <td>5.18M</td>
      <td>22.7G</td>
      <td>7.29K</td>
      <td>829</td>
      <td>20130807</td>
      <td>3 min 31 s</td>
      <td>205525</td>
    </tr>
    <tr>
      <th>1677</th>
      <td>why_i_hold_on_to_my_grandmother_s_tales</td>
      <td>13.0M</td>
      <td>22.7G</td>
      <td>3.21K</td>
      <td>820</td>
      <td>20180117</td>
      <td>7 min 8 s</td>
      <td>253939</td>
    </tr>
    <tr>
      <th>1678</th>
      <td>obesity_hunger_1_global_food_issue_ellen_gusta...</td>
      <td>15.4M</td>
      <td>22.7G</td>
      <td>7.16K</td>
      <td>814</td>
      <td>20130801</td>
      <td>16 min 34 s</td>
      <td>130247</td>
    </tr>
    <tr>
      <th>1679</th>
      <td>a_broken_body_isn_t_a_broken_person_janine_she...</td>
      <td>34.8M</td>
      <td>22.7G</td>
      <td>7.08K</td>
      <td>805</td>
      <td>20130528</td>
      <td>18 min 57 s</td>
      <td>256244</td>
    </tr>
    <tr>
      <th>1680</th>
      <td>the_case_for_collaborative_consumption_rachel_...</td>
      <td>29.1M</td>
      <td>22.8G</td>
      <td>6.97K</td>
      <td>792</td>
      <td>20130717</td>
      <td>16 min 34 s</td>
      <td>245390</td>
    </tr>
    <tr>
      <th>1681</th>
      <td>ultrasound_surgery_healing_without_cuts_yoav_m...</td>
      <td>30.7M</td>
      <td>22.8G</td>
      <td>6.94K</td>
      <td>790</td>
      <td>20130719</td>
      <td>16 min 13 s</td>
      <td>265049</td>
    </tr>
    <tr>
      <th>1682</th>
      <td>how_to_defend_earth_from_asteroids_phil_plait</td>
      <td>22.7M</td>
      <td>22.8G</td>
      <td>6.94K</td>
      <td>789</td>
      <td>20130808</td>
      <td>14 min 16 s</td>
      <td>222574</td>
    </tr>
    <tr>
      <th>1683</th>
      <td>let_s_teach_kids_to_code_mitch_resnick</td>
      <td>29.1M</td>
      <td>22.8G</td>
      <td>6.92K</td>
      <td>787</td>
      <td>20130424</td>
      <td>16 min 48 s</td>
      <td>242327</td>
    </tr>
    <tr>
      <th>1684</th>
      <td>a_whistleblower_you_haven_t_heard_geert_chatrou</td>
      <td>21.9M</td>
      <td>22.9G</td>
      <td>6.92K</td>
      <td>786</td>
      <td>20130815</td>
      <td>11 min 56 s</td>
      <td>256334</td>
    </tr>
    <tr>
      <th>1685</th>
      <td>a_doctor_s_touch_abraham_verghese</td>
      <td>38.3M</td>
      <td>22.9G</td>
      <td>6.88K</td>
      <td>782</td>
      <td>20130816</td>
      <td>18 min 32 s</td>
      <td>288793</td>
    </tr>
    <tr>
      <th>1686</th>
      <td>how_we_found_the_giant_squid_edith_widder</td>
      <td>15.2M</td>
      <td>22.9G</td>
      <td>6.76K</td>
      <td>769</td>
      <td>20130830</td>
      <td>8 min 38 s</td>
      <td>246726</td>
    </tr>
    <tr>
      <th>1687</th>
      <td>a_plane_you_can_drive_anna_mracek_dietrich</td>
      <td>19.5M</td>
      <td>22.9G</td>
      <td>6.75K</td>
      <td>767</td>
      <td>20130809</td>
      <td>9 min 37 s</td>
      <td>283238</td>
    </tr>
    <tr>
      <th>1688</th>
      <td>a_civil_response_to_violence_emiliano_salinas</td>
      <td>20.4M</td>
      <td>22.9G</td>
      <td>6.66K</td>
      <td>757</td>
      <td>20130808</td>
      <td>12 min 17 s</td>
      <td>232158</td>
    </tr>
    <tr>
      <th>1689</th>
      <td>let_s_transform_energy_with_natural_gas_t_boon...</td>
      <td>34.6M</td>
      <td>23.0G</td>
      <td>6.65K</td>
      <td>756</td>
      <td>20130719</td>
      <td>19 min 42 s</td>
      <td>245664</td>
    </tr>
    <tr>
      <th>1690</th>
      <td>pool_medical_patents_save_lives_ellen_t_hoen</td>
      <td>18.6M</td>
      <td>23.0G</td>
      <td>6.63K</td>
      <td>754</td>
      <td>20130428</td>
      <td>11 min 16 s</td>
      <td>230821</td>
    </tr>
    <tr>
      <th>1691</th>
      <td>how_to_buy_happiness_michael_norton</td>
      <td>17.8M</td>
      <td>23.0G</td>
      <td>6.61K</td>
      <td>752</td>
      <td>20130821</td>
      <td>10 min 58 s</td>
      <td>226082</td>
    </tr>
    <tr>
      <th>1692</th>
      <td>re_examining_the_remix_lawrence_lessig</td>
      <td>28.9M</td>
      <td>23.0G</td>
      <td>6.58K</td>
      <td>748</td>
      <td>20130801</td>
      <td>18 min 45 s</td>
      <td>215319</td>
    </tr>
    <tr>
      <th>1693</th>
      <td>the_flavors_of_life_through_the_eyes_of_a_chef</td>
      <td>17.4M</td>
      <td>23.1G</td>
      <td>2.91K</td>
      <td>744</td>
      <td>20171130</td>
      <td>6 min 39 s</td>
      <td>365194</td>
    </tr>
    <tr>
      <th>1694</th>
      <td>what_nonprofits_can_learn_from_coca_cola_melin...</td>
      <td>33.8M</td>
      <td>23.1G</td>
      <td>6.50K</td>
      <td>739</td>
      <td>20130815</td>
      <td>16 min 28 s</td>
      <td>286996</td>
    </tr>
    <tr>
      <th>1695</th>
      <td>kids_need_structure_colin_powell</td>
      <td>33.4M</td>
      <td>23.1G</td>
      <td>6.48K</td>
      <td>737</td>
      <td>20130401</td>
      <td>17 min 46 s</td>
      <td>263030</td>
    </tr>
    <tr>
      <th>1696</th>
      <td>a_mini_robot_powered_by_your_phone_keller_rinaudo</td>
      <td>12.0M</td>
      <td>23.1G</td>
      <td>6.42K</td>
      <td>730</td>
      <td>20130823</td>
      <td>5 min 54 s</td>
      <td>284933</td>
    </tr>
    <tr>
      <th>1697</th>
      <td>meet_the_water_canary_sonaar_luthra</td>
      <td>5.73M</td>
      <td>23.1G</td>
      <td>6.40K</td>
      <td>728</td>
      <td>20130726</td>
      <td>3 min 37 s</td>
      <td>220475</td>
    </tr>
    <tr>
      <th>1698</th>
      <td>the_right_time_to_second_guess_yourself</td>
      <td>22.4M</td>
      <td>23.2G</td>
      <td>3.55K</td>
      <td>726</td>
      <td>20170810</td>
      <td>11 min 56 s</td>
      <td>261970</td>
    </tr>
    <tr>
      <th>1699</th>
      <td>how_you_can_help_fight_pediatric_cancer</td>
      <td>14.4M</td>
      <td>23.2G</td>
      <td>3.51K</td>
      <td>718</td>
      <td>20170608</td>
      <td>8 min 6 s</td>
      <td>247613</td>
    </tr>
    <tr>
      <th>1700</th>
      <td>the_future_race_car_150mph_and_no_driver_chris...</td>
      <td>29.8M</td>
      <td>23.2G</td>
      <td>6.30K</td>
      <td>717</td>
      <td>20130829</td>
      <td>10 min 47 s</td>
      <td>386111</td>
    </tr>
    <tr>
      <th>1701</th>
      <td>a_universal_translator_for_surgeons_steven_sch...</td>
      <td>19.3M</td>
      <td>23.2G</td>
      <td>6.27K</td>
      <td>713</td>
      <td>20130519</td>
      <td>11 min 41 s</td>
      <td>230884</td>
    </tr>
    <tr>
      <th>1702</th>
      <td>a_vision_of_crimes_in_the_future_marc_goodman</td>
      <td>20.6M</td>
      <td>23.2G</td>
      <td>6.25K</td>
      <td>711</td>
      <td>20130628</td>
      <td>8 min 44 s</td>
      <td>329923</td>
    </tr>
    <tr>
      <th>1703</th>
      <td>how_do_you_save_a_shark_you_know_nothing_about...</td>
      <td>35.7M</td>
      <td>23.3G</td>
      <td>6.17K</td>
      <td>701</td>
      <td>20130626</td>
      <td>16 min 46 s</td>
      <td>297692</td>
    </tr>
    <tr>
      <th>1704</th>
      <td>let_s_put_birth_control_back_on_the_agenda_mel...</td>
      <td>55.2M</td>
      <td>23.3G</td>
      <td>6.04K</td>
      <td>687</td>
      <td>20130605</td>
      <td>25 min 36 s</td>
      <td>301447</td>
    </tr>
    <tr>
      <th>1705</th>
      <td>a_father_daughter_dance_in_prison_angela_patton</td>
      <td>22.3M</td>
      <td>23.4G</td>
      <td>5.37K</td>
      <td>686</td>
      <td>20131211</td>
      <td>8 min 48 s</td>
      <td>353499</td>
    </tr>
    <tr>
      <th>1706</th>
      <td>the_good_news_on_poverty_yes_there_s_good_news...</td>
      <td>24.9M</td>
      <td>23.4G</td>
      <td>5.96K</td>
      <td>678</td>
      <td>20130823</td>
      <td>13 min 57 s</td>
      <td>249200</td>
    </tr>
    <tr>
      <th>1707</th>
      <td>what_we_learn_before_we_re_born_annie_murphy_paul</td>
      <td>21.3M</td>
      <td>23.4G</td>
      <td>5.95K</td>
      <td>676</td>
      <td>20130809</td>
      <td>8 min 44 s</td>
      <td>340362</td>
    </tr>
    <tr>
      <th>1708</th>
      <td>sometimes_it_s_good_to_give_up_the_driver_s_se...</td>
      <td>24.8M</td>
      <td>23.4G</td>
      <td>5.89K</td>
      <td>670</td>
      <td>20130501</td>
      <td>9 min 47 s</td>
      <td>354403</td>
    </tr>
    <tr>
      <th>1709</th>
      <td>unlock_the_intelligence_passion_greatness_of_g...</td>
      <td>44.7M</td>
      <td>23.5G</td>
      <td>5.81K</td>
      <td>661</td>
      <td>20130712</td>
      <td>20 min 28 s</td>
      <td>305223</td>
    </tr>
    <tr>
      <th>1710</th>
      <td>1000_tedtalks_6_words_sebastian_wernicke</td>
      <td>13.3M</td>
      <td>23.5G</td>
      <td>5.75K</td>
      <td>654</td>
      <td>20130815</td>
      <td>7 min 33 s</td>
      <td>246048</td>
    </tr>
    <tr>
      <th>1711</th>
      <td>a_prosthetic_arm_that_feels_todd_kuiken</td>
      <td>38.2M</td>
      <td>23.5G</td>
      <td>5.75K</td>
      <td>653</td>
      <td>20130809</td>
      <td>18 min 51 s</td>
      <td>283656</td>
    </tr>
    <tr>
      <th>1712</th>
      <td>my_friend_richard_feynman_leonard_susskind</td>
      <td>27.6M</td>
      <td>23.5G</td>
      <td>5.64K</td>
      <td>641</td>
      <td>20130815</td>
      <td>14 min 41 s</td>
      <td>262607</td>
    </tr>
    <tr>
      <th>1713</th>
      <td>a_child_of_the_state_lemn_sissay</td>
      <td>29.0M</td>
      <td>23.6G</td>
      <td>4.99K</td>
      <td>638</td>
      <td>20131211</td>
      <td>15 min 36 s</td>
      <td>260032</td>
    </tr>
    <tr>
      <th>1714</th>
      <td>experiments_that_hint_of_longer_lives_cynthia_...</td>
      <td>31.1M</td>
      <td>23.6G</td>
      <td>5.51K</td>
      <td>626</td>
      <td>20130809</td>
      <td>16 min 23 s</td>
      <td>265307</td>
    </tr>
    <tr>
      <th>1715</th>
      <td>using_nature_to_grow_batteries_angela_belcher</td>
      <td>19.7M</td>
      <td>23.6G</td>
      <td>5.51K</td>
      <td>626</td>
      <td>20130815</td>
      <td>10 min 25 s</td>
      <td>263752</td>
    </tr>
    <tr>
      <th>1716</th>
      <td>could_the_sun_be_good_for_your_heart_richard_w...</td>
      <td>23.7M</td>
      <td>23.6G</td>
      <td>5.45K</td>
      <td>620</td>
      <td>20130325</td>
      <td>12 min 59 s</td>
      <td>255197</td>
    </tr>
    <tr>
      <th>1717</th>
      <td>energy_from_floating_algae_pods_jonathan_trent</td>
      <td>30.6M</td>
      <td>23.7G</td>
      <td>5.41K</td>
      <td>615</td>
      <td>20130607</td>
      <td>14 min 45 s</td>
      <td>289624</td>
    </tr>
    <tr>
      <th>1718</th>
      <td>crowdsource_your_health_lucien_engelen</td>
      <td>14.6M</td>
      <td>23.7G</td>
      <td>5.35K</td>
      <td>609</td>
      <td>20130815</td>
      <td>6 min 12 s</td>
      <td>327705</td>
    </tr>
    <tr>
      <th>1719</th>
      <td>before_i_die_i_want_to_candy_chang</td>
      <td>11.3M</td>
      <td>23.7G</td>
      <td>5.31K</td>
      <td>604</td>
      <td>20130614</td>
      <td>6 min 19 s</td>
      <td>250429</td>
    </tr>
    <tr>
      <th>1720</th>
      <td>where_is_home_pico_iyer</td>
      <td>31.2M</td>
      <td>23.7G</td>
      <td>5.30K</td>
      <td>603</td>
      <td>20130823</td>
      <td>14 min 4 s</td>
      <td>309872</td>
    </tr>
    <tr>
      <th>1721</th>
      <td>the_dance_of_the_dung_beetle_marcus_byrne</td>
      <td>35.9M</td>
      <td>23.8G</td>
      <td>5.28K</td>
      <td>600</td>
      <td>20130429</td>
      <td>17 min 8 s</td>
      <td>292995</td>
    </tr>
    <tr>
      <th>1722</th>
      <td>lessons_from_death_row_inmates_david_r_dow</td>
      <td>32.2M</td>
      <td>23.8G</td>
      <td>5.19K</td>
      <td>590</td>
      <td>20130821</td>
      <td>18 min 16 s</td>
      <td>245943</td>
    </tr>
    <tr>
      <th>1723</th>
      <td>mental_health_for_all_by_involving_all_vikram_...</td>
      <td>32.5M</td>
      <td>23.8G</td>
      <td>5.11K</td>
      <td>581</td>
      <td>20130607</td>
      <td>12 min 22 s</td>
      <td>366785</td>
    </tr>
    <tr>
      <th>1724</th>
      <td>how_healthy_living_nearly_killed_me_a_j_jacobs</td>
      <td>14.8M</td>
      <td>23.8G</td>
      <td>5.05K</td>
      <td>574</td>
      <td>20130726</td>
      <td>8 min 42 s</td>
      <td>237793</td>
    </tr>
    <tr>
      <th>1725</th>
      <td>how_do_we_heal_medicine_atul_gawande</td>
      <td>33.9M</td>
      <td>23.9G</td>
      <td>5.02K</td>
      <td>570</td>
      <td>20130419</td>
      <td>19 min 19 s</td>
      <td>245187</td>
    </tr>
    <tr>
      <th>1726</th>
      <td>what_s_a_snollygoster_a_short_lesson_in_politi...</td>
      <td>15.6M</td>
      <td>23.9G</td>
      <td>4.99K</td>
      <td>567</td>
      <td>20130410</td>
      <td>6 min 39 s</td>
      <td>328286</td>
    </tr>
    <tr>
      <th>1727</th>
      <td>science_is_for_everyone_kids_included_beau_lot...</td>
      <td>37.9M</td>
      <td>23.9G</td>
      <td>4.91K</td>
      <td>558</td>
      <td>20130524</td>
      <td>15 min 25 s</td>
      <td>343462</td>
    </tr>
    <tr>
      <th>1728</th>
      <td>how_to_topple_a_dictator_srdja_popovic</td>
      <td>37.9M</td>
      <td>24.0G</td>
      <td>4.86K</td>
      <td>553</td>
      <td>20130815</td>
      <td>12 min 3 s</td>
      <td>439720</td>
    </tr>
    <tr>
      <th>1729</th>
      <td>let_s_prepare_for_our_new_climate_vicki_arroyo</td>
      <td>21.3M</td>
      <td>24.0G</td>
      <td>4.86K</td>
      <td>553</td>
      <td>20130524</td>
      <td>10 min 38 s</td>
      <td>279143</td>
    </tr>
    <tr>
      <th>1730</th>
      <td>parkinson_s_depression_and_the_switch_that_mig...</td>
      <td>24.7M</td>
      <td>24.0G</td>
      <td>4.66K</td>
      <td>530</td>
      <td>20130612</td>
      <td>15 min 34 s</td>
      <td>222034</td>
    </tr>
    <tr>
      <th>1731</th>
      <td>gaming_to_re_engage_boys_in_learning_ali_carr_...</td>
      <td>24.5M</td>
      <td>24.0G</td>
      <td>4.60K</td>
      <td>522</td>
      <td>20130815</td>
      <td>12 min 30 s</td>
      <td>273708</td>
    </tr>
    <tr>
      <th>1732</th>
      <td>neuroscience_game_theory_monkeys_colin_camerer</td>
      <td>21.7M</td>
      <td>24.1G</td>
      <td>4.56K</td>
      <td>519</td>
      <td>20130619</td>
      <td>13 min 49 s</td>
      <td>219212</td>
    </tr>
    <tr>
      <th>1733</th>
      <td>the_voice_of_the_natural_world_bernie_krause</td>
      <td>34.1M</td>
      <td>24.1G</td>
      <td>4.48K</td>
      <td>509</td>
      <td>20130816</td>
      <td>14 min 51 s</td>
      <td>320770</td>
    </tr>
    <tr>
      <th>1734</th>
      <td>the_single_biggest_health_threat_women_face_no...</td>
      <td>31.5M</td>
      <td>24.1G</td>
      <td>4.45K</td>
      <td>505</td>
      <td>20130506</td>
      <td>15 min 59 s</td>
      <td>274979</td>
    </tr>
    <tr>
      <th>1735</th>
      <td>a_choreographer_s_creative_process_in_real_tim...</td>
      <td>43.7M</td>
      <td>24.2G</td>
      <td>4.44K</td>
      <td>505</td>
      <td>20130607</td>
      <td>15 min 18 s</td>
      <td>399183</td>
    </tr>
    <tr>
      <th>1736</th>
      <td>we_the_people_and_the_republic_we_must_reclaim...</td>
      <td>34.1M</td>
      <td>24.2G</td>
      <td>4.40K</td>
      <td>500</td>
      <td>20130823</td>
      <td>18 min 22 s</td>
      <td>259499</td>
    </tr>
    <tr>
      <th>1737</th>
      <td>how_to_expose_the_corrupt_peter_eigen</td>
      <td>26.9M</td>
      <td>24.2G</td>
      <td>4.38K</td>
      <td>498</td>
      <td>20130725</td>
      <td>16 min 12 s</td>
      <td>231766</td>
    </tr>
    <tr>
      <th>1738</th>
      <td>michael_green_why_we_should_build_wooden_skysc...</td>
      <td>23.7M</td>
      <td>24.2G</td>
      <td>4.38K</td>
      <td>498</td>
      <td>20130816</td>
      <td>12 min 25 s</td>
      <td>266990</td>
    </tr>
    <tr>
      <th>1739</th>
      <td>inside_the_egyptian_revolution_wael_ghonim</td>
      <td>26.8M</td>
      <td>24.3G</td>
      <td>4.37K</td>
      <td>497</td>
      <td>20130725</td>
      <td>10 min 7 s</td>
      <td>370206</td>
    </tr>
    <tr>
      <th>1740</th>
      <td>a_clean_energy_proposal_race_to_the_top_jennif...</td>
      <td>27.2M</td>
      <td>24.3G</td>
      <td>4.37K</td>
      <td>496</td>
      <td>20130830</td>
      <td>12 min 41 s</td>
      <td>299333</td>
    </tr>
    <tr>
      <th>1741</th>
      <td>how_i_taught_rats_to_sniff_out_land_mines_bart...</td>
      <td>22.5M</td>
      <td>24.3G</td>
      <td>4.26K</td>
      <td>484</td>
      <td>20130801</td>
      <td>12 min 11 s</td>
      <td>257804</td>
    </tr>
    <tr>
      <th>1742</th>
      <td>the_shared_experience_of_absurdity_charlie_todd</td>
      <td>32.2M</td>
      <td>24.4G</td>
      <td>4.23K</td>
      <td>481</td>
      <td>20130808</td>
      <td>12 min 4 s</td>
      <td>372746</td>
    </tr>
    <tr>
      <th>1743</th>
      <td>could_tissue_engineering_mean_personalized_med...</td>
      <td>10.3M</td>
      <td>24.4G</td>
      <td>4.19K</td>
      <td>476</td>
      <td>20130517</td>
      <td>6 min 19 s</td>
      <td>226531</td>
    </tr>
    <tr>
      <th>1744</th>
      <td>my_immigration_story_tan_le</td>
      <td>26.7M</td>
      <td>24.4G</td>
      <td>4.08K</td>
      <td>463</td>
      <td>20130815</td>
      <td>12 min 16 s</td>
      <td>304405</td>
    </tr>
    <tr>
      <th>1745</th>
      <td>older_people_are_happier_laura_carstensen</td>
      <td>20.9M</td>
      <td>24.4G</td>
      <td>4.04K</td>
      <td>459</td>
      <td>20130821</td>
      <td>11 min 38 s</td>
      <td>251296</td>
    </tr>
    <tr>
      <th>1746</th>
      <td>we_can_recycle_plastic_mike_biddle</td>
      <td>22.4M</td>
      <td>24.4G</td>
      <td>3.97K</td>
      <td>451</td>
      <td>20130809</td>
      <td>10 min 58 s</td>
      <td>285426</td>
    </tr>
    <tr>
      <th>1747</th>
      <td>print_your_own_medicine_lee_cronin</td>
      <td>5.44M</td>
      <td>24.4G</td>
      <td>3.93K</td>
      <td>447</td>
      <td>20130510</td>
      <td>3 min 6 s</td>
      <td>244453</td>
    </tr>
    <tr>
      <th>1748</th>
      <td>how_to_look_inside_the_brain_carl_schoonover</td>
      <td>9.04M</td>
      <td>24.4G</td>
      <td>3.89K</td>
      <td>442</td>
      <td>20130712</td>
      <td>4 min 59 s</td>
      <td>253123</td>
    </tr>
    <tr>
      <th>1749</th>
      <td>building_unimaginable_shapes_michael_hansmeyer</td>
      <td>24.9M</td>
      <td>24.5G</td>
      <td>3.83K</td>
      <td>436</td>
      <td>20130621</td>
      <td>11 min 7 s</td>
      <td>313347</td>
    </tr>
    <tr>
      <th>1750</th>
      <td>how_to_step_up_in_the_face_of_disaster_caitria...</td>
      <td>19.7M</td>
      <td>24.5G</td>
      <td>3.77K</td>
      <td>428</td>
      <td>20130829</td>
      <td>9 min 23 s</td>
      <td>293566</td>
    </tr>
    <tr>
      <th>1751</th>
      <td>a_prosthetic_eye_to_treat_blindness_sheila_nir...</td>
      <td>19.1M</td>
      <td>24.5G</td>
      <td>3.66K</td>
      <td>416</td>
      <td>20130726</td>
      <td>10 min 5 s</td>
      <td>265064</td>
    </tr>
    <tr>
      <th>1752</th>
      <td>embrace_the_remix_kirby_ferguson</td>
      <td>17.5M</td>
      <td>24.5G</td>
      <td>3.52K</td>
      <td>400</td>
      <td>20130510</td>
      <td>9 min 42 s</td>
      <td>252445</td>
    </tr>
    <tr>
      <th>1753</th>
      <td>advice_to_young_scientists_e_o_wilson</td>
      <td>27.0M</td>
      <td>24.6G</td>
      <td>3.44K</td>
      <td>391</td>
      <td>20130705</td>
      <td>14 min 56 s</td>
      <td>252301</td>
    </tr>
    <tr>
      <th>1754</th>
      <td>the_strange_politics_of_disgust_david_pizarro</td>
      <td>27.5M</td>
      <td>24.6G</td>
      <td>3.37K</td>
      <td>383</td>
      <td>20130408</td>
      <td>14 min 2 s</td>
      <td>273724</td>
    </tr>
    <tr>
      <th>1755</th>
      <td>what_s_left_to_explore_nathan_wolfe</td>
      <td>14.1M</td>
      <td>24.6G</td>
      <td>3.31K</td>
      <td>377</td>
      <td>20130507</td>
      <td>7 min 10 s</td>
      <td>274600</td>
    </tr>
    <tr>
      <th>1756</th>
      <td>what_if_our_healthcare_system_kept_us_healthy_...</td>
      <td>29.6M</td>
      <td>24.6G</td>
      <td>3.31K</td>
      <td>376</td>
      <td>20130705</td>
      <td>16 min 34 s</td>
      <td>249614</td>
    </tr>
    <tr>
      <th>1757</th>
      <td>visualizing_the_medical_data_explosion_anders_...</td>
      <td>25.7M</td>
      <td>24.6G</td>
      <td>3.26K</td>
      <td>371</td>
      <td>20130710</td>
      <td>16 min 34 s</td>
      <td>216509</td>
    </tr>
    <tr>
      <th>1758</th>
      <td>the_100000_student_classroom_peter_norvig</td>
      <td>11.4M</td>
      <td>24.7G</td>
      <td>3.22K</td>
      <td>366</td>
      <td>20130705</td>
      <td>6 min 11 s</td>
      <td>257566</td>
    </tr>
    <tr>
      <th>1759</th>
      <td>a_teacher_growing_green_in_the_south_bronx_ste...</td>
      <td>31.5M</td>
      <td>24.7G</td>
      <td>3.21K</td>
      <td>365</td>
      <td>20130829</td>
      <td>13 min 42 s</td>
      <td>321095</td>
    </tr>
    <tr>
      <th>1760</th>
      <td>tracking_the_trackers_gary_kovacs</td>
      <td>11.2M</td>
      <td>24.7G</td>
      <td>3.21K</td>
      <td>364</td>
      <td>20130426</td>
      <td>6 min 39 s</td>
      <td>234870</td>
    </tr>
    <tr>
      <th>1761</th>
      <td>fighting_with_non_violence_scilla_elworthy</td>
      <td>13.8M</td>
      <td>24.7G</td>
      <td>3.19K</td>
      <td>362</td>
      <td>20130619</td>
      <td>8 min 44 s</td>
      <td>221284</td>
    </tr>
    <tr>
      <th>1762</th>
      <td>why_architects_need_to_use_their_ears_julian_t...</td>
      <td>16.5M</td>
      <td>24.7G</td>
      <td>3.11K</td>
      <td>353</td>
      <td>20130531</td>
      <td>9 min 51 s</td>
      <td>234554</td>
    </tr>
    <tr>
      <th>1763</th>
      <td>the_secret_lives_of_paintings_maurizio_seracini</td>
      <td>21.8M</td>
      <td>24.8G</td>
      <td>2.91K</td>
      <td>331</td>
      <td>20130524</td>
      <td>12 min 34 s</td>
      <td>242803</td>
    </tr>
    <tr>
      <th>1764</th>
      <td>what_s_your_200_year_plan_raghava_kk</td>
      <td>20.8M</td>
      <td>24.8G</td>
      <td>2.92K</td>
      <td>331</td>
      <td>20130829</td>
      <td>10 min 58 s</td>
      <td>264901</td>
    </tr>
    <tr>
      <th>1765</th>
      <td>be_an_artist_right_now_young_ha_kim</td>
      <td>38.2M</td>
      <td>24.8G</td>
      <td>2.85K</td>
      <td>324</td>
      <td>20130612</td>
      <td>16 min 57 s</td>
      <td>314816</td>
    </tr>
    <tr>
      <th>1766</th>
      <td>life_s_third_act_jane_fonda</td>
      <td>26.0M</td>
      <td>24.8G</td>
      <td>2.85K</td>
      <td>324</td>
      <td>20130815</td>
      <td>11 min 20 s</td>
      <td>320792</td>
    </tr>
    <tr>
      <th>1767</th>
      <td>making_sense_of_maps_aris_venetikidis</td>
      <td>36.0M</td>
      <td>24.9G</td>
      <td>2.82K</td>
      <td>321</td>
      <td>20130529</td>
      <td>16 min 35 s</td>
      <td>303255</td>
    </tr>
    <tr>
      <th>1768</th>
      <td>fighting_a_contagious_cancer_elizabeth_murchison</td>
      <td>26.7M</td>
      <td>24.9G</td>
      <td>2.77K</td>
      <td>314</td>
      <td>20130816</td>
      <td>13 min 3 s</td>
      <td>285996</td>
    </tr>
    <tr>
      <th>1769</th>
      <td>tracking_ancient_diseases_using_plaque_christi...</td>
      <td>9.05M</td>
      <td>24.9G</td>
      <td>2.74K</td>
      <td>311</td>
      <td>20130712</td>
      <td>5 min 31 s</td>
      <td>229033</td>
    </tr>
    <tr>
      <th>1770</th>
      <td>experiments_that_point_to_a_new_understanding_...</td>
      <td>36.7M</td>
      <td>24.9G</td>
      <td>2.73K</td>
      <td>310</td>
      <td>20130628</td>
      <td>16 min 17 s</td>
      <td>315143</td>
    </tr>
    <tr>
      <th>1771</th>
      <td>cloudy_with_a_chance_of_joy_gavin_pretor_pinney</td>
      <td>18.9M</td>
      <td>25.0G</td>
      <td>2.73K</td>
      <td>310</td>
      <td>20130816</td>
      <td>10 min 57 s</td>
      <td>241567</td>
    </tr>
    <tr>
      <th>1772</th>
      <td>design_for_people_not_awards_timothy_prestero</td>
      <td>20.8M</td>
      <td>25.0G</td>
      <td>2.72K</td>
      <td>309</td>
      <td>20130829</td>
      <td>11 min 4 s</td>
      <td>262976</td>
    </tr>
    <tr>
      <th>1773</th>
      <td>the_art_of_creating_awe_rob_legato</td>
      <td>50.3M</td>
      <td>25.0G</td>
      <td>2.56K</td>
      <td>291</td>
      <td>20130614</td>
      <td>16 min 27 s</td>
      <td>427329</td>
    </tr>
    <tr>
      <th>1774</th>
      <td>can_democracy_exist_without_trust_ivan_krastev</td>
      <td>27.9M</td>
      <td>25.1G</td>
      <td>2.53K</td>
      <td>287</td>
      <td>20130510</td>
      <td>14 min 4 s</td>
      <td>276692</td>
    </tr>
    <tr>
      <th>1775</th>
      <td>the_promise_of_research_with_stem_cells_susan_...</td>
      <td>24.4M</td>
      <td>25.1G</td>
      <td>2.42K</td>
      <td>275</td>
      <td>20130607</td>
      <td>15 min 31 s</td>
      <td>220244</td>
    </tr>
    <tr>
      <th>1776</th>
      <td>a_census_of_the_ocean_paul_snelgrove</td>
      <td>27.5M</td>
      <td>25.1G</td>
      <td>2.39K</td>
      <td>271</td>
      <td>20130719</td>
      <td>16 min 47 s</td>
      <td>229353</td>
    </tr>
    <tr>
      <th>1777</th>
      <td>finding_life_we_can_t_imagine_christoph_adami</td>
      <td>41.4M</td>
      <td>25.1G</td>
      <td>2.38K</td>
      <td>270</td>
      <td>20130808</td>
      <td>18 min 51 s</td>
      <td>306735</td>
    </tr>
    <tr>
      <th>1778</th>
      <td>your_phone_company_is_watching_malte_spitz</td>
      <td>27.3M</td>
      <td>25.2G</td>
      <td>2.32K</td>
      <td>264</td>
      <td>20130621</td>
      <td>10 min 10 s</td>
      <td>374691</td>
    </tr>
    <tr>
      <th>1779</th>
      <td>welcome_to_the_genomic_revolution_richard_resnick</td>
      <td>20.1M</td>
      <td>25.2G</td>
      <td>2.32K</td>
      <td>263</td>
      <td>20130703</td>
      <td>11 min 2 s</td>
      <td>254242</td>
    </tr>
    <tr>
      <th>1780</th>
      <td>technology_s_epic_story_kevin_kelly</td>
      <td>31.7M</td>
      <td>25.2G</td>
      <td>2.28K</td>
      <td>259</td>
      <td>20130725</td>
      <td>16 min 32 s</td>
      <td>267854</td>
    </tr>
    <tr>
      <th>1781</th>
      <td>freeing_energy_from_the_grid_justin_hall_tipping</td>
      <td>30.8M</td>
      <td>25.3G</td>
      <td>2.21K</td>
      <td>251</td>
      <td>20130809</td>
      <td>12 min 45 s</td>
      <td>337256</td>
    </tr>
    <tr>
      <th>1782</th>
      <td>excuse_me_may_i_rent_your_car_robin_chase</td>
      <td>31.3M</td>
      <td>25.3G</td>
      <td>2.14K</td>
      <td>243</td>
      <td>20130517</td>
      <td>12 min 24 s</td>
      <td>352605</td>
    </tr>
    <tr>
      <th>1783</th>
      <td>the_economic_injustice_of_plastic_van_jones</td>
      <td>41.7M</td>
      <td>25.3G</td>
      <td>2.09K</td>
      <td>238</td>
      <td>20130808</td>
      <td>17 min 33 s</td>
      <td>331828</td>
    </tr>
    <tr>
      <th>1784</th>
      <td>how_open_data_is_changing_international_aid_sa...</td>
      <td>31.8M</td>
      <td>25.4G</td>
      <td>2.09K</td>
      <td>237</td>
      <td>20130517</td>
      <td>15 min 20 s</td>
      <td>290169</td>
    </tr>
    <tr>
      <th>1785</th>
      <td>a_girl_who_demanded_school_kakenya_ntaiya</td>
      <td>44.2M</td>
      <td>25.4G</td>
      <td>2.06K</td>
      <td>234</td>
      <td>20130513</td>
      <td>15 min 16 s</td>
      <td>404565</td>
    </tr>
    <tr>
      <th>1786</th>
      <td>demand_a_fair_trade_cell_phone_bandi_mbubi</td>
      <td>15.2M</td>
      <td>25.4G</td>
      <td>2.03K</td>
      <td>230</td>
      <td>20130829</td>
      <td>9 min 21 s</td>
      <td>227216</td>
    </tr>
    <tr>
      <th>1787</th>
      <td>what_your_designs_say_about_you_sebastian_dete...</td>
      <td>18.0M</td>
      <td>25.4G</td>
      <td>1.95K</td>
      <td>221</td>
      <td>20130821</td>
      <td>12 min 20 s</td>
      <td>203631</td>
    </tr>
    <tr>
      <th>1788</th>
      <td>demand_a_more_open_source_government_beth_noveck</td>
      <td>41.4M</td>
      <td>25.5G</td>
      <td>1.91K</td>
      <td>217</td>
      <td>20130607</td>
      <td>17 min 23 s</td>
      <td>333166</td>
    </tr>
    <tr>
      <th>1789</th>
      <td>a_story_about_knots_and_surgeons_ed_gavagan</td>
      <td>24.7M</td>
      <td>25.5G</td>
      <td>1.84K</td>
      <td>209</td>
      <td>20130531</td>
      <td>12 min 21 s</td>
      <td>279567</td>
    </tr>
    <tr>
      <th>1790</th>
      <td>let_s_pool_our_medical_data_john_wilbanks</td>
      <td>32.1M</td>
      <td>25.5G</td>
      <td>1.75K</td>
      <td>198</td>
      <td>20130524</td>
      <td>16 min 25 s</td>
      <td>273151</td>
    </tr>
    <tr>
      <th>1791</th>
      <td>a_lab_the_size_of_a_postage_stamp_george_white...</td>
      <td>26.3M</td>
      <td>25.6G</td>
      <td>1.65K</td>
      <td>187</td>
      <td>20130808</td>
      <td>16 min 16 s</td>
      <td>225764</td>
    </tr>
    <tr>
      <th>1792</th>
      <td>a_test_for_parkinson_s_with_a_phone_call_max_l...</td>
      <td>12.5M</td>
      <td>25.6G</td>
      <td>1.65K</td>
      <td>187</td>
      <td>20130614</td>
      <td>6 min 3 s</td>
      <td>288191</td>
    </tr>
    <tr>
      <th>1793</th>
      <td>ethical_riddles_in_hiv_research_boghuma_kabise...</td>
      <td>20.8M</td>
      <td>25.6G</td>
      <td>1.64K</td>
      <td>186</td>
      <td>20130605</td>
      <td>11 min 10 s</td>
      <td>260600</td>
    </tr>
    <tr>
      <th>1794</th>
      <td>massive_scale_online_collaboration_luis_von_ahn</td>
      <td>32.2M</td>
      <td>25.6G</td>
      <td>1.61K</td>
      <td>183</td>
      <td>20130808</td>
      <td>16 min 39 s</td>
      <td>270177</td>
    </tr>
    <tr>
      <th>1795</th>
      <td>a_short_intro_to_the_studio_school_geoff_mulgan</td>
      <td>8.79M</td>
      <td>25.6G</td>
      <td>1.49K</td>
      <td>169</td>
      <td>20130816</td>
      <td>6 min 16 s</td>
      <td>196168</td>
    </tr>
    <tr>
      <th>1796</th>
      <td>3_stories_of_local_eco_entrepreneurship_majora...</td>
      <td>27.2M</td>
      <td>25.7G</td>
      <td>1.46K</td>
      <td>165</td>
      <td>20130725</td>
      <td>16 min 34 s</td>
      <td>229255</td>
    </tr>
    <tr>
      <th>1797</th>
      <td>put_a_value_on_nature_pavan_sukhdev</td>
      <td>31.9M</td>
      <td>25.7G</td>
      <td>1.45K</td>
      <td>165</td>
      <td>20130726</td>
      <td>16 min 30 s</td>
      <td>270182</td>
    </tr>
    <tr>
      <th>1798</th>
      <td>how_to_stop_torture_karen_tse</td>
      <td>20.1M</td>
      <td>25.7G</td>
      <td>1.32K</td>
      <td>150</td>
      <td>20130809</td>
      <td>8 min 44 s</td>
      <td>322088</td>
    </tr>
    <tr>
      <th>1799</th>
      <td>how_cyberattacks_threaten_real_world_peace_guy...</td>
      <td>13.5M</td>
      <td>25.7G</td>
      <td>1.31K</td>
      <td>149</td>
      <td>20130808</td>
      <td>9 min 23 s</td>
      <td>200531</td>
    </tr>
    <tr>
      <th>1800</th>
      <td>the_day_i_turned_down_tim_berners_lee_ian_ritchie</td>
      <td>10.7M</td>
      <td>25.7G</td>
      <td>1.27K</td>
      <td>144</td>
      <td>20130809</td>
      <td>5 min 41 s</td>
      <td>262294</td>
    </tr>
    <tr>
      <th>1801</th>
      <td>women_entrepreneurs_example_not_exception_gayl...</td>
      <td>28.7M</td>
      <td>25.8G</td>
      <td>1.25K</td>
      <td>142</td>
      <td>20130815</td>
      <td>13 min 16 s</td>
      <td>302883</td>
    </tr>
    <tr>
      <th>1802</th>
      <td>the_arts_festival_revolution_david_binder</td>
      <td>17.0M</td>
      <td>25.8G</td>
      <td>1.21K</td>
      <td>137</td>
      <td>20130517</td>
      <td>9 min 4 s</td>
      <td>261495</td>
    </tr>
    <tr>
      <th>1803</th>
      <td>filming_democracy_in_ghana_jarreth_merz</td>
      <td>18.0M</td>
      <td>25.8G</td>
      <td>1.08K</td>
      <td>122</td>
      <td>20130809</td>
      <td>8 min 36 s</td>
      <td>292976</td>
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
</div>


* Enter the view count minimum, which will generate a list of wanted youtube id's.


```python
views_min = 120000
print(type(views_min))
wanted_ids = []
sql = 'SELECT yt_id from video_info where views_per_year > ?'
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
