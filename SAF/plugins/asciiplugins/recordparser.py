# recordparser.py 
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

from simpleparse.parser import Parser
from simpleparse.dispatchprocessor import *
from commonterms import MonthInterpreter, TimeInterpreter 
from commonterms import TimestampInterpreter, DayInterpreter
from commonterms import MinInterpreter, HourInterpreter
from commonterms import YearInterpreter, SecInterpreter
from commonterms import TzoneInterpreter, EpochInterpreter, MicrosecInterpreter
import inspect

class DefaultRecordParser( DispatchProcessor ):

    timestamp =  TimestampInterpreter()
    day = DayInterpreter()
    month = MonthInterpreter()
    year = YearInterpreter()
    hour = HourInterpreter()
    min =  MinInterpreter()
    sec =  SecInterpreter()
    tzone =  TzoneInterpreter()
    epoch =  EpochInterpreter()
    microsec =  MicrosecInterpreter()
       
    def __init__(self, attributes):
        self.attributes = attributes
        self.timeobj    = attributes.get_timeobj()
        self.col_index  = 5

    def reset_col_index (self, resetval=None):
        self.col_index = resetval if(resetval) else 5    
    
    def set_record(self, at):
        self.attributes = at
        self.timeobj = at.get_timeobj()
    
    def _extract_time_elements(self,tlist):
        for t in tlist:
            if isinstance(t, tuple):
                (typ, val) = t
                self.timeobj[typ] = val
            elif(isinstance(t,list)):
                self._extract_time_elements(t)

    def record(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        retval = dispatchList(self, subtags, buffer)
        self._extract_time_elements(retval)                
        return retval
                 
    def message(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        #print "%s:%s" % (tag, buffer[start:stop])        
        return dispatchList(self, subtags, buffer)

    def hostname(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        #print "%s:%s" % (tag, buffer[start:stop])        
        retval = dispatchList(self, subtags, buffer)
        hostname = getString((tag, start+len(retval[0]), stop, subtags), buffer)
        self.attributes.set('hostname', hostname)
        self.attributes.set_origin(hostname)
        return hostname

    def daemon(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        #print "%s:%s" % (tag, buffer[start:stop])        
        retval = dispatchList(self, subtags, buffer)
        daemon = getString((tag, start+len(retval[0]), stop, subtags), buffer)
        self.attributes.set('daemon', daemon)
        return daemon

    def pid(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        retval = dispatchList(self, subtags, buffer)
        pid = getString((tag, start+len(retval[0]), stop, subtags), buffer)
        self.attributes.set('pid', pid)
        return pid

    def charstring(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        retval = dispatchList(self, subtags, buffer)
        cs = getString((tag, start+len(retval[0]), stop, subtags), buffer)
        self.attributes.set('charstring', cs)
        return cs
    
    def sipaddr(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        retval = dispatchList(self, subtags, buffer)
        sip = getString((tag, start, stop, subtags), buffer)
        if(self.attributes.has_attr('sipaddr')):
            self.attributes.set('sipaddr', sip)
        return sip

    def identd(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        retval = dispatchList(self, subtags, buffer)
        id = getString((tag, start, stop, subtags), buffer)
        self.attributes.set('identd', id)
        return id


    def remoteuser(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        retval = dispatchList(self, subtags, buffer)
        ru = getString((tag, start, stop, subtags), buffer)
        self.attributes.set('remoteuser', ru)
        return ru
    
    def httpreq(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        retval = dispatchList(self, subtags, buffer)
        ru = getString((tag, start, stop, subtags), buffer)
        self.attributes.set('httpreq', ru)
        return ru

    def httpstatus(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        retval = dispatchList(self, subtags, buffer)
        ru = getString((tag, start, stop, subtags), buffer)
        self.attributes.set('httpstatus', ru)
        return ru

    def contentlength(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        retval = dispatchList(self, subtags, buffer)
        clstr = getString((tag, start, stop, subtags), buffer)
        if(clstr == '-'):
            self.attributes.set('contentlength', None)
            ru = None
        else:
            try:
                ru = int(clstr)
                self.attributes.set('contentlength', ru)
            except:
                raise Exception("Invalid contentlength detected %s" %(clstr))
        return ru

    def referrer(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        retval = dispatchList(self, subtags, buffer)
        ru = getString((tag, start, stop, subtags), buffer)
        self.attributes.set('referrer', ru)
        return ru

    def useragent(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        retval = dispatchList(self, subtags, buffer)
        ru = getString((tag, start, stop, subtags), buffer)
        self.attributes.set('useragent', ru)
        return ru
    
    def loglevel(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        retval = dispatchList(self, subtags, buffer)
        ru = getString((tag, start, stop, subtags), buffer)
        self.attributes.set('loglevel', ru)
        return ru
    
    def misc(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        return dispatchList(self, subtags, buffer)

    def tstamp(self, (tag, start, stop, subtags), buffer):
        #print "%s:%s" % (tag, buffer[start:stop])        
        return dispatchList(self, subtags, buffer)

    def ts(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        return getString((tag, start, stop, subtags), buffer)
    
    def hexdigit(self, (tag, start, stop, subtags), buffer):
        ##print "%s:%s" % (tag, buffer[start:stop])        
        return getString((tag, start, stop, subtags), buffer)
    
    def funcname(self):
        return inspect.stack()[1][3]
    
