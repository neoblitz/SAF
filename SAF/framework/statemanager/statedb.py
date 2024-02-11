# 
# statedb.py - Class for managing state data
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
import sys
import webbrowser

import os
import cPickle
import base64
import math

from time import time, asctime
from threading import Lock

#Local Imports
import framework.common.utils as utils
from framework.common.storage import SqliteStorage
from framework.common.sorted_collection import SortedCollection

class StateRecord:
    '''
        A StateRecord object represents a record in the State database
    '''

    # TABLECOLS
    TABLECOLS = { 'col0' : 'recordid',
                  'col1': 'currstatename',
                  'col2': 'currstateval',
                  'col3':  'constraints',
                  'col4': 'nextstatename',
                  'col5': 'nextstateval',
                  'col6': 'output',
                  'col7': 'history',
                  'col8': 'etuples'
                 }

    def __init__(self, options=None):
        self.record = {}
        if options:
            self.set_record_from_dict(options)

    @staticmethod
    def get_attribute_names():
        # This is being returned as a manually coded list for 
        # reasons of efficiency and requirements of order
        return ['recordid', 'currstatename', 'currstateval',
                'constraints', 'nextstatename', 'nextstateval',
                'output', 'history', 'etuples']

    @staticmethod
    def get_attribute_types():
        # This is being returned as a manually coded list for 
        # reasons of efficiency and requirements of order
        return ['number', 'text', 'text',
                'text', 'text', 'text',
                'text', 'text', 'text']

    def set_record_from_dict(self, opts, unmarshal=False):
        self.record['col0'] = opts.get('col0', '')
        self.record['col1'] = opts.get('col1', '')
        self.record['col3'] = opts.get('col3', '')
        self.record['col4'] = opts.get('col4', '')
        self.record['col8'] = opts.get('col8', '')
        self.record['col2'] = opts.get('col2', {})
        self.record['col5'] = opts.get('col5', {})
        self.record['col6'] = opts.get('col6', [])
        self.record['col7'] = opts.get('col7', {})

    def set_record_from_tuple(self, rtup, unmarshal=False):
        self.record['col0'] = rtup[0]
        self.record['col1'] = rtup[1]
        self.record['col3'] = rtup[3]
        self.record['col4'] = rtup[4]
        self.record['col8'] = rtup[8]
        self.record['col5'] = rtup[5]
        self.record['col2'] = rtup[2]
        self.record['col6'] = rtup[6]
        self.record['col7'] = rtup[7]

    def get_record_as_list(self, marshal=False):
        reclist = \
        [
         self.record['col0'],
         self.record['col1'],
         (marshal and utils.marshal(self.record['col2'])\
                    or  self.record['col2']),
         self.record['col3'],
         self.record['col4'],
         (marshal and utils.marshal(self.record['col5'])\
                    or  self.record['col5']),
         (marshal and utils.marshal(self.record['col6'])\
                    or  self.record['col6']),
         (marshal and utils.marshal(self.record['col7'])\
                    or  self.record['col7']),
         (marshal and utils.marshal(self.record['col8'])\
                    or  self.record['col8'])
                    ]
        return reclist
    
    
#    def get_record_as_list(self, marshal=False):
#        reclist = \
#        [
#         self.record['col0'],
#         self.record['col1'],
#         (marshal and utils.marshal(self.record['col2'])\
#                    or  self.record['col2']),
#         self.record['col3'],
#         self.record['col4'],
#         (marshal and utils.marshal(self.record['col5'])\
#                    or  self.record['col5']),
#         (marshal and utils.marshal(self.record['col6'])\
#                    or  self.record['col6']),
#         (marshal and utils.marshal(self.record['col7'])\
#                    or  self.record['col7']),
#         (marshal and utils.marshal(self.record['col8'])\
#                    or  self.record['col8'])
#                    ]
#        return reclist

    def get_val(self, key):
        r = self.record.get(key, '')
        if(r is None):
            return ''
        try:
            unr = utils.unmarshal(r)
            return unr
        except cPickle.UnpicklingError:
            return r
        except EOFError as e:
            return r

    def get_history(self):
        return self.get_val('col7') or {}

    def get_output(self):
        return self.get_val('col6') or []

    def get_nextstatename(self):
        return self.get_val('col4') or ''

    def get_currstatename(self):
        return self.record.get('col1', '')

    def get_nextstateval(self):
        return self.get_val('col5') or {}

    def get_currstateval(self):
        return self.get_val('col2') or {}

    def get_etuples(self):
        return self.get_val('col8') or {}


class StateDatabase(SqliteStorage):
    MAX_CACHE_SIZE = 100000
    PREFETCH_SIZE = 20000

    def __init__(self, tempdir, logger, inmem=False):
        self.logger = logger
        self.tempdir = tempdir
        self.tablename = "state"

        if inmem:
            self.dbname = ":memory:"
        else:
            # Create a random name
            self.dbname = tempdir + os.path.sep + \
                         utils.get_randstring(10) + ".sqlite";


        if __debug__: self.logger.info("Connecting to database " + self.dbname)
        SqliteStorage.__init__(self, self.dbname, self.logger, pragmas=True)
        self.recordcache = {}
        self.removed_record_hash = {} # This is a hash for every transaction
        self.reslock = Lock()
        self.updlock = Lock()
        self.deletedids = {} # This is a global hash of deleted ids
        self.table_empty = {}
        self.table_empty[self.tablename] = False


    def flush_cache(self):
        if __debug__: self.logger.info("Clearing record cache!")
        self.recordcache.clear()
        self.removed_record_hash.clear()

    def reset_internal_state(self):
        if __debug__: self.logger.info("Resetting internal statedatabase!")
        self.recordcache.clear()
        self.removed_record_hash.clear()
        self.deletedids.clear()

    def print_cache(self):
        if __debug__: self.logger.info(self.recordcache.keys())

    def get_tablename(self):
        return self.tablename


    def print_state_header(self, obj):
        context = "behavior: %s Object Name: %s Type: %s" % \
                             (obj.get_behaviorname(),
                              obj.get_name(),
                              obj.get_type())
        if __debug__: self.logger.state(context)


    def get_state_header(self, obj):
        context = "behavior: %s Object Name: %s Type: %s" % \
                             (obj.get_behaviorname(),
                              obj.get_name(),
                              obj.get_type())
        return context


    def print_state(self, statename, reclist):
        if(not self.logger.isEnabledFor(self.logger.LOGLEVELS.get('state'))):
            return

        sqlcmd = """ select * from %s """ % (self.tablename)
        (val, status) = self.execute_sql_returnall(sqlcmd)
        if(not val):
            return

        if __debug__: 
            self.logger.state("\t Record list returned after processing state %s: %s\n " % \
                           (statename, reclist))

        # Get console size to compute the output widths
        columns = 80
        try:
            rows, columns = os.popen('stty size', 'r').read().split()
        except:
            pass

        col1w = int((0.04) * int(columns))
        col2w = int((0.06) * int(columns))
        col3w = int((0.50) * int(columns))
        col4w = int((0.49) * int(columns))

        fstring = "%%%ds| %%%ds| %%%ds| %%%ds" % \
                    (col1w, col2w, col3w, col4w)


        if __debug__: self.logger.state("\t Intermediate State Table: %s\n " % \
                           (self.tablename))
        if __debug__: self.logger.state(fstring % ("Recordid".center(col1w),
                                     "CurrState".center(col2w),
                                     "CurrStateVal".center(col3w),
                                     "History".center(col4w)))
        if __debug__: self.logger.state('-' * int(columns))


        for t in val:
            printstr = fstring % \
            (str(t[0]).center(col1w)[:col1w],
             str(t[1]).center(col2w)[:col2w],
             str(utils.unmarshal(t[2])).replace('and', '').center(col3w)[:col3w],
             str(utils.unmarshal(t[7])).replace('and', '').center(col4w)[:col4w]
             )

            if __debug__: self.logger.state(printstr)

        if __debug__: self.logger.state("-" * int(columns))


    def get_output(self, state, tablename=None):
        tablename = tablename or self.tablename
        sqlcmd = """select output from %s where currstatename LIKE '%s%%'""" %\
            (tablename, state)
        (val, status) = self.execute_sql(sqlcmd)
        if(not val):
            if __debug__: self.logger.debug("NO output for state : " + state)
            return []
        return  map(utils.unmarshal, val)


    def prefetch_records(self, recordidlist, startrecordid=None):

        if not startrecordid:
            if(not recordidlist):
                return
            startrecordid = recordidlist[0].get_first_id()

        prefetch_query = "select * from %s where recordid>=%s limit  %s"\
                         % (self.tablename, startrecordid, self.PREFETCH_SIZE)
        srecord = self.get_record_from_cache(startrecordid)
        if(srecord):
            return srecord

        if __debug__: 
            self.logger.fine("Prefetching records : %s" % (prefetch_query))
        (recordlist, status) = \
            self.execute_sql_returnall(prefetch_query)
        
        if(len(self.recordcache) > self.MAX_CACHE_SIZE):
            self.recordcache.clear()
        
        if recordlist:
            for  rtuple in   recordlist :
                srecord = StateRecord()
                srecord.set_record_from_tuple(rtuple, unmarshal=True)
                self.recordcache[rtuple[0]] = srecord

    def get_recordids(self, query, prefetch=True):
        sqlcmd = "select recordid from %s where %s " % (self.tablename, query)
        if __debug__: 
            self.logger.debug(sqlcmd)
        (recordidlist, status) = self.execute_sql(sqlcmd)
        return recordidlist


    def remove_record_from_cache(self, recordid):
         try:
             del self.recordcache[recordid]
         except:
             pass

    def get_record_from_cache(self, recordid):
        return self.recordcache.get(recordid, None)


    def get_record(self, recordid):

        if(recordid in self.deletedids):
            return None
        
        if self.table_empty[self.tablename]:
            return None

        # Check if the record exists in the cache
        if __debug__: 
            self.logger.fine("Cache State: %s"% (self.recordcache.keys()))
        srecord = self.get_record_from_cache(recordid)
        if(not srecord):
            if __debug__: self.logger.fine("Cache MISS: Wanted: %s \
            Got %s from cache! Fetching" % (recordid, srecord))
            self.prefetch_records([], recordid)
            srecord = self.get_record_from_cache(recordid)
        else:
            if __debug__: 
                self.logger.fine("Cache HIT : Wanted: %s \
            Got %s from cache!" % (recordid, srecord))
        self.logger.fine("Record for recordid %s : %s" % (recordid, srecord))
        return  srecord


    def set_active_table(self, name) :
        if name is None:
            raise Exception("Tablename cannot be set to None !")
        self.tablename = name


    def record_deleted(self, recordid):
        if(recordid in self.removed_record_hash):
            return True
        else:
            return False

    def remove_record(self, recordid):
        name = self.tablename
        sqlcmd = """delete from %(name)s where  recordid=%(recordid)s"""
        if __debug__: 
            self.logger.debug("Executing SQL: " + sqlcmd % vars())
        
        # Mark that the record is deleted
        self.removed_record_hash[recordid] = True


    def create_table(self, name=None) :
        if(name is None):
            name = self.tablename
        else:
            self.tablename = name

        colnames = StateRecord.get_attribute_names()
        coltypes = StateRecord.get_attribute_types()

        sql_string = ""
        sql_list = []
        for key, val in zip(colnames, coltypes):
            if(val != ''):
                s = "%s %s" % (key, val)
                sql_list.append(s)

        sql_string = ",".join(sql_list)

        sqlcmd = """create table %s(%s)""" % (self.tablename, sql_string)

        self.begin_transaction()
        if __debug__: self.logger.debug("Executing SQL: " + sqlcmd)
        self.execute_sql(sqlcmd)

        sqlcmds = ["""create index  ind_%s_recid on %s(recordid)""",
                   """create index  ind_%s_currstatename on %s(currstatename)""",
#                   """create index  ind_%s_nextstatename on %s(nextstatename)""",
#                   """create index  ind_%s_nextstateval on %s(nextstateval)""",
#                   """create index  ind_%s_constraints on %s(constraints)""",
#                   """create index  ind_%s_output on %s(output)""",
#                   """create index  ind_%s_history on %s(history)""",
#                   """create index  ind_%s_etuples on %s(etuples)"""
                   ]

        for cmd in sqlcmds:
            if __debug__: self.logger.info("Executing SQL: " + cmd % (name, name))
            self.execute_sql(cmd % (name, name))
        self.commit_transaction()
        self.table_empty[self.tablename] = True 



    def add_new_records(self, recordlist, values):
        srecord = StateRecord(values)
        rec = srecord.get_record_as_list(marshal=True)
        paramlist = [(r.get_id(), rec[1], rec[2], rec[3], rec[4], rec[5], rec[6],
                      rec[7], rec[8]) for r in recordlist]

        sqlcmd = """insert into %s values (?,?,?,?,?,?,?,?,?)""" % (self.tablename)
        if __debug__: self.logger.debug("Adding records : %s " % (sqlcmd))
        self.execute_many(sqlcmd, paramlist)
        self.table_empty[self.tablename] = False

    def update_record(self, recordid, values):
        srecord = StateRecord(values)
        colvals = srecord.get_record_as_list(marshal=True)
        colnames = srecord.get_attribute_names()

        upd_string = ""
        upd_list = []
        for key, val in zip(colnames, colvals):
            if(val != ''):
                s = "%s='%s'" % (key, val)
                upd_list.append(s)

        upd_string = ",".join(upd_list)

        sqlcmd = """update %s SET %s  where recordid=%s""" %\
         (self.tablename, upd_string, recordid)
        if __debug__: self.logger.fine("Executing SQL: " + sqlcmd)
        self.execute_sql(sqlcmd)
        # Put the recordid in the deletedid list
        # And take the recordid in colval[0] off the deleted list 
        # if its not empty
        try:
            if colvals[0]:
                del self.deletedids[int(colvals[0])]
                self.deletedids[recordid] = True
        except KeyError:
            pass




