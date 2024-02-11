# log.py - Logging Module
# 
# 
# Copyright (C) 2011 University of Southern California.
# All rights reserved.
#
# Redistribution and use in source and binary forms are permitted
# provided that the above copyright notice and this paragraph are
# duplicated in all such forms and that any documentation, advertising
# materials, and other materials related to such distribution and use
# acknowledge that the software was developed by the University of
# Southern California, Information Sciences Institute.  The name of the
# University may not be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND WITHOUT ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#
# Author: Arun Viswanathan (aviswana@usc.edu)
#------------------------------------------------------------------------------
import logging
import logging.handlers
import os

LOGDIR = "logs"
BLOGFILE = LOGDIR + os.path.sep + "behaviorlog" 
SLOGFILE = LOGDIR + os.path.sep + "statelog" 

class Log:

    # Logging Levels
    # Specifying a level (l) causes all levels >= l to be printed
    LOGLEVELS = {
                 'fine'    : 5,
                 'debug'   : logging.DEBUG, #10
                 'state'   : 15,
                 'info'    : logging.INFO,  #20
                 'warning' : logging.WARNING, #30
                 'error'   : logging.ERROR,    #40 
                 'critical': logging.CRITICAL, #50
                 'behavior': 90, # Special level for tracing behavior processing 
                 'sqlcmd' : 91} # Special level for producing sql commands used   
    # The value of DEBUG is 10. So keeping STATE at 15 makes sure that 
    # selecting debug also outputs  STATE messages into statelog  

    def __init__(self, name, levelname):
        self.name = name
        self.levelname = levelname
        logging.addLevelName(self.LOGLEVELS.get('state'),
                              'STATE')

        # Pick out the corresponding level from the hash
        self.level = self.LOGLEVELS.get(self.levelname, logging.NOTSET)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level=self.level)

        # Create console handler 
        self.ch = logging.StreamHandler()
        self.ch.setLevel(self.level)

        # Create formatter and add it to logger object
        #self.formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        self.formatter = logging.Formatter("%(levelname)s - %(message)s")
        self.ch.setFormatter(self.formatter)
        self.logger.addHandler(self.ch)
        levels_to_filter = ['STATE', 'Level 90', 'Level 91']
        self.ch.addFilter(FilterLevels(levels_to_filter))

        # Log all state messages to a file
        self.rofile = logging.handlers.RotatingFileHandler(SLOGFILE, mode="w",
                                                    backupCount=10)
        self.rofile.setLevel(self.LOGLEVELS.get('state'))
        self.logger.addHandler(self.rofile)
        levels_to_filter = ['INFO', 'CRITICAL', 'DEBUG', 'WARNING', 'ERROR', 
                            'Level 90', 'Level 5', 
                            'Level 91']
        self.rofile.addFilter(FilterLevels(levels_to_filter))
        
        # Log the behavior processing to file

        self.bfile = logging.handlers.RotatingFileHandler(BLOGFILE, mode="w",
                                                    backupCount=10)
        self.bfile.setLevel(self.LOGLEVELS.get('behavior'))
        self.logger.addHandler(self.bfile)
        levels_to_filter = ['INFO', 'CRITICAL', 'DEBUG', 'WARNING', 'ERROR', 
                            'STATE', 'Level 5']
        self.bfile.addFilter(FilterLevels(levels_to_filter))


    def setlevel(self, levelname):
        self.level = self.LOGLEVELS.get(levelname, logging.NOTSET)
        self.logger.setLevel(level=self.level)

    def debug(self, log):
        if self.logger.isEnabledFor(logging.DEBUG):
            (filename, linenumber, function) = self.logger.findCaller()
            cstring = str(os.path.basename(filename)) + ":" + \
                      str(linenumber) + ":" + \
                      str(function) + " - "

            tolog = cstring + str(log)
            self.logger.debug(tolog)

    def fine(self, log):
        if self.logger.isEnabledFor(self.LOGLEVELS.get('fine')):
          (filename, linenumber, function) = self.logger.findCaller()
          cstring = str(os.path.basename(filename)) + ":" + \
                      str(linenumber) + ":" + \
                      str(function) + " - "
          tolog = cstring + str(log)
          self.logger.log(self.LOGLEVELS.get('fine'), tolog)

    def info(self, log):
        if self.logger.isEnabledFor(logging.INFO):
          (filename, linenumber, function) = self.logger.findCaller()
          cstring = str(os.path.basename(filename)) + ":" + \
                      str(linenumber) + ":" + \
                      str(function) + " - "
          tolog = cstring + str(log)
          self.logger.info(tolog)

    def critical(self, log):
       if self.logger.isEnabledFor(logging.CRITICAL):
            self.logger.critical(log)

    def error(self, log):
        if self.logger.isEnabledFor(logging.ERROR):
             self.logger.error(log)

    def warning(self, log):
        if self.logger.isEnabledFor(logging.WARNING):
             self.logger.warning(log)

    def state(self, log):
        if  self.logger.isEnabledFor(self.LOGLEVELS.get('state')):
             self.logger.log(self.LOGLEVELS.get('state'), log)
            
    def behavior(self, numtabs, log):
        if  self.logger.isEnabledFor(self.LOGLEVELS.get('behavior')):
            tabstop = "  "
            tolog = tabstop * numtabs +  str(log)
            self.logger.log(self.LOGLEVELS.get('behavior'), tolog)

    def sqlcmd(self, log):
        if  self.logger.isEnabledFor(self.LOGLEVELS.get('sqlcmd')):
            (filename, linenumber, function) = self.logger.findCaller()
            cstring = str(os.path.basename(filename)) + ":" + \
                      str(linenumber) + ":" + \
                      str(function) + " - "
            tolog = cstring + str(log)
            self.logger.log(self.LOGLEVELS.get('sqlcmd'), tolog)

    def close(self):
         self.logger.clear()

    def isEnabledFor(self, lvl):
        return  self.logger.isEnabledFor(lvl)

class FilterLevels(logging.Filter):

    def __init__(self, levels_to_filter):
        logging.Filter.__init__(self)
        self.levels_to_filter = levels_to_filter

    def filter(self, record):
        if (record.levelname in self.levels_to_filter):
            return 0
        return 1



