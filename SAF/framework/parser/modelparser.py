# 
# modelparser.py - Processes model expressions using 
#                     defined EBNF
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

# Standard Library Imports
import os
import sys
from exceptions import Exception

# Third Party Imports
import ConfigParser
from simpleparse.common import numbers, strings, comments
from simpleparse.parser import Parser
from simpleparse import generator
from simpleparse.dispatchprocessor import *


# Local Imports
import framework.objects.behaviortree
import framework.common.dictionary
from language import OperatorTokens, KeywordTokens, SectionTokens
from language import BconstraintTokens, OpconstraintTokens

class ModelExprParser(DispatchProcessor):

    def __init__(self, logger, modelname, modelattrs):
        self.logger = logger
        self.modelname = modelname
        self.modelattrs = modelattrs


    def reset(self):
        if __debug__: self.logger.info("Resetting...")

    '''
        Every function below corresponds to a production rule for 
        behaviors as defined in the grammar
    '''
    def startparens(self, (tag, start, stop, subtags), buffer):
        """
            startparens := '('
        """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))


    def endparens(self, (tag, start, stop, subtags), buffer):
        """
            endparens   := ')'
        """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))


    def identifiers(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        retval = dispatchList(self, subtags, buffer)
        if __debug__: self.logger.debug("identifiers: %s" % (retval))

    def model_output(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))


    def model_id(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        self.modelname.append(buffer[start:stop].strip())

    def identifier(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        attr = buffer[start:stop]
        self.modelattrs.append(attr.strip())

    def ts(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        return getString((tag, start, stop, subtags), buffer)
