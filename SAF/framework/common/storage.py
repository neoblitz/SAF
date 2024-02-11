# storage.py - Database Module
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
import os
from time import time
from threading import Lock

# Third Party Imports
# The following piece of code is necessary to run the following code
# smoothly across Ubuntu 9.10 / FC4/ FC6 
try:
    import sqlite3
except:
    from pysqlite2 import dbapi2 as sqlite3

# Local Imports
import framework.common.utils as utils


class SqliteStorage:

    CACHE_SIZE_PERCENTAGE = 20
    PAGE_SIZE_DEFAULT = 1024
    INTERNAL_TABLES = ['sqlite_sequence']

    def __init__(self, dbname, logger=None, pragmas=True):
        """
            Establishes a connection to the database and executes
            a set of default SQLite pragmas.
        """
        
        # Initialize the logger for this module
        self.logger = logger
        self.within_transaction = False

        self.dbname = dbname
        if(self.dbname != ":memory:"):
            if not os.path.exists(self.dbname):
                f = open(self.dbname, "w");
                f.close()

        self.conn = sqlite3.connect(self.dbname, 
                                    check_same_thread=False)
        self.conn.isolation_level = None
        self.c = self.conn.cursor()
        
        if __debug__: 
            self.updates = 0
            self.inserts = 0
            self.selects = 0
            self.pragmas = 0
            self.creates = 0
            self.misc = 0
            self.deletes = 0
            self.transactions = 0

        # Get available memory
        self.mem = utils.get_available_memory()

        if __debug__: 
            self.logger.info("Available Physical Memory : %d" % (self.mem))
        cachesize = (self.mem * self.CACHE_SIZE_PERCENTAGE / 100)
        cache_pages = cachesize / self.PAGE_SIZE_DEFAULT
        if __debug__: 
            self.logger.info("SQL Cache Size  : %d" % (cache_pages))

        # Make optimization settings 
        if pragmas:
            self.execute_sql("PRAGMA auto_vacuum=NONE")
            # Disable immediate writes to disk
            self.execute_sql("PRAGMA synchronous=off")
            self.execute_sql("PRAGMA temp_store=MEMORY")
            self.execute_sql("PRAGMA default_cache_size=%d" % (cache_pages))
            self.execute_sql("PRAGMA journal_mode=OFF")
            self.execute_sql("PRAGMA count_changes=OFF")
            

    def update_stats(self, sqlstmt):
        sqlstmt = sqlstmt.strip()
        if(sqlstmt.find("select") == 0):
            self.selects += 1
        elif(sqlstmt.find("update") == 0):    
            self.updates += 1
        elif(sqlstmt.find("create") == 0):    
            self.creates += 1
        elif(sqlstmt.find("insert") == 0):    
            self.inserts += 1
        elif(sqlstmt.find("PRAGMA") == 0):    
            self.pragmas += 1
        elif(sqlstmt.find("delete") == 0):    
            self.deletes += 1
        else:
            self.misc += 1
            
    def get_stats(self):
        return ({'selects':self.selects,
                 'updates':self.updates,
                 'creates':self.creates,
                 'inserts':self.inserts,
                 'pragmas':self.pragmas,
                 'misc': self.misc,
                 'deletes': self.deletes,
                 'transactions' : self.transactions})
    
    
    def execute_sql(self, sqlstmt):
        """
            Executes input SQL query and returns a list of 1-tuples
            where each 1-tuple in the list corresponds to a table row 
            with the first column.
            
            Output Format:
                result = [ (r1c1), ..., (rkc1)]
        """

        if __debug__: 
            self.logger.sqlcmd("%s"% (sqlstmt))
        
        try:
            self.c.execute(sqlstmt)
        except sqlite3.OperationalError as e1:
            err = str(e1)
            if(err.find("syntax error") > 0):
                raise Exception("Sqlite3 Operational Error: %s \
                            \n while executing %s" % (e1, sqlstmt))
            else:
                if __debug__: self.logger.debug("Sqlite3 Operational Error: %s \
                            \n while executing %s" % (e1, sqlstmt))
            return (None, 2)
        except sqlite3.Error as e2:
            if __debug__: self.logger.critical("Sqlite3 Generic Error: %s \
                            \n while executing %s" % (e2, sqlstmt))
            return (None, 3)


        if __debug__:
            self.update_stats(sqlstmt)

        result = [row[0] for row in self.c]
        if(not result):
            return ([], 4)
            
        return (result, 0)


    def dump(self, filename):
        """
            Dump a SQL database to a file 
        """
        
        with open(filename, 'w') as f:
            for line in self.c.iterdump():
                f.write('%s\n' % line)

    def execute_sql_returnall(self, sqlstmt):
        """
            Executes input SQL query and returns a list of n-tuples
            where each n-tuple in the list corresponds to a table row 
            of n columns.
            
            Output Format:
                result = [ (r1c1, r1c2,..., r1cn), ..., (rkc1, rkc2,..., rkcn)]
        """
        if __debug__:
            self.update_stats(sqlstmt)
            st = time()
            self.logger.sqlcmd("%s"% (sqlstmt))
                        
        try:
            self.c.execute(sqlstmt)
        except sqlite3.OperationalError:
            return (None, 2)
        except sqlite3.Error, e:
            return (None, 3)

        # Profiling revealed that 
        # a) the loop comprehension used below is more efficient 
        #     than self.c.fetchall() with python2.7
        # b) more efficient than the identity map operation
        #     map(None, self.c)
        result = [row for row in self.c]

        if __debug__:        
            self.logger.sqlcmd("%0.6f"%(time()-st))
        
        if(not result):
            return ([], 4)
        return (result, 0)


    def begin_transaction(self):
        """
            Begins a database transaction 
        """
        
        if(self.within_transaction):
            if __debug__: self.logger.info("WARNING Already within a transaction !!")
            return
        stime = time()
        if __debug__: self.logger.info("Started Transaction .. time: %d" % (stime))
        self.execute_sql("BEGIN")
        self.within_transaction = True


    def commit_transaction(self):
        """
            Commits Transaction 
        """
        self.execute_sql("COMMIT")
        etime = time()
        self.within_transaction = False
        if __debug__: 
            self.transactions +=1 
        if __debug__: self.logger.info("ENDED Transaction.. time: %d" % (etime))

    def execute_many(self, sqlstmt, plist):
        '''
            Executes a prepared SQL statement 
        '''
        
        if __debug__:
            self.update_stats(sqlstmt)
            self.logger.sqlcmd("%s"% (sqlstmt))

        try:
            self.c.executemany(sqlstmt, plist)
        except sqlite3.OperationalError as e1:
            err = str(e1)
            if(err.find("syntax error") > 0):
                raise Exception("Sqlite3 Operational Error: %s \
                            \n while executing %s" % (e1, sqlstmt))
            else:
                if __debug__: self.logger.debug("Sqlite3 Operational Error: %s \
                            \n while executing %s" % (e1, sqlstmt))
            return (None, 2)
        except sqlite3.Error as e2:
            if __debug__: 
                self.logger.critical("Sqlite3 Generic Error: %s \
                            \n while executing %s" % (e2, sqlstmt))
            return (None, 3)


        return (0)

