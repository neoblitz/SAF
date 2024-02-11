# eventlist.py
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

# Local Imports
from behaviorinstance import BehaviorInstance
from framework.common.sorted_collection import SortedCollection


class EventGroup(BehaviorInstance):
    """
       An EventGroup object holds a group of events satisfying a behavior. 
    """

    def __init__(self, evlist = None, bobject=None):
        
        if(evlist):
           self.binstances = SortedCollection(evlist, key=self._get_timestamp)
           self.bcount    = len(self.binstances)
           self.starttime = self.binstances[0].get_starttime()
           self.endtime   = self.binstances[-1].get_endtime()
           self.contents  = self.binstances
        else:
           self.binstances = SortedCollection([], key=self._get_timestamp)
           self.contents  = self.binstances
           # These values are set later when events get added
           self.starttime = None
           self.endtime   = None
           self.bcount    = 0
        
        self.ptr_to_behavior = bobject
        self.ptr_to_dependee = None
        self.atleast_count = None

    def _get_timestamp(self,inst):
        return (inst.get_starttime(), inst.get_endtime(), inst.get_id())
        
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
            Adds a new event or another eventgroup to the group 
            maintaining the time sorted order 
        """
        self.binstances.insert(ev)
        self.starttime = self.binstances[0].get_starttime()
        self.endtime = self.binstances[-1].get_endtime()
        # Increment the count to avoid an unnecessary 
        # and potentially expensive call to the len() function
        self.bcount  = self.bcount + 1
   
    def get_uniqueid_str(self):
        unqstr = ['(']
        for e in self.contents:
            unqstr.append(e.get_uniqueid_str())
        unqstr.append(")")            
        return " ".join(unqstr)
    
    def get_id(self):
        """
            Returns the ID of the last event as ID of the group. Note that 
            an event group could contain event groups as its elements.
        """
        if len(self.binstances) > 0:
            return self.binstances[-1].get_id()
        else:
            return -1 
        
    def get_first_id(self):
        """
            Returns the ID of the last event as ID of the group. Note that 
            an event group could contain event groups as its elements.
        """
        if len(self.binstances) > 0:
            return self.binstances[0].get_id()

    def get_last_id(self):
        """
            Returns the ID of the last event as ID of the group. Note that 
            an event group could contain event groups as its elements.
        """
        if len(self.binstances) > 0:
            return self.binstances[-1].get_id()
        else:
            return -1 
    
    def get_type(self):
        """
            Returns the type of the last event as type of the group. Note that 
            an event group could contain event groups as its elements.
        """
        return self.binstances[-1].get_type()

    def get_last_type(self):
        """
            Returns the type of the last event as type of the group. Note that 
            an event group could contain event groups as its elements.
        """
        return self.binstances[-1].get_type()

    
    def get_first_timestamp(self):
        """
            Returns the starttime of the first instance in the group
        """
        return self.binstances[0].get_timestamp()
    
    def get_last_timestamp(self):
        """
            Returns the starttime of last instance in the group
        """
        return self.binstances[-1].get_timestamp()
    
    def get_event_byid(self, id):
        """
            Returns the event corresponding to the ID
        """
        return self.binstances[-1].get_timestamp()

    def get_ids(self):
        """
            Returns all ids
        """
        idlist = []
        for ev in self.binstances:
            idlist.extend(ev.get_ids())
        return idlist
    
    def __ne__(self, tocompare):
        """
            Implements the __ne__() method of python objects. 
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
        if(isinstance(other, EventGroup)):
            return self.__dict__ == other.__dict__
        else:
            return False

    
    
