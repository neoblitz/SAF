# normalizerclass.py
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

from storage import SqliteStorage
from attributes import Attributes

class Normalizer():
    
    def __init__(self, infile, outdb, plugin, debug,
                 set=None, attrs=None, xattrs=None, inmem=False):
        '''
            
        '''
        self.debug = debug
        self.plugin = plugin
        self.infilename = infile
        self.outdbname = outdb
        self.handle   = plugin.open(infile) 
        self.attrs    = plugin.init_plugin_attrs(cmdlineattrs=attrs, 
                                                 setval=set,
                                                 addtodefault=xattrs)
        
        print "\nPlugin attributes (with default values): "
        for a,v,t in self.attrs:
            print "\t%s = %s" %(a,v)

        # Stat counters
        self.parse_success = 0
        self.parse_failure = 0
        self.event_success = 0
        self.event_failure = 0
                
        self.tablename = plugin.get_eventtype() or 'DEFAULT_TYPE'        
        self._init_output(outdb, inmem)

    def _init_output(self, outdb, inmem):
        if inmem:
            self.dbname = ":memory:"
        else:
            # Create a random name
            self.dbname = self.outdbname

        print("Connecting to output database " + self.dbname)
        self.sqlite = SqliteStorage(self.dbname, pragmas=True)
        
        tablecols = []
        for a,t in self.attrs.get_attr_type_tuples():
            if(a == 'eventno'):
                t = "integer primary key autoincrement"
            tablecols.append('%s %s'%(a, t))
        tstr = ",".join(tablecols)
        
        sqlcmd = """create table %s (%s)""" %(self.tablename, tstr)
        #print("Building table: %s" %(sqlcmd))
        (ret, status) = self.sqlite.execute_sql(sqlcmd)
        if(status == 2):
            print "WARNING: Events will be appended to the table '%s'!" %\
            (self.tablename)
            print "If this is not desirable please delete the existing table '%s' or database file '%s' and try again !" %\
            (self.tablename, self.dbname)
            

        ilist = []
        for a in self.attrs.get_all_attrs():
            ilist.append('?')
        istr = ",".join(ilist)       
        self.insert_cmd = """insert into %s values(%s)""" %(self.tablename, istr)
        self.insert_param_cache = []
        

    def write_to_output(self, avhash):
        params = []
        for a in self.attrs.get_all_attrs():
            params.append(avhash.get(a))
        self.insert_param_cache.append(tuple(params))


    def run(self, processor=None):
        """
            Implements the main run loop of the normalizer
        """
        print "\nParsing records.."
        while True:
            record = self.plugin.get_next_record(self.handle)
            if record:
                parsed_record = self.plugin.parse(record, processor)
                if self.debug: 
                    print parsed_record
                if(parsed_record):
                    self.write_to_output(parsed_record)
                    self.num_raw_records = self.plugin.get_num_rawrecords()
                    if((self.num_raw_records % 10000)==0):
                        self.persist()
                    self.parse_success += 1
                else:
                    self.parse_failure += 1
            else: 
                break
        
        self.persist()
        self.num_raw_records = self.plugin.get_num_rawrecords()
        self.plugin.close()

        
    def persist(self):  
        (ret, status) =\
            self.sqlite.execute_many(self.insert_cmd, self.insert_param_cache)
        if status != 0:
           print("ERROR: Writing events to database failed!")
           self.event_failure +=  len(self.insert_param_cache)
        else:
            print ("Wrote %d events to database" %(len(self.insert_param_cache)))
            self.event_success +=  len(self.insert_param_cache)
        ''' Clear the parameter cache once done '''
        self.insert_param_cache = []
    
    
    def get_stats(self):
        stats = {'Total Input Records': self.num_raw_records,
                 'Parsed Successfully': self.parse_success,
                 'Parsing Failures': self.parse_failure,
                 'Events Output' : self.event_success}
        return stats

