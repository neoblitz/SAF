# 
# language.py - Language  definitions
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

class OperatorTokens:
    LEADSTO = "~>"
    SUMMOUTPUT = ">>"
    PARALLEL_SPEC = "or"
    AND = "and"
    OR = "or"
    XOR = "xor"
    NOT = "not"
    ALWAYS = "[]"
    OVERLAP = "olap"
    SW = "sw"
    EW = "ew"
    DUR = "dur"
    EQ =  "eq"
    
    def __init__(self):
        pass

class KeywordTokens:
    KEYWORD_INIT = "QUALIFIER"
    KEYWORD_NAME = "NAME"
    KEYWORD_ROOT = "ROOT"
    KEYWORD_DEP = "IMPORT"
    KEYWORD_NAMESPACE = "NAMESPACE"

    def __init__(self):
        pass

class SectionTokens:
    SECTION_HEADER = "header"
    SECTION_BEHAVIOR = 'behavior'
    SECTION_STATES = 'states'
    SECTION_MODEL = 'model'

    def __init__(self):
        pass

class BconstraintTokens:
    CONSTRAINTS = ["at", "duration", "end", 
                   "icount", "bcount", "rate",
                   "_limit", "_eventno"]
   
    def __init__(self):
        pass

class OpconstraintTokens:
    CONSTRAINTS = ['>=','<=','>','=','<','!=']
   
    def __init__(self):
        pass

