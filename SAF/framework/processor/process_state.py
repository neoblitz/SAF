# proces_state.py - Applies the model to data
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
from copy import deepcopy
import framework.processor.resolver as resolver
import framework.common.sqlutils as sqlutils
import framework.common.utils as utils
from framework.objects.behaviorinstancelist import BehaviorInstanceList
from framework.processor.process_behaviorconstraints import BehaviorConstraintProcessor
from framework.common.errordefs import SymbolTableError, StateRecordError
from framework.objects.eventgroup import EventGroup

class StateProcessor:

    """
        Provides a behavior abstraction for the model processing algorithm.
    """
       
    def __init__(self, logger, datahandle, statehandle, symt, model_proc):
        self.logger      = logger
        self.dh          = datahandle
        self.sh          = statehandle
        self.globalsyms  = symt
        self.model_proc  = model_proc
        self.qualifying_instances = BehaviorInstanceList()
        
        self.behavior_cons_proc = BehaviorConstraintProcessor(self.logger,
                                                        self.dh,
                                                        self.sh,
                                                        self,
                                                        self.model_proc)
     
    def set_qualifying_instances(self, qual_inst):
        self.qualifying_instances = \
                ",".join([str(r.get_id()) for r in qual_inst])

    def process_state(self, stateobj, in_binstances, treelevel, callerobj=None):
        """
            Processes atomic state propositions (a.k.a states) where each state
            is a collection of attribute value pairs.
            
            States could be of two types
            1. Independent 
               All attributes in the state have non-dependent or constant 
               value.
            2. Dependent
               Atleast one attribute in the state depends on value of some other
               state 
        """

        fullobjname = stateobj.get_fullname()    
        if __debug__: 
            self.logger.info(stateobj.details())
            self.logger.debug("Processing state object : %s=%s" % \
                            (fullobjname, stateobj))
        if(self.globalsyms.is_state_dependent(fullobjname)):
            # Dependent-valued state
            #-------------------
            if __debug__: 
                self.logger.info("State " + fullobjname + " is DEPENDENT ")
            ret_instances =\
                self.process_dependent_state(stateobj, in_binstances, callerobj)
            
            if __debug__: 
                self.logger.info("Dependent State matched %d instances" %\
                                     (len(ret_instances)))
        else:
            # Independent or constant-valued state
            #---------------------------------------
            if __debug__: 
                self.logger.info("State " + fullobjname + " is INDEPENDENT ")
            
            ret_instances =\
                self.process_independent_state(stateobj,in_binstances)
            
            if ret_instances:          
                # Cache corresponding state records in memory 
                #self.sh.cache_state_instances(ret_instances)

                # Update existing state table instances 
                self.sh.update_statetable_instances(stateobj, ret_instances)
                
            
            if __debug__: 
                self.logger.info("Independent State matched %d instances" %\
                                     (len(ret_instances)))
        
        if(self.globalsyms.is_state_negated(fullobjname)):
            if(ret_instances):
                insts_to_remove = ret_instances.get_ids()
                neg_instances = BehaviorInstanceList() 
                neg_instances.set_behavior(stateobj)
                for inst in in_binstances:
                    ids = inst.get_ids()
                    for id in ids:
                        if(id not in insts_to_remove):
                            neg_instances.insert(inst)
                ret_instances = neg_instances
                    
        
        if __debug__: 
            self.logger.behavior(treelevel,
                             "%s (IN: %s Type: %s OUT: %s Type: %s)" % \
                              (stateobj.get_name(),
                               len(in_binstances),
                               type(in_binstances),
                               len(ret_instances),
                               type(ret_instances)))
        
        # Print minimal information
        if((not stateobj.is_name_anon())):
            utils.lprint(2, "State %s .. found %d instances" %\
                         (stateobj.get_name(), len(ret_instances)))
        return ret_instances
    

    def process_independent_state(self, stateobj, binstances):
        
        statename   = stateobj.get_name()
        statens     = stateobj.get_namespace()
        ret_binstances = None
        state_expr = self.globalsyms.get_symbol(statens,
                                                statename,
                                                None)

        if (state_expr ):
            if __debug__: 
                self.logger.info("Getting instances matching state expression %s"%\
                             (state_expr))
            mainns = self.model_proc.model.get_tree().get_namespace()
            ret_binstances = \
            self.dh.get_binstances_satisfying_state(stateobj,
                                                    state_expr,
                                                    instances=self.qualifying_instances,
                                                    fullobjname=stateobj.get_fullname(),
                                                    mainns=mainns)
            ret_binstances.set_behavior(stateobj)
        else:
            raise SymbolTableError("Symbol %s.%s not found" % \
                                   (statens, statename))

        if __debug__: 
            self.logger.fine("Instances satisfying INDEPENDENT state %s:\n%s" % \
                           (stateobj, ret_binstances))
        if(not ret_binstances):
            self.sh.flush_cache()
            if __debug__: 
                self.logger.state("No records for state %s\n" % (stateobj))
            return BehaviorInstanceList([], bobject=stateobj)
        else:
            fullobjname = stateobj.get_fullname()
            constraintobj = self.globalsyms.get_state_constraint(fullobjname)
            inst_list = BehaviorInstanceList(bobject=stateobj)
            inst_list.insert(ret_binstances)            
            if (constraintobj.has_constraint()):
                constrained_list =\
                     self.behavior_cons_proc.apply_behavior_constraints(stateobj,
                                                                     constraintobj,
                                                                     inst_list)
                constrained_list.set_behavior(stateobj)
                return constrained_list
            else:
                return BehaviorInstanceList(ret_binstances.get_contents(), 
                                            bobject=stateobj)

    
    def process_dependent_state(self, stateobj, binstances, callerobj):
        
        statename   = stateobj.get_name()
        statens     = stateobj.get_namespace()

        # Create a deque from the recordids. The advantage of deque over 
        # a list is that a deque provides O(1) performance for pop. This 
        # makes a notable difference when processing 1000's of ids.
        # SREC = deque(recordids)
        SREC = binstances
        if(not SREC):
            self.sh.flush_cache()
            if __debug__: 
                self.logger.state("No records for state %s\n" % (stateobj.get_name()))
                self.logger.fine("No records for state %s\n" % (stateobj.get_name()))
            return BehaviorInstanceList([], bobject=stateobj)

        SREC_deleted_hash = {}
        #self.sh.cache_state_instances(binstances)
        return_list = BehaviorInstanceList()

        fullobjname = stateobj.get_fullname()
        constraintobj = self.globalsyms.get_state_constraint(fullobjname)
        if __debug__: 
            self.logger.debug("Dependent state %s has constraints %s" % \
                          (fullobjname,
                           constraintobj))
                                           
        self.sh.begin_transaction()
        if __debug__: 
            self.logger.debug("Dependent State: length(SREC) : %d" % (len(SREC)))
       
        caller = callerobj or stateobj
        numinstances = len(SREC)    
        recindex = 0
        while recindex < numinstances:   
            # Read an instance
            r = SREC[recindex]
            recindex += 1

            recordid = r.get_id()
            rectype  = r.get_type()
           
            if __debug__: 
                self.logger.info("\n\nProcessing %s, %s" %(recordid, rectype))

            # Skip the instance if its marked deleted. 
            if(recordid in SREC_deleted_hash):
                if __debug__:
                    self.logger.info("Record %s deleted in local hash!" % (recordid))  
                continue
            
            currsrec = self.sh.get_record(recordid)
            if(currsrec ==  None):
                if __debug__:
                    self.logger.fine("Record %s deleted in state database!" %\
                                  (recordid))  
                continue

            # Bind the state definition with values from actual event with
            # id recordid
            # currsrec is corresponding state record
            mainns = self.model_proc.model.get_tree().get_namespace()
            kvhash = resolver.resolve_state(self.logger,
                                            r,
                                            currsrec, 
                                            stateobj, 
                                            self.globalsyms, 
                                            caller,
                                            mainns=mainns)
            if not kvhash: continue
            if __debug__:
                self.logger.info("Resolved state: %s" % (kvhash))
            
            ret_list = self.dh.get_binstances_satisfying_state(
                                        stateobj, 
                                        kvhash,
                                        instances=self.qualifying_instances,
                                        fullobjname=stateobj.get_fullname())    
                                        #mainns=mainns)
            
            # Remove already processed records
            ret_group = EventGroup()
            for c in ret_list.get_contents():
                if(c.get_id() not in SREC_deleted_hash):
                    ret_group.add(c)
            
            if __debug__:
                self.logger.info("Valid return list: %s" % (ret_group))

            # If the dependent state processing happens as a result of 
            # leadstoop make sure the instances are later in time
            ret_instances = BehaviorInstanceList()
            if caller.is_leadsto_op():
                newlist = ret_group.get_contents()
                index = 0
                try:
                    gtr = None
                    gtr = newlist.find_gt(r.get_timerange())
                    index = newlist.index(gtr)
                except ValueError:
                    pass

                if len(newlist) > 0:
                    ret_group =  EventGroup(newlist[index:])               
                    if __debug__:
                        self.logger.info("Return list after adjusting for leadsto : %s" %\
                                      (ret_group))
            
            ret_instances.insert(ret_group)            
            constrained_group = None    
            if(len(ret_instances) > 0):
                constrained_group = EventGroup()                
                if(constraintobj.has_constraint()):
                    # Apply constraints to the returned behavior instances                    
                    constrained_list =\
                    self.behavior_cons_proc.apply_behavior_constraints(stateobj,
                                                                 constraintobj, 
                                                                 ret_instances)
                    if(constrained_list):
                        constrained_group = constrained_list[0]
                else:
                    inst = ret_instances[0].get_contents()
                    if(inst):
                        constrained_group.add(inst[0])

                constrained_group.set_behavior(stateobj)

                if(len(constrained_group) > 0):
                    if __debug__: 
                        self.logger.info(
                    "Returned List with constraints applied is of len: %d\n%s" % \
                              (len(constrained_group), constrained_group))

                    fullobjname = ".".join([stateobj.get_namespace(),
                                            stateobj.get_name()])

                    options = {'col1': stateobj.get_name(),
                               'col2': kvhash,
                               'col3': ' ',
                               'col4': ' ',
                               'col5': {},
                               'col6': ' ' , # Filled in the loop below
                               'col7': {}  }

                    self.do_removal_and_updates(constrained_group.get_contents(),
                                                r,
                                                SREC_deleted_hash,
                                                currsrec,
                                                options,
                                                caller,
                                                fullobjname)
                    
                    
                    # Associate the returned constrained list with the 
                    # current instance being processed
                    constrained_group.set_dependee(r)
                    return_list.insert(constrained_group)
                    if __debug__: 
                        self.logger.fine("Current Return List: %s" % \
                                       (return_list))
        SREC_deleted_hash.clear()
        self.sh.commit_transaction()
        self.sh.flush_cache()

        if __debug__: 
            self.sh.print_state(stateobj.get_name(), return_list)
        return return_list
    
    
    def do_removal_and_updates(self, evgroup,
                                     r,
                                     SREC_deleted_hash,
                                     currsrec,
                                     options,
                                     callerobj,
                                     fullobjname):
        # Remove the corresponding record from statedb since we have a match
        # Delete the eid from SREC  (Mark as deleted)  
        # This is to prevent a condition where the record just removed 
        # from the statedb might be one from the SREC list and 
        # might be processed later in the main for loop
            
        if(len(evgroup) >= 1):
            if __debug__: 
                self.logger.debug("Removing and updating events in list %s" %\
                                   (evgroup))
            for el in evgroup:
                e = el.get_id()
                self.sh.remove_record(e)
                SREC_deleted_hash[e] = 'DELETED'
            laste = evgroup[-1].get_id()
            #options['col0'] = e
            evhash = evgroup[-1].get_avhash()
        else:
            raise Exception("Number of instances in eventgroup is zero")

        oldhistory = currsrec.get_history()

        history = self.sh.append_ctxt(fullobjname,
                                   evhash.copy(),
                                   oldhistory)
        options['col7'] = history
        #self.sh.update_record(r.get_id(), options)
        self.sh.update_record(laste, options)

      