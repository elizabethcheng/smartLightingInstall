""" To Do 
1. How to get UUIDS, latitude, longitude, timezone
2. Artificial lights
3. Start Date

sensors = ['light1', 'light2'...]
"""
    

### DATABASE ###

import urllib2
import datetime
import numpy as np
import sqlite3
from numpy import vstack
import scipy as sp
from scipy import stats
from datetime import datetime,date
import time
from time import mktime, localtime, gmtime, strftime
import statsmodels as sm
import matplotlib as mpl
from matplotlib import pyplot as plt
import pytz
from pytz import timezone
import math
import pdb
import sys

import sqlite3
from sqlite3 import dbapi2 as sqlite3
from scipy.cluster.vq import *

if __name__ == '__main__':
    # Read db_info.txt
    f = open(sys.argv[1], 'r')
    split_lines = f.read().split('\n')
    print split_lines
    # Parse the file
    sensors = split_lines[0].split(',')
    print sensors
    sensors_strip = [x.strip() for x in sensors]
    print sensors_strip
    window = split_lines[1].strip()
    print window
    lat = split_lines[2].strip()
    lon = split_lines[3].strip()
    print lat + ', ' + lon
    timezone = split_lines[4].strip()
    print timezone
    uuid_dict = {}
    uuids = split_lines[5].split(',')
    for elem in uuids:
        split = elem.split(':')
        uuid_dict[split[0].strip()] = split[1].strip()
    print uuid_dict
    start_unix = split_lines[6].strip()
    print start_unix
    # Create tables and add data
    #create_db(sensors_strip, window, lat, lon, timezone, uuid_dict, start_unix)
    print "done"

def create_db(sensors, window, lat, lon, timezone, UUID_dict, start_unix):
    create_tables()
    createLightData()
    
    ##########################
    ### CREATE TABLE CODE ####
    ##########################

    def create_tables():

        #Create a database data.db and connect to it
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        for elem in sensors:
            table = elem
            cursor.execute('''CREATE TABLE ''' + table + '''(unixtime REAL, weekday TEXT,
                    day INTEGER, month INTEGER, year INTEGER, hour INTEGER,
                    minute INTEGER, seconds INTEGER, light REAL, altitude REAL,
                    azimuth REAL, cloudiness TEXT, x REAL, y REAL, exponential REAL,
                    average REAL, daylight REAL,maxlight REAL,cluster INTEGER,
                    soft1 INTEGER, soft2 INTEGER, soft3 INTEGER, mem1 REAL,
                    mem2 REAL, mem3 REAL, movingavg REAL, processed REAL,
                    PRIMARY KEY (unixtime))''')

        #Save your changes
        connection.commit()

    def make_unix_timestamp(date_string, time_string):
        """This command converts string format of date into unix timstamps."""
        format = '%Y %m %d %H %M %S'
        return time.mktime(time.strptime(date_string + " " + time_string, format))
                       

    ######################################        
    ### LIGHT TABLES CODE ################
    ######################################

    def parse(url):
        """Returns a list of the timestamps, readings, and unixtimes of each
        entry from the raw data provided by the input url."""
        timestamp=[]
        reading=[]
        timest=[]
        temp=[]
        unixtime=[]
        webpage = urllib2.urlopen(url).read()
        page = str.split(webpage, '[')
        for count in range(len(page)):
            z1=str.split(page[count],',')
            temp.append(z1)
            count+=1
        getvar = temp[3:]
        for count in range(len(getvar)):
            t=float(getvar[count][0])/1000
            unixtime.append(float(getvar[count][0]))
            ttb=time.localtime(t)
            #Returns time in string format: "Wed 21 11 2012 16 45 3"
            tim=strftime("%a %d %m %Y %H %M %S",ttb)
            #For debugging:
            if (count == 0):
                print(tim)
            timestamp.append(tim.split())
            read=str.split((getvar[count][1]),']')
            reading.append(float(read[0]))
            #For debugging:
            if (count == 0):
                print(float(read[0])) #37.851485925
            count+=1
        return [timestamp, reading, unixtime]

    def getSunpos(lat, lon, timezon, year, month, day, hour, minute, seconds):
        """Returns a list containing the altitude and the azimuth given the
        latitude LAT, longitude LON, timezone TIMEZON, year YEAR, month MONTH,
        minute MINUTE, and seconds SECONDS."""
        splat = str.split(lat)
        splon = str.split(lon)
        latitude = float(splat[0]) + float(splat[1])/60 + float(splat[2])/3600
        if splon[3] == 'W':
            longitude = -(float(splon[0]) + float(splon[1])/60 +
                          float(splon[2])/3600)
        else:
            longitude = float(splon[0]) + float(splon[1])/60 +\
            float(splon[2])/3600
        local = pytz.timezone(timezon)
        loctime = str(year) + '-' + str(month) + '-' + str(day) + ' ' +\
                    str(hour) + ':' + str(minute) + ':' + str(seconds)
        naive = datetime.strptime(loctime, "%Y-%m-%d %H:%M:%S")
        local_dt = local.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        utc_dt.strftime("%Y-%m-%d %H:%M:%S")
        utcsplit = str.split(str(utc_dt))
        utcdt = str.split(utcsplit[0],'-')
        utctime = str.split(utcsplit[1],'+')
        utctimefinal = str.split(utctime[0],':')
        year = utcdt[0]
        month = utcdt[1]
        day = utcdt[2]
        hour = utctimefinal[0]
        minute = utctimefinal[1]
        second = utctimefinal[2]
        #+1 for e and -1 for w for dst
        houronly = float(hour) + float(minute)/60 + float(second)/3600
        delta = int(year)-1949
        leap = int(delta/4)
        doy = [31,28,31,30,31,30,31,31,30,31,30,31]
        if int(year)%4 == 0:
            doy[1] = 29
        dayofyear = sum(doy[0:(int(month)-1)]) + int(day)
        jd = 2432916.5 + delta*365 + dayofyear + leap + houronly/24
        actime = jd - 2451545
        pi = 3.1415926535897931
        rad = pi/180

        #mean longitude in degrees between 0 and 360
        L = (280.46 + 0.9856474*actime)%360
        if L < 0:
            L+=360
        #mean anomaly in radians
        g = (357.528 + 0.9856003*actime) % 360
        if g < 0:
            g+=360
        g = g*rad
        #ecliptic longitude in radians
        eclong = (L + 1.915*math.sin(g) + 0.02*math.sin(2*g)) % 360
        if eclong < 0:
            eclong+=360
        eclong = eclong*rad
        #ecliptic obliquity in radians
        ep = (23.439 - 0.0000004*actime)*rad
        #get right ascension in radians between 0 and 2 pi
        num = math.cos(ep)*math.sin(eclong)
        den = math.cos(eclong)
        ra = math.atan(num/den)
        if den < 0:
            ra+=pi
        elif den > 0 and num < 0:
            ra+=2*pi
        #get declination in radians
        dec = math.asin(math.sin(ep)*math.sin(eclong))
        #get greenwich mean sidereal time
        gmst = (6.697375 + 0.0657098242*actime + houronly) % 24
        if gmst < 0:
            gmst+=24
        #get local mean sidereal time in radians
        lmst=(gmst + longitude/15) % 24
        if lmst < 0:
            lmst+=24
        lmst = lmst*15*rad
        #get hour angle in radians between -pi and pi
        ha = lmst - ra
        if ha < -pi:
            ha+=2*pi
        elif ha > pi:
            ha = ha - 2*pi
        #change latitude to radians
        latrad = latitude*rad
        #calculate elevation and azimuth in degrees
        el=math.asin(math.sin(dec)*math.sin(latrad) +
                     math.cos(dec)*math.cos(latrad)*math.cos(ha))
        az=math.asin(-math.cos(dec)*math.sin(ha)/math.cos(el*rad))
        #approximation for azimuth
        #if az==90, elcrit=math.degrees(math.asin(math.sin(dec)/math.sin(latitude)))
        if math.sin(dec) - math.sin(el)/math.sin(latrad) >= 0 and\
            math.sin(az) < 0:
            az+=2*pi
        elif math.sin(dec) - math.sin(el)/math.sin(latrad) < 0:
            az = pi-az
        eldeg = round(math.degrees(el),2)
        azdeg = round(math.degrees(az),2)
        if eldeg > -0.56:
            refrac = 3.51561*(0.1594 + 0.0196*eldeg + 0.00002*math.pow(eldeg,2))\
                        /(1 + 0.505*eldeg + 0.0845*math.pow(eldeg,2))
        else:
            refrac = 0.56
        eldeg=eldeg+refrac
        #print eldeg,azdeg
        #data is saved for future reference
        return [str(eldeg), str(azdeg)]


    def createData(sensor, start, end, lat, lon, timezon):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        sensorID = UUID_dict[sensor]
        table = sensor
        url = "http://new.openbms.org/backend/api/prev/uuid/" + sensorID +\
              "?&start=" + start + "&end=" + end + "&limit=100000&"
        timestamp, reading, unixtime = parse(url)
        for count in range(len(reading)):
            time = timestamp[count]
            sunpos = getSunpos(lat, lon, timezon, time[3], time[2],
                               time[1], time[4], time[5], time[6])
            to_db = [unixtime[count], time[0], time[1], time[2], time[3],
                 time[4], time[5],time[6], reading[count], sunpos[0],
                 sunpos[1], "None", 0, 0, float('NaN'), float('NaN'),
                 float('NaN'), float('NaN'), float('Nan'),float('NaN'),
                 float('NaN'), float('NaN'), float('Nan'),float('NaN'),
                 float('NaN'), float('NaN'), float('Nan')]
            cursor.execute('INSERT OR IGNORE INTO ' + table +
                           ' VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                           to_db)      
        connection.commit()

    def createLightData():
        print "Fetching Raw Light Data"
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        for elem in sensors:
            createData(elem, start_unix, str(int(time.time())*1000),lat, lon, timezone)
        connection.commit()
        print "Processing Light Tables"
        insert_movingavg()
        insert_processed_light()
        print 'Smoothing Light Tables'
        smoothingtables()
        print " Hard Clustering Light Tables"
        window_cluster = cluster(str(window), start_unix,  str(int(time.time())*1000))
        create_cluster(str(window), start_unix,  str(int(time.time())*1000), window_cluster)
        print "Updating Other Clusters"
        update_clusters(str(window))

    def updateLightData():
        for elem in sensors:
            updateData(elem, lat, lon, timezone)

    def updateData(sensor, lat, lon, timezon):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        sensorID = sensors_dict[sens_no]
        cursor.execute('SELECT MAX(unixtime) FROM ' + sensor)
        start = int(cursor.fetchone()[0])
        end = int(time.time())*1000
        limit = (end - start)/300000
        print("limit is:" + str(limit))
        print("Start is:" + str(start))
        print("End is:" + str(end))
        createData(sens_no, start, end,lat, lon, timezon)
        #Save your changes
        connection.commit()



    #############################
    ### PROCESSING LIGHT CODE ###
    #############################

    def movavg(testbed = 'all',mote = 'all',movavg_len=6):

        #determine options
        allmotes = [sensors]
        motelist = []
        for count in range(len(motes)):
            motelist = motelist+motes[count]

        #connect db
        connection=sqlite3.connect('data.db')
        cursor=connection.cursor()

        #initialize
        movavg = dict()
        unixtimes = dict()

        #retrieve unixtimes (to process all raw data)
        for mote in motelist:
            cursor.execute('SELECT MIN(unixtime),MAX(unixtime) FROM '+str(mote))
            unixtimedata = cursor.fetchall()
            unixtimerange = list(unixtimedata[0])
            unixtimes[mote] = unixtimerange

            #determine the moving average using movavg_len
            cursor.execute('SELECT light,unixtime FROM '+str(mote)+' WHERE unixtime>= '+str(unixtimerange[0])+' AND unixtime<= '+str(unixtimerange[1]))        
            alldata = cursor.fetchall()
            movavg[mote] = []
            total = 0
            for count in range(len(alldata)):
                if count < movavg_len:
                    total = total + alldata[count][0]
                else:
                    total = total + alldata[count][0] - alldata[count-movavg_len][0]
                movavg[mote].append([total/movavg_len,alldata[count][1]])

        return movavg

    def insert_movingavg():
        connection=sqlite3.connect('data.db')
        cursor=connection.cursor()
        moving_avg = movavg()  
        light_tables = sensors
        for table in light_tables:
            data = moving_avg[table]
            for elem in data:
                avg = elem[0]
                unix = elem[1]
                cursor.execute('UPDATE ' + str(table) + ' SET movingavg = ' + str(avg) + ' WHERE unixtime = ' + str(unix))
            connection.commit()

    def insert_processed_light(avg_len=3):
        connection=sqlite3.connect('data.db')
        cursor=connection.cursor()
        light_tables = sensors
        for table in light_tables:

            #get threshold time
            cursor.execute('SELECT MIN(unixtime) FROM '+str(table))
            threshold = cursor.fetchall()[0][0]

            #processing
            print 'processing '+str(table)
            cursor.execute('SELECT light, movingavg, unixtime, cluster FROM ' + str(table))
            data = cursor.fetchall()
            i = 1
            while i < len(data):
                if i == len(data)/4:
                    print '25%'
                elif i == len(data)/2:
                    print '50%'
                elif i == 3*len(data)/4:
                    print '75%'
                elif i%5000 == 0:
                    print i,' ',len(data)
                current_light = data[i][0]
                previous_light = data[i-1][0]
                value = abs(current_light - previous_light)
                other = abs(data[i][1] - previous_light) * 2.0
                if value > other:

                    #retrieve closest avg_len number of data to current
                    clust = data[i][3]
                    unix = data[i][2]
                    replace = []
                    retrieved = 'not done'
                    while retrieved == 'not done': #a loop is a day
                        if clust != None:
                            cursor.execute('SELECT light,MAX(unixtime) FROM '+str(table)+' WHERE cluster = '+str(clust)+' AND unixtime < '+str(unix)+' AND unixtime >= '+str(unix-86400000))
                        else:
                            cursor.execute('SELECT light,MAX(unixtime) FROM '+str(table)+' WHERE unixtime< '+str(unix)+' AND unixtime >= '+str(unix-86400000))
                        datum = cursor.fetchall()
                        if datum[0][0] >= 0:
                            replace.append(datum[0][0])
                        unix-=86400000
                        if unix < threshold or abs(data[i][2]-unix) >= 86400000*14:
                            replace = replace + [current_light for n in range(avg_len-len(replace))] 
                            retrieved = 'done'
                        if len(replace) == avg_len:
                            retrieved = 'done'

                    #average
                    replace = sum(replace)/avg_len
                    
                    cursor.execute('UPDATE ' + str(table) + ' SET processed = ' + str(replace) + ' WHERE unixtime = ' + str(data[i][2]))
                    i+=1
                else:
                    cursor.execute('UPDATE ' + str(table) + ' SET processed = ' + str(current_light) + ' WHERE unixtime = ' + str(data[i][2]))
                    i+=1
            cursor.execute('UPDATE ' + str(table) + ' SET processed = ' + str(data[0][0]) + ' WHERE unixtime = ' + str(data[0][2]))
            connection.commit()


    #######################
    ### SMOOTHING CODE ###
    #######################

    def smoothing(sensor, smoothtype, movingStatsWindow=8, expWindow=12, Alpha=0.7):
        """This function is an exterior function that smoothes the light values.
        The arguments to this function can be changed here and then when createLightData()
        runs, it will update the smoothing table values with the new smoothing values.
        moteNum is the sensor number and nasa is a true or false argument for whether it
        is nasa sensors or BEST Lab sensors. The smoothtype asks for exponential or average
        type of smoothing. The remaining arguments are particular types of smoothing values that
        Jacob Richards saw fit. """
        #define arrays
        data1=[]
        time1=[]
        hour1=[]
        ROC1=[]
        RROC1=[]
        mean1=[]
        stdev1=[]
        esmooth1=[]
        output=[]
        nROC1=[]
        nRROC1=[]

        connection=sqlite3.connect('data.db')
        cursor=connection.cursor()
        cursor.execute('SELECT processed, unixtime, hour from %s' %(sensor))
        x=0
        z1=cursor.fetchall()
        ##print len(z)
        for count in z1:
            if float(count[0])==1:
                x+=1
            if int(count[2])>=5 and int(count[2])<=20:
                if float(count[0])<=1:
                    data1.append('nan')
                else:
                    data1.append(float(count[0]))
            elif int(count[2])<5 or int(count[2])>20:
                data1.append(float(count[0]))
            time1.append(float(count[1]))
            hour1.append(float(count[2]))
            
        #print len(data)
        for count in range(len(data1)):
            if time1[count]-time1[count-1]<=6*300000 and data1[count]=='nan':
                if data1[count-1]!='nan':
                    data1[count]=data1[count-1]
                else:
                    data1[count]=1
                #data1[count]=np.mean(data1[count-2:count-1])
            elif time1[count]-time1[count-1]>6*300000 and data1[count]=='nan':
                data1[count]=1
                
        #rate of change
        for t in range(len(data1)-1):
            rate=data1[t+1]-data1[t]
            ROC1.append(rate)
            
        #rate of rate of change
        for n in range(len(ROC1)-1):
            changeofrate=ROC1[n+1]-ROC1[n]
            RROC1.append(changeofrate)
            
        #moving mean and standard deviation
        w= movingStatsWindow
        count=0
        while count<=w-1:
            average=np.mean(data1[count:w])
            std=np.std(data1[count:w])
            mean1.append((average, time1[count]))
            stdev1.append(std)
            count+=1
        count=w
        while count<=(len(data1)-w):
            average=np.mean(data1[count-w:count+w])
            std=np.std(data1[count-w:count+w])
            mean1.append((average, time1[count]))
            stdev1.append(std)
            count+=1
        while count>=len(data1)-w+1 and count<len(data1):
            average=np.mean(data1[count:len(data1)])
            std=np.std(data1[count:len(data1)])
            mean1.append((average,time1[count]))
            stdev1.append(std)
            count+=1
        for count in range(len(data1)):
            if data1[count]=='nan' or mean1[count]=='nan':
                print("WHAT THE HECK")

        p=expWindow
        alpha=Alpha

        for count in range(len(data1)):
            addsum1=0
            for add in range(p-1):
                term=float(alpha)*math.pow((1-float(alpha)),add)*data1[count-add]
                addsum1+=term
            smoothed=addsum1+math.pow((1-float(alpha)),p)*data1[count-p]
            esmooth1.append((smoothed,time1[count]))


        final=[time1,data1,mean1,esmooth1,stdev1]
        if smoothtype=='exponential':
            output=final[3]
        elif smoothtype=='average':
            output=final[2]

        return output


    def smoothingtables():
        """This command smoothes all the BEST lab light data and the
        NASA light data by calling the smoothing function. It performs
        both types of smoothing including exponential and average. """
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        tables = sensors
        types = ['exponential', 'average']
        for table in tables:
            print table
            for element in types:
                connection = sqlite3.connect('data.db')
                cursor = connection.cursor()
                x = smoothing(table, element)
                for part in x:
                    cursor.execute('UPDATE ' + str(table) + ' SET ' + str(element) + ' = ' + str(part[0]) + ' WHERE unixtime = ' + str(part[1]))
                connection.commit()

    #############################
    ### CLUSTERING LIGHT DATA ###
    #############################


    def inter(start,end):
        interval = [start]
        while interval[-1] < end:
            interval.append(interval[-1]+1800000)
        return interval

    def getdeviations(x, mean, stddev):
        return math.fabs(x - mean) / stddev

    def classify(month, table):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        # 24 - 30 min intervals from hours 6 to 18
        intervals_avg = [[] for i in range(24)]
        intervals_std = [[] for i in range(24)]
        uncounted = []
        i = 0
        alldata = [[] for i in range(24)]
        for count in range(len(alldata)):
            alldata[count] = [[] for i in range(3)]
        while i < len(month) - 1:
            unix = month[i]
            unix_next = month[i+1]
            cursor.execute('SELECT AVG(light),hour,AVG(minute) FROM ' + str(table) + ' WHERE unixtime >= ' + str(unix) + ' AND unixtime < ' + str(unix_next) + ' AND hour >= 6 AND hour < 18')
            data = cursor.fetchall()
            if data[0] != (None,None,None):
                avg = data[0][0]
                cursor.execute('SELECT SUM((light- ' + str(avg) + ')*(light - ' + str(avg) + '))/COUNT(light) FROM ' + str(table) + ' WHERE unixtime >= ' + str(unix) + ' AND unixtime < ' + str(unix_next) + ' AND hour >= 6 AND hour < 18')
                variance = cursor.fetchall()
                std = np.sqrt(variance)
                if data[0][2] < 30:
                    intervals_avg[2*(data[0][1]-6)].append(avg)
                    intervals_std[2*(data[0][1]-6)].append(std)
                elif data[0][2] >= 30 and data[0][2] < 60:
                    intervals_avg[2*(data[0][1]-6)+1].append(avg)
                    intervals_std[2*(data[0][1]-6)+1].append(std)
                else:
                    uncounted.append(data[0])
            i+=1
        return intervals_avg,intervals_std


    def cluster(table,start, end, cen_num = 3,iter_num = 100,n = 20):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        # cluster training period (dec 1 to apr 1)
        avgs,stds = classify(inter(start,end), table)
        a = 0
        while a < len(avgs):
            med = np.mean(avgs[a])
            std = np.std(avgs[a])
            i = 0
            while i < len(avgs[a]):
                if getdeviations(avgs[a][i], med, std) > 1 or stds[a][i] > avgs[a][i]:
                    avgs[a].pop(i)
                    stds[a].pop(i)
                    i-=1
                i+=1
            a+=1

        #colors
        cs = [[1,0,0],[0,1,0],[0,0,1],[0,1,1],[1,1,0],[1,0,1],[0,0,0]]
        allcentroids = []
        #run kmeans (choose int_num and cen_num and iter_num)
        for int_num in range(24):
            #cen_num = 3
            #iter_num = 300
            #run kmeans n-times (different initialization points each time)
            #n = 60
            centroids = []
            ##stdss = stds[int_num]
            stdss = [stds[int_num][count]/avgs[int_num][count] for count in range(len(stds[int_num]))]
            allpoints = np.array(zip(avgs[int_num],stdss))#stds[int_num]))
            if n > 1:
                Js = []
                labs = []
                plt.figure()
                plt.scatter(avgs[int_num],stdss,c=cs[6])
                for i in range(n):
                    dists = []
                    centroid,lab = kmeans2(allpoints,cen_num,iter_num,minit='points')
                    labs.append(lab)
                    centroids.append(centroid)
                    x = list(centroids[i][:,0])
                    y = list(centroids[i][:,1])
                    a = list(centroids[i][:,0])
                    b = list(centroids[i][:,1])
                    for rep in range(len(a)):
                        for cen in range(len(a)-1):
                            if a[cen] > a[cen+1]:
                                x[cen] = a[cen+1]
                                y[cen] = b[cen+1]
                                x[cen+1] = a[cen]
                                y[cen+1] = b[cen]              
                            a = list(x)
                            b = list(y)
                    #plt.scatter(x,y,s=30*(n-i),c=cs[:cen_num])
                    for count in range(len(allpoints)):
                        dist = np.linalg.norm(allpoints[count]-centroid[lab[count]])
                        dists.append(dist)
                    J = 1.0/float(len(allpoints))*np.sum(np.array(dists)**2)
                    Js.append(J)
                # centroid stores all n centroids
                centroid = centroids
                # just the one with min J
                plt.scatter(centroid[np.argmin(Js)][:,0],centroid[np.argmin(Js)][:,1],s=200,c=cs[:cen_num])
                colors = ([(cs[:cen_num])[j] for j in labs[np.argmin(Js)]])
                plt.scatter(avgs[int_num],stdss,c=colors)
                centroid = centroid[np.argmin(Js)]
            else:
                centroid,lab = kmeans2(allpoints,cen_num,iter_num,minit='points')
                colors = ([(cs[:cen_num])[j] for j in lab])
                plt.scatter(avgs[int_num],stds[int_num],c=colors)
                plt.scatter(centroid[:,0],centroid[:,1],s=100,c=cs[:cen_num])
                #plt.savefig('D:/Ben/Downloads/Classify/cluster.png')
                dists = []
                for count in range(len(allpoints)):
                    dist = np.linalg.norm(allpoints[count]-centroid[lab[count]])
                    dists.append(dist)
                J = 1.0/float(len(allpoints))*np.sum(np.array(dists)**2)
            allcentroids.append(centroid)
        return allcentroids
        #plt.show()


    def whereisit(light,interval,acs,n=3):
        avg = np.mean(light)
        std = np.std(light)
        point = np.array([avg,std])
        dists = []
        for count in range(n):
            dist = np.linalg.norm(point - acs[interval][count])
            dists.append(dist)
        tag = interval*n+np.argmin(dists)
        return tag


    def intervals(table, start, end):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        cursor.execute('SELECT light, hour, minute, day, unixtime FROM ' + str(table) + ' WHERE unixtime > ' + str(start) + ' AND unixtime < ' + str(end) + ' AND hour >= 6 AND hour < 18')
        data = cursor.fetchall()
        intervals = [[] for i in range(24)]
        for i in range(24):
            intervals[i].append([])
        current = data[0][3]
        counter = [0 for i in range(24)]
        for count in range(len(data)):
            if data[count][2] < 30:
                if current != data[count][3]:
                    counter[2*(data[count][1]-6)]+=1
                    intervals[2*(data[count][1]-6)].append([])
                intervals[2*(data[count][1]-6)][counter[2*(data[count][1]-6)]].append(data[count])
            elif data[count][2] >= 30 and data[count][2] < 60:
                if current != data[count][3]:
                    counter[2*(data[count][1]-6)+1]+=1
                    intervals[2*(data[count][1]-6)+1].append([])
                intervals[2*(data[count][1]-6)+1][counter[2*(data[count][1]-6)+1]].append(data[count])
            current = data[count][3]
        return intervals

    def create_cluster(table, start, end, cluster_results):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        results = intervals(table, start, end)
        #0-23 light intervals
        interval = 0
        for elem in results:
            #Each 30 minute interval
            for element in elem:
                lights = []
                unixtimes = []
                if len(element) != 0:
                    first = element[0][4]
                    last = element[-1][4]
                    #if last - first <= 1800000:
                        #Every tuple
                    for i in element:
                        lights.append(i[0])
                        unixtimes.append(i[4])
                    cluster = whereisit(lights, interval,cluster_results)
                    for time in unixtimes:
                        cursor.execute('UPDATE ' + str(table) + ' SET cluster = ' + str(cluster) + ' WHERE unixtime = ' + str(time))
                    connection.commit()
            interval+=1            


    def update_clusters(table):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        tables = [x for x in sensors if x!= str(windows)]
        for other_tables in tables:
            a = cursor.execute('SELECT cluster, unixtime FROM ' + str(table) + ' WHERE cluster >= 0')
            y = a.fetchall()
            for elem in y:
                c = cursor.execute('SELECT unixtime FROM ' +str(other_tables)+ ' WHERE unixtime >= -150000 + ' + str(elem[1]) + ' AND unixtime <= 150000 + ' + str(elem[1]))
                x = c.fetchall()
                if len(x) > 0:
                    cursor.execute('UPDATE ' + str(other_tables) + ' SET cluster = ' + str(elem[0]) + ' WHERE unixtime >= -150000 + ' + str(elem[1]) + ' AND unixtime < 150000 + ' + str(elem[1]))  
            connection.commit()    


