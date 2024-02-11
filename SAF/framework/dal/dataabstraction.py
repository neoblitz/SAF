# abstraction.py - Provides a behavior abstraction over events 
#                    for the model processing algorithm
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
from framework.objects.event import Event
from framework.objects.eventgroup import EventGroup
from framework.statemanager.statedb import StateDatabase
from copy import deepcopy

class DataManager:
    """
        Provides a behavior abstraction for the model processing algorithm.
    """
       
    def __init__(self, logger, eventdb, symtable):
        self.logger  = logger
        self.eventdb = eventdb
        self.globalsyms = symtable        
        self.tablenamehash = {}
        self.query_cache = {}
   
    def reset_query_cache(self):
        self.query_cache.clear()

    def get_binstances_satisfying_state(self, stateobj, kvhash, 
                                        instances=None, 
                                        fullobjname=None,
                                        mainns=None):
        """
            Returns a BehaviorInstanceList of instances matching the 
            input state proposition
        """
        
        # Always better to operate on a copy of the hash since 
        # the kvhash (expression hash) is linked in the the global
        # symbol table
        newkvhash = kvhash.copy()
        statename = stateobj.get_name()        
        
        
        # It is possible that top-level models would have 
        # defined specific values for attributes of lower-level models
        # These values are stored indexed by the appropriate attributes 
        # albeit under the main namespace being  
        # processed. 
        # Update values of variables if required
        if mainns:
            rootbname = stateobj.get_alias() or "" 
            for k,v in newkvhash.items():
                fullname = [] 
                fullname.append(mainns)
                fullname.append(rootbname)
                fullname.append(k)
                fn = ".".join(fullname)
                if(self.globalsyms.has_symbol(fn)):
                    newv = self.globalsyms.get_symbol(None, None, 
                                               fullname=fn)  
                    vtype = self.globalsyms.symtype(newv)
                    if((vtype == self.globalsyms.get_code_const()) or
                        (vtype == self.globalsyms.get_code_any())):
                        newkvhash[k] = newv
            if rootbname: 
                fullobjname = mainns + "." + rootbname
            #print fullobjname

        if __debug__: 
            self.logger.info("Modified hash according to context: %s" % \
                                (newkvhash))
        query = sqlutils.attrhash_to_sql(newkvhash, 
                                         statename, 
                                         self.globalsyms,
                                         fullobjname)
        if __debug__: 
            self.logger.info("Converted state hash %s to query %s" % \
                                (newkvhash, query))
        
        ret_instances = None
        if(instances):
            # Having "eventno IN (*)" at the beginning of the query
            # ensures efficient usage of the INDEX. 
            # Read  http://www.sqlite.org/optoverview.html (Index usage 
            # examples) to understand the rationale
            query = "eventno IN (%s) and %s" % (instances,query)
        
        #Retrieve instances matching this query from the cache 
        if(query in self.query_cache):
            ret_instances = self.query_cache[query]
            egroup = ret_instances.get_contents()
            newegroup = EventGroup(bobject=stateobj)
            
            # FIXME: THis is highly inefficient. This is being done just
            # to set the correct behavior object on cached instances.
            # See if it is possible to remove the behavior pointer from 
            # Event and shift it elsewhere.
            for r in egroup:
                if(isinstance(r,Event)):
                    newr = Event(r.get_id(), avhash=r.get_avhash())
                    newr.set_behavior(stateobj)
                    newegroup.add(newr)
                else:
                    raise Exception("UNEXPECTED type of instance encountered while fetching events from cache!")

            ret_instances = newegroup
            if __debug__: 
                self.logger.fine("Query found in cache: Number instances: %d Query: %s" % \
                          (len(ret_instances), query))
        else:
            ret_instances = self.get_binstances_matching_query(query, stateobj)
            # Cache the returned instances overwriting the existing contents
            self.query_cache[query] = ret_instances
            
        if __debug__: 
            self.logger.debug("Instances matching state (from eventdb): "\
                                + query + " \n " + str(ret_instances))    
        return ret_instances
    
    def get_binstances_matching_query(self, query, stateobj):
        return self.eventdb.get_events(query, stateobj)
    
    def get_event(self, id):
        return self.eventdb.get_event(id)
         