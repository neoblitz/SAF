# plugin_mysql.py - Plugin for MySql logs
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
from plugin_base import BasicPlugin
from attributes import Attributes
import commonterms

class MySqlPlugin(BasicPlugin):

    PLUGIN_ATTRIBUTES = [ ('loglevel', 'text'),
                          ('charstring', 'text')] 
          
    def get_eventtype(self, record=None, plugin_record=None):
        return "MYSQL"
    
    def get_production(self):
        return "mysqlrec"
  
    def get_ebnf(self):
        return self.ebnf

    ebnf = r'''#Comment
mysqlrec := record
record    := tstamp, (':'/','), [0-9]+,  ts, '[',loglevel, ']', ts, charstring
tstamp    := day, '/', month, '/', year, ':',hour, ':', min, ':', sec, (ts, tzone)?  
loglevel := [A-Za-z]+
charstring := ts, -"\n"*
'''       
    
    def plugin_usage(self):
        usagestr = """
+===============+
| mysql plugin  |
+===============+
    Input file: 
        Generic plugin for mysql server logs.
        
    Output event:
        eventno 
        eventtype = 'MYSQL'
        origin 
        timestamp
        timestampusec
        loglevel
        charstring

    Record format expected (default): 
        timestamp, ts, loglevel, ts, charstring 
            
        'timestamp' is expected to be in the following format (its easy to extend this):
            day, '/', month, '/', year, ':', hour, ':', min, ':', sec
                   
        'ts' stands for whitespace (space and tab).
    
    Example input record (single line):
        11/Sep/2010:20:35:05:138 [CRITICAL] ./mysqld: Shutdown complete

    Command line usage(s):
        To parse standard syslog
            ./normalizer.py -i <mysql file> -o sql.sqlite -p mysql
            
"""
        return usagestr