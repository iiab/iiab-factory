#!/bin/bash 
# write jupyter notebook to markdown
if [ $# -eq 0 ];then
	echo Please select a notebook as first paramater.
	exit 1
fi
jupyter nbconvert $1 --to markdown 

