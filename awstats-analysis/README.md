## Extract Usage Statistics from awstats files

These files are a work in progress but have been committed in case others can use them

## Copy Utility

cp-stats

* Use when combining awstats from several servers
* Directory names are constants in script
* Start in destination top level dir
* Such as /media/usb0/Devel/AwstatsAnalysis/Nigeria2019
* Source IIAB expected in another media/usb mount
* Copies source awstats files to destination directory given by parameter 1

## Spreadsheet Creation Utility

wr-xlsx

* Requires pip3 install XlsxWriter
* Start in destination top level dir
* Such as /media/usb0/Devel/AwstatsAnalysis/Nigeria2019
* Expects a set of subdirectories for each device with files copied from that device
* Expects awstats file layout as of Mar 10, 2020 (AWSTATS DATA FILE 7.6 build 20161204):
* Writes xlsx to current directory
