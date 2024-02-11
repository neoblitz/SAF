# utils.py - Common functions which do not have any other place to go
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
import re
import commands
import os, sys
import subprocess
import random
import string
import time
import cPickle
import base64
import datetime
import psutil

# Credits for this 
# http://www.daniweb.com/code/snippet216610.html
def print_timing(func):
    def wrapper(*arg):
        t1 = time.time()
        res = func(*arg)
        t2 = time.time()
        print '%s took %0.3f ms' % (func.func_name, (t2 - t1) * 1000.0)
        return res
    return wrapper


def getcontrolip(node):
    """
        Returns the controlip of the node
    """

    # Get the user who created the experiment from the emulab files
    file = open('/var/emulab/boot/creator', 'r')
    username = file.readline().strip()
    file.close()

    ssh_cmd = 'sudo -u ' + username
    ssh_cmd += ' /usr/bin/ssh -q -o StrictHostKeyChecking=no ' + node
    ssh_cmd += ' sudo cat /var/emulab/boot/myip'
    status, output = commands.getstatusoutput(ssh_cmd)
    return status, output

"""
    Opens any file in a system independent way
    http://stackoverflow.com/questions/1679798/how-to-open-a-file-\
    with-the-standard-application
"""
def openfile(file):
    if sys.platform == 'linux2':
        subprocess.call(["xdg-open", file])
    else:
        os.startfile(file)

def get_randstring(size):
    d = [random.choice(string.letters) for x in xrange(size)]
    tempname = "".join(d)
    return tempname

"""
Adapted from http://stackoverflow.com/questions/766335/python-speed-testing-\
time-difference-milliseconds
"""
def get_timediff(t1, t2):
    """ Returns the timedifference between two time tuples (t2-t1) where 
        each tuple has seconds, microseconds
    """
    (s1, ms1) = t1
    (s2, ms2) = t2

    # Convert the time values to their float representation taking care 
    # to preprend the microseconds value with necessary 0's.
    time1 = float(str(s1) + "." + str(ms1).zfill(6))
    time2 = float(str(s2) + "." + str(ms2).zfill(6))

    return (datetime.datetime.fromtimestamp(time2) -
             datetime.datetime.fromtimestamp(time1))


def marshal(obj):
     return base64.b64encode(cPickle.dumps(obj, cPickle.HIGHEST_PROTOCOL))


def unmarshal(b64text):
     return cPickle.loads(base64.b64decode(b64text))


def get_index(self, a, x):
    'Locate the leftmost value exactly equal to x'
    i = bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return i
    raise ValueError


def isfatal(status, output):
   """
        Checks if the output of a command did not succeed
   """
   p = re.compile('not found', re.IGNORECASE);
   if p.search(output):
      return True
   else:
      return False

def unique(a):
    """ 
        Returns the list with duplicate elements removed 
    """
    return list(set(a))

def intersect(a, b):
    """ 
        Returns the intersection of two lists 
    """
    return list(set(a) & set(b))

def union(a, b):
    """ 
        Returns the union of two lists 
    """
    return list(set(a) | set(b))


def get_available_memory():
    return psutil.avail_phymem()


def get_filename_with_time(prefix = None, suffix = None):
    filename = (prefix or "") 
    currdatetime = time.asctime(time.gmtime(time.time()))
    currdatetime = currdatetime.replace(':','_')
    currdatetime = currdatetime.replace(' ','-')
    filename += currdatetime + (suffix or "")
    return filename

def get_string_to_print(data, maxcols):
    toprint = (data[:maxcols] + '..') if len(data) > maxcols else data
    return toprint

def lprint(level, msg, nl=True):
    tabstop = "  "
    tolog = tabstop * level +  str(msg) 
    if nl:
        print tolog
    else:
        print tolog,

def h1(msg):
    mlen = len(msg) + 2
    char = '#'
    printstr = char * mlen + '\n' + char + msg + '\n' + char * mlen
    print printstr


def h2(msg):
    mlen = len(msg) 
    char = '='
    printstr = char * mlen + '\n' +  msg + '\n' + char * mlen
    print printstr

def h3(msg):
    mlen = len(msg) + 2
    char = '-'
    printstr = char * mlen + '\n' + msg + '\n' + char * mlen
    print printstr
