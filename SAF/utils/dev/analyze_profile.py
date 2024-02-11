# analyze_profile.py - Simple script to read saved profiling data
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

import cProfile
import pstats
import sys

if len(sys.argv[1:]) < 1 :
    print "Provide space separated filenames as arguments !"
    sys.exit(2)


for f in sys.argv[1:]:
    p = pstats.Stats(f)
    p.strip_dirs().sort_stats('time' , 'cumulative', 'calls').print_stats(50)
