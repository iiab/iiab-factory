### Using Openzim Youtube2zim program
* This program is written by Kiwix and has a variety of methods for specifying which videos to include in a ZIM file. Unfortunately, a flat file of youtube ID's is not one of them. But one of the input specifications that is available is to specify a "Youtube Playlist".
* Getting permission to write a playlist from a python program is a task.
    1. The written playlist can only be written to by a user who has a google account, and who also owns a Youtube Channel.
    2. with proper credentials, the owner can create a playlist of up to 5000 videos in her own channel.
    3. Writing to youtube requires an oauth2 credential. The steps I found necessary:
        1. Go to "console.developer.google.com" to create a project.
        2. Within that project create a key (for reading public data) and a oauth2 credential for writing.
        3. The credential needs to specify a callback where google can return a software key which includes the permission that the owner of a Youtube channel gives to the python program. The callback I used was a flask program at iiab-factory/content/kiwix/ted-tools/flask_oauth_youtuve.py. And the URL created by this flask program needs to be specified to google during the process of creating the oauth2 credential as "http://localhost:8088/oauth2callback".
        4. The flask program writes a file in the current directory "zim_playbook_oauth_credentials".
* Very useful:  https://github.com/youtube/api-samples/tree/master/python


```python
# -*- coding: utf-8 -*-
# This cell defines GLOBALS and the ENV

import os,sys
import json

PREFIX = os.environ.get('ZIM_PREFIX','/ext/zims')
# Declare a short project name (ZIM files are often long strings
#PROJECT_NAME = 'ted-kiwix'
PROJECT_NAME = 'youtube'
PREFIX = os.environ.get('ZIM_PREFIX','/ext/zims')
TARGET_SIZE =10000000000  #10GB
# Input the full path of the downloaded ZIM file
ZIM_PATH = '%s/%s/working/wanted_list.csv'%(PREFIX,PROJECT_NAME,) 
# The rest of the paths are computed and represent the standard layout
# Jupyter sets a working director as part of it's setup. We need it's value
HOME = os.environ['HOME']
WORKING_DIR = PREFIX + '/' + PROJECT_NAME + '/working'
PROJECT_DIR = PREFIX + '/' + PROJECT_NAME + '/tree'
OUTPUT_DIR = PREFIX + '/' + PROJECT_NAME + '/output_tree'
SOURCE_DIR = PREFIX + '/' + PROJECT_NAME + '/zim-src'

# Create the directory structure for this project
dir_list = ['output_tree','tree','working/video_json','zim-src'] 
for f in dir_list:
    if not os.path.isdir(PREFIX + '/' + PROJECT_NAME +'/' + f): os.makedirs(PREFIX + '/' + PROJECT_NAME +'/' + f) 
# abort if the input file cannot be found
if not os.path.exists(ZIM_PATH):
    print('%s path not found. Quitting. . .'%ZIM_PATH)
    exit

```


```python
# This cell creates an authenticated youtube object which has methods described in:
#   in https://googleapis.github.io/google-api-python-client/docs/dyn/youtube_v3.html

import google.oauth2.credentials
import googleapiclient.discovery

# The User validated google credentials are in my home directory
home = os.environ['HOME']
with open("%s/zim_playbook_oauth_credentials"%home,'r') as fp:
    credentials = json.loads(fp.read())
    
# Load credentials from file
credentials = google.oauth2.credentials.Credentials(**credentials)
 
youtube = googleapiclient.discovery.build(
    'youtube', 'v3', credentials=credentials)

channel = youtube.channels().list(mine=True, part='snippet').execute()

# check that the authentication worked
#print(json.dumps(channel,indent=2))
```


```python
# Playlist id for youtube2zim
CURRENT_PLAYLIST_ID = "PLs2auPpToJpbDRe9sh5nbeXRviOI4HpAL"
#PLs2auPpToJpb0ttyGab3c5h5XUn7dXE-9
def add_playlist(youtube):
  body = dict(
    snippet=dict(
      title="youtube2zim",
      description="This is a temporary Playslist which is used as source for the Openzim 'youtube2zim' program."
    ),
    status=dict(
      privacyStatus='public'
    ) 
  ) 
  playlists_insert_response = youtube.playlists().insert(
    part='snippet,status',
    body=body
  ).execute()
  print('New playlist ID: %s' % playlists_insert_response['id'])
#add_playlist(youtube)
```


```python
def get_my_playlists():
    playlists_list_response = youtube.playlists().list(
        part='contentDetails,snippet',
        mine = True
        ).execute()
    playlists = []
    for item in playlists_list_response['items']:
        playlists.append([item['id'],item['snippet']['title'],item['contentDetails']['itemCount']])
    return playlists


my_playlists = get_my_playlists()
for pl in my_playlists:
    print(pl)

```

    ['PLs2auPpToJpb0ttyGab3c5h5XUn7dXE-9', 'youtube2zim', 0]
    ['PLs2auPpToJpbDRe9sh5nbeXRviOI4HpAL', 'youtube2zim', 0]
    ['PLs2auPpToJpb6MeiaKEIpkdSWeBVgvC_p', 'top-ted', 0]



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

db = Sqlite(CACHE_DIR + '/zim_video_info.sqlite')
TEST_VIDEO_ID = 'zzu2POfYv0Y'

def get_data_from_video_id(video_id):
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    )
    response = request.execute()
    #print(json.dumps(response,indent=2))
    return response
    
def get_title_from_video_id(video_id):
    # A daatabase lookup is much faster than round trip to google
    sql = 'select * from video_info where yt_id = ?'
    result = db.c.execute(sql,(video_id,))
    rows = result.fetchall()
    if len(rows) == 1:
        print('resolving title via sqlite')
        return rows[0]['title']
    
    # Let google look up the title`
    data = get_data_from_video_id(video_id)
    return data['items'][0]['snippet']['title']

test_title = get_title_from_video_id(TEST_VIDEO_ID)
print(test_title)
    
```

    resolving title via sqlite
    Logarithms, Explained - Steve Kelly



```python
def add_video_to_playlist(video_id,playlist_id):
    body={
      "snippet": {
        "playlistId": playlist_id,
        "position": 0,
        "resourceId": {
          "kind": "youtube#video",
          "videoId": video_id
        }
      } 
    }
    # print(json.dumps(body,indent=2))
    request = youtube.playlistItems().insert(part="snippet",body=body)
    response = request.execute()
    #print(json.dumps(response,indent=2))
        
def delete_video_from_playlist(video_id,playlist_id):
    # print(json.dumps(body,indent=2))
    request = youtube.playlistItems().delete(id=video_id)
    response = request.execute()
    print(json.dumps(response,indent=2))

# add_video_to_playlist(TEST_VIDEO_ID,CURRENT_PLAYLIST_ID)
```


```python

```


```python

```


```python
def get_my_uploads_list():
  # Retrieve the contentDetails part of the channel resource for the
  # authenticated user's channel.
  channels_response = youtube.channels().list(
    mine=True,
    part='contentDetails'
  ).execute()

  for channel in channels_response['items']:
    # From the API response, extract the playlist ID that identifies the list
    # of videos uploaded to the authenticated user's channel.
    return channel['contentDetails']['relatedPlaylists']['uploads']

  return None

```


```python
def get_list_from_playlist_id(playlist_id):
  # Retrieve the list of videos uploaded to the authenticated user's channel.
  playlistitems_list_request = youtube.playlistItems().list(
    playlistId=playlist_id,
    part='snippet',
    maxResults=50
  )
  pl_list = {}
  while playlistitems_list_request:
    playlistitems_list_response = playlistitems_list_request.execute()

    for playlist_item in playlistitems_list_response['items']:
      title = playlist_item['snippet']['title']
      video_id = playlist_item['snippet']['resourceId']['videoId']
        
      # create a dictionary which the video_id as key and playlist_id as value
      pl_list[video_id] = playlist_item['id']
      # 

    playlistitems_list_request = youtube.playlistItems().list_next(
      playlistitems_list_request, playlistitems_list_response)
  return pl_list

try:
    playlist_ids = get_list_from_playlist_id(CURRENT_PLAYLIST_ID)
    print(CURRENT_PLAYLIST_ID)
    for video_id in playlist_ids.keys():
        print('video_id:%s, playlistItem_id:%s'%(video_id,playlist_ids[video_id]))
        pass
except HttpError as e:
    print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
    print('Probably the %s playlist is does not exist'%CURRENT_PLAYLIST_ID)

```

    PLs2auPpToJpbDRe9sh5nbeXRviOI4HpAL
    video_id:zzu2POfYv0Y, playlistItem_id:UExzMmF1UHBUb0pwYkRSZTlzaDVuYmVYUnZpT0k0SHBBTC41NkI0NEY2RDEwNTU3Q0M2



```python
def delete_video_from_playlist(playlist_id):
    response = youtube.playlistitems().delete(id=playlist_id.execute()
    print(response)
```


```python
# This cell synchronizes a playlist with wanted id's in ZIM_PATH file
CACHE_DIR = '/home/ghunt/zimtest/teded/working'

# First delete any vidoes in the playlist that are not wanted
def sync_playlist_with_wanted(playlist_id):
    video_to_playlist_map = get_list_from_playlist_id(playlist_id)
    print('video_to_playlist_map length:%s'%len(video_to_playlist_map))
    with open(ZIM_PATH,'r') as fp:
        wanted = fp.readlines()
        print('length of wanted: %s'%len(wanted))
        for video_id in video_to_playlist_map.keys():
            if video_id not in wanted:
                item_id = video_to_playlist_map[video_id]
                response = youtube.playlistItems().delete(id=item_id).execute()
        added = 1
        for line in wanted:
            if added % 100 == 0:
                print('Added %s'%added)
            id = line.strip().split(',')[0]
            if id not in video_to_playlist_map.keys():
                add_video_to_playlist(id,CURRENT_PLAYLIST_ID)
                
sync_playlist_with_wanted(CURRENT_PLAYLIST_ID)
```


    ---------------------------------------------------------------------------

    HttpError                                 Traceback (most recent call last)

    <ipython-input-20-44e67489662e> in <module>
         21                 add_video_to_playlist(id,CURRENT_PLAYLIST_ID)
         22 
    ---> 23 sync_playlist_with_wanted(CURRENT_PLAYLIST_ID)
    

    <ipython-input-20-44e67489662e> in sync_playlist_with_wanted(playlist_id)
          4 # First delete any vidoes in the playlist that are not wanted
          5 def sync_playlist_with_wanted(playlist_id):
    ----> 6     video_to_playlist_map = get_list_from_playlist_id(playlist_id)
          7     print('video_to_playlist_map length:%s'%len(video_to_playlist_map))
          8     with open(ZIM_PATH,'r') as fp:


    <ipython-input-8-5ea4cae9c6c8> in get_list_from_playlist_id(playlist_id)
          8   pl_list = {}
          9   while playlistitems_list_request:
    ---> 10     playlistitems_list_response = playlistitems_list_request.execute()
         11 
         12     for playlist_item in playlistitems_list_response['items']:


    ~/miniconda3/lib/python3.9/site-packages/googleapiclient/_helpers.py in positional_wrapper(*args, **kwargs)
        132                 elif positional_parameters_enforcement == POSITIONAL_WARNING:
        133                     logger.warning(message)
    --> 134             return wrapped(*args, **kwargs)
        135 
        136         return positional_wrapper


    ~/miniconda3/lib/python3.9/site-packages/googleapiclient/http.py in execute(self, http, num_retries)
        918             callback(resp)
        919         if resp.status >= 300:
    --> 920             raise HttpError(resp, content, uri=self.uri)
        921         return self.postproc(resp, content)
        922 


    HttpError: <HttpError 403 when requesting https://youtube.googleapis.com/youtube/v3/playlistItems?playlistId=PLs2auPpToJpbDRe9sh5nbeXRviOI4HpAL&part=snippet&maxResults=50&alt=json&pageToken=CGQQAA returned "The request cannot be completed because you have exceeded your <a href="/youtube/v3/getting-started#quota">quota</a>.". Details: "The request cannot be completed because you have exceeded your <a href="/youtube/v3/getting-started#quota">quota</a>.">



```python

```


```python

```
