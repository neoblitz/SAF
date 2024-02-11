# event.py 
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
from timeobject import Time
from behaviorinstance import BehaviorInstance

class Event(BehaviorInstance):
    """
        Represents an event in memory.
    """

    def __init__(self, eventno, attrlist=None, valuelist=None, avhash=None):
        self.eventno = eventno
        self.ahash = {}
       
        if avhash:
            self.ahash = avhash.copy()
        else:
            index = 0
            for a in attrlist:
                v = valuelist[index]
                self.ahash[a] = v
                index += 1  
        self._initialize_fields()
       
    def _initialize_fields(self):
        self.eventno = self.ahash['eventno']        
        self.timestamp_sec = self.ahash['timestamp']
        self.timestamp_usec = self.ahash['timestampusec']
        self.timestamp = Time(self.timestamp_sec, self.timestamp_usec)
        self.eventtype = self.ahash['eventtype']
        
        # Set the variables required by BehaviorInstance
        self.starttime = self.timestamp
        self.endtime   = self.timestamp
        self.bcount    = 1
        self.contents  = self.ahash
        self.ptr_to_behavior = None
        self.ptr_to_dependee = None
        self.atleast_count = None

    def get_avhash(self):
        return self.ahash


    def get_timestamp(self):        
        return self.timestamp    
  
    def get_uniqueid_str(self):
        return str(self.eventno) + "-" + self.eventtype
    
    def get_id(self):
        return self.eventno

    def get_first_id(self):
        return self.eventno

    def get_ids(self):
        return [self.eventno]
    
    def get_type(self):
        return self.eventtype

    def get_timerange(self):
        return (self.starttime, self.endtime, self.get_id())
    
    def set_behavior(self, ptr_to_behavior):
        """
            Sets the pointer to the behavior object for which this object
            represents an instance
        """
        self.ptr_to_behavior = ptr_to_behavior

    
    def add(self, ev):
        """
            Replaces the existing event fields with fields from the 
            new event.
        """
        self.ahash = ev.get_avhash()
        self._initialize_fields()

    def __repr__(self):
        printstr = [] 
        bname = None
        if(self.ptr_to_behavior):
            rptr = self.ptr_to_behavior.get_rootbehavior()
            if (rptr):
                bname =  rptr.get_qualifiedname()
        printstr.append("%s-%s (%s)" % (self.eventno,
                                        self.eventtype,
                                        bname))
        return ','.join(printstr)
    
    def __ne__(self, tocompare):
        """
            Implements the __neq__() method of python objects. 
            Tests the provided behavior instance object for inequality with 
            self. 
        """
        return not self.__eq__(tocompare)
    
    def __eq__(self, other) : 
        """
            Implements the __eq__() method of python objects.
            Tests the provided behavior instance object for equality with 
            self and returns true iff the contents of both objects are exactly
            the same.
        """
        if(isinstance(other, Event)):
            return self.ahash == other.ahash
        else:
            return False
        
