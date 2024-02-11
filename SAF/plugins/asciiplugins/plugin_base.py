# plugin_base.py 
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

import linecache
import time
import sys
from datetime import datetime
from datetime import tzinfo, timedelta, datetime
from simpleparse.parser import Parser
from copy import deepcopy

from attributes import Attributes
from normalizerclass import Normalizer
from recordparser import DefaultRecordParser
from simpleparse.parser import Parser
from simpleparse.dispatchprocessor import *

class BasicPlugin():
    """
        Basic plugin class provides a default plugin implementation. 
        The basic plugin treats records consisting of fields separated by 
        either a tab or whitespace.  The fieldnames are expected to be specified
        at the command line with the -a option.
    """
    
    PLUGIN_ATTRIBUTES = {}
    
    def __init__(self, cmdlineattrs=None):
        self.bnf = None
        self.production = None
        self.cmdlineattrs = False
        if cmdlineattrs:
            self.cmdlineattrs = True
        ebnf = self.get_ebnf() 
        if(ebnf != self.basicebnf):
            ebnf += '\n'+ self.basicebnf
        self.parser = Parser(ebnf, self.get_production())
        self.rec_number = 1 

    def get_num_rawrecords(self):
        return (self.rec_number-1)

    def open(self, filename):
        self.logfile = filename
        handle = None
        return handle
    
    def init_plugin_attrs(self, cmdlineattrs=None, setval=None, addtodefault=None):
        self.attrs = Attributes()
        self.num_default_plugin_attrs = len(self.attrs)
        if(cmdlineattrs):
            self.attrs = self.parse_input_attrs(cmdlineattrs)
            self.cmdlineattrs = True
        else:
            for at,t in self.PLUGIN_ATTRIBUTES:
                self.attrs.add(at, t)
            self.num_default_plugin_attrs += len(self.PLUGIN_ATTRIBUTES)
            if (addtodefault):
                attrs = self.parse_input_attrs(addtodefault)
                for a,v,t in attrs:
                    if not self.attrs.has_attr(a):
                        self.attrs.add(a,t)
            self.cmdlineattrs = False
                
        if(setval):
            for av in setval.split("|"):
                av = av.strip()
                try:
                    (a, v) = av.split("=")
                except ValueError:
                    raise Exception("No '=' for attribute %s in option -s" %(av))
                self.attrs.set(a, v)
        return self.attrs
        
    def get_next_record(self, handle):
       line = linecache.getline(self.logfile, self.rec_number)
       if line:           
           line = line.strip('\n')
           line = line.strip(' ')
           if line:
               self.rec_number += 1
       return line
                    
    def parse(self, record, processor=None):
        parsed_record = self.get_record_attrs(record)
        if not processor:
            processor = BasicParser(parsed_record)
        else:
            processor.set_record(parsed_record)
            
        processor.reset_col_index(self.num_default_plugin_attrs)
        success, children, nextcharacter = self.parser.parse(record, 
                                                    processor=processor)
        if(not success):
            print "Unable to parse %s (%s chars parsed of %s),returned value was %s"%\
            ( repr(record), nextcharacter, len(record), 
              (success, children, nextcharacter))
            return None           
       
        parsed_record.set_eventno(self.get_eventno(record, parsed_record))
        parsed_record.set_origin(self.get_origin(record, parsed_record))
        parsed_record.set_eventtype(self.get_eventtype(record, parsed_record))
        parsed_record.set_timestamp(self.get_timestamp(record, parsed_record))
        return parsed_record
    
    def get_processor(self):
        return BasicParser(self.attrs) 

    def get_ebnf(self):
        return self.basicebnf

    def get_record_attrs(self, record):
        return deepcopy(self.attrs)
    
    def get_eventno(self, record, parsed_record):
        return parsed_record.get('eventno')

    def get_eventtype(self, record=None, parsed_record=None):
        if(parsed_record):
            return parsed_record.get('eventtype')
        else:
            return None

    def get_origin(self, record, parsed_record):
        return parsed_record.get('origin')

    def get_production(self):
        return "basicrec"

    def get_timestamp(self, record, parsed_record):
        return self._datetime_to_epoch(parsed_record.get_timeobj())

    def parse_input_attrs(self, attrs):
        out_attrs = Attributes() 
        for att in attrs.split("|"):
            att = att.strip()
            (at, t) = att.split(":")
            out_attrs.add(at, t)
        return out_attrs

    def close(self):
        pass
    
    def _datetime_to_epoch(self, timeobj):
        d = datetime.now()
        year = d.year
        month = d.month
        day = d.day
        hour = 0
        minute = 0
        second = 0
        microsec = 0
        tzinfo = None
        epoch = None
        
        epoch = timeobj.get('epoch')  if ('epoch' in timeobj) else None
        microsec = timeobj.get('microsec')  if ('microsec' in timeobj) else 0
            
        # If time is already in unix epoch format return it
        if(epoch):
            return (epoch, microsec)          

        year = timeobj.get('year')  if ('year' in timeobj) else d.year
        month = timeobj.get('month')  if ('month' in timeobj) else d.month
        day = timeobj.get('day')  if ('day' in timeobj) else d.day
        
        hour = timeobj.get('hour')  if ('hour' in timeobj) else 0
        minute = timeobj.get('min')  if ('min' in timeobj) else 0
        second = timeobj.get('sec')  if ('sec' in timeobj) else 0
        tzinfo = timeobj.get('tzinfo') if ('tzinfo' in timeobj) else None
        
        try:
            d = datetime(year, month, day, hour, minute, second, microsec, tzinfo)
        except Exception as ex:
            print "ERROR: '%s' while processing %s" %(ex, timeobj)
            sys.exit(2)
        
        epoch = int(time.mktime(d.timetuple()))
        return (epoch, microsec)

    basicebnf = r'''#Comment
basicrec := brec
brec   := ts, timestamp, ts, col, (ts, col)*
col      := [a-zA-Z0-9\\(:;$#%!^*\\)@_<>.-]+
ts        := [ \t]*
'''
    
    
    def plugin_usage(self):
        usagestr = """
+==============+
| Basic plugin |
+==============+
    Input file: 
        Any ascii file containing records where each record can be separated into
        fields delimited by space or tab characters. 
        
        The first field of each record is assumed to be a timestamp and is used 
        to populate the event 'timsetamp' and 'timestampusec' attributes. The attribute 
        names for all remaining fields in the record are expected to be specified
        with the -a option on the command line
        
    Output event:
        eventno 
        eventtype = None or the value specified in command line with -s
        origin    = None or the value specified in command line with -s
        timestamp
        timestampusec
        <any attributes specified on the command line>


    Record format expected (default): 
        timestamp, ts, field, (ts, field)*
        
        For now, timestamp is assumed to be unix epoch format but many other 
        formats will be supported. For Ex:  1238567803.632043  
                           
        'field' is a generic character string. Attributes specified on the 
        command line with -a are associated with each successive field in specified order.
        
        'ts' stands for whitespace (space and tab).
    
    Example input record (single line):
        1238567803.632043  0.000000      192.168.1.101    239.255.255.250
    
    Command line usage(s):
        To parse logs containing records as in the above example  
            ./normalizer.py -i <asciilog> -o basic.sqlite -p basic -a 'duration:real|sipaddr:text|dipaddr:text'
            
        Note that there are four fields in the record but we specify only three fields with -a. 
        This is due to the fact that the first field is assumed to be timestamp by default.      
            
"""
        return usagestr


class BasicParser(DefaultRecordParser): 
    
    def col(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" %(tag,buffer[start:stop]) 
        try:
            a = self.attributes.getbyindex(self.col_index)
        except:
            raise Exception("ERROR: Data contains less columns than expected! Check your command-line or data!")
        self.attributes.set(a, buffer[start:stop])
        self.col_index += 1
        return buffer[start:stop]
    
    def brec(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        #print "%s:%s" % (tag, buffer[start:stop])        
        retval = dispatchList(self, subtags, buffer)
        self._extract_time_elements(retval)                  
        return retval