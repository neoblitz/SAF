# timeobject.py
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
from framework.common.utils import get_timediff

class Time:
    """ 
        Generic object to handle time 
    """
    
    def __init__(self, sec=0, usec=0):
        self.seconds = sec
        self.microseconds = usec
        self._compute_floatrepr()

    def _compute_floatrepr(self):
         self.floatrepr = \
               str(self.seconds) + "." + str(self.microseconds).zfill(6)       
    
    def get_time(self):
        return float(self.floatrepr)
    
    def get_time_tuple(self):
        return (self.seconds, self.microseconds)        

    def set_time_from_str(self, floatstr, qualifier):
        assert(isinstance(floatstr,str))
        
        q = qualifier.upper()
        if(q == 'S' or q  == 'SEC' or q == 'SECS'):
            fracpart = "0.0"
            fields = floatstr.split(".")
            if len(fields) == 2:
                intpart = fields[0]
                fracpart = "0."+fields[1]
            elif len(fields) == 1:
                intpart = fields[0]
            else:
                raise Exception("Invalid number %s!" %(floatstr))
            self.seconds = int(intpart)
            self.microseconds = int(float(str(fracpart).zfill(6)) * 1000000.0)
        elif(q == 'MS' or q  == 'MSEC' or q == 'MSECS'):
            self.seconds = int(float(floatstr)/ 1000.0)
            self.microseconds = int(float(floatstr) * 1000.0)
        else:
            raise Exception("Invalid time qualifier (%s) found !" %(q))
        self._compute_floatrepr()
        
    def __eq__(self, tocompare):
        return ((self.seconds == tocompare.seconds) and
                (self.microseconds == tocompare.microseconds))
        
    def __ne__(self, tocompare):
        return not self.__eq__(tocompare)
    
    def __gt__(self,tocompare):
        if(self.seconds == tocompare.seconds):
            if(self.microseconds > tocompare.microseconds):
                return True
            else:
                return False
        elif(self.seconds > tocompare.seconds):
            return True
        else:
            return False
            
    def __ge__(self,tocompare):
        if(self.seconds == tocompare.seconds):
            if(self.microseconds >= tocompare.microseconds):
                return True
            else:
                return False
        elif(self.seconds >= tocompare.seconds):
            return True
        else:
            return False

    def __lt__(self,tocompare):
        if(self.seconds == tocompare.seconds):
            if(self.microseconds < tocompare.microseconds):
                return True
            else:
                return False
        elif(self.seconds < tocompare.seconds):
            return True
        else:
            return False


    def __add__(self, toadd):
        (s1, ms1) = self.get_time_tuple()
        (s2, ms2) = toadd.get_time_tuple()
        
        # Add corresponding parts from both timeobjects
        # FIXME: Not handling overflow of seconds addition
        sum_s = s1 + s2
        sum_ms = ms1 + ms2
        
        # Overflow case for milliseconds
        if(sum_ms >= 1000000):
            # Increment the seconds
            sum_s += 1
            # Put the remainder if any in milliseconds
            sum_ms = (sum_ms - 1000000)
            
        return Time(sum_s, sum_ms)

    def __sub__(self, tosub):
        t2 = self.get_time_tuple()
        t1 = tosub.get_time_tuple()
        t = get_timediff(t1, t2)
        return Time(t.seconds, t.microseconds)


    def __le__(self,tocompare):
        if(self.seconds == tocompare.seconds):
            if(self.microseconds <= tocompare.microseconds):
                return True
            else:
                return False
        elif(self.seconds <= tocompare.seconds):
            return True
        else:
            return False
        
    def __float__(self):
        return float(self.floatrepr)

    def __repr__(self):
        return ("%s" % (self.floatrepr))
