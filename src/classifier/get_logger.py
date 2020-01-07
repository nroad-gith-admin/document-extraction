# Logger Module
'''
This is logging module. It defines the GetLogger class in which you can we have getlogger function that is used to setup the logging functionality

e.x:
    obj = GetLogger("prashant","mylog.log",2)
    logger = obj.getlogger()
    logger.info("hello")
    logger.error("Oh..")
'''

# Maintainer, contributors, etc.
import logging
from logging.handlers import RotatingFileHandler
import time
import os

class GetLogger():
    def __init__(self,name=None ,logfileloc=None, debuglevel=None):
        if name== None and logfileloc ==None :
            raise  Exception("Expected parameter: name, loffileloc and optional parameter debuglevel ")
        if debuglevel==None:
            debuglevel = 2
        self.name = name

        # if not os.path.isdir("".join(logfileloc.split("\\")[:-1])):
        #     raise Exception("log file path is incorrect : "+ str(logfileloc))
        self.logfileloc = logfileloc
        self.debuglevel = debuglevel
        self.logger=None


    def getlogger(self):
        '''
        This function does the logging setup.
        If debuglevel is defined as 0 it will create a Null Handler.
        If debuglevel is 1, it will create a Error handler.
        If debuglevel is 2, it will create a Debug handler
        By default it uses the formatter: time, filename, line number, level name and message
        The max file size is 5*1024*1024
        :return: logger object
        '''

        if self.logger==None:
            self.logger=logging.getLogger(self.name)
            self.logger.setLevel(logging.DEBUG)
            formatter_=logging.Formatter('%(asctime)s - %(filename)s - %(lineno)i - %(levelname)s - %(message)s',"%Y-%m-%d %H:%M:%S")
            formatter_.converter=time.gmtime
            if self.debuglevel == 0:
                handler=logging.NullHandler()
            elif self.debuglevel == 1:
                try:
                    handler=RotatingFileHandler(self.logfileloc,mode='a',maxBytes=5*1024*1024,backupCount=500,encoding=None,delay=0)
                    handler.setLevel(logging.ERROR)
                except Exception as e:
                    self.logger.error("Exception while creating handler in debug level 1 : " + str(e))
                    raise Exception("Exception while creating handler in debug level 1 : " + str(e))

            elif self.debuglevel == 2:
                try:
                    handler=RotatingFileHandler(self.logfileloc,mode='a',maxBytes=5*1024*1024,backupCount=500,encoding=None,delay=0)
                    handler.setLevel(logging.DEBUG)
                except Exception as e:
                    self.logger.error("Exception while creating handler in debug level 2 : " + str(e))
                    raise Exception("Exception while creating handler in debug level 2 : " + str(e))
            handler.setFormatter(formatter_)
            self.logger.addHandler(handler)
        loggerobj=self.logger
        if loggerobj==None:
            raise Exception("Something failed while creating the logger object.File location is incorrect or debug level is incorrct. Debug level can be 0,1 or 2. 0 for Null handler, 1 for error handler and 2 for debug handler.")
        return loggerobj


if __name__=="__main__":
    obj = GetLogger("prashant","../mylog.log",2)
    logger = obj.getlogger()
    logger.info("hello")