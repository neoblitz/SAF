# plugin_bindquery.py - Plugin for parsing bind queries from syslog
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
from plugin_base import BasicParser
from attributes import Attributes
from recordparser import DefaultRecordParser
from simpleparse.dispatchprocessor import *
import commonterms
import socket

class BindQueryPlugin(BasicPlugin):

    PLUGIN_ATTRIBUTES = [ ('hostname', 'text'), 
                          ('daemon', 'text'), 
                          ('pid', 'text'), 
                          ('clientip', 'text'), 
                          ('clientport', 'text'), 
                          ('query', 'text'),  
                          ('rrname', 'text'), 
                          ('rrtype', 'text'),
                          ('options', 'text'),
                          ('nsname', 'text')] 

    def get_eventtype(self, record=None, parsed_record=None):
        return "BINDDNSQUERY"
    
    def get_production(self):
        return "syslogrec"
  
    def get_ebnf(self):
        return self.syslogbnf
    
    def get_processor(self):
        return BindProcessor(self.attrs)

#Jun 10 09:57:50 n30-hp named[2513]: client 192.168.2.51#40899: query: api.twitter.com IN AAAA + (192.168.2.54)
#
    syslogbnf = r'''#Comment
syslogrec := record
record    := timestamp, ts, message
message   := hostname, daemon, ('[', pid ,']')?, ':', ts, 'client', ts, clientip, '#', clientport, ':', ts, 'query', ':', ts, query, ts, rrname, ts, rrtype, ts, options, ts, '(', nsname, ')' 
daemon    := ts, [a-zA-Z0-9_.-]+
pid       := ts, [0-9]+
hostname  := ts, [a-zA-Z0-9\\(_.-]+
rrname    := [a-zA-Z]+
rrtype    := [a-zA-Z]+    
clientip  := sipaddr
clientport:= [0-9]+
sipaddr   := [0-9],[0-9]?,[0-9]?,'.',[0-9],[0-9]?,[0-9]?,'.',[0-9],[0-9]?,[0-9]?,'.',[0-9],[0-9]?,[0-9]?
query     := [a-zA-Z0-9\\(_.-]+
options   := '+', ([a-zA-Z]+)? 
nsname    := sipaddr
'''       

    def plugin_usage(self):
        usagestr = """
+===============+
| bind plugin   |
+===============+
    Input file: 
        Plugin for bind queries logged (by the bind9 daemon) to syslog files.
        Such logging is easily enabled for bind using the following command:
            $ rndc querylog
        
    Output event:
        eventno 
        eventtype = 'BINDQUERY'
        origin 
        timestamp
        timestampusec
        hostname
        daemon
        pid
        clientip 
        clientport 
        query
        rrname 
        rrtype
        options
        nsname

    Record format expected (default): 
        <syslog format> where the 'charstring' is now 
            'client', ts, clientip, '#', clientport, ':', ts, 'query', ':', ts, query, ts, rrname, ts, rrtype, ts, options, ts, '(', nsname, ')'             
        
        'ts' stands for whitespace (space and tab).
    
    Example input record (single line):
        Jun 1 07:47:16 myhost named[2513]: client 192.168.2.51#51150: query: www.google.com IN A + (192.168.2.54)

    Command line usage(s):
        To parse standard syslog
            ./normalizer.py -i <syslog file> -o bind.sqlite -p bind
            
    
    Notes:
        It is possible that plugin may not be able to parse some records. 
        Please raise a bug on the wiki at http://thirdeye.isi.deterlab.net.
"""
        return usagestr
    
class BindProcessor(BasicParser):
    
    def clientip(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        #print "%s:%s" % (tag, buffer[start:stop])        
        self.attributes.set('clientip', buffer[start:stop])
	    #clienthostname = socket.gethostbyaddr(buffer[start:stop])
        #self.attributes.set('clienthostname', clienthostname[0])
        return buffer[start:stop]
    
    def clientport(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        #print "%s:%s" % (tag, buffer[start:stop])        
        self.attributes.set('clientport', buffer[start:stop])
        return buffer[start:stop]

    def query(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        #print "%s:%s" % (tag, buffer[start:stop])       
        retval = dispatchList(self, subtags, buffer)
        self.attributes.set('query', buffer[start:stop])
        return buffer[start:stop]
        
    def rrname(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        #print "%s:%s" % (tag, buffer[start:stop])        
        retval = dispatchList(self, subtags, buffer)
        self.attributes.set('rrname', buffer[start:stop])
        return buffer[start:stop]
    
    def rrtype(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        #print "%s:%s" % (tag, buffer[start:stop])        
        retval = dispatchList(self, subtags, buffer)
        self.attributes.set('rrtype', buffer[start:stop])
        return buffer[start:stop]
    
    def options(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        #print "%s:%s" % (tag, buffer[start:stop])        
        retval = dispatchList(self, subtags, buffer)
        self.attributes.set('options', buffer[start:stop])
        return buffer[start:stop]
        
    def nsname(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        #print "%s:%s" % (tag, buffer[start:stop])        
        retval = dispatchList(self, subtags, buffer)
        self.attributes.set('nsname', buffer[start:stop])
        return buffer[start:stop]
