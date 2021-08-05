# coding: utf-8
import os, atexit
import datetime

import config_manager

file_log = None
name_log = 'FMC.log'

def init_log():
    global file_log
    atexit.register(onExit_log)
    file_log = open(name_log, 'a')
    write_log('--------------------------------------------------')
    write_log('Execute ' + config_manager.name_app)
    write_log(str(datetime.datetime.now()))
    
    
def write_log(log):
    global file_log
    log = str(log)
    print(log)
    file_log.write(log+'\n')
    
    
def onExit_log():
    global file_log
    file_log.close()

init_log()
# -------------------------- debug

def main():
    write_log('log_manager test')

if __name__ == '__main__':
    main()