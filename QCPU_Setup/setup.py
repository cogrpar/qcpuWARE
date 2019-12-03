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


#now build the dwave python library
packages = ["dwave-qbsolv", "dwave-cloud-client", "dwave-embedding-utilities", "dwave-micro-client", "dwave-micro-client-dimod", "dwave-networkx", "dwave-sapi-dimod", "dwave-sdk", "dwave-system", "dwavebinarycsp"] 
for package in packages:
    installDWave = subprocess.Popen(["pip3 install " + package])
    installDWave.wait()

    

#append command to start code on boot
onBoot = open("/etc/crontab", "a+")
progrms = [] #put the name of each program in this list to write them to the contrab file so they run on boot...
for progrm in progrms:
    onBoot.write("@reboot " + progrm)
onBoot.close()
