# process_logicalops.py - Functions for processing logical operators
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

import framework.common.sqlutils as sqlutils
from framework.objects.behaviorinstancelist import BehaviorInstanceList

class LogicalOpsProcessor:
    """
        Provides a behavior abstraction for the model processing algorithm.
    """
       
    def __init__(self, logger, datahandle, statehandle, stateproc, modelproc):
        self.sh      = statehandle
        self.dh      = datahandle
        self.logger  = logger
        self.state_proc = stateproc
        self.model_proc  = modelproc
    
    
    def process_orop(self, obj, prevobj, nextobj):
                        
        # Semantics of OR 
        #     Returns an empty list only if both the 
        #     behavior instance lists are empty otherwise
        #     just return whichever is non-empty 
        lhs_instances = prevobj.get_instances()
        rhs_instances = nextobj.get_instances()

        if(len(lhs_instances) or len(rhs_instances)):      
            obj.add_instances(lhs_instances)
            obj.add_instances(rhs_instances)
        else:
            obj.add_instances(BehaviorInstanceList())
       
    
    def process_andop(self, obj, prevobj, nextobj):
                
        # Semantics of AND 
        #    Returns instances of both lists if non-empty 
        #    and returns a empty list otherwise
        lhs_instances = prevobj.get_instances()
        rhs_instances = nextobj.get_instances()
        
        if(len(lhs_instances) and len(rhs_instances)):      
            obj.add_instances(lhs_instances)
            obj.add_instances(rhs_instances)
        else:
            obj.add_instances(BehaviorInstanceList())
    

    def process_xorop(self, obj, prevobj, nextobj):
        
        # Semantics of XOR 
        #     Returns an empty list when both the 
        #     behavior instance lists are simultaneously empty 
        #     or both are simultaneously non-empty 
        lhs_instances = prevobj.get_instances()
        rhs_instances = nextobj.get_instances()
        
        # a xor b = (a and !b) or (b and !a)
        len_lhs = len(lhs_instances)
        len_rhs = len(rhs_instances)
        if len_lhs and (not len_rhs) :
            obj.add_instances(lhs_instances)
        elif len_rhs and (not len_lhs):
            obj.add_instances(rhs_instances)
        else:      
            obj.add_instances(BehaviorInstanceList())


    def process_notop(self, obj, nextobj):
                
        # Semantics of NOT 
        #    Returns an empty list if the
        #    specified behavior instance list is non empty
        #    Else returns a special instance list 
        rhs_instances = nextobj.get_instances()
               
        if(len(rhs_instances) > 0):
            obj.add_instances(BehaviorInstanceList())
        else:
            obj.add_instances(BehaviorInstanceList(special=True))
        
        
    
    def process_logicalop(self, obj, prevobj, nextobj, in_binstances, treelevel):

        if __debug__: 
            self.logger.behavior(treelevel, "--> %s (IN: %s Type: %s)" % \
                                      (obj.get_name(),
                                       len(in_binstances),
                                       type(in_binstances))
                                     )
            self.logger.fine("Record IDs  : " + str(in_binstances))
       
        self.sh.flush_cache()
        binstances = []
        
        if(nextobj.is_behavior_object()):
            objlist = nextobj.get_contents().get_objects()
            binstances = self.model_proc.process_behavior(nextobj.get_contents(),
                                      in_binstances,
                                      treelevel+1,
                                      objlist=None,
                                      callerobj=None)
            if __debug__: 
                self.logger.fine("Returned list from behavior processing : %s" % \
                             (binstances))
        else:
            # Process the next object
            if(nextobj.is_state_node()):
                fullobjname = nextobj.get_fullname()    
                if self.dh.globalsyms.is_state_dependent(fullobjname):
                    binstances = self.state_proc.process_state(nextobj,
                                                    prevobj.get_instances(),
                                                    treelevel+1,
                                                    callerobj=obj)
                else:
                    binstances = self.state_proc.process_state(nextobj,
                                                    in_binstances,
                                                    treelevel+1,
                                                    callerobj=obj)
                    
                if __debug__: 
                    self.logger.fine("Returned IDs : %s" % (binstances))
            else:
                raise Exception("UNEXPECTED object %s of type %s after \
                 %s" % (nextobj.get_name(), nextobj.get_type(), obj.get_name()))

        nextobj.add_instances(binstances)
        
        if(obj.is_or_op()):
            self.process_orop(obj, prevobj, nextobj)
        elif(obj.is_xor_op()):
            self.process_xorop(obj, prevobj, nextobj)
        elif(obj.is_and_op()):
            self.process_andop(obj, prevobj, nextobj)
        elif(obj.is_not_op()):
            self.process_notop(obj, nextobj)
        else:
            raise SyntaxError("Unrecognized logical operator - %s" %\
                               (obj.get_name()))
        
        if __debug__: 
            self.logger.behavior(treelevel, "<-- %s (OUT: %s  Type: %s)" % \
                                    (obj.get_name(),
                                     len(obj.get_instances()),
                                     type(obj.get_instances())))
        return obj.get_instances()