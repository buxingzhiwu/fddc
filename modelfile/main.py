#-*- coding: utf-8 -*-
import subprocess, sys, os, time, socket
import shutil

########################################################################################################################
if os.path.exists("../submit/"):
    shutil.rmtree("../submit/")
os.mkdir("../submit/")

if os.path.exists("./ht/tem/"):
    shutil.rmtree("./ht/tem/")
os.mkdir("./ht/tem/")

if os.path.exists("./zjc/tem/"):
    shutil.rmtree("./zjc/tem/")
os.mkdir("./zjc/tem/")

if os.path.exists("./cz/tem/"):
    shutil.rmtree("./cz/tem/")
os.mkdir("./cz/tem/")

if os.path.exists("./InformationExtraction/data/"):
    shutil.rmtree("./InformationExtraction/data/")
os.mkdir("./InformationExtraction/data/")

if os.path.exists("./InformationExtraction/jieba.cache"):
    os.remove("./InformationExtraction/jieba.cache")


########################################################################################################################
cmd = 'python3 ./zjc/run_zjc.py'
subprocess.call(cmd, shell=True)

cmd = 'python3 ./ht/run_ht.py'
subprocess.call(cmd, shell=True)

cmd = 'python3 ./cz/run_cz.py'
subprocess.call(cmd, shell=True)

