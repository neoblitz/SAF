# process_behaviorconstraints.py - Handles behavior constraints
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
# Author: Arun Viswanathan (aviswana@usc.edu)
#------------------------------------------------------------------------------

import framework.common.sqlutils as sqlutils
import framework.common.utils as utils
from framework.objects.eventgroup import EventGroup
from framework.objects.behaviorinstancelist import BehaviorInstanceList
from framework.objects.behaviorinstance import BehaviorInstance
from framework.objects.timeobject import Time
from framework.objects.behaviortree import BehaviorTreeObject
from framework.common.errordefs import SymbolTableError
from framework.common.errordefs import SyntaxError, AbortCondition
from framework.common.errordefs import ConstraintError,ModelProcessingError

class BehaviorConstraintProcessor:
    """
        Provides a behavior abstraction for the model processing algorithm.
    """
       
    def __init__(self, logger, datahandle, statehandle, stateproc, modelproc):
        self.sh      = statehandle
        self.dh      = datahandle
        self.logger  = logger
        self.state_proc = stateproc
        self.model_proc  = modelproc
            

    def apply_behavior_constraints(self, callerobj, constraints, instances):
        """
            Apply behavior constraints for each instance in the input list
            of instances and return a list of behavior instances satisfying the 
            constraint.
        """          
        if __debug__: 
            self.logger.info("Applying behavior constraints %s to behavior %s" % \
                                                     (constraints,
                                                      callerobj.get_name()))

        (cname, relop, cval, cqual) = constraints.get_constraint()
        if __debug__: 
            self.logger.debug("Constraint Fetched : %s %s %s %s " % \
                         (cname, relop, cval, cqual))
        newinstances = BehaviorInstanceList()
        self.sh.flush_cache()        

        if not instances:
            return newinstances

        if(len(instances[0]) <= 0):
            return newinstances

#        if(len(instances[0]) > 0):
#            self.sh.prefetch_records(instances)
#        else:
#            return newinstances
        
        if constraints.get_apply_flag() == True:
            try:
                if(cname == "bcount"):
                    newinstances = self.apply_bcount(instances, cval, relop, cqual)
                elif(cname == "_limit"):
                    newinstances = self.apply__limit(instances, cval, relop, cqual)
                elif(cname == "_eventno"):
                    newinstances = self.apply__eventno(instances, cval, relop, cqual)
                else:
                    raise Exception("Constraint '%s' not recognized!" % (cname))
            except SyntaxError, ConstraintError:
                raise ModelProcessingError
            except SymbolTableError:
                raise AbortCondition
            return newinstances

        try:
            if(cname == "bcount"):
                newinstances = self.check_bcount(instances, cval, relop, cqual)
            elif(cname == "icount"):
                newinstances = self.check_icount(instances, cval, relop, cqual)
            elif(cname == "at"):
                newinstances = self.check_at(instances, cval, relop, cqual)
            elif(cname == "end"):
                newinstances = self.check_end(instances, cval, relop, cqual)
            elif(cname == "duration"):
                newinstances = self.check_duration(instances, cval, relop, cqual)
            elif(cname == "rate"):
                newinstances = self.check_rate(instances, cval, relop, cqual)
            elif(cname == "_limit"):
                newinstances = self.apply__limit(instances, cval, relop, cqual)
            elif(cname == "_eventno"):
                newinstances = self.apply__eventno(instances, cval, relop, cqual)
            else:
                raise Exception("Constraint '%s' not recognized!" % (cname))
        except SyntaxError, ConstraintError:
            raise ModelProcessingError
        except SymbolTableError:
            raise AbortCondition

        return newinstances
    
    
    def build_constraint_expr(self, relop, expval, actualval):
        expr = ""
        if(isinstance(expval,tuple)):
            lower,upper = expval
            expr = "%s >= %s and %s <= %s" % (actualval, lower, actualval, upper)
            if(relop != "="):
                raise Exception(" Constraint expression cannot be related to a range via '%s'" %(relop))    
        else:
            if (relop == '='):
                relop = "=="
            expr = "%s %s %s" % (actualval, relop, expval)
        return expr


    def check_icount(self, instances, cval, relop, cqual):

        expr = self.build_constraint_expr(relop, cval, instances.get_icount())
        val = eval(expr)
        if __debug__: 
            self.logger.debug("Check Instance Count : %s %s" % (expr, val))
        
        if(val):
            return instances
        else:
            return BehaviorInstanceList([], bobject=instances.get_behavior())


    def _to_integer(self, cval):
        try: 
            cval = int(cval)
        except:                
            raise Exception("'_limit' keyword followed by invalid value %s" %(cval))
        
        if (cval < 0):
            raise Exception("'_limit' keyword followed by a negative value %s" %(cval))
        return cval


    def apply__limit(self, instances, cval, relop, cqual):
        if(relop != "="):
            raise Exception("'_limit' can be followed only by '=' ")
        cval = self._to_integer(cval)
        
        for r in instances:
            if(not isinstance(r,BehaviorInstance)):
                raise Exception("Invalid type of instance for _limit!")
            
            insts = r.get_contents()
            newinstlist = BehaviorInstanceList(insts[:cval])
            return newinstlist           
            
    def apply__eventno(self, instances, cval, relop, cqual):
            
        lower = None
        upper = None
        if(isinstance(cval,tuple)): 
            lower,upper = cval
            if(relop != "="):
                raise Exception("'_eventno' cannot be related to a range via '%s'" %(relop))    
        else:
            try:
                cval = int(cval)
            except:
                raise Exception("'_eventno' followed by invalid value '%s'" %(cval))            
            if(relop == "="):
                lower = cval
                upper = cval
            elif (relop == ">"):                
                lower = cval + 1
            elif (relop == ">="):                
                lower = cval
            elif (relop == "<="):                
                upper = cval
            elif (relop == "<"):                
                upper = (cval - 1) if ((cval - 1) >0) else 1 
            else:
                raise Exception("Unsupported operator %s for '_eventno' " %(relop))    
        
        for r in instances:
            if(not isinstance(r,BehaviorInstance)):
                raise Exception("Invalid type of instance for _eventno!")        
                        
            newinstlist = BehaviorInstanceList()
            insts = r.get_contents()
        
            lower = 0 if lower == None else lower
            upper = r.get_last_id() if upper == None else upper
            # Note that for eventgroups the get_id() always returns the 
            # last id of the last event in the group
            
            if __debug__:
                self.logger.info("Lower eventno : %s Upper eventno : %s " %\
                                 (lower,upper))
            for n in insts:
                id = n.get_id()
                if((id >= lower) and (id <= upper)):
                    newinstlist.insert(n) 
            return newinstlist

    def check_at(self, instances, cval, relop, cqual):
        newinstances = BehaviorInstanceList([], 
                                            bobject=instances.get_behavior())
        utils.lprint(2, "Checking constraint 'at' over %s instances" %(len(instances)))
        for r in instances:
            
            if(not isinstance(r,BehaviorInstance)):
                raise Exception("Invalid type of instance found while checking bcount!")
            rid = r.get_id()
            bcount = r.get_bcount() 
            insts = r.get_contents()
            dep_ptr = r.get_dependee()
            b_ptr = r.get_behavior()
         
            expr = self.build_constraint_expr(relop, cval, attime)
            val = eval(expr)
            if __debug__: 
                self.logger.info("Check attime : %s %s" % (expr, val))

            if(val):
                updatelist = insts                
                eg = EventGroup(updatelist)
                eg.set_behavior(b_ptr)
                eg.set_dependee(dep_ptr)
                newinstances.insert(eg)
                utils.lprint(3, "Found an instance with at = %0.2f [%s %s]" %\
                     (at, relop, cval))
                
        return newinstances
    
    
    def check_end(self, instances, cval, relop, cqual):
        newinstances = BehaviorInstanceList([], 
                                            bobject=instances.get_behavior())
        utils.lprint(2, "Checking constraint 'end' over %s instances" %(len(instances)))
        for r in instances:
            
            if(not isinstance(r,BehaviorInstance)):
                raise Exception("Invalid type of instance found while checking end!")
            rid = r.get_id()
            bcount = r.get_bcount() 
            insts = r.get_contents()
            dep_ptr = r.get_dependee()
            b_ptr = r.get_behavior()
            
            atleast_count = r.get_atleast_count()
            if(atleast_count):  
                endtime = float(r.get_endtime(index=atleast_count))
            else:
                endtime = float(r.get_endtime())
         
            expr = self.build_constraint_expr(relop, cval, endtime)
            val = eval(expr)
            if __debug__: 
                self.logger.info("Check endtime : %s %s" % (expr, val))
            if(val):
                updatelist = insts                
                eg = EventGroup(updatelist)
                eg.set_behavior(b_ptr)
                eg.set_dependee(dep_ptr)
                newinstances.insert(eg)
                utils.lprint(3, "Found an instance with end = %0.2f [%s %s]" %\
                     (endtime, relop, cval))

        
        return newinstances
    
    
    def check_duration(self, instances, cval, relop, cqual):
        newinstances = BehaviorInstanceList([], 
                                            bobject=instances.get_behavior())
        utils.lprint(2, "Checking constraint 'duration' for %s instances" %(len(instances)))
        for r in instances:
            
            if(not isinstance(r,BehaviorInstance)):
                raise Exception("Invalid type of instance found while checking duration!")
            rid = r.get_id()
            bcount = r.get_bcount() 
            insts = r.get_contents()
            dep_ptr = r.get_dependee()
            b_ptr = r.get_behavior()
           
            atleast_count = r.get_atleast_count()
            if(atleast_count):
                duration = float(r.get_endtime(atleast_count) - r.get_starttime())               
            else:
                duration = float(r.get_endtime() - r.get_starttime())
            
            expr = self.build_constraint_expr(relop, cval, duration)
            val = eval(expr)
            if __debug__: 
                self.logger.info("Check duration : %s %s" % (expr, val))

            if(val):
                updatelist = insts                
                eg = EventGroup(updatelist)
                eg.set_behavior(b_ptr)
                eg.set_dependee(dep_ptr)
                newinstances.insert(eg)
                utils.lprint(3, "Found an instance with duration = %0.2f [%s %s]" %\
                     (duration, relop, cval))
        return newinstances

 
    def check_rate(self, instances, cval, relop, cqual):
        newinstances = BehaviorInstanceList([], 
                                            bobject=instances.get_behavior())
        utils.lprint(2, "Checking constraint 'rate' for %s instances" %(len(instances)))
        for r in instances:
            
            if(not isinstance(r,BehaviorInstance)):
                raise Exception("Invalid type of instance found while checking bcount!")
            rid = r.get_id()
            bcount = r.get_bcount() 
            insts = r.get_contents()
            dep_ptr = r.get_dependee()
            b_ptr = r.get_behavior()
            
            atleast_count = r.get_atleast_count()
            if(atleast_count):
                dur = r.get_endtime(atleast_count) - r.get_starttime()
            else:
                dur = r.get_endtime() - r.get_starttime()          

            if __debug__: 
                self.logger.info("Computed duration : %s " % (dur))
            rate = 0.0
            if(dur > Time(0,0)):
                rate = float(bcount) / float(dur)

            if __debug__: 
                self.logger.info("rate : %s (%f/%f)" % (rate, float(bcount), float(dur)))            
            expr = self.build_constraint_expr(relop, cval, rate)
            val = eval(expr)
            if __debug__: 
                self.logger.info("Check rate : %s %s" % (expr, val))

            if(val):
                updatelist = insts                
                eg = EventGroup(updatelist)
                eg.set_behavior(b_ptr)
                eg.set_dependee(dep_ptr)
                newinstances.insert(eg)
                utils.lprint(3, "Found instance with rate = %s (%s instances / %s sec) (%s %s)" %\
                     (rate, bcount, dur, relop, cval))        

        return newinstances

    
    def check_bcount(self, instances, cval, relop, cqual):
        newinstances = BehaviorInstanceList([], bobject=instances.get_behavior())
        utils.lprint(2, "Checking constraint 'bcount' for %s instances" %(len(instances)))
                      
        for r in instances:            
            if(not isinstance(r,BehaviorInstance)):
                raise Exception("Invalid type of instance found while checking bcount!")
            rid = r.get_id()
            bcount = r.get_bcount() 
            insts = r.get_contents()
            dep_ptr = r.get_dependee()
            b_ptr = r.get_behavior()

            expr = self.build_constraint_expr(relop, cval, bcount)
            val = eval(expr)
            if __debug__: 
                self.logger.info("Check Event Count : %s %s" % (expr, val))

            if(val):
                updatelist = insts
                eg = EventGroup(updatelist)
                eg.set_behavior(b_ptr)
                eg.set_dependee(dep_ptr)
                if relop == ">=":
                    c = self._to_integer(cval)
                    eg.set_atleast_count(c)
                newinstances.insert(eg) 
                utils.lprint(3, "Found instance with bcount = %s (%s %s)" %\
                     (bcount, relop, cval))   
        
        return newinstances


    def apply_bcount(self, instances, cval, relop, cqual):
        newinstances = BehaviorInstanceList([], bobject=instances.get_behavior())  
                
        r = None
        if(len(instances) > 1):
            r = EventGroup()
            for inst in instances:
                r.add(inst)
            r.set_behavior(inst.get_behavior())
            #raise Exception("Unhandled / Unexpected condition occured! Please raise a bug!")
        else:
            r = instances[0]

        if(not isinstance(r,EventGroup)):
            raise Exception("Invalid instance type %s found while applying bcount!" %\
                            (r.__class__.__name__))

        # Get all the contents of the event group
        insts = r.get_contents()
        bcount = r.get_bcount()              
        dep_ptr = r.get_dependee()
        b_ptr = r.get_behavior()
        
        lower = None
        upper = None
        #-------------------------------------------------------------------
        # Case 0: bcount = lower:upper
        # Find satisfying events and group them into instances containing 
        # 'lower' number to 'upper' number of events.
        # Ex. Assuming there are 23 matches and lower:upper = 5:10,  
        #     there will be two instances with each instance containing 10, 10.
        #     Remaining 3 will be ignored since they are < 5. 
        #-------------------------------------------------------------------
        if(isinstance(cval,tuple)): 
            lower,upper = cval
            if(relop != "="):
                raise Exception("'bcount' cannot be related to a range via '%s'" %\
                                (relop))   
            if(bcount <= lower):
                return newinstances
            else:
                index = 0
                eg = EventGroup()
                eg.set_behavior(b_ptr)
                eg.set_dependee(dep_ptr)
                cval = upper
                temp_count = bcount
                for n in insts:
                    if(cval >= lower):
                        if index < (cval):
                            eg.add(n)
                            index += 1                                          
                        elif index == (cval):
                            newinstances.insert(eg)
                            index = 0
                            temp_count -= cval
                            if(temp_count >= upper):
                                cval = upper
                            elif(temp_count >= lower):
                                cval = temp_count
                            else:
                                cval = 0                            
                        if index == 0:
                            eg = EventGroup()
                            eg.set_behavior(b_ptr)
                            eg.set_dependee(dep_ptr)
                            eg.add(n)
                            index += 1
                if(index >= lower):
                    newinstances.insert(eg)                 
        else:
            try:
                cval = int(cval)
            except:
                raise Exception("'bcount' followed by invalid value '%s'" %(cval))
            #-------------------------------------------------------------------
            # Case 1: bcount = cval
            # ---------------------
            # Divide the events into eventgroups with bcount = cval.
            # Add all such bins that have bcount = cval to the newinstances list
            #-------------------------------------------------------------------
            if(relop == "="):
                if(bcount < cval):
                    return newinstances
                self._group_instances(insts, relop, cval, b_ptr, dep_ptr, newinstances)              
            #-------------------------------------------------------------------
            # Case 2: bcount > cval
            # ---------------------
            # Put all the instances into an eventgroup if bcount > cval
            #
            # Case 3: bcount >= cval
            # ---------------------
            # Put all the instances into an eventgroup if bcount >= cval
            #-------------------------------------------------------------------            
            elif (relop == ">" or relop == ">="):                
                if(bcount > cval):
                    eg = EventGroup(insts)
                    eg.set_behavior(b_ptr)
                    eg.set_dependee(dep_ptr)
                    if relop == ">=":
                        c = self._to_integer(cval)
                        eg.set_atleast_count(c)
                    newinstances.insert(eg)
                return newinstances             
            #-------------------------------------------------------------------
            # Case 4: bcount <= cval
            # ---------------------
            # Group events containing less than <= cval but a non-zero number of
            # events. An attempt will be made to place 10 events into each 
            # eventgroup and the last eventgroup will contain the remaining if 
            # any. 
            # Ex. If there are 20 matches, number of instances returned will be 
            #     2 with each instance containing 10, 10 
            #-------------------------------------------------------------------          
            elif (relop == "<="):
                if(bcount <= cval):
                    eg = EventGroup(insts)
                    eg.set_behavior(b_ptr)
                    eg.set_dependee(dep_ptr)
                    newinstances.insert(eg)
                elif (bcount > cval):
                    self._group_instances(insts, relop, cval,  b_ptr, dep_ptr, newinstances)
            #-------------------------------------------------------------------
            # Case 5: bcount < cval
            # ---------------------
            # Group events containing less than < cval but a non-zero number of 
            # events. An attempt will be made to place one less than cval events 
            # into each  eventgroup and the last eventgroup will contain the 
            # remaining events if any. 
            # Ex. If there are 20 matches, number of instances returned will be 
            #     3 with each instance containing 9, 9, 2 
            #-------------------------------------------------------------------
            elif (relop == "<"): 
                if(bcount < cval):
                    eg = EventGroup(insts)
                    eg.set_behavior(b_ptr)
                    eg.set_dependee(dep_ptr)
                    newinstances.insert(eg)
                elif (bcount > cval):
                    self._group_instances(insts, relop, cval - 1,  b_ptr, dep_ptr, newinstances)
            else:
                raise Exception("Unsupported operator %s for 'bcount' " %(relop)) 
                
        return newinstances

    def _group_instances(self, insts, relop, cval, b_ptr, dep_ptr, newinstances):        
        index = 0
        eg = EventGroup()
        eg.set_behavior(b_ptr)
        eg.set_dependee(dep_ptr)
        for n in insts:
            if index < (cval):
                eg.add(n)
                index += 1                                          
            elif index == (cval):
                newinstances.insert(eg)
                index = 0
            if index == 0:
                eg = EventGroup()
                eg.set_behavior(b_ptr)
                eg.set_dependee(dep_ptr)
                eg.add(n)
                index += 1
        if(relop == "="):
            # We add only if there are sufficient instances to add
            if (index == cval):
                newinstances.insert(eg)
        else:
            # For the < and <= operators
            if index != 0:
                # Add the remaining
                newinstances.insert(eg)
