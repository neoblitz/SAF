# 
# behaviorparser.py - Processes behavior expressions using 
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
import framework.common.dictionary
import framework.common.utils as utils
from language import OperatorTokens, KeywordTokens, SectionTokens
from language import BconstraintTokens, OpconstraintTokens
from framework.parser.stateparser import StateExprParser
from framework.objects.constraints import ConstraintObject
import framework.objects.behaviortree as behaviortree
from framework.objects.behaviortree import Behavior

class BehaviorExprParser(DispatchProcessor, StateExprParser):
    """
        Parser class for parsing behavior expressions
    """

    def __init__(self, logger, behaviortree, statehash, bhash, phash,
                  statebehavior, packagepath, stateopts=None, model=False, symt=None):
        self.logger = logger
        self.behaviortree = behaviortree
        self.statehash = statehash
        self.behaviorhash = bhash
        self.rootbehavior = statebehavior
        self.namespace = packagepath
        self.behaviorhash = phash
        self.globalsyms = symt
        
        # Behaviorstack maintains the recursive stacks of behaviors
        self.behaviorstack = []
        
        # Points to the currently active behavior
        self.currentbehavior = self.rootbehavior
        self.behavior_for_constraints = self.currentbehavior
        self.op_for_constraints = None
        self.stateopts = stateopts
               
        # List of valid attributes for a state declaration
        self.valid_attr_list = self.stateopts['validattrs']
        self.is_model = model


    def reset(self):
        if __debug__: self.logger.info("Resetting...")
        
    '''
        Every function below corresponds to a production rule for 
        behaviors as defined in the grammar
    '''     
        
    def sexpr(self, (tag, start, stop, subtags), buffer):
        """
           
        """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        expr = buffer[start:stop].strip()
        if(not expr):
            return
        
        self.varhash = {}
        if(self.stateopts):
            statename = "anonstate_"+utils.get_randstring(10)
            StateExprParser.__init__(self, self.logger, 
                                     self.stateopts['symt'], 
                                     self.varhash,
                                     statename, 
                                     self.stateopts['ns'],    
                                     self.stateopts['name'],
                                     self.valid_attr_list)
            retval = StateExprParser.sexpr(self, (tag,start,stop,subtags),buffer)
            if not retval: return
            
            fullname = []
            if("eventtype" in self.varhash):
                val = self.varhash['eventtype']
                self.globalsyms.display()
                fullname.append(self.namespace)
                fullname.append(self.name)
                fullname.append(statename)
                fullname.append("eventtype_op")
                op = self.globalsyms.get_symbol(None, None, 
                                                fullname=".".join(fullname))
                if(op == "="):
                    val = val.strip("'") 
                    self.stateopts['etypelist'].append(val)
                                    
            self.statehash[statename] = buffer[start:stop]                      
            statecontents = self.statehash[statename].strip()
            negation = False
            if(statecontents.startswith("not")):
                negation = True

            # First check if there is a behavior indexed using the fullname
            fullname = self.namespace + "." + self.name + "." + statename
            b = self.globalsyms.get_symbol(None, None, fullname)
            if b and isinstance(b, Behavior):
                existingbehavior = deepcopy(b)
                # Add existing behavior to path
                self.behaviortree.add_existing_behavior(self.currentbehavior,
                                             existingbehavior, 
                                              self.namespace+"."+self.name)
                existingbehavior.set_rootbehavior(self.rootbehavior)

            
                if __debug__: 
                    self.logger.info("\tAdded behavior: %s to behavior %s " % \
                          (existingbehavior.get_name(), 
                            self.currentbehavior.get_name()))

                sym = self.globalsyms.add_symbol(self.stateopts['token'],
                                       existingbehavior,
                                       self.namespace,
                                       self.name)
                if __debug__: 
                    self.logger.info("\tAdded  %s ==> %s to symtable " % \
                          (sym, 
                            existingbehavior))

            else:
                snode = self.behaviortree.add_statenode(statename,
                                                        statecontents,
                                                        self.currentbehavior,
                                                        self.namespace+"."+self.name
                                                        )
                snode.set_negation(negation)
                snode.set_rootbehavior(self.rootbehavior)
                if __debug__: 
                    self.logger.info("\tAdded State node: %s (neg: %s) to behavior %s " % \
                              (snode.get_name(), snode.get_negation(),
                                self.currentbehavior.get_name()))
                self.globalsyms.add_symbol(statename,
                                           retval,
                                           self.stateopts['ns'],
                                           self.stateopts['name'])


    def bstartsymbol(self, (tag, start, stop, subtags), buffer):
        """
            bstartsymbol := '('
        """
        if __debug__: 
            self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
            self.logger.debug("\tAdding a new behavior node ")

        # Start a new behavior
        newbehavior = self.behaviortree.add_behaviornode(
                                              self.currentbehavior,
                                              self.namespace);
        newbehavior.set_rootbehavior(self.rootbehavior)
        
        # Push the old behavior into the stack
        self.behaviorstack.append(self.currentbehavior)

        # Set the currentbehavior to the newly created behavior
        self.currentbehavior = newbehavior

        if __debug__: 
            self.logger.debug("\tCreated New behavior: %s " %\
                               (newbehavior.get_name()))


    def simpleoperand(self, (tag, start, stop, subtags), buffer):
        """
            simpleoperand := ts, 'not'?, identifier, ts   
        """
        if __debug__: 
            self.logger.debug("%s : %s " % (tag, buffer[start:stop]))

        statename = buffer[start:stop]
        statename = statename.strip()

        negation = False
        if(statename.startswith("not")):
            negation = True
            statename = statename[3:].strip()
            onode = self.behaviortree.add_notop(self.currentbehavior,
                                                self.namespace)
            onode.set_rootbehavior(self.rootbehavior)
            if __debug__: self.logger.debug("\tAdded Operator node: %s to behavior %s " % \
                           (onode.get_name(),
                            self.currentbehavior.get_name()))
        
        try:
            fullname = self.namespace + "." + statename
            b = self.globalsyms.get_symbol(None, None, fullname)
            if(isinstance(b,Behavior)):
                if(statename in self.behaviorhash):                    
                    existingbehavior = deepcopy(self.behaviorhash[statename])
                else:
                    # It is important to create a copy of the behavior 
                    # since the objects within a behavior store 
                    # context-specific internal state
                    existingbehavior = deepcopy(b)
                    
                if (isinstance(existingbehavior, Behavior)):    
                    if(existingbehavior.get_name() ==
                        self.rootbehavior.get_name()):
                        if __debug__:
                            self.logger.info("RECURSION DETECTED (%s %s)!!"\
                                                  %(existingbehavior.get_name(),
                                                    self.rootbehavior.get_name()))
                        self.behaviortree.add_recursionnode(
                                                    self.currentbehavior,
                                                    self.namespace,
                                                    existingbehavior)
                        if __debug__:
                            self.logger.info("Current Behavior %s !!"\
                                                  %(existingbehavior))
                        return
                
                if __debug__: 
                    self.logger.debug("Behavior %s found in symbol table!!" % 
                                      (statename))
                # Add existing behavior to path                
                self.behaviortree.add_existing_behavior(self.currentbehavior,
                                                 existingbehavior, 
                                                 self.namespace)
                existingbehavior.set_rootbehavior(self.rootbehavior)
                
                if __debug__: 
                    self.logger.debug("\tAdded Behavior node: %s (neg: %s) to behavior %s " % \
                           (existingbehavior.get_name(), 
                            existingbehavior.get_negation(),
                            self.currentbehavior.get_name()))
                    self.logger.debug("behavior: %s" % (self.currentbehavior))
            else:
                statecontents = self.statehash[statename]
                snode = self.behaviortree.add_statenode(statename,
                                                        statecontents,
                                                        self.currentbehavior,
                                                        self.namespace)
                snode.set_negation(negation)
                snode.set_rootbehavior(self.rootbehavior)
                
                if __debug__: 
                    self.logger.debug("\tAdded State node: %s (neg: %s) to behavior %s " % \
                           (snode.get_name(), snode.get_negation(),
                            self.currentbehavior.get_name()))
                
        except KeyError:
            raise Exception("Invalid behavior %s!\n" % (statename))           


    def bop(self, (tag, start, stop, subtags), buffer):
        """
            bop            := ts, ('~>'/'<>'/'[]'/','/'|')
        """
        if __debug__: self.logger.debug("%s : %s " % (tag, buffer[start:stop]))

        op = buffer[start:stop]
        op = op.strip()

        onode = None
        if (op == OperatorTokens.LEADSTO):
            onode = self.behaviortree.add_causalop(self.currentbehavior,
                                        self.namespace)
        elif(op == OperatorTokens.ALWAYS):
            onode = self.behaviortree.add_alwaysop(self.currentbehavior,
                                         self.namespace)
        elif(op == OperatorTokens.AND):
            onode = self.behaviortree.add_andop(self.currentbehavior,
                                         self.namespace)
        elif(op == OperatorTokens.OR):
            onode = self.behaviortree.add_orop(self.currentbehavior,
                                         self.namespace)
        elif(op == OperatorTokens.NOT):
            onode = self.behaviortree.add_notop(self.currentbehavior,
                                         self.namespace)
        elif(op == OperatorTokens.XOR):
            onode = self.behaviortree.add_xorop(self.currentbehavior,
                                         self.namespace)
        elif(op == OperatorTokens.OVERLAP):
            onode = self.behaviortree.add_overlapop(self.currentbehavior,
                                         self.namespace)
        elif(op == OperatorTokens.EQ):
            onode = self.behaviortree.add_eqop(self.currentbehavior,
                                         self.namespace)
        elif(op == OperatorTokens.SW):
            onode = self.behaviortree.add_swop(self.currentbehavior,
                                         self.namespace)
        elif(op == OperatorTokens.EW):
            onode = self.behaviortree.add_ewop(self.currentbehavior,
                                         self.namespace)
        elif(op == OperatorTokens.DUR):
            onode = self.behaviortree.add_durop(self.currentbehavior,
                                         self.namespace)
        else:
            raise Exception("Unrecognized operator: %s found in %s" % \
                             (op, buffer))

        onode.set_rootbehavior(self.rootbehavior)
        self.op_for_constraints = onode
        if __debug__: self.logger.debug("\tAdded Operator node: %s to behavior %s " % \
                           (onode.get_name(),
                            self.currentbehavior.get_name()))


    def bendsymbol(self, (tag, start, stop, subtags), buffer):
        """
            bendsymbol   := ')'
        """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        self.behavior_for_constraints = self.currentbehavior
        self.currentbehavior = self.behaviorstack.pop()
        if __debug__: 
            self.logger.debug("\tJumping to previous behavior %s" % \
                          (self.currentbehavior.get_name()))


    def bkeyval(self, (tag, start, stop, subtags), buffer):
        """
           bkeyval := bconstraintkey, relop, ts,  number, ('s'/'ms')?
        """
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))

        # Call dispatch to get the bconstraintkey, relop and number 
        retval = dispatchList(self, subtags, buffer)
        if __debug__: self.logger.debug("%s" % (retval))

        qualifier = None
        if(len(retval) >= 4):
            bconkey = retval[0].strip()
            relop = retval[1].strip()
            number = retval[3].strip()
        else:
            raise Exception("Syntax Error in %s" % (buffer))


        if(len(retval) == 5):
            qualifier = retval[4].strip()

        # Create a constraint object and add it to the behavior
        constraint_obj = behaviortree.BehaviorTreeBehaviorConstraints(\
                                    self.behavior_for_constraints.get_name())

        constraint_obj.set_constraint(bconkey, relop, number, qualifier)
        self.behavior_for_constraints.set_behavior_constraints(constraint_obj)
        
        if __debug__: 
            self.logger.debug("\tAdded constraints %s to behavior %s" % \
                        (constraint_obj, self.behavior_for_constraints.get_name()))


    def bopconstraint(self, (tag, start, stop, subtags), buffer):
        """ 
             bopconstraint  := relop, ts, number, sec_or_ms_or_usec?
        """
        # Call dispatch to get the relop,  number and/or sec_or_ms_or_usec 
        retval = dispatchList(self, subtags, buffer)
        if __debug__: self.logger.debug("%s" % (retval))

        qualifier = None
        if(len(retval) >= 3):
            bopkey = retval[0].strip()
            number = retval[2].strip()
        else:
            raise Exception("Syntax Error in %s" % (buffer))

        if(len(retval) == 4):
            qualifier = retval[3].strip()

        # Create a constraint object and add it to the behavior
        constraint_obj = behaviortree.BehaviorTreeOpConstraints(
                                        self.currentbehavior.get_name())

        # Put "=" by default as the relational operator
        constraint_obj.set_constraint(bopkey, bopkey, number, qualifier)
        self.op_for_constraints.set_constraints(constraint_obj)
        
        if __debug__: 
            self.logger.debug("\tAdded constraints %s to op %s" % \
                        (constraint_obj, self.op_for_constraints.get_name()))


    def bopconskey(self, (tag, start, stop, subtags), buffer):
        """ 
             bopconskey     := ts, ('within'/'after')
        """
        if __debug__: 
            self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        return getString((tag, start, stop, subtags), buffer)

    def sec_or_ms_or_usec(self, (tag, start, stop, subtags), buffer):
        """
            sec_or_ms_or_usec:= ts, ('s'/'ms'/'us'/'secs'/'msecs'/'usecs')
        """
        if __debug__: 
            self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        return getString((tag, start, stop, subtags), buffer)


    def bconstraints(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        return dispatchList(self, subtags, buffer)

    def behavior_decl(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        return dispatchList(self, subtags, buffer)

    def bexpr(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        if __debug__: self.logger.debug("%s : %s" % (tag, buffer[start:stop]))
        # Start a new behavior by default
        newbehavior = self.behaviortree.add_behaviornode(
                                              self.currentbehavior,
                                              self.namespace);
        newbehavior.set_rootbehavior(self.rootbehavior)
        
        # Push the old behavior into the stack
        self.behaviorstack.append(self.currentbehavior)

        # Set the currentbehavior to the newly created behavior
        self.currentbehavior = newbehavior

        if __debug__: 
            self.logger.debug("\tCreated New behavior: %s " %\
                               (newbehavior.get_name()))
        retval = dispatchList(self, subtags, buffer)

    def behaviorops(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        return dispatchList(self, subtags, buffer)

    def operand2(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        return dispatchList(self, subtags, buffer)

    def operand1(self, (tag, start, stop, subtags), buffer):
        """Process the given production and it's children"""
        return dispatchList(self, subtags, buffer)
