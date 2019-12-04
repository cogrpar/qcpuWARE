import os
import subprocess
#library to run terminal commands
#make sure that this code is run as root...
################################################################################################################


#start by installing a webserver application and creating the webserver files which allow your computer to communicate with the QCPU
installWS = subprocess.Popen(["apt-get install apache2 php libapache2-mod-php", "-y"], shell=True)
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


#make sure swig is installed:
swig = subprocess.check_output(["swig"])
if ("not found" in swig):
    print ("It looks like you don't have SWIG installed.  Please install it to continue.  If you are on a pi or similar device, see https://github.com/Yadoms/yadoms/wiki/Build-on-RaspberryPI for installing SWIG.  Otherwise, try 'apt-get install swig'.  Once you have SWIG installed, rerun this script.")
    quit()


#now build the dwave python library
packages = ["dwave-qbsolv", "dwave-cloud-client", "dwave-embedding-utilities", "dwave-micro-client", "dwave-micro-client-dimod", "dwave-networkx", "dwave-sapi-dimod", "dwave-sdk", "dwave-system", "dwavebinarycsp", "dwave-hybrid", "DWave-library/dwave-tabu-0.2.1.tar.gz"] 
for package in packages:
    installDWave = subprocess.Popen(["pip3 install " + package], shell=True)
    installDWave.wait()

    

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
