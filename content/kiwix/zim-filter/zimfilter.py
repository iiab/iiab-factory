#!/usr/bin/env python3
# coding: utf-8

# ## Modifying ZIM Files
# 
# #### The Larger Picture
# * Kiwix scrapes many useful sources, but sometimes the chunks are too big for IIAB.
# * Using the zimdump program, the highly compressed ZIM files can be flattened into a file tree, modified, and then re-packaged as a ZIM file.
# * This Notebook has a collection of tools which help in the above process.
# 

# #### How to Use this notebook
# * There are install steps that only need to happen once. The cells containing these steps are set to "Raw" in the right most dropdown so that they do not execute automatically each time the notebook starts.
# * The following bash script successfully installed zimtools on Ubuntu 20.04.It only needs to be run once. I think it's easier to do it from the command line, with tab completion. In a terminal, do the following:
# 
# ```
# cd /opt/iiab/iiab-factory/content/kiwix/generic/ 
# sudo ./install-zim-tools.sh
# ```

# * **Some conventions**: Jupyter does not want to run as root. We will create a file structure that exists in the users home directory -- so the application will be able to write all the files it needs to function.
# ```
# <PREFIX>
# ├── new-zim
# ├── tree
# ├── working
# └── zim-src
# ```
# In general terms, this program will dump the zim data into "tree", modify it, gather additional data into "working"
# , and create a ZIM file in "new_zim"
# * For testing purposes, the user will need to link from the server's document root to her home directory (so that the nginx http server in IIAB will serve the candidate in "tree):
# 
# ```
# cd
# mkdir -p zimtest
# ln -s /home/<user name>/zimtest /library/www/html/zimtest 
# ```
# 

# #### Installation Notes to myself
# * Installing on Windows 10 insider preview WSL2. Used https://towardsdatascience.com/configuring-jupyter-notebook-in-windows-subsystem-linux-wsl2-c757893e9d69.
# * First tried installing miniconda, and then installing jupyterlab with it.
# * Wanted VIM bindings to edit cells, but jupyterlab version installed by conda was too old for jupyter-vim extenion. Wound up deleting old version with conda, and used pip to install both.
# * Jupyterlab seems to make the current directory its root. I created a notebook directory, and aways start jupyter lab from my home directiry
# * Discovered that I could enable writing by non-root group in the iiab-factory repo, and continue to use git for version control. Needed to make symbolic link from ~/miniconda to iiab-factory.
# * Reminder: Start jupyterlab in console via "jupyter lab --no-browser", and then pasteing the html link displayed into my browser.

# #### Declare input and output
# * The ZIM file names tend to be long and hard to remember. The PROJECT_NAME, initialized below, is used to create path names. All of the output of the zimdump program is placed in \<home\>/zimtest/\<PROJECT_NAME\>/tree. All if the intermediate downloads, and data, are placed in \<home\>/zimtest/\<PROJECT_NAME\>/working. If you use the IIAB Admin Console to download ZIMS, you will find them in /library/zims/content/.

# In[5]:


# -*- coding: utf-8 -*-
import os,sys
import json
import youtube_dl
import pprint as pprint
from types import SimpleNamespace
import subprocess

# Fetch the config from repo or passed parameter
print('Setting up config for %s'%sys.argv[0])
FACTORY_REPO = '/opt/iiab/iiab-factory'
# Get the config (ipython has lots of parameters) 
if len(sys.argv) > 2: 
    config_file = FACTORY_REPO + '/content/kiwix/ted-tools/default_filter.json'
else:
    config_file = sys.argv[1]
print('Config file: %s'%config_file)
with open(config_file,'r') as fp:
    cfg_json = json.loads(fp.read())
cfg = SimpleNamespace(**cfg_json)    

# Declare a short project name (ZIM files are often long strings
#PROJECT_NAME = 'ted-kiwix'
PROJECT_NAME = cfg.PROJECT_NAME
#PREFIX = os.environ.get('ZIM_PREFIX','/ext/zims')
PREFIX = cfg.PREFIX
CACHE_DIR = PREFIX + '/youtube/cache'
if not os.path.isdir(CACHE_DIR):
   os.makedirs(CACHE_DIR)
TARGET_SIZE =cfg.TARGET_SIZE  #10GB
# The rest of the paths are computed and represent the standard layout
# Jupyter sets a working director as part of it's setup. We need it's value
HOME = os.environ['HOME']
WORKING_DIR = PREFIX + '/' + PROJECT_NAME + '/working'
PROJECT_DIR = PREFIX + '/' + PROJECT_NAME + '/tree'
OUTPUT_DIR = PREFIX + '/' + PROJECT_NAME + '/output_tree'
SOURCE_DIR = PREFIX + '/' + PROJECT_NAME + '/zim-src'
NEW_ZIM_DIR = PREFIX + '/' + PROJECT_NAME + '/new-zim'
dir_list = ['output_tree','tree','../youtube/cache/video_json','zim-src','new-zim']
for f in dir_list: 
    if not os.path.isdir(PREFIX + '/' + PROJECT_NAME +'/' + f):
       os.makedirs(PREFIX + '/' + PROJECT_NAME +'/' + f)

# Input the full path of the downloaded ZIM file
zim_path_contents = os.listdir(SOURCE_DIR)
if zim_path_contents:
    ZIM_PATH = SOURCE_DIR + '/' + zim_path_contents[0]
else:
    ZIM_PATH = '%s/%s/zim-src/teded_en_all_2021-01.zim'%(PREFIX,PROJECT_NAME,) 
# abort if the input file cannot be found
if not os.path.exists(ZIM_PATH):
    print('%s path not found. Quitting. . .'%ZIM_PATH)
    exit


# In[7]:


print('This is the PREFIX:%s'%PREFIX)


# In[8]:


# First we need to get a current copy of the script
cmd = '/bin/cp %s/content/kiwix/de-namespace.sh %s'%(cfg.FACTORY_REPO,PREFIX)
subprocess.run(cmd,shell=True)


# In[13]:


# The following command will zimdump to the "tree" directory
#  Despite the name, removing namespaces seems unnecessary, and more complex
# It will return without doing anything if the "tree' is not empty
print('Using zimdump to expand the zim file to %s'%PROJECT_DIR)
progname = PREFIX + '/de-namespace.sh'
cmd = "%s %s %s"%(progname,ZIM_PATH,PROJECT_NAME)
print('command:%s'%cmd)
subprocess.run(cmd,shell=True)


# * The next step is a manual one that you will need to do with your browser. That is: to verify that after the namespace directories were removed, and all of the html links have been adjusted correctly. Point your browser to <hostname>/zimtest/\<PROJECT_NAME\>/tree.
# * If everything is working, it's time to go fetch the information about each video from youtube.

# In[14]:


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


# #### Playlist Navigation to Videos
# * On the home page there is a drop down selector which lists about 70 cateegories (or playlists).
# * The value from that drop down is used to pick an entry in "-/assets/data.js", which in turn specifies the playlist of yourtube ID"s that are displayed when a selection is made.

# In[15]:


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


# #### The following Cell is subroutines and can be left minimized

# In[16]:


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


# In[17]:


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


# #### Create a sqlite database which collects Data about each Video
# * We've already downloaded the data from YouTube for each Video. So get the items that are interesing to us. Such as size,date uploaded to youtube,view count

# In[21]:


def initialize_db():
    sql = 'CREATE TABLE IF NOT EXISTS video_info ('            'yt_id TEXT UNIQUE, zim_size INTEGER, view_count INTEGER, age INTEGER, '            'views_per_year INTEGER, upload_date TEXT, duration TEXT, '            'height INTEGER, width INTEGER,'            'bit_rate TEXT, format TEXT, '            'average_rating REAL,slug TEXT,title TEXT)'
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
        db.c.execute(sql,[yt_id,vsize,view_count,round(age),views_per_year,upload_date,                           duration,v_height,v_width,bit_rate,v_format,average_rating,slug,title, ])
    db.conn.commit()
    print(yt_id,vsize,view_count,views_per_year,upload_date,                           duration,bit_rate,v_format,average_rating,slug,round(age))

sqlite_db = WORKING_DIR + '/zim_video_info.sqlite'
#!sqlite3 {sqlite_db} '.headers on' 'select * from video_info limit 2'
# #### Select the cutoff using view count and total size
# * Order the videos by view count. Then select the sum line in the that has the target sum.

# In[22]:


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

sql = 'select slug,zim_size,views_per_year,view_count,duration,upload_date,'       'bit_rate from video_info order by views_per_year desc'
tot_sum = 0
db.c.execute(sql)
rows = db.c.fetchall()
row_list = []
boundary_views_per_year = 0
for row in rows:
    tot_sum += row['zim_size']
    row_list.append([row['slug'][:60],human_readable(row['zim_size']),                              human_readable(tot_sum),human_readable(row['view_count']),                              human_readable(row['views_per_year']),                              row['upload_date'],row['duration'],row['bit_rate']])
    if tot_sum > TARGET_SIZE and boundary_views_per_year == 0:
        boundary_views_per_year = row['views_per_year']
sql = 'select slug,zim_size,views_per_year,view_count,duration,upload_date,'       'format,width,height,bit_rate from video_info order by views_per_year desc'
db.c.execute(sql)
rows = db.c.fetchall()
print('%60s %6s %6s %6s %6s %8s %8s'%('Name','Size','Sum','Views','Views','Date  ','Duration'))
print('%60s %6s %6s %6s %6s %8s %8s'%('','','','','/ yr','',''))
tot_sum = 0
for row in rows:
    tot_sum += row['zim_size']
    print('%60s %6s %6s %6s %6s %8s %8s'%(row['slug'][:60],human_readable(row['zim_size']),                              human_readable(tot_sum),human_readable(row['view_count']),                              human_readable(row['views_per_year']),                              row['upload_date'],row['duration']))
#df = pd.read_sql(sql,db.conn)
#df = pd.DataFrame(row_list,columns=['Name','Size','Sum','Views','Views','Date','Duration','Bit Rate'])
#display(df)


# * Now determine the video ID's that we want in our new zim

# In[23]:


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

wanted_ids
# * Now let's start building up the output directory
# 

# In[24]:


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


# In[26]:


# Copy the videos selected by the wanted_ids list to output file
import shutil
for f in wanted_ids:
    if not os.path.isdir(os.path.join(OUTPUT_DIR,'videos',f)):
        os.makedirs(os.path.join(OUTPUT_DIR,'videos',f))
        src = os.path.join(PROJECT_DIR,'videos',f)
        dest = os.path.join(OUTPUT_DIR,'videos',f)
        shutil.copytree(src,dest,dirs_exist_ok=True)


# In[27]:


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

wanted_ids
# In[28]:


# There are essential files that are needed in the zim
needed = ['/favicon.jpg','/home.html','/profile.jpg']
for f in needed:
    cmd = '/bin/cp %s %s'%(PROJECT_DIR  + f,OUTPUT_DIR)
    subprocess.run(cmd,shell=True)


# In[29]:


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
    


# In[30]:


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
    


# In[ ]:





# In[31]:


playlist = 'PLs2auPpToJpb6MeiaKEIpkdSWeBVgvC_p'
CHANNEL = 'UCljl2cmQMgzlTkeJqJier7g'

# Create a template for a script to run zimwriterfs
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
# #### Jupyter Lab and OpenZim Environments Conflict
# * The "Youtube2zim" path seems to create functioning ZIMS. But it involves a huge cost in time and patience interacting with the Google API.
# * But it provides a simple model in the 'Run' subroutine of scraper.py. Making a zim is really just a subroutine call.
# * So the current strategy is a pass off the environment variables from the jupyter virtual environment to the youtube2zim virtual environment to "zimming" up the modified/shrunken disk tree.

# In[33]:


print('Creatng a new ZIM and Indexing it')

from pathlib import Path
from zimscraperlib.zim import make_zim_file

period = datetime.now().strftime("%Y-%m")
fname = f"{PROJECT_NAME}_{period}"
print('fname:%s'%fname)
#sys.exit(1)

os.chdir(OUTPUT_DIR)
make_zim_file(
    build_dir=Path(OUTPUT_DIR),
    fpath=Path(NEW_ZIM_DIR),
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


# In[ ]:




