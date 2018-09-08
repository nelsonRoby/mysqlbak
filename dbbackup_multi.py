#!/usr/bin/python
# -*- coding:utf-8 -*

import os,time
import ConfigParser
import tarfile
import logging
from logging.handlers import RotatingFileHandler

#Get the backup db name
def getbakdb(skipdb):
    skipstr = skipdb.split('|')
    skipstr.extend(['Database','information_schema'])
    bakdb = []
    cmdstr= "mysql -h%s -P%s -u%s -p'%s' -e 'show databases;' " %(DBHOST,DBPORT,DBUSER,DBPASS)
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
    cmdstr = "mysqldump -h%s -P%s -u%s -p'%s' --databases %s  > %s " %(DBHOST,DBPORT,DBUSER,DBPASS,bakdb,BAKNAME)
    try:
        os.system(cmdstr)
        logger.info("Sucessfully to dump the mysql database " + bakdb )
    except:
        logger.error("dump the mysql database " + bakdb)


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
    	logger.info("delete the file " +BAKTAR)

def cleanlog():
    cmdstr = "find %s -maxdepth 1 -type d -name '20*'  -mtime +%s | xargs rm -fr" %(BAKDIR,KEEPDAY)
    cmdstr2 = "find %s -maxdepth 1 -type d -name '20*' -mtime +%s "  %(BAKDIR,KEEPDAY)
    output = os.popen(cmdstr2)
    logger.info(output.read())
    
    try:
    	os.system(cmdstr)
    	logger.info("delete " + KEEPDAY + " days ago files about backup database.")
    except:
    	logger.error("faild to delete the history backup file .")


def log2f():
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    #handler = logging.FileHandler(LOGFILE)
    #handler.setLevel(logging.INFO)
    #handler.setFormatter(formatter)
    rfh = RotatingFileHandler(LOGFILE,maxBytes=1024*1024,backupCount=5)
    rfh.setLevel(logging.INFO)
    rfh.setFormatter(formatter)
    
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(rfh)
    logger.addHandler(console)
    
    return  logger

if __name__ == '__main__':
    skipdb="mysql|performance_schema|test|sys"
    
    config = ConfigParser.ConfigParser()
    local_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    config_ini = local_path + "/config.ini"
    config.read(config_ini)
    nodes = config.sections()
    
    BAKDIR = config.get("global","bakdir")
    KEEPDAY = config.get("global","keepday")
    LOGFILE = config.get("global","logfile")
    
    NOWDATE = time.strftime('%Y%m%d')
    NOWTIME = time.strftime('%Y%m%d-%H%M%S')
    BAKPATH = BAKDIR + NOWDATE + "/"
    WEEKDAY = int(time.strftime('%u'))

    logger = log2f()
    if WEEKDAY == 7:
        cleanlog()
    
    if not os.path.exists(BAKPATH):
        os.makedirs(BAKPATH)
        os.chdir(BAKPATH)
        logger.info("Creating the folder: " + BAKPATH)
    	
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
        msg = "get the backup database list %s of node (%s)" %(getdb,sc)
        logger.info(msg)
        for db in getdb:
        	backupdb(db)
        gzfile(sc)
