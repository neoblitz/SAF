# plugin_apache.py - Plugin for apache combined access logs
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

class ApachePlugin(BasicPlugin):

    PLUGIN_ATTRIBUTES = [ ('sipaddr', 'text'), 
                          ('identd', 'text'), 
                          ('remoteuser', 'text'), 
                          ('httpreq', 'text'), 
                          ('httpstatus', 'integer'), 
                          ('contentlength', 'integer'),  
                          ('referrer', 'text'), 
                          ('useragent', 'text')] 

       
    def get_eventtype(self, record=None, parsed_record=None):
        return "APACHE_COMBINED"
    
    def get_production(self):
        return "apacherec"
  
    def get_ebnf(self):
        return self.apachebnf

#192.1.2.35 - - [10/Sep/2010:00:42:00] "POST /flower_store/order.do HTTP/1.1" 200 14392 
#"http://mystore.splunk.com/flower_store/enter_order_information.screen&JSESSIONID=SD7SL1FF9ADFF2" 
#"Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.10) Gecko/20070223 CentOS/1.5.0.10-0.1.el4.centos Firefox/1.5.0.10" 
#3697 4661 

    apachebnf = r'''#Comment
apacherec := record
record    := sipaddr, ts, identd, ts, remoteuser, ts, '[', tstamp, ']', ts, httpreq, ts, 
httpstatus, ts, contentlength, ts, referrer, ts, useragent, ts, misc
tstamp    := day, '/', month, '/', year, ':',hour, ':', min, ':', sec, (ts, tzone)?  
sipaddr   := [0-9],[0-9]?,[0-9]?,'.',[0-9],[0-9]?,[0-9]?,'.',[0-9],[0-9]?,[0-9]?,'.',[0-9],[0-9]?,[0-9]?
identd    := [a-zA-Z0-9_.-]+ 
remoteuser:= [a-zA-Z0-9_.-]+
httpreq   := '"', [A-Z]+, ts, [a-zA-Z0-9_.&?%=;:/\\()-]+, (ts, [HTTP0-9/.]+)? , '"'
httpstatus   := ('-'/[0-9]+)
contentlength   := ('-'/[0-9]+)
referrer   := '"', [a-zA-Z0-9_?%=;:/\\()&.-]+, '"'
useragent  := '"', [a-zA-Z0-9_?%=;:/\\()&. -]+,'"'
misc       := -"\n"*
'''       


    def plugin_usage(self):
        usagestr = """
+===============+
| apache plugin |
+===============+
    Input file: 
        Apache combined log
        
    Output event:
        eventno 
        eventtype = 'APACHE_COMBINED'
        origin 
        timestamp
        timestampusec
        sipaddr
        identd
        remoteuser
        httpreq
        httpstatus
        contentlength
        referrer
        useragent

    Record format expected (default): 
        sipaddr, ts, identd, ts, remoteuser, ts, '[', tstamp, ']', ts, httpreq, ts, 
        httpstatus, ts, contentlength, ts, referrer, ts, \useragent, ts, misc
        
        'tstamp' is expected to be in the following format (its easy to extend this):
           day, '/', month, '/', year, ':',hour, ':', min, ':', sec, (ts, tzone)?
                   
        'tstamp' is used to fillup the 'timestamp', 'timestampusec' fields.
        
        'ts' stands for whitespace (space and tab).
    
    Example input record (single line):
        192.1.2.35 - - [10/Sep/2010:00:42:00] "POST /flower_store/order.do HTTP/1.1" 200 14392 
        "http://mystore.splunk.com/flower_store/enter_order_information.screen&JSESSIONID=SD7SL1FF9ADFF2" 
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.10) Gecko/20070223 CentOS/1.5.0.10-0.1.el4.centos Firefox/1.5.0.10" 
        3697 4661 
    
    Command line usage(s):
        To parse standard combined apache logs
            ./normalizer.py -i <apache_combined_log> -o apache.sqlite -p apache
"""
        return usagestr