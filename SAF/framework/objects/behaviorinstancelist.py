# behaviorinstancelist.py
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

from operator import itemgetter

# Local Imports
from framework.common.sorted_collection import SortedCollection

class BehaviorInstanceList(SortedCollection):
    """
        BehaviorInstanceList is a sorted list of BehaviorInstance objects
        sorted in ascending order first by startime and then by endtime.
    """
    
    def __init__(self, iterable=(), bobject=None, special=False):
        super(BehaviorInstanceList,self).__init__(iterable, 
                                                  key=self._get_timestamp)
        self.icount = self.__len__()
        # A pointer to the behavior of which the list objects are instances 
        self.ptr_to_behavior = bobject
        
        # Setting special to True means that this list
        # just acts as a signal that some condition has been met.
        # Special list wont have any contents. Its a NULL list with 
        # the special flag set. This is primarily used for indicating the 
        # success of the 'negation' logical operation
        self.special = special 
    
    def set_behavior(self,ptr_to_behavior):
        self.ptr_to_behavior = ptr_to_behavior
    
    def get_behavior(self):
        return self.ptr_to_behavior
    
    def get_icount(self):        
        return self.__len__()
    
    def copy(self):
        return self.__class__(self)
    
    def get_ids(self):
        idlist = []
        for binst in self._items:
            idlist.extend(binst.get_ids())
        return idlist

    def _get_timestamp(self,inst):
        return (inst.get_starttime(), inst.get_endtime(), inst.get_id())
    
    def __repr__(self):
        return self.__class__.__name__+"{ icount = "+str(self.get_icount())+ ",behavior = " + str(self.get_behavior()) + ",contents = ("+ str(self._items)+")}"
    
