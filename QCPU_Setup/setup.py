import os
import subprocess
#library to run terminal commands
#make sure that this code is run as root...
################################################################################################################


#start by installing a webserver application and creating the webserver files which allow your computer to communicate with the QCPU
installWS = subprocess.Popen(["apt-get install apache2 php libapache2-mod-php", "-y"])
installWS.wait()
#create files
file = open("/var/www/html/storage.php","w+")
file.write('''<?php
//this script allows the users computer to communicate with the QCPU...
?>''')
file.close()


#now build the dwave python library
for filename in os.listdir("DWave-library/"):
    installDWave = subprocess.Popen(["pip3 install " + filename])
    installDWave.wait()