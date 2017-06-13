#!/bin/bash -x
# pull latest version of 4 main git repos

IIAB_BASE=/opt/iiab

cd $IIAB_BASE/iiab-factory
git pull

cd $IIAB_BASE/iiab
git pull

cd $IIAB_BASE/iiab-admin-console
git pull

cd $IIAB_BASE/iiab-menu
git pull
