#!/bin/bash

# Part 1: Install dependencies
sudo apt-get install python-setuptools
sudo pip install smap
#sudo apt-get install smap 
#sudo apt-get install scipy 
#sudo apt-get install python-devel 
sudo apt-get install postgresql-9.1
sudo apt-get install libpq-dev
sudo apt-get install python-psycopg2

# Part 2: Check that necessary drivers are present
