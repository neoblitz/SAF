# process_intervalops.py - Functions for processing interval temporal
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
from framework.objects.eventgroup import EventGroup

class ITLOpsProcessor:
    """
        Processor for interval temporal operators 
    """

    def __init__(self, logger, datahandle, statehandle, stateproc, modelproc):
        self.sh = statehandle
        self.dh = datahandle
        self.logger = logger
        self.state_proc = stateproc
        self.model_proc = modelproc

    def apply_concurrent_semantics(self, obj, prevobj, nextobj, deltatime, cop):
        """ Processes the olap operator and operator constraints """

        phi1_instances = prevobj.get_instances()
        phi2_instances = nextobj.get_instances()

        if __debug__:
            self.logger.debug(\
            "Processing olap over phi1_instance (%s) and phi2_instances (%s)" % \
             (phi1_instances, phi2_instances))

        # Input instances have to be of type EventGroup.
        if phi1_instances and phi2_instances:
            first1 = phi1_instances[0]
            first2 = phi2_instances[0]
            if((not isinstance(first1, EventGroup)) or
               (not isinstance(first2, EventGroup))):
                raise \
                Exception("Concurrent operator semantics requires group of events!")

        # Create a new return instance list
        newinstlist = BehaviorInstanceList([], bobject=obj)

        for phi1 in phi1_instances:
            for phi2 in phi2_instances:
                if __debug__:
                    self.logger.debug("phi1 (%s)\nphi2 (%s) " % (phi1, phi2))

                if (phi1 == phi2):
                    continue

                phi1_start = phi1.get_starttime()
                phi1_end = phi1.get_endtime()
                phi2_start = phi2.get_starttime()
                phi2_end = phi2.get_endtime()

                satisfied = False
                if(obj.is_olap_op()):
                    satisfied = \
                    self.process_olap_op(phi1_start, phi1_end, phi2_start,
                                            phi2_end, deltatime, cop)
                elif(obj.is_ew_op()):
                    satisfied = \
                     self.process_ew_op(phi1_start, phi1_end, phi2_start,
                                            phi2_end, deltatime, cop)
                elif(obj.is_sw_op()):
                    satisfied = \
                     self.process_sw_op(phi1_start, phi1_end, phi2_start,
                                            phi2_end, deltatime, cop)
                elif(obj.is_dur_op()):
                    satisfied = \
                     self.process_dur_op(phi1_start, phi1_end, phi2_start,
                                            phi2_end, deltatime, cop)
                elif(obj.is_eq_op()):
                    satisfied = \
                     self.process_eq_op(phi1_start, phi1_end, phi2_start,
                                            phi2_end, deltatime, cop)
                else:
                    raise SyntaxError("Unrecognized logical operator - %s" % \
                                       (obj.get_name()))

                if(satisfied):
                    egrp = EventGroup(bobject=obj)
                    egrp.add(phi1)
                    egrp.add(phi2)
                    newinstlist.insert(egrp)
        return newinstlist


    def process_olap_op(self, phi1_start, phi1_end, phi2_start, phi2_end, 
                                                        deltatime, cop):
        """ 
            Processes the olap operator and operator constraints
            
            Default olap semantics
                phi2_start < phi1_start < phi2_end
                phi1_end > phi2_end
                
            OLAP semantics with operator constraints specified 
                (phi2_end - phi1_start) <relop> deltatime
        """
        
        satisfied = False

        if ((phi2_start < phi1_start < phi2_end) and
             (phi1_end > phi2_end)):
            # Need to still satisfy the operator constraints if any
            satisfied = True
        else:
            return False

        if(deltatime and cop):
            if(cop == "="): cop = "=="
            eval_expr = "%s %s %s" % (phi2_end,
                                      cop,
                                      (phi1_start + deltatime))
            
            satisfied = True if eval(eval_expr) else False
                                
            if __debug__:
                satstr = "not" if not satisfied else "" 
                self.logger.info(\
                    "Eval expression %s satisfied %s by %s <-> %s" % \
                    (eval_expr, satstr, phi1, phi2))
        
        return satisfied


    def process_sw_op(self, phi1_start, phi1_end, phi2_start, phi2_end, 
                                                        deltatime, cop):
        """ 
            Processes the sw operator and operator constraints
            
            Default sw semantics
                phi2_start == phi1_start
                
            sw semantics with operator constraints specified 
                phi1_start  <relop> (phi2_start + deltatime)
        """
               
        satisfied = False
        if(deltatime and cop):
            if(cop == "="): cop = "=="
            eval_expr = "%s %s %s" % (phi1_start,
                                      cop,
                                      (phi2_start + deltatime))
            satisfied = True if eval(eval_expr) else False    
            
            if __debug__:
                satstr = "not" if not satisfied else "" 
                self.logger.info(\
                    "Eval expression %s satisfied %s by %s <-> %s" % \
                    (eval_expr, satstr, phi1, phi2))
        else:
            if ((phi2_start == phi1_start)):
               satisfied = True

        return satisfied


    def process_ew_op(self, phi1_start, phi1_end, phi2_start, phi2_end, 
                                                        deltatime, cop):
        """ 
            Processes the ew operator and operator constraints
            
            Default ew semantics
                phi2_end == phi1_end
                
            ew semantics with operator constraints specified 
                phi1_end  <relop> (phi2_end + deltatime)
        """        
        satisfied = False
        if(deltatime and cop):
            if(cop == "="): cop = "=="
            eval_expr = "%s %s %s" % (phi1_end,
                                      cop,
                                      (phi2_end + deltatime))
            satisfied = True if eval(eval_expr) else False    
            
            if __debug__:
                satstr = "not" if not satisfied else "" 
                self.logger.info(\
                    "Eval expression %s satisfied %s by %s <-> %s" % \
                    (eval_expr, satstr, phi1, phi2))
        else:
            if ((phi2_end== phi1_end)):
               satisfied = True

        return satisfied


    def process_eq_op(self, phi1_start, phi1_end, phi2_start, phi2_end, 
                      deltatime, cop):
        """ 
            Processes the eq operator and operator constraints
            
            Default eq semantics
                phi1_duration == phi2_duration
                
            dur semantics with operator constraints specified 
                phi1_duration == phi2_duration
        """        

        phi1_duration = (phi1_end - phi1_start)
        phi2_duration = (phi2_end - phi2_start)
        satisfied = False
        if(deltatime and cop):
            if(cop == "="): cop = "=="
            
            eval_expr = "(%s %s %s) and (%s %s %s)" % \
                (phi1_duration, cop, deltatime,
                 phi2_duration, cop, deltatime)
             
            satisfied = True if eval(eval_expr) else False   

            if __debug__:
                satstr = "not" if not satisfied else "" 
                self.logger.info(\
                    "Eval expression %s satisfied %s by %s <-> %s" % \
                    (eval_expr, satstr, phi1, phi2))
        else:
            if ((phi2_duration == phi1_duration)):
               satisfied = True
        
        return satisfied


    def process_dur_op(self, phi1_start, phi1_end, phi2_start, phi2_end, 
                                                        deltatime, cop):
        """ 
            Processes the dur operator and operator constraints
            
            Default dur semantics
                phi1_duration == phi2_duration
                
            dur semantics with operator constraints specified 
                phi1_end  <relop> (phi2_end + deltatime)
        """
        satisfied = False
        if(deltatime and cop):
            if(cop == "="): cop = "=="

            eval_expr = "(%s %s %s) and (%s %s %s)" % \
                (phi1_duration, cop, deltatime,
                 phi2_duration, cop, deltatime)
             
            satisfied = True if eval(eval_expr) else False   

            if __debug__:
                satstr = "not" if not satisfied else "" 
                self.logger.info(\
                    "Eval expression %s satisfied %s by %s <-> %s" % \
                    (eval_expr, satstr, phi1, phi2))
        else:
            #-------------------------------------------------
            # Default eq semantics
            #
            # phi1_start > phi2_start and phi1_end < phi2_end
            #-------------------------------------------------
            if ((phi1_start > phi2_start) and (phi1_end < phi2_end)):
               satisfied = True
               
        return satisfied


    def process_concurrent_ops(self, obj, prevobj, nextobj, in_binstances,
                               treelevel):

        if __debug__:
            self.logger.behavior(treelevel, "--> %s (IN: %s Type: %s)" % \
                     (obj.get_name(), len(in_binstances), type(in_binstances)))
            self.logger.fine("Record IDs  : " + str(in_binstances))

        self.sh.flush_cache()

        # Create an empty return list
        ret_instances = BehaviorInstanceList()
        if(nextobj.is_behavior_object()):
            ret_instances = self.model_proc.process_behavior(
                                               nextobj.get_contents(),
                                               in_binstances,
                                               treelevel + 1,
                                               objlist=None,
                                               callerobj=obj)
            if __debug__:
                self.logger.fine("Returned list from behavior processing : %s" % \
                             (ret_instances))
        else:
            # Process the next object
            if(nextobj.is_state_node()):
                ret_instances = self.state_proc.process_state(nextobj,
                                                    in_binstances,
                                                    treelevel + 1,
                                                    callerobj=obj)
                if __debug__:
                    self.logger.fine("Returned IDs : %s" % (ret_instances))
            else:
                raise Exception("UNEXPECTED object %s of type %s after \
                 %s" % (nextobj.get_name(), nextobj.get_type(), obj.get_name()))

        # Add the instances to the nextobject
        nextobj.add_instances(ret_instances)

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

