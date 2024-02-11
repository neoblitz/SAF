# process_model.py - Applies the model to data
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

# Standard Imports
import sys
from exceptions import Exception
from bisect import bisect_left
from collections import deque
from operator import itemgetter
from copy import copy, deepcopy

#Local Imports
import framework.objects.behaviortree as behaviortree
import framework.common.utils as utils
import framework.statemanager.statedb as statedb

from framework.parser.language import OperatorTokens, KeywordTokens, SectionTokens
from framework.parser.language import BconstraintTokens, OpconstraintTokens

from framework.common.utils import print_timing
from framework.common.sorted_collection import SortedCollection
from framework.common.errordefs import SyntaxError, AbortCondition, ModelProcessingError

from framework.objects.behaviorinstance import BehaviorInstance
from framework.objects.event import Event
from framework.objects.behaviorinstancelist import BehaviorInstanceList
from framework.dal.dataabstraction import DataManager
from framework.objects.behaviortree import Behavior

from framework.processor.process_behaviorconstraints import BehaviorConstraintProcessor
from framework.processor.process_state import StateProcessor
from framework.processor.process_temporalops import LTLOpsProcessor
from framework.processor.process_intervaltemporalops import ITLOpsProcessor
from framework.processor.process_logicalops import LogicalOpsProcessor


class ModelProcessor:
    """ 
        Applies behavior behaviors to an event database
    """

    def __init__(self, logger, datahandle, statehandle, symt, icache):
        
        self.logger     = logger
        self.dh         = datahandle
        self.sh         = statehandle
        self.globalsyms = symt
        self.qualifierstate = None
        self.icache = icache
                
        self.state_proc      = StateProcessor(self.logger, 
                                              self.dh,
                                              self.sh,
                                              self.globalsyms,
                                              self)
        
        self.b_cons_proc = BehaviorConstraintProcessor(self.logger,
                                                       self.dh,
                                                       self.sh,
                                                       self.state_proc,
                                                       self)

        
        self.temporalop_proc = LTLOpsProcessor(self.logger, 
                                               self.dh,
                                               self.sh,
                                               self.state_proc,
                                               self)
        
        self.intervalop_proc = ITLOpsProcessor(self.logger, 
                                               self.dh,
                                               self.sh,
                                               self.state_proc,
                                               self)

        self.logicalop_proc = LogicalOpsProcessor(self.logger, 
                                               self.dh,
                                               self.sh,
                                               self.state_proc,
                                               self)
         
    def get_instances_satisfying_model(self, model, datahandle):
        """
            Returns instances of data satisfying the model. 
            Note that a model is a top-level behavior formula.
        """

        self.model = model        
        self.data  = datahandle

        if __debug__: 
            self.logger.info("Applying behavior %s of tree %s " % \
                           (model.get_name(), 
                            model.get_parent()))

        # The treelevel variable indicates the level being currently
        # processed in the behavior tree. Its only use is when printing the 
        # behavior dump whenever --verbose behavior is specified
        treelevel = 0
        return self.process_behavior(model, BehaviorInstanceList([],bobject=model), 
                                     treelevel)
        
    
    def process_behavior(self, behaviorobj, recordids, treelevel, objlist=None,
                            callerobj=None, ignorequalifier=False):
        """
            behavior objects represent grouped subbehavior of a behavior.
            behaviors can contains subbehaviors within themselves.
        """

        if __debug__: 
            self.logger.behavior(treelevel, "--> %s (IN: %s Type: %s)" %\
                                          (behaviorobj.get_name(),
                                           len(recordids), 
                                           type(recordids)))

        objlist = behaviorobj.get_objects()
        currobj = None
        prevobj = None
        nextobj = None

        if(not objlist):
            return BehaviorInstanceList()

        # Initialize the state tables when a QUALIFIER is encountered.
        # The QUALIFIER can be encountered many times during a run. 
        if(objlist[0].is_qualifier() and (ignorequalifier == False)):
            if __debug__:
                self.logger.info("Initializing state tables for %s.." %\
                                 (behaviorobj))     
            self.sh.initialize_state(behaviorobj)
            
        index = 0
        skip_next_object = False
        binstances = BehaviorInstanceList()
        # Get a list of objects constituting the model 
        # An object represents either a 
        # a) qualifier 
        # b) state expression
        # c) operators (logical, linear temporal, interval temporal)
        # d) another behavior object
        for obj in objlist:
            
            if((ignorequalifier and obj.is_qualifier()) or (skip_next_object)):
                index += 1
                skip_next_object = False
                continue

            if (index < (len(objlist) - 1)):
                nextobj = objlist [index + 1]               

           
            #-------------
            # Sub-behavior
            #-------------
            if(obj.is_behavior_object()):
                binstances = self.process_behavior(obj.get_contents(),
                                               binstances or recordids,
                                               treelevel + 3,
                                               callerobj=callerobj,
                                               ignorequalifier=ignorequalifier)
                obj.add_instances(binstances)

                # The QUALIFIER expression is treated as a behavior.
                # The statetable is initialized whenever the qualifier 
                # is encountered.
                if((obj.is_qualifier()) and (ignorequalifier == False)):
                   
                    qualifier_expr =  self.globalsyms.get_symbol(
                                                    obj.get_namespace(),
                                                    obj.get_name(),
                                                    None)
                    self.sh.add_instances_to_statetable(binstances, 
                                                        obj, 
                                                        qualifier_expr)
                    # Set the recordids to point to the ones returned
                    # by the qualifier
                    recordids = binstances
                    
                    
                    # Set the qualifying instances over which the  
                    # behaviors are evaluated
                    self.state_proc.set_qualifying_instances(binstances)

                prevobj = obj
            
            #-------------------------------------------
            # Simple behaviors (aka state propositions)
            #-------------------------------------------
            if(obj.is_state_node()):
                binstances = self.state_proc.process_state(obj,
                                           recordids,
                                           treelevel + 2,
                                           callerobj)
                if (not binstances):
                    if __debug__:
                        self.logger.warning("No instances satisfying (%s)" %\
                                          (obj.get_name()));
                    return binstances
                obj.add_instances(binstances)
                prevobj = obj
            
            #-------------------------------------------
            # Logical Operators (and, or, xor, not/neg)
            #-------------------------------------------
            if(obj.is_logical_op()):
                binstances = self.logicalop_proc.process_logicalop(obj, 
                                                     prevobj, 
                                                     nextobj, 
                                                     recordids, 
                                                     treelevel+2)
                skip_next_object = True
                prevobj = obj

            #-----------------------------
            # Temporal Operators (~>, [])
            #-----------------------------
            if(obj.is_leadsto_op()):
                binstances = self.temporalop_proc.process_leadstoop(
                                      obj, prevobj, nextobj, 
                                      recordids, treelevel+2)
                # Leadsto Op processing also processes the next object in the 
                # objlist. So skip the already processed object 
                skip_next_object = True
                prevobj = obj
            
            #------------------------------------------------------
            # Interval Temporal Operators (olap, sw, ew, dur, eq)
            #-------------------------------------------------------
            if(obj.is_conc_op()):
                binstances =\
                     self.intervalop_proc.process_concurrent_ops(obj, 
                                                                 prevobj,
                                         nextobj, recordids, treelevel + 2)
                skip_next_object = True
                prevobj = obj

            #---------------------
            # Recursive behaviors
            #---------------------
            if(obj.is_type_recursion()):
                binstances =\
                     self.process_recursion(obj, 
                                           recordids, 
                                           treelevel + 2)
                #skip_next_object = True
                prevobj = obj


            index += 1
            
        #-------------------------------
        # Process behavior Constraints
        #-------------------------------
        constraints = behaviorobj.get_behavior_constraints()
        if(constraints):
            newbinstances = self.b_cons_proc.apply_behavior_constraints(behaviorobj,
                                                                    constraints,
                                                                    binstances)
            behaviorobj.add_instances(newbinstances)
            binstances = newbinstances
            self.sh.flush_cache()
        else:
            behaviorobj.add_instances(binstances)
            
#        fullobjname = behaviorobj.get_name()
#        if(self.globalsyms.is_state_negated(fullobjname)):
#            print "Here"
#            pass
##            if(ret_instances):
##                insts_to_remove = ret_instances.get_ids()
##                neg_instances = BehaviorInstanceList() 
##                neg_instances.set_behavior(stateobj)
##                for inst in in_binstances:
##                    ids = inst.get_ids()
##                    for id in ids:
##                        if(id not in insts_to_remove):
##                            neg_instances.insert(inst)
##                ret_instances = neg_instances
#            
        
        
        if __debug__: 
            self.logger.behavior(treelevel, "<-- %s (OUT: %s Type: %s)" %\
                                      (behaviorobj.get_name(),
                                       len(binstances), 
                                       type(binstances)))
        
        # Print minimal information
        if((not behaviorobj.is_behavior_anon()) and 
                (behaviorobj.get_name() != 'QUALIFIER') and 
                (behaviorobj.get_name() != self.model.get_name())):
            utils.lprint(1, "Behavior %s .. found %d instances" %\
                         (behaviorobj.get_name(), len(binstances)))

        elif((behaviorobj.get_name() == 'QUALIFIER') and (ignorequalifier == False)):
             utils.lprint(2, "QUALIFIER matched %d instances" %\
                         (len(binstances)))
        
        return binstances

    def process_recursion(self, obj,  in_binstances, treelevel, callerobj=None):

        if __debug__:
            self.logger.behavior(treelevel, "--> %s (IN: %s Type: %s)" % \
                     (obj.get_name(), len(in_binstances), type(in_binstances)))
            self.logger.fine("Record IDs  : " + str(in_binstances))

        self.sh.flush_cache()
 
        nextobj = obj.get_contents()
        if(not isinstance(nextobj, Behavior)):
            raise Exception("Unhandled object type during recursion!")   

        # Create an empty return list
        ret_instances = BehaviorInstanceList()
        ret_instances = self.process_behavior(nextobj, 
                                            in_binstances,
                                            treelevel + 1,
                                            objlist=None,
                                            callerobj=callerobj,
                                            ignorequalifier=True)
        if __debug__:
            self.logger.fine("Returned list from behavior processing : %s" % \
                         (ret_instances))

        # Add the instances to the nextobject
        #nextobj.add_instances(ret_instances)

        # Apply constraints along with the operator-specific semantics
        constraints = obj.get_constraints()
        if __debug__:
            self.logger.info("Operator Constraints :%s" % (constraints))

        deltatime = None
        cop = None
        if(constraints):
            ctuple = constraints.get_constraint()
            (cname, cop, cval, cqual) = ctuple
            deltatime = Time()
            deltatime.set_time_from_str(cval, cqual)
            self.logger.info("Time delta :%s" % (deltatime))

        parop_instances = \
            self.apply_concurrent_semantics(obj, prevobj,
                                            nextobj, deltatime, cop)
        obj.add_instances(parop_instances)

        if __debug__:
            self.logger.debug("Instance List after applying parallel operator :%s" % \
                               (parop_instances))

        if __debug__:
            self.logger.behavior(treelevel, "<-- %s (OUT: %s  Type: %s)" % \
                    (obj.get_name(), len(parop_instances),
                     type(parop_instances)))

        return parop_instances


