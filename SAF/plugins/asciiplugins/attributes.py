# attributes.py 
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
from datetime import datetime
from datetime import tzinfo, timedelta, datetime

class Attributes:


    default_attrs = [('eventno', 'integer'), 
                     ('eventtype','text'), 
                     ('origin','text'),
                     ('timestamp','integer'),
                     ('timestampusec','integer')]    

    valid_attr_types = [('text', 't'), 
                        ('integer', 'int', 'i'),
                        ('real', 'r') ] 
    
        
    def __init__(self):
        self.attrlist = []
        self.attrvaluehash = {}
        self.attrtypehash = {}
        for a, t in self.default_attrs:               
            self.add(a, t)
        self.timeobj = {}

        
    def add(self, attr, attrtype):
        if(attr not in self.attrlist):
            self.attrlist.append(attr)
            if self._is_valid_attrtype(attrtype):
                self.attrtypehash[attr] = attrtype
                self.attrvaluehash[attr] = None
            else:
                raise Exception("Invalid attribute type '%s' specified"%\
                                (attrtype))
   
    def has_attr(self, at):
        if(at in self.attrlist):
            return True
        return False
   
    def set(self, attr, value):
        if(attr in self.attrvaluehash):
            if(self.attrvaluehash.get(attr) is None):
                self.attrvaluehash[attr] = value
        else:
            raise Exception("Invalid attribute '%s' specified" %(attr))
 
    def set_eventno(self, value):
        if(value):
            self.set('eventno', value)
    
    def set_eventtype(self, value):
         self.set('eventtype', value)

    def set_origin(self, value):
         self.set('origin', value)

    def set_timestamp(self, (ts,tsusec)):
         self.set('timestamp', ts)
         self.set('timestampusec', tsusec)
         
    def get(self, attr):
        if(attr not in self.attrlist):
            raise Exception("Invalid attribute '%s' specified"%(attr))
        else:
            return self.attrvaluehash.get(attr, None)

    def getbyindex(self, index):
        try:
            return self.attrlist[index]
        except:
            raise Exception("Invalid attribute index '%s' specified" %(index))

    def get_all_attrs(self):
        return self.attrlist

    def get_unique_attrs(self):
        return list(set(self.attrlist)-set(self.default_attrs))
    
    def get_attr_type_tuples(self):
        tuplist = []
        for a in self.attrlist:
            tup = (a, self.attrtypehash.get(a))
            tuplist.append(tup)
        return tuplist  
              
    def get_timeobj(self):
        return self.timeobj

    def _is_valid_attrtype(self, at):
        for tup in self.valid_attr_types:
            if at in tup:
                return True
        return False

    def __iter__(self):
        return iter([(a,self.attrvaluehash[a],self.attrtypehash[a])\
                      for a in self.attrlist])

    def __len__(self):
        return len(self.attrlist)

    def __repr__(self):
        pstrlist = []
        for a in self.attrlist:
            pstrlist.append('%s = %s'%(a, self.attrvaluehash.get(a)))
        return "|".join(pstrlist)