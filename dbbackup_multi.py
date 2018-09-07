#!/usr/bin/python
# -*- coding:utf-8 -*

import os,time
import ConfigParser
import tarfile
import shutil

def init():
	global config,nodes


#########
#Get the backup db name
def getbakdb(skipdb):
    skipstr = skipdb.split('|')
    skipstr.extend(['Database','information_schema'])
    bakdb = []
    cmdstr= "mysql -u%s -p'%s' -e 'show databases;' " %(DBUSER,DBPASS)
    lines = os.popen(cmdstr).readlines()
    for i in lines:
        str1 = i.replace('\n','')
        if str1 not in skipstr:
            bakdb.append(str1)
    return bakdb


## full backup the MySQL
#
def backupdb(bakdb):
    BAKNAME = BAKPATH + NOWTIME + bakdb + ".sql"
    cmdstr = "mysqldump -u%s -p'%s' --databases %s  > %s " %(DBUSER,DBPASS,bakdb,BAKNAME)
    os.system(cmdstr)


def gzfile(sc):
	BAKTAR = BAKPATH + NOWDATE + sc + ".tar"
	BAKZIP = BAKTAR + ".gz"
	tar = tarfile.open(BAKTAR,"a:")
	os.chdir(BAKPATH)
	for f in os.listdir(BAKPATH):
		if os.path.splitext(f)[1] == ".sql":
			tar.add(f,recursive=False)
			os.unlink(f)
	tar.close()

	tar2 = tarfile.open(BAKZIP,"w:gz")
	tar2.add(BAKTAR)
	tar2.close()
	if os.path.exists(BAKTAR):
		os.unlink(BAKTAR)
		
if __name__ == '__main__':
	skipdb="mysql|performance_schema|test|sys"
	
	config = ConfigParser.ConfigParser()
	local_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
	config_ini = local_path + "/config.ini"
	config.read(config_ini)
	nodes = config.sections()
	
	BAKDIR = config.get("global","bakdir")

	NOWDATE = time.strftime('%Y%m%d')
	NOWTIME = time.strftime('%Y%m%d-%H%M%S')
	BAKPATH = BAKDIR + NOWDATE + "/"

	if not os.path.exists(BAKPATH):
		os.makedirs(BAKPATH)
		os.chdir(BAKPATH)
		print("creating the %s folder\n") %(BAKPATH)
		
	for n in nodes:
		if n == 'global':
			continue
		else:
			sc = n	
		DBHOST = config.get(sc,"host")
		DBUSER = config.get(sc,"user")
		DBPASS = config.get(sc,"pass")
		DBPORT = config.get(sc,"port")

		getdb = getbakdb(skipdb)
		for db in getdb:
			backupdb(db)
		gzfile(sc)
