#!/usr/bin/python -O
#
# saf.py - Semantic Analysis Framework 
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

try:
	# Python libraries
	import sys
	import os
	import getopt
	import tempfile
	import shutil
	import traceback
	import time
	from datetime import date
	import commands
	
	# Thirdparty libraries
	from simpleparse.common import numbers, strings, comments
	from simpleparse.parser import Parser
	from simpleparse.error import ParserSyntaxError
except Exception as ex:
	#header()
	print "ERROR: Unmet depedencies!"
	print ex
	print "\n Please install dependencies as explained in README!"
	sys.exit(2)
	

profilefound = True
try:
	import cProfile
	import pstats
except:
	profilefound = False

hpyfound = True
try:
	from guppy import hpy; 
except:
	hpyfound = False

# Local imports
import framework.dal.eventdb as eventdb
import framework.parser.parser as bparser
import framework.objects.behaviortree as behaviortree
import framework.objects.behaviortree as Event
import framework.objects.behaviortree as EventGroup
import framework.objects.behaviortree as BehaviorInstance
import framework.objects.behaviortree as BehaviorInstanceList
import framework.processor.process_model as processmodel
import framework.common.utils as utils
import framework.common.globalsym as globalsym
import framework.common.log as log
from framework.dal.dataabstraction import DataManager
from framework.statemanager.statemanager import StateManager
from framework.presentation.textsummary import DisplayTextSummary

# Custom exceptions
from framework.common.errordefs import SyntaxError,\
					  AbortCondition,\
					  ModelProcessingError
VERSION = "0.2a"
LANGUAGE_EBNF_FILE = 'framework/parser/language.ebnf'
LOGDIR = "logs"

# Flag for pretty printing
pretty = False

# Setting this will cause failed paths to be not shown
dont_report_fails = False

# Print the total time taken for applying the model over data
print_time = False

# Profiling execution time and memory usage
profile   = False
showheap  = False
if hpyfound and showheap:
	h = hpy()

def main():
	#FIXME: Shift the command line handling functions to 
	# the newer argparse module. NOTE: argparse is supported only from 
	# python 2.7.5

	# Parse command line options
	try:
		opts, args = getopt.getopt(sys.argv[1:],
								   '',
								  ['db=', 'model=', 'knowbase=',
								   'verbose=',  'inmem', 'profile',
								   'pretty', 'nofail', 
								   'time', 'stats'])
	except getopt.error, msg:
		usage()
		sys.exit(2)

	# Set defaults for the command-line options
	dbname 	  = None
	dbtype    = "sqlite3"
	verbosity = ""
	knowbase  = "knowbase"
	model     = None
	inmem     = False
	showstats = False
	
	global pretty
	global dont_report_fails
	global print_time
	global profile
	global profilefound
	global h

	# Process options
	for option, arg in opts:
		if option == '--db':
		  dbname = arg
		elif option == '--verbose':
		  verbosity = arg
		elif option == '--knowbase':
		  knowbase = arg
		elif option == '--model':
		  model = arg
		elif option == '--inmem':
		  inmem = True
		elif option == '--pretty':
		  pretty = True
		elif option == '--time':
		  print_time = True
		elif option == '--nofail':
		  dont_report_fails = True
		elif option == '--profile':
		  if profilefound:
		  	profile = True
		elif option == '--stats':
		  showstats = True
		else:
			usage()
			sys.exit(2)

	if (not dbname):
		usage()
		sys.exit(2)

	# Display program header
	header()
	

	try:
		os.mkdir(LOGDIR)
	except Exception as e:
		pass
	

	# Open a log stream
	logger = log.Log("SAF", verbosity)
		
	# Initialize data from the databases
	if(not os.path.exists(dbname)):
		print "Database file '" + dbname + "' does not exist"
		sys.exit(2)
		
	print("Reading input event database '%s' .."%(dbname))
	evdb = eventdb.EventDatabase(dbtype, dbname, logger)
	evdb.show_minimal_stats()
	
	# Show data stats
	if(showstats):
		evdb.showstats()
		sys.exit(0)
			
	if((not dbtype)
			or (not model)):
		usage()
		sys.exit(2)


	# Create a temporary directory for storing the state database
	# The state databases are not deleted upon completion and are the 
	# responsibility of the user
	tempdir = tempfile.gettempdir() + os.path.sep + "temp"
	try:
		os.mkdir(tempdir)
		print("Creating temporary directory for storing state " + tempdir)
	except Exception as e:
		pass

	# Create a global symbol table for storing symbols from the model scripts
	# All symbols in the symbol table are stored as fully qualified variable 
	# names (FQVNs)
	print("Initializing global symbol table..")
	globalsymt = globalsym.SymbolTable(logger)
	print("Reading and initializing from the knowledge base '%s'.."%\
			(knowbase))
	globalsymt.build_nsmap(knowbase)
	globalsymt.display_nsmap()

	# Parse the language EBNF
	ebnf = open(LANGUAGE_EBNF_FILE).read()
	parser = Parser(ebnf)

	try:
		print("Parsing specified model : '%s'.."% (model))
		# Parse user specified model and build corresponding behavior trees
		fileparser = bparser.ScriptParser(logger, knowbase, model,
									  globalsymt, parser, evdb)
		tree = fileparser.parse()
		
		modelattrs = fileparser.get_modelattrhash()
		globalsymt.display()

		if __debug__: 
			logger.info("Final Behavior Tree:\n"+str(tree))

		# Apply model over data 
		if profile:	
			profilefile = LOGDIR + os.path.sep + utils.get_filename_with_time(prefix="p_", suffix=".prof")
			cProfile.runctx(\
			'apply_models(logger, evdb, tree,tempdir, globalsymt, inmem, modelattrs)',
				globals(),
				locals(),
				profilefile)
			p = pstats.Stats(profilefile)
			p.strip_dirs().\
						sort_stats('time' , 'cumulative', 'calls').\
						print_stats(50)

		else:
			apply_models(logger, evdb, tree,tempdir, globalsymt, inmem, modelattrs)
		
		if __debug__:
			logger.info("Event cache state  Hit Count: %s Miss Count: %s" %\
					 (evdb.get_cache_stats()))
			logger.info("Event database stats: %s " % (evdb.get_stats()))
	except SyntaxError as e:
		t = """Syntax Error: Expected : %(expected)s Got : %(text)s"""
		print pse.messageFormat(template=t)
	except ParserSyntaxError as pse:
		t = """Syntax Error: Expected : %(expected)s Got : %(text)s"""
		print pse.messageFormat(template=t)
	except Exception as ex:
		print "ERROR: %s" % (ex)
		if __debug__:
			traceback.print_exc()
	finally:
		cleanup(logger, tempdir)


def apply_models(logger, evdb, tree, tempdir, globalsymt, inmem, modelattrs):
	"""
		Applies models over data
	"""

	# Initialization of StateManager, DataManager,  ModelProcessor
	# and Presentation modules
	icache = {}
	statehandle = StateManager(logger, inmem, tempdir, globalsymt);
	datahandle	= DataManager(logger, evdb, globalsymt)	
	mp = processmodel.ModelProcessor(logger, datahandle, statehandle, 
									globalsymt, icache)
	output = DisplayTextSummary(datahandle, statehandle)
	
	stime = time.time()
	binstances = []
	
	modellist = tree.get_behaviors()	
	for model in modellist:
		modelname = model.get_name()
		attrlist = modelattrs[modelname]
		if __debug__:
			logger.info("Model attributes for :" + str(model) + "\n\t"+str(attrlist))
		try:
			print("Processing model %s " % (modelname))
			binstances = mp.get_instances_satisfying_model(model, evdb)
			if (len(binstances) == 0):
				if(not dont_report_fails):
					print "NO instances found satisfying model %s\n" %(modelname)
			utils.lprint(0, "Model %s satisfied by %d instances" %\
                         (modelname, len(binstances)))
			output.display_summary(modelname, 
									model, pretty, binstances,attrlist);
			
			if(hpyfound and showheap):
				print h.heap()
				print h.iso(binstances)								
		except ModelProcessingError:
			if(not dont_report_fails):
				print "Failure while processing model %s!" % (model)
			pass
		if __debug__:
			logger.info("State Database stats : %s " % (statehandle.get_stats()))
	if(print_time):
		etime = time.time()
		print "Timing Results"
		print "=============="
		print "%-10s = %-10d\n%-10s = %d\n%-10s = %10s" %\
		 ("Data Size", evdb.get_data_size(), 
		  "Instances", len(binstances), 
		  "Time Taken", etime - stime)

def header():
	print """
#############################################
#    Semantic Analysis Framework - v%s    #
#############################################
""" % (VERSION)

def usage():
	header()
	profileopt = "--profile   Collect profile information" if profilefound else ""
	print """
./saf.py --db <dbname>  --model  <name> [optional args]
	
Optional Arguments
==================
	[--knowbase <knowledgebase dir> (default: ./knowbase)]
	[--inmem ]
	[--profile]
	[--pretty]
	[--nofail]
	[--verbose {debug|state|info|critical|error|state|fine|behavior}]

Description
===========	
--inmem     Creates the temp database in memory
--showmdata Prints statistics about the events in the database
--pretty    Prints Pretty Tabular Output
--nofail    Dont show failures
--time      Print timing info for performance
--stats 	Show statistics of input data
%s
""" % (profileopt)

def cleanup(logger, tempdir):
	if __debug__: 
		logger.debug("Removing temporary state directory %s" %(tempdir))
	shutil.rmtree(tempdir, ignore_errors=True)

if __name__ == '__main__':
	(status, sqlitever) = commands.getstatusoutput("sqlite3 -version")
	pythonverstr = ".".join(["%s" % el for el in sys.version_info[0:3]])
	#if __debug__:
	#print "Detected Python %s, SQLite %s" %(pythonverstr, sqlitever)
	if sys.version_info < (2, 6):		
		raise "SAF requires Python 2.6 or greater!"
	if(not sqlitever):
		raise "SAF requires SQLite 3.6 or greater!"
	main()




