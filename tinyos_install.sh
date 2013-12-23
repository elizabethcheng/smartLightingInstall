#!/bin/bash

# Installing TinyOS
git clone git://github.com/tinyos/tinyos-main.git

cd tinyos-main/tools
./Bootstrap
./configure
make
sudo make install

# Part 3: Set environment variables in ~/.bashrc file
echo "export TOSROOT=$HOME/smart/smartLightingInstall/tinyos-main" >> ~/.bashrc
echo "export TOSDIR=$TOSROOT/tos" >> ~/.bashrc
echo "export MAKERULES=$TOSROOT/support/make/Makerules" >> ~/.bashrc
echo "export CLASSPATH=$TOSROOT/support/sdk/java/tinyos.jar:." >> ~/.bashrc
echo "export PYTHONPATH=$TOSROOT/support/sdk/python:$PYTHONPATH" >> ~/.bashrc
echo "export PATH=$TOSROOT/support/sdk/c:$PATH" >> ~/.bashrc

# Part 4: Tar filing
mv App App.tar.gz
mv App.tar.gz tinyos-main/apps
cd tinyos-main/apps
tar -xzf App.tar.gz
cd ../..

mv PythonFiles PythonFiles.tar.gz
mv PythonFiles.tar.gz tinyos-main/support/sdk/python
cd tinyos-main/support/sdk/python
tar -xzf PythonFiles.tar.gz
cd ../..

# Part 5: Edit necessary tinyos files
sed 's/4096/1024/g' tinyos-main/tos/chips/msp430/timer/Msp430DcoSpec.h > tinyos-main/tos/chips/msp430/timer/Msp430DcoSpec.h.new
rm tinyos-main/tos/chips/msp430/timer/Msp430DcoSpec.h
mv tinyos-main/tos/chips/msp430/timer/Msp430DcoSpec.h.new tinyos-main/tos/chips/msp430/timer/Msp430DcoSpec.h

sed 's/115200/28800/g' tinyos-main/support/sdk/python/SmartLightingPython/udm_smapDriverMulti_onboard.py > tinyos-main/support/sdk/python/SmartLightingPython/udm_smapDriverMulti_onboard.py.new
rm tinyos-main/support/sdk/python/SmartLightingPython/udm_smapDriverMulti_onboard.py
mv tinyos-main/support/sdk/python/SmartLightingPython/udm_smapDriverMulti_onboard.py.new tinyos-main/support/sdk/python/SmartLightingPython/udm_smapDriverMulti_onboard.py

sed 's/mcombine(getPowerState(),/MSP430_POWER_LPM1;/g' tinyos-main/tos/chips/msp430/McuSleepC.nc > tinyos-main/tos/chips/msp430/McuSleepC.nc.new1
sed 's/call McuPowerOverride.lowestState())//g' tinyos-main/tos/chips/msp430/McuSleepC.nc.new1 > tinyos-main/tos/chips/msp430/McuSleepC.nc.new2
rm tinyos-main/tos/chips/msp430/McuSleepC.nc
rm tinyos-main/tos/chips/msp430/McuSleepC.nc.new1
mv tinyos-main/tos/chips/msp430/McuSleepC.nc.new2 tinyos-main/tos/chips/msp430/McuSleepC.nc

sed 's/100/40/g' tinyos-main/tos/types/Lpl.h > tinyos-main/tos/types/Lpl.h.new
rm tinyos-main/tos/types/Lpl.h
mv tinyos-main/tos/types/Lpl.h.new tinyos-main/tos/types/Lpl.h
 

