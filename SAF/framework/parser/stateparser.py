# 
# stateparser.py - Processes state expressions using 
#                     defined EBNF
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
from copy import deepcopy

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
from framework.objects.constraints import ConstraintObject
from framework.objects.behaviortree import Behavior

class StateExprParser(DispatchProcessor):

    def __init__(self, logger, globalsyms, varhash, exprlhs, namespace, name, attrlist):
        self.logger = logger
        self.globalsyms = globalsyms
        self.varhash = varhash
        self.exprlhs = exprlhs
        self.namespace = namespace
        self.name = name
        self.contextvar = None
        self.valid_attrlist = attrlist

        # Set the type of the state to INDEPENDENT by default
        self.globalsyms.add_symbol(self.exprlhs + "_INTERNAL_TYPE_",
                                        self.globalsyms.get_code_indep(),
                                        self.namespace,
                                        self.name)

        # Set the default state constraint to Nothing                    
        self.globalsyms.add_symbol(self.exprlhs + "_STATE_CONSTRAINT_",
                        ConstraintObject(self.exprlhs,BconstraintTokens.CONSTRAINTS),
                        self.namespace,
                        self.name)
        
        self.globalsyms.add_symbol(self.exprlhs + "_NEGATION_",
                                   False,
                                   self.namespace,
                                   self.name)      
        

    def reset(self):
        if __debug__: self.logger.info("Resetting...")
        
        
    def sexpr(self, (tag, start, stop, subtags), buffer):
        """
            sexpr :=   'not'?, ts, (validexpr_1 / validexpr_2 / nullsexpr)
        """
        if __debug__: 
            self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        
        # Check if we have an empty expression
        expr = buffer[start:stop]
        if(not expr):
            return 
        
        retval = dispatchList(self, subtags, buffer)
        if(retval[0] == 'not'):
            if __debug__: 
                self.logger.debug("Set negation for state: %s" % \
                                    (self.exprlhs))
            self.globalsyms.add_symbol(self.exprlhs + "_NEGATION_",
                                       True,
                                       self.namespace,
                                       self.name)            
    
        # Use the context (if any) to resolve all the variables and 
        # add them to the variable hash
        for k, v in self.varhash.items():
            vtype = self.globalsyms.symtype(v)
            if((vtype != self.globalsyms.get_code_const())):
                self.varhash[k] =\
                 self.globalsyms.get_qualified_symbol(v,
                                                      k,
                                                      self.contextvar)
            else:
                self.varhash[k] = v
                        
            if __debug__: 
                self.logger.debug("After appending context %s ===> %s" % \
                                        (k, 
                                         self.varhash[k]))
            
        for attr, value in self.varhash.items():
            if __debug__: 
                self.logger.debug("Processing : %s=%s"%(attr, value))
     
            vtype = self.globalsyms.symtype(value)
            if(vtype == self.globalsyms.get_code_const()):
                # Constant
                newkey = self.exprlhs + "." + attr
                if __debug__: self.logger.debug("Adding to Symtable: %s=%s" % \
                                    (newkey, value))

                self.globalsyms.add_symbol(newkey,
                                           value,
                                           self.namespace,
                                           self.name)
            elif(vtype == self.globalsyms.get_code_any()):
                # WILDCARDED
                newkey = self.exprlhs + "." + attr
                if __debug__: 
                    self.logger.debug("Adding to Symtable: %s=%s"%(newkey, value))

                self.globalsyms.add_symbol(newkey,
                                           value,
                                            self.namespace,
                                            self.name)
            else:
                if(self.globalsyms.has_symbol(value)):
                    self.globalsyms.add_symbol(self.exprlhs + "_INTERNAL_TYPE_",
                                       self.globalsyms.get_code_dep(),
                                       self.namespace,
                                       self.name)
                    if __debug__: 
                        self.logger.debug("Marking state %s dependent!" % \
                                        (self.exprlhs))
                else:
                    # Else this is a template variable like with values 
                    # like $1, $2 etc. Add the attribute and rename the 
                    # variable with an _ prepended
                    newkey = self.exprlhs + "." + attr
                    if __debug__: 
                        self.logger.debug("Adding to symtable: " + newkey)
                    self.globalsyms.add_symbol(newkey,
                                                "",
                                                self.namespace,
                                                self.name)

        if __debug__: 
            self.logger.debug("Result of applying context :" + str(self.varhash))
        return self.varhash

    def validexpr_1(self, (tag, start, stop, subtags), buffer):
        """
            validexpr_1 := '{', ts, (baseform) ,ts, '}'!, ts, (sconstraint)?
        """
        if __debug__: 
            self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        retval = dispatchList(self, subtags, buffer)
       
        if len(retval[1]) == 0:
           self.varhash["eventtype"] = "*"
        
    
    def validexpr_2(self, (tag, start, stop, subtags), buffer):
        """
            validexpr_2 := ts, (importform) ,ts, (sconstraint)?
        """
        if __debug__: 
            self.logger.debug("%s : %s" % (tag, buffer[start:stop]))

        retval = dispatchList(self, subtags, buffer)
        # The list retval will contain elements matching the grammar above

        #----------------------------------------------------------------------
        # Attach the sconstraint (if any) to the behavior
        #
        # There are two distinct cases:
        # 1. The importform is an imported state.
        #        We dont attach the constraint in this case since the constraint
        #        is already read from the global symbol table.
        # 
        # 2. The importform is an imported behavior or a model (also a behavior)
        #    In this case we attach the constraint directly to the behavior
        #----------------------------------------------------------------------
        
        # sconstraint object will be the last element in the retval list
        sconstraint = retval[-1]
        if sconstraint:
            # Importform is a list as the second element of retval with the 
            # first object being the behavior object
            b = retval[1][0]            
            if(isinstance(b, Behavior)):
                b.set_behavior_constraints(sconstraint)
                sconstraint.set_apply_flag(True)                
                if __debug__: 
                    self.logger.info("Set constraint object %s for %s" %\
                                      (sconstraint, b))        
            
            
    def validexpr_3(self, (tag, start, stop, subtags), buffer):
        """
            validexpr_3 := ts, (importform) ,ts, (sconstraint)?
        """
        if __debug__: 
            self.logger.debug("%s : %s" % (tag, buffer[start:stop]))

        retval = dispatchList(self, subtags, buffer)
       
        return retval
    
    def nullexpr(self, (tag, start, stop, subtags), buffer):
        """
            nullexpr  := '{',ts, '}' ts, (sconstraint)?
        """
        if __debug__: 
            self.logger.debug("%s : %s" % (tag, buffer[start:stop]))

        # Look past the initial brackets 
        expr = buffer[start+1:stop-1].strip()
        if(expr == ""):
            self.varhash["eventtype"] = "*"
        retval =  dispatchList(self, subtags, buffer)
        return retval 
    
    def sconstraint(self, (tag, start, stop, subtags), buffer):
        """
            sconstraint := openbracket, bconstraintkey, relop, 
                        (rangevalue/number), ts, closebracket
        """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        retval =  dispatchList(self, subtags, buffer)
        
        # retval contains a list of 7 elements
        # example: [bcount >= 1] produces 
        # ['[', 'bcount', '>=', ' ', '1', ' ',  ']']
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        ckey = retval[1]
        cop  = retval[2]
        cval = retval[4]
        cobj = ConstraintObject(self.exprlhs, BconstraintTokens.CONSTRAINTS)
        cobj.set_constraint(ckey, cop, cval)
        cobj.set_apply_flag(True)

        # Store the constraint object in the global symbol table using the 
        # special constraint key      
        key   = self.exprlhs + "_STATE_CONSTRAINT_"     
        self.globalsyms.add_symbol(key,
                                   cobj,
                                   self.namespace,
                                   self.name)
        return cobj
    
    def importform(self, (tag, start, stop, subtags), buffer):
        """
          importform := importvariable, ts, '(', context?, baseform?, ts, ')' 
        """
        if __debug__: self.logger.debug("%s : %s " % (tag, buffer[start:stop]))
        return dispatchList(self, subtags, buffer)
   
    
    def importvariable(self, (tag, start, stop, subtags), buffer):
        """
          importvariable := identifier, '.', identifier 
        """
        if __debug__: 
            self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        retval =  dispatchList(self, subtags, buffer)
        
        # retval should be a list containing 2 elements
        # 'identifier'  'identifier' 
        if __debug__: 
            self.logger.debug("Parsed Import Variable: %s" % (retval))

        expr = buffer[start:stop]        
        if(len(retval) == 2):
            name = retval[0]
            var = retval[1]
            # Retrieve the symbol expressions stored while parsing earlier imports.
            # The expressions are stored as a hash of attribute->values.
            # So just get them and append to the existing varhash
            symexp = self.globalsyms.get_symbol(name, var)
            if(symexp):
                if __debug__: 
                    self.logger.debug("Symbol table has symbol:"\
                                   + expr + " ==> " + str(symexp))
                
                if(isinstance(symexp, dict)):
                    for key,value in symexp.items():
                        self.varhash[key] = value   
                        if __debug__: 
                            self.logger.debug("ImportVariable: %s : %s ~~> %s" \
                                      %( expr, key, self.varhash[key]))
                    return symexp
                elif(isinstance(symexp, Behavior)):
                    symname =  self.exprlhs 
                    newsymexp = deepcopy(symexp)
                    self.globalsyms.add_symbol(symname, 
                                               newsymexp, 
                                               self.namespace,
                                               self.name)
                    newsymexp.set_alias(self.exprlhs)
                    if __debug__: 
                        self.logger.debug("Set alias %s for %s" \
                                          %(self.exprlhs, newsymexp))
                        self.logger.debug("Added %s ==> %s to symbol table:"\
                                          %(symname, newsymexp))
                    return newsymexp
                else:
                    # Do nothing
                    pass
            else:
                raise Exception("Symbol %s not found in symbol table!" % (expr))
        else:
            raise Exception("UNEXPECTED CONDITION while parsing state "\
                                + expr)
        return retval

    def baseform(self, (tag, start, stop, subtags), buffer):
        """
            baseform :=  (simpleavpair, ','?)* 
        """
        retval = dispatchList(self, subtags, buffer)
        if __debug__: self.logger.debug("baseform: %s" % (retval))
        return retval
        
    
    def simpleavpair(self, (tag, start, stop, subtags), buffer):
        """ 
             simpleavpair := (identifier, relop, "'"?, value, "'"?)
        """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        retval =  dispatchList(self, subtags, buffer)
        if __debug__: self.logger.debug("Parsed AV Pair: %s" % (retval))
        
        if(len(retval) == 3):
            key   = retval[0]
            value = retval[2]
            op    = retval[1]
            self.varhash[key] = value
            
            if(key not in self.valid_attrlist):
                raise SyntaxError("Attribute '%s' is not a valid attribute !" %\
                                   (key))

            # Add the fully qualified key (namespace.name.key) to the symbol table               
            fqkey = self.exprlhs + "." + key + "_op"
            self.globalsyms.add_symbol(fqkey,
                                       op,
                                       self.namespace,
                                       self.name)

            s = self.exprlhs + "." + key
            self.globalsyms.add_symbol(s, "",
                                       self.namespace,
                                       self.name)
                
            if __debug__: 
                self.logger.debug("simpleavpair: %s : %s --> %s" %\
                                  ( retval, key, self.varhash[key]))
        return retval

    def complexavpairs(self, (tag, start, stop, subtags), buffer):
        """
           complexavpairs := ts, (context)?, ","? , (simpleavpair, ','?)*
        """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))

        retval = dispatchList(self, subtags, buffer)
        if __debug__: self.logger.debug("%s" % (retval))
        return retval

    def bconstraintkey(self, (tag, start, stop, subtags), buffer):
        """ 
            bconstraintkey:= ts, ('at'/'end'/'rate'/'icount'/'bcount'/'duration')
        """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        retval =  dispatchList(self, subtags, buffer)
        return getString((tag, start+len(retval[0]), stop, subtags), buffer)


    def relop(self, (tag, start, stop, subtags), buffer):
        """
            relop         := ts, ('>='/'<='/'>'/'='/'<'/'!=') 
        """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        retval =  dispatchList(self, subtags, buffer)
        # Skip over the whitespace
        return getString((tag, start+len(retval[0]), stop, subtags), buffer)
 
 
    def number(self, (tag, start, stop, subtags), buffer):
        """
            Return the value as a string
        """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        num =  getString((tag, start, stop, subtags), buffer)
        try: 
            val1 = int(num)
        except:
            raise SyntaxError("Value '%s' must be valid integer."%\
                              (num))
        
        if((val1 < 0)):
            raise SyntaxError("Value cannot be negative (%s)"%\
                         (val1))
        return num
    
    
    def context(self, (tag, start, stop, subtags), buffer):
        """ 
             context := (ts, '$', identifier), ","?
        """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        retval =  dispatchList(self, subtags, buffer)
        if __debug__: self.logger.debug("Parsed Context: %s" % (retval))
        
        if(len(retval) == 2):
            self.contextvar = retval[1]
        return retval

    def identifier(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        retval =  dispatchList(self, subtags, buffer)
        if __debug__: self.logger.debug("%s" % (retval))
        # Skip over the whitespace
        return getString((tag, start+len(retval[0]), stop, subtags), buffer)

    def negation(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        return 'not'

    def string(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        # Skip over the whitespace
        return getString((tag, start, stop, subtags), buffer)

    def string_single_quote(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        return getString((tag, start, stop, subtags), buffer)

    def ts(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        return getString((tag, start, stop, subtags), buffer)

    def value(self, (tag, start, stop, subtags), buffer):
        """ Return the value as a string """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        retval =  dispatchList(self, subtags, buffer)
        
        # Skip over the whitespace
        return retval[1]

    def rangevalue(self, (tag, start, stop, subtags), buffer):
        """ Return a list [lowval,highval] """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        retval =  dispatchList(self, subtags, buffer)

        # retval contains a list of 3 elements
        # example: [1000:2000] produces 
        # [' ', '1000', '2000']
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        try: 
            val1 = int(retval[1])
            val2 = int(retval[2])
        except:
            raise SyntaxError("Range values '%s:%s' must be valid integers."%\
                              (retval[1],retval[2]))
        
        if((val1 < 0)  or (val2 < 0)):
            raise SyntaxError("Range values cannot be negative (%s:%s)"%\
                         (val1,val2))
        if(val2 < val1):
            raise SyntaxError("Range value '%s' must be lower than '%s'"%\
                         (val1,val2))    
        return (val1, val2)

    def float(self, (tag, start, stop, subtags), buffer):
        """ float         := ts, number, '.', number! """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        retval =  dispatchList(self, subtags, buffer)

        # retval contains a list of 3 elements
        # example: [1000.2000] produces 
        # [' ', '1000', '2000']
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        fstr = ".".join(retval[1:])
        try: 
            val = float(fstr)
        except:
            raise SyntaxError("Val %s must be valid float!"% (fstr))
        
        if(val < 0):
            raise SyntaxError("Val cannot be negative (%s)"%\
                         (val))
        return fstr
    

    def wildcard(self, (tag, start, stop, subtags), buffer):
        """ wildcard      := ts, (_ANY_/*) """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        return getString((tag, start, stop, subtags), buffer)
    
    def dynvalue(self, (tag, start, stop, subtags), buffer):
        """ dynvalue      := ts, '$', [$0-9]+ """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        return getString((tag, start, stop, subtags), buffer)
    
    def depvalue(self, (tag, start, stop, subtags), buffer):
        """ depvalue      := ts, ('$', identifier, '.', identifier) """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        return getString((tag, start, stop, subtags), buffer)

    def openbracket(self, (tag, start, stop, subtags), buffer):
        """ openbracket:= ts, '[' """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        return getString((tag, start, stop, subtags), buffer)

    def closebracket(self, (tag, start, stop, subtags), buffer):
        """ closebracket:= ts, ']' """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        return getString((tag, start, stop, subtags), buffer)
