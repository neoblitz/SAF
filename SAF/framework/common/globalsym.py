# 
# symtable.py - Global Symbol Table
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

import os
import sys
from copy import copy
try:
    from collections import OrderedDict
except:
    from framework.common.dictionary import OrderedDict as OrderedDict


# Local Imports
from framework.parser.parser import ScriptParser
from framework.parser.language import KeywordTokens

class SymbolTable:

    SYMTYPES = {'CONSTANT': 1,
                'DEP': 2,
                'INDEP': 3,
                'GLOBAL': 4,
                'ANY' : 5,
                'BEHAVIOR': 6}

    def __init__(self, logger):
        self.logger = logger
        self.table = OrderedDict()
        self.namespaces = {}
        self.nsmap = {}

    def get_symbol(self, name, var, fullname=None):

        if(fullname):
            key = copy(fullname)
        else:
            key = name + "." + var

        key = key.strip()
        for ns, v in self.table.items():
            if(ns.find(key, -len(key)) >= 0):
                if __debug__: self.logger.fine("Match found in Symbol table for %s in %s"\
                                  % (key, ns))
                return v

        if __debug__: self.logger.fine("NO Match in Symbol Table for " + key)
        return None

    def get_qualified_symbol(self, var, k, newctxt):
        key = copy(var)
        key = key.replace('$', '')
        key = key.strip();

        if newctxt is not None:
            if(key.rfind(".") > 0):
                (oldctxt, dot , dvar) = key.rpartition(".")
                val = newctxt + "." + dvar
                key = val
                if __debug__: self.logger.debug("Key with newctxt " + newctxt + " = " + key)
            else:
                # These are the $1, $2 variables
                val = newctxt + "." + k
                key = val
                if __debug__: self.logger.debug("Key with newctxt " + newctxt + " = " + key)

        for ns, v in self.table.items():
            if(ns.find(key, -len(key)) >= 0):
                if __debug__: self.logger.fine("Qualified symbol found in Symbol table for\
                %s in %s" % (key, ns))
                return '$' + ns
        if __debug__: self.logger.fine("NO Match in Symbol Table for " + key)
        return var


    def has_symbol(self, v):
        sym = v.replace('$', '')
        sym = sym.strip();
        l = len(sym)
        for ns, v in self.table.items():
            if(ns.find(sym, -l) >= 0):
                if __debug__: self.logger.fine("Match found in Symbol table for " + sym)
                return True
        if __debug__: self.logger.fine("NO Match in Symbol Table for " + sym)
        return False

    def get_code_indep(self):
        return self.SYMTYPES.get('INDEP')

    def get_code_dep(self):
        return self.SYMTYPES.get('DEP')

    def get_code_const(self):
        return self.SYMTYPES.get('CONSTANT')

    def get_code_global(self):
        return self.SYMTYPES.get('GLOBAL')

    def get_code_behavior(self):
        return self.SYMTYPES.get('BEHAVIOR')

    def get_code_any(self):
        return self.SYMTYPES.get('ANY')

    def is_state_dependent(self, statename):
        statetype = self.table.get(statename + "_INTERNAL_TYPE_")
        if(statetype == self.get_code_dep()):
            return True
        elif (statetype == self.get_code_indep()):
            return False
        else:
            raise Exception("Unrecognized value in Symbol Table for %s\
            found for %s " % (statetype, statename))

    def is_state_negated(self, statename):
        return self.table.get(statename + "_NEGATION_")

    def get_state_constraint(self, name):
        return self.table.get(name + "_STATE_CONSTRAINT_")

    def get_ns_for_name(self, name):
        return self.nsmap.get(ns, None)

    def build_nsmap(self, basebehavior):
        options = {'log':self.logger,
                        'basebehavior':basebehavior}
        os.path.walk(basebehavior, self.domap, options)

    def display_nsmap(self):
        if __debug__: 
            self.logger.info("Namespace to File Mapping")
            self.logger.info("====================")
            for k, v in self.nsmap.items():
                self.logger.info(k + " ==> " + v)

    def get_filename_from_ns(self, ns):
        return self.nsmap.get(ns, None)

    def is_import_processed(self, imp):
        (ns, n) = imp.rsplit('.', 1)
        if(ns not in self.namespaces):
            return False
        else:
            nlist = self.namespaces[ns]
            if(n not in nlist):
                return False
        return True

    def domap(self, options, dirnames, names):
        for name in names:
            behavior = dirnames + os.path.sep + name
            if os.path.isfile(behavior):
                 (root, ext) = os.path.splitext(behavior)
                 if(ext == ".b"):
                    bp = options.get('basebehavior')
                    self.process_script(bp, behavior)

    def process_script(self, basebehavior, behavior):
        self.logger.info("Processing script %s/%s" % (basebehavior, behavior))
        (fn, namespace, name, config) = ScriptParser.init(basebehavior, behavior)
        if((name is None) or
            (namespace is None)):
            raise Exception("NAME or NAMESPACE not found in %s"\
                             % (behavior))
        key = namespace+"."+name
        if key not in self.nsmap:
            self.nsmap[key] = behavior
        else:
            raise Exception("Namespace/Name pair '%s' already exists! Must be unique." %(key))

    def add_symbols(self, namespace, name, symbolhash):
        if(namespace not in self.namespaces):
            self.namespaces[namespace] = [name]
        else:
            nlist = self.namespaces[namespace]
            if(name not in nlist):
                nlist.append(name)

        prefix = namespace + "." + name + "."

        for k, v in symbolhash.items():
            self.table[prefix + k] = v

    def add_symbol(self, symbol, value, namespace, name):
        if(namespace not in self.namespaces):
            self.namespaces[namespace] = [name]
        else:
            nlist = self.namespaces[namespace]
            if(name not in nlist):
                nlist.append(name)
        prefix = namespace + "." + name + "."
        self.table[prefix + symbol] = value
        return prefix+symbol

    def symtype(self, val):
        var = v = ''
        if(type(val) is str): v = val.strip()
        if __debug__: self.logger.fine("\t Checking type of variable value: " + v)
        if(v.find("_ANY_") >= 0 
           or ((v.find('*') >=0) and (v.find('\*') <0))):
            if __debug__: self.logger.fine("\t Variable value :%s is wildcarded" % (v))
            return self.get_code_any()
        elif(v.find('$') != 0):
            if __debug__: self.logger.fine("\t Value  value: " + v + " is a CONSTANT ")
            return self.get_code_const()
        else:
             if(v.find('.') < 0):
                 if __debug__: self.logger.fine("\t Variable value :%s is independent" % (v))
                 return self.get_code_indep()
             else:
                 if __debug__: self.logger.fine("\t Variable value :%s is dependent" % (v))
                 return self.get_code_dep()

    def display(self):
#        print("Symbol Table")
#        print("==========")
#        for k, v in self.table.items():
#            print("\tSymbol: " + k + " ==> " + str(v))
        if __debug__: 
            self.logger.debug("Symbol Table")
            self.logger.debug("==========")
            for k, v in self.table.items():
                self.logger.debug("\tSymbol: " + k + " ==> " + str(v))

