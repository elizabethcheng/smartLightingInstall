#!/bin/bash

sudo apt-get update

# Install python modules (tkinter, numpy, scipy, matplotlib, pandas, sqlite3, pip, setuptools
sudo apt-get install python python-tk idle python-pmw python-imaging python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose python-pip python-setuptools sqlite3 python-imaging-tk

# Install patsy
sudo pip install --upgrade patsy

# Install pandas version 0.7.1
sudo easy_install pandas==0.7.1

# Install statsmodels
sudo easy_install -U statsmodels

# Install curl
sudo apt-get install curl

# Update autoconf
cd /usr/local
export build=~/devtools # or wherever you'd like to build
mkdir -p $build

##
# Autoconf
# http://ftpmirror.gnu.org/autoconf

cd $build
curl -OL http://ftpmirror.gnu.org/autoconf/autoconf-2.69.tar.gz
tar xzf autoconf-2.69.tar.gz
cd autoconf-2.69
./configure --prefix=/usr/local
make
sudo make install
export PATH=/usr/local/bin

exit 0
