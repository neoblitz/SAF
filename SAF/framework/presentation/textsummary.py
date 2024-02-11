# textsummary.py - Produces simple and pretty summaries
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

import framework.common.utils as utils   
from copy import copy
from framework.objects.event import Event
from framework.objects.eventgroup import EventGroup

class DisplayTextSummary:
    """
        Class to output simple and pretty textual summaries
    """
    
    DEFAULT_COLUMN_WIDTH = 16
   
    def __init__(self, dh, sh):
        self.dh = dh
        self.sh = sh
        
        self.colw = self.DEFAULT_COLUMN_WIDTH
     

    def print_event(self, inst, pretty, attrlist):
        if(not inst): 
            return
        if(pretty and len(attrlist)):
            ev = inst.get_contents()
            vallist = []
            for a in attrlist:
                vallist.append(
                           utils.get_string_to_print(str(ev.get(a, '')), 
                           self.colw-2))
            print self.fstring % \
                 (tuple([str(d).center(self.colw) for d in vallist]))
        else:
            # The comma at the end is intentional and ensures that a newline
            # does not get printed
            print inst.get_id(),

    def print_start_instance(self, l, pretty, attrlist):
        if(pretty and len(attrlist)): 
            if l.get_behavior():
                s = "Behavior: " +\
                 l.get_behavior().get_rootbehavior().get_qualifiedname() +\
                  "(%s events)" %(l.get_bcount())
                pstr =  s.center(self.llength)
                return pstr
        else:
            print "(",

    def print_end_instance(self, l, pretty, attrlist):
        if(pretty and len(attrlist)): 
            if l.get_behavior():
                # Dont print behaviors
                pass
        else:
            print ")",
    
    
    def print_instance(self, inst, pretty, attrlist):
        if(isinstance(inst,Event)):
#            annote = self.print_start_instance(inst, pretty, attrlist)
#            if (self.annotation_printed.get(annote,0) == 0):
#                #s = "Behavior: " + inst.get_behavior().get_rootbehavior().get_qualifiedname()
#                s = ""
#                s = s + inst.get_behavior().get_name()
#                print s.center(self.llength)
#                self.annotation_printed[annote] = \
#                                self.annotation_printed.get(annote,0) + 1
            self.print_event(inst, pretty, attrlist)
            return
        elif(isinstance(inst,EventGroup)):
            l = inst.get_contents()
            annote = self.print_start_instance(inst, pretty, attrlist)
            for bin in l:
                if((not isinstance(bin,EventGroup))):
                    if (self.annotation_printed.get(annote,0) == 0):
                        if(annote): print annote
                        self.annotation_printed[annote] = \
                                self.annotation_printed.get(annote,0) + 1
                self.print_instance(bin, pretty, attrlist)
                    
            self.print_end_instance(inst, pretty, attrlist)
            
    
    def display_summary(self, summnode, behavior, pretty, binstances, attrlist):
        self.treebehavior = behavior

        if(pretty and not len(attrlist)):
            print "\nWARNING : Pretty printing ineffective as no attributes specified with model!"
        
        tlist = self.sh.get_tablelist()
        header_line = "Instances satisfying %s" % (summnode)
        
        print 
        utils.h2(header_line)
        print("\nTotal Matching Instances: %d\n" %\
               (len(binstances)))

        self.fstrint = ""
        if pretty and len(attrlist):
            totalattrs = len(attrlist)
            flist = []
            for a in attrlist:
                flist.append(" %%%ds " % (self.colw))
                flist.append("|")
            flist.pop()
            self.fstring = "".join(flist)
            self.llength = totalattrs * (self.colw+3)

            dstring = self.fstring % (tuple([d.center(self.colw) for d in attrlist]))

            header = []
            header.append('-' * self.llength)
            header.append(dstring)
            header.append('-' * self.llength)
            print "\n".join(header)
        
        # Sort the instances based on the behavior names they match
        binstances =  sorted(binstances, key=self._get_key)
        for inst in binstances:
            self.annotation_printed = {}
            self.print_instance(inst, pretty, attrlist)
            if(pretty and len(attrlist)):
                print '-' * self.llength
            else:
                print ">>",inst.get_behavior().get_rootbehavior().get_qualifiedname()

        if(not pretty):
            print '-' * len(header_line)
            print "\n"

    def _get_key(self, inst):
        return inst.get_behavior().get_rootbehavior().get_qualifiedname()