# process_temporalops.py - Functions for processing linear temporal
#                          operators
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
from framework.objects.event import Event
from framework.objects.eventgroup import EventGroup
from framework.objects.timeobject import Time

class LTLOpsProcessor:
    """
        Processor for linear temporal operators leadsto(~>) and always([])
    """
       
    def __init__(self, logger, datahandle, statehandle, stateproc, modelproc):
        self.sh      = statehandle
        self.dh      = datahandle
        self.logger  = logger
        self.state_proc = stateproc
        self.model_proc  = modelproc
        

    def process_leadstoop(self, obj, prevobj, nextobj, in_binstances, treelevel):

        # Get the list of instances matching the previous state
        prev_instances = prevobj.get_instances();

        if __debug__: 
            self.logger.behavior(treelevel,"--> %s (IN: %s Type: %s)" %\
                     (obj.get_name(), len(prev_instances),type(prev_instances)))
            self.logger.fine("Record IDs  : " + str(prev_instances))
        
        self.sh.flush_cache()
        
        # Create an empty return list
        ret_instances = BehaviorInstanceList()
        
        if(nextobj.is_behavior_object()):
            objlist = nextobj.get_contents().get_objects()
            ret_instances = self.model_proc.process_behavior(
                                               nextobj.get_contents(),
                                               prev_instances,
                                               treelevel + 1,
                                               objlist,
                                               callerobj=obj)
            if __debug__: 
                self.logger.fine("Returned list from behavior processing : %s" % \
                             (ret_instances))
        elif(nextobj.is_type_recursion()):
            ret_instances = self.model_proc.process_recursion(                                
                                               nextobj,
                                               prev_instances,
                                               treelevel + 1,
                                               callerobj=obj)
            if __debug__: 
                self.logger.fine("Returned list from behavior processing : %s" % \
                             (ret_instances))
        else:
            # Process the next object
            if(nextobj.is_state_node()):
                ret_instances = self.state_proc.process_state(nextobj,
                                                    prev_instances,
                                                    treelevel + 1,
                                                    callerobj=obj)
                if __debug__: 
                    self.logger.fine("Returned IDs : %s" % (ret_instances))
            else:
                raise Exception("UNEXPECTED object %s of type %s after %s" %\
                                 (nextobj.get_name(), nextobj.get_type(), obj.get_name()))
        
        # Add the instances to the nextobject
        nextobj.add_instances(ret_instances)

        
        #---------------------------------------------------- 
        # Apply leadsto semantics to the returned instances
        # along with the optional operator constraints
        #----------------------------------------------------- 
        constraints = obj.get_constraints()
        if __debug__: 
            self.logger.info("Operator Constraints :%s" % (constraints))
        
        deltatime = None
        cop = None 
        if(constraints):
            ctuple = constraints.get_constraint()
            (cname, cop, cval, cqual) = ctuple
            deltatime = Time()
            deltatime.set_time_from_str(cval,cqual)
            self.logger.info("Time delta :%s" % (deltatime))
        
  
        leadsto_instances = self.apply_leadsto_semantics(obj,
                                                         prevobj,
                                                         nextobj,
                                                         deltatime, cop)
        obj.add_instances(leadsto_instances)
        
        if __debug__:
               self.logger.debug("Instance List after applying leadstoop:%s" %\
                               (leadsto_instances))

        if __debug__: 
                self.logger.behavior(treelevel, "<-- %s (OUT: %s  Type: %s)" % \
                    (obj.get_name(),
                     len(leadsto_instances),
                     type(leadsto_instances)))
        
        return leadsto_instances
    
    
    def apply_leadsto_semantics(self, obj, prevobj, nextobj, 
                                        deltatime=None, cop=None):
        """
            Checks leadsto operator semantics on the input instances
            and returns a list of satisfying ones 
        """

        newinstlist = BehaviorInstanceList()

        phi2_instances = nextobj.get_instances()
        phi1_instances = prevobj.get_instances()

        phi1_dependent = False
        phi2_dependent = False 
        
        if __debug__:
            self.logger.info("Leadsto Input:\nphi1_instances = %s\n\nphi2_instances = %s" %\
                              (phi1_instances, phi2_instances))            
        
        # If the dependee pointer is set for the instances 
        # it means that the instances are for a dependent state.
        try:
            phi2_1 = phi2_instances[0]
            if(phi2_1.get_dependee()):
                phi2_dependent = True
        except IndexError as e:
            if __debug__:
                 self.logger.info("Empty phi2 given to leadstop")       
            return newinstlist
        
        try:
            phi1_1 = phi1_instances[0]
            if(phi1_1.get_dependee()):
                phi1_dependent = True
        except IndexError as e:
            if __debug__:
                 self.logger.info("Empty phi2 given to leadstop")       
            return newinstlist
        
        #-------------------------------------------------------------
        # Cases:
        #    phi1 = independent phi2 = dependent
        #    phi1 = dependent   phi2 = dependent
        #    phi1 = independent phi2 = independent
        #    phi1 = dependent   phi2 = independent
        #-------------------------------------------------------------
        
        if(phi2_dependent == True):         
            #    phi1 = independent phi2 = dependent
            #    phi1 = dependent   phi2 = dependent
            if __debug__: 
                self.logger.info("Leadstoop case: Phi2 dependent")
      
            for phi2 in phi2_instances:
                phi1 = phi2.get_dependee()

                if __debug__:
                    self.logger.info("Processing phi1 = %s <--> phi2 = %s" %\
                              (phi1, phi2))
                      
                if(phi1 == phi2):
                    continue
                
                t1_start = phi1.get_starttime()
                atleast_count = phi1.get_atleast_count()
                if(atleast_count):
                    t1_end = phi1.get_endtime(index=atleast_count)
                else:
                    t1_end = phi1.get_endtime()
                
                t2_start = phi2.get_starttime()
                atleast_count = phi2.get_atleast_count()
                if(atleast_count):
                    t2_end = phi2.get_endtime(index=atleast_count)
                else:
                    t2_end = phi2.get_endtime()
                     
                
                if(self.check_semantics(t1_start, t1_end, t2_start, t2_end, 
                                     deltatime, cop)):
                    phi2.add(phi1)
                    phi2.set_behavior(nextobj.get_parent())
                    #phi2.set_behavior(nextobj.get_rootbehavior())
                    phi2.set_dependee(None)
                    newinstlist.insert(phi2)
                    
        elif((phi1_dependent == False) and 
             (phi2_dependent == False)):
            #    phi1 = independent phi2 = independent
            if __debug__: 
                self.logger.info("Leadstoop case: Phi1 and phi2 are independent")
            
            index = 0            
            for phi1 in phi1_instances:
                for phi2 in phi2_instances[index:]:
                    if __debug__:
                        self.logger.debug("Processing phi1 = %s <--> phi2 = %s" %\
                              (phi1, phi2))  
                    if(phi1 == phi2):
                        index += 1
                        continue
                    
                    t1_start = phi1.get_starttime()
                    atleast_count = phi1.get_atleast_count()
                    if(atleast_count):
                        t1_end = phi1.get_endtime(index=atleast_count)
                    else:
                        t1_end = phi1.get_endtime()
                    
                    t2_start = phi2.get_starttime()
                    atleast_count = phi2.get_atleast_count()
                    if(atleast_count):
                        t2_end = phi2.get_endtime(index=atleast_count)
                    else:
                        t2_end = phi2.get_endtime()    
                    
                    if(self.check_semantics(t1_start, t1_end, t2_start, t2_end, 
                                     deltatime, cop)):
                        if(isinstance(phi2,Event)):
                            neweg = EventGroup(bobject=nextobj.get_parent())
                            #neweg = EventGroup(bobject=nextobj.get_rootbehavior())
                            neweg.add(phi1)
                            neweg.add(phi2)
                            newinstlist.insert(neweg)
                        else:
                            phi2.add(phi1)
                            newinstlist.insert(phi2)
                        index += 1
                        break
        elif((phi1_dependent == True) and 
             (phi2_dependent == True)):
            raise Exception("UNHANDLED case for leadsto semantics!")
        
        return newinstlist 
    
    
    def check_semantics(self, t1_start, t1_end, t2_start, t2_end, 
                                     deltatime, cop):
        
        #-------------------------------------------------
        # Default leadsto semantics
        #
        # Behavior is valid if t2_start >= t1_end 
        #-------------------------------------------------
        relop = ">="
        eval_expr = "%s %s %s" % (t2_start, relop, t1_end)

        #------------------------------------------------------
        # leadsto semantics with operator constraints specified 
        # 
        # Behavior is valid if t2_start <op> (t1_end + <delta>)
        #------------------------------------------------------
        if(deltatime and cop):
            relop = cop
            if(relop == "="):
                relop = "=="
            eval_expr = "%s %s %s" % (t2_start, relop, (t1_end + deltatime))
        
        if __debug__: 
            self.logger.info("Eval expression for constraints %s" % \
                (eval_expr))

        if eval(eval_expr):
            if __debug__:
                self.logger.info("Eval expression %s satisfied" % (eval_expr))
            return True
        else:
            return False
