import os
import subprocess
import sys
#library to run terminal commands
#make sure that this code is run as root...
################################################################################################################

#check sys.argv

#if install
if ("install" in sys.argv[1]):
	#start by installing a webserver application and creating the webserver files which allow your computer to communicate with the QCPU
	installWS = subprocess.Popen(["apt-get install apache2 php libapache2-mod-php libatlas-base-dev", "-y"], shell=True)
	installWS.wait()
	#create files
	file = open("/var/www/html/storage.php","w+")
	file.write('''<?php
	//this script allows the users computer to communicate with the QCPU...
	if($_REQUEST['input']){ //append to the file with the solver input
	    $var1 = $_REQUEST['input'];
	    $WriteMyRequest=$var1;
	    file_put_contents('/var/www/html/storage.txt', $WriteMyRequest);
	    echo "printed";
	}
	if($_REQUEST['clrRes']){ //clear result file
	    file_put_contents('/var/www/html/results.txt', ' ');
	    echo "cleared";
	}
	?>''')
	file.close()
	store = open("/var/www/html/storage.txt","w+")
	store.write(".")
	store = open("/var/www/html/results.txt", "w+")
	store.write(".")
	store.close()

	#give read/write permissions to the server user:
	usrPer = subprocess.Popen(["chown www-data /var/www/html/*"], shell=True)
	usrPer.wait()



	usr = " "
	from os import path
	while True:
		usr = input("username:")
		usrLoc = ["/home/", usr, "/.local/lib/"]
		userLocate = ''.join(str(v) for v in usrLoc)
		if(path.exists(userLocate)):
			print ("valid username")
			break
		else:
			print ("invalid username...  ")
		
	#now check to see if we are using a raspberry pi (or similar device) or not
	#the pi has trouble using pip to install the dwave libraries, so we copy the prebuilt librariess to the correct files
	#for other platforms, we can just use pip
	while True:
		platform = input("Are you using a raspberry pi or other device with similar architecture? (y = yes, n = no):")
		if (platform == "y" or platform == "n"):
			break
		else:
			print("err; pease enter either n or y\n")
		
	if (platform == "y"):
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
		#import cloud client
		cloud = subprocess.Popen(["pip3 install dwave-cloud-client"], shell=True)
		cloud.wait()
		#import sympy
		sym = subprocess.Popen(["pip3 install sympy"], shell=True)
		sym.wait()
	    
	if (platform == "n"): #if other platform, just use pip
		pip_method = subprocess.Popen(["pip3 install dwave-ocean-sdk"], shell=True)
		pip_method.wait()
		#import sympy
		sym = subprocess.Popen(["pip3 install sympy"], shell=True)
		sym.wait()
	    
	    
	    
	#get root password, so that we can use it to execute solver as root on startup
	root_pass = input("root password:\n")
	#append command to start code on boot
	onBoot = open("/home/" + usr + "/.bashrc", "a+")
	prg1 = "echo " + root_pass + " | sudo -S python3 " + os.path.dirname(os.path.abspath(__file__)).replace("setup.py", "") + "/solver/qcpuWare.py" #get the location of the solver file
	progrms = [prg1] #put the name of each program in this list to write them to the contrab file so they run on boot...
	for progrm in progrms:
		onBoot.write(progrm + "\n")
	onBoot.close()
	print(prg1)




	#setup DWave connection and ping the machine
	print ("if you are not sure how to fill out these fields, please refer to https://docs.ocean.dwavesys.com/en/latest/overview/dwavesys.html")
	conec = ["sudo --u ", usr, " dwave config create"]
	connec = ''.join(str(v) for v in conec)
	setupConnec = subprocess.Popen([connec], shell=True)
	setupConnec.wait()
	pinng = ["sudo --u ", usr, " dwave ping"]
	pinnng = ''.join(str(v) for v in pinng)
	ping = subprocess.Popen([pinnng], shell=True)
	ping.wait()


	#all done
	print ("setup complete")


#if update
if ("update" in sys.argv[1]):
	#get file location
	path = os.path.dirname(os.path.abspath(__file__)).replace("setup.py", "")
	print(path)
	path = path.replace("/QCPU_Setup", "")
	print(path)
	#remove autorun code
	usr = " "
	from os import path
	while True:
		usr = input("username:")
		usrLoc = ["/home/", usr, "/.local/lib/"]
		userLocate = ''.join(str(v) for v in usrLoc)
		if(path.exists(userLocate)):
			print ("valid username")
			break
		else:
			print ("invalid username...  ")

	auto = open("/home/" + usr + "/.bashrc", "a+")

	root_pass = input("root password:")

	content = auto.read()
	content = content.replace("echo " + root_pass + " | sudo -S python3 " + os.path.dirname(os.path.abspath(__file__)).replace("setup.py", "") + "/solver/qcpuWare.py", "")

	auto.close()
	writeAuto = open("/home/" + usr + "/.bashrc", "w")
	writeAuto.write(content)
	writeAuto.close()

	#change dir name
	cd = subprocess.Popen(["(cd " + "/home/" + usr + " && mv qcpuWARE null)"], shell=True)
	cd.wait()
	
	#now clone a new repo and delete this one (and start setup.py install again)
	clone = subprocess.Popen(["(cd /home/" + usr + " && git clone https://github.com/cogrpar/qcpuWARE.git)"], shell=True)
	clone.wait()
	os.system("(cd /home/" + usr + "/qcpuWare/QCPU_Setup/ && python3 setup.py install)")

	os.system("rm -R /home/" + usr + "/null")
	

#invalid arg
else:
	print("invalid arg: " + sys.argv[1])
