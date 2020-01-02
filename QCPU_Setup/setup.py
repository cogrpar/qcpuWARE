import os
import subprocess
import sys
#library to run terminal commands
#make sure that this code is run as root...
################################################################################################################


#start by installing a webserver application and creating the webserver files which allow your computer to communicate with the QCPU
installWS = subprocess.Popen(["apt-get install apache2 php libapache2-mod-php libatlas-base-dev", "-y"], shell=True)
installWS.wait()
#create files
file = open("/var/www/html/storage.php","w+")
file.write('''<?php
//this script allows the users computer to communicate with the QCPU...
$var1 = $_REQUEST['input'];
$WriteMyRequest=$var1;
file_put_contents('storage.txt', ' ', FILE_APPEND);
file_put_contents('storage.txt', $WriteMyRequest, FILE_APPEND);
?>''')
file.close()
store = open("/var/www/html/storage.txt","w+")
store.write(".")
store.close()

usr = " "
from os import path
while True:
    usr = input("username:")
    usrLoc = ["/home/", usr, "/.local/lib/python"]
    userLocate = ''.join(str(v) for v in usrLoc)
    if(path.exists("guru99.txt")):
        print ("valid username")
        break
    else:
        print ("invalid username...  ")
        
#now copy the dwave python librarys to the correct locations
for filename in os.listdir("DWave-library/site-packages"):
    pyVer = sys.version
    pyVerSplit = pyVer.split(" ")
    pyVer = pyVerSplit[0]
    pyVerSplit = pyVer.split(".")
    pyVer = (pyVerSplit[0] + "." + pyVerSplit[1])
    oLoc = ["DWave-library/site-packages/", filename]
    nLoc = ["/home/", usr, "/.local/lib/python", pyVer, "/site-packages/"]
    dir1 = ''.join(str(v) for v in oLoc)
    dir2 = ''.join(str(w) for w in nLoc)
    mvSite = subprocess.Popen(["mv", dir1, dir2])
    mvSite.wait()
    print ("moved ", dir1, " to new location: ", dir2)
    
for filename in os.listdir("DWave-library/dist-packages"):
    pyVer = sys.version
    pyVerSplit = pyVer.split(" ")
    pyVer = pyVerSplit[0]
    pyVerSplit = pyVer.split(".")
    pyVer = (pyVerSplit[0] + "." + pyVerSplit[1])
    oLoc = ["DWave-library/dist-packages/", filename]
    nLoc = ["/usr/local/lib/python", pyVer, "/dist-packages/"]
    dir1 = ''.join(str(v) for v in oLoc)
    dir2 = ''.join(str(w) for w in nLoc)
    mvDist = subprocess.Popen(["mv", dir1, dir2])
    mvDist.wait()
    print ("moved ", dir1, " to new location: ", dir2)

    
    

#append command to start code on boot
onBoot = open("/etc/crontab", "a+")
progrms = [] #put the name of each program in this list to write them to the contrab file so they run on boot...
for progrm in progrms:
    onBoot.write("@reboot " + progrm)
onBoot.close()



#setup DWave connection and ping the machine
print ("if you are not sure how to fill out these fields, please refer to https://docs.ocean.dwavesys.com/en/latest/overview/dwavesys.html")
setupConnec = subprocess.Popen(["dwave config create"], shell=True)
setupConnec.wait()
ping = subprocess.Popen(["dwave ping"])
ping.wait()


#all done
print ("setup complete")
