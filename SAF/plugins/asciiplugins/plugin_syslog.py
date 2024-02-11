# plugin_syslog.py - Plugin for syslog files
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

class SyslogPlugin(BasicPlugin):

    PLUGIN_ATTRIBUTES = [ ('hostname', 'text'), 
                          ('daemon', 'text'), 
                          ('pid', 'text'), 
                          ('charstring', 'text')] 
     
    def get_eventtype(self, record=None, parsed_record=None):
        return "SYSLOG"
    
    def get_production(self):
        return "syslogrec"
  
    def get_ebnf(self):
        return self.syslogbnf

    syslogbnf = r'''#Comment
syslogrec := record
record    := timestamp, ts, message
message   := hostname, daemon, ('[', pid ,']')?, ':', charstring
hostname  := ts, [a-zA-Z0-9_.-]+
daemon    := ts, [a-zA-Z0-9_.-]+
pid       := ts, [0-9]+
charstring:= ts, -"\n"*
'''       
    
    
    def plugin_usage(self):
        usagestr = """
+===============+
| syslog plugin |
+===============+
    Input file: 
        Generic plugin for syslog files.
        
    Output event:
        eventno 
        eventtype = 'SYSLOG'
        origin 
        timestamp
        timestampusec
        hostname
        daemon
        pid
        charstring

    Record format expected (default): 
        timestamp, ts, hostname, ts, daemon, ts, ('[', pid ,']')?, ':', charstring 
            
        'timestamp' is expected to be in the following format (its easy to extend this):
            month, ts, day, ts, hour, ':', min, ':', sec
                   
        'ts' stands for whitespace (space and tab).
    
    Example input record (single line):
        Jun 1 11:40:26 n30 dhclient: bound to 192.168.2.56 -- renewal in 2901 seconds.

    Command line usage(s):
        To parse standard syslog
            ./normalizer.py -i <syslog file> -o syslog.sqlite -p syslog
            
    Note that it is extremely easy to adapt this basic syslog parser to parse
    the 'charstring' further. See the 'bind' plugin of how this is done.
"""
        return usagestr
