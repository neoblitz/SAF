# resolve.py - Procedures to resolve state expressions to actual values
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
def resolve_state(logger, binst, state_record, obj, symt, callerobj, mainns=None):
    """
        Binds a state expression to actual values
    """
    data_rec = binst.get_contents();
    if(data_rec is None):
        if __debug__: 
            logger.info("NO instance provided %s" % (binst))
        return None

    if __debug__:
        logger.fine("Fetched instance %s "% (data_rec))

    state_rec = state_record.get_history()
    if state_rec == None:
        return None
    if __debug__: 
        logger.fine("Unpickled history from statedb:  %s" % (state_rec))

    state_expr = obj.get_contents()
    name       = obj.get_name()
    ns         = obj.get_namespace()
    query      = symt.get_symbol(ns, name)
    if __debug__: 
        logger.fine("Fetched hash for symbol : %s.%s : %s" % \
                       (ns, name, query))
        
    #query = queryc.copy()
    #alias = obj.get_alias() or ""
    
#    if mainns:
#        for k,v in query.items():
#            fullname = [] 
#            fullname.append(mainns)
#            fullname.append(alias)
#            fullname.append(k)
#            fn = ".".join(fullname)
#            if(symt.has_symbol(fn)):
#                newv = symt.get_symbol(None, None, 
#                                       fullname=fn)  
#                vtype = symt.symtype(newv)
#                if((vtype == symt.get_code_const()) or
#                        (vtype == symt.get_code_any())):
#                        query[k] = newv

    kvhash = {}  #kvhash contains all the attributes. 
    for k, v in query.items():
        newk = "%s.%s.%s" % (ns, name, k)
        if __debug__:
            logger.fine("Processing hash : Qualified Key = %s -> %s" \
                          % (newk, v))

        vtype = symt.symtype(v)
        if(vtype == symt.get_code_any()):
            # Put a *
            kvhash[k] = '*'
        elif(vtype == symt.get_code_const()):
            # Assign the constant as value
            kvhash[k] = v
        elif (vtype == symt.get_code_indep()):
            if(callerobj.is_state_node()):
                kvhash[k] = data_rec[k]
            elif(callerobj.is_leadsto_op()):
                kvhash[k] = '*'
        elif (vtype == symt.get_code_dep()):
            newv = v.replace('$', '')
            # Assign the corresponding value for correlated key
            # from history
            if __debug__:
                logger.fine("New Value: %s"% (newv))
            try:
                kvhash[k] = state_rec[newv]
            except:
                if newv not in state_rec:
                    # FORWARD REFERENCE 
                    # Its possible that the referenced key has 
                    # no history in the state_rec due to forward reference.
                    # In such case, treat the variable as an independent 
                    # variable and use the values from existing data record
                    try:
                        kvhash[k] = data_rec[k]
                    except:
                        if __debug__:
                            logger.info("EXCEPTION:::Forward reference case exception while processing '%s'\n\
\tkvhash = %s\n\n\tstate_rec=%s\n\n\tdata_rec=%s" %(k, kvhash, state_rec, data_rec))
                        return None
                        #sys.exit(2)

    if __debug__:
        logger.fine("Resolved state expression '%s' ==> '%s" \
                       % (state_expr, kvhash))
    return  kvhash
