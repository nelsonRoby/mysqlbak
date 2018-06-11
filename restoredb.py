#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: Nelson 
# @Time : 2018/4/16 9:37
# @File : restoredb.py

import os,time,sys
import tarfile
import shutil

DBHOST = 'localhost'
DBUSER = 'root'
DBPASS = '123456'
DBPORT = 3306

BAKDIR = "/backup/mysql/"
LOGDIR = BAKDIR + "binlog/"
NOWDATE = time.strftime('%Y%m%d')
BAKPATH = BAKDIR + NOWDATE + "/"

###
# extract from backup file and import the sql file
#

#found back file
def fndfile():
    j=0
    file = []
    for(root,dirs,files) in os.walk(BAKPATH):
        for i in files:
            if i.endswith(".tar.gz"):
                j += 1
                file.append(os.path.join(root,i))
    return file

#restore from tar file
def rftf(tf):
    print("extract the backup file...")
    tar = tarfile.open(tf, 'r:gz')
    tar.extractall(path='/')
    tar.close()
    xf = tf[:-3]
    if os.path.exists(xf):
        tar1 = tarfile.open(xf,"r")
        tar1.extractall(path='/')
        tar1.close()

    print("import the mysql file...")
    for(root,dirs,files) in os.walk(BAKPATH):
        for f in files:
            if f.endswith(".sql"):
                DBNAME = f.split(".")[0][15:]
                cmdstr = "/usr/bin/mysql -u%s -p%s %s < %s " % (DBUSER, DBPASS, DBNAME,os.path.join(root,f))
                print(cmdstr)
                if os.system(cmdstr) ==0 :
                    print("Sucessfully to import full mysql backup")
                    os.unlink(os.path.join(root,f))
                else:
                    print("Fail to import sql file")
                    #sys.exit(1)

##import the binlog
def iptlog(dotime):
    fsttime = int(time.mktime(time.strptime(dotime,'%Y-%m-%d')))
    endtime = int(time.mktime(time.strptime(dotime,'%Y-%m-%d %H:%M')))
    for(root,dirs,files) in os.walk(LOGDIR):
        for i in files:
            fp = os.path.join(root,i)
            ft = os.stat(fp)
            fmt = ft.st_mtime
            if ft.st_size < 170:
                continue
            elif  fmt > fsttime and fmt < endtime:
                cmdstr = "mysqlbinlog %s | mysql -u%s -p%s" %(fp,DBUSER,DBPASS)
                os.system(cmdstr)


def main():
    #get tar file
    file = fndfile()
    fn = len(file)

    if fn == 0 :
        print("I haven't found your backup files.")
    elif fn == 1 :
        print("I have found one backup file: %s !\n") %(file[0])
        geta = raw_input("Do you want to restore the backup [Y/n]:")
        if geta == "Y" or geta == "y" or geta == "Yes" or geta == "yes" :
            #restore the file
            rftf(file[0])
        else:
            print("Reject to restore the backup file.")
            sys.exit(1)

    elif fn > 1 :
        print("I have found multiple backup files.\n")
        root = os.path.dirname(file[0])
        for f in file:
            print(f)
        while True:
            getn = raw_input("Please input the full path of backup file:")
            f2 = getn
            if os.path.exists(f2):
                #restore from tar file
                rftf(f2)
            else:
                print("Your input file hasn't found.\n")
                continue


if __name__ == "__main__":
    #this way to go
    main()





