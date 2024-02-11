# plugin_bindquery.py - Plugin for parsing argus flow data generated using the 
#                       the ra tool
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


from plugin_base import BasicPlugin, BasicParser
from attributes import Attributes
from recordparser import DefaultRecordParser
from simpleparse.dispatchprocessor import *
import commonterms
import socket

class ArgusPlugin(BasicPlugin):

    PLUGIN_ATTRIBUTES = [ ('protoflags', 'text'), 
                          ('protocol', 'text'), 
                          ('sipaddr', 'text'), 
                          ('sport', 'integer'), 
                          ('dir', 'text'),  
                          ('dipaddr', 'text'), 
                          ('dport', 'integer'), 
                          ('totalpkts', 'integer'),
                          ('totalbytes', 'integer'), 
                          ('state', 'text')] 


    FLOW_ETYPE_MAP = {'udp': 'UDP_FLOW',
                      'tcp': 'TCP_FLOW',
                      'arp': 'ARP_FLOW',
                      'igmp': 'IGMP_FLOW',
                      'icmp': 'ICMP_FLOW',
                      'ip' : 'IP_FLOW'}
        
    def get_eventtype(self, record=None, parsed_record=None):
        if parsed_record:
            if parsed_record.has_attr('protocol'):
                p = parsed_record.get('protocol')
            elif parsed_record.has_attr('proto'):
                p = parsed_record.get('proto')
            else:
                p = None
            return self.FLOW_ETYPE_MAP.get(p,'ARGUS_FLOW')
        return 'ARGUS_FLOW'
    
    def get_production(self):
        if(self.cmdlineattrs):
            return "basicrec"
        else:
            return "argusrec"
  
    def get_ebnf(self):
        return self.ebnf
    
    def get_processor(self):
        return ArgusProcessor(self.attrs)

#Default record output from ra without any options
#============================================================
# Refer the Ra (Version 3.0.4.1) manpage for details
#
# time proto  srchost  dir  dsthost  [count] status
#------------------------------------------------------------
    ebnf = r'''#Comment
argusrec := record
record    := timestamp, ts, protoflags?, ts, protocol, ts,  sipaddr, ('.', sport)?, ts, dir, ts,  dipaddr, ('.', dport)?, ts, (totalpkts)?, ts,(totalbytes)?, ts, state, ((ts, col)?)*
protoflags:= [0-9A-Za-z*],[0-9A-Za-z* ],[0-9A-Za-z* ],[0-9A-Za-z* ],[0-9A-Za-z* ],[0-9A-Za-z* ],[0-9A-Za-z* ],[0-9A-Za-z* ]
protocol  := [a-z],[a-z],[a-z]?,[a-z]?
sipaddr   := (macaddr/ipaddr/hostname)
dipaddr   := (macaddr/ipaddr/hostname)
ipaddr    := [0-9],[0-9]?,[0-9]?,'.',[0-9],[0-9]?,[0-9]?,'.',[0-9],[0-9]?,[0-9]?,'.',[0-9],[0-9]?,[0-9]?  
macaddr   := hexdigit,hexdigit?,':', hexdigit,hexdigit?,':', hexdigit,hexdigit?,':', hexdigit,hexdigit?,':', hexdigit,hexdigit?,':', hexdigit,hexdigit?
sport     := [0-9]+/[a-z]+
dport     := [0-9]+/[a-z]+
dir       := [<>?a-zA-Z-]+
hostname  := [a-zA-Z0-9\\(_.-]+
totalpkts   := [0-9]+
totalbytes  := [0-9]+
state   := [A-Z]+
hexdigit := [0-9a-fA-F]
'''       

    def plugin_usage(self):
        usagestr = """
+===============+
| argus plugin  |
+===============+

    Input file: 
    ===========
        Argus flow records generated using the 'ra' tool. 
        
        'ra' is a very sophisticated tool and can generate its output in many different
        ways. The argus plugin provides an ability to parse argus output produced in 
        three different ways. The only binding requirement for all cases is the 
        use of the -u option to the ra tool instructing it to output time in 
        unix epoch format.
        
        Note: 'ra' version 3.0.4.1 was used for the following examples. Older versions
        of ra may produce different default outputs in which case the default usage 
        of the plugin may fail.
        
        1. Default output produced by the following command
           ra -r <in.argus> -u
           
           Example output 
               1238567803.632043  e         udp      192.168.1.101.1031      ->    239.255.255.250.1900          1        143   INT
               1238567805.601316  e         udp      192.168.1.102.64040     ->      192.168.1.101.1031          1        272   INT
            
        2. Output produced by specifying the columns to print using -s option
            ra -r <in.argus>  -s  stime dur sipaddr dipaddr -u
            
            Example output:
                1238567803.632043   0.000000      192.168.1.101    239.255.255.250
                1238567805.601316   0.000000      192.168.1.102      192.168.1.101
        
        3. Output produced by appending columns to the default output
            ra -r <in.argus> +dur +tcprtt
            
            Example output:
             1238567803.632043  e         udp      192.168.1.101.1031      ->    239.255.255.250.1900          1        143   INT   0.000000 0.000000
             1238567805.601316  e         udp      192.168.1.102.64040     ->      192.168.1.101.1031          1        272   INT   0.000000 0.000000
        
    Output event:
    ============
    
        For case 1 above
            eventno 
            eventtype = 'ARGUS_FLOW'/'UDP_FLOW'/'TCP_FLOW'/'IP_FLOW'/'ARP_FLOW'/'IGMP_FLOW'/'ICMP_FLOW'
            origin 
            timestamp
            timestampusec
            protoflags 
            protocol 
            srcaddr 
            sport 
            dir  
            dstaddr 
            dport 
            totalpkts
            totalbytes 
            state
    
        For case 2 above
            eventno 
            eventtype = 'ARGUS_FLOW'/'UDP_FLOW'/'TCP_FLOW'/'IP_FLOW'/'ARP_FLOW'/'IGMP_FLOW'/'ICMP_FLOW'
            origin 
            timestamp
            timestampusec
            <attributes specified with -a>

        For case 3 above
            eventno 
            eventtype = 'ARGUS_FLOW'/'UDP_FLOW'/'TCP_FLOW'/'IP_FLOW'/'ARP_FLOW'/'IGMP_FLOW'/'ICMP_FLOW'
            origin 
            timestamp
            timestampusec
            protoflags 
            protocol 
            srcaddr 
            sport 
            dir  
            dstaddr 
            dport 
            totalpkts
            totalbytes 
            state
            <attributes specified with -x>

    Record format expected (default): 
    ================================
        timestamp, ts, protoflags, ts, protocol, ts,  srcaddr, ('.', sport)?, ts, dir, ts,  dstaddr, ('.', dport)?, ts, (totalpkts)?, ts,(totalbytes)?, ts, state
            
        'timestamp' is expected to be in the following format:
            unix_epoch, '.', microsec
                   
        'ts' stands for whitespace (space and tab).
    
    Example input records:
    =====================
        Shown above for cases 1, 2 and 3.

    Command line usage(s):
    =====================
       When input is in the default format (case 1 above)
        ./normalizer.py -i <logfile> -o argus.sqlite -p argus
        
       When input is produced by specifying columns (case 2 above)
        ./normalizer.py -i <logfile> -o argus.sqlite -p argus -a 'stime:real|duration:real|sipaddr:t|dipaddr:t' 
        
       When input is produced by appending columns to the default output (case 3 above)
         ./normalizer.py -i <logfile> -o argus.sqlite -p argus -x 'duration:real|tcprtt:real' 
    
"""
        return usagestr

class ArgusProcessor(BasicParser):    
   
    def protoflags(self, (tag, start, stop, subtags), buffer):
        ##print "%s:%s" % (tag, buffer[start:stop])        
        self.attributes.set(self.funcname(), buffer[start:stop])
        return buffer[start:stop]
        
    def protocol(self, (tag, start, stop, subtags), buffer):
        ##print "%s:%s" % (tag, buffer[start:stop])        
        self.attributes.set(self.funcname(), buffer[start:stop])
        return buffer[start:stop]

    def sipaddr(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        self.attributes.set(self.funcname(), buffer[start:stop])
        return buffer[start:stop]

    def dipaddr(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        self.attributes.set(self.funcname(), buffer[start:stop])
        return buffer[start:stop]

    def sport(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        self.attributes.set(self.funcname(), buffer[start:stop])
        return buffer[start:stop]

    def dport(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        self.attributes.set(self.funcname(), buffer[start:stop])
        return buffer[start:stop]

    def dir(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])       
        self.attributes.set(self.funcname(), buffer[start:stop])
        return buffer[start:stop]

    def totalpkts(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        self.attributes.set(self.funcname(), buffer[start:stop])
        return buffer[start:stop]
    
    def totalbytes(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        self.attributes.set(self.funcname(), buffer[start:stop])
        return buffer[start:stop]
    
    def state(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        self.attributes.set(self.funcname(), buffer[start:stop])
        return buffer[start:stop]