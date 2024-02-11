# sqlutils.py - Class for managing event database
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


def attrhash_to_sql(kvhash, statename, globalsyms=None, fullobjname=None):
    expr = []
    
    for k, v in kvhash.items():
        # A wildcard * is replaced with a "GLOB *" in SQL Query
        if((type(v) is str) and 
           (globalsyms.symtype(v) == globalsyms.get_code_any())):
            expr.append(k)
            expr.append("GLOB")
            newv = v        

            # Check if the wildcarded expression is preceded by 
            # the relational op != and replace it with the
            # SQL keyword "NOT"             
            if(globalsyms and fullobjname):
                op = globalsyms.get_symbol(None, 
                                    None, 
                                    fullname=fullobjname + "." + k + "_op")
                if op == "!=":
                    expr.append("NOT")                 

        else:           
            newv = v
            op = "="
            newk = "%s.%s" %(statename, k)
            
            if(globalsyms.symtype(newv) != globalsyms.get_code_const()):
                if(globalsyms.has_symbol(newk)):
                    newv = globalsyms.get_symbol(statename, k)
                    if(newv == None):
                        raise Exception("UNEXPECTED: Value None for symbol " + \
                                 statename + "." + k)
                    if(newv == ''):
                        # $1 $2 variables
                        op = ""
                        k = "1=1"
                else:
                    raise Exception("Unrecognized attributes %s" %\
                                     (statename + "." + k))
            
            expr.append(k)

            if(globalsyms and fullobjname):
                op = globalsyms.get_symbol(None, 
                                    None, 
                                    fullname=fullobjname + "." + k + "_op")
                if(not op):
                    op = "="
                    
            if(k != "1=1"):
                expr.append(op)
            
        if(newv):
            newv = str(newv)
            if ((newv.startswith("'") and newv.endswith("'")) or\
                (newv.startswith("\"") and newv.endswith("\""))):
                expr.append(newv)
            else:
                expr.append("'%s'" %(newv))
                
        expr.append("and")
    
    # Remove the extra 'and' from the back of the list
    if(expr):
        expr.pop()
    sqlform = " ".join(expr)
    return (sqlform)
