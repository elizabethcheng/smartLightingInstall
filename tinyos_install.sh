#!/bin/bash

# Installing TinyOS
git clone git://github.com/tinyos/tinyos-main.git

cd tinyos-main/tools
./Bootstrap
./configure
make
sudo make install

# Part 3: Set environment variables in ~/.bashrc file
echo "export TOSROOT=$HOME/tinyos-main" >> ~/.bashrc
echo "export TOSDIR=$TOSROOT/tos" >> ~/.bashrc
echo "export MAKERULES=$TOSROOT/support/make/Makerules" >> ~/.bashrc
echo "export CLASSPATH=$TOSROOT/support/sdk/java/tinyos.jar:." >> ~/.bashrc
echo "export PYTHONPATH=$TOSROOT/support/sdk/python:$PYTHONPATH" >> ~/.bashrc
echo "export PATH=$TOSROOT/support/sdk/c:$PATH" >> ~/.bashrc
