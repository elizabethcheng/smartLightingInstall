Authors: Aparna Dhinakaran and Elizabeth Cheng

This application installs several programs necessary for light sensor set-up and data collection such as TinyOS and sMAP. It also walks the user through the installation of Smart Lighting light sensors and a BaseStation. The application then creates a local sqlite3 database for storing light sensor data. 

1. GeneralDB.py: run the command
    python GeneralDB.py db_info.txt
   to create a local database configured with the information found in db_info.txt

2. make_database.sh: shell script which runs the command 
    python GeneralDB.py db_info.txt

3. nesc.sh: shell script which installs nesc (necessary for TinyOS)

4. pre-install.sh: shell script which must be run before the user starts the installation application. Installs necessary python modules and updates autoconf.

5. smap_install.sh: shell script which installs sMAP software.

6. tinyos_install.sh: shell script which installs TinyOS software and configures TinyOS directories for Smart Lighting sensors.

7. tktest.py: the Tkinter python installation application.
