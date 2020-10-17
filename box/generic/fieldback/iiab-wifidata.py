#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Create a mysql database for hostapd client connection information


import os
import sys
#import mysql.connector as mariadb
import sqlite3
import datetime
import time
import hashlib
from subprocess import Popen, PIPE
#import pdb; pdb.set_trace()


# Globals
db = object
ZERO = datetime.timedelta(0)
EPOCHORDINAL = datetime.datetime.utcfromtimestamp(0).toordinal()

class tzlocal(datetime.tzinfo):
    global tz_offset

    _std_offset = datetime.timedelta(seconds=-time.timezone)
    if time.daylight:
        _dst_offset = datetime.timedelta(seconds=-time.altzone)
    else:
        _dst_offset = _std_offset
    tz_offset = _std_offset.total_seconds()

    def utcoffset(self, dt):
        if self._isdst(dt):
            return self._dst_offset
        else:
            return self._std_offset

    def dst(self, dt):
        if self._isdst(dt):
            return self._dst_offset-self._std_offset
        else:
            return ZERO

    def tzname(self, dt):
        return time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        # We can't use mktime here. It is unstable when deciding if
        # the hour near to a change is DST or not.
        # 
        # timestamp = time.mktime((dt.year, dt.month, dt.day, dt.hour,
        #                         dt.minute, dt.second, dt.weekday(), 0, -1))
        # return time.localtime(timestamp).tm_isdst
        #
        # The code above yields the following result:
        #
        #>>> import tz, datetime
        #>>> t = tz.tzlocal()
        #>>> datetime.datetime(2003,2,15,23,tzinfo=t).tzname()
        #'BRDT'
        #>>> datetime.datetime(2003,2,16,0,tzinfo=t).tzname()
        #'BRST'
        #>>> datetime.datetime(2003,2,15,23,tzinfo=t).tzname()
        #'BRST'
        #>>> datetime.datetime(2003,2,15,22,tzinfo=t).tzname()
        #'BRDT'
        #>>> datetime.datetime(2003,2,15,23,tzinfo=t).tzname()
        #'BRDT'
        #
        # Here is a more stable implementation:
        #
        timestamp = ((dt.toordinal() - EPOCHORDINAL) * 86400
                     + dt.hour * 3600
                     + dt.minute * 60
                     + dt.second)
        return time.localtime(timestamp+time.timezone).tm_isdst

    def __eq__(self, other):
        if not isinstance(other, tzlocal):
            return False
        return (self._std_offset == other._std_offset and
                self._dst_offset == other._dst_offset)
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "%s()" % self.__class__.__name__

    __reduce__ = object.__reduce__

class tzutc(datetime.tzinfo):

    def utcoffset(self, dt):
        return ZERO
     
    def dst(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def __eq__(self, other):
        return (isinstance(other, tzutc) or
                (isinstance(other, tzoffset) and other._offset == ZERO))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "%s()" % self.__class__.__name__

    __reduce__ = object.__reduce__

# get a global instance of the tzlocal class
tz = tzlocal()
tzu = tzutc()
UTC2LOCAL = datetime.datetime.now(tz) - datetime.datetime.now(tzu)
UTC2LOCALSECONDS = UTC2LOCAL.total_seconds()

class Tools:
    def __init__(self):
        global tz_offset
        pass

    def cli(self, cmd):
        """send cmd line to shell, rtn (text,error code)"""
        p1 = Popen(cmd,stdout=PIPE, shell=True)
        output = p1.communicate()
        if p1.returncode != 0 :
            print('error returned from shell command: %s was %s'%(cmd,output[0]))
        return output[0],p1.returncode


    def get_datetime_object(self, tstamp):
        return datetime.datetime.fromtimestamp(int(tstamp), tz=tz)

    def get_datetime(self, datestr):
        """ translate ymdhms string into datetime """
        dt = datetime.datetime.strptime(datestr, "%Y/%m/%d-%H:%M:%S-%Z")
        if datestr.find("GMT"):
            tzaware = dt.replace(tzinfo=tzu)
        else:
            tzaware = dt.replace(tzinfo=tz)
        return tzaware

    def tstamp(self, dtime):
        '''return a UNIX style seconds since 1970 for datetime input'''
        epoch = datetime.datetime(1970, 1, 1,tzinfo=tzu)
        newdtime = dtime.astimezone(tzu)
        since_epoch_delta = newdtime - epoch
        return since_epoch_delta.total_seconds()

    def get_utc_tmtamp_from_local_string(self,instr):
        localdt = self.get_datetime(instr)
        return self.tstamp(localdt)  + tzoffset

    def parse_date(self,datestr):
        try:
            unawaredt = datetime.datetime.strptime(datestr, "%m/%d/%Y")
            tzaware = unawaredt.replace(tzinfo=tz)
            return self.tstamp(tzaware)  # + tzoffset
        except Exception as e:    
            print("returned error:%s. Error in date [%s]. Expected in format mm/dd/yyyy"% (e,datestr,))
        return 0 

    def str2tstamp(self, thestr):
        '''return a UNIX style seconds since 1970 for string input'''
        dtime = datetime.datetime.strptime(thestr.strip(), "%Y/%m/%d-%H:%M:%S-%Z")
        awaredt = dtime.replace(tzinfo=tz)
        newdtime = awaredt.astimezone(tz)
        epoch = datetime.datetime(1970, 1, 1,tzinfo=tzu)
        since_epoch_delta = newdtime - epoch
        return since_epoch_delta.total_seconds()

    def tstamp_now(self):
        """ return seconds since 1970 """
        return self.tstamp(datetime.datetime.now(tz))

    def format_datetime(self, dt):
        """ return ymdhms string """
        return datetime.datetime.strftime(dt, "%Y/%m/%d-%H:%M:%S-%z")

    def ymd(self, dt):
        """ return ymd string """
        return datetime.datetime.strftime(dt, "%Y/%m/%d")

    def dhm_from_seconds(self,s):
        """ translate seconds into days, hour, minutes """
        #print s
        days, remainder = divmod(s, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, remainder = divmod(remainder, 60)
        return (days, hours, minutes)

    def ts2str(self,ts):
        """ change a time stamp into a string expressed in local time zone"""
        dttime = datetime.datetime.fromtimestamp(ts)
        return self.format_datetime(dttime)

    def ts2date(self,ts):
        """ change a time stamp into a string expressed in local time zone"""
        dttime = datetime.datetime.fromtimestamp(ts)
        return datetime.datetime.strftime(dttime, "%Y/%m/%d")

class Sqlite():
   # Fieldback starts with initial intention of working with both sqlite3 and mysql
   def __init__(self, filename):
      self.conn = sqlite3.connect(filename)
      self.conn.row_factory = sqlite3.Row
      self.conn.text_factory = str
      self.c = self.conn.cursor()

   def __del__(self):
      self.conn.commit()
      self.c.close()
      del self.conn


class MySQL():
   # Fieldback starts with initial intention of working with both sqlite3 and mysql
   def __init__(self,database):
      self.conn = mariadb.connect(host="localhost",
               charset="utf8",
               user="reporter",
               passwd="g0adm1n",
               autocommit=True,
               db=database)
      if not self.conn:
          print("failed to open mysql database")
          sys.exit(1)
      self.c = self.conn.cursor()

   def __del__(self):
      self.conn.commit()
      del self.conn

def get_uuid():
   try:
      with open('/etc/iiab/uuid','r') as filedesc:
         uuid = filedesc.read()
   except:
      print('failed to open uuid file')
      return ''
   return uuid

def host_number(client_id):
   sql = "select host_num from lookup where client_id = ?"
   db.c.execute(sql,(client_id,))
   looked_up = db.c.fetchone()
   if looked_up != None:
      return looked_up[0]
   sql = "select * from lookup"
   db.c.execute(sql)
   row = db.c.fetchone()
   if row == None:
      host_num = 1
   else:
      sql = "select max(id) from lookup"
      db.c.execute(sql)
      host_num = db.c.fetchone()[0]
      host_num += 1
   sql = "insert or replace into lookup ( host_num,client_id) values (?, ?)" 
   db.c.execute(sql,(host_num,client_id,))
   return host_num 

def create_connection_history():
   db.c.execute("CREATE TABLE if not exists connections (id INTEGER PRIMARY KEY,"\
                "host_num TEXT, client_id TEXT, start_time_stamp TEXT,"\
                "period_start_time_stamp TEXT, period_start_tx_bytes INTEGER,"\
                "period_start_rx_bytes INTEGER,"\
                "tx_bytes INTEGER, rx_bytes INTEGER,connected_time TEXT,"\
                "connected_str TEXT,period_hour INTEGER, hour INTEGER,"\
                "minute INTEGER, "\
                "datestr TEXT,month INTEGER,day INTEGER,dow INTEGER,week INTEGER,"\
                "doy INTEGER,datetime TEXT,year INTEGER,site TEXT"\
                ")")
   db.c.execute("CREATE UNIQUE INDEX IF NOT EXISTS client_id on connections "\
                "(client_id,datestr,period_hour)")
   db.c.execute("CREATE TABLE if not exists lookup (id INTEGER PRIMARY KEY,"\
                "host_num INTEGER, client_id TEXT,name TEXT)")
   db.c.execute("CREATE UNIQUE INDEX IF NOT EXISTS  lookup_index ON lookup "\
                "(client_id)")
   
def hash_id(id):
   m = hashlib.sha256()
   m.update(id.encode('utf-8'))
   return m.hexdigest()

def update_connections(client_id,ymd, period_hour,tx_bytes,rx_bytes,connected_time):
   # look for a record with this id, and a start time within a second
   sql = 'select id,period_hour, datestr, period_start_time_stamp, '\
            'period_start_rx_bytes,period_start_tx_bytes from connections '\
         'where client_id = ? and datestr = ? and period_hour = ?'
   db.c.execute(sql,(client_id,ymd,period_hour,))
   row = db.c.fetchone()
   if row == None:
      period_start_time_stamp = tools.tstamp_now()
      period_start_rx_bytes = rx_bytes
      period_start_tx_bytes = tx_bytes
   else:
      period_start_time_stamp = row['period_start_time_stamp']
      rx_bytes = int(rx_bytes) - row['period_start_rx_bytes']
      tx_bytes = int(tx_bytes) - row['period_start_tx_bytes']
      period_start_tx_bytes = row['period_start_tx_bytes']
      period_start_rx_bytes = row['period_start_rx_bytes']
   host_num = host_number(client_id)
   datetime_object = tools.get_datetime_object(tools.tstamp_now())
   datetime = tools.format_datetime(datetime_object)
   datestr = tools.ymd(datetime_object)
   month = datetime_object.month
   day = datetime_object.day
   year = datetime_object.year
   hour = datetime_object.hour
   minute = datetime_object.minute
   d = datetime_object.date()
   week = int(d.isocalendar()[1])
   site = get_uuid()
   dow = datetime_object.weekday()
   doy = int(datetime_object.strftime('%j'))
   connected_time = tools.tstamp_now() - float(period_start_time_stamp)
   days, hours, minutes = tools.dhm_from_seconds(int(connected_time))
   start_time_stamp = int(tools.tstamp_now()) - int( connected_time)
   connected_str = "%s:%s:%s:"%(days,hours,minutes,)
   #print(host_num,client_id,ymd,period_hour,tx_bytes,rx_bytes,connected_time,
   #            datestr,month,day,dow,doy,week,datetime,year,site,)
   sql = "insert or replace into connections (host_num,client_id,start_time_stamp,tx_bytes,"\
         "rx_bytes,connected_time,connected_str,hour,minute,datestr,month,day,dow,doy,week,datetime,year,site,period_hour,period_start_time_stamp, "\
         "period_start_rx_bytes,period_start_tx_bytes) "\
         "values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
   db.c.execute(sql,(host_num,client_id,start_time_stamp,tx_bytes,rx_bytes,connected_time,connected_str,
               hour,minute,datestr,month,day,dow,doy,week,datetime,year,site,period_hour,period_start_time_stamp, period_start_rx_bytes,period_start_tx_bytes))


###########################################################
if __name__ == "__main__":
   # ########## database operations ##############
   #db = MySQL('clientinfo')
   db = Sqlite('/opt/iiab/clientinfo.sqlite')

   #db.c.execute('drop table if exists connections')
   create_connection_history()

   tools = Tools()
   if(True):
      cmd = "hostapd_cli all_sta"
      result,status = tools.cli(cmd)
      result = result.decode('utf=8')
      if status == 0:
         lines = result.split('\n')
         for line in lines:
            if line.find('=') == -1:
               netaddr = line
               client_id = hash_id(netaddr)
               continue
            if line.startswith('tx_bytes'):
               tx_bytes = line.split('=')[1]
            if line.startswith('rx_bytes'):
               rx_bytes = line.split('=')[1]
            if line.startswith('connected'):
               connected_time = line.split('=')[1]
               # calculate the start time for this connection
               start_time_stamp = int(tools.tstamp_now()) - int( connected_time)
               mydate = datetime.datetime.fromtimestamp(tools.tstamp_now())
               #print(mydate.hour)
               period_hour = mydate.hour
               ymd = tools.ymd(mydate)
               # this seems to be last item of interest for this client
               update_connections(client_id, ymd, period_hour, tx_bytes, rx_bytes, connected_time)
