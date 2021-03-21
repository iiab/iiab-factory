#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os,sys
from  googleapiclient.discovery import build
import googleapiclient.errors
import json

if len(sys.argv) < 2:
    print('Please specify a path to a file of channel ids')
    sys.exit(1)
# Check to see if it is readable
if not os.path.isfile(sys.argv[1]):
    print('%s file not found'%sys.argv[1])
    sys.exit(1)

api_key = os.environ['API_KEY']

def main():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    youtube = build(api_service_name, api_version, developerKey=api_key)

    with open(sys.argv[1],'r') as fp:
        lines = fp.readlines()
        for line in lines:
            request = youtube.playlists().list(
                part="contentDetails,snippet",
                #channelId=sys.argv[1]
                channelId=line.strip()
            )
            try:
                response = request.execute()
            except Exception as e:
                print('Exception %s'%e)
                continue


            #print(json.dumps(response,indent=2))
            #sys.exit(1)
            print('\n%24s%s'%('Channed ID', '     Channel Title'))
            print('%60s %36s %4s %s'%("Title","Playlist ID","#","Date"))
            print('%s %s'%(line.strip(),response['items'][0]['snippet']['channelTitle']))
            for item in response['items']:
                print('%60s %36s %4s %s'%(item['snippet']['title'],item['id'],item['contentDetails']['itemCount'],item['snippet']['publishedAt'][:10]))
    

if __name__ == "__main__":
    main()
