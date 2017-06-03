# To Create a OSM Subset:
1. Visit http://www.openstreetmap.org/#map=2/17.6/-78.8 and click the export button -- top row, middle left.
1. Drag the handles at the corners of the bounding box to contain the area where increased detail is desired.
1. Record the North, South, East, and West boundaries of the box.
1. Copy central-america.ini to a filename that describes your subset. It is convenient to do this in the same directory which contains the scripts you will use:
     1. mk-subset.py
     1. cp-subset.sh
     1. iiab-unzip
1. The config file needs changes to the right of the "=" to specify name, bounding box. (lngw is longitude West, latn is latitde North, etc.)
~~~
;; Configuration file for subset-iiab
;;
[DEFAULT]
;
subset_name = central_america
lngw = -120
lnge = -64.7
latn = 33.3
lats = 5.97
zoom_start = 9
zoom_stop = 15
~~~
6. Pass the name of your <subset_name>.ini file to the python subset generation program:
~~~ 
./mk-subset.py <subset_name>.ini
~~~
7. Copy the files thus selected into /library/<subset_name/output uing the command:
~~~
./cp-subset.sh <subset_name>
~~~
8. A zip file containing the zoom levels that lie within the bounday box specified in the ini file will be found at /library/<subset_name>/output/<subset_name>.zip
9. Copy the zip file and the iiab-unzip helper program to the target machine, into any convenient directory. Be sure that there is enough disk space for the zip file and it's expanded form (This is the sum of the unzipped size as indicated in the first few lines of <subset_name>.info, and the size of the <subset_name>.zip file itself).
There is a shell script embedded in the zip file, which designates the target directory, so the the "iiab-unzip" program can put it into the proper place -- regardless of where the iiab-unzip script, or the <subset_name>.zip files are located.
10. Install OSM up to 8 zoom levels (only requires 200MB) so that general coverage of the world is available. See http://download.iiab.io/content/world8.zip.
~~~
./iiab-unzip world8.zip
~~~
