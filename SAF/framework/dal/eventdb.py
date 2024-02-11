# eventdb.py - Class for managing event database
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
import os
from threading import Lock
from datetime import date
from datetime import datetime
from copy import deepcopy
import time

# Local Imports
import framework.common.log
from framework.objects.event import Event
from framework.common.errordefs import EventError
from framework.common.utils import unique
from framework.common.storage import SqliteStorage
from framework.objects.eventgroup import EventGroup
from framework.common.utils import h1, h2, h3


class EventDatabase(SqliteStorage):
    """
        Class for handling operations on an event database 
    """
    MAX_CACHE_SIZE = 100000
    PREFETCH_SIZE = 20000

    def __init__(self, dbtype, dbname, logger):
        self.dbtye = dbtype
        self.dbname = dbname
        self.numrecords = 0
        self.eventlist = []
        self.originlist = []
        self.eventmdata = {}
        self.logger = logger

        self.tablespresent = []
        self.datasize = 0;
        self.activetables = [];
        self.attributehash = {}
        self.recordcache = {}

        self.hitcount = 0
        self.misscount = 0
        
        if(dbtype == "sqlite3"):
            if __debug__: self.logger.info("Connecting to database " + dbname)
            SqliteStorage.__init__(self, self.dbname, self.logger, pragmas=True)
            self._init_caches_()

            self.numrecords = self.get_data_size()
            if __debug__: self.logger.info("Total number of records in database: %d" \
                              % (self.numrecords))

            self.eventlist = None
            self.eventlist = self.get_event_types()
            if __debug__: self.logger.info("Events found: %s" % (self.eventlist))

            self.originlist = self.get_origins()
            if __debug__: self.logger.info("Origins:" + str(self.originlist))

            for ev in self.eventlist:
                attrs = self.get_attribute_names(ev);
                for at in attrs:
                    sqlcmd_ind_1 = """create index  ind_%s_%s on %s(%s)"""
                    if __debug__: self.logger.info("Building index: " \
                                 + sqlcmd_ind_1 % (ev, at, ev, at))
                    (ret, status) = \
                            self.execute_sql(sqlcmd_ind_1 % (ev, at, ev, at))
                    if status == 2:
                        if __debug__: self.logger.info("Return with status 2")
   

    def _init_caches_ (self):
        query = "select name from sqlite_master where type='table'"
        (val, status) = self.execute_sql(query)
        self.tablespresent = val
        self.datasize = 0;
        for table in self.tablespresent:
            query = "select count(*) from %s" % (table)
            (val, status) = self.execute_sql(query)
            if(val[0] > 0):
                self.datasize += val[0]
                self.activetables.append(table)
                self.attributehash[table] = self.get_attribute_names(table)
                if((val[0] / 2) < self.MAX_CACHE_SIZE):
                    self.greedy_prefetch(table, val[0] / 2)

    def get_active_tables(self):
        return self.activetables

    def set_active_tables(self, tlist):
        self.activetables = []
        for t in tlist:
            if(t):
                if(t.find("*") >= 0):
                    elist = self.get_matching_event_types(t)
                    self.activetables.extend(elist)
#                    for e in elist:
#                        query = "select count(*) from %s" % (e)
#                        (val, status) = self.execute_sql(query)
#                        if(status == 0):
#                            self.greedy_prefetch(e, val[0]) 
                else:
                    if t not in self.eventlist:
                        raise Exception("Eventtype '%s' not valid for given database!" %(t))
                    self.activetables.append(t)
#                    query = "select count(*) from %s" % (t)
#                    (val, status) = self.execute_sql(query)
#                    if(status == 0):
#                        self.greedy_prefetch(t, val[0])
        if __debug__:
            self.logger.debug("Active tables set to %s" % (self.activetables))

    def get_event_types(self):
        if (self.eventlist):
            return self.eventlist
        query = "select name from sqlite_master where type='table'"
        (val, status) = self.execute_sql(query)
        self.tablespresent = val
        eventlist = []
        for table in self.tablespresent:
            if(table not in self.INTERNAL_TABLES):            
                query = "select count(*) from %s" % (table)
                (val, status) = self.execute_sql(query)
                if(val[0] > 0):
                    eventlist.append(table)
        return eventlist


    def get_matching_event_types(self, pattern):
        elist = self.eventlist
        if(pattern.strip() == '*'):
            return elist
        newp = pattern.replace('*','')

        retlist = []
        for e in elist:
            if(e.find(newp) >= 0):
                retlist.append(e)
        return retlist

    def get_data_size(self):
        if(self.datasize is not None):
            return self.datasize

    def greedy_prefetch(self, tablename, size):
        prefetch_query = "select * from %s limit %d"\
                 % (tablename, size)
        (recordlist, status) = \
        self.execute_sql_returnall(prefetch_query)

        # Clear the recordcache with all keys with prefix tablename
        if(len(self.recordcache) >= self.MAX_CACHE_SIZE):
            self.recordcache.clear()
        if(recordlist):
            attrlist = self.attributehash.get(tablename)
            for rtuple in recordlist:
                self.recordcache["%s-%s" % (tablename, rtuple[0])] = rtuple

    def get_origins(self):
        originlist = []
        for table in self.activetables:
            query = "select distinct origin from " + table
            (val, status) = self.execute_sql(query)
            if(val):
                originlist.extend(val)
        return (unique(originlist))

    
    def get_cache_stats(self):
        return (self.hitcount, self.misscount)
    

    def get_event(self, eid, table=None):
        vlist = []
        t = None

        if(table):
            val = self.prefetch_events([], table, eid)
            if(val):
                 vlist = list(val)
            t = table
        else:
            for t in self.activetables:
                 val = self.prefetch_events([], t, eid)
                 if(val):
                     vlist = list(val)
                     break

        # t now holds the tablename containing  event
        attrlist = []
        if t in self.attributehash:
            attrlist = self.attributehash.get(t)
        else:
            if __debug__: self.logger.critical("UNEXPECTED: Table name '%s' not found !" % (t))
            return None
        if __debug__: 
            self.logger.fine("Event Output for ID %s : %s" % (eid, vlist))
        if vlist:
            ev = Event(eid, attrlist, vlist)
            return (ev.get_avhash())
        else:
            return None


    def get_events(self, query, stateobj):
        """
            Executes input query and returns an EventGroup containing 
            Event objects sorted in ascending order of time.
        """
        evgroup = EventGroup()

        sqlcmd = "select * from  %s where %s"
        for table in self.activetables:            
            if __debug__: self.logger.debug(sqlcmd % (table, query))
            (rows, status) = self.execute_sql_returnall(sqlcmd % (table, query))
            if(status == 0):
                alist = self.get_attribute_names(table)
                for etuple in rows:
                    evid  = etuple[0]
                    etype = etuple[1]
                    vallist = list(etuple)
                    ev = Event(evid, attrlist=alist, valuelist=vallist)
                    ev.set_behavior(stateobj)
                    evgroup.add(ev)
        return evgroup

    def prefetch_events(self, idlist, tablename, startid=None):
        if not startid:
            startid = idlist[0]

        cachekey = "%s-%s" % (tablename, startid)
        if cachekey in self.recordcache:
            self.hitcount = self.hitcount + 1
            return self.recordcache.get(cachekey)
        else:
            self.misscount += 1
            
        prefetch_query = "select * from %s where eventno >= %s\
          limit %s" % (tablename, startid, self.PREFETCH_SIZE)
        if __debug__: 
            self.logger.fine("Key: %s - Prefetching Events : %s" % \
                          (cachekey, prefetch_query))
        (recordlist, status) = \
            self.execute_sql_returnall(prefetch_query)

        # Clear the recordcache with all keys with prefix tablename
        if(len(self.recordcache) >= self.MAX_CACHE_SIZE):
            self.recordcache.clear()
        if(recordlist):
            for  rtuple in recordlist :
                ckey = "%s-%s" % (tablename, rtuple[0])
                self.recordcache[ckey] = rtuple
            return self.recordcache.get(cachekey)

    def get_attribute_names(self, tablename):
        attrlist = []
        sqlcmd = "PRAGMA table_info(" + tablename + ");"
        (val, status) = self.execute_sql_returnall(sqlcmd)

        for row in val:
            attrlist.append(row[1])
        return attrlist

    def get_distinct_attrvalues(self, table, attr):
        query = "select distinct %s from %s" % (attr, table)
        (val, status) = self.execute_sql(query)
        return (val)

    def get_attrvalue_freq(self, table, attr, value):
        query = "select count(*)  from %s where %s='%s' " % \
             (table, attr, value)
        (val, status) = self.execute_sql(query)
        return (val[0])
    
    def show_minimal_stats(self):
        self.numrecords = self.get_data_size()
        print("Found %d events in database" \
                           % (self.numrecords))

        self.eventlist = self.get_event_types()
        for ev in self.eventlist:
            self.print_timestamps(ev)

        
    def print_timestamps(self, ev):
        timestamp_low = None
        timestamp_high = None
        freq = self.get_attrvalue_freq(ev, "eventtype", ev)
        query = "select timestamp from %s order by timestamp ASC, timestampusec ASC limit 1" % (ev)
        (val, status) = self.execute_sql(query)
        if(val[0] > 0):
            timestamp_low = val[0]
            
        query = "select timestamp from %s order by timestamp DESC, timestampusec DESC limit 1" % (ev)
        (val, status) = self.execute_sql(query)
        if(val[0] > 0):
            timestamp_high = val[0]

        if(timestamp_low and timestamp_high):            
            print ("\t%s - %s events [ %s (%s) to %s (%s) ] " %\
                 (ev, freq, time.asctime(time.gmtime(timestamp_low)), 
                    timestamp_low, 
                    time.asctime(time.gmtime(timestamp_high)),
                    timestamp_high))
  
  
    def showstats(self):
        
        h1("Statistics for %s" % (self.dbname)) 

        self.numrecords = self.get_data_size()
        print("Total number of records in database: %d" \
                           % (self.numrecords))

        self.eventlist = self.get_event_types()
        h2("Events")
        for ev in self.eventlist:
            self.print_timestamps(ev)

        h2("Event Attributes (number of distinct values)")
        ignore_list = ['eventno', 'eventtype', 'timestamp', 'timestampusec',
                       'origin']
        for ev in self.eventlist:
             attrs = self.get_attribute_names(ev);
             print("\tEvent: %s" % (ev))
             for attr in attrs:
                 if(attr not in ignore_list):                
                     attrvalues = self.get_distinct_attrvalues(ev, attr)
                     print("\t\t%s : %s " % (attr, len(attrvalues)))

        self.originlist = self.get_origins()
        
        h2("Event Origins")
        print("\t%s" % " ".join(self.originlist))



