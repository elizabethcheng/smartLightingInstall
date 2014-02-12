import Tkinter as tk
import tkFont
import os
import ttk
import time
import threading

from Tkinter import *
from subprocess import call
from pytz import all_timezones

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        # Set initial page to 1
        self.page = 1
        # Boolean keeping track of entering sensor ID loop
        self.loop = True 
        # Font for 'SmartLighting2013' title text
        self.titleFont = tkFont.Font(family="Times", size=36, weight="bold", \
            slant="italic")
        # Font for regular text
        self.textFont = tkFont.Font(family="Helvetica", size=14)
        # Create the 'Cancel' button, which exits the application when pressed
        self.quitButton = tk.Button(self, text='Cancel', command=self.quit)
        # Create the 'Next' button, which calls self.next() and takes user to next page
        self.nextButton = tk.Button(self, text = 'Next', command = self.next)
        # Create the 'Finish' button, which indicates the last light sensor
        self.finishButton = tk.Button(self, text = 'Finish', command = self.lastSensor)
        # Variable to store the first entry box text (Sensor #, folder name, etc.)
        self.entryText = StringVar()
        # Set self.entryText so that disableNextIfEmpty does not disable the next button
        self.entryText.set('blank')
        # Use trace to disable the Next button if entry box is blank
        self.entryText.trace('w', self.disableNextIfEmpty)
        # Variable to store latitude entry box test
        self.latText = StringVar()
        # Set self.latText so that disableNextIfEmpty does not disable the next button
        #self.latText.set('blank')
        self.latText.set('')
        # Use trace to disable the Next button if entry box is blank
        #self.latText.trace('w', self.disableNextIfEmpty)
        # Variable to store longitude entry box test
        self.lonText = StringVar()
        # Set self.lonText so that disableNextIfEmpty does not disable the next button
        #self.lonText.set('blank')
        self.lonText.set('')
        # Use trace to disable the Next button if entry box is blank
        #self.lonText.trace('w', self.disableNextIfEmpty)
        self.windowVar = StringVar()
        self.windowVar.set('blank')
        self.windowVar.trace('w', self.disableNextIfEmpty)
        self.timezoneVar = StringVar()
        self.timezoneVar.set('blank')
        self.timezoneVar.trace('w', self.disableNextIfEmpty)
        # List of light sensor names
        self.sensors = []
        # Create Layout for Page 1
        self.columnconfigure(0, minsize="350")
        self.columnconfigure(1, minsize="120")
        self.columnconfigure(2, minsize="120")
        self.rowconfigure(0, minsize="100", pad="20")
        self.rowconfigure(1, minsize="135")
        self.rowconfigure(2, minsize="100")
        self.rowconfigure(3, minsize="140")
        # Create application window
        self.grid()
        # Create widgets for first page
        self.titlePage()

    def titlePage(self):
        # Create the SmartLighting2013 title
        self.title = tk.Label(self, text = "SmartLighting2013", font = self.titleFont)
        self.title.grid(column = 0, row = 0, columnspan = 3, ipadx = "30", sticky=tk.W)
        # Add text widget
        self.text = tk.Label(self, text = "The SmartLighting Installation wizard " + \
            "will step through the software installation and light sensor set-up " + \
            "for your building's Smart Lighting system. " + \
            "Please click 'Next' to continue.", wraplength = "470", justify = LEFT, \
            anchor = W, font=self.textFont) 
        self.text.grid(column=0, row=1, columnspan=3, rowspan=2)
        self.nextButton.grid(column=1, row=3, sticky=tk.W)
        self.quitButton.grid(column=2, row=3, sticky=tk.W)

    def tinyOSInstallPage(self):
        self.nextButton.config(state='disabled')
        self.text['text'] = "Please wait while the wizard installs TinyOS software."
        self.text.grid(row=1, column=0, columnspan=3, rowspan=2)
        self.pb = ttk.Progressbar(self, orient="horizontal", length = 200, mode="indeterminate")
        self.pb.grid(row=2, column=0, columnspan=3)
        global install_thread
        install_thread = threading.Thread(target=self.installTinyOS)
        install_thread.daemon = True
        self.pb.start()
        install_thread.start()
        self.after(20, self.check_tinyos_thread)

    def check_tinyos_thread(self):
        if install_thread.is_alive():
            self.after(20, self.check_tinyos_thread)
        else:
            self.pb.stop()
            self.text['text'] = "TinyOS software successfully installed."
            self.text.grid(rowspan=2)
            self.nextButton.config(state='normal')

    def disableNextIfEmpty(self, *args):
        #if self.entryText.get() and self.latText.get() and self.lonText.get() \
        if self.entryText.get() \
                and self.windowVar.get() != "Select window sensor ID"\
                and self.timezoneVar.get() != "Select timezone":
            self.nextButton.config(state='normal')
        else:
            self.nextButton.config(state='disabled')

    def smapFolderPage(self):
        self.pb.grid_forget()
        self.text['text'] = "Enter a name for your sMAP data folder:"
        self.entryText.set('')
        self.entry = tk.Entry(self, cursor="xterm", exportselection=0, \
            textvariable=self.entryText)
        self.entry.grid(column=0, row=2, columnspan=3)
        self.update_idletasks()

    def smapInstallPage(self):
        self.nextButton.config(state='disabled')
        self.entry.grid_forget()
        self.text['text'] = "Please wait while the wizard sets up sMAP."
        self.text.grid(row=1, column=0, columnspan=3, rowspan=2)
        self.pb = ttk.Progressbar(self, orient="horizontal", length = 200, mode="indeterminate")
        self.pb.grid(row=2, column=0, columnspan=3)
        global install_thread
        install_thread = threading.Thread(target=self.installSmap)
        install_thread.daemon = True
        self.pb.start()
        install_thread.start()
        self.after(20, self.check_smap_thread)

    def check_smap_thread(self):
        if install_thread.is_alive():
            self.after(20, self.check_smap_thread)
        else:
            self.pb.stop()
            self.text['text'] = "sMAP software successfully installed."
            self.text.grid(rowspan=2)
            self.nextButton.config(state='normal')

    def sensorPlugPage(self):
        self.pb.grid_forget()
        self.finishButton.grid_forget()
        self.columnconfigure(0, minsize="350")
        self.columnconfigure(1, minsize="120")
        self.columnconfigure(2, minsize="120")
        self.columnconfigure(3, minsize="0")
        self.nextButton.grid(row=3, column=1)
        self.quitButton.grid(row=3, column=2)
        self.text['text'] = "Pick a light sensor and put two batteries in it. Plug the " +\
                "light sensor into a USB port. Click 'Next' when you are finished."
        self.text.grid(row=1, column=0, columnspan=3, rowspan=2)
        self.title.grid(row=0, column=0, columnspan=3)
        self.update_idletasks()

    def sensorIDPage(self):
        self.entryText.set('')
        self.text['text'] = "Please input the sensor ID of the sensor plugged into " + \
                "your computer. (Ex: '1', '4', etc.)."
        self.entry.grid(column=0, row=2, columnspan=3, rowspan=1)
        self.update_idletasks()

    def sensorConfigurePage(self):
        self.entry.grid_forget()
        self.columnconfigure(0, minsize="230")
        self.columnconfigure(1, minsize="120")
        self.columnconfigure(2, minsize="120")
        self.columnconfigure(3, minsize="120")
        self.title.grid(row=0, column=0, columnspan=4)
        self.text['text'] = "Please wait while we configure the light sensor." 
        self.text.grid(row=1, column=0, rowspan=2, columnspan=4)
        self.nextButton.grid(row=3, column=1)
        self.quitButton.grid(row=3, column=3)
        # Grid the 'Finish' button, which indicates that user is finished inputting light sensors
        self.finishButton.grid(row=3, column=2, sticky=tk.W)
        self.nextButton.config(state='disabled')
        self.finishButton.config(state='disabled')
        self.pb = ttk.Progressbar(self, orient="horizontal", length = 200, mode="indeterminate")
        self.pb.grid(row=2, column=0, columnspan=4, rowspan=1)
        global install_thread
        install_thread = threading.Thread(target=self.configureSensor)
        install_thread.daemon = True
        self.pb.start()
        install_thread.start()
        self.after(20, self.check_sensorconfig_thread)
        self.update_idletasks()

    def check_sensorconfig_thread(self):
        if install_thread.is_alive():
            self.after(20, self.check_sensorconfig_thread)
        else:
            self.pb.stop()
            self.text['text'] = "Light sensor " + self.entryText.get() + " successfully " +\
                    "installed. You may now place the sensor in the room. Please make sure " +\
                    "that one sensor is placed at a window. You may also want to record each " +\
                    "sensor's position in the room for your own convenience. Click 'Next' to " +\
                    "install the next light sensor. If you have finished installing the last " +\
                    "light sensor, click the 'Finish' button."
            self.nextButton.config(state='normal')
            self.finishButton.config(state='normal')

    def baseStationPlugPage(self):
        self.pb.grid_forget()
        self.finishButton.grid_forget()
        self.quitButton['text'] = "Cancel"
        self.columnconfigure(0, minsize="350")
        self.columnconfigure(1, minsize="120")
        self.columnconfigure(2, minsize="120")
        self.columnconfigure(3, minsize="0")
        self.text['text'] = "Plug the Base Station into a USB port. Click 'Next' when you are finished."
        self.text.grid(row=1, column=0, columnspan=3, rowspan=2)
        self.title.grid(row=0, column=0, columnspan=3)
        self.nextButton.grid(row=3, column=1)
        self.quitButton.grid(row=3, column=2)
        self.update_idletasks()
        
    def baseStationConfigurePage(self):
        self.nextButton.config(state='disabled')
        self.text['text'] = "Please wait while we configure the Base Station." 
        self.pb = ttk.Progressbar(self, orient="horizontal", length = 200, mode="indeterminate")
        self.pb.grid(row=2, column=0, columnspan=3)
        global install_thread
        install_thread = threading.Thread(target=self.configureBaseStation)
        install_thread.daemon = True
        self.pb.start()
        install_thread.start()
        self.after(20, self.check_baseconfig_thread)

    def check_baseconfig_thread(self):
        if install_thread.is_alive():
            self.after(20, self.check_baseconfig_thread)
        else:
            self.pb.stop()
            self.text['text'] = "BaseStation successfully installed."
            self.text.grid(rowspan=2)
            self.nextButton.config(state='normal')

    def inputInfoPage(self):
        self.pb.grid_forget()
        self.columnconfigure(0, minsize="80")
        self.columnconfigure(1, minsize="180")
        self.columnconfigure(2, minsize="220")
        self.columnconfigure(3, minsize="110")
        self.rowconfigure(0, minsize="100", pad="20")
        self.rowconfigure(1, minsize="90")
        self.rowconfigure(2, minsize="50")
        self.rowconfigure(3, minsize="50")
        self.rowconfigure(4, minsize="50")
        self.rowconfigure(5, minsize="50")
        self.rowconfigure(6, minsize="85", pad="20")
        self.latText.set('')
        self.lonText.set('')
        self.text['text'] = "Please select the ID number of the window sensor " +\
                "and the correct timezone. Then you can optionally input an " +\
                "approximate latitude (Ex: '37 52 27.447') and an approximate " +\
                "longitude (Ex: '12 15 33.386 W')."
        self.text.grid(columnspan=4, sticky=tk.N)
        self.windowVar.set("Select window sensor ID")
        self.windowLabel = tk.Label(self, text="Window Sensor ID:")
        self.windowLabel.grid(column=1, row=2, sticky=tk.E)
        self.windowMenu = tk.OptionMenu(self, self.windowVar, *self.sensors) 
        self.windowMenu.config(width="20")
        self.windowMenu.grid(column=2, row=2, sticky="ew")
        self.timezoneVar.set("Select timezone")
        self.timezoneLabel = tk.Label(self, text="Timezone:")
        self.timezoneLabel.grid(column=1, row=3, sticky=tk.E)
        us_timezones = ['US/Central', 'US/Eastern', 'US/Pacific']
        self.timezoneMenu = tk.OptionMenu(self, self.timezoneVar, *us_timezones) 
        self.timezoneMenu.config(width="20")
        # TODO: find a good height for option menu
        self.timezoneMenu.grid(column=2, row=3, sticky="ew")
        self.latLabel = tk.Label(self, text="Latitude:")
        self.latLabel.grid(column=1, row=4, sticky=tk.E) 
        self.latEntry = tk.Entry(self, cursor="xterm", exportselection=0, \
            textvariable=self.latText)
        self.latEntry.grid(column=2, row=4, sticky="ew")
        self.lonLabel = tk.Label(self, text="Longitude:")
        self.lonLabel.grid(column=1, row=5, sticky=tk.E)
        self.lonEntry = tk.Entry(self, cursor="xterm", exportselection=0, \
            textvariable=self.lonText)
        self.lonEntry.grid(column=2, row=5, sticky="ew")
        self.nextButton.grid_forget()
        self.nextButton.grid(row=6, column=2)
        self.quitButton.grid(row=6, column=3)
        self.update_idletasks()

    def initializeNetworkPage(self):
        self.windowLabel.grid_forget()
        self.windowMenu.grid_forget()
        self.latLabel.grid_forget()
        self.latEntry.grid_forget()
        self.lonLabel.grid_forget()
        self.lonEntry.grid_forget()
        self.timezoneLabel.grid_forget()
        self.timezoneMenu.grid_forget()
        self.columnconfigure(0, minsize="350")
        self.columnconfigure(1, minsize="120")
        self.columnconfigure(2, minsize="120")
        self.columnconfigure(3, minsize="0")
        self.rowconfigure(0, minsize="100", pad="20")
        self.rowconfigure(1, minsize="135")
        self.rowconfigure(2, minsize="100")
        self.rowconfigure(3, minsize="140", pad="20")
        self.rowconfigure(4, minsize="0")
        self.rowconfigure(5, minsize="0")
        self.rowconfigure(6, minsize="0")
        self.text['text'] = "The system is currently initializing the Wireless Sensor Network.\n\n" +\
                "1. If the system boots successfully, the terminal will display " +\
                "the message 'Flushing serial port...' DO NOT CLOSE THE TERMINAL " +\
                "WINDOW!\n\n2. Click the 'Next' button to continue the installation."
        self.text.grid(row=1, column=0, columnspan=3, rowspan=2, sticky=tk.N+tk.S)
        self.nextButton.grid(row=3, column=1)
        self.quitButton.grid(row=3, column=2)
        global install_thread
        install_thread = threading.Thread(target=self.initializeWSN)
        install_thread.daemon = True
        install_thread.start()
        self.update_idletasks()
        #self.after(20, self.check_baseconfig_thread)

    def uuidPage(self):
        self.nextButton.config(state='disabled')
        self.text['text'] = "Please wait while sMAP uuid's are retrieved."
        self.pb = ttk.Progressbar(self, orient="horizontal", length = 200, mode="indeterminate")
        self.pb.grid(row=2, column=0, columnspan=3)
        global uuid_thread 
        uuid_thread = threading.Thread(target=self.writeUUIDs)
        uuid_thread.daemon = True
        self.pb.start()
        uuid_thread.start()
        self.after(20, self.check_uuid_thread)

    def check_uuid_thread(self):
        if uuid_thread.is_alive():
            self.after(20, self.check_uuid_thread)
        else:
            self.pb.stop()
            self.text['text'] = "sMAP uuid's successfully retrieved."
            self.text.grid(rowspan=2)
            self.nextButton.config(state='normal')

    def congratzPage(self):
        # Record needed info in db_info.txt
        self.pb.grid_forget()
        f = open('db_info.txt', 'w')
        sensors = ','.join(["light" + x for x in self.sensors])
        f.write(sensors + '\n')
        f.write('light' + self.windowVar.get() + '\n')
        f.write(self.latText.get() + '\n')
        f.write(self.lonText.get() + '\n')
        f.write(self.timezoneVar.get() + '\n')
        f.write(str(int(time.time())))
        f.close()
        self.nextButton.grid_forget()
        self.text['text'] = "Congratulations! You have successfully installed " + \
            "SmartLighting. After two weeks, you may create a local database for " +\
            "data collection and prediction. Click 'Finish' to exit the installation " +\
            "wizard and to begin collecting sensor data."
        self.quitButton['text'] = 'Finish'
        self.update_idletasks()

    def next(self):
        # Set the correct page number
        if self.loop == True and self.page == 7:
            self.page = 5 
        else:
            self.page += 1
        self.generatePage()

    def lastSensor(self):
        self.loop = False 
        self.next()

    def generatePage(self):
        if self.page == 2:
            self.tinyOSInstallPage()
        elif self.page == 3:
            self.smapFolderPage()
        elif self.page == 4:
            self.smapInstallPage()
        elif self.page == 5:
            self.sensorPlugPage()
        elif self.page == 6:
            self.sensorIDPage()
        elif self.page == 7:
            self.sensorConfigurePage()
        elif self.page == 8:
            self.baseStationPlugPage()
        elif self.page == 9:
            self.baseStationConfigurePage()
        elif self.page == 10:
            self.inputInfoPage()
        elif self.page == 11:
            self.initializeNetworkPage()
        elif self.page == 12:
            self.uuidPage()
        else:
            self.congratzPage()

    def installTinyOS(self):
        """
        Installs nesc and tiny-os. Edits App and PythonFiles.
        Takes about __ minutes.
        """
        call(["sh", "nesc.sh"])
        call(["sh", "tinyos_install.sh"])
        #x = [i for i in range(2)]
        #for elem in x:
        #    print x
        #    time.sleep(1)

    def installSmap(self):
        """
        Installs smap. Takes about __ minutes.
        """
        call(["sh", "smap_install.sh"])
        self.folderName = self.entryText.get()
        print self.folderName
        #x = [i for i in range(2)]
        #for elem in x:
        #    print x
        #    time.sleep(1)

    def configureSensor(self):
        sensorNum = self.entryText.get()
        savedPath = os.getcwd()
        os.chdir('./tinyos-main/apps/SmartLightingApps/LightSensor')
        call(["sudo", "chmod", "666", "/dev/ttyUSB1"])
        call(["make", "telosb", "install," + str(sensorNum)])
        os.chdir(savedPath)
        print sensorNum
        self.sensors.append(str(sensorNum))
        #x = [i for i in range(2)]
        #for elem in x:
        #    print x
        #    time.sleep(1)

    def configureBaseStation(self):
        savedPath = os.getcwd()
        os.chdir('./tinyos-main/apps/SmartLightingApps/BaseStation')
        call(["sudo", "chmod", "666", "/dev/ttyUSB1"])
        call(["make", "telosb", "install"])
        os.chdir(savedPath)
        # sMAP Log set-up
        os.chdir('./tinyos-main/support/sdk/python/SmartLightingPython')
        # Replace TEST4 with self.folderName
        findReplace = "s/TEST4/" + self.folderName + "/g"
        call("sed " + findReplace + " testconfigMulti.py > testconfigMulti.py.new", shell=True)
        call(["rm", "testconfigMulti.py"])
        call(["mv", "testconfigMulti.py.new", "testconfigMulti.py"])
        os.chdir(savedPath) 
        #x = [i for i in range(2)]
        #for elem in x:
        #    print x
        #    time.sleep(1)

    def initializeWSN(self):
        savedPath = os.getcwd()
        os.chdir('./tinyos-main/support/sdk/python/SmartLightingPython')
        findReplaceLight = "'s/nodenum = int/#/g'"
        call("sed " + findReplaceLight + " udm_smapDriverMulti_onboard.py > udm_smapDriverMulti_onboard.py.new", shell=True)
        call(["rm", "udm_smapDriverMulti_onboard.py"])
        call(["mv", "udm_smapDriverMulti_onboard.py.new", "udm_smapDriverMulti_onboard.py"])
        findReplaceMulti = "'s/nodemultinum = int/#/g'"
        call("sed " + findReplaceMulti + " udm_smapDriverMulti_onboard.py > udm_smapDriverMulti_onboard.py.new", shell=True)
        call(["rm", "udm_smapDriverMulti_onboard.py"])
        call(["mv", "udm_smapDriverMulti_onboard.py.new", "udm_smapDriverMulti_onboard.py"])
        call(["sed", "-i", "-e", "56i\            nodenum = " + str(len(self.sensors)), "udm_smapDriverMulti_onboard.py"])
        call(["sed", "-i", "-e", "57i\            nodemultinum = 0", "udm_smapDriverMulti_onboard.py"])
        call(["sh", "startMulti.sh"])
        os.chdir(savedPath)
        #x = [i for i in range(2)]
        #for elem in x:
        #    print x
        #    time.sleep(1)

    def writeUUIDs(self):
        # call(["sh", "writeUUIDs.sh"])
        # Dummy executions since writeUUIds.sh doesn't do anything now
        x = [i for i in range(2)]
        for elem in x:
            print x
            time.sleep(1)

app = Application()
app.master.title('Smart Lighting')
app.mainloop()
