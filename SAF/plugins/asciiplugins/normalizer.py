#!/usr/bin/python
#normalizer.py : The main interface to normalize datas
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
import os
import getopt

from plugin_base import BasicPlugin
from normalizerclass import Normalizer
VERSION = '0.1a'

def main():
    logfile =  '/var/log/syslog'
    outdb   = 'test.sqlite'
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   'i:,o:,p:,s:,a:,v,x:,l',
                                  ['input=', 
                                   'output=', 
                                   'ptype=',
                                   'set=', 
                                   'attrs=',
                                   'xattrs=',
                                   'verbose',
                                   'list'])
    except getopt.error, msg:
        usage()
        sys.exit(2)

    # Set defaults for the command-line options
    input    = None
    output   = "default.sqlite"
    ptype    = None
    set      = None
    attrs    = None
    xattrs   = None
    debug    = False
    listplugins = False
    # Process options
    for option, arg in opts:
        if option in ('--input', '-i'):
          input = arg
        elif option in ('--output', '-o'):
          output = arg
        elif option in ('--ptype', '-p'):
          ptype = arg
        elif option in ('--set', '-s'):
          set = arg
        elif option in ('--attrs', '-a'):
          attrs = arg
        elif option in ('--xattrs', '-x'):
          xattrs = arg
        elif option in ('--verbose', '-v'):
          debug = True
        elif option in ('--list', '-l'):
          listplugins = True
        else:
            usage()
            sys.exit(2)
            
    if listplugins:
        opt = 'list'
        if(ptype):
            opt = ptype
        list_plugin_types(opt)
        sys.exit(2)

    # Display program header
    header()
       
    if(ptype =='basic' and attrs == None):
        print "\nERROR: Attributes must be specified using -a option when ptype = basic!"
        sys.exit(2)
            
    
    if ((not input) or (not ptype)):
        print "Input file (-i) and plugin type (-p) are mandatory arguments!\n"
        usage()
        sys.exit(2)
    
    if(xattrs and attrs):
        print "Only one of --xattrs (-x) or --attrs (-a) can be specified!\n"
        usage()
        sys.exit()

        
    if(not os.path.exists(input)):
        print "ERROR: Input '%s' does not exist" % (input)
        sys.exit(2)
        
    print "Input file: %s" %(input)

    if(os.path.exists(output)):
        print "WARNING: Output file '%s' exists!" % (output)
    else:
        print "Output file: %s" %(output)

   
    pluginclass = get_plugin_class(ptype)  
    plugin = pluginclass(attrs)
    n = Normalizer(input, output, plugin, debug, set, attrs,xattrs)
    n.run(plugin.get_processor())
    print "\n+=============+"
    print "| Statistics  |"
    print "+=============+"
    for k,v in n.get_stats().items():
        print "%-20s : %s" %(k,v) 
    

def get_plugin_class(ptype):
      
    # FIXME: There should be a better way to register the plugins 
    if(ptype == 'basic'):
        mod = __import__('plugin_base', globals(), locals(), ['BasicPlugin'])
        pluginclass = getattr(mod, 'BasicPlugin')
    elif(ptype == 'syslog'):
        mod = __import__('plugin_syslog', globals(), locals(), ['SyslogPlugin'])
        pluginclass = getattr(mod, 'SyslogPlugin')
    elif(ptype == 'apache'):
        mod = __import__('plugin_apache', globals(), locals(), ['ApachePlugin'])
        pluginclass = getattr(mod, 'ApachePlugin')
    elif(ptype == 'mysql'):
        mod = __import__('plugin_mysql', globals(), locals(), ['MySqlPlugin'])
        pluginclass = getattr(mod, 'MySqlPlugin')
    elif(ptype == 'bind'):
        mod = __import__('plugin_bindquery', globals(), locals(), ['BindQueryPlugin'])
        pluginclass = getattr(mod, 'BindQueryPlugin')
    elif(ptype == 'argus'):
        mod = __import__('plugin_argus', globals(), locals(), ['ArgusPlugin'])
        pluginclass = getattr(mod, 'ArgusPlugin')
    else:
        print "Plugin type '%s' does not exist!" % (ptype)
        sys.exit(2)        
    return pluginclass


def header():
    print """
#############################################
#    Raw Data to Events Normalizer - v%s  #
#############################################
""" % (VERSION)

def usage():
    header()
    print """
./normalize.py -i <inputfile>  -o  <outputfile> -p <plugintype> [optional arguments]

 -i (--input)  : Raw data input file 
 -o (--output) : Output database file
 -p (--ptype)  : Plugin type (Use -l to list all available types and usage examples)

 Optional Arguments:
 ===================
 -l (--list)
                List the available plugin types. To get detailed information on 
                an plugin with usage examples use -l with -p <plugintype>.
 
 -v (--verbose) 
                If specified, normalizer outputs detailed runtime information. 
                Useful for understanding the event output being written and 
                information on parsing failure.
 
 -a (--attrs) <attr:type pairs separated by '|'>  
                 Attribute name (field name) and attribute type pairs for records 
                 in input file separated by '|'. This is useful in two situations:                 
                 (a) With -p 'basic' while parsing a generic log.
                 (b) With any other plugin type but where the data input to the plugin 
                     can vary. Note that specifying -a will override the attributes 
                     specified in the plugin so that the output will contain only
                     the attributes specified with -a.
                     (See argus plugin as an example for details)
                  
                 Format:
                    <attrname1>:<type>|<attrname2>:<type>|..
                    where <attrname> is any character string
                          <type> is the type of attribute. 
                              3 types are supported:
                                 i/int/integer : For attributes of types integer
                                 t/text        : For attributes of type string
                                 r/real        : For attributes of type float
                 
                 Ex: -a 'sipaddr:text|dipaddr:text|tos:integer|duration:float'
                
                Caveat: 
                    When specifying attributes with -a, it is important to 
                    remember that the first field of any generic record is always
                    assumed to be a timestamp field and hence it is assumed 
                    that the attributes specified with -a apply to the fields
                    subsequent to the first one. 
                    
                    In the above example, the record format expected would be
                        timestamp, sipaddr, dipaddr, tos, duration  
                
 -x (--xattrs) <attr:type pairs separated by '|'>: 
                 Extend the already specified attributes in the plugin with the 
                 additional ones specified on the command line.  
                 (See argus plugin usage as an example for details)
                 
 -s (--set)    <attr=value pairs separated by '|'>: 
                 Set constant values for specified attributes. When using the -s 
                 option, the attribute values from the input file are ignored 
                 and replaced with the specified values.
                 
                 Format:
                    <attrname1>=<value>|<attrname2>=<value>|..
                    where <attrname> is any character string
                          <value> is the constant value for the attrname 
                 
                 Ex: -s 'origin=localhost|sipaddr=10.1.1.1'     
"""

def list_plugin_types(type):
    header()
    
    if (type == 'list'):
        print simple_plugin_list()
    else:
        pluginclass = get_plugin_class(type)
        p = pluginclass()
        try:
            print p.plugin_usage()
            print basic_details()
        except AttributeError:
            print "ERROR: No usage available for plugin type '%s'!"%(type)
            
    

def simple_plugin_list():
    s = """
Valid plugin types
==================
    apache - for parsing apache combined logs
    argus  - for parsing argus flow data generated using the 'ra' tool.
    basic  - for parsing generic files where the fields are separated by tab or space. 
             (-a option is mandatory if 'basic' is specified as plugin type.) 
    bind   - for parsing bind query logs in standard format              
    mysql  - for parsing mysql server logs
    syslog - for parsing syslog files

Use the -l with -p <plugin type> to get information on a specific plugin
"""
    return s

def basic_details():
    s = """
----------------------------------------------------------------------------
Additional Information
=====================

Each plugin type parses one-or-more  records at a time in the input file in 
the format specified and outputs an event of consisting of attribute value 
pairs. By default, every event output from a plugin contain 5 
additional attributes:
    eventno       -  A unique ID for every record. This is automatically 
                     assigned by the framework but can be overridden in the 
                     plugin.
    eventtype     -  The type of event. A plugin can assign eventtypes 
                     on a per record basis or on an entire file basis.
    origin        -  Origin of the record. This is usually a hostname, an 
                     IP address or any other identifier. Its value can also 
                     be left unspecified. An easy way to set this field outside 
                     the plugin is to pass -s 'origin=<constant>' in the 
                     command line.
    timestamp     -  The timestamp in seconds in unix epoch format. Plugins 
                     are expected to convert all other formats to this format.
    timestampusec -  The microseconds component of the time. 
   

The record format expected by each plugin is the default format specified
within the plugin. But this does not restrict the plugin from parsing 
variations of the format especially with the use of -a and -x options to the 
normalizer. See 'argus' and 'basic' plugin types for examples by specifying  
'-p argus -l' or '-p basic -l' as command line options. 
----------------------------------------------------------------------------
"""
    return s


if __name__ == '__main__':
    main()
    
    
    