# commonterms.py - Provides parsers and interpreters for commonly used terms
#                  for plugins
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
from simpleparse import common, objectgenerator
from simpleparse.common import chartypes
from simpleparse.dispatchprocessor import *
import string
from datetime import tzinfo, timedelta, datetime

ZERO = timedelta(0)
HOUR = timedelta(hours=1)


c = {}

declaration = r"""
timestamp := (ts, epoch, ('.',microsec)?) / (ts, month, ts, day, ts, time) 
microsec := [0-9]+
epoch   := [0-9]+
month   := [A-Za-z],[a-z],[a-z]
day     := [0-9],[0-9]?
time    := ts, hour, ':', min, ':', sec
hour    := [0-9],[0-9]
min     := [0-9],[0-9]
sec     := [0-9],[0-9]
year    := [0-9],[0-9],[0-9],[0-9]
tzone   := ('-'/'+'), [0-9],[0-9],[0-9],[0-9]
ts      := [ \t]*
"""

_p = Parser(declaration)
for name in ["timestamp", "day", "time", "hour", "min", "sec", "month", "year", "tzone","epoch", "microsec"]:
	c[ name ] = objectgenerator.LibraryElement(
		generator=_p._generator,
		production=name,
	)

if __name__ == "__main__":
	test()

common.share(c)

class MonthInterpreter(DispatchProcessor):
		
	MONTH_MAP = {'Jan': 1,
				 'Feb': 2,
				 'Mar': 3,
				 'Apr': 4,
				 'May': 5,
				 'Jun': 6,
				 'Jul': 7,
				 'Aug': 8,
				 'Sep': 9,
				 'Oct': 10,
				 'Nov': 11,
				 'Dec': 12}
		
	def month(self, (tag, left, right, children), buffer):
		m = getString((tag, left, right, children), buffer)
		intm = self.MONTH_MAP.get(m) 
		return ("month",intm)

class DayInterpreter(DispatchProcessor):
		
	def day(self, (tag, left, right, children), buffer):
		return ("day", int(buffer[left:right]))

class WhiteSpaceInterpreter(DispatchProcessor):
	def ts(self, (tag, start, stop, subtags), buffer):
		"""Process the given production and it's children"""
		return getString((tag, start, stop, subtags), buffer)

class HourInterpreter(DispatchProcessor):
	def hour(self, (tag, start, stop, subtags), buffer):
		"""Process the given production and it's children"""
		return ("hour", int(buffer[start:stop]))

class SecInterpreter(DispatchProcessor):
	def sec(self, (tag, start, stop, subtags), buffer):
		"""Process the given production and it's children"""
		return ("sec", int(buffer[start:stop]))

class MinInterpreter(DispatchProcessor):
	def min(self, (tag, start, stop, subtags), buffer):
		"""Process the given production and it's children"""
		return ("min", int(buffer[start:stop]))

class YearInterpreter(DispatchProcessor):
	def year(self, (tag, start, stop, subtags), buffer):
		"""Process the given production and it's children"""
		return ("year", int(buffer[start:stop]))

class MicrosecInterpreter(DispatchProcessor):
	def microsec(self, (tag, start, stop, subtags), buffer):
		"""Process the given production and it's children"""
		return ("microsec", int(buffer[start:stop]))

class EpochInterpreter(DispatchProcessor):
	def epoch(self, (tag, start, stop, subtags), buffer):
		"""Process the given production and it's children"""
		return ("epoch", int(buffer[start:stop]))

class TzoneInterpreter(DispatchProcessor):
	def tzone(self, (tag, start, stop, subtags), buffer):
		"""Process the given production and it's children"""
		tz = FixedOffset(int(buffer[start:stop])*60,buffer[start:stop])
		return ("tzinfo", tz)

class TimeInterpreter(DispatchProcessor):

	ts = WhiteSpaceInterpreter()
	hour = HourInterpreter()
	min =  MinInterpreter()
	sec =  SecInterpreter()
	year = YearInterpreter()
	
	def time(self, (tag, start, stop, subtags), buffer):
		"""Process the given production and it's children"""
		retval = dispatchList(self, subtags, buffer)
		return retval

class TimestampInterpreter(DispatchProcessor):
	time  = TimeInterpreter()
	day = DayInterpreter()
	month = MonthInterpreter()
	ts = WhiteSpaceInterpreter()
	epoch = EpochInterpreter()
	microsec = MicrosecInterpreter()

	def timestamp(self, (tag, start, stop, subtags), buffer):
		"""Process the given production and it's children"""
		retval = dispatchList(self, subtags, buffer)
		return retval
	

# A class building tzinfo objects for fixed-offset time zones.
# Note that FixedOffset(0, "UTC") is a different way to build a
# UTC tzinfo object.

class FixedOffset(tzinfo):
    """Fixed offset in hours east from UTC."""
    def __init__(self, offset, name):
        self.__offset = timedelta(minutes = offset)
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
		return timedelta(hours=1)
		