# 
# constraints.py - Generic class for representing constraints
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

class ConstraintObject:
    """ Generic Class for Constraints """
    def __init__(self, behaviorname, clist):
        self.constraints = {}
        self.behaviorname = behaviorname
        self.valid_constraints = clist
        # The default attribute makes sure that only constraint 
        # is associated for now. Will change this when the semantics of
        # multiple constraints are worked out 
        self.default = None
        
        # Flag to control if constraints should be applied or only checked for
        self.apply_flag = False

    def set_constraint(self, key, op, val, qual=None):
        if(key not in self.valid_constraints):
            raise SyntaxError("Unrecognized keyword '%s'"%(key))
        self.constraints[key] = (op, val, qual)
        self.default = key

    def set_apply_flag(self, flag):
        self.apply_flag = True 
        
    def get_apply_flag(self):
        return self.apply_flag

    def get_active_constraints(self):
        return self.constraints.keys()
    
    def has_constraint(self):
        if(self.default == None):
            return False
        else:
            return True

    def get_constraint(self, key=None):
        k = key or self.default
        (op, cval, cqual) = \
                self.constraints.get(k, (None, None, None))
        return (k, op, cval, cqual)

    def __repr__(self):
        l = ['[']
        for key, val in self.constraints.items():
            l.append(key)
            for v in val:
                if v: l.append(str(v))
        l.append(']')
        return " ".join(l)