# behaviorinstance.py
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
from framework.common.sorted_collection import SortedCollection

class BehaviorInstance:
    """
        A behavior instance is defined as an event or a group of sorted 
        events matching a behavior (b). 
        
        In terms of implementation, a BehaviorInstance object could be either
        an Event or an EventGroup object. The BehaviorInstance class provides 
        a single abstraction for the algorithms to work with. 
        The Event and EventGroup classes, subclass BehaviorInstance to 
        implement the low-level semantics of a behavior instance.
        
        Each behavior instance object has:
        (a) starttime - Starttime of the first event in the instances
        (b) endtime   - Endtime of the last event in the instance
        (c) bcount    - count of the number of objects in the instance
        (d) contents  - a pointer to an instance object (either Event or EventGroup)                       
    """

    def __init__(self):
        # Starttime of the behavior instance represented as a Time() object
        self.starttime = None
        
        # Endtime of the behavior instance represented as a Time() object
        self.endtime   = None
        
        # Total number of contents in the instance
        self.bcount    = None
        
        # Contents of the instance (an event or group of events)
        self.contents   = None
        
        # A pointer to the behavior object for which this is an instance
        self.ptr_to_behavior = None
        
        # A special pointer for pointing to the dependee behavior instance
        # For ex: Instances matching dependent states will have this set
        # to their dependee instance objects
        self.ptr_to_dependee = None
        
        self.atleast_count = None

    def add(self, content):
        """
            Adds content to the instance. Exact semantics are defined by 
            the Event and EventGroup subclasses.  
        """
        pass

    def set_behavior(self, ptr_to_behavior):
        """
            Sets the pointer to the behavior object for which this object
            represents an instance
        """
        self.ptr_to_behavior = ptr_to_behavior

    def get_behavior(self):
        """
            Gets the pointer to the behavior object for which this object
            represents an instance
        """
        return self.ptr_to_behavior        
    
    def set_dependee(self, depbi):
        """
            Sets the pointer to the behavior object for which this object
            represents an instance
        """
        self.ptr_to_dependee = depbi

    def get_dependee(self):
        """
            Gets the pointer to the behavior object for which this object
            represents an instance
        """
        return self.ptr_to_dependee       
                    
    
    def get_starttime(self):
        """
            Returns the starttime of the instance as a Time() object
        """
        return self.starttime

    def set_starttime(self, st):
        """
            Sets the starttime to the provided Time() object.
        """
        assert(not isinstance(st, Time))
        self.starttime = st
       
    def get_endtime(self, index=None):
        """
           Returns the endtime as a Time() object
        """
        if(index):
            if(isinstance(self.contents, SortedCollection)):
                return self.contents[index].get_timestamp()
        return self.endtime

    def set_endtime(self, et):
        """
            Sets the endtime to the provided Time() object.
        """
        assert(not isinstance(et, Time))
        self.endtime = et
        
    def get_timestamp(self):
        """
            Returns the starttime as a Time() object. This function is a 
            convenience function for dealing with single events.
        """
        return self.starttime
    
    def get_contents(self):
        """
            Returns the contents of the instance.
        """
        return self.contents

    def get_bcount(self):
        """
            Returns the behavior count
        """
        return self.bcount

    def set_atleast_count(self, c):
        """
            Sets the atleast count to be used by comparisons
        """
        if(c > 0):
            self.atleast_count = c
        else:
            self.atleast_count = 0
    
    def get_atleast_count(self):
        """
            Gets the atleast count if valid or returns None
        """
        return self.atleast_count
    
    
    def get_bcount(self):
        """
            Returns the behavior count
        """
        return self.bcount


    def __len__(self):
        """
            Implements the __len__() method of python objects and returns the 
            total number of objects in a behavior instance.
        """
        return self.bcount

    def __eq__(self, other) : 
        """
            Implements the __eq__() method of python objects.
            Tests the provided behavior instance object for equality with 
            self and returns true iff the contents of both objects are exactly
            the same.
        """
        return self.__dict__ == other.__dict__
        
    def __ne__(self, tocompare):
        """
            Implements the __neq__() method of python objects. 
            Tests the provided behavior instance object for inequality with 
            self. 
        """
        return not self.__eq__(tocompare)
    
    def __repr__(self):
        printstr = []
        printstr.append("%s ( " %(self.__class__.__name__))
        if self.ptr_to_behavior:
            b = self.ptr_to_behavior.get_rootbehavior().get_qualifiedname()
            printstr.append("Behavior = %s" %(b))
        if self.ptr_to_dependee:
            b = self.ptr_to_dependee
            printstr.append("Dependee = \n\t%s" %(b))
        printstr.append("starttime = %s"% (self.starttime))
        printstr.append("endtime = %s" % (self.endtime))
        printstr.append("bcount = %s" % (self.bcount))
        printstr.append("\n\tcontents = [ %s ] )" % (self.get_uniqueid_str()))
        return printstr[0]+", ".join(printstr[1:])