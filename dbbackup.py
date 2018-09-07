#!/usr/bin/python
# This script to used for mysql database backup
# Only for the capacity less than 2G and MyISAM storage engine
# -*- coding:utf-8 -*

import os,time
import ConfigParser
import tarfile
import shutil

# DBHOST = 'localhost'
# DBUSER = 'root'
# DBPASS = '123456'
# DBPORT = 3306
# BAKDIR = "/backup/mysql/"

config = ConfigParser.ConfigParser()
local_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
config_ini = local_path + "/config.ini"
config.read(config_ini)

DBHOST = config.get("dbinfo","host")
DBUSER = config.get("dbinfo","user")
DBPASS = config.get("dbinfo","pass")
DBPORT = config.get("dbinfo","port")
BAKDIR = config.get("global","bakdir")
LOGDIR = BAKDIR + "binlog/"

NOWDATE = time.strftime('%Y%m%d')
NOWTIME = time.strftime('%Y%m%d-%H%M%S')
BAKPATH = BAKDIR + NOWDATE + "/"
NOWHOUR = int(time.strftime('%H'))

if not os.path.exists(BAKPATH):
    os.makedirs(BAKPATH)
    os.chdir(BAKPATH)
    print("creating the %s folder\n") %(BAKPATH)

if not os.path.exists(LOGDIR):
    os.makedirs(LOGDIR)

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

## flush log before copy binlog
#
def flushlog():
    cmdstr = "mysql -u%s -p'%s' -e 'flush logs;' " %(DBUSER,DBPASS)
    if os.system(cmdstr):
        return 1
    else:
        return 0

## full backup the MySQL
#
def backupdb(bakdb):
    BAKNAME = BAKPATH + NOWTIME + bakdb + ".sql"
    cmdstr = "mysqldump -u%s -p'%s' --databases %s --flush-logs > %s " %(DBUSER,DBPASS,bakdb,BAKNAME)
    os.system(cmdstr)
    BAKTAR = BAKPATH + NOWDATE + ".tar"
    tar = tarfile.open(BAKTAR,"a:")
    tar.add(BAKNAME)
    tar.close()
    if os.path.exists(BAKTAR):
        os.unlink(BAKNAME)

def gzfile():
    BAKTAR =  BAKPATH + NOWDATE +".tar"
    BAKZIP = BAKTAR + ".gz"
    tar = tarfile.open(BAKZIP,"w:gz")
    tar.add(BAKTAR)
    tar.close()
    if os.path.exists(BAKZIP):
        os.unlink(BAKTAR)

## copy the binlog file
#
def copybinlog():
    cmdstr = "mysql -u%s -p'%s' -e 'show variables' " %(DBUSER,DBPASS)
    data = os.popen(cmdstr).readlines()
    for line in data:
        str1 = line.split('\t')
        if str1[0] == "datadir":
            DATADIR = str1[1].replace('\n','')
            DBINDFILE = DATADIR + "mysql-bin.index"
            #print(DBINDFILE)
            #break
        if str1[0] == 'log_bin_index':
            str2 = str1[1].replace('\n', '')
            if not str2 == "":
                DBINDFILE = str2

    if os.path.exists(DBINDFILE):
        fp = open(DBINDFILE,'r')
        lines = fp.readlines()
        num = len(lines)
        #print(num)
        i = 1
        for file in lines:
            if i + 1 > num:
                break
            i = i + 1
            #print(file)
            f1 = file.replace('\n','')
            srcfile = DATADIR + f1
            dstfile = LOGDIR + f1
            if not os.path.exists(dstfile):
                shutil.copyfile(srcfile,dstfile)

if __name__ == '__main__':
    if NOWHOUR == 02 :
        skipdb="mysql|performance_schema|test"
        getdb = getbakdb(skipdb)
        for db in getdb:
            backupdb(db)
        gzfile()

    elif NOWHOUR % 4 == 0 :
        flushlog()
        copybinlog()
