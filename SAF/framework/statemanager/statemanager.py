# statemanager.py - Abstraction for managing state tables
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
import framework.processor.resolver as resolver 
from framework.objects.behaviorinstancelist import BehaviorInstanceList
from framework.statemanager.statedb import StateDatabase
from framework.objects.eventgroup import EventGroup

class StateManager(StateDatabase):
    """
        Provides an abstraction for managing internal state.
    """
       
    def __init__(self, logger, inmem, tempdir, symtable):
        StateDatabase.__init__(self,tempdir, logger, inmem)
        self.logger  = logger
        self.globalsyms = symtable
        self.inmem = inmem
        self.tempdir = tempdir
        self.tablelist = []

    def get_tablelist(self):
        return self.tablelist
    
    def initialize_state(self, behavior):
        """
            Creates a new table in the state database
        """
        tablename = "state_" + behavior.get_parent() + "_" + behavior.get_name()
        self.create_table(tablename)
        self.set_active_table(tablename)
        self.tablelist.append(tablename)

        if __debug__: 
            self.logger.info("State table created in state database:" + tablename)
        self.reset_internal_state()      
    
    def add_instances_to_statetable(self, instances, obj, expr=None):            
        self.begin_transaction()
        options = {'col1': obj.get_name(),
                   'col2': expr or "",
                   'col7': expr or ""}
        self.add_new_records(instances, options)
        self.commit_transaction()
        if __debug__: self.print_state(obj.get_name(),instances) 
        
    
    def get_output_count(self, state, tablename=None):
        """    
            Returns output count of specified tablename or the 
            total count of all tables from the tablelist
        """
        count = 0
        if (tablename):
            sqlcmd = """select count(*) from %s where currstatename LIKE '%s%%'""" %\
                        (tablename, state)
            (val, status) = self.execute_sql(sqlcmd)
            count = val[0]            
        else:
            count = 0
            for t in self.tablelist:
                sqlcmd = """select count(*) from %s where currstatename LIKE '%s%%'""" %\
                        (t, state)
                (val, status) = self.execute_sql(sqlcmd)
                count += val[0]
        return  count
    
    
    def update_statetable_instances(self, obj, instances):
        self.begin_transaction()
        for bi in instances:
            self.update_state(bi, obj)               
        self.commit_transaction()
        self.flush_cache()
        if __debug__: self.print_state(obj.get_name(), instances)
    
    def cache_state_instances(self, instances):
        self.prefetch_records(instances)
   
    def append_modelname_to_instances(self, instances, modelname):
        
        ret_instances = BehaviorInstanceList()        
        self.begin_transaction()
        for r in instances:
            idlist = r.get_ids()
            for recordid in idlist:
                currsrec = self.get_record(recordid)
                if(currsrec):
                    prevout = currsrec.get_output()
                    self.add_to_output(">>", prevout)
                    options = { 'col3': ' ',
                                'col4':  modelname,
                                'col6':  prevout
                              }
                    self.update_record(recordid, options)
                    ret_instances.insert(r)
        self.commit_transaction()
        self.flush_cache()
        if __debug__:  
            self.print_state(modelname, ret_instances)
        return ret_instances
    
    
    def update_state(self, binst,  obj):
        
        recordid = binst.get_id()
        etype    = binst.get_type()
        
        fullobjname = obj.get_fullname()
        currsrec = self.get_record(recordid)
        if(currsrec == None):
            return

        if (isinstance(binst,EventGroup)):
            if __debug__:
                self.logger.debug("Instance is an eventgroup! Fetching only one event %s instance for updation!" %(recordid))
            inst = binst.get_contents()[-1]
        else:
            inst = binst
        # Bind values to state declaration
        kvhash = resolver.resolve_state(self.logger,
                                        inst,
                                        currsrec,
                                        obj,
                                        self.globalsyms,
                                        obj)
        if(kvhash is None):
            return

        oldhistory = currsrec.get_history()
        kvhashcopy = dict(kvhash)
        history = self.append_ctxt(fullobjname,
                                    kvhashcopy,
                                    oldhistory)
        options = { 'col1': obj.get_name(),
                    'col2': kvhash,
                    'col7': history}
        self.update_record(recordid, options)

    
    def append_ctxt(self, fullobjname, kvhash, oldhistory):
        if type(kvhash) is dict:
            for k, v in kvhash.items():
                newk = fullobjname + "." + k
                del kvhash[k]
                kvhash[newk] = v

            if(oldhistory is not None):
                for k, v in oldhistory.items():
                    kvhash[k] = v
        else:
            raise AbortCondition("UNEXPECTED: Expected a type dict but got %s" % \
                              (type(kvhash)))
        return kvhash
