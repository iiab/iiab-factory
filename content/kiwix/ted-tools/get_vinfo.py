#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os,sys
from pprint import pprint
from pymediainfo import MediaInfo

class Zim_tools(object):
    def __init__(self,ted_root):
        self.ted_root = ted_root

    def mediainfo_dict(self,path):
        if path[0] != "/":
            path = os.path.join(self.ted_root,path)
        minfo =MediaInfo.parse(path)
        return minfo.to_data()

    def select_info(self,path):
        if path[0] != "/":
            path = os.path.join(self.ted_root,path)
        data = self.mediainfo_dict(path)
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
                rtn['v_rate'] = track['bit_rate']
                rtn['v_frame_rate'] = track['frame_rate']
        return rtn
        
if __name__ == "__main__":
    ted_path = '/library/www/html/zimtest/teded/tree'
    zt = Zim_tools(ted_path)
    relative_path = 'videos/ZZZ6QB5TSfk/video.webm'
    pprint(zt.select_info(relative_path))
