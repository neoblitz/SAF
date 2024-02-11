# 
# parser.py - Parses behavior script into a state tree 
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

# Standard Library Imports
import os
import sys
from exceptions import Exception
from copy import copy

# Third Party Imports
import ConfigParser
from simpleparse.common import numbers, strings, comments
from simpleparse.parser import Parser
from simpleparse import generator
from simpleparse.dispatchprocessor import *
try:
	from collections import OrderedDict
except:
	from framework.common.dictionary import OrderedDict as OrderedDict

# Local Imports
import framework.objects.behaviortree as behaviortree
from behaviorparser import BehaviorExprParser
from modelparser import ModelExprParser
from stateparser import StateExprParser
from language import OperatorTokens, KeywordTokens, SectionTokens
from language import BconstraintTokens, OpconstraintTokens


class ScriptParser:
    """
    
    """

    def __init__(self, logger, basebehavior, filename, symt, parser, evdb):
        
        self.logger = logger
        self.globalsyms = symt
        self.simpleparser = parser
        (fn, ns, name, cn) = ScriptParser.init(basebehavior, filename)
        self.basebehavior = basebehavior
        self.filename = fn
        self.config = cn
        self.namespace = ns
        self.name = name
        if __debug__: self.logger.info("Parser initialized for file '%s'" \
                          % (self.filename));

        self.behaviortree = None
        self.statehash = {}
        self.behaviorhash = {}
        self.behaviorhash = {}
        self.fullpackagepath = ''
        self.eventdb = evdb

        self.eventlist = evdb.get_event_types()
        self.valid_attr_list = []
        for ev in self.eventlist:        
            self.valid_attr_list.extend(evdb.get_attribute_names(ev))

    @staticmethod
    def init(basebehavior, filename):

        fn = filename
        # If the filename does not have the basebehavior
        # prepend the basebehavior

        if(not os.path.exists(fn)):
            print  "Error: Filename '", fn, "' does not exist ! Aborting !!"
            sys.exit(2)

        #sys.stderr.write("Reading '" + fn + "'..\n");

        # Passing ordered dictionary makes sure that we get the lines
        # in order they were entered in the file.
        config = ConfigParser.SafeConfigParser(dict_type=\
                                                OrderedDict)

        # The following option is important to prevent configparser 
        # from converting everything to lowercase
        config.optionxform = str
        config.read(fn)

        # Read the header and initialize the name, namespace
        headertokens = config.items(SectionTokens.SECTION_HEADER)
        ns = None
        name = None
        for token, value in headertokens:
            if token.upper() == KeywordTokens.KEYWORD_NAMESPACE:
                ns = value
            if token.upper() == KeywordTokens.KEYWORD_NAME:
                name = value
        return (fn, ns, name, config)


    def get_namespace(self):
        return self.namespace

    def get_modelattrhash(self):
        return self.modelattrs

    def parse(self):
        self.parse_header(SectionTokens.SECTION_HEADER)
        self.parse_states(SectionTokens.SECTION_STATES)
        self.parse_behavior(SectionTokens.SECTION_BEHAVIOR)
        self.parse_model(SectionTokens.SECTION_MODEL)
        return self.behaviortree

    def parse_header(self, keyword):
        headertokens = self.config.items(keyword)
        if __debug__: 
            self.logger.debug("Parsing HEADER")

        for token, value in headertokens:
            if __debug__: 
                self.logger.debug("Parsing : %s %s " % (token, value))
            
            if token.upper() == KeywordTokens.KEYWORD_NAME:
                if(self.behaviortree is None):
                    self.behaviortree = behaviortree.BehaviorTree(value)
                    if __debug__: 
                        self.logger.info ("\tCreated new state tree:%s" \
                                       % (value))
                    self.name = value
                else:
                    raise Exception('Behavior script cannot contain two \
                                            NAME  variables')

            if token.upper() == KeywordTokens.KEYWORD_INIT:
                if __debug__: 
                    self.logger.info ("\t Added QUALIFIER : " + value)
                
                varhash = {}
                etypelist = []
                behavior = self.behaviortree.get_newbehavior(token.upper())
                behavior.set_rootbehavior(self.behaviortree)
                self.behaviorhash[KeywordTokens.KEYWORD_INIT] = value
                self.behaviorhash[KeywordTokens.KEYWORD_INIT] = behavior
                options = { 'symt': self.globalsyms,
                            'vh': varhash,
                            'token':token.upper(),
                            'ns': self.namespace,
                            'name':self.name,
                            'validattrs': self.valid_attr_list,
                            'etypelist': etypelist}
 
 
                success, children, nextcharacter = self.simpleparser.parse(value,
                            production="behavior_decl",
                            processor=BehaviorExprParser(self.logger,
                                                   self.behaviortree,
                                                   self.statehash,
                                                   self.behaviorhash,
                                                   self.behaviorhash,
                                                   behavior,
                                                   self.namespace+"."+self.name,
                                                   stateopts=options,
                                                   symt=self.globalsyms))
                if ((not success)): 
                    raise SyntaxError("Unable to parse %s = '%s'! Please check the syntax"%\
                                      (token, value))
                
                if __debug__: 
                    self.logger.info("Behavior %s:\n\t %s" % (token.upper(), 
                                                              behavior))
                self.globalsyms.add_symbol(token.upper(),
                                           varhash,
                                           self.namespace,
                                           self.name)

                if (len(etypelist)):
                    self.eventdb.set_active_tables(etypelist)
                else:
                    self.eventdb.set_active_tables(['*'])

            if token.upper() == KeywordTokens.KEYWORD_DEP:
                if __debug__: self.logger.info ("\n\n")
                if __debug__: self.logger.info ("Processing IMPORTS: " + value)
                self.process_imports(value)
                self.globalsyms.display()

            if token.upper() == KeywordTokens.KEYWORD_NAMESPACE:
                if __debug__: self.logger.info ("\t Namespace :" + value)
                self.namespace = value

        self.fullpackagepath = self.namespace + "." + self.name
        self.behaviortree.set_namespace(self.fullpackagepath)
        
        if KeywordTokens.KEYWORD_INIT not in self.behaviorhash:
            # Create a default QUALIFIER behavior 
            behavior = self.behaviortree.get_newbehavior(token.upper())
            self.behaviorhash[KeywordTokens.KEYWORD_INIT] = behavior


    def get_name(self):
        if(not self.name):
            headertokens = self.config.items(SectionTokens.SECTION_HEADER)
            for token, value in headertokens:
                 if token.upper() ==\
                     KeywordTokens.KEYWORD_NAME:
                     return value
        else:
            return self.name


    def get_header(self):
        return self.config.items(SectionTokens.SECTION_HEADER)


    def parse_states(self, keyword):
        statetokens = self.config.items(keyword)

        if __debug__: self.logger.debug("Parsing STATE")
        if __debug__: self.logger.debug("===========")

        for lhs, rhs in statetokens:
            self.globalsyms.display()
            if __debug__: self.logger.debug("\n\n")
            if __debug__: self.logger.debug("Parsing : " + lhs + " " + rhs)
            self.statehash[lhs] = rhs
            
            varhash = {}           
            # Parse the state expression 
            success, children, nextcharacter = self.simpleparser.parse(rhs,
                                    production="state_decl",
                                    processor=StateExprParser(self.logger,
                                                          self.globalsyms,
                                                          varhash,
                                                          lhs,
                                                          self.namespace,
                                                          self.name,
                                                          self.valid_attr_list))
            if ((not success)): 
                raise SyntaxError("Unable to parse %s! Please check the syntax"%(rhs))
            
            
            if __debug__: 
                self.logger.debug("Result of parsing state %s : %s" %\
                                  ( lhs, str(varhash)))
            
            if(not self.globalsyms.get_symbol(None, None, 
                            fullname=self.namespace+"."+self.name+"."+lhs)):
                # Cache the parsed varhash in the symboltable 
                self.globalsyms.add_symbol(lhs,
                                       varhash,
                                       self.namespace,
                                       self.name)

    def parse_behavior(self, keyword):
       """
           Parses statements specified in the [behavior] section
       """
       b_stmts = self.config.items(keyword)
       if __debug__: 
           self.logger.debug("Parsing BEHAVIOR")
       
       for b_id, b_expr in b_stmts:
            if __debug__: 
                self.logger.debug("Parsing : %s %s " % (b_id , b_expr))
            self.behaviorhash[b_id] = b_expr
            
            # Create a new behavior for the behavior declaration
            behavior = self.behaviortree.get_newbehavior(b_id)
            if __debug__: 
                self.logger.debug("\t Created New Root behavior: " + b_id)
            self.behaviorhash[b_id] = behavior
            behavior.set_rootbehavior(self.behaviortree)
            behavior.set_tree(self.behaviortree)
            
            # Add qualifier            
            qualifier = self.behaviorhash[KeywordTokens.KEYWORD_INIT]
            self.behaviortree.add_existing_behavior(self.behaviorhash[b_id],
                                                qualifier, self.namespace)
            qualifier.set_rootbehavior(self.behaviorhash[b_id])
            qualifier.set_tree(self.behaviortree)
            self.behaviortree.add_connectop(self.behaviorhash[b_id],
                                                 self.namespace)
            
            # Store the parsed behavior object (copy of) in the symbol table.
            self.globalsyms.add_symbol(b_id, 
                                       self.behaviorhash[b_id], 
                                       self.namespace, 
                                       self.name)
            
            varhash = {}
            options = { 'symt': self.globalsyms,
                       'vh': varhash,
                       'token':b_id,
                       'ns': self.namespace,
                       'name':self.name,
                       'validattrs': self.valid_attr_list}
            # Parse the behavior expression 
            success, children, nextcharacter = self.simpleparser.parse(b_expr,
                        production="behavior_decl",
                        processor=BehaviorExprParser(self.logger,
                                                     self.behaviortree,
                                                     self.statehash,
                                                     self.behaviorhash,
                                                     self.behaviorhash,
                                                     behavior,
                                                     self.fullpackagepath,
                                                     stateopts=options,
                                                     symt=self.globalsyms))
            if ((not success)): 
                raise SyntaxError("Unable to parse %s = '%s'! Please check the syntax"%\
                                      (b_id, b_expr))
            


            if __debug__: 
                self.logger.info("behavior for %s:\n\t %s" % (b_id, behavior))
            


    def parse_model(self, keyword):
       """
           Parse statements specified in the [model] section
       """
       tokens = self.config.items(keyword)
                   
       if __debug__: self.logger.debug("Parsing MODEL")
       self.modelattrs = {}
       
       for b_id, b_expr in tokens:
            self.globalsyms.add_symbol(b_id , "", self.namespace, self.name)
            
            if __debug__: 
                self.logger.info("Parsing : %s %s " % (b_id , b_expr))
            
            # Parse the attributes from the model name
            modelname = []
            attrs = []
            success, children, nextcharacter = self.simpleparser.parse(b_id,
                                    production="model_output",
                                    processor=ModelExprParser(self.logger, 
                                                             modelname,
                                                             attrs))
            if ((not success)): 
                raise SyntaxError("Unable to parse %s ! Please check the syntax"%\
                                      (bid))
            self.behaviorhash[modelname[0]] = b_expr
            self.modelattrs[modelname[0]] = attrs
            b_id = modelname[0]
            self.globalsyms.add_symbol(b_id + "_attrs", 
                                       self.modelattrs, 
                                       self.namespace, 
                                       self.name)
            
            # Create a new behavior for the behavior declaration
            behavior = self.behaviortree.get_newbehavior(b_id)
            if __debug__: 
                self.logger.debug("\t Created New Root behavior: " + b_id)
            self.behaviorhash[b_id] = behavior
            behavior.set_rootbehavior(self.behaviortree)
            behavior.set_tree(self.behaviortree)

            
            # Store the parsed behavior object in the symbol table.
            self.globalsyms.add_symbol(b_id, 
                                       self.behaviorhash[b_id], 
                                       self.namespace, 
                                       self.name)
            
            
            # Parse the behavior expression 
            varhash = {}
            options = { 'symt': self.globalsyms,
                       'vh': varhash,
                       'token':b_id,
                       'ns': self.namespace,
                       'name':self.name,
                       'validattrs': self.valid_attr_list}
            success, children, nextcharacter = self.simpleparser.parse(b_expr,
                                    production="behavior_decl",
                                    processor=BehaviorExprParser(self.logger,
                                                          self.behaviortree,
                                                          self.statehash,
                                                          self.behaviorhash,
                                                          self.behaviorhash,
                                                          behavior,
                                                          self.fullpackagepath,
                                                          stateopts=options,
                                                          model=True,
                                                          symt=self.globalsyms))
            if ((not success)): 
                raise SyntaxError("Unable to parse %s = '%s'! Please check the syntax"%\
                                      (b_id, b_expr))
                                    
            if __debug__: 
                self.logger.info("behavior for %s:\n\t %s" % (b_id, behavior))
            
            self.behaviortree.add_behavior(self.behaviorhash[b_id])       
       
    def process_imports(self, imports):
        
        implist = imports.split(",")

        for imp in implist:
            imp = imp.strip()
            if(not self.globalsyms.is_import_processed(imp)):
                f = self.globalsyms.get_filename_from_ns(imp)
                if(f is None):
                    raise\
                    Exception("Invalid import '%s' found while processing %s"\
                                % (imp, self.filename))
                else:
                    fileparser = ScriptParser(self.logger,
                                              self.basebehavior,
                                              f,
                                              self.globalsyms,
                                              self.simpleparser,
                                              self.eventdb)
                    fileparser.parse()

