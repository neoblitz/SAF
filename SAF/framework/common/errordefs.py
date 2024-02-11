# 
#errordefs.py - Error Definitions
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

from exceptions import Exception


class EventError(Exception):
    """ Raised when Event Fetching or Processing fails """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class SymbolTableError(Exception):
    """ Raised when Symbol Table related processing fails """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.__class__.__name__ + ":" +self.msg)


class StateRecordError(Exception):
    """ Raised when State Record related processing fails """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class ConstraintError(Exception):
    """ Raised when Processing Constraints """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class SyntaxError(Exception):
    """ Raised for syntax errors """
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return self.__class__.__name__ + ":" +self.msg

class AbortCondition(Exception):
    """ Suggests aborting whole program """
    def __init__(self, msg=None):
        self.msg = msg or ""

    def __str__(self):
        return repr(self.msg)

class ModelProcessingError(Exception):
    """ Raised when Processing behaviors """
    def __init__(self, msg=None):
        self.msg = msg or ""

    def __str__(self):
        return repr(self.msg)
