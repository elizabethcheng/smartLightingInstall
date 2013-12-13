import Tkinter as tk
import tkFont
import os
import ttk
import time
import threading

from time import mktime, localtime, gmtime, strftime
from Tkinter import *
from PIL import Image, ImageTk
from subprocess import call

class Meter(tk.Frame):
    def __init__(self, master, width=300, height=20, bg='white', fillcolor='orchid1',value=0.0, text=None, font=None, textcolor='black', *args, **kw):
        tk.Frame.__init__(self, master, bg=bg, width=width, height=height, *args, **kw)
        self._value = value
        self._canv = tk.Canvas(self, bg=self['bg'], width=self['width'], height=self['height'],highlightthickness=0, relief='flat', bd=0)
        self._canv.pack(fill='both', expand=1)
        self._rect = self._canv.create_rectangle(0, 0, 0, self._canv.winfo_reqheight(), fill=fillcolor, width=0)
        self._text = self._canv.create_text(self._canv.winfo_reqwidth()/2, self._canv.winfo_reqheight()/2,text='', fill=textcolor)
        if font:
            self._canv.itemconfigure(self._text, font=font)
            self.set(value, text)
            self.bind('<Configure>', self._update_coords)
    
    def _update_coords(self, event):
        '''Updates the position of the text and rectangle inside the canvas when the size of
            the widget gets changed.'''
        # looks like we have to call update_idletasks() twice to make sure
        # to get the results we expect
        self._canv.update_idletasks()
        self._canv.coords(self._text, self._canv.winfo_width()/2, self._canv.winfo_height()/2)
        self._canv.coords(self._rect, 0, 0, self._canv.winfo_width()*self._value, self._canv.winfo_height())
        self._canv.update_idletasks()
        
    def get(self):
        return self._value, self._canv.itemcget(self._text, 'text')
    
    def set(self, value=0.0, text=None):
        #make the value failsafe:
        if value < 0.0:
            value = 0.0
        elif value > 1.0:
            value = 1.0
        self._value = value
        if text == None:
            #if no text is specified use the default percentage string:
            text = str(int(round(100 * value))) + ' %'
        self._canv.coords(self._rect, 0, 0, self._canv.winfo_width()*value, self._canv.winfo_height())
        self._canv.itemconfigure(self._text, text=text)
        self._canv.update_idletasks()

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        # Set initial page to 1
        self.page = 1
        # Boolean keeping track of entering sensor ID loop
        self.loop = True 
        # Path for image on first page
        self.imgPath = './moel.gif'
        # Font for 'SmartLighting2013 title text'
        self.titleFont = tkFont.Font(family="Times", size=36, weight="bold", \
            slant="italic")
        # Font for regular text
        self.textFont = tkFont.Font(family="Helvetica", size=14)
        # Variable to store entry box text (Sensor #, etc.)
        self.entryText = StringVar()
        # List of light sensor names
        self.sensors = []
        # Current date in unixtime
        self.currentDate = ""
        # Create Layout for Page 1
        self.columnconfigure(0, minsize="350")
        self.columnconfigure(1, minsize="120")
        self.columnconfigure(2, minsize="120")
        self.rowconfigure(0, minsize="120", pad="20")
        self.rowconfigure(1, minsize="100")
        self.rowconfigure(2, minsize="100")
        self.rowconfigure(3, minsize="150", pad="20")
        # Create application window
        self.grid()
        # Create widgets for first page
        self.titlePage()

    def demo(self, meter, value):
        meter.set(value)
        if value < 1.0:
            value = value + 0.005 
            meter.after(50, lambda: self.demo(meter, value))
        else:
            meter.set(value, 'Demo successfully finished')

    def titlePage(self):
        # Create the SmartLighting2013 title
        self.title = tk.Label(self, text = "SmartLighting2013", font = self.titleFont)
        self.title.grid(column = 0, row = 0, columnspan = 3, ipadx = "20", \
                ipady="10", sticky=tk.W)
        # Add photo image to first page
        #self.img = ImageTk.PhotoImage(Image.open(self.imgPath))
        #self.image = tk.Label(self, image = self.img)
        #self.image.grid(column = 0, row = 1, columnspan=3, rowspan=1, sticky=tk.N)
        # Add text widget
        self.text = tk.Label(self, text = "The SmartLighting Installation wizard " + \
            "will step through the software installation and light sensor set-up. " + \
            "Please click 'Next' to continue.", wraplength = "450", justify = LEFT, \
            anchor = W, font=self.textFont) 
        self.text.grid(column=0, row=1, columnspan=3, rowspan=2, ipady=".5i")
        # Create the 'Cancel' button, which exits the application when pressed
        # Doubles as the 'Finish' button on the last page
        self.quitButton = tk.Button(self, text='Cancel', command=self.quit)
        # Create the 'Next' button, which calls self.next() and takes user to next page
        # Doubles as the 'Next Sensor' button
        self.nextButton = tk.Button(self, text = 'Next', command = self.next)
        self.nextButton.grid(column=1, row=3)
        self.quitButton.grid(column=2, row=3)
        # Create the button but DO NOT GRID IT
        self.finishButton = tk.Button(self, text = 'Finish', command = self.lastSensor)

    def tinyOSInstallPage(self):
        #self.image.grid_forget()
        self.nextButton.config(state='disabled')
        self.text['text'] = "Please wait while the wizard installs TinyOS software."
        self.text.grid(row=1, column=0, columnspan=3, rowspan=2)
        #self.m = Meter(self, relief='ridge', bd=3)
        #self.m.grid(row=2, column=0, columnspan=3)
        #self.m.set(0.0, 'Starting demo...')
        #self.m.after(10, lambda: self.demo(self.m, 0.0))
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

    def smapFolderPage(self):
        self.pb.grid_forget()
        self.text['text'] = "Enter a name for your sMAP data folder:"
        self.entry = tk.Entry(self, cursor="xterm", exportselection=0, \
            textvariable=self.entryText)
        self.entry.grid(column=0, row=2, columnspan=3)
        self.update_idletasks()

    def smapInstallPage(self):
        self.nextButton.config(state='disabled')
        self.entry.grid_forget()
        self.text['text'] = "Please wait while the wizard sets up sMAP."
        self.text.grid(row=1, column=0, columnspan=3, rowspan=2)
        #self.m = Meter(self, relief='ridge', bd=3)
        #self.m.grid(row=2, column=0, columnspan=3)
        #self.m.set(0.0, 'Starting demo...')
        #self.m.after(10, lambda: self.demo(self.m, 0.0))
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
        self.text['text'] = "Pick a light sensor and put two batteries in it. Plug the light sensor into a USB port. Click 'Next' when you are finished."
        self.text.grid(row=1, column=0, columnspan=3, rowspan=2)
        self.title.grid(row=0, column=0, columnspan=3)
        self.update_idletasks()

    def sensorIDPage(self):
        self.entryText.set('')
        self.text['text'] = "Please input the sensor ID of the sensor plugged into " + \
                "your computer. (Ex: '1', '4', etc.)."
        #self.text.grid(rowspan=1)
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
        # Create the 'Last Sensor' button, which indicates that user is finished inputting light sensors
        self.nextButton.grid(row=3, column=1)
        self.quitButton.grid(row=3, column=3)
        self.finishButton = tk.Button(self, text = 'Finish', command = self.lastSensor)
        self.finishButton.grid(row=3, column=2)
        self.nextButton.config(state='disabled')
        self.finishButton.config(state='disabled')
        #self.m = Meter(self, relief='ridge', bd=3)
        #self.m.grid(row=2, column=0, columnspan=4)
        #self.m.set(0.0, 'Starting demo...')
        #self.m.after(10, lambda: self.demo(self.m, 0.0))
        self.pb = ttk.Progressbar(self, orient="horizontal", length = 200, mode="indeterminate")
        self.pb.grid(row=2, column=0, columnspan=4, rowspan=1)
        global install_thread
        install_thread = threading.Thread(target=self.configureSensor)
        install_thread.daemon = True
        self.pb.start()
        install_thread.start()
        self.after(20, self.check_sensorconfig_thread)
        #self.configureSensor()
        #If successful, change text to: "Light sensor successfully installed"
        self.update_idletasks()

    def check_sensorconfig_thread(self):
        if install_thread.is_alive():
            self.after(20, self.check_sensorconfig_thread)
        else:
            self.pb.stop()
            self.text['text'] = "Light sensor " + self.entryText.get() + " successfully installed"
            #self.text.grid(rowspan=2)
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
        self.text['text'] = "Put two batteries in the BaseStation mote. Plug the " +\
            "BaseStation mote into a USB port. Click 'Next' when you are finished."
        self.text.grid(row=1, column=0, columnspan=3, rowspan=2)
        self.title.grid(row=0, column=0, columnspan=3)
        self.nextButton.grid(row=3, column=1)
        self.quitButton.grid(row=3, column=2)
        self.update_idletasks()
        
    def baseStationConfigurePage(self):
        self.nextButton.config(state='disabled')
        self.quitButton.config(state='disabled')
        self.text['text'] = "Please wait while we configure the BaseStation." 
        #self.text.grid(row=1, column=0, columnspan=3, rowspan=1)
        #self.m = Meter(self, relief='ridge', bd=3)
        #self.m.grid(row=2, column=0, columnspan=3)
        #self.m.set(0.0, 'Starting demo...')
        #self.m.after(10, lambda: self.demo(self.m, 0.0))
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
            self.quitButton.config(state='normal')

    def congratzPage(self):
        self.pb.grid_forget()
        self.nextButton.grid_forget()
        self.text['text'] = "Congratulations! You have successfully installed " + \
            "SmartLighting. Click 'Finish' to exit the installation wizard."
        self.text.grid(row=1, column=0, columnspan=3, rowspan=2)
        self.quitButton['text'] = "Finish"
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
            self.congratzPage()

    def installTinyOS(self):
        #run terminal command here
        #call(["sh", "tinyos_install.sh"])
        x = [i for i in range(2)]
        for elem in x:
            print x
            time.sleep(1)

    def installSmap(self):
        #run terminal commands here
        #call(["sh", "smap_install.sh"])
        #folderName = self.entryText.get()
        #print folderName
        #call(["sh", "smap_folder.sh"])
        x = [i for i in range(2)]
        for elem in x:
            print x
            time.sleep(1)

    def configureSensor(self):
        #sensorNum = self.entryText.get()
        #savedPath = os.getcwd()
        #os.chdir('./tinyos-main/apps/LightSensor')
        #call(["make", "telosb", "install,", str(sensorNum)])
        #os.chdir(savedPath)
        #print sensorNum
        #self.sensors.append("light" + str(sensorNum))
        #run terminal commands here
        x = [i for i in range(2)]
        for elem in x:
            print x
            time.sleep(1)

    def configureBaseStation(self):
        #savedPath = os.getcwd()
        #os.chdir('./tinyos-main/apps/BaseStation')
        #call(["make", "telosb", "install"])
        #os.chdir(savedPath)
        x = [i for i in range(2)]
        for elem in x:
            print x
            time.sleep(1)

app = Application()
app.master.title('Smart Lighting')
app.mainloop()
