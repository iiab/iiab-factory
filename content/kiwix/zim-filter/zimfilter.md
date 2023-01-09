## Modifying ZIM Files

#### The Larger Picture
* Kiwix scrapes many useful sources, but sometimes the chunks are too big for IIAB.
* Using the zimdump program, the highly compressed ZIM files can be flattened into a file tree, modified, and then re-packaged as a ZIM file.
* This Notebook has a collection of tools which filters the content into a new smaller zim selected by youtube views/per year.


#### How to Use this notebook
* The zimdump program (at https://github.com/openzim/zim-tools) needs to be compiled from source.
* A bash script makes is easy to compile zimtools (which contains zimdump) on Ubuntu 20.04. There are instructions for the compilation at the github url. In a terminal, do the following:

```
cd /opt/iiab/iiab-factory/content/kiwix/generic/ 
sudo ./install-zim-tools.sh

```
* This ```zimfilter``` program can be set up into a python virtual environment using a role in the iiab-factory repository:

```
cd /opt/iiab/iiab-factory/ansible/
sudo ./runrole youtube
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


#### Installation Notes
* Installing on Windows 10 insider preview WSL2. Used https://towardsdatascience.com/configuring-jupyter-notebook-in-windows-subsystem-linux-wsl2-c757893e9d69.
* First tried installing miniconda, and then installing jupyterlab with it.
* Wanted VIM bindings to edit cells, but jupyterlab version installed by conda was too old for jupyter-vim extenion. Wound up deleting old version with conda, and used pip to install both.
* Jupyterlab seems to make the current directory its root. I created a notebook directory, and aways start jupyter lab from my home directiry
* Discovered that I could enable writing by non-root group in the iiab-factory repo, and continue to use git for version control. Needed to make symbolic link from ~/miniconda to iiab-factory.
* Reminder: Start jupyterlab in console via "jupyter lab --no-browser", and then pasteing the html link displayed into my browser.

#### Declare input and output
* The ZIM file names tend to be long and hard to remember. The PROJECT_NAME, initialized below, is used to create path names. All of the output of the zimdump program is placed in \<home\>/zimtest/\<PROJECT_NAME\>/tree. All if the intermediate downloads, and data, are placed in \<home\>/zimtest/\<PROJECT_NAME\>/working. If you use the IIAB Admin Console to download ZIMS, you will find them in /library/zims/content/.


```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os,sys
import json
import youtube_dl
import pprint as pprint
from types import SimpleNamespace
import subprocess
from ruamel.yaml import YAML 
from pprint import pprint

# Get the current project from it's pointer in iiab-factory repo
FACTORY_REPO = '/opt/iiab/iiab-factory'
PREFIX = '/ext/zims'

current_project = FACTORY_REPO + '/content/kiwix/zim-filter/current_project'
if not os.path.isfile(current_project):
    print(f'\"current_project\" file is missing: {current_project}')
    sys.exit(1)
with open(current_project,'r') as fp:
    project_name = fp.read().strip().split('/')
    if len(project_name) > 0:
        prefix = project_name[:-1]
        project_name = project_name[-1]
lookfor = f"{PREFIX}/{project_name}/default_config.yaml"
dflt_cfg = f'{FACTORY_REPO}/content/kiwix/zim-filter/default_filter.yaml'
yml = YAML()
if not os.path.isfile(lookfor):
    with open(dflt_cfg,'r') as fp:
        cfg = yml.load(fp)
    cfg['PREFIX'] = PREFIX
    cfg['PROJECT_NAME'] = project_name
    with open(lookfor,'w') as newfp:
        yml.dump(cfg,newfp) 
else:
    with open(lookfor,'r') as fp:
        cfg = yml.load(fp)

PROJECT_NAME = cfg['PROJECT_NAME']
SOURCE_URL = cfg['SOURCE_URL']
CACHE_DIR = PREFIX + '/youtube/cache'
if not os.path.isdir(CACHE_DIR):
   os.makedirs(CACHE_DIR)
TARGET_SIZE = cfg['TARGET_SIZE']  #10GB

# The rest of the paths are computed and represent the standard layout
WORKING_DIR = PREFIX + '/' + PROJECT_NAME + '/working'
PROJECT_DIR = PREFIX + '/' + PROJECT_NAME + '/tree'
OUTPUT_DIR = PREFIX + '/' + PROJECT_NAME + '/output_tree'
SOURCE_DIR = PREFIX + '/' + PROJECT_NAME + '/zim-src'
NEW_ZIM_DIR = PREFIX + '/' + PROJECT_NAME + '/new-zim'
PROOF_DIR = PREFIX + '/' + PROJECT_NAME + '/proof'
dir_list = ['output_tree','tree','../youtube/cache/video_json','zim-src','new-zim','proof']
for f in dir_list: 
    if not os.path.isdir(PREFIX + '/' + PROJECT_NAME +'/' + f):
       os.makedirs(PREFIX + '/' + PROJECT_NAME +'/' + f)

# Input the full path of the downloaded ZIM file
ZIM_PATH = SOURCE_DIR
zim_path_contents = os.listdir(SOURCE_DIR)
if zim_path_contents:
    ZIM_PATH = SOURCE_DIR + '/' + zim_path_contents[0]
else:
    if SOURCE_URL.find('/library/zims') == 0:
        os.symlink(SOURCE_URL,SOURCE_DIR)
    else:
        cmd = 'wget -P %s %s'%(SOURCE_DIR,SOURCE_URL)
        print('command:%s'%cmd)
        subprocess.run(cmd,shell=True)
        
# abort if the input file cannot be found
if not os.path.exists(ZIM_PATH):
    print('%s path not found. Quitting. . .'%ZIM_PATH)
    exit

```

    command:wget -P /ext/zims/teded/zim-src 



```python
print(f'{PREFIX},{PROJECT_DIR},{project_name}')
```

    /ext/zims,/ext/zims/teded/tree,teded



```python
print('This is the PREFIX:%s'%PREFIX)
```

    This is the PREFIX:/ext/zims



```python
# First we need to get a current copy of the script
cmd = '/bin/cp %s/content/kiwix/de-namespace.sh %s'%(cfg['FACTORY_REPO'],PREFIX)
subprocess.run(cmd,shell=True)
```




    CompletedProcess(args='/bin/cp /opt/iiab/iiab-factory/content/kiwix/de-namespace.sh /ext/zims', returncode=1)




```python
# The following command will zimdump to the "tree" directory
#  Despite the name, removing namespaces seems unnecessary, and more complex
# It will return without doing anything if the "tree' is not empty
print('Using zimdump to expand the zim file to %s'%PROJECT_DIR)
progname = PREFIX + '/de-namespace.sh'
cmd = "%s %s %s"%(progname,ZIM_PATH,PROJECT_DIR)
print('command:%s'%cmd)
subprocess.run(cmd,shell=True)
```

    Using zimdump to expand the zim file to /ext/zims/crash/tree
    command:/ext/zims/de-namespace.sh /ext/zims/crash/zim-src/crashcourse_en_all_2021-01.zim crash





    CompletedProcess(args='/ext/zims/de-namespace.sh /ext/zims/crash/zim-src/crashcourse_en_all_2021-01.zim crash', returncode=0)



* The next step is a manual one that you will need to do with your browser. That is: to verify that after the namespace directories were removed, and all of the html links have been adjusted correctly. Point your browser to <hostname>/zimtest/\<PROJECT_NAME\>/tree.
* If everything is working, it's time to go fetch the information about each video from youtube.


```python
ydl = youtube_dl.YoutubeDL()
print('Downloading metadata from Youtube')
downloaded = 0
skipped = 0
# Create a list of youtube id's
yt_id_list = os.listdir(PROJECT_DIR + '/videos/')
for yt_id in iter(yt_id_list):
    if os.path.exists(CACHE_DIR + '/video_json/' + yt_id + '.json'):
        # skip over items that are already downloadd
        skipped += 1
        continue
    with ydl:
       result = ydl.extract_info(
                'http://www.youtube.com/watch?v=%s'%yt_id,
                download=False # We just want to extract the info
                )
       downloaded += 1

    with open(CACHE_DIR + '/video_json/' + yt_id + '.json','w') as fp:
        fp.write(json.dumps(result))
    #pprint.pprint(result['upload_date'],result['view_count'])
print('%s skipped and %s downloaded'%(skipped,downloaded))
```

    Downloading metadata from Youtube
    1309 skipped and 0 downloaded


#### Playlist Navigation to Videos
* On the home page there is a drop down selector which lists about 70 cateegories (or playlists).
* The value from that drop down is used to pick an entry in "-/assets/data.js", which in turn specifies the playlist of yourtube ID"s that are displayed when a selection is made.


```python
def get_assets_data():
    # the file <root>/assets/data.js holds the category to video mappings
    outstr = '['
    data = {}
    with open(PROJECT_DIR + '/assets/data.js', 'r') as fp:
    #with open(OUTPUT_DIR + '/assets/data.js', 'r') as fp:
        line = fp.readline()
        while True:
            if line.startswith('var') or not line :
                if len(outstr) > 3:
                    # clip off the trailing semicolon
                    outstr = outstr[:-2]
                    try:
                        data[cat] = json.loads(outstr)
                    except Exception:
                        print('Parse error: %s'%outstr[:80])
                        exit
                cat = line[9:-4]
                outstr = '['
                if not line: break
            else:
                outstr += line
            line = fp.readline()
    return data

zim_category_js = get_assets_data()
#print(json.dumps(zim_category_js,indent=2))
def get_zim_data(yt_id):
    rtn_dict = {}
    for cat in  iter(zim_category_js.keys()):
        for video in range(len(zim_category_js[cat])):
            if zim_category_js[cat][video]['id'] == yt_id:
                rtn_dict = zim_category_js[cat][video]
                break
        if len(rtn_dict) > 0: break
    return rtn_dict
ans = get_zim_data('usdJgEwMinM')
#print(json.dumps(ans,indent=2))
```

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
    
print('Creating/Updating a Sqlite database with information about the Videos in this ZIM.')
db = Sqlite(WORKING_DIR + '/zim_video_info.sqlite')
initialize_db()
sql = 'select count() as num from video_info'
db.c.execute(sql)
row = db.c.fetchone()
if row[0] == len(yt_id_list):
    print('skipping update of sqlite database. Number of records equals number of videos')
else:
    for yt_id in iter(yt_id_list):
        # some defaults
        age = 0
        views_per_year = 1
        # fetch data from assets/data.js
        zim_data = get_zim_data(yt_id)
        if len(zim_data) == 0: 
            print('get_zim_data returned no data for %s'%yt_id)
        slug = zim_data['slug']

        # We already have youtube data for every video, use it 
        data = get_video_json(CACHE_DIR + "/video_json/" + yt_id + '.json')
        if len(data) == 0:
            print('get_video_json returned no data for %s'%yt_id)
        vsize = data.get('filesize',0)
        view_count = data.get('view_count',0)
        upload_date = data.get('upload_date','')
        average_rating = data.get('average_rating',0)
        title = data.get('title','unknown title')
        # calculate the views_per_year since it was uploaded
        if upload_date != '':
            age = round(age_in_years(upload_date))
            views_per_year = int(view_count / age)

        # interogate the video itself
        filename = PROJECT_DIR + '/videos/' + yt_id + '/video.webm'
        if os.path.isfile(filename):
            vsize = os.path.getsize(filename)
            #print('vsize:%s'%vsize)
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
    print(yt_id,vsize,view_count,views_per_year,upload_date, \
                          duration,bit_rate,v_format,average_rating,slug,round(age))
```

    Creating/Updating a Sqlite database with information about the Videos in this ZIM.
    skipping update of sqlite database. Number of records equals number of videos

sqlite_db = WORKING_DIR + '/zim_video_info.sqlite'
!sqlite3 {sqlite_db} '.headers on' 'select * from video_info limit 2'
#### Select the cutoff using view count and total size
* Order the videos by view count. Then select the sum line in the that has the target sum.


```python
import pandas as pd
from IPython.display import display 
global tot_sum

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
sql = 'select slug,zim_size,views_per_year,view_count,duration,upload_date,'\
       'format,width,height,bit_rate from video_info order by views_per_year desc'
db.c.execute(sql)
rows = db.c.fetchall()
print('%60s %6s %6s %6s %6s %8s %8s'%('Name','Size','Sum','Views','Views','Date  ','Duration'))
print('%60s %6s %6s %6s %6s %8s %8s'%('','','','','/ yr','',''))
tot_sum = 0
for row in rows:
    tot_sum += row['zim_size']
    print('%60s %6s %6s %6s %6s %8s %8s'%(row['slug'][:60],human_readable(row['zim_size']),\
                              human_readable(tot_sum),human_readable(row['view_count']),\
                              human_readable(row['views_per_year']),\
                              row['upload_date'],row['duration']))
#df = pd.read_sql(sql,db.conn)
#df = pd.DataFrame(row_list,columns=['Name','Size','Sum','Views','Views','Date','Duration','Bit Rate'])
#display(df)
```

                                                            Name   Size    Sum  Views  Views   Date   Duration
                                                                                        / yr                  
                   intro_to_psychology_crash_course_psychology_1  30.9M  30.9M  10.3M  1.29M 20140203 10 min 53 s
        the_agricultural_revolution_crash_course_world_history_1  32.3M  63.2M  12.8M  1.28M 20120126 11 min 10 s
    conflict_in_israel_and_palestine_crash_course_world_history_  35.6M  98.8M  7.66M  1.09M 20150128 12 min 52 s
                      world_war_ii_crash_course_world_history_38  38.9M   138M  9.71M  1.08M 20121011 13 min 12 s
    islam_the_quran_and_the_five_pillars_all_without_a_flamewar_  31.2M   169M  9.57M   980K 20120419 12 min 52 s
           introduction_to_anatomy_physiology_crash_course_a_p_1  26.1M   195M  6.46M   945K 20150106 11 min 19 s
    the_black_legend_native_americans_and_spaniards_crash_course  30.6M   226M  8.29M   943K 20130131 11 min 19 s
          capitalism_and_socialism_crash_course_world_history_33  42.1M   268M  8.80M   901K 20120906 14 min 2 s
                    the_nervous_system_part_1_crash_course_a_p_8  23.4M   291M  6.05M   885K 20150223 10 min 35 s
                          atp_respiration_crash_course_biology_7  37.9M   329M  8.31M   851K 20120312 13 min 25 s
                    what_is_philosophy_crash_course_philosophy_1  27.4M   357M  4.93M   841K 20160208 10 min 34 s
                       existentialism_crash_course_philosophy_16  23.6M   380M  4.70M   801K 20160606 8 min 53 s
           dna_structure_and_replication_crash_course_biology_10  35.9M   416M  7.56M   774K 20120402 12 min 58 s
             the_french_revolution_crash_course_world_history_29  35.4M   451M  7.55M   773K 20120810 11 min 53 s
    christianity_from_judaism_to_constantine_crash_course_world_  31.1M   482M  7.53M   771K 20120405 11 min 36 s
                          intro_to_economics_crash_course_econ_1  36.0M   519M  5.26M   769K 20150708 12 min 8 s
                        immune_system_part_1_crash_course_a_p_45  24.7M   543M  4.35M   742K 20151208 9 min 12 s
                  the_problem_of_evil_crash_course_philosophy_13  25.7M   569M  4.35M   742K 20160509 10 min 3 s
    usa_vs_ussr_fight_the_cold_war_crash_course_world_history_39  35.6M   605M  6.45M   734K 20121018 12 min 15 s
    fall_of_the_roman_empire_in_the_15th_century_crash_course_wo  35.5M   640M  7.14M   731K 20120412 12 min 43 s
    the_nervous_system_part_2_action_potential_crash_course_a_p_  28.4M   668M  4.81M   704K 20150302 11 min 43 s
    the_dark_ages_how_dark_were_they_really_crash_course_world_h  29.8M   698M  6.82M   699K 20120426 12 min 7 s
           wait_for_it_the_mongols_crash_course_world_history_17  32.0M   730M  6.76M   692K 20120517 11 min 30 s
                         carbon_so_simple_crash_course_biology_1  34.0M   764M  6.72M   688K 20120130 12 min 32 s
                 muscles_part_1_muscle_cells_crash_course_a_p_21  23.0M   787M  4.67M   682K 20150608 10 min 23 s
          indus_valley_civilization_crash_course_world_history_2  24.4M   812M  6.64M   680K 20120202 9 min 34 s
                the_persians_greeks_crash_course_world_history_5  28.9M   841M  6.63M   679K 20120223 11 min 38 s
    2000_years_of_chinese_history_the_mandate_of_heaven_and_conf  36.5M   877M  6.62M   678K 20120308 12 min 11 s
          how_world_war_i_started_crash_course_world_history_209  28.2M   905M  5.30M   678K 20140912 9 min 9 s
                        mesopotamia_crash_course_world_history_3  35.4M   941M  6.62M   678K 20120209 12 min 5 s
    the_constitution_the_articles_and_federalism_crash_course_us  32.8M   974M  5.93M   675K 20130321 13 min 3 s
                 let_s_talk_about_sex_crash_course_psychology_27  34.2M  0.98G  5.27M   675K 20140818 11 min 35 s
                            the_nucleus_crash_course_chemistry_1  23.3M  1.01G  5.76M   655K 20130211 10 min 11 s
                      ancient_egypt_crash_course_world_history_4  32.5M  1.04G  6.38M   653K 20120216 11 min 54 s
                           photosynthesis_crash_course_biology_8  39.5M  1.08G  6.36M   652K 20120319 13 min 14 s
             the_heart_part_1_under_pressure_crash_course_a_p_25  22.0M  1.10G  4.45M   652K 20150706 10 min 7 s
    the_roman_empire_or_republic_or_which_was_it_crash_course_wo  30.9M  1.13G  6.29M   645K 20120329 12 min 25 s
                 the_great_depression_crash_course_us_history_33  42.0M  1.17G  4.92M   630K 20131010 14 min 26 s
    luther_and_the_protestant_reformation_crash_course_world_his  45.5M  1.21G  4.24M   621K 20141129 15 min 6 s
                     the_periodic_table_crash_course_chemistry_4  27.8M  1.24G  5.43M   618K 20130304 11 min 21 s
    the_crusades_pilgrimage_or_holy_war_crash_course_world_histo  32.9M  1.27G  5.99M   613K 20120503 11 min 32 s
                motion_in_a_straight_line_crash_course_physics_1  22.1M  1.30G  3.57M   609K 20160331 10 min 39 s
                       utilitarianism_crash_course_philosophy_36  25.4M  1.32G  2.96M   607K 20161121 10 min 0 s
            ocd_and_anxiety_disorders_crash_course_psychology_29  31.6M  1.35G  4.71M   603K 20140901 11 min 31 s
    reproductive_system_part_1_female_reproductive_system_crash_  23.2M  1.37G  3.51M   599K 20151026 10 min 14 s
           introduction_crash_course_u_s_government_and_politics  19.6M  1.39G  4.05M   593K 20150123 6 min 46 s
     endocrine_system_part_1_glands_hormones_crash_course_a_p_23  23.5M  1.42G  4.00M   585K 20150622 10 min 24 s
                 medieval_europe_crash_course_european_history_1  37.0M  1.45G  1.71M   584K 20190412 14 min 8 s
                  buddha_and_ashoka_crash_course_world_history_6  31.5M  1.48G  5.55M   568K 20120301 12 min 16 s
                psychological_research_crash_course_psychology_2  28.0M  1.51G  4.41M   565K 20140210 10 min 50 s
     mitosis_splitting_up_is_complicated_crash_course_biology_12  25.3M  1.53G  5.52M   565K 20120416 10 min 47 s
    how_to_argue_philosophical_reasoning_crash_course_philosophy  23.7M  1.56G  3.28M   559K 20160216 9 min 42 s
    meet_your_master_getting_to_know_your_brain_crash_course_psy  31.6M  1.59G  4.30M   551K 20140224 12 min 33 s
    biological_molecules_you_are_what_you_eat_crash_course_biolo  43.2M  1.63G  5.37M   550K 20120213 14 min 8 s
    the_renaissance_was_it_a_thing_crash_course_world_history_22  29.8M  1.66G  5.29M   542K 20120621 11 min 32 s
    coal_steam_and_the_industrial_revolution_crash_course_world_  30.6M  1.69G  5.26M   539K 20120830 11 min 4 s
                               tissues_part_1_crash_course_a_p_2  24.7M  1.71G  3.68M   539K 20150112 10 min 42 s
                       urinary_system_part_1_crash_course_a_p_38  24.8M  1.74G  3.15M   538K 20151012 10 min 17 s
                personality_disorders_crash_course_psychology_34  28.7M  1.77G  3.67M   537K 20141014 10 min 57 s
              introduction_to_astronomy_crash_course_astronomy_1  33.4M  1.80G  3.62M   530K 20150115 12 min 11 s
                      the_war_of_1812_crash_course_us_history_11  33.0M  1.83G  4.64M   528K 20130418 12 min 42 s
    alexander_the_great_and_the_situation_the_great_crash_course  27.1M  1.86G  5.14M   526K 20120315 11 min 1 s
          rethinking_civilization_crash_course_world_history_201  40.8M  1.90G  4.04M   517K 20140711 13 min 41 s
                     the_chemical_mind_crash_course_psychology_3  24.8M  1.92G  3.99M   511K 20140217 10 min 13 s
                         the_skeletal_system_crash_course_a_p_19  23.8M  1.94G  3.49M   510K 20150518 10 min 37 s
    archdukes_cynicism_and_world_war_i_crash_course_world_histor  35.4M  1.98G  4.92M   504K 20120927 11 min 44 s
                            newton_s_laws_crash_course_physics_5  21.2M  2.00G  2.95M   503K 20160428 11 min 3 s
                       imperialism_crash_course_world_history_35  37.3M  2.04G  4.88M   500K 20120920 13 min 45 s
                   respiratory_system_part_1_crash_course_a_p_31  20.4M  2.06G  3.40M   498K 20150824 9 min 21 s
                 early_computing_crash_course_computer_science_1  32.0M  2.09G  2.41M   494K 20170222 11 min 52 s
     depressive_and_bipolar_disorders_crash_course_psychology_30  27.5M  2.11G  3.84M   491K 20140908 9 min 59 s
    when_is_thanksgiving_colonizing_america_crash_course_us_hist  36.6M  2.15G  4.30M   490K 20130207 12 min 25 s
                      what_is_sociology_crash_course_sociology_1  28.2M  2.18G  2.36M   482K 20170313 9 min 41 s
                     digestive_system_part_1_crash_course_a_p_33  26.0M  2.20G  3.29M   482K 20150907 11 min 4 s
         kant_categorical_imperatives_crash_course_philosophy_35  25.2M  2.23G  2.35M   481K 20161114 10 min 26 s
                 the_civil_war_part_i_crash_course_us_history_20  28.8M  2.26G  4.18M   475K 20130628 12 min 0 s
                            lymphatic_system_crash_course_a_p_44  22.4M  2.28G  2.78M   474K 20151130 9 min 19 s
          who_started_world_war_i_crash_course_world_history_210  32.5M  2.31G  3.68M   471K 20140920 10 min 55 s
                         the_cold_war_crash_course_us_history_37  34.0M  2.34G  3.66M   469K 20131108 13 min 33 s
             napoleon_bonaparte_crash_course_european_history_22  43.6M  2.39G   937K   469K 20191021 15 min 53 s
               iran_s_revolutions_crash_course_world_history_226  38.0M  2.42G  3.20M   468K 20150226 13 min 40 s
          the_nervous_system_part_3_synapses_crash_course_a_p_10  24.3M  2.45G  3.19M   467K 20150310 10 min 56 s
           in_da_club_membranes_transport_crash_course_biology_5  35.0M  2.48G  4.54M   465K 20120227 11 min 44 s
                              slavery_crash_course_us_history_13  39.3M  2.52G  4.05M   461K 20130502 14 min 24 s
    the_silk_road_and_ancient_trade_crash_course_world_history_9  27.8M  2.55G  4.48M   459K 20120322 10 min 30 s
             the_2008_financial_crisis_crash_course_economics_12  30.4M  2.58G  2.68M   457K 20151021 11 min 24 s
    russia_the_kievan_rus_and_the_mongols_crash_course_world_his  28.9M  2.60G  4.45M   455K 20120607 10 min 46 s
    dna_hot_pockets_the_longest_word_ever_crash_course_biology_1  44.7M  2.65G  4.43M   453K 20120409 14 min 7 s
    tea_taxes_and_the_american_revolution_crash_course_world_his  31.3M  2.68G  4.42M   453K 20120802 11 min 26 s
    schizophrenia_and_dissociative_disorders_crash_course_psycho  31.8M  2.71G  3.52M   451K 20140929 11 min 43 s
    eukaryopolis_the_city_of_animal_cells_crash_course_biology_4  27.9M  2.74G  4.39M   450K 20120220 11 min 34 s
                           crash_course_computer_science_preview  8.46M  2.74G  2.17M   445K 20170215 2 min 44 s
                 the_1960s_in_america_crash_course_us_history_40  38.8M  2.78G  3.47M   445K 20131206 15 min 14 s
                        immune_system_part_2_crash_course_a_p_46  24.8M  2.81G  2.59M   442K 20151214 9 min 43 s
        1984_by_george_orwell_part_1_crash_course_literature_401  31.3M  2.84G  1.72M   441K 20171107 14 min 27 s
                      central_nervous_system_crash_course_a_p_11  20.7M  2.86G  3.02M   441K 20150323 10 min 7 s
                  world_war_ii_part_1_crash_course_us_history_35  33.1M  2.89G  3.43M   439K 20131025 13 min 26 s
              sensation_and_perception_crash_course_psychology_5  27.7M  2.92G  3.42M   438K 20140303 10 min 45 s
               islam_and_politics_crash_course_world_history_216  36.1M  2.95G  2.99M   437K 20141114 13 min 27 s
            meiosis_where_the_sex_starts_crash_course_biology_13  29.3M  2.98G  4.22M   432K 20120423 11 min 42 s
          the_atlantic_slave_trade_crash_course_world_history_24  30.8M  3.01G  4.21M   431K 20120705 11 min 7 s
              reconstruction_and_1876_crash_course_us_history_22  35.0M  3.04G  3.79M   431K 20130718 12 min 59 s
           how_and_why_we_read_crash_course_english_literature_1  17.9M  3.06G  3.77M   429K 20121115 6 min 59 s
                         the_new_deal_crash_course_us_history_34  36.2M  3.10G  3.34M   428K 20131018 14 min 56 s
              aristotle_virtue_theory_crash_course_philosophy_38  20.8M  3.12G  2.09M   427K 20161205 9 min 21 s
    the_integumentary_system_part_1_skin_deep_crash_course_a_p_6  24.7M  3.14G  2.92M   427K 20150209 9 min 39 s
                     the_roaring_20_s_crash_course_us_history_32  37.4M  3.18G  3.72M   424K 20131004 13 min 11 s
    the_seven_years_war_and_the_great_awakening_crash_course_us_  28.3M  3.21G  3.68M   419K 20130228 10 min 39 s
                      the_vikings_crash_course_world_history_224  34.1M  3.24G  2.86M   418K 20150204 11 min 17 s
      the_industrial_revolution_crash_course_european_history_24  47.4M  3.29G   831K   416K 20191105 17 min 5 s
                          obamanation_crash_course_us_history_47  40.8M  3.33G  3.21M   411K 20140206 15 min 39 s
                     water_liquid_awesome_crash_course_biology_2  32.7M  3.36G  4.00M   410K 20120206 11 min 16 s
       who_won_the_american_revolution_crash_course_us_history_7  34.8M  3.39G  3.60M   409K 20130314 12 min 40 s
           the_epic_of_gilgamesh_crash_course_world_mythology_26  35.5M  3.43G  2.00M   409K 20170908 13 min 45 s
                 the_cold_war_in_asia_crash_course_us_history_38  38.3M  3.46G  3.19M   408K 20131115 13 min 41 s
    taxes_smuggling_prelude_to_revolution_crash_course_us_histor  32.7M  3.50G  3.57M   406K 20130307 12 min 18 s
    mansa_musa_and_islam_in_africa_crash_course_world_history_16  30.1M  3.52G  3.96M   405K 20120510 10 min 30 s
           civil_rights_and_the_1950s_crash_course_us_history_39  30.5M  3.55G  3.17M   405K 20131121 11 min 57 s
           the_natives_and_the_english_crash_course_us_history_3  35.3M  3.59G  3.55M   404K 20130214 11 min 26 s
                                 heredity_crash_course_biology_9  30.5M  3.62G  3.86M   396K 20120326 10 min 17 s
                        taking_notes_crash_course_study_skills_1  17.7M  3.64G  1.90M   390K 20170808 8 min 50 s
        globalization_i_the_upside_crash_course_world_history_41  31.0M  3.67G  3.43M   390K 20121102 11 min 50 s
    florence_and_the_renaissance_crash_course_european_history_2  34.9M  3.70G  1.14M   390K 20190419 14 min 33 s
                      human_evolution_crash_course_big_history_6  40.4M  3.74G  2.66M   389K 20141105 16 min 12 s
    communists_nationalists_and_china_s_revolutions_crash_course  38.1M  3.78G  3.78M   387K 20121004 12 min 10 s
             tissues_part_2_epithelial_tissue_crash_course_a_p_3  23.3M  3.80G  2.64M   386K 20150119 10 min 15 s
            the_columbian_exchange_crash_course_world_history_23  34.3M  3.83G  3.75M   384K 20120628 12 min 8 s
             the_rise_of_conservatism_crash_course_us_history_41  40.1M  3.87G  2.98M   381K 20131213 14 min 50 s
               america_in_world_war_i_crash_course_us_history_30  38.4M  3.91G  3.34M   380K 20130919 13 min 39 s
    the_quakers_the_dutch_and_the_ladies_crash_course_us_history  31.6M  3.94G  3.32M   378K 20130221 11 min 37 s
      political_ideology_crash_course_government_and_politics_35  24.3M  3.96G  2.21M   378K 20151016 8 min 46 s
                 how_to_train_a_brain_crash_course_psychology_11  28.1M  3.99G  2.95M   378K 20140421 11 min 48 s
             determinism_vs_free_will_crash_course_philosophy_24  25.1M  4.02G  2.20M   376K 20160815 10 min 25 s
           anselm_the_argument_for_god_crash_course_philosophy_9  21.0M  4.04G  2.20M   375K 20160404 9 min 12 s
    the_mughal_empire_and_historical_reputation_crash_course_wor  30.3M  4.07G  2.56M   375K 20141121 11 min 43 s
                          disease_crash_course_world_history_203  30.8M  4.10G  2.91M   373K 20140724 11 min 36 s
                       age_of_jackson_crash_course_us_history_14  36.8M  4.13G  3.28M   373K 20130509 15 min 4 s
    the_spanish_empire_silver_runaway_inflation_crash_course_wor  29.0M  4.16G  3.61M   370K 20120712 10 min 45 s
    a_long_and_difficult_journey_or_the_odyssey_crash_course_lit  31.5M  4.19G  2.87M   367K 20140227 12 min 6 s
                      supply_and_demand_crash_course_economics_4  26.6M  4.22G  2.49M   365K 20150814 10 min 21 s
     venice_and_the_ottoman_empire_crash_course_world_history_19  27.3M  4.24G  3.56M   364K 20120531 10 min 11 s
          the_french_revolution_crash_course_european_history_21  44.8M  4.29G   729K   364K 20191008 15 min 28 s
                 how_we_make_memories_crash_course_psychology_13  26.7M  4.31G  2.85M   364K 20140505 9 min 54 s
    unit_conversion_significant_figures_crash_course_chemistry_2  24.7M  4.34G  3.20M   364K 20130218 11 min 23 s
      how_to_argue_induction_abduction_crash_course_philosophy_3  23.3M  4.36G  2.13M   364K 20160222 10 min 17 s
                     blood_part_1_true_blood_crash_course_a_p_29  22.2M  4.38G  2.47M   361K 20150803 9 min 59 s
        latin_american_revolutions_crash_course_world_history_31  37.2M  4.42G  3.52M   360K 20120823 13 min 42 s
    decolonization_and_nationalism_triumphant_crash_course_world  38.3M  4.46G  3.15M   359K 20121025 12 min 48 s
       boolean_logic_logic_gates_crash_course_computer_science_3  23.3M  4.48G  1.75M   359K 20170308 10 min 6 s
                     what_is_myth_crash_course_world_mythology_1  33.5M  4.51G  1.75M   359K 20170224 13 min 1 s
                the_reagan_revolution_crash_course_us_history_43  36.8M  4.55G  2.80M   359K 20140111 14 min 19 s
             polar_non_polar_molecules_crash_course_chemistry_23  31.6M  4.58G  3.15M   359K 20130722 10 min 45 s
                         the_big_bang_crash_course_big_history_1  37.6M  4.62G  2.79M   357K 20140917 14 min 24 s
                                      vision_crash_course_a_p_18  19.5M  4.64G  2.44M   357K 20150511 9 min 38 s
                 american_imperialism_crash_course_us_history_28  36.2M  4.67G  3.13M   356K 20130905 14 min 3 s
          the_age_of_exploration_crash_course_european_history_4  41.2M  4.71G  1.04M   355K 20190503 15 min 39 s
    japan_in_the_heian_period_and_cultural_history_crash_course_  41.2M  4.75G  2.43M   355K 20150304 13 min 32 s
               the_seven_years_war_crash_course_world_history_26  31.8M  4.78G  3.46M   354K 20120719 12 min 19 s
           where_us_politics_came_from_crash_course_us_history_9  33.9M  4.81G  3.10M   352K 20130404 13 min 56 s
    samurai_daimyo_matthew_perry_and_nationalism_crash_course_wo  31.5M  4.85G  3.44M   352K 20120913 11 min 52 s
    the_bicameral_congress_crash_course_government_and_politics_  22.5M  4.87G  2.40M   351K 20150130 9 min 4 s
    separation_of_powers_and_checks_and_balances_crash_course_go  21.6M  4.89G  2.39M   350K 20150206 8 min 30 s
    economic_systems_and_macroeconomics_crash_course_economics_3  30.9M  4.92G  2.39M   349K 20150730 10 min 17 s
                        immune_system_part_3_crash_course_a_p_47  25.4M  4.94G  2.03M   346K 20151221 9 min 36 s
                        ragnarok_crash_course_world_mythology_24  35.9M  4.98G  1.68M   345K 20170826 12 min 19 s
    charles_v_and_the_holy_roman_empire_crash_course_world_histo  35.4M  5.01G  2.35M   343K 20141205 13 min 15 s
    economic_depression_and_dictators_crash_course_european_hist  43.8M  5.06G   686K   343K 20200305 16 min 33 s
    world_war_ii_a_war_for_resources_crash_course_world_history_  30.4M  5.09G  2.34M   343K 20141214 11 min 1 s
    columbus_de_gama_and_zheng_he_15th_century_mariners_crash_co  29.0M  5.11G  3.31M   339K 20120614 10 min 37 s
       thomas_jefferson_his_democracy_crash_course_us_history_10  32.3M  5.15G  2.98M   339K 20130411 13 min 18 s
                         india_crash_course_history_of_science_4  32.7M  5.18G  1.32M   338K 20180425 13 min 14 s
    leonardo_dicaprio_the_nature_of_reality_crash_course_philoso  22.8M  5.20G  1.97M   336K 20160229 9 min 2 s
                           crash_course_european_history_preview  17.9M  5.22G  0.98M   335K 20190329 6 min 35 s
            terrorism_war_and_bush_43_crash_course_us_history_46  39.9M  5.26G  2.61M   334K 20140130 15 min 26 s
                   westward_expansion_crash_course_us_history_24  35.5M  5.29G  2.93M   333K 20130808 12 min 43 s
                 metabolism_nutrition_part_1_crash_course_a_p_36  24.1M  5.31G  2.28M   333K 20150928 10 min 32 s
               federalism_crash_course_government_and_politics_4  24.7M  5.34G  2.26M   331K 20150214 9 min 14 s
                                      joints_crash_course_a_p_20  24.1M  5.36G  2.25M   329K 20150526 9 min 22 s
                  the_progressive_era_crash_course_us_history_27  40.3M  5.40G  2.87M   327K 20130829 15 min 0 s
                            moon_phases_crash_course_astronomy_4  24.4M  5.43G  2.23M   327K 20150205 9 min 45 s
    cartesian_skepticism_neo_meet_rene_crash_course_philosophy_5  24.9M  5.45G  1.91M   326K 20160307 10 min 0 s
                           the_electron_crash_course_chemistry_5  30.1M  5.48G  2.86M   326K 20130312 12 min 47 s
              psychological_disorders_crash_course_psychology_28  27.7M  5.51G  2.53M   323K 20140825 10 min 9 s
           to_sleep_perchance_to_dream_crash_course_psychology_9  29.3M  5.53G  2.53M   323K 20140331 10 min 40 s
                   intelligent_design_crash_course_philosophy_11  21.3M  5.56G  1.89M   322K 20160425 9 min 33 s
             locke_berkeley_empiricism_crash_course_philosophy_6  23.3M  5.58G  1.89M   322K 20160315 9 min 51 s
    stoichiometry_chemistry_for_massive_creatures_crash_course_c  30.4M  5.61G  2.82M   320K 20130318 12 min 46 s
    russian_revolution_and_civil_war_crash_course_european_histo  37.5M  5.64G   639K   320K 20200213 14 min 15 s
               specialization_and_trade_crash_course_economics_2  23.4M  5.67G  2.18M   319K 20150715 9 min 3 s
                           black_holes_crash_course_astronomy_33  30.4M  5.70G  2.17M   318K 20150925 12 min 25 s
                             deep_time_crash_course_astronomy_45  37.0M  5.73G  1.86M   318K 20160114 15 min 14 s
                perspectives_on_death_crash_course_philosophy_17  21.3M  5.75G  1.85M   316K 20160613 9 min 0 s
    like_pale_gold_the_great_gatsby_part_1_crash_course_english_  29.8M  5.78G  2.77M   315K 20121213 11 min 42 s
    george_hw_bush_and_the_end_of_the_cold_war_crash_course_us_h  39.1M  5.82G  2.45M   313K 20140116 13 min 52 s
              karl_marx_conflict_theory_crash_course_sociology_6  24.3M  5.85G  1.53M   313K 20170417 11 min 18 s
    aquinas_the_cosmological_arguments_crash_course_philosophy_1  22.7M  5.87G  1.83M   313K 20160411 10 min 25 s
                quantum_mechanics_part_1_crash_course_physics_43  20.8M  5.89G  1.51M   310K 20170303 8 min 45 s
    the_election_of_1860_the_road_to_disunion_crash_course_us_hi  39.0M  5.93G  2.72M   309K 20130613 14 min 15 s
                             hearing_balance_crash_course_a_p_17  24.3M  5.95G  2.11M   309K 20150504 10 min 39 s
                    work_energy_and_power_crash_course_physics_9  19.0M  5.97G  1.81M   309K 20160526 9 min 54 s
                      social_thinking_crash_course_psychology_37  29.7M  6.00G  2.10M   307K 20141103 10 min 47 s
                    autonomic_nervous_system_crash_course_a_p_13  18.9M  6.02G  2.09M   306K 20150406 8 min 48 s
                        war_expansion_crash_course_us_history_17  37.6M  6.05G  2.68M   305K 20130606 12 min 46 s
    reproductive_system_part_2_male_reproductive_system_crash_co  25.1M  6.08G  1.78M   304K 20151109 10 min 43 s
     karl_popper_science_pseudoscience_crash_course_philosophy_8  21.8M  6.10G  1.77M   303K 20160328 8 min 56 s
              the_enlightenment_crash_course_european_history_18  46.1M  6.14G   906K   302K 20190909 16 min 22 s
               haitian_revolutions_crash_course_world_history_30  33.5M  6.18G  2.95M   302K 20120816 12 min 34 s
    italian_and_german_unification_crash_course_european_history  36.7M  6.21G   603K   302K 20191126 14 min 21 s
                 war_human_nature_crash_course_world_history_204  28.4M  6.24G  2.35M   301K 20140731 10 min 36 s
              the_meaning_of_knowledge_crash_course_philosophy_7  24.1M  6.26G  1.76M   301K 20160321 10 min 11 s
           creation_from_the_void_crash_course_world_mythology_2  33.4M  6.30G  1.46M   299K 20170303 12 min 21 s
          controversy_of_intelligence_crash_course_psychology_23  35.6M  6.33G  2.33M   298K 20140721 12 min 38 s
    asian_responses_to_imperialism_crash_course_world_history_21  33.4M  6.36G  2.03M   296K 20141024 12 min 54 s
        acid_base_reactions_in_solution_crash_course_chemistry_8  25.1M  6.39G  2.60M   296K 20130408 11 min 16 s
               the_industrial_economy_crash_course_us_history_23  34.6M  6.42G  2.60M   295K 20130725 12 min 31 s
                     what_is_god_like_crash_course_philosophy_12  26.1M  6.45G  1.73M   295K 20160502 10 min 31 s
                  gilded_age_politics_crash_course_us_history_26  41.0M  6.49G  2.59M   294K 20130823 13 min 50 s
      globalization_ii_good_or_bad_crash_course_world_history_42  40.8M  6.53G  2.58M   294K 20121109 13 min 54 s
                   peripheral_nervous_system_crash_course_a_p_12  20.3M  6.55G  2.00M   292K 20150330 10 min 1 s
            tissues_part_3_connective_tissues_crash_course_a_p_4  28.0M  6.57G  1.99M   291K 20150126 10 min 28 s
                measuring_personality_crash_course_psychology_22  31.0M  6.60G  2.26M   290K 20140714 11 min 7 s
                       redox_reactions_crash_course_chemistry_10  26.0M  6.63G  2.55M   290K 20130422 11 min 12 s
                            homunculus_crash_course_psychology_6  25.0M  6.65G  2.25M   288K 20140310 10 min 23 s
                         consciousness_crash_course_psychology_8  26.9M  6.68G  2.25M   288K 20140324 9 min 33 s
            emotion_stress_and_health_crash_course_psychology_26  29.7M  6.71G  2.23M   285K 20140811 10 min 19 s
    eating_and_body_dysmorphic_disorders_crash_course_psychology  28.0M  6.74G  2.22M   284K 20141006 10 min 11 s
               perceiving_is_believing_crash_course_psychology_7  24.1M  6.76G  2.21M   283K 20140317 9 min 59 s
      the_protestant_reformation_crash_course_european_history_6  46.2M  6.81G   847K   282K 20190518 15 min 43 s
              the_power_of_motivation_crash_course_psychology_17  31.7M  6.84G  2.18M   280K 20140602 11 min 19 s
                    the_bobo_beatdown_crash_course_psychology_12  27.1M  6.86G  2.18M   280K 20140428 9 min 34 s
                         neutron_stars_crash_course_astronomy_32  36.2M  6.90G  1.91M   279K 20150917 12 min 56 s
    int_l_commerce_snorkeling_camels_and_the_indian_ocean_trade_  25.6M  6.92G  2.72M   278K 20120524 10 min 14 s
            electronic_computing_crash_course_computer_science_2  26.1M  6.95G  1.36M   278K 20170301 10 min 43 s
                the_market_revolution_crash_course_us_history_12  38.1M  6.99G  2.44M   277K 20130426 14 min 10 s
                       money_debt_crash_course_world_history_202  40.6M  7.03G  2.16M   276K 20140717 14 min 3 s
    the_end_of_civilization_in_the_bronze_age_crash_course_world  36.8M  7.06G  2.15M   276K 20141003 12 min 58 s
                           metaethics_crash_course_philosophy_32  22.0M  7.08G  1.34M   275K 20161025 9 min 33 s
                     social_influence_crash_course_psychology_38  26.0M  7.11G  1.88M   275K 20141111 10 min 7 s
             muscles_part_2_organismal_level_crash_course_a_p_22  25.5M  7.13G  1.88M   275K 20150615 10 min 40 s
                    what_is_statistics_crash_course_statistics_1  32.5M  7.16G  1.07M   274K 20180124 12 min 59 s
     congo_and_africa_s_world_war_crash_course_world_history_221  32.7M  7.20G  1.88M   274K 20150116 12 min 57 s
               the_heart_part_2_heart_throbs_crash_course_a_p_26  22.6M  7.22G  1.87M   274K 20150713 9 min 33 s
                            crash_course_world_mythology_preview  5.94M  7.22G  1.34M   274K 20170217 1 min 59 s
    climate_change_chaos_and_the_little_ice_age_crash_course_wor  27.3M  7.25G  2.14M   273K 20140821 10 min 7 s
        growth_cities_and_immigration_crash_course_us_history_25  33.2M  7.28G  2.40M   273K 20130815 12 min 44 s
      blood_vessels_part_1_form_and_function_crash_course_a_p_27  21.8M  7.31G  1.86M   273K 20150720 9 min 29 s
                     witchcraft_crash_course_european_history_10  44.3M  7.35G   817K   272K 20190622 15 min 32 s
                 the_civil_war_part_2_crash_course_us_history_21  29.3M  7.38G  2.38M   271K 20130711 10 min 53 s
                   natural_law_theory_crash_course_philosophy_34  22.2M  7.40G  1.32M   271K 20161107 9 min 38 s
                              orbitals_crash_course_chemistry_25  28.1M  7.43G  2.36M   269K 20130805 10 min 51 s
    atomic_hook_ups_types_of_chemical_bonds_crash_course_chemist  25.3M  7.45G  2.36M   269K 20130716 9 min 45 s
    world_war_ii_part_2_the_homefront_crash_course_us_history_36  36.5M  7.49G  2.09M   268K 20131101 14 min 22 s
    cognition_how_your_mind_can_amaze_and_betray_you_crash_cours  29.1M  7.51G  2.09M   268K 20140519 10 min 41 s
       the_clinton_years_or_the_1990s_crash_course_us_history_45  37.7M  7.55G  2.09M   268K 20140123 15 min 37 s
                       urinary_system_part_2_crash_course_a_p_39  22.3M  7.57G  1.57M   268K 20151019 9 min 50 s
       the_roads_to_world_war_i_crash_course_european_history_32  40.1M  7.61G   534K   267K 20200116 15 min 0 s
                               the_sun_crash_course_astronomy_10  28.8M  7.64G  1.82M   267K 20150319 12 min 3 s
        the_northern_renaissance_crash_course_european_history_3  35.3M  7.68G   796K   265K 20190426 14 min 1 s
                   respiratory_system_part_2_crash_course_a_p_32  25.2M  7.70G  1.81M   265K 20150831 10 min 22 s
                         macroeconomics_crash_course_economics_5  39.1M  7.74G  1.81M   264K 20150824 13 min 42 s
                          adolescence_crash_course_psychology_20  26.6M  7.76G  2.05M   263K 20140623 10 min 14 s
                 trauma_and_addiction_crash_course_psychology_31  31.0M  7.79G  2.05M   263K 20140922 10 min 50 s
                 indian_pantheons_crash_course_world_mythology_8  35.0M  7.83G  1.28M   262K 20170414 12 min 30 s
    imports_exports_and_exchange_rates_crash_course_economics_15  28.2M  7.86G  1.53M   261K 20151120 10 min 10 s
                   world_war_ii_crash_course_european_history_38  47.2M  7.90G   523K   261K 20200317 16 min 14 s
                       natural_selection_crash_course_biology_14  33.3M  7.93G  2.54M   260K 20120430 12 min 43 s
    endocrine_system_part_2_hormone_cascades_crash_course_a_p_24  24.3M  7.96G  1.78M   260K 20150629 9 min 33 s
                     digestive_system_part_2_crash_course_a_p_34  24.5M  7.98G  1.77M   259K 20150914 10 min 54 s
    ghosts_murder_and_more_murder_hamlet_part_1_crash_course_lit  35.7M  8.02G  2.03M   259K 20140313 12 min 23 s
                 19th_century_reforms_crash_course_us_history_15  37.6M  8.05G  2.27M   258K 20130514 14 min 46 s
         prejudice_and_discrimination_crash_course_psychology_39  26.2M  8.08G  1.76M   257K 20141117 9 min 53 s
                              plant_cells_crash_course_biology_6  32.4M  8.11G  2.49M   255K 20120305 10 min 27 s
              the_growth_of_knowledge_crash_course_psychology_18  27.5M  8.14G  1.98M   254K 20140609 9 min 49 s
    democracy_authoritarian_capitalism_and_china_crash_course_wo  45.1M  8.18G  1.73M   254K 20150404 15 min 31 s
    reproductive_system_part_3_sex_fertilization_crash_course_a_  25.0M  8.21G  1.49M   254K 20151116 9 min 58 s
               registers_and_ram_crash_course_computer_science_6  29.0M  8.23G  1.23M   252K 20170329 12 min 16 s
                       altered_states_crash_course_psychology_10  29.1M  8.26G  1.97M   252K 20140407 11 min 18 s
    capitalism_and_the_dutch_east_india_company_crash_course_wor  42.4M  8.30G  1.70M   249K 20150318 15 min 39 s
            revolutions_of_1848_crash_course_european_history_26  48.2M  8.35G   495K   248K 20191119 16 min 25 s
              the_norse_pantheon_crash_course_world_mythology_10  34.2M  8.39G  1.21M   247K 20170430 12 min 44 s
    the_holocaust_genocides_and_mass_murder_of_wwii_crash_course  33.2M  8.42G   493K   246K 20200410 13 min 38 s
         fate_family_and_oedipus_rex_crash_course_literature_202  33.5M  8.45G  1.92M   246K 20140306 13 min 34 s
                         electric_charge_crash_course_physics_25  28.3M  8.48G  1.44M   246K 20160929 9 min 41 s
          scientific_revolution_crash_course_european_history_12  45.8M  8.52G   736K   245K 20190714 15 min 7 s
          covid_19_and_public_health_a_message_from_crash_course  56.8M  8.58G   245K   245K 20201019 13 min 50 s
                  sympathetic_nervous_system_crash_course_a_p_14  24.8M  8.60G  1.67M   245K 20150413 10 min 43 s
       the_history_of_atomic_chemistry_crash_course_chemistry_37  24.2M  8.63G  1.91M   244K 20131104 9 min 41 s
                           dark_matter_crash_course_astronomy_41  30.9M  8.66G  1.43M   244K 20151203 11 min 59 s
               progressive_presidents_crash_course_us_history_29  37.8M  8.69G  2.13M   243K 20130912 15 min 6 s
            women_in_the_19th_century_crash_course_us_history_16  35.2M  8.73G  2.13M   242K 20130523 13 min 10 s
                        uranus_neptune_crash_course_astronomy_19  37.1M  8.76G  1.65M   242K 20150528 12 min 18 s
            intro_to_algorithms_crash_course_computer_science_13  25.7M  8.79G  1.18M   241K 20170524 11 min 43 s
    how_computers_calculate_the_alu_crash_course_computer_scienc  27.0M  8.82G  1.18M   241K 20170322 11 min 9 s
                       the_nervous_system_crashcourse_biology_26  30.1M  8.84G  2.35M   240K 20120723 12 min 3 s
                              derivatives_crash_course_physics_2  19.2M  8.86G  1.41M   240K 20160407 10 min 1 s
           remembering_and_forgetting_crash_course_psychology_14  30.0M  8.89G  1.87M   239K 20140512 10 min 17 s
    the_creation_of_chemistry_the_fundamental_laws_crash_course_  24.6M  8.92G  2.10M   239K 20130225 10 min 58 s
           plato_and_aristotle_crash_course_history_of_science_3  28.0M  8.94G   954K   238K 20180416 12 min 28 s
                      what_is_justice_crash_course_philosophy_40  25.1M  8.97G  1.16M   238K 20161219 10 min 14 s
         the_congress_of_vienna_crash_course_european_history_23  32.9M  9.00G   474K   237K 20191029 14 min 0 s
        the_17th_century_crisis_crash_course_european_history_11  38.2M  9.04G   709K   236K 20190629 13 min 29 s
           major_sociological_paradigms_crash_course_sociology_2  27.0M  9.06G  1.15M   236K 20170320 9 min 38 s
           taxonomy_life_s_filing_system_crash_course_biology_19  38.1M  9.10G  2.30M   236K 20120604 12 min 15 s
                     the_ideal_gas_law_crash_course_chemistry_12  21.6M  9.12G  2.06M   235K 20130507 9 min 2 s
                       high_mass_stars_crash_course_astronomy_31  37.9M  9.16G  1.60M   234K 20150910 12 min 16 s
                               magnetism_crash_course_physics_32  25.0M  9.18G  1.14M   233K 20161201 9 min 46 s
    the_amazing_life_and_strange_death_of_captain_cook_crash_cou  27.8M  9.21G  2.27M   232K 20120726 10 min 32 s
                     women_s_suffrage_crash_course_us_history_31  37.4M  9.25G  2.04M   232K 20130926 13 min 30 s
    representing_numbers_and_letters_with_binary_crash_course_co  33.1M  9.28G  1.13M   232K 20170315 10 min 45 s
                              enthalpy_crash_course_chemistry_18  29.6M  9.31G  2.04M   232K 20130617 11 min 23 s
                     contractarianism_crash_course_philosophy_37  21.1M  9.33G  1.13M   232K 20161128 9 min 31 s
                                 light_crash_course_astronomy_24  25.7M  9.35G  1.58M   231K 20150709 10 min 33 s
          the_handmaid_s_tale_part_1_crash_course_literature_403  29.9M  9.38G   915K   229K 20171128 12 min 40 s
           rama_and_the_ramayana_crash_course_world_mythology_27  35.8M  9.42G  1.12M   229K 20170922 13 min 24 s
    the_integumentary_system_part_2_skin_deeper_crash_course_a_p  26.3M  9.44G  1.56M   229K 20150216 9 min 56 s
                        the_oort_cloud_crash_course_astronomy_22  29.0M  9.47G  1.55M   227K 20150625 11 min 40 s
                               jupiter_crash_course_astronomy_16  23.6M  9.50G  1.54M   226K 20150508 10 min 42 s
                                 taste_smell_crash_course_a_p_16  24.6M  9.52G  1.54M   225K 20150427 10 min 29 s
              absolute_monarchy_crash_course_european_history_13  32.9M  9.55G   670K   223K 20190727 13 min 15 s
                    personal_identity_crash_course_philosophy_19  19.6M  9.57G  1.31M   223K 20160627 8 min 32 s
            explore_the_solar_system_360_degree_interactive_tour  6.63M  9.58G  1.30M   222K 20160212 4 min 40 s
    constitutional_compromises_crash_course_government_and_polit  24.2M  9.60G  1.51M   221K 20150220 8 min 56 s
    tissues_part_4_types_of_connective_tissues_crash_course_a_p_  24.5M  9.63G  1.51M   221K 20150202 9 min 42 s
                 naked_eye_observations_crash_course_astronomy_2  29.2M  9.65G  1.51M   221K 20150122 11 min 16 s
    thermodynamics_and_energy_diagrams_crash_course_organic_chem  38.3M  9.69G   221K   221K 20201028 11 min 11 s
                     hydrocarbon_power_crash_course_chemistry_40  27.6M  9.72G  1.72M   221K 20131125 11 min 31 s
          circulatory_respiratory_systems_crashcourse_biology_27  30.0M  9.75G  2.15M   220K 20120730 11 min 39 s
           economic_schools_of_thought_crash_course_economics_14  26.2M  9.77G  1.29M   220K 20151106 10 min 4 s
       introduction_to_the_solar_system_crash_course_astronomy_9  25.1M  9.80G  1.49M   218K 20150312 10 min 16 s
              rorschach_and_freudians_crash_course_psychology_21  32.3M  9.83G  1.70M   218K 20140708 12 min 23 s
    population_sustainability_and_malthus_crash_course_world_his  38.7M  9.87G  1.48M   217K 20141107 12 min 50 s
                             language_crash_course_psychology_16  27.0M  9.89G  1.69M   216K 20140526 10 min 1 s
             war_and_civilization_crash_course_world_history_205  37.1M  9.93G  1.68M   215K 20140809 12 min 47 s
                      electrochemistry_crash_course_chemistry_36  21.1M  9.95G  1.67M   214K 20131029 9 min 3 s
                  what_is_engineering_crash_course_engineering_1  29.9M  9.98G   857K   214K 20180517 9 min 36 s
                             distances_crash_course_astronomy_25  26.7M  10.0G  1.46M   214K 20150716 11 min 20 s
    cosmic_sexy_time_eggs_seeds_and_water_crash_course_world_myt  29.7M  10.0G  1.04M   214K 20170311 12 min 21 s
    african_pantheons_and_the_orishas_crash_course_world_mytholo  29.8M  10.1G  1.04M   213K 20170512 11 min 9 s
      expansion_and_consequences_crash_course_european_history_5  48.0M  10.1G   639K   213K 20190511 16 min 33 s
                     the_digestive_system_crashcourse_biology_28  36.9M  10.1G  2.08M   213K 20120806 11 min 52 s
              english_civil_war_crash_course_european_history_14  37.9M  10.2G   636K   212K 20190806 14 min 35 s
           getting_help_psychotherapy_crash_course_psychology_35  25.4M  10.2G  1.44M   211K 20141021 11 min 21 s
    anti_vaxxers_conspiracy_theories_epistemic_responsibility_cr  22.9M  10.2G  1.23M   210K 20160516 9 min 46 s
        to_kill_a_mockingbird_part_1_crash_course_literature_210  34.1M  10.3G  1.64M   210K 20140501 11 min 54 s
      post_world_war_i_recovery_crash_course_european_history_36  39.5M  10.3G   419K   210K 20200225 14 min 47 s
                  evolution_it_s_a_thing_crash_course_biology_20  34.0M  10.3G  2.04M   209K 20120611 11 min 43 s
                feeling_all_the_feels_crash_course_psychology_25  31.1M  10.4G  1.62M   208K 20140804 10 min 50 s
    how_a_bill_becomes_a_law_crash_course_government_and_politic  18.5M  10.4G  1.42M   208K 20150320 7 min 0 s
       political_parties_crash_course_government_and_politics_40  23.7M  10.4G  1.22M   208K 20151204 9 min 22 s
                   lord_of_the_flies_crash_course_literature_305  28.2M  10.4G  1.21M   207K 20160804 11 min 54 s
    what_s_all_the_yellen_about_monetary_policy_and_the_federal_  26.7M  10.5G  1.21M   206K 20151008 9 min 24 s
                         electric_fields_crash_course_physics_26  27.0M  10.5G  1.01M   206K 20161007 9 min 56 s
    bonding_models_and_lewis_structures_crash_course_chemistry_2  32.8M  10.5G  1.81M   205K 20130730 11 min 37 s
    war_and_nation_building_in_latin_america_crash_course_world_  33.4M  10.6G  1.40M   205K 20150211 12 min 13 s
                  uniform_circular_motion_crash_course_physics_7  24.2M  10.6G  1.20M   204K 20160512 9 min 53 s
    your_immune_system_natural_born_killer_crash_course_biology_  45.0M  10.6G  1.99M   204K 20120903 15 min 1 s
                                 stars_crash_course_astronomy_26  30.4M  10.6G  1.39M   204K 20150723 10 min 40 s
    pantheons_of_the_ancient_mediterranean_crash_course_world_my  33.1M  10.7G  0.99M   203K 20170407 13 min 7 s
       world_war_i_battlefields_crash_course_european_history_33  41.4M  10.7G   407K   203K 20200123 14 min 15 s
                         traveling_waves_crash_course_physics_17  15.8M  10.7G  1.19M   203K 20160728 7 min 44 s
          income_and_wealth_inequality_crash_course_economics_17  27.7M  10.8G  1.18M   202K 20151206 10 min 15 s
                                 venus_crash_course_astronomy_14  23.6M  10.8G  1.38M   201K 20150424 10 min 49 s
    the_central_processing_unit_cpu_crash_course_computer_scienc  26.2M  10.8G  0.98M   201K 20170405 11 min 37 s
    reform_and_revolution_1815_1848_crash_course_european_histor  35.7M  10.8G   400K   200K 20191112 14 min 5 s
    language_voice_and_holden_caulfield_the_catcher_in_the_rye_p  23.7M  10.9G  1.75M   199K 20130110 10 min 51 s
                        compatibilism_crash_course_philosophy_25  22.1M  10.9G  1.16M   198K 20160822 8 min 54 s
                           equilibrium_crash_course_chemistry_28  27.6M  10.9G  1.74M   198K 20130826 10 min 56 s
    of_pentameter_bear_baiting_romeo_juliet_part_1_crash_course_  33.4M  11.0G  1.74M   198K 20121129 12 min 41 s
                                 friction_crash_course_physics_6  22.2M  11.0G  1.16M   198K 20160505 10 min 58 s
    the_rise_of_the_west_and_historical_methodology_crash_course  31.3M  11.0G  1.35M   197K 20141017 11 min 53 s
      presidential_power_crash_course_government_and_politics_11  16.5M  11.0G  1.35M   197K 20150411 6 min 29 s
    the_medieval_islamicate_world_crash_course_history_of_scienc  35.2M  11.1G   786K   196K 20180514 13 min 3 s
    the_railroad_journey_and_the_industrial_revolution_crash_cou  34.5M  11.1G  1.34M   196K 20141101 12 min 30 s
      5_human_impacts_on_the_environment_crash_course_ecology_10  32.8M  11.1G  1.72M   196K 20130107 10 min 37 s
                       galaxies_part_1_crash_course_astronomy_38  28.3M  11.1G  1.14M   195K 20151029 12 min 5 s
               dutch_golden_age_crash_course_european_history_15  34.4M  11.2G   585K   195K 20190813 13 min 43 s
                     nuclear_chemistry_crash_course_chemistry_38  23.6M  11.2G  1.52M   195K 20131111 9 min 57 s
                          life_begins_crash_course_big_history_4  36.5M  11.2G  1.33M   194K 20141008 13 min 28 s
             fiscal_policy_and_stimulus_crash_course_economics_8  35.2M  11.3G  1.33M   194K 20150916 11 min 53 s
    was_gatsby_great_the_great_gatsby_part_2_crash_course_englis  20.4M  11.3G  1.69M   193K 20121220 8 min 49 s
    catholic_counter_reformation_crash_course_european_history_9  34.2M  11.3G   579K   193K 20190607 13 min 43 s
    reproductive_system_part_4_pregnancy_development_crash_cours  25.2M  11.4G  1.13M   192K 20151123 10 min 44 s
         the_big_bang_cosmology_part_1_crash_course_astronomy_42  34.1M  11.4G  1.13M   192K 20151210 13 min 22 s
    don_t_reanimate_corpses_frankenstein_part_1_crash_course_lit  31.7M  11.4G  1.50M   192K 20140327 12 min 56 s
                       jupiter_s_moons_crash_course_astronomy_17  25.6M  11.4G  1.30M   191K 20150514 10 min 29 s
    reformation_and_consequences_crash_course_european_history_7  36.1M  11.5G   573K   191K 20190526 13 min 37 s
                              the_moon_crash_course_astronomy_12  23.8M  11.5G  1.30M   191K 20150409 9 min 50 s
                precipitation_reactions_crash_course_chemistry_9  24.5M  11.5G  1.68M   191K 20130415 11 min 30 s
      what_is_organic_chemistry_crash_course_organic_chemistry_1  24.7M  11.5G   377K   189K 20200430 10 min 15 s
                      batman_identity_crash_course_philosophy_18  22.9M  11.6G  1.10M   188K 20160620 9 min 8 s
            blood_part_2_there_will_be_blood_crash_course_a_p_30  23.3M  11.6G  1.28M   188K 20150811 10 min 0 s
             battles_of_the_civil_war_crash_course_us_history_19  15.1M  11.6G  1.65M   187K 20130620 7 min 24 s
    water_and_classical_civilizations_crash_course_world_history  32.3M  11.6G  1.27M   186K 20150121 11 min 8 s
                               eclipses_crash_course_astronomy_5  22.0M  11.7G  1.27M   185K 20150213 10 min 31 s
              parasympathetic_nervous_system_crash_course_a_p_15  20.6M  11.7G  1.27M   185K 20150420 10 min 16 s
    earth_mothers_and_rebellious_sons_creation_part_3_crash_cour  31.1M  11.7G   925K   185K 20170317 12 min 6 s
         george_orwell_s_1984_part_2_crash_course_literature_402  30.2M  11.7G   740K   185K 20171121 12 min 41 s
             the_history_of_life_on_earth_crash_course_ecology_1  40.9M  11.8G  1.62M   185K 20121105 13 min 36 s
      water_solutions_for_dirty_laundry_crash_course_chemistry_7  30.9M  11.8G  1.62M   185K 20130325 13 min 33 s
                                  crash_course_sociology_preview  4.20M  11.8G   923K   185K 20170227 1 min 19 s
    nonviolence_and_peace_movements_crash_course_world_history_2  35.2M  11.8G  1.26M   184K 20150313 12 min 48 s
    the_greeks_and_romans_pantheons_part_3_crash_course_world_my  30.0M  11.9G   920K   184K 20170422 12 min 45 s
                productivity_and_growth_crash_course_economics_6  25.4M  11.9G  1.26M   184K 20150828 8 min 50 s
                     digestive_system_part_3_crash_course_a_p_35  22.4M  11.9G  1.26M   184K 20150922 10 min 23 s
    intro_to_history_of_science_crash_course_history_of_science_  29.2M  12.0G   735K   184K 20180326 12 min 19 s
                                   sound_crash_course_physics_18  24.0M  12.0G  1.08M   184K 20160804 9 min 38 s
                     money_and_finance_crash_course_economics_11  30.6M  12.0G  1.07M   183K 20151014 10 min 35 s
            ma_ui_oceania_s_hero_crash_course_world_mythology_31  38.4M  12.0G   733K   183K 20171022 13 min 23 s
    ford_carter_and_the_economic_malaise_crash_course_us_history  31.8M  12.1G  1.43M   183K 20131221 13 min 22 s
                 lab_techniques_safety_crash_course_chemistry_21  26.3M  12.1G  1.60M   182K 20130708 9 min 2 s
                                  tides_crash_course_astronomy_8  21.9M  12.1G  1.24M   181K 20150305 9 min 46 s
                    vectors_and_2d_motion_crash_course_physics_4  20.5M  12.1G  1.06M   181K 20160421 10 min 5 s
                            ph_and_poh_crash_course_chemistry_30  24.6M  12.2G  1.59M   180K 20130909 11 min 22 s
                               mercury_crash_course_astronomy_13  23.3M  12.2G  1.23M   180K 20150416 10 min 17 s
         indiana_jones_pascal_s_wager_crash_course_philosophy_15  23.5M  12.2G  1.05M   180K 20160523 9 min 12 s
                         the_milky_way_crash_course_astronomy_37  34.1M  12.2G  1.05M   180K 20151022 11 min 13 s
                  what_is_a_good_life_crash_course_philosophy_46  24.1M  12.3G   899K   180K 20170213 9 min 17 s
                      cycles_in_the_sky_crash_course_astronomy_3  22.7M  12.3G  1.23M   180K 20150129 9 min 28 s
                divine_command_theory_crash_course_philosophy_33  22.2M  12.3G   893K   179K 20161031 9 min 1 s
    the_rise_of_russia_and_prussia_crash_course_european_history  37.3M  12.4G   533K   178K 20190827 14 min 55 s
             game_theory_and_oligopoly_crash_course_economics_26  26.0M  12.4G  1.04M   178K 20160305 9 min 55 s
                                saturn_crash_course_astronomy_18  28.6M  12.4G  1.21M   176K 20150521 12 min 15 s
          where_does_your_mind_reside_crash_course_philosophy_22  21.0M  12.4G  1.03M   176K 20160801 9 min 6 s
               exploring_the_universe_crash_course_big_history_2  36.8M  12.5G  1.37M   176K 20140924 14 min 36 s
                       galaxies_part_2_crash_course_astronomy_39  36.1M  12.5G  1.02M   174K 20151105 15 min 34 s
                          crash_course_organic_chemistry_preview  10.5M  12.5G   348K   174K 20200422 3 min 33 s
                          thermodynamics_crash_course_physics_23  22.6M  12.5G  1.02M   173K 20160915 10 min 3 s
                 monkeys_and_morality_crash_course_psychology_19  30.7M  12.6G  1.35M   173K 20140616 11 min 37 s
                              polymers_crash_course_chemistry_45  26.9M  12.6G  1.34M   172K 20140106 10 min 14 s
         monsters_they_re_us_man_crash_course_world_mythology_36  26.8M  12.6G   686K   172K 20171201 10 min 29 s
                  simple_harmonic_motion_crash_course_physics_16  18.8M  12.6G  1.01M   172K 20160721 9 min 10 s
               aggression_vs_altruism_crash_course_psychology_40  26.4M  12.7G  1.17M   171K 20141124 10 min 40 s
           the_gravity_of_the_situation_crash_course_astronomy_7  21.3M  12.7G  1.16M   169K 20150226 10 min 2 s
              operating_systems_crash_course_computer_science_18  37.0M  12.7G   845K   169K 20170628 13 min 35 s
       inflation_and_bubbles_and_tulips_crash_course_economics_7  30.2M  12.7G  1.15M   169K 20150912 10 min 24 s
    wwi_s_civilians_the_homefront_and_an_uneasy_peace_crash_cour  37.3M  12.8G   335K   168K 20200129 14 min 6 s
                          nomenclature_crash_course_chemistry_44  20.4M  12.8G  1.31M   168K 20131230 9 min 4 s
                          brown_dwarfs_crash_course_astronomy_28  26.3M  12.8G  1.14M   167K 20150813 11 min 5 s
                        blood_vessels_part_2_crash_course_a_p_28  20.8M  12.8G  1.14M   167K 20150727 9 min 3 s
    structure_of_the_court_system_crash_course_government_and_po  18.0M  12.9G  1.14M   167K 20150605 6 min 58 s
             entropy_embrace_the_chaos_crash_course_chemistry_20  40.1M  12.9G  1.47M   167K 20130701 13 min 40 s
                             the_earth_crash_course_astronomy_11  25.2M  12.9G  1.14M   167K 20150402 10 min 13 s
                      what_is_geography_crash_course_geography_1  43.4M  13.0G   166K   166K 20201130 10 min 32 s
      emile_durkheim_on_suicide_society_crash_course_sociology_5  26.3M  13.0G   830K   166K 20170410 9 min 36 s
                     the_deep_future_crash_course_big_history_10  35.0M  13.0G  1.13M   166K 20150109 13 min 30 s
    arguments_against_personal_identity_crash_course_philosophy_  24.8M  13.1G   992K   165K 20160711 9 min 43 s
       great_glands_your_endocrine_system_crashcourse_biology_33  32.5M  13.1G  1.61M   165K 20120910 11 min 20 s
                                 crash_course_statistics_preview  8.58M  13.1G   657K   164K 20180117 2 min 59 s
                      gamma_ray_bursts_crash_course_astronomy_40  36.0M  13.1G   985K   164K 20151112 14 min 4 s
                                   alchemy_history_of_science_10  30.0M  13.2G   654K   164K 20180611 12 min 49 s
                      special_relativity_crash_course_physics_42  24.3M  13.2G   815K   163K 20170223 8 min 58 s
    social_orders_and_creation_stories_crash_course_world_mythol  28.1M  13.2G   815K   163K 20170325 10 min 32 s
    who_even_is_an_entrepreneur_crash_course_business_entreprene  25.5M  13.2G   488K   163K 20190814 13 min 1 s
    market_failures_taxes_and_subsidies_crash_course_economics_2  36.1M  13.3G   976K   163K 20160122 12 min 11 s
    globalization_and_trade_and_poverty_crash_course_economics_1  26.4M  13.3G   973K   162K 20151127 9 min 1 s
                             telescopes_crash_course_astronomy_6  28.2M  13.3G  1.11M   162K 20150219 11 min 59 s
                        electric_current_crash_course_physics_28  24.2M  13.3G   809K   162K 20161020 8 min 22 s
                  cybersecurity_crash_course_computer_science_31  35.4M  13.4G   646K   162K 20171011 12 min 29 s
                           aesthetics_crash_course_philosophy_31  25.4M  13.4G   807K   161K 20161017 10 min 37 s
                            exoplanets_crash_course_astronomy_27  31.0M  13.4G  1.10M   161K 20150806 11 min 49 s
             binary_and_multiple_stars_crash_course_astronomy_34  29.0M  13.5G  1.09M   160K 20151001 12 min 0 s
             roman_engineering_crash_course_history_of_science_6  28.6M  13.5G   636K   159K 20180507 12 min 28 s
                         sex_sexuality_crash_course_sociology_31  35.4M  13.5G   636K   159K 20171030 11 min 33 s
    commerce_agriculture_and_slavery_crash_course_european_histo  40.8M  13.6G   475K   158K 20190602 15 min 33 s
                                  mars_crash_course_astronomy_15  24.2M  13.6G  1.07M   156K 20150430 10 min 11 s
    free_will_witches_murder_and_macbeth_part_1_crash_course_lit  32.2M  13.6G   625K   156K 20180123 12 min 55 s
                      migration_crash_course_european_history_29  34.7M  13.7G   312K   156K 20191210 13 min 57 s
    machine_learning_artificial_intelligence_crash_course_comput  25.7M  13.7G   622K   155K 20171101 11 min 50 s
                          light_is_waves_crash_course_physics_39  21.9M  13.7G   777K   155K 20170126 9 min 44 s
                                    crash_course_physics_preview  6.65M  13.7G   931K   155K 20160218 2 min 35 s
                              collisions_crash_course_physics_10  19.0M  13.7G   930K   155K 20160602 9 min 20 s
                               crash_course_study_skills_preview  5.07M  13.7G   775K   155K 20170801 1 min 39 s
                    non_human_animals_crash_course_philosophy_42  24.1M  13.8G   774K   155K 20170116 9 min 46 s
    post_war_rebuilding_and_the_cold_war_crash_course_european_h  39.5M  13.8G   309K   155K 20200421 14 min 45 s
       migrations_and_intensification_crash_course_big_history_7  40.0M  13.8G  1.06M   155K 20141126 13 min 40 s
       expansion_and_resistance_crash_course_european_history_28  33.5M  13.9G   309K   154K 20191203 13 min 13 s
          dark_energy_cosmology_part_2_crash_course_astronomy_43  25.4M  13.9G   925K   154K 20151217 11 min 22 s
     assisted_death_the_value_of_life_crash_course_philosophy_45  26.0M  13.9G   765K   153K 20170206 9 min 53 s
                humans_and_energy_crash_course_world_history_207  19.8M  13.9G  1.19M   153K 20140828 7 min 20 s
                                 taxes_crash_course_economics_31  30.3M  14.0G   914K   152K 20160427 12 min 28 s
              the_presocratics_crash_course_history_of_science_2  27.0M  14.0G   608K   152K 20180409 12 min 31 s
               reader_it_s_jane_eyre_crash_course_literature_207  40.9M  14.0G  1.19M   152K 20140410 13 min 11 s
          pride_and_prejudice_part_1_crash_course_literature_411  27.2M  14.1G   607K   152K 20180206 11 min 43 s
                           personhood_crash_course_philosophy_21  22.9M  14.1G   906K   151K 20160725 9 min 13 s
                the_evolutionary_epic_crash_course_big_history_5  41.3M  14.1G  1.03M   151K 20141029 15 min 4 s
                  the_apocalyspe_crash_course_world_mythology_23  33.1M  14.2G   752K   150K 20170818 12 min 2 s
        old_odd_archaea_bacteria_protists_crashcourse_biology_35  38.5M  14.2G  1.47M   150K 20120924 12 min 16 s
    the_excretory_system_from_your_heart_to_the_toilet_crashcour  31.0M  14.2G  1.47M   150K 20120813 12 min 20 s
              how_to_speak_chemistrian_crash_course_chemistry_11  24.7M  14.2G  1.32M   150K 20130430 10 min 42 s
                 metabolism_nutrition_part_2_crash_course_a_p_37  23.8M  14.3G  1.02M   150K 20151005 10 min 7 s
                         crash_course_history_of_science_preview  6.14M  14.3G   596K   149K 20180319 2 min 2 s
                        low_mass_stars_crash_course_astronomy_29  28.8M  14.3G  1.02M   149K 20150820 12 min 2 s
                    movies_are_magic_crash_course_film_history_1  23.8M  14.3G   744K   149K 20170413 9 min 43 s
                           moral_luck_crash_course_philosophy_39  23.3M  14.3G   743K   149K 20161212 9 min 45 s
    modern_thought_and_culture_in_1900_crash_course_european_his  34.8M  14.4G   297K   149K 20200108 15 min 8 s
    humans_and_nature_and_creation_crash_course_world_mythology_  29.0M  14.4G   742K   148K 20170331 11 min 2 s
    congressional_committees_crash_course_government_and_politic  22.2M  14.4G  1.01M   148K 20150306 8 min 27 s
             sociology_research_methods_crash_course_sociology_4  23.9M  14.5G   740K   148K 20170403 10 min 10 s
            serpents_and_dragons_crash_course_world_mythology_38  29.4M  14.5G   592K   148K 20171222 11 min 23 s
    the_first_programming_languages_crash_course_computer_scienc  29.6M  14.5G   738K   148K 20170510 11 min 51 s
                     language_meaning_crash_course_philosophy_26  21.6M  14.5G   884K   147K 20160829 9 min 31 s
    cultures_subcultures_and_countercultures_crash_course_sociol  26.9M  14.6G   734K   147K 20170522 9 min 39 s
      bureaucracy_basics_crash_course_government_and_politics_15  17.6M  14.6G  1.00M   147K 20150509 6 min 58 s
               drought_and_famine_crash_course_world_history_208  31.4M  14.6G  1.14M   146K 20140905 10 min 29 s
              computer_networks_crash_course_computer_science_28  31.5M  14.6G   731K   146K 20170913 12 min 19 s
                               nebulae_crash_course_astronomy_36  30.7M  14.7G   877K   146K 20151015 12 min 15 s
    the_anthropocene_and_the_near_future_crash_course_big_histor  32.9M  14.7G  1.00M   146K 20141211 12 min 19 s
    world_war_ii_civilians_and_soldiers_crash_course_european_hi  39.0M  14.7G   292K   146K 20200331 14 min 24 s
    recession_hyperinflation_and_stagflation_crash_course_econ_1  27.3M  14.8G   875K   146K 20151030 9 min 53 s
    introduction_to_media_literacy_crash_course_media_literacy_1  22.2M  14.8G   582K   146K 20180227 10 min 37 s
                 fungi_death_becomes_them_crashcourse_biology_39  35.5M  14.8G  1.28M   145K 20121022 11 min 51 s
                        race_ethnicity_crash_course_sociology_34  27.0M  14.8G   581K   145K 20171120 10 min 58 s
       ecology_rules_for_living_on_earth_crash_course_biology_40  33.5M  14.9G  1.27M   145K 20121029 10 min 25 s
                the_modern_revolution_crash_course_big_history_8  41.9M  14.9G  0.99M   145K 20141204 13 min 57 s
       a_brief_history_of_the_universe_crash_course_astronomy_44  31.7M  15.0G   864K   144K 20160107 12 min 35 s
                       brains_vs_bias_crash_course_psychology_24  32.6M  15.0G  1.12M   144K 20140728 11 min 3 s
                  what_is_linguistics_crash_course_linguistics_1  44.7M  15.0G   287K   144K 20200911 11 min 11 s
    if_one_finger_brought_oil_things_fall_apart_part_1_crash_cou  27.2M  15.1G  1.11M   142K 20140417 10 min 18 s
                             what_is_a_game_crash_course_games_1  26.7M  15.1G   853K   142K 20160401 10 min 17 s
                the_yellow_wallpaper_crash_course_literature_407  34.3M  15.1G   568K   142K 20180110 13 min 34 s
    congressional_elections_crash_course_government_and_politics  25.3M  15.1G   993K   142K 20150227 8 min 57 s
                    the_sun_the_earth_crash_course_big_history_3  34.1M  15.2G  1.10M   141K 20141002 14 min 32 s
           enlightened_monarchs_crash_course_european_history_19  34.4M  15.2G   423K   141K 20190916 13 min 40 s
    before_i_got_my_eye_put_out_the_poetry_of_emily_dickinson_cr  22.6M  15.2G  1.24M   141K 20130124 10 min 10 s
     legal_system_basics_crash_course_government_and_politics_18  21.9M  15.2G   978K   140K 20150530 8 min 13 s
              the_atomic_bomb_crash_course_history_of_science_33  27.9M  15.3G   418K   139K 20190114 12 min 4 s
                        circuit_analysis_crash_course_physics_30  31.5M  15.3G   696K   139K 20161104 10 min 55 s
             big_guns_the_muscular_system_crashcourse_biology_31  33.5M  15.3G  1.36M   139K 20120827 12 min 51 s
    nitrogen_phosphorus_cycles_always_recycle_part_2_crash_cours  24.6M  15.4G  1.22M   139K 20121231 9 min 21 s
                             asteroids_crash_course_astronomy_20  27.6M  15.4G   972K   139K 20150604 11 min 32 s
                       rotational_motion_crash_course_physics_11  17.9M  15.4G   832K   139K 20160609 8 min 55 s
    herakles_or_hercules_a_problematic_hero_crash_course_world_m  33.2M  15.4G   555K   139K 20171014 12 min 51 s
    eastern_europe_consolidates_crash_course_european_history_16  46.5M  15.5G   416K   139K 20190819 15 min 17 s
                 vascular_plants_winning_crash_course_biology_37  32.3M  15.5G  1.21M   138K 20121008 11 min 53 s
    ophelia_gertrude_and_regicide_hamlet_part_2_crash_course_lit  30.1M  15.5G  1.08M   138K 20140320 11 min 1 s
               civil_rights_liberties_crash_course_government_23  20.9M  15.6G   966K   138K 20150717 7 min 55 s
                    civil_engineering_crash_course_engineering_2  27.0M  15.6G   552K   138K 20180524 8 min 45 s
    darwin_and_natural_selection_crash_course_history_of_science  29.6M  15.6G   552K   138K 20181001 13 min 9 s
                         deficits_debts_crash_course_economics_9  20.4M  15.6G   956K   137K 20150923 7 min 30 s
    mean_median_and_mode_measures_of_central_tendency_crash_cour  31.6M  15.7G   546K   137K 20180207 11 min 22 s
                medieval_china_crash_course_history_of_science_8  28.7M  15.7G   546K   136K 20180521 12 min 34 s
    aliens_time_travel_and_dresden_slaughterhouse_five_part_1_cr  27.4M  15.7G  1.07M   136K 20140515 10 min 33 s
                        newtonian_gravity_crash_course_physics_8  18.8M  15.7G   818K   136K 20160519 9 min 19 s
                        netflix_chill_crash_course_philosophy_27  20.1M  15.8G   817K   136K 20160912 9 min 10 s
                data_structures_crash_course_computer_science_14  21.3M  15.8G   677K   135K 20170531 10 min 6 s
                      energy_chemistry_crash_course_chemistry_17  28.1M  15.8G  1.19M   135K 20130610 9 min 25 s
                the_economics_of_healthcare_crash_course_econ_29  25.4M  15.8G   812K   135K 20160406 10 min 25 s
                speciation_of_ligers_men_crash_course_biology_15  32.0M  15.9G  1.32M   135K 20120507 10 min 24 s
                 decolonization_crash_course_european_history_43  35.0M  15.9G   270K   135K 20200519 13 min 22 s
      everything_the_universe_and_life_crash_course_astronomy_46  31.2M  15.9G   809K   135K 20160121 11 min 22 s
        sociology_the_scientific_method_crash_course_sociology_3  29.8M  16.0G   671K   134K 20170327 9 min 55 s
    presidential_powers_2_crash_course_government_and_politics_1  21.3M  16.0G   937K   134K 20150417 7 min 52 s
                       discrimination_crash_course_philosophy_41  20.2M  16.0G   669K   134K 20170110 9 min 6 s
    population_genetics_when_darwin_met_mendel_crash_course_biol  34.1M  16.0G  1.30M   133K 20120528 11 min 3 s
         judicial_review_crash_course_government_and_politics_21  23.5M  16.1G   934K   133K 20150626 8 min 0 s
                       alkenes_alkynes_crash_course_chemistry_41  23.2M  16.1G  1.04M   133K 20131209 9 min 35 s
     post_world_war_ii_recovery_crash_course_european_history_42  39.4M  16.1G   264K   132K 20200505 15 min 56 s
           software_engineering_crash_course_computer_science_16  26.6M  16.1G   659K   132K 20170614 10 min 34 s
          the_poetry_of_sylvia_plath_crash_course_literature_216  26.1M  16.2G  1.03M   131K 20140612 11 min 17 s
               what_is_artificial_intelligence_crash_course_ai_1  28.7M  16.2G   393K   131K 20190809 11 min 45 s
                 reading_assignments_crash_course_study_skills_2  22.2M  16.2G   654K   131K 20170815 9 min 53 s
                   pan_s_labyrinth_crash_course_film_criticism_9  27.3M  16.2G   522K   130K 20180315 11 min 20 s
               induction_an_introduction_crash_course_physics_34  21.5M  16.3G   652K   130K 20161216 9 min 48 s
                         star_clusters_crash_course_astronomy_35  32.9M  16.3G   781K   130K 20151008 10 min 35 s
    hermes_and_loki_and_tricksters_part_2_crash_course_world_myt  31.1M  16.3G   651K   130K 20170806 11 min 59 s
    artificial_intelligence_personhood_crash_course_philosophy_2  22.8M  16.4G   781K   130K 20160808 9 min 25 s
           18th_century_warfare_crash_course_european_history_20  40.1M  16.4G   390K   130K 20190924 14 min 58 s
    love_or_lust_romeo_and_juliet_part_2_crash_course_english_li  30.1M  16.4G  1.14M   130K 20121206 10 min 10 s
                                integrals_crash_course_physics_3  21.4M  16.4G   777K   130K 20160414 10 min 8 s
                   the_dying_god_crash_course_world_mythology_19  29.8M  16.5G   646K   129K 20170714 10 min 43 s
                    modern_life_crash_course_european_history_30  38.7M  16.5G   258K   129K 20191217 14 min 32 s
                           calorimetry_crash_course_chemistry_19  28.9M  16.5G  1.13M   129K 20130624 11 min 56 s
                          what_is_a_map_crash_course_geography_2  40.6M  16.6G   129K   129K 20201214 10 min 29 s
                         crash_course_anatomy_physiology_preview  4.49M  16.6G   897K   128K 20141215 1 min 52 s
                    theories_of_gender_crash_course_sociology_33  24.3M  16.6G   512K   128K 20171113 10 min 36 s
                                  torque_crash_course_physics_12  16.1M  16.6G   767K   128K 20160616 8 min 2 s
    monopolies_and_anti_competitive_markets_crash_course_economi  28.1M  16.6G   765K   127K 20160226 10 min 16 s
    population_ecology_the_texas_mosquito_mystery_crash_course_e  33.7M  16.7G  1.12M   127K 20121112 11 min 52 s
        labor_markets_and_minimum_wage_crash_course_economics_28  29.8M  16.7G   763K   127K 20160327 10 min 37 s
                 mathematical_thinking_crash_course_statistics_2  33.0M  16.7G   508K   127K 20180131 11 min 0 s
    the_scientific_revolution_crash_course_history_of_science_12  28.8M  16.8G   504K   126K 20180702 12 min 45 s
               shakespeare_s_sonnets_crash_course_literature_304  38.4M  16.8G   755K   126K 20160727 12 min 26 s
                          what_is_theater_crash_course_theater_1  33.8M  16.8G   503K   126K 20180209 14 min 6 s
         election_basics_crash_course_government_and_politics_36  25.8M  16.9G   753K   125K 20151023 8 min 45 s
        white_dwarfs_planetary_nebulae_crash_course_astronomy_30  28.2M  16.9G   877K   125K 20150827 11 min 9 s
                    max_weber_modernity_crash_course_sociology_9  31.0M  16.9G   626K   125K 20170508 10 min 16 s
      history_of_the_4th_of_july_crash_course_us_history_special  17.1M  16.9G  1.09M   124K 20130704 5 min 27 s
    holden_jd_and_the_red_cap_the_catcher_in_the_rye_part_2_cras  21.1M  17.0G  1.09M   124K 20130117 8 min 20 s
                         nuclear_physics_crash_course_physics_45  23.8M  17.0G   618K   124K 20170320 10 min 23 s
                        fluids_in_motion_crash_course_physics_15  20.8M  17.0G   741K   124K 20160714 9 min 46 s
               aesthetic_appreciation_crash_course_philosophy_30  24.5M  17.0G   740K   123K 20161003 9 min 25 s
       freedom_of_speech_crash_course_government_and_politics_25  21.0M  17.1G   863K   123K 20150731 6 min 51 s
    langston_hughes_and_the_harlem_renaissance_crash_course_lite  26.5M  17.1G   983K   123K 20140605 11 min 31 s
     ecosystem_ecology_links_in_the_chain_crash_course_ecology_7  32.1M  17.1G  1.08M   123K 20121218 10 min 9 s
                 great_goddesses_crash_course_world_mythology_13  27.4M  17.1G   610K   122K 20170528 11 min 10 s
                      citizen_kane_crash_course_film_criticism_1  25.2M  17.2G   487K   122K 20180111 10 min 39 s
           instructions_programs_crash_course_computer_science_8  22.2M  17.2G   609K   122K 20170412 10 min 35 s
                   family_obligations_crash_course_philosophy_43  23.6M  17.2G   609K   122K 20170123 9 min 22 s
                biomedical_treatments_crash_course_psychology_36  27.5M  17.2G   851K   122K 20141027 11 min 8 s
            advanced_cpu_designs_crash_course_computer_science_9  32.3M  17.3G   608K   122K 20170426 12 min 22 s
    check_yourself_with_lateral_reading_crash_course_navigating_  38.2M  17.3G   364K   121K 20190122 13 min 51 s
                witches_and_hags_crash_course_world_mythology_39  22.3M  17.3G   485K   121K 20180112 9 min 40 s
             2001_a_space_odyssey_crash_course_film_criticism_15  28.5M  17.3G   484K   121K 20180426 13 min 38 s
               mechanical_engineering_crash_course_engineering_3  21.7M  17.4G   484K   121K 20180531 9 min 38 s
               the_global_carbon_cycle_crash_course_chemistry_46  24.9M  17.4G   967K   121K 20140113 10 min 33 s
    introduction_to_crash_course_navigating_digital_information_  32.3M  17.4G   362K   121K 20190108 13 min 33 s
                  human_population_growth_crash_course_ecology_3  34.2M  17.5G  1.06M   121K 20121119 10 min 53 s
                             solutions_crash_course_chemistry_27  19.8M  17.5G  1.06M   120K 20130819 8 min 20 s
          the_fall_of_communism_crash_course_european_history_47  53.9M  17.5G   240K   120K 20200716 13 min 24 s
               planning_organization_crash_course_study_skills_4  23.1M  17.6G   601K   120K 20170829 9 min 25 s
                  studying_for_exams_crash_course_study_skills_7  20.6M  17.6G   600K   120K 20170919 8 min 58 s
                  cities_of_myth_crash_course_world_mythology_35  32.1M  17.6G   479K   120K 20171118 12 min 24 s
    understanding_financial_statements_and_accounting_crash_cour  24.4M  17.6G   239K   120K 20191127 12 min 42 s
    the_hydrologic_and_carbon_cycles_always_recycle_crash_course  30.9M  17.7G  1.05M   119K 20121224 10 min 3 s
     ancient_medieval_medicine_crash_course_history_of_science_9  28.7M  17.7G   477K   119K 20180604 12 min 5 s
                   how_words_can_harm_crash_course_philosophy_28  25.6M  17.7G   714K   119K 20160919 10 min 45 s
    congressional_leadership_crash_course_government_and_politic  22.4M  17.7G   830K   119K 20150314 8 min 11 s
    the_basics_of_organic_nomenclature_crash_course_organic_chem  30.1M  17.8G   236K   118K 20200506 12 min 47 s
                         socialization_crash_course_sociology_14  23.0M  17.8G   590K   118K 20170620 9 min 35 s
    georges_melies_master_of_illusion_crash_course_film_history_  24.4M  17.8G   589K   118K 20170504 10 min 21 s
    nuclear_chemistry_part_2_fusion_and_fission_crash_course_che  24.7M  17.8G   941K   118K 20131119 11 min 17 s
           poverty_our_response_to_it_crash_course_philosophy_44  20.2M  17.9G   587K   117K 20170130 8 min 53 s
                              memory_crash_course_study_skills_3  25.0M  17.9G   586K   117K 20170822 10 min 51 s
                  symbols_values_norms_crash_course_sociology_10  22.8M  17.9G   586K   117K 20170515 9 min 32 s
          the_handmaid_s_tale_part_2_crash_course_literature_404  34.5M  17.9G   467K   117K 20171205 12 min 12 s
                                comets_crash_course_astronomy_21  30.8M  18.0G   815K   116K 20150618 11 min 54 s
         interest_groups_crash_course_government_and_politics_42  19.8M  18.0G   695K   116K 20151219 8 min 12 s
                                  crash_course_geography_preview  16.3M  18.0G   116K   116K 20201117 3 min 22 s
    voltage_electric_energy_and_capacitors_crash_course_physics_  23.0M  18.0G   577K   115K 20161014 10 min 13 s
                               meteors_crash_course_astronomy_23  26.0M  18.0G   799K   114K 20150702 11 min 21 s
                 frankenstein_part_2_crash_course_literature_206  36.2M  18.1G   906K   113K 20140403 12 min 37 s
                     procrastination_crash_course_study_skills_6  22.7M  18.1G   565K   113K 20170912 10 min 26 s
                          fluids_at_rest_crash_course_physics_14  18.9M  18.1G   678K   113K 20160708 9 min 58 s
                                crash_course_engineering_preview  6.02M  18.1G   452K   113K 20180510 2 min 9 s
                 social_stratification_crash_course_sociology_21  23.4M  18.2G   563K   113K 20170807 10 min 41 s
                            semantics_crash_course_linguistics_5  43.0M  18.2G   112K   112K 20201009 10 min 38 s
                 equilibrium_equations_crash_course_chemistry_29  20.4M  18.2G  0.99M   112K 20130903 9 min 28 s
    programming_basics_statements_functions_crash_course_compute  23.4M  18.2G   561K   112K 20170517 11 min 56 s
    nonexistent_objects_imaginary_worlds_crash_course_philosophy  21.4M  18.3G   672K   112K 20160927 9 min 20 s
                 memory_storage_crash_course_computer_science_19  34.5M  18.3G   558K   112K 20170705 12 min 16 s
    galahad_perceval_and_the_holy_grail_crash_course_world_mytho  34.4M  18.3G   554K   111K 20170929 13 min 31 s
    supreme_court_of_the_united_states_procedures_crash_course_g  18.4M  18.3G   773K   110K 20150612 6 min 53 s
                                 crash_course_philosophy_preview  5.38M  18.3G   661K   110K 20160118 2 min 12 s
    race_class_and_gender_in_to_kill_a_mockingbird_crash_course_  27.7M  18.4G   881K   110K 20140508 11 min 36 s
                        geometric_optics_crash_course_physics_38  20.1M  18.4G   550K   110K 20170119 9 min 39 s
                    apocalypse_now_crash_course_film_criticism_8  28.7M  18.4G   440K   110K 20180308 11 min 54 s
                micro_biology_crash_course_history_of_science_24  25.7M  18.4G   330K   110K 20181015 12 min 11 s
       the_scientific_methods_crash_course_history_of_science_14  30.3M  18.5G   439K   110K 20180716 13 min 3 s
                               crash_course_film_history_preview  3.57M  18.5G   549K   110K 20170406 1 min 29 s
                    crash_course_artificial_intelligence_preview  11.6M  18.5G   329K   110K 20190802 3 min 49 s
    noah_s_ark_and_floods_in_the_ancient_near_east_crash_course_  27.5M  18.5G   546K   109K 20170616 10 min 22 s
    the_facts_about_fact_checking_crash_course_navigating_digita  30.8M  18.5G   327K   109K 20190115 13 min 54 s
    thespis_athens_and_the_origins_of_greek_drama_crash_course_t  24.7M  18.6G   435K   109K 20180216 10 min 23 s
    the_hero_s_journey_and_the_monomyth_crash_course_world_mytho  32.2M  18.6G   544K   109K 20170902 13 min 19 s
                   cryptography_crash_course_computer_science_33  33.5M  18.6G   434K   109K 20171025 12 min 32 s
    marginal_analysis_roller_coasters_elasticity_and_van_gogh_cr  31.0M  18.7G   649K   108K 20151212 11 min 32 s
                  behavioral_economics_crash_course_economics_27  28.3M  18.7G   636K   106K 20160312 10 min 33 s
                     maxwell_s_equations_crash_course_physics_37  25.9M  18.7G   529K   106K 20170113 10 min 48 s
                                crash_course_linguistics_preview  11.6M  18.7G   211K   105K 20200904 2 min 49 s
      tricksters_an_introduction_crash_course_world_mythology_20  24.5M  18.8G   527K   105K 20170721 10 min 9 s
         introduction_to_intellectual_property_crash_course_ip_1  24.8M  18.8G   736K   105K 20150423 10 min 9 s
      partial_pressures_vapor_pressure_crash_course_chemistry_15  30.0M  18.8G   939K   104K 20130528 11 min 54 s
        the_soviet_bloc_unwinds_crash_course_european_history_46  56.5M  18.9G   207K   104K 20200630 13 min 58 s
    how_presidents_govern_crash_course_government_and_politics_1  25.5M  18.9G   725K   104K 20150501 9 min 22 s
                       papers_essays_crash_course_study_skills_9  20.5M  18.9G   516K   103K 20171003 8 min 59 s
    revolutions_in_science_and_tech_crash_course_european_histor  62.6M  19.0G   206K   103K 20200601 15 min 13 s
          gerrymandering_crash_course_government_and_politics_37  20.4M  19.0G   616K   103K 20151031 7 min 57 s
                     the_physics_of_heat_crash_course_physics_22  22.5M  19.0G   610K   102K 20160908 9 min 15 s
     freedom_of_religion_crash_course_government_and_politics_24  17.5M  19.0G   707K   101K 20150724 6 min 47 s
              early_programming_crash_course_computer_science_10  25.2M  19.1G   505K   101K 20170503 9 min 25 s
    archetypes_and_male_divinities_crash_course_world_mythology_  34.1M  19.1G   502K   100K 20170609 11 min 45 s
                      screenplays_crash_course_film_production_1  18.2M  19.1G   502K   100K 20170824 9 min 18 s
             revenue_profits_and_price_crash_course_economics_24  30.6M  19.1G   602K   100K 20160217 11 min 9 s
                    alan_turing_crash_course_computer_science_15  29.5M  19.2G   501K   100K 20170607 13 min 4 s
          buffers_the_acid_rain_slayer_crash_course_chemistry_31  29.2M  19.2G   901K   100K 20130916 11 min 40 s
    what_is_space_and_how_do_we_study_it_crash_course_geography_  42.8M  19.2G  99.7K  99.7K 20201222 10 min 25 s
               phonetics_1_consonants_crash_course_linguistics_8  41.5M  19.3G  99.1K  99.1K 20201030 11 min 29 s
                    ideal_gas_problems_crash_course_chemistry_13  26.8M  19.3G   890K  98.8K 20130513 11 min 44 s
    coyote_and_raven_american_tricksters_crash_course_world_myth  32.2M  19.3G   494K  98.8K 20170812 12 min 32 s
                                 crash_course_psychology_preview  7.55M  19.3G   781K  97.7K 20140127 2 min 32 s
    monetary_and_fiscal_policy_crash_course_government_and_polit  23.5M  19.4G   585K  97.6K 20160212 9 min 18 s
    price_controls_subsidies_and_the_risks_of_good_intentions_cr  31.7M  19.4G   582K  97.0K 20160113 10 min 14 s
        100_years_of_solitude_part_1_crash_course_literature_306  36.0M  19.4G   582K  96.9K 20160810 11 min 38 s
      fire_and_buffalo_goddesses_crash_course_world_mythology_14  35.8M  19.5G   484K  96.7K 20170602 12 min 26 s
    the_americas_and_time_keeping_crash_course_history_of_scienc  30.9M  19.5G   386K  96.5K 20180430 12 min 48 s
                 focus_concentration_crash_course_study_skills_5  24.0M  19.5G   482K  96.4K 20170905 10 min 12 s
          hackers_cyber_attacks_crash_course_computer_science_32  26.8M  19.5G   385K  96.3K 20171018 11 min 52 s
    markets_efficiency_and_price_signals_crash_course_economics_  31.2M  19.6G   574K  95.7K 20160106 11 min 0 s
    eugenics_and_francis_galton_crash_course_history_of_science_  26.8M  19.6G   286K  95.5K 20181008 12 min 20 s
          foreign_policy_crash_course_government_and_politics_50  29.4M  19.6G   569K  94.8K 20160304 9 min 59 s
                              deviance_crash_course_sociology_18  19.4M  19.6G   472K  94.4K 20170717 9 min 5 s
                   dubois_race_conflict_crash_course_sociology_7  26.3M  19.7G   472K  94.4K 20170424 10 min 39 s
    the_adventures_of_huckleberry_finn_part_1_crash_course_liter  31.0M  19.7G   565K  94.2K 20160714 12 min 23 s
    the_plants_the_bees_plant_reproduction_crashcourse_biology_3  31.3M  19.7G   846K  94.0K 20121015 10 min 23 s
         protests_east_and_west_crash_course_european_history_45  50.0M  19.8G   187K  93.5K 20200620 12 min 27 s
                             candide_crash_course_literature_405  29.7M  19.8G   373K  93.3K 20171213 12 min 12 s
     political_campaigns_crash_course_government_and_politics_39  25.0M  19.8G   559K  93.2K 20151121 9 min 35 s
                                 crash_course_us_history_preview  5.31M  19.8G   185K  92.6K 20200818 1 min 2 s
                           pragmatics_crash_course_linguistics_6  42.2M  19.9G  92.5K  92.5K 20201016 9 min 56 s
     ecological_succession_change_is_good_crash_course_ecology_6  27.5M  19.9G   829K  92.1K 20121210 10 min 1 s
     animal_development_we_re_just_tubes_crash_course_biology_16  30.0M  19.9G   914K  91.4K 20120514 11 min 31 s
    the_reproductive_system_how_gonads_go_crashcourse_biology_34  35.0M  20.0G   913K  91.3K 20120917 12 min 1 s
            aromatics_cyclic_compounds_crash_course_chemistry_42  23.3M  20.0G   729K  91.2K 20131216 9 min 49 s
                theories_of_myth_crash_course_world_mythology_12  33.4M  20.0G   456K  91.1K 20170521 12 min 14 s
        their_eyes_were_watching_god_crash_course_literature_301  25.9M  20.1G   546K  91.0K 20160707 11 min 23 s
    yu_the_engineer_and_flood_stories_from_china_crash_course_wo  23.5M  20.1G   454K  90.8K 20170701 9 min 24 s
    gender_guilt_and_fate_macbeth_part_2_crash_course_literature  30.2M  20.1G   363K  90.7K 20180130 12 min 6 s
           the_skeletal_system_it_s_alive_crashcourse_biology_30  35.9M  20.1G   905K  90.5K 20120820 13 min 10 s
                       lthwr_lzr_y_lhlq_1_mn_crash_course_bl_rby  32.5M  20.2G   361K  90.3K 20180118 11 min 58 s
                   the_internet_crash_course_computer_science_29  29.2M  20.2G   450K  90.0K 20170920 11 min 57 s
            things_fall_apart_part_2_crash_course_literature_209  23.0M  20.2G   720K  90.0K 20140424 9 min 29 s
    who_can_you_trust_crash_course_navigating_digital_informatio  38.5M  20.3G   268K  89.4K 20190129 14 min 45 s
      search_and_seizure_crash_course_government_and_politics_27  23.3M  20.3G   624K  89.2K 20150815 7 min 37 s
              astrophysics_and_cosmology_crash_course_physics_46  24.3M  20.3G   444K  88.9K 20170324 9 min 20 s
    what_history_was_is_and_will_be_crash_course_european_histor  62.3M  20.4G   178K  88.8K 20200828 15 min 6 s
          community_ecology_feel_the_love_crash_course_ecology_4  35.2M  20.4G   794K  88.2K 20121126 11 min 29 s
             files_file_systems_crash_course_computer_science_20  26.2M  20.4G   438K  87.6K 20170712 12 min 2 s
                    measures_of_spread_crash_course_statistics_4  25.4M  20.5G   350K  87.5K 20180214 11 min 46 s
                              religion_crash_course_sociology_39  25.7M  20.5G   348K  87.0K 20180108 11 min 5 s
    types_of_bureaucracies_crash_course_government_and_politics_  17.2M  20.5G   608K  86.8K 20150515 5 min 57 s
      due_process_of_law_crash_course_government_and_politics_28  25.9M  20.5G   607K  86.7K 20150821 8 min 28 s
                                    a_note_on_cc_human_geography  3.51M  20.5G   433K  86.5K 20161031 2 min 3 s
                    the_physics_of_music_crash_course_physics_19  27.5M  20.6G   515K  85.8K 20160811 10 min 34 s
    simple_animals_sponges_jellies_octopuses_crash_course_biolog  35.0M  20.6G   857K  85.7K 20120625 11 min 30 s
    the_sex_lives_of_nonvascular_plants_alternation_of_generatio  30.0M  20.6G   850K  85.0K 20121001 9 min 41 s
                           morphology_crash_course_linguistics_2  41.4M  20.7G   170K  84.9K 20200918 10 min 48 s
       the_shape_of_data_distributions_crash_course_statistics_7  27.6M  20.7G   339K  84.9K 20180307 11 min 22 s
                 the_mwindo_epic_crash_course_world_mythology_29  31.8M  20.7G   339K  84.7K 20171007 12 min 41 s
                       heat_transfer_crash_course_engineering_14  18.3M  20.7G   338K  84.5K 20180823 8 min 35 s
          slavery_ghosts_and_beloved_crash_course_literature_214  27.2M  20.8G   676K  84.5K 20140529 11 min 38 s
    kinetics_chemistry_s_demolition_derby_crash_course_chemistry  23.3M  20.8G   756K  84.0K 20130924 9 min 56 s
    freud_jung_luke_skywalker_and_the_psychology_of_myth_crash_c  30.2M  20.8G   336K  83.9K 20180119 12 min 54 s
               hydrocarbon_derivatives_crash_course_chemistry_43  19.4M  20.8G   670K  83.7K 20131223 8 min 37 s
                     sociolinguistics_crash_course_linguistics_7  45.9M  20.9G  83.5K  83.5K 20201023 11 min 21 s
    racial_ethnic_prejudice_discrimination_crash_course_sociolog  28.7M  20.9G   334K  83.4K 20171127 11 min 39 s
        theories_about_family_marriage_crash_course_sociology_37  27.9M  20.9G   333K  83.2K 20171211 10 min 59 s
    integrated_circuits_moores_law_crash_course_computer_science  37.2M  21.0G   414K  82.8K 20170621 13 min 49 s
                earth_science_crash_course_history_of_science_20  31.1M  21.0G   331K  82.8K 20180910 13 min 43 s
                         social_groups_crash_course_sociology_16  29.1M  21.0G   413K  82.7K 20170703 9 min 51 s
    natural_language_processing_crash_course_computer_science_36  24.9M  21.0G   331K  82.6K 20171122 11 min 49 s
           party_systems_crash_course_government_and_politics_41  27.7M  21.1G   495K  82.6K 20151211 10 min 47 s
    ptsd_and_alien_abduction_slaughterhouse_five_part_2_crash_co  25.9M  21.1G   660K  82.5K 20140522 10 min 25 s
                              ancient_games_crash_course_games_2  26.8M  21.1G   492K  82.0K 20160408 11 min 1 s
                            real_gases_crash_course_chemistry_14  27.4M  21.2G   738K  82.0K 20130520 11 min 34 s
    liberals_conservatives_and_pride_and_prejudice_part_2_crash_  26.5M  21.2G   327K  81.7K 20180213 11 min 11 s
    congressional_decisions_crash_course_government_and_politics  16.5M  21.2G   568K  81.2K 20150327 6 min 35 s
       europe_in_the_global_age_crash_course_european_history_48  47.8M  21.2G   162K  81.1K 20200730 11 min 56 s
                 mythical_horses_crash_course_world_mythology_37  28.3M  21.3G   323K  80.8K 20171217 11 min 16 s
              the_first_movie_camera_crash_course_film_history_2  21.8M  21.3G   401K  80.2K 20170420 9 min 25 s
                       invisible_man_crash_course_literature_308  28.4M  21.3G   479K  79.9K 20160824 11 min 6 s
           tragedy_lessons_from_aristotle_crash_course_theater_3  29.6M  21.3G   319K  79.7K 20180223 12 min 29 s
        21st_century_challenges_crash_course_european_history_49  53.5M  21.4G   159K  79.4K 20200814 12 min 45 s
               the_economics_of_immigration_crash_course_econ_33  28.5M  21.4G   476K  79.4K 20160518 11 min 20 s
    how_to_develop_a_business_idea_crash_course_business_entrepr  23.2M  21.5G   237K  78.9K 20190821 12 min 20 s
                           regression_crash_course_statistics_32  23.5M  21.5G   315K  78.9K 20181003 12 min 39 s
        social_interaction_performance_crash_course_sociology_15  25.0M  21.5G   394K  78.7K 20170626 11 min 37 s
              mythical_mountains_crash_course_world_mythology_33  28.7M  21.5G   315K  78.6K 20171105 11 min 41 s
                  mythical_trees_crash_course_world_mythology_34  29.0M  21.6G   315K  78.6K 20171112 11 min 26 s
                                 announcing_the_crash_course_app  7.78M  21.6G   157K  78.4K 20200501 3 min 21 s
                 gender_stratification_crash_course_sociology_32  25.8M  21.6G   313K  78.3K 20171106 10 min 48 s
                           phonology_crash_course_linguistics_10  49.8M  21.6G  77.9K  77.9K 20201120 12 min 5 s
    the_industrial_revolution_crash_course_history_of_science_21  30.5M  21.7G   311K  77.9K 20180925 12 min 28 s
                            ampere_s_law_crash_course_physics_33  18.6M  21.7G   388K  77.7K 20161208 8 min 44 s
                          doing_solids_crash_course_chemistry_33  22.7M  21.7G   698K  77.5K 20131007 9 min 17 s
                    the_underground_economy_crash_course_econ_32  23.4M  21.7G   464K  77.4K 20160507 9 min 1 s
             z_scores_and_percentiles_crash_course_statistics_18  24.3M  21.8G   310K  77.4K 20180530 10 min 54 s
          market_economy_crash_course_government_and_politics_46  29.0M  21.8G   463K  77.2K 20160129 9 min 38 s
                             ac_circuits_crash_course_physics_36  23.7M  21.8G   386K  77.1K 20170106 10 min 6 s
      mythical_caves_and_gardens_crash_course_world_mythology_32  26.3M  21.8G   308K  77.1K 20171029 10 min 40 s
                       theory_deviance_crash_course_sociology_19  21.1M  21.9G   385K  77.1K 20170724 9 min 45 s
                                anova_crash_course_statistics_33  25.9M  21.9G   231K  76.9K 20181010 13 min 16 s
    harriet_martineau_gender_conflict_theory_crash_course_sociol  22.7M  21.9G   382K  76.3K 20170501 9 min 1 s
    probability_part_1_rules_and_patterns_crash_course_statistic  27.5M  21.9G   304K  76.1K 20180425 12 min 0 s
    the_history_of_electrical_engineering_crash_course_engineeri  23.8M  21.9G   301K  75.3K 20180607 9 min 24 s
                                chordates_crashcourse_biology_24  30.4M  22.0G   753K  75.3K 20120709 12 min 8 s
                   psycholinguistics_crash_course_linguistics_11  42.8M  22.0G  75.2K  75.2K 20201204 11 min 2 s
      affirmative_action_crash_course_government_and_politics_32  19.8M  22.0G   526K  75.1K 20150926 7 min 13 s
                    social_development_crash_course_sociology_13  24.9M  22.1G   375K  75.1K 20170612 10 min 14 s
        einstein_s_revolution_crash_course_history_of_science_32  29.9M  22.1G   225K  74.9K 20190107 12 min 6 s
                  electricity_crash_course_history_of_science_27  27.5M  22.1G   225K  74.8K 20181105 12 min 32 s
                    environmental_econ_crash_course_economics_22  21.3M  22.1G   447K  74.5K 20160127 8 min 22 s
                                 crime_crash_course_sociology_20  27.5M  22.2G   372K  74.4K 20170731 11 min 30 s
                      soviet_montage_crash_course_film_history_8  29.2M  22.2G   369K  73.8K 20170601 12 min 28 s
    evolutionary_development_chicken_teeth_crash_course_biology_  24.8M  22.2G   738K  73.8K 20120521 10 min 56 s
                language_acquisition_crash_course_linguistics_12  44.5M  22.3G  73.7K  73.7K 20201211 10 min 51 s
    biomedical_industrial_engineering_crash_course_engineering_6  24.9M  22.3G   294K  73.5K 20180621 10 min 26 s
                     chi_square_tests_crash_course_statistics_29  22.7M  22.3G   292K  73.0K 20180829 11 min 3 s
    freedom_of_the_press_crash_course_government_and_politics_26  23.1M  22.3G   509K  72.7K 20150807 7 min 16 s
                german_expressionism_crash_course_film_history_7  24.4M  22.4G   363K  72.5K 20170525 10 min 25 s
     mythical_language_and_idiom_crash_course_world_mythology_41  31.5M  22.4G   290K  72.5K 20180128 12 min 48 s
                           supervised_learning_crash_course_ai_2  35.9M  22.4G   217K  72.3K 20190816 15 min 22 s
        biology_before_darwin_crash_course_history_of_science_19  30.1M  22.5G   288K  72.0K 20180827 12 min 50 s
                          crash_course_theater_and_drama_preview  10.9M  22.5G   288K  71.9K 20180202 3 min 48 s
                quantum_mechanics_part_2_crash_course_physics_44  21.1M  22.5G   358K  71.6K 20170309 9 min 7 s
        the_future_of_artificial_intelligence_crash_course_ai_20  28.8M  22.5G   141K  70.7K 20191227 10 min 59 s
                                 statics_crash_course_physics_13  19.2M  22.5G   424K  70.7K 20160623 9 min 7 s
             crash_course_navigating_digital_information_preview  14.0M  22.5G   211K  70.4K 20181218 5 min 11 s
                 american_floods_crash_course_world_mythology_18  25.4M  22.6G   352K  70.4K 20170709 8 min 59 s
                                           crash_course_outtakes  10.7M  22.6G   631K  70.1K 20130530 4 min 48 s
                                       a_history_of_crash_course  43.9M  22.6G   210K  69.9K 20181204 19 min 51 s
    language_change_and_historical_linguistics_crash_course_ling  54.3M  22.7G  69.9K  69.9K 20201218 12 min 12 s
                    the_dawn_of_video_games_crash_course_games_3  27.4M  22.7G   417K  69.6K 20160415 11 min 35 s
      judicial_decisions_crash_course_government_and_politics_22  20.5M  22.7G   485K  69.3K 20150710 7 min 13 s
                                    world_history_year_2_preview  6.41M  22.7G   553K  69.1K 20140627 2 min 35 s
                economics_of_education_crash_course_economics_23  31.3M  22.8G   413K  68.8K 20160211 10 min 25 s
    cathedrals_and_universities_crash_course_history_of_science_  28.6M  22.8G   274K  68.6K 20180625 12 min 29 s
           newton_and_leibniz_crash_course_history_of_science_17  32.7M  22.8G   274K  68.5K 20180814 13 min 49 s
    ir_spectroscopy_and_mass_spectrometry_crash_course_organic_c  51.7M  22.9G   137K  68.4K 20200609 13 min 50 s
             schools_social_inequality_crash_course_sociology_41  29.9M  22.9G   273K  68.2K 20180122 11 min 26 s
                        test_anxiety_crash_course_study_skills_8  22.8M  22.9G   341K  68.1K 20170926 8 min 49 s
                               liquids_crash_course_chemistry_26  27.9M  22.9G   613K  68.1K 20130813 11 min 3 s
       how_voters_decide_crash_course_government_and_politics_38  18.4M  23.0G   408K  68.0K 20151113 7 min 35 s
           copyright_basics_crash_course_intellectual_property_2  28.8M  23.0G   475K  67.8K 20150430 12 min 17 s
                  education_in_society_crash_course_sociology_40  26.4M  23.0G   271K  67.8K 20180115 11 min 31 s
                             crash_course_media_literacy_preview  3.98M  23.0G   271K  67.7K 20180220 1 min 52 s
          public_opinion_crash_course_government_and_politics_33  30.2M  23.1G   473K  67.6K 20151002 9 min 49 s
       media_institution_crash_course_government_and_politics_44  26.0M  23.1G   405K  67.5K 20160116 8 min 44 s
    using_wikipedia_crash_course_navigating_digital_information_  38.2M  23.1G   202K  67.4K 20190205 14 min 15 s
    why_you_need_trust_to_do_business_crash_course_business_soft  30.6M  23.1G   202K  67.3K 20190313 11 min 44 s
                          animal_behavior_crashcourse_biology_25  30.0M  23.2G   671K  67.1K 20120716 10 min 53 s
       3d_structure_and_bonding_crash_course_organic_chemistry_4  57.7M  23.2G   134K  66.9K 20200527 14 min 32 s
                       crash_course_business_soft_skills_preview  6.25M  23.2G   199K  66.5K 20190306 2 min 39 s
             neural_networks_and_deep_learning_crash_course_ai_3  27.4M  23.3G   199K  66.3K 20190823 12 min 22 s
                biotechnology_crash_course_history_of_science_40  31.7M  23.3G   198K  66.2K 20190318 12 min 12 s
    charts_are_like_pasta_data_visualization_part_1_crash_course  24.0M  23.3G   263K  65.7K 20180221 10 min 21 s
            the_new_astronomy_crash_course_history_of_science_13  30.2M  23.3G   262K  65.5K 20180709 12 min 34 s
    changing_the_blueprints_of_life_genetic_engineering_crash_co  27.7M  23.4G   196K  65.2K 20190228 11 min 46 s
             the_world_wide_web_crash_course_computer_science_30  28.5M  23.4G   326K  65.2K 20171004 11 min 36 s
    correlation_doesnt_equal_causation_crash_course_statistics_8  27.8M  23.4G   260K  64.9K 20180314 12 min 17 s
                    compression_crash_course_computer_science_21  29.5M  23.5G   322K  64.4K 20170726 12 min 47 s
                the_lumiere_brothers_crash_course_film_history_3  20.0M  23.5G   320K  64.0K 20170427 9 min 30 s
    the_history_of_chemical_engineering_crash_course_engineering  19.9M  23.5G   256K  63.9K 20180614 8 min 59 s
                 confidence_intervals_crash_course_statistics_20  30.1M  23.5G   255K  63.8K 20180613 13 min 1 s
                   to_the_lighthouse_crash_course_literature_408  30.6M  23.6G   255K  63.7K 20180116 12 min 21 s
        kinetic_theory_and_phase_changes_crash_course_physics_21  20.4M  23.6G   382K  63.6K 20160901 9 min 8 s
       the_columbian_exchange_crash_course_history_of_science_16  30.6M  23.6G   254K  63.6K 20180806 12 min 57 s
                  dc_resistors_batteries_crash_course_physics_29  25.3M  23.6G   317K  63.5K 20161027 10 min 47 s
               the_video_game_crash_of_1983_crash_course_games_6  30.2M  23.7G   381K  63.4K 20160513 10 min 50 s
                   phonetics_2_vowels_crash_course_linguistics_9  43.7M  23.7G  63.3K  63.3K 20201113 11 min 23 s
                               pollution_crash_course_ecology_11  23.8M  23.7G   565K  62.7K 20130114 9 min 21 s
    straight_outta_stratford_upon_avon_shakespeare_s_early_days_  27.0M  23.8G   250K  62.5K 20180518 11 min 26 s
                    3d_graphics_crash_course_computer_science_27  27.6M  23.8G   312K  62.4K 20170906 12 min 40 s
    shaping_public_opinion_crash_course_government_and_politics_  20.8M  23.8G   373K  62.1K 20151009 7 min 20 s
      complex_animals_annelids_arthropods_crashcourse_biology_23  40.0M  23.8G   621K  62.1K 20120702 13 min 14 s
    controlling_bureaucracies_crash_course_government_and_politi  19.0M  23.9G   434K  62.1K 20150523 7 min 24 s
              in_the_mood_for_love_crash_course_film_criticism_5  21.9M  23.9G   248K  62.0K 20180215 9 min 30 s
    more_organic_nomenclature_heteroatom_functional_groups_crash  47.9M  23.9G   124K  62.0K 20200520 12 min 23 s
    the_singularity_skynet_and_the_future_of_computing_crash_cou  32.4M  24.0G   248K  62.0K 20171221 12 min 29 s
    the_raft_the_river_and_the_weird_ending_of_huckleberry_finn_  31.4M  24.0G   371K  61.9K 20160720 10 min 47 s
        equal_protection_crash_course_government_and_politics_29  22.4M  24.0G   431K  61.5K 20150829 8 min 15 s
           social_policy_crash_course_government_and_politics_49  20.0M  24.0G   368K  61.3K 20160227 8 min 53 s
                                  crash_course_chemistry_preview  5.02M  24.0G   550K  61.1K 20130204 1 min 50 s
                computer_vision_crash_course_computer_science_35  26.9M  24.1G   243K  60.7K 20171115 11 min 9 s
               lost_in_translation_crash_course_film_criticism_7  22.4M  24.1G   241K  60.3K 20180301 10 min 28 s
    nintendo_and_a_new_standard_for_video_games_crash_course_gam  23.7M  24.1G   360K  59.9K 20160520 9 min 1 s
        the_golden_age_of_hollywood_crash_course_film_history_11  25.0M  24.1G   297K  59.4K 20170630 9 min 55 s
    comparative_anatomy_what_makes_us_animals_crash_course_biolo  24.7M  24.2G   590K  59.0K 20120618 8 min 50 s
                       how_we_got_here_crash_course_sociology_12  25.5M  24.2G   294K  58.8K 20170605 11 min 0 s
      sex_discrimination_crash_course_government_and_politics_30  19.9M  24.2G   411K  58.8K 20150904 8 min 6 s
    ford_cars_and_a_new_revolution_crash_course_history_of_scien  29.1M  24.2G   176K  58.8K 20181112 11 min 57 s
                 the_economics_of_happiness_crash_course_econ_35  30.3M  24.3G   348K  58.0K 20160609 10 min 25 s
           the_impacts_of_social_class_crash_course_sociology_25  23.1M  24.3G   289K  57.8K 20170918 9 min 23 s
                        moonlight_crash_course_film_criticism_13  30.2M  24.3G   231K  57.7K 20180412 11 min 40 s
            the_parable_of_the_sower_crash_course_literature_406  27.5M  24.3G   231K  57.7K 20171220 11 min 58 s
                  the_harlem_renaissance_crash_course_theater_41  24.5M  24.4G   173K  57.5K 20181221 12 min 10 s
      genetics_lost_and_found_crash_course_history_of_science_25  27.7M  24.4G   173K  57.5K 20181022 12 min 1 s
    passing_gases_effusion_diffusion_and_the_velocity_of_a_gas_c  30.3M  24.4G   518K  57.5K 20130603 11 min 25 s
    why_we_can_t_invent_a_perfect_engine_crash_course_engineerin  31.0M  24.4G   230K  57.5K 20180719 12 min 54 s
                            aliens_crash_course_film_criticism_2  28.3M  24.5G   229K  57.3K 20180118 11 min 36 s
     alkene_addition_reactions_crash_course_organic_chemistry_16  44.3M  24.5G  57.0K  57.0K 20201111 12 min 52 s
                stereochemistry_crash_course_organic_chemistry_8  52.3M  24.6G   114K  56.8K 20200723 14 min 34 s
      graphical_user_interfaces_crash_course_computer_science_26  34.3M  24.6G   283K  56.6K 20170830 12 min 58 s
                             temperature_crash_course_physics_20  21.3M  24.6G   339K  56.5K 20160818 9 min 0 s
                capacitors_and_kirchhoff_crash_course_physics_31  26.8M  24.6G   282K  56.4K 20161118 10 min 37 s
    playstation_and_more_immersive_video_games_crash_course_game  32.0M  24.7G   338K  56.4K 20160604 11 min 51 s
                 the_inventor_who_vanished_crash_course_recess_1  9.74M  24.7G   225K  56.3K 20180305 3 min 50 s
    evaluating_evidence_crash_course_navigating_digital_informat  29.6M  24.7G   168K  56.1K 20190212 13 min 20 s
                syntax_1_morphosyntax_crash_course_linguistics_3  37.9M  24.8G   112K  55.9K 20200925 10 min 31 s
                     the_economics_of_death_crash_course_econ_30  27.4M  24.8G   334K  55.7K 20160416 12 min 32 s
               thermodynamics_crash_course_history_of_science_26  29.3M  24.8G   167K  55.5K 20181029 12 min 28 s
    history_of_media_literacy_part_1_crash_course_media_literacy  22.3M  24.8G   221K  55.3K 20180306 9 min 50 s
                the_language_of_film_crash_course_film_history_5  24.1M  24.9G   276K  55.3K 20170511 9 min 28 s
    to_the_moon_mars_aerospace_engineering_crash_course_engineer  21.8M  24.9G   166K  55.2K 20190131 10 min 0 s
    making_time_management_work_for_you_crash_course_business_so  22.0M  24.9G   166K  55.2K 20190515 10 min 59 s
    congressional_delegation_crash_course_government_and_politic  14.7M  24.9G   385K  55.0K 20150424 6 min 15 s
        social_class_poverty_in_the_us_crash_course_sociology_24  21.7M  24.9G   275K  54.9K 20170911 9 min 23 s
              beasts_of_no_nation_crash_course_film_criticism_14  32.1M  25.0G   218K  54.6K 20180419 12 min 28 s
     you_know_im_all_about_that_bayes_crash_course_statistics_24  26.9M  25.0G   218K  54.5K 20180725 12 min 4 s
                             crash_course_world_history_outtakes  11.2M  25.0G   545K  54.5K 20120509 4 min 46 s
      pitching_and_pre_production_crash_course_film_production_2  17.1M  25.0G   272K  54.4K 20170831 8 min 15 s
    the_first_zeroth_laws_of_thermodynamics_crash_course_enginee  25.9M  25.0G   217K  54.4K 20180712 10 min 4 s
                                    what_s_new_with_crash_course  6.83M  25.1G   109K  54.3K 20191107 2 min 53 s
            the_binomial_distribution_crash_course_statistics_15  27.8M  25.1G   217K  54.2K 20180509 14 min 14 s
                       acidity_crash_course_organic_chemistry_11  40.3M  25.1G   108K  54.1K 20200903 11 min 17 s
    interest_group_formation_crash_course_government_and_politic  24.7M  25.1G   325K  54.1K 20160108 8 min 56 s
      atari_and_the_business_of_video_games_crash_course_games_4  22.1M  25.2G   324K  54.0K 20160422 10 min 18 s
    marie_curie_and_spooky_rays_crash_course_history_of_science_  26.8M  25.2G   161K  53.5K 20181217 11 min 47 s
                                    crash_course_biology_preview  5.81M  25.2G   106K  53.2K 20200702 1 min 23 s
           sega_and_more_mature_video_games_crash_course_games_8  29.2M  25.2G   319K  53.2K 20160528 10 min 46 s
              the_normal_distribution_crash_course_statistics_19  26.2M  25.3G   213K  53.2K 20180606 11 min 26 s
    value_proposition_and_customer_segments_crash_course_busines  23.0M  25.3G   159K  52.9K 20190828 12 min 2 s
    to_film_school_or_not_to_film_school_crash_course_film_produ  17.8M  25.3G   211K  52.7K 20171207 9 min 31 s
         bertolt_brecht_and_epic_theater_crash_course_theater_44  25.4M  25.3G   158K  52.7K 20190118 11 min 50 s
    keyboards_command_line_interfaces_crash_course_computer_scie  28.4M  25.3G   262K  52.3K 20170802 11 min 23 s
           community_ecology_ii_predators_crash_course_ecology_5  32.7M  25.4G   465K  51.7K 20121204 10 min 22 s
                        alkanes_crash_course_organic_chemistry_6  45.7M  25.4G   103K  51.4K 20200624 11 min 50 s
          discrimination_crash_course_government_and_politics_31  25.5M  25.4G   357K  51.1K 20150919 8 min 39 s
    defense_against_the_dark_arts_of_influence_crash_course_busi  31.0M  25.5G   152K  50.6K 20190320 12 min 18 s
        100_years_of_solitude_part_2_crash_course_literature_307  31.0M  25.5G   303K  50.4K 20160818 12 min 17 s
    how_p_values_help_us_test_hypotheses_crash_course_statistics  26.4M  25.5G   202K  50.4K 20180627 11 min 52 s
       the_birth_of_the_feature_film_crash_course_film_history_6  26.2M  25.6G   252K  50.4K 20170518 10 min 9 s
               the_mind_brain_crash_course_history_of_science_30  29.9M  25.6G   151K  50.3K 20181203 12 min 46 s
    cinema_radio_and_television_crash_course_history_of_science_  28.4M  25.6G   151K  50.2K 20181126 12 min 6 s
    copyright_exceptions_and_fair_use_crash_course_intellectual_  28.0M  25.6G   348K  49.7K 20150507 11 min 38 s
    sampling_methods_and_bias_with_surveys_crash_course_statisti  28.6M  25.7G   198K  49.5K 20180328 11 min 45 s
                      the_silent_era_crash_course_film_history_9  20.6M  25.7G   247K  49.4K 20170608 9 min 15 s
       why_cosmic_evolution_matters_crash_course_big_history_201  30.2M  25.7G   246K  49.3K 20170524 10 min 59 s
                 stages_of_family_life_crash_course_sociology_38  29.0M  25.7G   195K  48.6K 20171218 10 min 52 s
              the_law_of_conservation_crash_course_engineering_7  24.4M  25.8G   194K  48.6K 20180628 10 min 5 s
                do_the_right_thing_crash_course_film_criticism_6  32.8M  25.8G   194K  48.5K 20180222 11 min 26 s
                 foreign_aid_and_remittance_crash_course_econ_34  29.5M  25.8G   291K  48.5K 20160527 11 min 56 s
          microsoft_and_connected_consoles_crash_course_games_10  24.0M  25.9G   290K  48.3K 20160610 8 min 56 s
                                   mmorpgs_crash_course_games_12  22.9M  25.9G   290K  48.3K 20160624 8 min 53 s
    how_to_make_a_resume_stand_out_crash_course_business_soft_sk  26.4M  25.9G   145K  48.3K 20190410 11 min 23 s
                              politics_crash_course_sociology_30  26.4M  25.9G   193K  48.2K 20171023 10 min 12 s
                     optical_instruments_crash_course_physics_41  22.5M  26.0G   240K  47.9K 20170216 10 min 35 s
    the_secret_to_business_writing_crash_course_business_soft_sk  26.9M  26.0G   143K  47.7K 20190327 11 min 43 s
    beckett_ionesco_and_the_theater_of_the_absurd_crash_course_t  23.9M  26.0G   143K  47.6K 20190125 11 min 56 s
                                    crash_course_economics_intro  4.67M  26.0G   333K  47.6K 20150701 1 min 34 s
    government_regulation_crash_course_government_and_politics_4  27.4M  26.0G   285K  47.6K 20160206 9 min 48 s
              influence_persuasion_crash_course_media_literacy_6  23.2M  26.1G   190K  47.6K 20180403 9 min 50 s
            screens_2d_graphics_crash_course_computer_science_23  30.7M  26.1G   237K  47.5K 20170809 11 min 31 s
        media_regulation_crash_course_government_and_politics_45  23.5M  26.1G   283K  47.1K 20160123 9 min 15 s
                    the_first_home_consoles_crash_course_games_5  17.4M  26.1G   282K  47.1K 20160506 7 min 22 s
              the_cinematographer_crash_course_film_production_8  17.9M  26.1G   188K  47.1K 20171019 8 min 46 s
                     the_director_crash_course_film_production_7  16.8M  26.2G   188K  47.0K 20171012 8 min 43 s
                                sula_crash_course_literature_309  29.4M  26.2G   282K  46.9K 20160908 12 min 21 s
                           exercise_crash_course_study_skills_10  27.2M  26.2G   187K  46.7K 20171010 10 min 25 s
    polarity_resonance_and_electron_pushing_crash_course_organic  41.2M  26.3G  93.0K  46.5K 20200819 11 min 45 s
    shakespeare_s_tragedies_and_an_acting_lesson_crash_course_th  31.3M  26.3G   185K  46.3K 20180525 12 min 3 s
    air_travel_and_the_space_race_crash_course_history_of_scienc  29.2M  26.3G   139K  46.3K 20190218 12 min 21 s
                             age_aging_crash_course_sociology_36  24.6M  26.3G   184K  46.1K 20171204 10 min 18 s
                  crash_course_business_entrepreneurship_preview  4.70M  26.3G   138K  46.0K 20190807 2 min 14 s
    conservation_and_restoration_ecology_crash_course_ecology_12  29.5M  26.4G   414K  46.0K 20130121 10 min 12 s
    why_is_there_social_stratification_crash_course_sociology_22  31.0M  26.4G   230K  46.0K 20170814 10 min 23 s
    the_mighty_power_of_nanomaterials_crash_course_engineering_2  25.4M  26.4G   138K  46.0K 20181101 8 min 50 s
    e_z_alkenes_electrophilic_addition_carbocations_crash_course  48.1M  26.5G  46.0K  46.0K 20201014 14 min 1 s
     greek_comedy_satyrs_and_aristophanes_crash_course_theater_4  28.5M  26.5G   184K  45.9K 20180302 11 min 33 s
    the_english_renaissance_and_not_shakespeare_crash_course_the  32.2M  26.5G   184K  45.9K 20180511 12 min 51 s
    henrietta_lacks_the_tuskegee_experiment_and_ethical_data_col  25.9M  26.6G   183K  45.8K 20180418 11 min 24 s
        how_engineering_robots_works_crash_course_engineering_33  23.1M  26.6G   138K  45.8K 20190124 11 min 1 s
                               crash_course_literature_3_preview  6.42M  26.6G   275K  45.8K 20160630 2 min 24 s
    plots_outliers_and_justin_timberlake_data_visualization_part  24.1M  26.6G   183K  45.8K 20180228 11 min 35 s
                online_advertising_crash_course_media_literacy_7  23.3M  26.6G   183K  45.7K 20180410 10 min 31 s
      the_computer_and_turing_crash_course_history_of_science_36  28.0M  26.7G   137K  45.6K 20190211 11 min 53 s
     social_media_crash_course_navigating_digital_information_10  46.8M  26.7G   136K  45.3K 20190312 16 min 50 s
                             casual_gaming_crash_course_games_11  23.9M  26.7G   270K  45.1K 20160617 9 min 37 s
                         robots_crash_course_computer_science_37  32.0M  26.8G   180K  45.0K 20171129 12 min 25 s
    legal_basics_and_business_entity_formation_crash_course_busi  26.6M  26.8G   134K  44.8K 20190911 14 min 55 s
                                          changes_to_our_patreon  7.55M  26.8G   179K  44.7K 20171016 2 min 42 s
                   cyclohexanes_crash_course_organic_chemistry_7  49.7M  26.8G  89.1K  44.5K 20200708 14 min 8 s
              the_new_anatomy_crash_course_history_of_science_15  27.1M  26.9G   178K  44.5K 20180723 12 min 15 s
                       syntax_2_trees_crash_course_linguistics_4  36.9M  26.9G  89.0K  44.5K 20201002 10 min 41 s
     theories_of_global_stratification_crash_course_sociology_28  28.7M  26.9G   177K  44.2K 20171009 11 min 47 s
           how_to_sell_anything_crash_course_entrepreneurship_12  22.8M  27.0G  88.2K  44.1K 20191106 11 min 3 s
             how_power_gets_to_your_home_crash_course_physics_35  24.4M  27.0G   220K  44.0K 20161222 8 min 32 s
                                  crash_course_astronomy_preview  6.75M  27.0G  87.4K  43.7K 20200708 1 min 38 s
           how_to_become_an_engineer_crash_course_engineering_45  20.6M  27.0G   131K  43.6K 20190425 9 min 10 s
                        role_playing_games_crash_course_games_18  31.0M  27.0G   262K  43.6K 20160819 10 min 9 s
                 independent_cinema_crash_course_film_history_12  23.6M  27.1G   217K  43.5K 20170706 10 min 29 s
    the_engineering_challenges_of_renewable_energy_crash_course_  23.0M  27.1G   130K  43.5K 20190103 11 min 31 s
                       social_mobility_crash_course_sociology_26  21.8M  27.1G   217K  43.4K 20170925 9 min 1 s
                                      crash_course_games_preview  5.48M  27.1G   258K  43.0K 20160325 1 min 56 s
            the_new_chemistry_crash_course_history_of_science_18  32.8M  27.1G   172K  43.0K 20180820 13 min 14 s
                  biomedicine_crash_course_history_of_science_34  27.9M  27.2G   129K  43.0K 20190121 12 min 36 s
    pee_jokes_the_italian_renaissance_commedia_dell_arte_crash_c  27.4M  27.2G   172K  42.9K 20180504 11 min 17 s
               breaking_the_silence_crash_course_film_history_10  23.2M  27.2G   214K  42.8K 20170615 9 min 35 s
       how_to_avoid_burnout_crash_course_business_soft_skills_17  26.5M  27.2G   127K  42.5K 20190703 10 min 39 s
    how_to_speak_with_confidence_crash_course_business_soft_skil  28.2M  27.3G   126K  42.2K 20190404 11 min 11 s
             nfsl_lmsyhy_n_lyhwdy_lhlq_11_mn_crash_course_bl_rby  35.2M  27.3G   168K  42.0K 20180329 13 min 53 s
                  engineering_ethics_crash_course_engineering_27  19.6M  27.3G   126K  42.0K 20181206 9 min 50 s
                                 engines_crash_course_physics_24  23.0M  27.3G   251K  41.9K 20160922 10 min 20 s
         why_human_ancestry_matters_crash_course_big_history_205  25.6M  27.4G   208K  41.5K 20170627 10 min 26 s
                controlled_experiments_crash_course_statistics_9  32.2M  27.4G   165K  41.3K 20180321 12 min 26 s
                    media_the_mind_crash_course_media_literacy_4  19.0M  27.4G   165K  41.3K 20180320 9 min 13 s
    patents_novelty_and_trolls_crash_course_intellectual_propert  25.6M  27.4G   286K  40.9K 20150514 9 min 50 s
    the_biggest_problems_we_re_facing_today_the_future_of_engine  26.8M  27.5G   123K  40.9K 20190502 10 min 24 s
                    the_pokemon_phenomenon_crash_course_games_28  28.4M  27.5G   204K  40.7K 20161207 10 min 50 s
    the_personal_computer_revolution_crash_course_computer_scien  28.3M  27.5G   204K  40.7K 20170823 10 min 14 s
                               game_design_crash_course_games_19  26.5M  27.6G   244K  40.6K 20160902 9 min 57 s
    the_cold_war_and_consumerism_crash_course_computer_science_2  30.2M  27.6G   202K  40.4K 20170816 11 min 18 s
    the_structure_cost_of_us_health_care_crash_course_sociology_  26.1M  27.6G   161K  40.2K 20180212 9 min 49 s
    probability_part_2_updating_your_beliefs_with_bayes_crash_co  26.3M  27.6G   160K  40.1K 20180502 12 min 5 s
     economic_systems_the_labor_market_crash_course_sociology_29  23.0M  27.7G   160K  40.1K 20171016 10 min 18 s
    radical_reactions_hammond_s_postulate_crash_course_organic_c  43.3M  27.7G  39.9K  39.9K 20210106 12 min 0 s
    intro_to_reaction_mechanisms_crash_course_organic_chemistry_  41.9M  27.7G  79.7K  39.8K 20200930 12 min 42 s
        psychology_of_computing_crash_course_computer_science_38  33.1M  27.8G   158K  39.6K 20171206 12 min 38 s
    expenses_costs_how_to_spend_money_wisely_crash_course_entrep  22.9M  27.8G  78.8K  39.4K 20191120 10 min 53 s
    financing_options_for_small_businesses_crash_course_entrepre  26.3M  27.8G  78.7K  39.4K 20191204 10 min 55 s
                       health_medicine_crash_course_sociology_42  26.1M  27.8G   157K  39.2K 20180129 11 min 14 s
    silicon_the_internet_s_favorite_element_crash_course_chemist  21.5M  27.9G   314K  39.2K 20131021 9 min 26 s
                  formal_organizations_crash_course_sociology_17  25.4M  27.9G   196K  39.1K 20170710 10 min 7 s
    preventing_flint_environmental_engineering_crash_course_engi  23.9M  27.9G   117K  39.1K 20181220 10 min 13 s
                   media_ownership_crash_course_media_literacy_8  27.5M  27.9G   155K  38.8K 20180417 11 min 59 s
    history_of_media_literacy_part_2_crash_course_media_literacy  20.6M  28.0G   155K  38.7K 20180313 9 min 54 s
        the_dark_er_side_of_media_crash_course_media_literacy_10  22.9M  28.0G   154K  38.6K 20180501 10 min 34 s
             the_filmmaker_s_army_crash_course_film_production_3  20.6M  28.0G   192K  38.4K 20170907 9 min 56 s
           dada_surrealism_and_symbolism_crash_course_theater_37  27.1M  28.0G   115K  38.2K 20181123 12 min 25 s
                    intro_to_big_data_crash_course_statistics_38  29.6M  28.1G   115K  38.2K 20181114 11 min 22 s
                revenue_streams_crash_course_entrepreneurship_13  24.9M  28.1G  76.4K  38.2K 20191113 10 min 47 s
                    hdr_bld_lrfdyn_lhlq_3_mn_crash_course_bl_rby  33.2M  28.1G   152K  38.0K 20180201 12 min 40 s
                world_cinema_part_1_crash_course_film_history_14  26.8M  28.1G   190K  37.9K 20170720 10 min 15 s
    dances_to_flute_music_and_obscene_verse_it_s_roman_theater_e  31.6M  28.2G   151K  37.8K 20180309 12 min 25 s
                      training_neural_networks_crash_course_ai_4  28.8M  28.2G   113K  37.8K 20190830 12 min 28 s
                      ecology_crash_course_history_of_science_38  34.0M  28.2G   113K  37.8K 20190225 12 min 22 s
        why_human_evolution_matters_crash_course_big_history_204  29.4M  28.3G   187K  37.5K 20170621 11 min 29 s
       social_stratification_in_the_us_crash_course_sociology_23  19.5M  28.3G   187K  37.4K 20170821 9 min 33 s
    alkyne_reactions_tautomerization_crash_course_organic_chemis  40.3M  28.3G  37.4K  37.4K 20201216 11 min 55 s
        reversibility_irreversibility_crash_course_engineering_8  22.4M  28.3G   149K  37.3K 20180705 11 min 4 s
                                            crash_course_preview  1.24M  28.3G   372K  37.2K 20111202 38 s 811 ms
                    spectra_interference_crash_course_physics_40  17.0M  28.4G   186K  37.1K 20170202 8 min 24 s
    evaluating_photos_videos_crash_course_navigating_digital_inf  33.8M  28.4G   111K  37.1K 20190219 13 min 18 s
                      psychology_of_gaming_crash_course_games_16  21.5M  28.4G   222K  37.0K 20160730 8 min 46 s
    roman_theater_with_plautus_terence_and_seneca_crash_course_t  29.2M  28.4G   148K  36.9K 20180316 11 min 57 s
                         home_video_crash_course_film_history_13  23.0M  28.5G   183K  36.6K 20170713 10 min 18 s
                               crash_course_literature_2_preview  4.16M  28.5G   292K  36.5K 20140213 1 min 42 s
    more_stereochemical_relationships_crash_course_organic_chemi  47.9M  28.5G  72.9K  36.5K 20200805 12 min 47 s
                japan_kabuki_and_bunraku_crash_course_theater_23  34.5M  28.5G   145K  36.2K 20180727 12 min 38 s
                                card_games_crash_course_games_13  23.9M  28.6G   217K  36.2K 20160709 9 min 0 s
           television_production_crash_course_film_production_15  20.2M  28.6G   144K  36.0K 20171214 10 min 21 s
    why_it_s_so_hard_to_make_better_batteries_crash_course_engin  20.1M  28.6G   108K  36.0K 20190117 10 min 26 s
             stress_strain_quicksand_crash_course_engineering_12  20.7M  28.6G   144K  36.0K 20180809 9 min 9 s
    how_to_make_an_ai_read_your_handwriting_lab_crash_course_ai_  39.2M  28.7G   108K  36.0K 20190906 17 min 16 s
    how_to_set_and_achieve_smart_goals_crash_course_business_sof  31.2M  28.7G   108K  35.9K 20190508 10 min 52 s
    silicon_semiconductors_solar_cells_crash_course_engineering_  24.9M  28.7G   108K  35.9K 20181025 10 min 38 s
                        producers_crash_course_film_production_6  18.2M  28.7G   179K  35.8K 20171005 8 min 41 s
        just_say_noh_but_also_say_kyogen_crash_course_theater_11  31.8M  28.8G   143K  35.7K 20180427 12 min 54 s
                                     robotics_crash_course_ai_11  30.0M  28.8G  71.4K  35.7K 20191025 10 min 11 s
                  broadway_book_musicals_crash_course_theater_50  32.4M  28.8G   107K  35.6K 20190301 13 min 4 s
         global_stratification_poverty_crash_course_sociology_27  22.8M  28.9G   178K  35.6K 20171002 10 min 19 s
                three_colors_blue_crash_course_film_criticism_11  25.0M  28.9G   142K  35.6K 20180329 11 min 1 s
    click_restraint_crash_course_navigating_digital_information_  32.2M  28.9G   107K  35.6K 20190305 12 min 46 s
    heat_engines_refrigerators_cycles_crash_course_engineering_1  23.4M  28.9G   142K  35.5K 20180802 10 min 43 s
                             selma_crash_course_film_criticism_3  28.0M  29.0G   142K  35.5K 20180125 12 min 55 s
    why_early_globalization_matters_crash_course_big_history_206  35.6M  29.0G   177K  35.5K 20170712 12 min 16 s
                     crash_course_world_history_outtakes_part_ii  9.53M  29.0G   318K  35.3K 20121122 4 min 13 s
    computer_engineering_the_end_of_moore_s_law_crash_course_eng  26.6M  29.0G   106K  35.3K 20190207 11 min 34 s
    nostrils_harmony_with_the_universe_and_ancient_sanskrit_thea  31.6M  29.1G   141K  35.2K 20180323 12 min 37 s
                algorithmic_bias_and_fairness_crash_course_ai_18  28.2M  29.1G  70.2K  35.1K 20191213 11 min 19 s
    what_can_you_learn_from_your_competition_crash_course_busine  24.6M  29.1G   105K  35.0K 20190904 12 min 34 s
             network_solids_and_carbon_crash_course_chemistry_34  19.9M  29.1G   277K  34.6K 20131014 8 min 18 s
    data_infographics_crash_course_navigating_digital_informatio  29.4M  29.2G   104K  34.6K 20190226 13 min 1 s
    experimental_and_documentary_films_crash_course_film_history  26.6M  29.2G   172K  34.4K 20170803 10 min 20 s
                                 pc_gaming_crash_course_games_20  27.0M  29.2G   205K  34.2K 20160909 10 min 17 s
                             crash_course_film_criticism_preview  6.20M  29.2G   135K  33.8K 20180104 2 min 27 s
    how_to_build_customer_relationships_crash_course_entrepreneu  23.9M  29.2G  67.5K  33.7K 20191016 10 min 43 s
         educational_technology_crash_course_computer_science_39  30.1M  29.3G   135K  33.7K 20171213 11 min 51 s
                     metals_ceramics_crash_course_engineering_19  20.3M  29.3G   135K  33.7K 20180927 10 min 2 s
        is_growth_right_for_you_crash_course_entrepreneurship_17  24.3M  29.3G  67.3K  33.7K 20191211 11 min 3 s
                      test_statistics_crash_course_statistics_26  27.0M  29.3G   134K  33.6K 20180808 12 min 49 s
                         educational_games_crash_course_games_15  20.9M  29.4G   202K  33.6K 20160723 8 min 15 s
    t_tests_a_matched_pair_made_in_heaven_crash_course_statistic  23.9M  29.4G   133K  33.2K 20180815 11 min 16 s
    genetics_and_the_modern_synthesis_crash_course_history_of_sc  29.9M  29.4G  99.2K  33.1K 20190204 12 min 33 s
        alkene_redox_reactions_crash_course_organic_chemistry_17  39.9M  29.5G  33.0K  33.0K 20201203 11 min 8 s
                               board_games_crash_course_games_14  22.2M  29.5G   198K  33.0K 20160716 8 min 24 s
    nucleophiles_and_electrophiles_crash_course_organic_chemistr  43.3M  29.5G  65.8K  32.9K 20200916 12 min 7 s
    why_the_evolutionary_epic_matters_crash_course_big_history_2  32.8M  29.6G   163K  32.6K 20170606 12 min 21 s
                       media_money_crash_course_media_literacy_5  24.2M  29.6G   130K  32.6K 20180327 10 min 15 s
    how_to_seek_help_and_find_key_partners_crash_course_entrepre  22.2M  29.6G  64.9K  32.4K 20191009 11 min 14 s
                 sound_production_crash_course_film_production_5  22.7M  29.6G   162K  32.3K 20170928 10 min 5 s
              climate_science_crash_course_history_of_science_45  29.5M  29.6G  96.5K  32.2K 20190422 11 min 33 s
                           crash_course_world_history_outtakes_3  9.27M  29.7G   289K  32.1K 20121227 4 min 31 s
                                          world_history_outtakes  11.3M  29.7G   224K  32.0K 20141226 4 min 22 s
    antonin_artaud_and_the_theater_of_cruelty_crash_course_theat  24.9M  29.7G  95.7K  31.9K 20190113 11 min 26 s
    comedies_romances_and_shakespeare_s_heroines_crash_course_th  25.2M  29.7G   128K  31.9K 20180601 11 min 21 s
           bodies_and_dollars_crash_course_history_of_science_41  34.8M  29.8G  95.6K  31.9K 20190325 12 min 56 s
    controlling_the_environment_crash_course_history_of_science_  33.9M  29.8G  94.9K  31.6K 20190304 13 min 27 s
           life_and_longevity_crash_course_history_of_science_44  30.9M  29.8G  94.8K  31.6K 20190415 12 min 50 s
                      the_editor_crash_course_film_production_12  23.4M  29.8G   126K  31.5K 20171116 11 min 6 s
    cats_vs_dogs_let_s_make_an_ai_to_settle_this_crash_course_ai  28.6M  29.9G  62.9K  31.5K 20191220 13 min 4 s
      designing_the_world_of_film_crash_course_film_production_9  18.8M  29.9G   125K  31.3K 20171026 8 min 45 s
                    crashcourse_biology_outtakes_with_hank_green  16.5M  29.9G   312K  31.2K 20120519 5 min 38 s
            dissecting_the_camera_crash_course_film_production_4  19.8M  29.9G   155K  31.0K 20170921 9 min 5 s
    the_internet_and_computing_crash_course_history_of_science_4  31.2M  30.0G  92.7K  30.9K 20190408 12 min 27 s
                        reinforcement_learning_crash_course_ai_9  24.3M  30.0G  61.8K  30.9K 20191011 11 min 27 s
    how_to_find_your_leadership_style_crash_course_business_soft  29.0M  30.0G  92.4K  30.8K 20190613 10 min 10 s
      the_century_of_the_gene_crash_course_history_of_science_42  32.3M  30.0G  92.3K  30.8K 20190401 13 min 24 s
          the_future_of_clean_energy_crash_course_engineering_31  23.2M  30.1G  92.0K  30.7K 20190110 11 min 17 s
                         unsupervised_learning_crash_course_ai_6  29.6M  30.1G  92.0K  30.7K 20190920 12 min 34 s
    trademarks_and_avoiding_consumer_confusion_crash_course_inte  27.4M  30.1G   214K  30.5K 20150527 11 min 19 s
      how_youtube_knows_what_you_should_watch_crash_course_ai_15  25.1M  30.1G  61.0K  30.5K 20191122 10 min 51 s
    the_olympics_fifa_and_why_we_love_sports_crash_course_games_  34.1M  30.2G   183K  30.5K 20160805 12 min 1 s
    the_death_and_resurrection_of_theater_as_liturgical_drama_cr  31.5M  30.2G   122K  30.5K 20180406 12 min 32 s
     get_outside_and_have_a_mystery_play_crash_course_theater_10  33.1M  30.2G   120K  30.1K 20180420 11 min 44 s
                                  symbolic_ai_crash_course_ai_10  29.6M  30.3G  59.7K  29.8K 20191018 13 min 21 s
             why_star_stuff_matters_crash_course_big_history_202  28.3M  30.3G   149K  29.7K 20170531 11 min 3 s
       fjr_lslm_wthdyt_bn_mbrtwry_lhlq_13_mn_crash_course_bl_rby  37.1M  30.3G   118K  29.5K 20180412 15 min 26 s
      chekhov_and_the_moscow_art_theater_crash_course_theater_34  27.7M  30.4G  88.3K  29.4K 20181019 12 min 25 s
    how_to_make_tough_decisions_crash_course_business_soft_skill  24.6M  30.4G  88.1K  29.4K 20190522 11 min 27 s
                     media_skills_crash_course_media_literacy_11  24.8M  30.4G   117K  29.4K 20180508 11 min 2 s
    minimum_viable_product_and_pivoting_crash_course_business_en  21.6M  30.4G  87.8K  29.3K 20190918 11 min 14 s
    symbolism_realism_and_a_nordic_playwright_grudge_match_crash  25.8M  30.4G  87.2K  29.1K 20181012 13 min 8 s
    let_s_make_an_ai_that_destroys_video_games_crash_course_ai_1  27.2M  30.5G  58.0K  29.0K 20191108 13 min 25 s
    how_to_become_a_better_negotiator_crash_course_business_soft  31.2M  30.5G  87.0K  29.0K 20190501 11 min 32 s
                                   web_search_crash_course_ai_17  24.7M  30.5G  57.6K  28.8K 20191206 11 min 14 s
                 special_effects_crash_course_film_production_11  22.6M  30.6G   115K  28.7K 20171109 10 min 0 s
             futurism_and_constructivism_crash_course_theater_39  31.3M  30.6G  86.0K  28.7K 20181207 13 min 51 s
                     hdr_msr_lqdym_lhlq_4_mn_crash_course_bl_rby  33.7M  30.6G   113K  28.3K 20180208 12 min 45 s
    moliere_man_of_satire_and_many_burials_crash_course_theater_  30.8M  30.6G   113K  28.2K 20180713 11 min 45 s
                       marketing_crash_course_film_production_13  21.1M  30.7G   113K  28.2K 20171130 9 min 54 s
                     population_health_crash_course_sociology_43  21.7M  30.7G   112K  28.0K 20180205 9 min 55 s
        the_limits_of_history_crash_course_history_of_science_46  30.5M  30.7G  82.7K  27.6K 20190429 10 min 51 s
    how_to_ace_the_interview_crash_course_business_soft_skills_6  32.7M  30.7G  82.3K  27.4K 20190417 11 min 30 s
                   the_rise_of_melodrama_crash_course_theater_28  30.6M  30.8G   109K  27.4K 20180907 12 min 6 s
                             ai_playing_games_crash_course_ai_12  27.7M  30.8G  54.7K  27.4K 20191101 11 min 30 s
                                 handhelds_crash_course_games_23  27.8M  30.8G   137K  27.4K 20161008 11 min 7 s
                      the_future_of_gaming_crash_course_games_29  26.7M  30.9G   136K  27.3K 20161216 9 min 32 s
                          open_world_games_crash_course_games_22  34.3M  30.9G   164K  27.3K 20161001 11 min 59 s
     how_to_handle_conflict_crash_course_business_soft_skills_13  26.0M  30.9G  81.7K  27.2K 20190605 11 min 36 s
    how_the_leaning_tower_of_pisa_was_saved_crash_course_enginee  24.3M  30.9G  81.0K  27.0K 20190314 9 min 53 s
    lhmlt_lslyby_sr_lmy_mq_mm_ntkhyl_lhlq_15_mn_crash_course_bl_  37.8M  31.0G   107K  26.7K 20180426 13 min 39 s
                      hdr_wdy_lsnd_lhlq_2_mn_crash_course_bl_rby  24.5M  31.0G   106K  26.6K 20180125 10 min 29 s
                   science_journalism_crash_course_statistics_11  28.1M  31.0G   106K  26.5K 20180411 10 min 41 s
                                crash_course_literature_outtakes  11.0M  31.0G   212K  26.5K 20140619 4 min 19 s
             where_are_my_children_crash_course_film_criticism_4  24.6M  31.1G   106K  26.5K 20180208 9 min 43 s
                              crash_course_us_history_outtakes_2  9.81M  31.1G   238K  26.5K 20130801 4 min 46 s
      zola_france_realism_and_naturalism_crash_course_theater_31  28.2M  31.1G   105K  26.3K 20180928 12 min 36 s
                                      larp_crash_course_games_26  23.6M  31.1G   132K  26.3K 20161111 9 min 13 s
    mass_producing_ice_cream_with_food_engineering_crash_course_  24.1M  31.1G  77.9K  26.0K 20190307 9 min 20 s
                           randomness_crash_course_statistics_17  28.1M  31.2G   104K  25.9K 20180523 12 min 6 s
    geometric_distributions_and_the_birthday_paradox_crash_cours  23.0M  31.2G   103K  25.7K 20180516 10 min 18 s
                   natural_language_processing_crash_course_ai_7  33.1M  31.2G  77.2K  25.7K 20190927 13 min 28 s
                world_cinema_part_2_crash_course_film_history_15  24.9M  31.3G   128K  25.6K 20170727 9 min 53 s
                   expressionist_theater_crash_course_theater_38  25.3M  31.3G  76.7K  25.6K 20181130 12 min 14 s
                            crash_course_film_production_preview  4.49M  31.3G   128K  25.5K 20170817 1 min 49 s
                                           us_history_outtakes_4  9.71M  31.3G   203K  25.4K 20131227 4 min 11 s
    degrees_of_freedom_and_effect_sizes_crash_course_statistics_  29.6M  31.3G   100K  25.0K 20180822 13 min 29 s
             the_future_of_virtual_reality_crash_course_games_21  24.2M  31.3G   150K  25.0K 20160923 9 min 14 s
      lets_make_a_movie_recommendation_system_crash_course_ai_16  30.9M  31.4G  49.9K  24.9K 20191129 14 min 40 s
      l_swr_lwst_hl_knt_mzlm_hqan_lhlq_14_mn_crash_course_bl_rby  36.0M  31.4G  98.6K  24.7K 20180419 13 min 52 s
    how_to_communicate_with_customers_crash_course_entrepreneurs  22.3M  31.4G  49.3K  24.6K 20191030 10 min 28 s
    the_many_forms_of_power_crash_course_business_soft_skills_16  22.6M  31.5G  73.3K  24.4K 20190626 11 min 33 s
               humans_and_ai_working_together_crash_course_ai_14  24.7M  31.5G  48.9K  24.4K 20191115 10 min 12 s
                                           big_history_2_preview  5.72M  31.5G  48.8K  24.4K 20200724 1 min 25 s
                                  gambling_crash_course_games_27  33.0M  31.5G   122K  24.4K 20161119 11 min 44 s
                        biomaterials_crash_course_engineering_24  23.0M  31.5G  72.6K  24.2K 20181108 11 min 9 s
    prepare_to_negotiate_your_salary_or_anything_crash_course_bu  28.6M  31.6G  72.5K  24.2K 20190424 11 min 10 s
                              crash_course_us_history_outtakes_5  8.24M  31.6G   193K  24.2K 20140221 3 min 46 s
          lmgwl_byn_ltsmh_wlwhshy_lhlq_17_mn_crash_course_bl_rby  35.4M  31.6G  96.4K  24.1K 20180510 13 min 35 s
               grip_and_electric_crash_course_film_production_10  17.8M  31.6G  95.2K  23.8K 20171102 8 min 38 s
       international_ip_law_crash_course_intellectual_property_6  24.3M  31.7G   166K  23.7K 20150603 9 min 59 s
                     crash_course_literature_season_four_preview  5.79M  31.7G  94.9K  23.7K 20171031 2 min 16 s
                                           big_history_1_preview  5.94M  31.7G  47.1K  23.6K 20200724 1 min 25 s
    youtube_couldn_t_exist_without_communications_signal_process  23.9M  31.7G  70.6K  23.5K 20190404 9 min 29 s
    ip_problems_youtube_and_the_future_crash_course_intellectual  32.2M  31.7G   165K  23.5K 20150625 13 min 29 s
    building_a_desalination_plant_from_scratch_crash_course_engi  21.6M  31.7G  70.3K  23.4K 20190418 9 min 41 s
    electrical_power_conductors_your_dream_home_crash_course_eng  28.2M  31.8G  69.4K  23.1K 20181018 10 min 46 s
                poor_unfortunate_theater_crash_course_theater_48  26.3M  31.8G  68.9K  23.0K 20190215 13 min 6 s
                  the_spanish_golden_age_crash_course_theater_19  27.9M  31.8G  91.0K  22.7K 20180629 11 min 15 s
                crash_course_intellectual_property_and_economics  4.06M  31.8G   159K  22.7K 20150218 1 min 55 s
                     p_value_problems_crash_course_statistics_22  28.4M  31.9G  90.6K  22.6K 20180711 12 min 13 s
                 the_history_of_game_shows_crash_course_games_25  35.8M  31.9G   113K  22.6K 20161028 13 min 22 s
    rules_rule_breaking_and_french_neoclassicism_crash_course_th  33.2M  31.9G  90.0K  22.5K 20180706 13 min 14 s
    why_moving_people_is_complicated_crash_course_engineering_41  28.3M  31.9G  66.8K  22.3K 20190328 10 min 15 s
                             input_devices_crash_course_games_24  25.5M  32.0G   111K  22.2K 20161022 10 min 29 s
    lthwr_lsn_y_wlmdh_bdt_fy_wrwb_lhlq_32_mn_crash_course_bl_rby  36.1M  32.0G  88.5K  22.1K 20180927 14 min 4 s
                      neural_networks_crash_course_statistics_41  30.0M  32.0G  66.2K  22.1K 20181212 12 min 15 s
                    big_data_problems_crash_course_statistics_39  29.5M  32.1G  65.7K  21.9K 20181121 12 min 50 s
               the_polymer_explosion_crash_course_engineering_20  23.6M  32.1G  87.6K  21.9K 20181004 9 min 23 s
           trykh_rwsy_m_qbl_lqysr_lhlq_20_mn_crash_course_bl_rby  34.8M  32.1G  87.0K  21.8K 20180531 13 min 11 s
                      broadway_seriously_crash_course_theater_46  22.6M  32.1G  65.1K  21.7K 20190201 11 min 14 s
          lthwr_lmryky_thwr_hqyqy_lhlq_28_mn_crash_course_bl_rby  37.1M  32.2G  86.3K  21.6K 20180726 13 min 47 s
    synge_wilde_shaw_and_the_irish_renaissance_crash_course_thea  27.4M  32.2G  64.7K  21.6K 20181109 11 min 52 s
    the_core_of_a_business_key_activities_resources_crash_course  22.5M  32.2G  64.4K  21.5K 20191002 10 min 1 s
    how_to_avoid_teamwork_disasters_crash_course_business_soft_s  23.2M  32.3G  63.8K  21.3K 20190529 10 min 35 s
            china_zaju_and_beijing_opera_crash_course_theater_25  29.1M  32.3G  85.0K  21.3K 20180810 11 min 43 s
       mns_mws_wlslm_wst_mr_fryqy_lhlq_16_mn_crash_course_bl_rby  34.4M  32.3G  84.9K  21.2K 20180503 12 min 25 s
                                            hot_dog_contest_2014  13.7M  32.3G   168K  21.0K 20140704 6 min 5 s
      kyf_khrjt_lbwdhy_mn_rhm_lhndwsy_lhlq_6_crash_course_bl_rby  32.5M  32.4G  84.0K  21.0K 20180222 12 min 44 s
    lthwr_lfrnsy_thwr_qym_m_thwr_jy_lhlq_29_mn_crash_course_bl_r  40.8M  32.4G  84.0K  21.0K 20180906 14 min 44 s
                              outtakes_3_crash_course_psychology  12.6M  32.4G   167K  20.9K 20140915 5 min 1 s
                fluid_flow_equipment_crash_course_engineering_13  19.2M  32.4G  83.7K  20.9K 20180816 9 min 25 s
                    where_did_theater_go_crash_course_theater_18  33.9M  32.5G  82.7K  20.7K 20180615 13 min 25 s
                  the_philosopher_s_corpse_crash_course_recess_2  9.70M  32.5G  81.8K  20.5K 20181002 3 min 18 s
                  media_policy_you_crash_course_media_literacy_9  23.2M  32.5G  79.8K  20.0K 20180424 11 min 33 s
    how_to_engineer_health_drug_discovery_delivery_crash_course_  25.5M  32.5G  59.6K  19.9K 20190214 10 min 11 s
       english_theater_after_shakespeare_crash_course_theater_17  32.8M  32.6G  79.3K  19.8K 20180608 12 min 58 s
                                                        ilovepbs  9.62M  32.6G  98.9K  19.8K 20170411 3 min 34 s
                                  war_crash_course_statistics_42  25.9M  32.6G  58.9K  19.6K 20181219 11 min 11 s
    reaching_breaking_point_materials_stresses_toughness_crash_c  25.7M  32.6G  78.5K  19.6K 20180920 11 min 23 s
                            p_hacking_crash_course_statistics_30  24.5M  32.6G  78.4K  19.6K 20180905 11 min 1 s
    hrotsvitha_hildegard_and_the_nun_who_resurrected_theater_cra  30.0M  32.7G  78.2K  19.5K 20180413 12 min 11 s
                    l_wlm_ljz_lwl_lhlq_41_mn_crash_course_bl_rby  34.5M  32.7G  58.1K  19.4K 20181129 13 min 40 s
                 crash_course_world_history_season_2_outtakes_v2  16.7M  32.7G   135K  19.3K 20150325 6 min 45 s
          make_an_ai_sound_like_a_youtuber_lab_crash_course_ai_8  34.3M  32.7G  57.8K  19.3K 20191004 15 min 59 s
            into_africa_and_wole_soyinka_crash_course_theater_49  25.5M  32.8G  57.8K  19.3K 20190222 12 min 32 s
                              outtakes_1_crash_course_philosophy  14.7M  32.8G   115K  19.2K 20160418 6 min 34 s
    flirting_with_disaster_the_importance_of_safety_crash_course  23.2M  32.8G  57.4K  19.1K 20181213 11 min 12 s
                              outtakes_4_crash_course_psychology  11.8M  32.8G   134K  19.1K 20141201 4 min 29 s
    trykh_lsyn_wrtbth_blkwnfwshywsy_lhlq_7_mn_crash_course_bl_rb  36.9M  32.9G  75.9K  19.0K 20180301 15 min 50 s
    cheese_catastrophes_process_control_crash_course_engineering  22.4M  32.9G  56.5K  18.8K 20181115 11 min 1 s
                         crash_course_world_mythology_outtakes_1  9.77M  32.9G  93.9K  18.8K 20170506 4 min 7 s
    bayes_in_science_and_everyday_life_crash_course_statistics_2  24.2M  32.9G  75.0K  18.8K 20180801 11 min 13 s
    testing_your_product_and_getting_feedback_crash_course_busin  22.5M  32.9G  56.2K  18.7K 20190925 12 min 17 s
    hl_sqtt_lmbrtwry_lrwmny_bsqwt_rwm_lhlq_12_mn_crash_course_bl  43.1M  33.0G  74.4K  18.6K 20180405 15 min 2 s
                               crash_course_chemistry_outtakes_3  17.7M  33.0G   147K  18.4K 20131202 6 min 43 s
        unsupervised_machine_learning_crash_course_statistics_37  22.8M  33.0G  55.1K  18.4K 20181107 10 min 55 s
       race_melodrama_and_minstrel_shows_crash_course_theater_30  29.9M  33.0G  73.5K  18.4K 20180921 13 min 38 s
          hrb_lsb_snwt_wl_hrb_lmy_lhlq_26_mn_crash_course_bl_rby  35.7M  33.1G  72.9K  18.2K 20180712 13 min 42 s
          supervised_machine_learning_crash_course_statistics_36  24.8M  33.1G  54.6K  18.2K 20181031 11 min 50 s
             lskndr_lkbr_wsrw_l_zm_lhlq_8_mn_crash_course_bl_rby  32.7M  33.1G  72.4K  18.1K 20180308 13 min 13 s
                future_literacies_crash_course_media_literacy_12  16.8M  33.2G  71.5K  17.9K 20180515 7 min 37 s
        the_horrors_of_the_grand_guignol_crash_course_theater_35  27.3M  33.2G  53.5K  17.8K 20181102 11 min 42 s
                l_thmnywn_wlbndqy_lhlq_19_mn_crash_course_bl_rby  32.9M  33.2G  71.1K  17.8K 20180524 12 min 13 s
    how_not_to_set_your_pizza_on_fire_crash_course_engineering_1  24.1M  33.2G  70.7K  17.7K 20180830 10 min 38 s
                              crash_course_psychology_outtakes_1  17.1M  33.3G   141K  17.6K 20140414 6 min 37 s
    lmbryly_kyf_hymnt_wrwb_l_l_lm_lhlq_35_mn_crash_course_bl_rby  48.3M  33.3G  52.9K  17.6K 20181018 17 min 20 s
     playing_with_power_p_values_pt_3_crash_course_statistics_23  25.9M  33.3G  70.4K  17.6K 20180718 12 min 14 s
           smart_tattoos_tiny_robots_crash_course_engineering_37  20.3M  33.3G  52.4K  17.5K 20190221 9 min 50 s
                               crash_course_chemistry_outtakes_2  18.6M  33.4G   157K  17.4K 20130930 8 min 28 s
                     trykh_lrsmly_lhlq_33_mn_crash_course_bl_rby  41.1M  33.4G  69.3K  17.3K 20181004 15 min 9 s
        rwm_mn_ljmhwry_l_lmbrtwry_lhlq_10_mn_crash_course_bl_rby  36.3M  33.4G  69.0K  17.3K 20180322 15 min 5 s
             why_so_angry_german_theater_crash_course_theater_27  30.1M  33.5G  69.0K  17.2K 20180824 11 min 49 s
    all_night_demon_dance_party_kathakali_crash_course_theater_2  25.4M  33.5G  68.9K  17.2K 20180803 10 min 58 s
        how_seawater_sabotages_ships_crash_course_engineering_43  24.0M  33.5G  51.7K  17.2K 20190411 9 min 56 s
           l_wlm_ljz_lthny_lhlq_42_wlkhyr_mn_crash_course_bl_rby  43.6M  33.6G  51.6K  17.2K 20181206 15 min 28 s
                                            literature_1_preview  4.09M  33.6G  34.3K  17.2K 20200724 57 s 656 ms
                              crash_course_psychology_outtakes_2  23.2M  33.6G   136K  17.0K 20140630 9 min 12 s
               the_birth_of_off_broadway_crash_course_theater_47  28.8M  33.6G  50.9K  17.0K 20190208 12 min 47 s
                           crash_course_biology_ecology_outtakes  13.6M  33.6G   152K  16.9K 20130128 4 min 10 s
                       lfrs_wlgryq_lhlq_5_mn_crash_course_bl_rby  32.3M  33.7G  67.5K  16.9K 20180215 12 min 37 s
                                     outtakes_1_crash_course_a_p  11.3M  33.7G   118K  16.9K 20150316 4 min 31 s
                     mass_separation_crash_course_engineering_17  23.5M  33.7G  67.0K  16.8K 20180913 11 min 15 s
    little_theater_and_american_avant_garde_crash_course_theater  24.3M  33.7G  50.3K  16.8K 20181215 11 min 19 s
                        the_limey_crash_course_film_criticism_10  27.0M  33.7G  66.7K  16.7K 20180322 11 min 12 s
             realism_gets_even_more_real_crash_course_theater_32  31.0M  33.8G  66.3K  16.6K 20181005 12 min 24 s
    pre_columbian_theater_spanish_empire_and_sor_juana_crash_cou  28.5M  33.8G  66.0K  16.5K 20180721 12 min 3 s
                              outtakes_5_crash_course_psychology  11.6M  33.8G   114K  16.3K 20141208 4 min 7 s
             sr_lnhd_hl_hsl_f_lan_lhlq_22_mn_crash_course_bl_rby  37.5M  33.8G  64.9K  16.2K 20180614 13 min 14 s
        skyscrapers_statics_dynamics_crash_course_engineering_26  21.2M  33.9G  48.3K  16.1K 20181129 10 min 9 s
                              outtakes_5_crash_course_philosophy  13.5M  33.9G  79.8K  16.0K 20170220 5 min 59 s
       federal_theatre_and_group_theater_crash_course_theater_42  26.8M  33.9G  47.7K  15.9K 20190104 12 min 4 s
    how_to_create_a_fair_workplace_crash_course_business_soft_sk  23.6M  33.9G  47.5K  15.8K 20190619 10 min 41 s
                               outtakes_1_crash_course_astronomy  8.32M  33.9G   109K  15.5K 20150326 3 min 57 s
                when_predictions_fail_crash_course_statistics_43  30.9M  34.0G  46.5K  15.5K 20190102 10 min 38 s
    anova_part_2_dealing_with_intersectional_groups_crash_course  26.8M  34.0G  46.4K  15.5K 20181017 12 min 41 s
            drugs_dyes_mass_transfer_crash_course_engineering_16  15.9M  34.0G  60.7K  15.2K 20180906 8 min 23 s
       north_america_gets_a_theater_riot_crash_course_theater_29  30.2M  34.0G  59.8K  14.9K 20180914 12 min 39 s
        tryq_lhryr_tryq_lfkr_wlmrd_lhlq_9_mn_crash_course_bl_rby  30.8M  34.1G  58.2K  14.5K 20180315 10 min 48 s
                 lhrb_l_lmy_lthny_lhlq_38_mn_crash_course_bl_rby  43.1M  34.1G  43.6K  14.5K 20181108 14 min 32 s
                              outtakes_4_crash_course_philosophy  14.4M  34.1G  71.0K  14.2K 20170102 6 min 9 s
         tjr_lrqyq_br_lmhyt_ltlsy_lhlq_24_mn_crash_course_bl_rby  38.4M  34.2G  56.7K  14.2K 20180628 13 min 49 s
           england_s_sentimental_theater_crash_course_theater_26  29.4M  34.2G  55.8K  13.9K 20180817 12 min 10 s
        lhrb_l_lmy_lwl_akhr_lhrwb_lhlq_36_mn_crash_course_bl_rby  42.1M  34.2G  41.2K  13.7K 20181025 14 min 8 s
             when_predictions_succeed_crash_course_statistics_44  32.3M  34.3G  41.1K  13.7K 20190109 11 min 19 s
                                 outtakes_1_crash_course_physics  7.92M  34.3G  81.9K  13.7K 20160630 3 min 26 s
         ldwl_lqwmy_wsr_s_wd_lybn_lhlq_34_mn_crash_course_bl_rby  37.6M  34.3G  40.8K  13.6K 20181011 13 min 44 s
             shhr_bhwr_sr_lktshft_lhlq_21_mn_crash_course_bl_rby  35.4M  34.3G  54.3K  13.6K 20180607 13 min 0 s
                              crash_course_out_takes_chemistry_1  15.1M  34.4G   121K  13.5K 20130401 6 min 44 s
             hrkt_lthrr_mn_lst_mr_lhlq_40_mn_crash_course_bl_rby  44.6M  34.4G  40.1K  13.4K 20181122 15 min 28 s
               the_eagle_huntress_crash_course_film_criticism_12  27.2M  34.4G  53.0K  13.2K 20180405 10 min 3 s
               the_replication_crisis_crash_course_statistics_31  34.8M  34.5G  52.7K  13.2K 20180926 14 min 35 s
                                            crash_course_surveys  3.41M  34.5G   105K  13.1K 20140402 1 min 11 s
                               outtakes_4_crash_course_astronomy  10.2M  34.5G  78.5K  13.1K 20151119 4 min 39 s
                      crash_course_intellectual_property_preview  4.19M  34.5G  26.1K  13.0K 20200818 1 min 0 s
                                  hanging_out_at_crash_course_hq   111M  34.6G   129K  12.9K 20120509 1 h 2 min
                               crash_course_chemistry_outtakes_4  20.6M  34.6G   103K  12.8K 20140120 8 min 34 s
                               outtakes_5_crash_course_astronomy  11.5M  34.6G  76.8K  12.8K 20160128 4 min 52 s
                                  literature_outtakes_year_three  7.82M  34.6G  76.5K  12.8K 20160921 3 min 10 s
             statistics_in_the_courts_crash_course_statistics_40  25.6M  34.7G  37.5K  12.5K 20181128 11 min 17 s
           lhrb_lbrd_wltb_t_lskhn_lhlq_39_mn_crash_course_bl_rby  39.8M  34.7G  37.5K  12.5K 20181115 14 min 33 s
                              outtakes_2_crash_course_philosophy  13.1M  34.7G  73.2K  12.2K 20160718 5 min 31 s
                              outtakes_3_crash_course_philosophy  11.2M  34.7G  60.4K  12.1K 20161010 4 min 59 s
                                   outtakes_1_crash_course_games  16.5M  34.7G  70.5K  11.8K 20160701 6 min 24 s
      thwrt_lsyn_wswlan_l_lshyw_y_lhlq_37_mn_crash_course_bl_rby  42.2M  34.8G  34.9K  11.6K 20181101 14 min 8 s
        fitting_models_is_like_tetris_crash_course_statistics_35  23.8M  34.8G  34.6K  11.5K 20181024 11 min 8 s
    lhy_lmdhsh_wlmwt_lgmd_llqbtn_kwk_lhlq_27_mn_crash_course_bl_  30.8M  34.8G  45.3K  11.3K 20180719 12 min 40 s
                          crash_course_computer_science_outtakes  15.3M  34.8G  56.3K  11.3K 20170419 5 min 8 s
                                              office_hours_water  9.52M  34.8G   112K  11.2K 20120213 3 min 10 s
                               outtakes_3_crash_course_astronomy  9.40M  34.9G  78.3K  11.2K 20150903 4 min 32 s
                               outtakes_2_crash_course_astronomy  8.81M  34.9G  76.3K  10.9K 20150611 3 min 56 s
             ltbdl_lkwlwmby_lkbyr_lhlq_23_mn_crash_course_bl_rby  37.3M  34.9G  43.2K  10.8K 20180621 13 min 37 s
    sbny_wjbl_lfd_wqs_wl_zm_mly_lmy_fy_ltrykh_lhlq_25_mn_crash_c  36.1M  34.9G  42.4K  10.6K 20180705 13 min 3 s
                         outtakes_2_crash_course_world_mythology  7.83M  34.9G  52.8K  10.6K 20170728 3 min 32 s
              ltjr_fy_lmhyt_lhndy_lhlq_18_mn_crash_course_bl_rby  31.8M  35.0G  41.8K  10.4K 20180517 12 min 24 s
                 outtakes_1_crash_course_government_and_politics  12.8M  35.0G  72.8K  10.4K 20150403 5 min 35 s
                                   outtakes_2_crash_course_games  14.3M  35.0G  60.9K  10.1K 20160917 4 min 50 s
                                   outtakes_3_crash_course_games  15.2M  35.0G  50.5K  10.1K 20161223 4 min 58 s
                                     outtakes_4_crash_course_a_p  14.5M  35.0G  59.7K  9.94K 20151102 5 min 47 s
    mryk_ljnwby_ryd_hrkt_lthrr_fy_l_lm_lhlq_31_mn_crash_course_b  42.8M  35.1G  39.8K  9.94K 20180920 15 min 56 s
                                     outtakes_2_crash_course_a_p  11.6M  35.1G  68.5K  9.79K 20150601 5 min 2 s
                                 outtakes_2_crash_course_physics  14.2M  35.1G  57.2K  9.54K 20160825 4 min 58 s
                                    crash_course_ecology_preview  5.67M  35.1G  19.1K  9.53K 20200708 1 min 13 s
                                    become_a_crash_course_patron  8.79M  35.1G  66.3K  9.48K 20150316 3 min 17 s
                                     outtakes_3_crash_course_a_p  9.45M  35.1G  64.9K  9.27K 20150817 3 min 55 s
                                 outtakes_4_crash_course_physics  15.8M  35.1G  45.5K  9.09K 20170330 5 min 41 s
                 outtakes_5_crash_course_government_and_politics  10.8M  35.1G  54.2K  9.03K 20160312 4 min 45 s
                                     outtakes_5_crash_course_a_p  12.7M  35.2G  51.9K  8.65K 20160104 5 min 14 s
                                     outtakes_6_crash_course_a_p  13.1M  35.2G  51.8K  8.64K 20160111 5 min 31 s
                                 outtakes_3_crash_course_physics  20.0M  35.2G  42.5K  8.51K 20161110 6 min 20 s
                              outtakes_crash_course_film_history  11.3M  35.2G  42.5K  8.50K 20170810 5 min 40 s
      lthwr_lhyty_njh_thwr_ll_byd_lhlq_30_mn_crash_course_bl_rby  38.6M  35.2G  32.7K  8.18K 20180913 14 min 12 s
                     outtakes_crash_course_intellectual_property  8.28M  35.3G  55.9K  7.99K 20150610 4 min 47 s
                                      crash_course_econ_outtakes  15.4M  35.3G  46.8K  7.80K 20160616 5 min 49 s
                 outtakes_4_crash_course_government_and_politics  13.0M  35.3G  43.3K  7.21K 20151125 4 min 41 s
                        outtakes_2_crash_course_computer_science  10.6M  35.3G  34.7K  6.93K 20170719 3 min 38 s
                 outtakes_2_crash_course_government_and_politics  9.96M  35.3G  48.3K  6.90K 20150619 3 min 59 s
                 outtakes_3_crash_course_government_and_politics  11.9M  35.3G  44.8K  6.40K 20150911 3 min 53 s
                               crash_course_sociology_outtakes_1  16.7M  35.3G  30.3K  6.06K 20170828 5 min 53 s


* Now determine the video ID's that we want in our new zim


```python
print('We will include videos with views_per_year greater than %s'%boundary_views_per_year)
wanted_ids = []
sql = 'SELECT yt_id, title from video_info where views_per_year > ?'
db.c.execute(sql,[boundary_views_per_year,])
rows = db.c.fetchall()
for row in rows:
    wanted_ids.append(row['yt_id'])

#with open(HOME + '/zimtest/' + PROJECT_NAME + '/wanted_list.csv','w') as fp:
#    for row in rows:
#        fp.write('%s,%s\n'%(row['yt_id'],row['title'],))
```

    We will include videos with views_per_year greater than 237099

wanted_ids
* Now let's start building up the output directory



```python
import shutil
# copy the default top level directories (these were in the zim's "-" directory )
print('Copying wanted folders and Videos to %s'%OUTPUT_DIR)
cpy_dirs = ['assets','cache','channels']
for d in cpy_dirs:
    shutil.rmtree(os.path.join(OUTPUT_DIR,d),ignore_errors=True)
    os.makedirs(os.path.join(OUTPUT_DIR,d))
    src = os.path.join(PROJECT_DIR,d)
    dest = os.path.join(OUTPUT_DIR,d)
    shutil.copytree(src,dest,dirs_exist_ok=True, symlinks=True)
```

    Copying wanted folders and Videos to /ext/zims/crash/output_tree



```python
# Copy the videos selected by the wanted_ids list to output file
import shutil
for f in wanted_ids:
    if not os.path.isdir(os.path.join(OUTPUT_DIR,'videos',f)):
        os.makedirs(os.path.join(OUTPUT_DIR,'videos',f))
        src = os.path.join(PROJECT_DIR,'videos',f)
        dest = os.path.join(OUTPUT_DIR,'videos',f)
        shutil.copytree(src,dest,dirs_exist_ok=True)
```


```python
#  Copy the files in the root directory
import shutil
for yt_id in wanted_ids:
    map_index_to_slug = get_zim_data(yt_id)
    if len(map_index_to_slug) > 0:
        title = map_index_to_slug['slug']
        src = os.path.join(PROJECT_DIR,title + '.html')
        dest = OUTPUT_DIR + '/' + title + '.html'
        if os.path.isfile(src) and not os.path.isfile(dest):
            shutil.copyfile(src,dest)
        else:
            print('src:%s'%src)
```

    src:/ext/zims/crash/tree/italian_and_german_unification_crash_course_european_history_27.html
    src:/ext/zims/crash/tree/indian_pantheons_crash_course_world_mythology_8.html
    src:/ext/zims/crash/tree/creation_from_the_void_crash_course_world_mythology_2.html
    src:/ext/zims/crash/tree/the_end_of_civilization_in_the_bronze_age_crash_course_world_history_211.html
    src:/ext/zims/crash/tree/the_reagan_revolution_crash_course_us_history_43.html
    src:/ext/zims/crash/tree/what_is_myth_crash_course_world_mythology_1.html
    src:/ext/zims/crash/tree/what_is_sociology_crash_course_sociology_1.html
    src:/ext/zims/crash/tree/separation_of_powers_and_checks_and_balances_crash_course_government_and_politics_3.html
    src:/ext/zims/crash/tree/dna_hot_pockets_the_longest_word_ever_crash_course_biology_11.html
    src:/ext/zims/crash/tree/plato_and_aristotle_crash_course_history_of_science_3.html
    src:/ext/zims/crash/tree/the_periodic_table_crash_course_chemistry_4.html
    src:/ext/zims/crash/tree/the_cold_war_in_asia_crash_course_us_history_38.html
    src:/ext/zims/crash/tree/aquinas_the_cosmological_arguments_crash_course_philosophy_10.html
    src:/ext/zims/crash/tree/what_is_god_like_crash_course_philosophy_12.html
    src:/ext/zims/crash/tree/endocrine_system_part_2_hormone_cascades_crash_course_a_p_24.html
    src:/ext/zims/crash/tree/fall_of_the_roman_empire_in_the_15th_century_crash_course_world_history_12.html
    src:/ext/zims/crash/tree/the_integumentary_system_part_1_skin_deep_crash_course_a_p_6.html
    src:/ext/zims/crash/tree/latin_american_revolutions_crash_course_world_history_31.html
    src:/ext/zims/crash/tree/wait_for_it_the_mongols_crash_course_world_history_17.html
    src:/ext/zims/crash/tree/mesopotamia_crash_course_world_history_3.html
    src:/ext/zims/crash/tree/reconstruction_and_1876_crash_course_us_history_22.html
    src:/ext/zims/crash/tree/the_crusades_pilgrimage_or_holy_war_crash_course_world_history_15.html
    src:/ext/zims/crash/tree/witchcraft_crash_course_european_history_10.html
    src:/ext/zims/crash/tree/communists_nationalists_and_china_s_revolutions_crash_course_world_history_37.html
    src:/ext/zims/crash/tree/the_2008_financial_crisis_crash_course_economics_12.html
    src:/ext/zims/crash/tree/atp_respiration_crash_course_biology_7.html
    src:/ext/zims/crash/tree/neutron_stars_crash_course_astronomy_32.html
    src:/ext/zims/crash/tree/the_nervous_system_part_2_action_potential_crash_course_a_p_9.html
    src:/ext/zims/crash/tree/karl_marx_conflict_theory_crash_course_sociology_6.html
    src:/ext/zims/crash/tree/the_market_revolution_crash_course_us_history_12.html
    src:/ext/zims/crash/tree/the_chemical_mind_crash_course_psychology_3.html
    src:/ext/zims/crash/tree/the_cold_war_crash_course_us_history_37.html
    src:/ext/zims/crash/tree/money_debt_crash_course_world_history_202.html
    src:/ext/zims/crash/tree/the_seven_years_war_crash_course_world_history_26.html
    src:/ext/zims/crash/tree/the_industrial_economy_crash_course_us_history_23.html
    src:/ext/zims/crash/tree/uranus_neptune_crash_course_astronomy_19.html
    src:/ext/zims/crash/tree/homunculus_crash_course_psychology_6.html
    src:/ext/zims/crash/tree/redox_reactions_crash_course_chemistry_10.html
    src:/ext/zims/crash/tree/respiratory_system_part_2_crash_course_a_p_32.html
    src:/ext/zims/crash/tree/kant_categorical_imperatives_crash_course_philosophy_35.html
    src:/ext/zims/crash/tree/digestive_system_part_2_crash_course_a_p_34.html
    src:/ext/zims/crash/tree/terrorism_war_and_bush_43_crash_course_us_history_46.html
    src:/ext/zims/crash/tree/the_norse_pantheon_crash_course_world_mythology_10.html
    src:/ext/zims/crash/tree/metabolism_nutrition_part_1_crash_course_a_p_36.html
    src:/ext/zims/crash/tree/sensation_and_perception_crash_course_psychology_5.html
    src:/ext/zims/crash/tree/where_us_politics_came_from_crash_course_us_history_9.html
    src:/ext/zims/crash/tree/the_sun_crash_course_astronomy_10.html
    src:/ext/zims/crash/tree/war_expansion_crash_course_us_history_17.html
    src:/ext/zims/crash/tree/women_s_suffrage_crash_course_us_history_31.html
    src:/ext/zims/crash/tree/how_to_argue_philosophical_reasoning_crash_course_philosophy_2.html
    src:/ext/zims/crash/tree/the_epic_of_gilgamesh_crash_course_world_mythology_26.html
    src:/ext/zims/crash/tree/japan_in_the_heian_period_and_cultural_history_crash_course_world_history_227.html
    src:/ext/zims/crash/tree/personality_disorders_crash_course_psychology_34.html
    src:/ext/zims/crash/tree/alexander_the_great_and_the_situation_the_great_crash_course_world_history_8.html
    src:/ext/zims/crash/tree/when_is_thanksgiving_colonizing_america_crash_course_us_history_2.html
    src:/ext/zims/crash/tree/islam_the_quran_and_the_five_pillars_all_without_a_flamewar_crash_course_world_history_13.html
    src:/ext/zims/crash/tree/the_agricultural_revolution_crash_course_world_history_1.html
    src:/ext/zims/crash/tree/representing_numbers_and_letters_with_binary_crash_course_computer_science_4.html
    src:/ext/zims/crash/tree/rethinking_civilization_crash_course_world_history_201.html
    src:/ext/zims/crash/tree/how_we_make_memories_crash_course_psychology_13.html
    src:/ext/zims/crash/tree/florence_and_the_renaissance_crash_course_european_history_2.html
    src:/ext/zims/crash/tree/the_bobo_beatdown_crash_course_psychology_12.html
    src:/ext/zims/crash/tree/haitian_revolutions_crash_course_world_history_30.html
    src:/ext/zims/crash/tree/vision_crash_course_a_p_18.html
    src:/ext/zims/crash/tree/revolutions_of_1848_crash_course_european_history_26.html
    src:/ext/zims/crash/tree/the_mughal_empire_and_historical_reputation_crash_course_world_history_217.html
    src:/ext/zims/crash/tree/sympathetic_nervous_system_crash_course_a_p_14.html
    src:/ext/zims/crash/tree/age_of_jackson_crash_course_us_history_14.html
    src:/ext/zims/crash/tree/democracy_authoritarian_capitalism_and_china_crash_course_world_history_230.html
    src:/ext/zims/crash/tree/joints_crash_course_a_p_20.html
    src:/ext/zims/crash/tree/slavery_crash_course_us_history_13.html
    src:/ext/zims/crash/tree/george_hw_bush_and_the_end_of_the_cold_war_crash_course_us_history_44.html
    src:/ext/zims/crash/tree/the_big_bang_crash_course_big_history_1.html
    src:/ext/zims/crash/tree/the_quakers_the_dutch_and_the_ladies_crash_course_us_history_4.html
    src:/ext/zims/crash/tree/plant_cells_crash_course_biology_6.html
    src:/ext/zims/crash/tree/eukaryopolis_the_city_of_animal_cells_crash_course_biology_4.html
    src:/ext/zims/crash/tree/autonomic_nervous_system_crash_course_a_p_13.html
    src:/ext/zims/crash/tree/the_progressive_era_crash_course_us_history_27.html
    src:/ext/zims/crash/tree/digestive_system_part_1_crash_course_a_p_33.html
    src:/ext/zims/crash/tree/progressive_presidents_crash_course_us_history_29.html
    src:/ext/zims/crash/tree/america_in_world_war_i_crash_course_us_history_30.html
    src:/ext/zims/crash/tree/introduction_to_astronomy_crash_course_astronomy_1.html
    src:/ext/zims/crash/tree/natural_selection_crash_course_biology_14.html
    src:/ext/zims/crash/tree/the_rise_of_conservatism_crash_course_us_history_41.html
    src:/ext/zims/crash/tree/the_new_deal_crash_course_us_history_34.html
    src:/ext/zims/crash/tree/climate_change_chaos_and_the_little_ice_age_crash_course_world_history_206.html
    src:/ext/zims/crash/tree/motion_in_a_straight_line_crash_course_physics_1.html
    src:/ext/zims/crash/tree/economic_depression_and_dictators_crash_course_european_history_37.html
    src:/ext/zims/crash/tree/iran_s_revolutions_crash_course_world_history_226.html
    src:/ext/zims/crash/tree/the_1960s_in_america_crash_course_us_history_40.html
    src:/ext/zims/crash/tree/intelligent_design_crash_course_philosophy_11.html
    src:/ext/zims/crash/tree/capitalism_and_socialism_crash_course_world_history_33.html
    src:/ext/zims/crash/tree/aristotle_virtue_theory_crash_course_philosophy_38.html
    src:/ext/zims/crash/tree/altered_states_crash_course_psychology_10.html
    src:/ext/zims/crash/tree/consciousness_crash_course_psychology_8.html
    src:/ext/zims/crash/tree/high_mass_stars_crash_course_astronomy_31.html
    src:/ext/zims/crash/tree/ragnarok_crash_course_world_mythology_24.html
    src:/ext/zims/crash/tree/immune_system_part_1_crash_course_a_p_45.html
    src:/ext/zims/crash/tree/atomic_hook_ups_types_of_chemical_bonds_crash_course_chemistry_22.html
    src:/ext/zims/crash/tree/cognition_how_your_mind_can_amaze_and_betray_you_crash_course_psychology_15.html
    src:/ext/zims/crash/tree/ghosts_murder_and_more_murder_hamlet_part_1_crash_course_literature_203.html
    src:/ext/zims/crash/tree/who_started_world_war_i_crash_course_world_history_210.html
    src:/ext/zims/crash/tree/world_war_ii_a_war_for_resources_crash_course_world_history_220.html
    src:/ext/zims/crash/tree/how_world_war_i_started_crash_course_world_history_209.html
    src:/ext/zims/crash/tree/muscles_part_1_muscle_cells_crash_course_a_p_21.html
    src:/ext/zims/crash/tree/conflict_in_israel_and_palestine_crash_course_world_history_223.html
    src:/ext/zims/crash/tree/boolean_logic_logic_gates_crash_course_computer_science_3.html
    src:/ext/zims/crash/tree/the_holocaust_genocides_and_mass_murder_of_wwii_crash_course_european_history_40.html
    src:/ext/zims/crash/tree/early_computing_crash_course_computer_science_1.html
    src:/ext/zims/crash/tree/immune_system_part_2_crash_course_a_p_46.html
    src:/ext/zims/crash/tree/decolonization_and_nationalism_triumphant_crash_course_world_history_40.html
    src:/ext/zims/crash/tree/work_energy_and_power_crash_course_physics_9.html
    src:/ext/zims/crash/tree/the_election_of_1860_the_road_to_disunion_crash_course_us_history_18.html
    src:/ext/zims/crash/tree/the_problem_of_evil_crash_course_philosophy_13.html
    src:/ext/zims/crash/tree/the_seven_years_war_and_the_great_awakening_crash_course_us_history_5.html
    src:/ext/zims/crash/tree/quantum_mechanics_part_1_crash_course_physics_43.html
    src:/ext/zims/crash/tree/the_nervous_system_part_3_synapses_crash_course_a_p_10.html
    src:/ext/zims/crash/tree/economic_systems_and_macroeconomics_crash_course_economics_3.html
    src:/ext/zims/crash/tree/ancient_egypt_crash_course_world_history_4.html
    src:/ext/zims/crash/tree/tea_taxes_and_the_american_revolution_crash_course_world_history_28.html
    src:/ext/zims/crash/tree/reproductive_system_part_2_male_reproductive_system_crash_course_a_p_41.html
    src:/ext/zims/crash/tree/the_17th_century_crisis_crash_course_european_history_11.html
    src:/ext/zims/crash/tree/asian_responses_to_imperialism_crash_course_world_history_213.html
    src:/ext/zims/crash/tree/capitalism_and_the_dutch_east_india_company_crash_course_world_history_229.html
    src:/ext/zims/crash/tree/the_great_depression_crash_course_us_history_33.html
    src:/ext/zims/crash/tree/gilded_age_politics_crash_course_us_history_26.html
    src:/ext/zims/crash/tree/acid_base_reactions_in_solution_crash_course_chemistry_8.html
    src:/ext/zims/crash/tree/central_nervous_system_crash_course_a_p_11.html
    src:/ext/zims/crash/tree/metaethics_crash_course_philosophy_32.html
    src:/ext/zims/crash/tree/the_industrial_revolution_crash_course_european_history_24.html
    src:/ext/zims/crash/tree/adolescence_crash_course_psychology_20.html
    src:/ext/zims/crash/tree/remembering_and_forgetting_crash_course_psychology_14.html
    src:/ext/zims/crash/tree/polar_non_polar_molecules_crash_course_chemistry_23.html
    src:/ext/zims/crash/tree/indus_valley_civilization_crash_course_world_history_2.html
    src:/ext/zims/crash/tree/india_crash_course_history_of_science_4.html
    src:/ext/zims/crash/tree/endocrine_system_part_1_glands_hormones_crash_course_a_p_23.html
    src:/ext/zims/crash/tree/derivatives_crash_course_physics_2.html
    src:/ext/zims/crash/tree/the_renaissance_was_it_a_thing_crash_course_world_history_22.html
    src:/ext/zims/crash/tree/natural_law_theory_crash_course_philosophy_34.html
    src:/ext/zims/crash/tree/coal_steam_and_the_industrial_revolution_crash_course_world_history_32.html
    src:/ext/zims/crash/tree/the_history_of_atomic_chemistry_crash_course_chemistry_37.html
    src:/ext/zims/crash/tree/the_columbian_exchange_crash_course_world_history_23.html
    src:/ext/zims/crash/tree/heredity_crash_course_biology_9.html
    src:/ext/zims/crash/tree/what_is_statistics_crash_course_statistics_1.html
    src:/ext/zims/crash/tree/the_constitution_the_articles_and_federalism_crash_course_us_history_8.html
    src:/ext/zims/crash/tree/what_is_philosophy_crash_course_philosophy_1.html
    src:/ext/zims/crash/tree/civil_rights_and_the_1950s_crash_course_us_history_39.html
    src:/ext/zims/crash/tree/the_black_legend_native_americans_and_spaniards_crash_course_us_history_1.html
    src:/ext/zims/crash/tree/utilitarianism_crash_course_philosophy_36.html
    src:/ext/zims/crash/tree/leonardo_dicaprio_the_nature_of_reality_crash_course_philosophy_4.html
    src:/ext/zims/crash/tree/who_won_the_american_revolution_crash_course_us_history_7.html
    src:/ext/zims/crash/tree/meet_your_master_getting_to_know_your_brain_crash_course_psychology_4.html
    src:/ext/zims/crash/tree/trauma_and_addiction_crash_course_psychology_31.html
    src:/ext/zims/crash/tree/the_bicameral_congress_crash_course_government_and_politics_2.html
    src:/ext/zims/crash/tree/eating_and_body_dysmorphic_disorders_crash_course_psychology_33.html
    src:/ext/zims/crash/tree/usa_vs_ussr_fight_the_cold_war_crash_course_world_history_39.html
    src:/ext/zims/crash/tree/columbus_de_gama_and_zheng_he_15th_century_mariners_crash_course_world_history_21.html
    src:/ext/zims/crash/tree/newton_s_laws_crash_course_physics_5.html
    src:/ext/zims/crash/tree/registers_and_ram_crash_course_computer_science_6.html
    src:/ext/zims/crash/tree/the_roads_to_world_war_i_crash_course_european_history_32.html
    src:/ext/zims/crash/tree/taxonomy_life_s_filing_system_crash_course_biology_19.html
    src:/ext/zims/crash/tree/crash_course_computer_science_preview.html
    src:/ext/zims/crash/tree/world_war_ii_crash_course_european_history_38.html
    src:/ext/zims/crash/tree/the_protestant_reformation_crash_course_european_history_6.html
    src:/ext/zims/crash/tree/dna_structure_and_replication_crash_course_biology_10.html
    src:/ext/zims/crash/tree/war_human_nature_crash_course_world_history_204.html
    src:/ext/zims/crash/tree/macroeconomics_crash_course_economics_5.html
    src:/ext/zims/crash/tree/charles_v_and_the_holy_roman_empire_crash_course_world_history_219.html
    src:/ext/zims/crash/tree/urinary_system_part_1_crash_course_a_p_38.html
    src:/ext/zims/crash/tree/the_roaring_20_s_crash_course_us_history_32.html
    src:/ext/zims/crash/tree/luther_and_the_protestant_reformation_crash_course_world_history_218.html
    src:/ext/zims/crash/tree/how_and_why_we_read_crash_course_english_literature_1.html
    src:/ext/zims/crash/tree/psychological_disorders_crash_course_psychology_28.html
    src:/ext/zims/crash/tree/mansa_musa_and_islam_in_africa_crash_course_world_history_16.html
    src:/ext/zims/crash/tree/covid_19_and_public_health_a_message_from_crash_course.html
    src:/ext/zims/crash/tree/the_silk_road_and_ancient_trade_crash_course_world_history_9.html
    src:/ext/zims/crash/tree/the_nervous_system_part_1_crash_course_a_p_8.html
    src:/ext/zims/crash/tree/in_da_club_membranes_transport_crash_course_biology_5.html
    src:/ext/zims/crash/tree/westward_expansion_crash_course_us_history_24.html
    src:/ext/zims/crash/tree/human_evolution_crash_course_big_history_6.html
    src:/ext/zims/crash/tree/intro_to_economics_crash_course_econ_1.html
    src:/ext/zims/crash/tree/schizophrenia_and_dissociative_disorders_crash_course_psychology_32.html
    src:/ext/zims/crash/tree/imports_exports_and_exchange_rates_crash_course_economics_15.html
    src:/ext/zims/crash/tree/the_french_revolution_crash_course_european_history_21.html
    src:/ext/zims/crash/tree/existentialism_crash_course_philosophy_16.html
    src:/ext/zims/crash/tree/social_influence_crash_course_psychology_38.html
    src:/ext/zims/crash/tree/the_age_of_exploration_crash_course_european_history_4.html
    src:/ext/zims/crash/tree/prejudice_and_discrimination_crash_course_psychology_39.html
    src:/ext/zims/crash/tree/globalization_i_the_upside_crash_course_world_history_41.html
    src:/ext/zims/crash/tree/crash_course_world_mythology_preview.html
    src:/ext/zims/crash/tree/the_natives_and_the_english_crash_course_us_history_3.html
    src:/ext/zims/crash/tree/congo_and_africa_s_world_war_crash_course_world_history_221.html
    src:/ext/zims/crash/tree/the_dark_ages_how_dark_were_they_really_crash_course_world_history_14.html
    src:/ext/zims/crash/tree/supply_and_demand_crash_course_economics_4.html
    src:/ext/zims/crash/tree/anselm_the_argument_for_god_crash_course_philosophy_9.html
    src:/ext/zims/crash/tree/taking_notes_crash_course_study_skills_1.html
    src:/ext/zims/crash/tree/christianity_from_judaism_to_constantine_crash_course_world_history_11.html
    src:/ext/zims/crash/tree/muscles_part_2_organismal_level_crash_course_a_p_22.html
    src:/ext/zims/crash/tree/the_vikings_crash_course_world_history_224.html
    src:/ext/zims/crash/tree/tissues_part_3_connective_tissues_crash_course_a_p_4.html
    src:/ext/zims/crash/tree/growth_cities_and_immigration_crash_course_us_history_25.html
    src:/ext/zims/crash/tree/medieval_europe_crash_course_european_history_1.html
    src:/ext/zims/crash/tree/the_atlantic_slave_trade_crash_course_world_history_24.html
    src:/ext/zims/crash/tree/the_enlightenment_crash_course_european_history_18.html
    src:/ext/zims/crash/tree/russia_the_kievan_rus_and_the_mongols_crash_course_world_history_20.html
    src:/ext/zims/crash/tree/biological_molecules_you_are_what_you_eat_crash_course_biology_3.html
    src:/ext/zims/crash/tree/how_to_train_a_brain_crash_course_psychology_11.html
    src:/ext/zims/crash/tree/to_sleep_perchance_to_dream_crash_course_psychology_9.html
    src:/ext/zims/crash/tree/samurai_daimyo_matthew_perry_and_nationalism_crash_course_world_history_34.html
    src:/ext/zims/crash/tree/unit_conversion_significant_figures_crash_course_chemistry_2.html
    src:/ext/zims/crash/tree/meiosis_where_the_sex_starts_crash_course_biology_13.html
    src:/ext/zims/crash/tree/the_civil_war_part_i_crash_course_us_history_20.html
    src:/ext/zims/crash/tree/moon_phases_crash_course_astronomy_4.html
    src:/ext/zims/crash/tree/tissues_part_2_epithelial_tissue_crash_course_a_p_3.html
    src:/ext/zims/crash/tree/karl_popper_science_pseudoscience_crash_course_philosophy_8.html
    src:/ext/zims/crash/tree/major_sociological_paradigms_crash_course_sociology_2.html
    src:/ext/zims/crash/tree/globalization_ii_good_or_bad_crash_course_world_history_42.html
    src:/ext/zims/crash/tree/respiratory_system_part_1_crash_course_a_p_31.html
    src:/ext/zims/crash/tree/disease_crash_course_world_history_203.html
    src:/ext/zims/crash/tree/the_congress_of_vienna_crash_course_european_history_23.html
    src:/ext/zims/crash/tree/the_civil_war_part_2_crash_course_us_history_21.html
    src:/ext/zims/crash/tree/women_in_the_19th_century_crash_course_us_history_16.html
    src:/ext/zims/crash/tree/the_growth_of_knowledge_crash_course_psychology_18.html
    src:/ext/zims/crash/tree/locke_berkeley_empiricism_crash_course_philosophy_6.html
    src:/ext/zims/crash/tree/urinary_system_part_2_crash_course_a_p_39.html
    src:/ext/zims/crash/tree/world_war_ii_crash_course_world_history_38.html
    src:/ext/zims/crash/tree/what_is_justice_crash_course_philosophy_40.html
    src:/ext/zims/crash/tree/intro_to_psychology_crash_course_psychology_1.html
    src:/ext/zims/crash/tree/archdukes_cynicism_and_world_war_i_crash_course_world_history_36.html
    src:/ext/zims/crash/tree/measuring_personality_crash_course_psychology_22.html
    src:/ext/zims/crash/tree/ocd_and_anxiety_disorders_crash_course_psychology_29.html
    src:/ext/zims/crash/tree/the_power_of_motivation_crash_course_psychology_17.html
    src:/ext/zims/crash/tree/how_to_argue_induction_abduction_crash_course_philosophy_3.html
    src:/ext/zims/crash/tree/social_thinking_crash_course_psychology_37.html
    src:/ext/zims/crash/tree/how_computers_calculate_the_alu_crash_course_computer_science_5.html
    src:/ext/zims/crash/tree/orbitals_crash_course_chemistry_25.html
    src:/ext/zims/crash/tree/the_northern_renaissance_crash_course_european_history_3.html
    src:/ext/zims/crash/tree/carbon_so_simple_crash_course_biology_1.html
    src:/ext/zims/crash/tree/the_french_revolution_crash_course_world_history_29.html
    src:/ext/zims/crash/tree/the_amazing_life_and_strange_death_of_captain_cook_crash_course_world_history_27.html
    src:/ext/zims/crash/tree/reproductive_system_part_3_sex_fertilization_crash_course_a_p_42.html
    src:/ext/zims/crash/tree/the_nervous_system_crashcourse_biology_26.html
    src:/ext/zims/crash/tree/the_electron_crash_course_chemistry_5.html
    src:/ext/zims/crash/tree/the_meaning_of_knowledge_crash_course_philosophy_7.html
    src:/ext/zims/crash/tree/introduction_crash_course_u_s_government_and_politics.html
    src:/ext/zims/crash/tree/the_clinton_years_or_the_1990s_crash_course_us_history_45.html
    src:/ext/zims/crash/tree/int_l_commerce_snorkeling_camels_and_the_indian_ocean_trade_crash_course_world_history_18.html
    src:/ext/zims/crash/tree/federalism_crash_course_government_and_politics_4.html
    src:/ext/zims/crash/tree/world_war_ii_part_2_the_homefront_crash_course_us_history_36.html
    src:/ext/zims/crash/tree/scientific_revolution_crash_course_european_history_12.html
    src:/ext/zims/crash/tree/buddha_and_ashoka_crash_course_world_history_6.html
    src:/ext/zims/crash/tree/black_holes_crash_course_astronomy_33.html
    src:/ext/zims/crash/tree/napoleon_bonaparte_crash_course_european_history_22.html
    src:/ext/zims/crash/tree/immune_system_part_3_crash_course_a_p_47.html
    src:/ext/zims/crash/tree/psychological_research_crash_course_psychology_2.html
    src:/ext/zims/crash/tree/cartesian_skepticism_neo_meet_rene_crash_course_philosophy_5.html
    src:/ext/zims/crash/tree/deep_time_crash_course_astronomy_45.html
    src:/ext/zims/crash/tree/lymphatic_system_crash_course_a_p_44.html
    src:/ext/zims/crash/tree/magnetism_crash_course_physics_32.html
    src:/ext/zims/crash/tree/introduction_to_anatomy_physiology_crash_course_a_p_1.html
    src:/ext/zims/crash/tree/crash_course_european_history_preview.html
    src:/ext/zims/crash/tree/electronic_computing_crash_course_computer_science_2.html
    src:/ext/zims/crash/tree/2000_years_of_chinese_history_the_mandate_of_heaven_and_confucius_world_history_7.html
    src:/ext/zims/crash/tree/the_persians_greeks_crash_course_world_history_5.html
    src:/ext/zims/crash/tree/obamanation_crash_course_us_history_47.html
    src:/ext/zims/crash/tree/the_skeletal_system_crash_course_a_p_19.html
    src:/ext/zims/crash/tree/imperialism_crash_course_world_history_35.html
    src:/ext/zims/crash/tree/electric_charge_crash_course_physics_25.html
    src:/ext/zims/crash/tree/a_long_and_difficult_journey_or_the_odyssey_crash_course_literature_201.html
    src:/ext/zims/crash/tree/world_war_ii_part_1_crash_course_us_history_35.html
    src:/ext/zims/crash/tree/like_pale_gold_the_great_gatsby_part_1_crash_course_english_literature_4.html
    src:/ext/zims/crash/tree/the_war_of_1812_crash_course_us_history_11.html
    src:/ext/zims/crash/tree/intro_to_algorithms_crash_course_computer_science_13.html
    src:/ext/zims/crash/tree/hearing_balance_crash_course_a_p_17.html
    src:/ext/zims/crash/tree/the_ideal_gas_law_crash_course_chemistry_12.html
    src:/ext/zims/crash/tree/perceiving_is_believing_crash_course_psychology_7.html
    src:/ext/zims/crash/tree/reproductive_system_part_1_female_reproductive_system_crash_course_a_p_40.html
    src:/ext/zims/crash/tree/american_imperialism_crash_course_us_history_28.html
    src:/ext/zims/crash/tree/the_spanish_empire_silver_runaway_inflation_crash_course_world_history_25.html
    src:/ext/zims/crash/tree/peripheral_nervous_system_crash_course_a_p_12.html
    src:/ext/zims/crash/tree/blood_vessels_part_1_form_and_function_crash_course_a_p_27.html
    src:/ext/zims/crash/tree/russian_revolution_and_civil_war_crash_course_european_history_35.html
    src:/ext/zims/crash/tree/the_roman_empire_or_republic_or_which_was_it_crash_course_world_history_10.html
    src:/ext/zims/crash/tree/the_heart_part_2_heart_throbs_crash_course_a_p_26.html
    src:/ext/zims/crash/tree/blood_part_1_true_blood_crash_course_a_p_29.html
    src:/ext/zims/crash/tree/depressive_and_bipolar_disorders_crash_course_psychology_30.html
    src:/ext/zims/crash/tree/islam_and_politics_crash_course_world_history_216.html
    src:/ext/zims/crash/tree/specialization_and_trade_crash_course_economics_2.html
    src:/ext/zims/crash/tree/the_creation_of_chemistry_the_fundamental_laws_crash_course_chemistry_3.html
    src:/ext/zims/crash/tree/photosynthesis_crash_course_biology_8.html
    src:/ext/zims/crash/tree/19th_century_reforms_crash_course_us_history_15.html
    src:/ext/zims/crash/tree/mitosis_splitting_up_is_complicated_crash_course_biology_12.html
    src:/ext/zims/crash/tree/the_nucleus_crash_course_chemistry_1.html
    src:/ext/zims/crash/tree/let_s_talk_about_sex_crash_course_psychology_27.html
    src:/ext/zims/crash/tree/taxes_smuggling_prelude_to_revolution_crash_course_us_history_6.html
    src:/ext/zims/crash/tree/emotion_stress_and_health_crash_course_psychology_26.html
    src:/ext/zims/crash/tree/venice_and_the_ottoman_empire_crash_course_world_history_19.html
    src:/ext/zims/crash/tree/political_ideology_crash_course_government_and_politics_35.html
    src:/ext/zims/crash/tree/fate_family_and_oedipus_rex_crash_course_literature_202.html
    src:/ext/zims/crash/tree/water_liquid_awesome_crash_course_biology_2.html
    src:/ext/zims/crash/tree/determinism_vs_free_will_crash_course_philosophy_24.html
    src:/ext/zims/crash/tree/controversy_of_intelligence_crash_course_psychology_23.html
    src:/ext/zims/crash/tree/thomas_jefferson_his_democracy_crash_course_us_history_10.html
    src:/ext/zims/crash/tree/the_heart_part_1_under_pressure_crash_course_a_p_25.html
    src:/ext/zims/crash/tree/stoichiometry_chemistry_for_massive_creatures_crash_course_chemistry_6.html
    src:/ext/zims/crash/tree/dark_matter_crash_course_astronomy_41.html
    src:/ext/zims/crash/tree/perspectives_on_death_crash_course_philosophy_17.html
    src:/ext/zims/crash/tree/tissues_part_1_crash_course_a_p_2.html
    src:/ext/zims/crash/tree/1984_by_george_orwell_part_1_crash_course_literature_401.html
    src:/ext/zims/crash/tree/enthalpy_crash_course_chemistry_18.html

wanted_ids

```python
# There are essential files that are needed in the zim
needed = ['/favicon.jpg','/home.html','/profile.jpg']
for f in needed:
    cmd = '/bin/cp %s %s'%(PROJECT_DIR  + f,OUTPUT_DIR)
    subprocess.run(cmd,shell=True)
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
meta_data ={}
meta_file_names = os.listdir(PROJECT_DIR + '/M/')
for f in meta_file_names:
    meta_data[f] = get_file_value(PROJECT_DIR + '/M/' + f)
pprint(meta_data)
    


```

    {'Counter': 'application/font-sfnt=6;text/css=6;application/javascript=83;text/plain=8;application/octet-stream=15;text/html=1812;application/x-shockwave-flash=1;text/markdown=1;image/jpeg=647;image/svg+xml=1;application/json=208;image/png=2;video/webm=1811;image/webp=1197',
     'Creator': 'Youtube Channel “TED-Ed”',
     'Date': '2021-01-16',
     'Description': 'TED-Ed’s commitment to creating lessons worth sharing is an '
                    'extension of TED’s mission of spreading great ideas. Within '
                    'TED-Ed’s growing library of TED-Ed animations, you will find '
                    'carefully curated educational videos, many of which represent '
                    'collaborations between talented educators and animators '
                    'nominated through the TED-Ed website (ed.ted.com).  Want to '
                    'suggest an idea for a TED-Ed animation or get involved with '
                    'TED-Ed? Visit our website at: '
                    'http://ed.ted.com/get_involved.  Also, consider donating to '
                    'us on Patreon! By doing so, you directly support our mission '
                    'and receive some pretty awesome rewards: '
                    'https://www.patreon.com/teded  For more information on using '
                    'TED for commercial purposes (e.g. employee learning, in a '
                    'film, or in an online course), please submit a Media Request '
                    'using this link: https://media-requests.ted.com/',
     'IndexLanguage': 'eng',
     'Language': 'eng',
     'Name': 'teded_en_all',
     'Publisher': 'Kiwix',
     'Scraper': 'youtube2zim 2.1.13',
     'Tags': '_category:ted;_videos:yes',
     'Title': 'TED-Ed'}



```python
# Write a new mapping from categories to vides (with some removed)
print('Creating a new mapping from Categories to videos within each category.')
outstr = ''
for cat in zim_category_js:
    outstr += 'var json_%s = [\n'%cat
    for video in range(len(zim_category_js[cat])):
        if zim_category_js[cat][video].get('id','') in wanted_ids:
            outstr += json.dumps(zim_category_js[cat][video],indent=1)
            outstr += ','
    outstr = outstr[:-1]
    outstr += '];\n'
with open(OUTPUT_DIR + '/assets/data.js','w') as fp:
    fp.write(outstr)
    

```

    Creating a new mapping from Categories to videos within each category.



```python

```


```python
    playlist = 'PLs2auPpToJpb6MeiaKEIpkdSWeBVgvC_p'
    CHANNEL = 'UCljl2cmQMgzlTkeJqJier7g'
```

mk_zim_cmd = """
zimwriterfs --language=eng\
            --welcome=A/home.html\
            --favicon=I/favicon.jpg\
            --title=teded_en_%s\
            --description=\"TED-Ed Videos from YouTube Channel\"\
            --creator='Youtube Channel “TED-Ed”'\
            --publisher=IIAB\
            --name=TED-Ed\
             %s %s.zim"""%(PROJECT_NAME,OUTPUT_DIR,PROJECT_NAME)
#with open(HOME + '/zimtest/' + PROJECT_NAME + '-zimwriter-cmd.sh','w') as fp:
#    fp.write(mk_zim_cmd)
#### Jupyter Lab and OpenZim Environments Conflict
* The "Youtube2zim" path seems to create functioning ZIMS. But it involves a huge cost in time and patience interacting with the Google API.
* But it provides a simple model in the 'Run' subroutine of scraper.py. Making a zim is really just a subroutine call.
* So the current strategy is a pass off the environment variables from the jupyter virtual environment to the youtube2zim virtual environment to "zimming" up the modified/shrunken disk tree.


```python
print('Creatng a new ZIM and Indexing it')

from pathlib import Path
from zimscraperlib.zim import make_zim_file
from glob import glob
from datetime import datetime

original_name = glob("%s/*.zim"%(SOURCE_DIR))
fname = os.path.basename(original_name[0].replace('all','top'))
print('fname:%s'%fname)
#sys.exit(1)

os.chdir(OUTPUT_DIR)
if not os.path.isfile(os.path.join(NEW_ZIM_DIR,fname)):
    make_zim_file(
        build_dir=Path(OUTPUT_DIR),
        fpath=Path(NEW_ZIM_DIR) / fname,
        name=fname,
        main_page= "home.html",
        favicon="favicon.jpg",
        title=meta_data['Title'],
        description=meta_data['Description'],
        language=meta_data['Language'],
        creator=meta_data['Creator'],
        publisher="Internet In A Box",
        tags=meta_data['Tags'],
        scraper=meta_data['Scraper'],
    )

```

    Creatng a new ZIM and Indexing it
    fname:teded_en_top_2021-01.zim



```python
# Dump the zim file to get the metadata accumulated during it's creation
cmd = f'zimdump dump --dir={PROOF_DIR} {NEW_ZIM_DIR}/{fname}'
subprocess.run(cmd,shell=True)

```




    CompletedProcess(args='zimdump dump --dir=/ext/zims/teded/proof /ext/zims/teded/new-zim/teded_en_top_2021-01.zim', returncode=0)




```python
with open(f'{PROOF_DIR}/M/Counter','r') as fp:
    counts = fp.read().split(';')
countdict = {}
for nibble in counts:
    nibble = nibble.split('=')
    countdict[nibble[0]] = nibble[1]
pprint(countdict)
    
```

    {'application/csv': '40',
     'application/javascript': '43',
     'application/json': '207',
     'application/octet-stream': '15',
     'application/x-shockwave-flash': '1',
     'font/sfnt': '6',
     'image/jpeg': '51',
     'image/png': '2',
     'image/svg+xml': '1',
     'image/webp': '838',
     'text/css': '6',
     'text/html': '859',
     'text/markdown': '1',
     'text/plain': '8',
     'video/webm': '857'}



```python
# Create a catalog fragment for this video
import uuid
import base64
uuidstr = str(uuid.uuid4())
CATALOG_FRAG_DIR = '/opt/iiab/iiab-content/catalogs/zim-cat-fragments'
WASABI_URL = 'https://s3.us-east-2.wasabisys.com'
# Maintain the order of the zim catalog
cat_keys = ['path','title','description','language','creator','publisher','tags','favicomMimeType',
           'favicon','date','articleCount','mediaCount','size','url','name','flavour']
outstr = '{"%s": {\n'%uuidstr
outstr += f'"path": "../library/zims/content/{fname}",\n'
outstr += f'"title": "{meta_data["Title"]}",\n'
outstr += f'"description": "{meta_data["Description"]}",\n'
outstr += f'"language": "{meta_data["Language"]}",\n'
outstr += f'"creator": "{meta_data["Creator"]}",\n'
outstr += f'"publisher": "Internet In A box",\n'
outstr += f'"tags": "{meta_data["Tags"]}",\n'
outstr += f'"faviconMimeType": "image/png",\n'
with open(PROJECT_DIR + '/favicon.jpg','rb') as fp:
    favi = fp.read()
b64 = base64.b64encode(favi)
outstr += f'"favicon": "{b64}",\n'
outstr += f'"date": "{meta_data["Date"]}",\n'
outstr += f'"articleCount": "{countdict["text/html"]}",\n'
outstr += f'"mediaCount": "{countdict["video/webm"]}",\n'
size = os.path.getsize(f'{NEW_ZIM_DIR}/{fname}')
outstr += f'"size": "{size}",\n'
outstr += f'"url": "{WASABI_URL}/{fname}",\n'
outstr += f'"name": "{meta_data["Name"]}",\n'
outstr += f'"flavour": ""\n'
outstr += '}}'
cat_fragment = '%s/%s'%(CATALOG_FRAG_DIR,fname.replace('.zim','.json'))
with open(cat_fragment,'w') as fp:
    fp.write(outstr)
print(outstr)
```

    {"0169b1cf-21d5-45ff-a0dc-bff139782220": {
    "path": "../library/zims/content/teded_en_top_2021-01.zim",
    "title": "TED-Ed",
    "description": "TED-Ed’s commitment to creating lessons worth sharing is an extension of TED’s mission of spreading great ideas. Within TED-Ed’s growing library of TED-Ed animations, you will find carefully curated educational videos, many of which represent collaborations between talented educators and animators nominated through the TED-Ed website (ed.ted.com).  Want to suggest an idea for a TED-Ed animation or get involved with TED-Ed? Visit our website at: http://ed.ted.com/get_involved.  Also, consider donating to us on Patreon! By doing so, you directly support our mission and receive some pretty awesome rewards: https://www.patreon.com/teded  For more information on using TED for commercial purposes (e.g. employee learning, in a film, or in an online course), please submit a Media Request using this link: https://media-requests.ted.com/",
    "language": "eng",
    "creator": "Youtube Channel “TED-Ed”",
    "publisher": "Internet In A box",
    "tags": "_category:ted;_videos:yes",
    "faviconMimeType": "image/png",
    "favicon": "b'/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAAwADADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD+b+iuz8EeGdD8VahPp2r+LIPDFw8lhbaSk1oLt9WvL6aWD7LArXNsFkjcQAfMxZrhM7UDMPUP+FH6G3iVPCkHxGiuNcjie4vNOTRV+1Wtr9nSaK4ki/tPaY5RPbjmQHFxGV3sGC/DZxx7wzkOOxGXZri8dhsVhcFPMa3LkmdYihHAUo05VsYsXhsBVwk8NRdWlSr1oV5U6GIq08NVnTxFSFKX9BcB/Ro8YPEzhrLeLeC8l4czXJc3z/D8K4CVbxD8PsqzKtxJjKuJpYHI5ZFm3E+DzuhmuYQweMxmXYCvl1PF5hlmExObYLDYnLMPXxtL58or2+L4S+F7zUbLSNO+JIvdRu9RXT/sy+HLiJo2QSm5cvJe+UTB5MpIMiK4jbD5Kl5dR+CdsYPECeGPHOneItc8LK7atoJsltLqIxxPK8G5NQuWjuGWJxAXgNvLIPJM0bHcOJeJvBvtaNGpmONw060KVRSxmQ59g6VKjXxdLA0MTiq2IyyNLB4SrjK9HDU8Xi5UMNKrUjBVrt8v0E/of+PrwWOx+E4W4ezelgK2Ows6WQ+JXhnnuOxuPy3JMbxHmGVZNl+WcX1cZn2c4LIcux+bYrJclp5hm9HBYStWll7jFc/hdFMjcOoYcggEHpkEAg4OMZB6U+vvj+ZU7pNappNPo00mmvJpprya7mv4d1Gw0fxJ4c1bU7lLTT9N1/Rr28uJD8sVta6hBNM23OXKxoxWNMu5ARQScH2qw+Jngdvjhq/jOPW4ptAuNCitIrqCC4nlaZLPSYWRrKCCS7jXzbWdFla3SM7V+dRIrV9pf8EadH8O61+22kfidfAqadpf7Nn7VfiSDU/iV4PsfH3gnw1q/hv4Qarq+jeMNe8I6ho3iCDWrLwnf28WuTWkei6jdzQWc0FpaXE0ywS/UHiTw54X/a60TxDc/GL9uf8AZY+NPwN/Zo+Efjv9qT4uR/sM/sb6J8CvjNbaX4Rt/DngrQdC0jUvFnwR+FGj6vL8QfEfxBttLsF1i91rQPDgs7jXNX0gTWumTw/J5/wblfEdbEYjH1cbTniuHMz4XqLDVqVOKy/NMbgsfiasVOhVaxca2AoxpVW5U4U5VFKjOUozj+1+Gfj5xn4UZfleV8N4Lh7E4bJ/FjhHxkw0s3wONxVWXFPBnD3EPDWVYWtLDZlg4TyStgOJcfUx2DjCniq2Kp4WpSx1ClTqUa35ej4reEl1TT7i4+J+taxa2er293c6RN4bghijtiJfKLSWug296q24dWgzLvm8iMMk6tJtxX8ffDDwxqXjnxb4cv8AWtf8UeMIZ44rSeyns9OsnnBZdzz2VqFtknCTSlpLm5cRLDFGodmr7E/bV8MfAXS/2EP+CcniT4B6f4pXw/4q8W/tytqmq/Ezw54I034tfb9H+Jfw2tT4T8c+JPAtvFo3jeHwbLcXdp4W8RWv2aym0TUIxBomg3Z1HT1/KPAHQAfhXyWH8HeG8O3GOYZ59Wq4ejg8dg6NbKMBhczwNDMsLm1PB46GW5DgpVKLxuDw9SrKjLD4itGn7OriZQbS/cMy+np4tZnCFWfCvhss1wOaY7PuHOIMdgOOOJM54R4hzDhXOOCsTnvDmI4t8SM/o4XMI8PZ7mmEwdPHUczyzL6uIWKwWU0a8IykyJSsaqTkgAZ6ZwAM45xnGakoor9ZP4kSskuyS77JLrq9tW7t7vVs98/Zp/aR+I/7KPxVtPjF8K4fBl14rtfC/jLwZJY/EDwjZ+OvCWpeG/H2iSeHvFGl6x4X1C5tLLVLfUdJlls3hupWtzFLLHPBcQyyRN9RRf8ABUH47aZqVlqPhL4O/sR/DqP+zfEHhrxXo/w1/Y8+F/gjQfin8PvFmizaF4n+FfxZ0vSSI/HPwz1y2ktr678LXklqsGu6RoWvaffWWpaPaSr+cNFAmkz6k/aC/a9+Kn7SHhD4SfDvxjoXwl8G/Dv4Ef8ACdQfCPwH8HfhlpPwz8L+C9M+Il/omqeI9HtLHTLu8m1Cyk1HQba/gutZutQ1uS/vNWvtU1jVLvUZJU+W6KKB2tsFFFFAH//Z'",
    "date": "2021-01-16",
    "articleCount": "859",
    "mediaCount": "857",
    "size": "10028131108",
    "url": "https://s3.us-east-2.wasabisys.com/teded_en_top_2021-01.zim",
    "name": "teded_en_all",
    "flavour": ""
    }}



```python
# Now parse the file we just created to validate the json
with open(cat_fragment,'r') as fp:
    json_str = fp.read()
frag_dict = json.loads(json_str)
```


```python
pprint(frag_dict)
```

    {'cf8bcdb2-037a-42db-8276-8bf2e85b682b': {'articleCount': '94',
                                              'creator': "Youtube Channel “C'est "
                                                         'pas sorcier”',
                                              'date': '2021-01-14',
                                              'description': 'Magazine télévisuel '
                                                             'de vulgarisation '
                                                             'scientifique destiné '
                                                             'aux enfants',
                                              'favicon': "b'/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAAwADADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD+xiiiiuc6Aoorzf4tfE7Rfg74D1f4g+ILDVdS0rRp9Kt7iz0VLSTUZX1fUrfTLdoFvbm0tisc9wjzeZOhEQYoHcBD5+bZrl2R5ZmGdZvjKOX5VlOCxOY5ljsQ5qhg8Dg6Uq+KxVZ06VeoqVCjCVSbhRqz5YvlpzfunoZTlWY57mmXZLk+DrZhmubY7DZbluBw6g6+Mx+NqxoYXC0VUq0Kbq160o04e0rUoczXNUgryXpFFfDH/DeXgM+Df+Fg/wDCtviePB3/AAlX/CEf23s8GmL/AISkaN/wkB0n7KPFJvvM/sf/AE37R9l+xiP939oM/wC6P0/8JPidovxi8BaP8QvD1hqum6TrU+qQW1nrUdpHqMbaTqNxpk7TLZXN3bBZZ7aR4fLuHJiKlwj5UfGcLeLHhxxtmccl4U4vyrPM1llKz6GAwkcyhXnksqqoQzSmsbk2XU6uBnWap08RSrVI1JKfs4zVOpKH2nFXhN4kcEZXLOuLOEc0yTKo5s8hnjsXPLKlCnnUaUq0srqvA51mNSljYUoudShUowlTi4+0lB1KcamTfftB/ALTNd8ZeFtS+OXwa07xP8Om0yP4g+G774p+A7TxB4Fk1qN5dHj8Y6JP4gTU/DMmqxxSPp0WtWtlJdhCIUZsKWXX7Q/7P1jbeJL2++O/wVsrLwbpd9rnjC8vPiv4AtbPwpo2maxD4e1LVvEt3ceIY7fQdOsNfuLfQry81WW0t7fWri30mSRdQnitn/nE+EnwgtrHwn+3/wDB7U/2FPi1L+21a/Ev9unxhb/tQ6j8GptH8J6t4F+Nv7WPgbxb8GfC2j/Ga81DRYvi9N8RtFk0LxRo1poF3q6eDPDvg/XhrXiDwBbw3d2nmfxY8G+IvH/wv+LOg/HD4D/tRfD3T7f4j+H/AImf2x8JP2aLv4/yfDjxLo/7XVj478MePtZ+CGu+E/BPgD4tfs0pHrWl+LfFnw38LaX4u17x3FeeOPEbafa3enXFlqP6H1trbTXTrZX31u/n31PzxaxctrNryv018uv4dD+p4fGf4OHWPh74dHxc+Fh8QfFzTm1f4T6EvxG8FtrPxS0lIhO2qfDfS11w33jvTRCwlF94Vg1a1dc+XK7Kyj5y+Pfjz4QftA/AL4uaL8Mvj9+z7rMfgyXw/qPj3xEPjR4An8K/Dyx0fXrfUby5+IOuaTrWq23guEwafdxwT+IlsIZbmNrcOHDAfyr+BPgR8bvE3i/9lOfxN+wr4q+FfxV+KXh//gmJc/s3/wDCA/s/+OdL+H/wM079n39vb4zfEL9onV/7d1+PxBcfssQ698ONU0n4x+KPBXinxNoDNY+OV02xtGsY7PSbXwf4M/shfHbQvht8Wda+IX7OvxGn0q68D/AH4g6X4G8Ffsz+JNKk8f8A7Onw/wD+CwHjT4iftH+G/jTpMWg3Gr/Gn42eFdJ0bwv408I6Fqli2sa9+z3qlpDonhzUdI0C3uJ/H4j4fy7irh/POGc39vLK+IMpx+S5lHC1/q+IlgcyoTwmLjh8TGFV0KzozkqdeNKo6c7TUJWSfscN8QZjwrxDknE2U+wWZ8PZtgM6y54qh9awqx2W4iOLwrxGGdSkq9H2sIupRlVpqpC8XUhrJf0DXvg24034TWvwtvvjN+y9Z+Fr7X7L9piz+Itz8dPD9v4TuPhxqHhqP4Z6f46h8Uyxx+FZPh/feLp4PBlnr8eptPd+OLiDRbe3kt3N2P0T/ZQ+I/wV8EfDf4XfByX9of8AZ28UePvEUev614Q0PwR8bvh74nvPG2ka14l125sNQ8E2VrrkeqeLLNzaX9qbrQtOvbdr3TtRtYZJpbK4CfzHft5/CWw+IuhfFLxZ+yj+xF8cPgZ8D/Ff/BPDw5H4B+GOpfs5eKHv7XUpv+Cyfw++JOt30Xwj02LxC1lJ4y8O2et/Gqw+Ddy+l6+/gG7NzqPhLw1p95NFbXfiF8BfiB8SP25P2Yfi9onw01jXf2cfDL/8ErB8RviT4W/YF1L9nL4hafL4X/aG/aFurnxp8IfhjcaRcT/s4+HtC8fWnhkfHzwT4djvtQuvhv4utvFGo31rYCG41H8k8Nvo9cCeF/ED4nyHFcR4rNIcPS4SwbzfNoYvD4LhqnXhisLlsMPTy/Cxr1sPXjVccwrVfrM415wnSajFn634l/SG468UuHo8M5/hOG8JlcuII8WYz+yMonhMTjeI5UKmFxGYzxFXMsW6NHE0pU1LL6FL6tTlQhOFW8pRP7RN74VfMk2oWMa+Y+2Mv9/y13Yj3/x7Au85LZzThLMu3bNMpRzKhWaVSkrAhpUIcFJGBIaRcOQSCSKjor9zPwsf5kmJF82XbKQ0y+bJtmYEsGmXdtlYMSwaQMQxLA55pfOnJ3GectvWTcZ5SfMQbY5M78+bGoCxyffRQFVgOKjooAkE06klZ51YuZSyzShjKw2tKWDgmVlJVpCS7KSpYgkFfPuCcm4uCcscm4mJJkUJISS+SZEASQ9XQBHyoAqKigD/2Q=='",
                                              'faviconMimeType': 'image/png',
                                              'flavour': '',
                                              'language': 'fra',
                                              'mediaCount': '92',
                                              'name': 'cest-pas-sorcier_fr_all',
                                              'path': '../library/zims/content/cest-pas-sorcier_fr_top_2021-01.zim',
                                              'publisher': 'Internet In A box',
                                              'size': '9877741846',
                                              'tags': 'youtube;_videos:yes',
                                              'title': "C'est pas sorcier",
                                              'url': 'https://s3.us-east-2.wasabisys.com/cest-pas-sorcier_fr_top_2021-01.zim'}}



```python

```
