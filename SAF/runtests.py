# runtests.py -   Master Controller for running tests
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
#-------------------------------------------------------------------------------

#
# NOTE: All tests are defined in tests/testcmds.py. 
#
# Usage
# -----
#    python runtests.py 
#
#
# Set the environment variable DATADIR to the directory containing the 
# SQLite files. Default value for DATADIR is the current directory.
# 
# Running all tests
# -------------------
#    $python runtests.py 
#         OR
#    $python runtests.py --a
#
# Running individual tests
# ------------------------
#    See usage for options
#------------------------------------------------------------------------------

import sys
sys.path.append("./tests")

import os
import subprocess
import unittest
import testcmds
import grammartest
import getopt
try:
    from collections import OrderedDict
except:
    from framework.common.dictionary import OrderedDict as OrderedDict

from framework.common.utils import h1, h2, get_filename_with_time

COVERAGECONF = "utils/dev/coverageconf"
COVERAGEOUT  = "logs/"

def usage():
    print """
python runtests.py [optional args] 

Optional Arguments
==================
    [--data] # Data directory containing the sqlite files 
    [--a]    # Run all tests (default)
    [--b]    # Run tests for knowledgebase
    [--c]    # Run case studies from paper
    [--g]    # Run grammar parsing tests
    [--f]    # Run simple feature tests
    [--s]    # Run smoke tests to test installation
    [--x]    # Run plugin tests
    [--diffs] # Output only differences between actual and expected output for failed tests
    [--capture]  # Run tests and capture output. Existing output files 
                 # will be overwritten but a backup is made in /tmp/
    [--coverage]  # Run all tests with code coverage enabled
"""



class TestBaseClass(unittest.TestCase):
    """ Base Test Class Providing Common Functions"""

    def setUp(self):        
        try:
            dirname = "/tmp/temp/"
            os.mkdir(dirname)
        except:
            pass        
        self.expectedoutdir = "tests" + os.path.sep + "expected" + os.path.sep
        self.datadir = os.environ.get('DATADIR', "./")
        self.capture  = os.environ.get('CAPTURE', None)
        self.onlydiffs = os.environ.get('ONLYDIFFS', None)
        self.withcoverage = os.environ.get('COVERAGE', None)
        self.testprog = os.environ.get('TESTPROG', "./saf.py")
        self.testhash = {}
        self.totaltests = 0
       
    def tearDown(self):
        os.system("rm -f /tmp/temp/*.sqlite")
    
    def execute(self, tests):
        print "\n"
        failstr = self.runsuite(tests)
        if failstr:
            self.fail("\n\n".join(failstr))
            
    def runsuite(self, tests):
        failstr = []
        for testid, topts in tests.items():
            testopts = topts % (self.datadir)
            testcmd = self.testprog + " " + testopts            
            if self.withcoverage and self.testprog == "./saf.py":
                testcmd = "coverage run --rcfile=%s %s %s "  %(COVERAGECONF, self.testprog, testopts)
            print "\tRunning " + testid + " [" + testcmd + "]"            
            testcmd = testcmd.split()
            gp = subprocess.Popen(testcmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE);
            (out, err) = gp.communicate()
            outlist = out.split("\n")
            try:
                c = outlist.count('')
                for _ in range(c):
                    outlist.remove('')
            except:
                pass

            # Expected output file
            exoutfile = self.expectedoutdir + testid
                       
            # In capture mode just write out the results 
            # to the expected output file
            if(self.capture):
                f = open(exoutfile, "w")
                expoutlist = [f.write(l+"\n") for l in outlist]
                continue
            
            f = open(exoutfile, "r")            
            expoutlist = [l.strip('\n') for l in f.readlines()]

            try:
                c = expoutlist.count('')
                for _ in range(c):
                    expoutlist.remove('')
            except:
                pass
            
            if(self.onlydiffs):
                outputstr = "Test %s\n~~~~~ DIFF ~~~~~\n%s" % \
                (testid, (list(set(expoutlist) - set(outlist))))
            else:
                outputstr = "Test %s\n ~~~~~ Expected ~~~~~\n\t\t%s\n ~~~~~ Actual ~~~~~\n\t\t%s\n~~~~~ DIFF ~~~~~\n%s" % \
                (testid,"\n\t\t".join(expoutlist), "\n\t\t".join(outlist),
                 (list(set(expoutlist) - set(outlist))))
            
            if(expoutlist != outlist):
                diff = list(set(expoutlist) - set(outlist))
                ignore = False
                if(not self.ignore_failure(diff)):
                    failstr.append(outputstr)                 
            self.totaltests += 1
        return failstr
    
    def ignore_failure(self, diff):
        ignore = False
        ignore_list = ['Reading input event', 
                       'Detected',
                       'Creating temporary directory',
                       '#    Semantic Analysis Framework']
        if (len(diff) >= 1):
            for d in diff:
                found = False
                for ig in ignore_list:
                    if(d.find(ig) >= 0):
                        ignore = True
                        found = True
                        break
                if not found:
                    ignore = False
                
        return ignore

class SimpleFeatureTests(TestBaseClass):
    """ Test of simple features """
       
    def test_qualifier_expression(self):
        self.execute(OrderedDict(testcmds.featuretests_qualifier))

    def test_relationops(self):       
        self.execute(OrderedDict(testcmds.featuretests_relationalops))

    def test_wildcards(self):        
        self.execute(OrderedDict(testcmds.featuretests_wildcards))

    def test_constraints(self):        
        self.execute(OrderedDict(testcmds.featuretests_constraints))
        
    def test_opconstraints(self):
        self.execute(OrderedDict(testcmds.featuretests_opconstraints))

    def test_concurrentops(self):
        self.execute(OrderedDict(testcmds.featuretests_concurrentops))

    def test_logicalops(self):
        self.execute(OrderedDict(testcmds.featuretests_logicalops))

    def test_leadstoops(self):
        self.execute(OrderedDict(testcmds.featuretests_leadstoop))

    def test_errors(self):
        self.execute(OrderedDict(testcmds.featuretests_errors))

    def test_import(self):
        self.execute(OrderedDict(testcmds.featuretests_import))
        
    def test_bconstraints(self):
        self.execute(OrderedDict(testcmds.featuretests_bconstraints))
                
    def test_sconstraints(self):
        self.execute(OrderedDict(testcmds.featuretests_sconstraints))


class SmokeTests(TestBaseClass):
    """ Test of simple features to quickly check functionality"""
       
    def test_qualifier_expression(self):
        self.execute(OrderedDict(testcmds.featuretests_qualifier))

    def test_relationops(self):       
        self.execute(OrderedDict(testcmds.featuretests_relationalops))

    def test_wildcards(self):        
        self.execute(OrderedDict(testcmds.featuretests_wildcards))

    def test_constraints(self):        
        self.execute(OrderedDict(testcmds.featuretests_constraints))
        
    def test_opconstraints(self):
        self.execute(OrderedDict(testcmds.featuretests_opconstraints))

    def test_import(self):
        self.execute(OrderedDict(testcmds.featuretests_import))

class KnowledgeBaseTests(TestBaseClass):
    """ Tests for basic functionality with simple scripts"""
       
    def test_basic_ip(self):
        failstr = self.execute(testcmds.basictests_ip)

    def test_basic_tcp_pkt(self):
        self.execute(testcmds.basictests_tcp_pkt)

    def test_basic_tcp_connsetup(self):
        self.execute(testcmds.basictests_tcp_connsetup)

    def test_basic_tcp_conntdown(self):
        self.execute(testcmds.basictests_tcp_conntdown)

    def test_basic_udp(self):
        self.execute(testcmds.basictests_udp)

    def test_basic_dns(self):
        self.execute(testcmds.basictests_dns)
        

class CaseStudyTests(TestBaseClass):
    """ Tests for basic functionality with simple scripts"""
       
    def test_dnskaminsky(self):
        self.execute(testcmds.casestudy_dnskaminsky)

    def test_doshussain03(self):
        self.execute(testcmds.casestudy_doshussain03)

class GrammarParsingTests(TestBaseClass):
    """ Tests for parsing of behavior and state declarations"""

    def setUp(self):
        self.expectedoutdir = "tests" + os.path.sep + \
                               "expected" + os.path.sep
        self.ebnf = './framework/parser/language.ebnf'

    def tearDown(self):
        os.system("rm -f /tmp/temp/*.sqlite")

    def test_behavior_declarations(self):
        print "\n"
        retval = grammartest.run_behavior_parse_tests(self.ebnf)
        self.assertTrue(retval)

    def test_state_declarations(self):
        print "\n"
        retval = grammartest.run_state_parse_tests(self.ebnf)
        self.assertTrue(retval)

class PluginTests(TestBaseClass):
    
    def test_syslog_plugin(self):
        self.execute(OrderedDict(testcmds.syslog_plugin_test))

    def test_bind_plugin(self):
        self.execute(OrderedDict(testcmds.bind_plugin_test))

    def test_argus_plugin(self):
        self.execute(OrderedDict(testcmds.argus_plugin_test))

    def test_basic_plugin(self):
        self.execute(OrderedDict(testcmds.basic_plugin_test))

    def test_mysql_plugin(self):
        self.execute(OrderedDict(testcmds.mysql_plugin_test))

    def test_apache_plugin(self):
        self.execute(OrderedDict(testcmds.apache_plugin_test))


try:
    opts, args = getopt.getopt(sys.argv[1:], '', [ 'data=', 'b', 'c',
                                                  'g',
                                                  'a',
                                                  'f', 
                                                  's', 
                                                  'x',
                                                  'capture',
                                                  'diffs',
                                                  'coverage'])
except getopt.error, msg:
    usage()
    sys.exit(2)

#curses.noecho()

basictests = False
casestudies = False
grammarparsetests = False
smoketests= False
featuretests = False
alltests = True
plugintests = False

datadir = None
capture = False
diffs = False
coverage = False
# Process options
for option, arg in opts:
    if option == '--a':
      alltests = True
    elif option == '--b':
      basictests = True
      alltests = False
    elif option == '--g':
      grammarparsetests = True
      alltests = False
    elif option == '--c':
      casestudies = True
      alltests = False
    elif option == '--data':
      datadir = arg     
    elif option == '--f':
      featuretests = True
      alltests = False       
    elif option == '--s':
      smoketests = True
      alltests = False 
    elif option == '--x':
      plugintests = True
      alltests = False      
    elif option == '--capture':
      capture = True
    elif option == '--diffs':
      diffs = True
    elif option == '--coverage':
      coverage = True
    else:
        usage()
        sys.exit(2)



# Set the data directory to specified value or the current directory by default 
os.environ["DATADIR"] = datadir or "."
print "Data directory set to %s " % (os.environ.get("DATADIR"))

if(capture):  
    h2 ("CAUTION: Capture enabled! ") 
    print("Existing expected output files will be overwritten")
    os.environ["CAPTURE"] = str(capture)
    var = raw_input("!!! Please confirm by typing 'YES' !!!")
    if (var != 'YES'):
        print "Aborting!"
        sys.exit(2)

if(diffs):
    print("Outputting only diffs for failures")
    os.environ["ONLYDIFFS"] = str(diffs)
    
if(coverage):
    print("Running tests with code coverage")
    os.environ["COVERAGE"] = str(coverage)    
    
if(alltests or basictests):
    h1("Running Tests for Models in KnowledgeBase ")
    suite = unittest.TestLoader().loadTestsFromTestCase(KnowledgeBaseTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

if(alltests or casestudies):
    h1("Running Case Studies From Paper")
    suite = unittest.TestLoader().loadTestsFromTestCase(CaseStudyTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

if(alltests or featuretests):
    h1("Running Feature Tests")
    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleFeatureTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

if(alltests or smoketests):
    h1("Running Smoke Tests")
    suite = unittest.TestLoader().loadTestsFromTestCase(SmokeTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

if(alltests or grammarparsetests):
    h1("Running Grammar Parsing Tests")
    suite = unittest.TestLoader().loadTestsFromTestCase(GrammarParsingTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

if(plugintests):
    h1("Running Plugin Tests")
    os.environ["TESTPROG"] = "plugins/asciiplugins/normalizer.py "
    suite = unittest.TestLoader().loadTestsFromTestCase(PluginTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

if(coverage):
    print "Combining coverage results from all test cases..."
    os.system("coverage combine --rcfile=COVERAGECONF")
    dirname = get_filename_with_time(prefix="htmlreport_")
    dirpath = "%s/%s"  %(COVERAGEOUT, dirname)
    
    print "Generating HTML report and saving it in %s ..." %(dirpath)
    os.system("coverage html -d %s" %(dirpath))
    
    print "Open report in browser..."
    os.system("firefox %s/index.html" %(dirpath))
    
    print "Removing .ccoverage .."
    os.system("rm -f .coverage")
