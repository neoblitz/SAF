# 
# behaviortree.py - Class for creating and manipulating behavior tree
#                   Behavior trees are in-memory representations  
#                   of model scripts.
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

import random
from exceptions import Exception
from constraints import ConstraintObject
from framework.parser.language import OperatorTokens, KeywordTokens, SectionTokens
from framework.parser.language import BconstraintTokens, OpconstraintTokens
import framework.common.utils as utils

TreeObjectType = {
                 'STATE_NODE' : 0,
                 'SUMMARY_NODE': 1,
                 'PBEGIN_NODE' : 2,
                 'PEND_NODE' : 3,
                 'QUALIFIER_OBJ': 4,
                 'LEADSTO_OP': 5,
                 'EVENTUALLY_OP' :6,
                 'ALWAYS_OP': 7,
                 'SUMM_OP': 8,
                 'CONC_SPEC_OP': 9,
                 'CONNECT_OP': 10,
                 'BEHAVIOR': 11,
                 'AND_OP' : 12,
                 'OR_OP' : 13,
                 'XOR_OP': 14,
                 'CONC_OLAP_OP': 15,
                 'CONC_EW_OP': 16,
                 'CONC_SW_OP': 17,
                 'CONC_DUR_OP': 18,
                 'CONC_EQ_OP': 19,
                 'RECURSION_NODE' : 20
                }

class BehaviorTree:
    def __init__(self, name, ns=None):
        self.name = name
        self.namespace = ns
        self.behaviorlist = []

    def set_namespace(self, ns):
        self.namespace = ns
        
    def get_namespace(self):
        return self.namespace

    def add_initnode(self, state, behavior, ns):
        sobj = BehaviorTreeObject("QUALIFIER_OBJ", 
                                  KeywordTokens.KEYWORD_INIT, ns, state)
        behavior.add_obj(sobj)
        sobj.set_behaviorname(behavior.get_name())
        sobj.set_tree(self)
        return sobj

    def add_causalop(self, behavior, ns):
        name = "LEADSTO_OP_"+utils.get_randstring(10)
        sobj = BehaviorTreeObject("LEADSTO_OP" , name, ns, "~>")
        behavior.add_obj(sobj)
        sobj.set_behaviorname(behavior.get_name())
        sobj.set_parent(behavior)
        sobj.set_tree(self)
        return sobj

    def add_alwaysop(self, behavior, ns):
        name = "ALWAYS_OP_"+utils.get_randstring(10)
        sobj = BehaviorTreeObject("ALWAYS_OP" , name, ns, "[]")
        behavior.add_obj(sobj)
        sobj.set_behaviorname(behavior.get_name())
        sobj.set_parent(behavior)
        sobj.set_tree(self)
        return sobj

    def add_andop(self, behavior, ns):
        name = "AND_OP_"+utils.get_randstring(10)
        sobj = BehaviorTreeObject("LOG_AND_OP" , name, ns, "and")
        behavior.add_obj(sobj)
        sobj.set_behaviorname(behavior.get_name())
        sobj.set_parent(behavior)
        sobj.set_tree(self)
        return sobj

    def add_orop(self, behavior, ns):
        name = "OR_OP_"+utils.get_randstring(10)
        sobj = BehaviorTreeObject("LOG_OR_OP" , name, ns, "or")
        behavior.add_obj(sobj)
        sobj.set_behaviorname(behavior.get_name())
        sobj.set_parent(behavior)
        sobj.set_tree(self)
        return sobj
    
    def add_xorop(self, behavior, ns):
        name = "XOR_OP_"+utils.get_randstring(10)
        sobj = BehaviorTreeObject("LOG_XOR_OP" , name, ns, "xor")
        behavior.add_obj(sobj)
        sobj.set_behaviorname(behavior.get_name())
        sobj.set_parent(behavior)
        sobj.set_tree(self)
        return sobj
    
    def add_notop(self, behavior, ns):
        name = "NOT_OP_"+utils.get_randstring(10)
        sobj = BehaviorTreeObject("LOG_NOT_OP" , name, ns, "not")
        behavior.add_obj(sobj)
        sobj.set_behaviorname(behavior.get_name())
        sobj.set_parent(behavior)
        sobj.set_tree(self)
        return sobj

    def add_overlapop(self, behavior, ns):
        name = "OLAP_OP_"+utils.get_randstring(10)
        sobj = BehaviorTreeObject("CONC_OLAP_OP" , name, ns, "olap")
        behavior.add_obj(sobj)
        sobj.set_behaviorname(behavior.get_name())
        sobj.set_parent(behavior)
        sobj.set_tree(self)
        return sobj

    def add_swop(self, behavior, ns):
        name = "SW_OP_"+utils.get_randstring(10)
        sobj = BehaviorTreeObject("CONC_SW_OP" , name, ns, "sw")
        behavior.add_obj(sobj)
        sobj.set_behaviorname(behavior.get_name())
        sobj.set_parent(behavior)
        sobj.set_tree(self)
        return sobj

    def add_ewop(self, behavior, ns):
        name = "EW_OP_"+utils.get_randstring(10)
        sobj = BehaviorTreeObject("CONC_EW_OP" , name, ns, "ew")        
        behavior.add_obj(sobj)
        sobj.set_behaviorname(behavior.get_name())
        sobj.set_parent(behavior)
        sobj.set_tree(self)
        return sobj

    def add_durop(self, behavior, ns):
        name = "DUR_OP_"+utils.get_randstring(10)
        sobj = BehaviorTreeObject("CONC_DUR_OP" , name, ns, "dur")        
        behavior.add_obj(sobj)
        sobj.set_behaviorname(behavior.get_name())
        sobj.set_parent(behavior)
        sobj.set_tree(self)
        return sobj

    def add_eqop(self, behavior, ns):
        name = "EQ_OP_"+utils.get_randstring(10)
        sobj = BehaviorTreeObject("CONC_EQ_OP" , name, ns, "eq")        
        behavior.add_obj(sobj)
        sobj.set_behaviorname(behavior.get_name())
        sobj.set_parent(behavior)
        sobj.set_tree(self)
        return sobj

    def add_summop(self, name, behavior, ns):
        name = "SUMM_OP_"+utils.get_randstring(10)
        sobj = BehaviorTreeObject("SUMM_OP" , name, ns, ">>")
        behavior.add_obj(sobj)
        sobj.set_behaviorname(behavior.get_name())
        sobj.set_parent(behavior)
        sobj.set_tree(self)
        return sobj

    def add_connectop(self, behavior, ns):
        name = "CONNECT_OP_"+utils.get_randstring(10)
        sobj = BehaviorTreeObject("CONNECT_OP" , name, ns, "")
        behavior.add_obj(sobj)
        sobj.set_behaviorname(behavior.get_name())
        sobj.set_parent(behavior)
        sobj.set_tree(self)
        return sobj

    def add_statenode(self, name, state, behavior, ns):
        sobj = BehaviorTreeObject("STATE_NODE" , name , ns, state)
        behavior.add_obj(sobj)
        sobj.set_behaviorname(behavior.get_name())
        sobj.set_parent(behavior)
        sobj.set_tree(self)
        return sobj

    def add_summnode(self, name, behavior, ns):
        sobj = BehaviorTreeObject("SUMMARY_NODE" , name, ns)
        behavior.add_obj(sobj)
        sobj.set_behaviorname(behavior.get_name())
        sobj.set_parent(behavior)
        sobj.set_tree(self)
        return sobj

    def add_behaviornode(self, behavior, ns):
        newbehavior = self.get_newbehavior()
        sobj = BehaviorTreeObject("BEHAVIOR" , newbehavior.get_name(), ns, newbehavior)
        behavior.add_obj(sobj)
        sobj.set_behaviorname(behavior.get_name())
        sobj.set_parent(behavior)
        sobj.set_tree(self)
        return newbehavior

    def add_recursionnode(self, behavior, ns, object):
        name = "RECURSION_"+utils.get_randstring(10)
        sobj = BehaviorTreeObject("RECURSION_NODE" , name , ns, contents=object)
        behavior.add_obj(sobj)
        sobj.set_behaviorname(behavior.get_name())
        sobj.set_parent(behavior)
        sobj.set_tree(self)
        return sobj

    def add_existing_behavior(self, behavior, existing_behavior, ns):
        """
            Adds an existing behavior object as an object in another behavior
        """
        sobj = BehaviorTreeObject("BEHAVIOR" , 
                                  existing_behavior.get_name(), 
                                  ns, 
                                  existing_behavior)
        behavior.add_obj(sobj)
        sobj.set_tree(self)
        
    def update_namespaces(self, behavior, newns):
        """
            Recursively updates namespaces for all objects in a behavior
        """
        objlist = behavior.get_objects()
        for obj in objlist:
            if obj.is_behavior_object():
                self.update_namespaces(obj.get_contents(), newns)
            else:
                obj.set_namespace(newns)
                
    def get_name(self):
        return self.name

    def get_newbehavior(self, behaviorname=None):
        sbehavior = Behavior(self.name, behaviorname)
        return sbehavior

    def get_behaviors(self):
        return self.behaviorlist

    def get_behavior_byname(self, name):
        for p in self.behaviorlist:
            if(p.get_name() == name):
                return p
        return None

    def add_behavior(self, behavior):
        if behavior is not None:
            self.behaviorlist.append(behavior)
        else:
            raise Exception("behaviorname cannot be Empty !")

    def __repr__(self):
        pstr = []
        for p in self.behaviorlist:
            pstr.append("%s" % (p))
        return ("\n"+"\n".join(pstr)+"\n")

class BehaviorTreeBehaviorConstraints(ConstraintObject):
    """ Represents behavior constraints"""   
    def __init__(self, behaviorname):
        ConstraintObject.__init__(self, behaviorname, BconstraintTokens.CONSTRAINTS)


class BehaviorTreeOpConstraints(ConstraintObject):
    """ Represents Operator constraints"""

    def __init__(self, behaviorname):
        ConstraintObject.__init__(self, behaviorname,  OpconstraintTokens.CONSTRAINTS)


class Behavior:
    """ Represents behavior """
    
    def __init__(self, parentname, name=None):
        self.parentname = parentname
        self.constraints = None
        if(name is None):
            self.behaviorname = "p" + str(random.randint(1, 1000000))
            self.anonbehavior = True
        else:
            self.behaviorname = name
            self.anonbehavior = False
        self.objlist = []
        self.count = 0
        self.instance_list = []
        self.isnegated = False
        self.rootbehavior= None
        self.tree = None
        self.alias = ''

    def set_alias(self, alias):
        self.alias = alias
        for obj in self.objlist:
            obj.set_alias(alias)

    def get_alias(self):
        return self.alias
            
    def get_tree(self):
        return self.tree

    def set_tree(self, tree):
        self.tree = tree

    def add_instances(self, inlist):
        self.instance_list.extend(inlist)

    def get_instances(self):
        return self.instance_list

    def set_negation(self, bool):
        self.isnegated = bool

    def set_rootbehavior(self, root):
        self.rootbehavior = root

    def get_rootbehavior(self):
        return self.rootbehavior

    def add_obj (self, sobj):
        self.objlist.append(sobj)

    def get_name (self):
        return self.behaviorname

    def get_parent (self):
        return self.parentname

    def get_qualifiedname(self):
        return self.rootbehavior.get_name() +"."+ self.behaviorname

    def get_objects(self):
        return self.objlist

    def get_summary_node(self):
        return self.objlist[len(self.objlist) - 1].get_name()

    def set_behavior_constraints(self, constraints):
        self.constraints = constraints

    def get_behavior_constraints(self):
        return self.constraints

    def get_negation(self):
        return self.isnegated

    def is_behavior_anon(self):
        return self.anonbehavior

    def __repr__(self):
        dispelems = []
        for obj in self.objlist:
            if(obj.is_state_node()):
                dispelems.append(obj.get_name())
                dispelems.append("("+obj.get_alias()+")")
            elif(obj.is_behavior_object()):
                dispelems.append('[-');
                dispelems.append(str(obj.get_contents()));
                dispelems.append('-]');
                dispelems.append("("+obj.get_alias()+")")
                const = obj.get_contents().get_behavior_constraints()
                if(const != None):
                    dispelems.append(str(const));
            elif(obj.is_type_op()):
                dispelems.append(obj.get_contents());
                const = obj.get_constraints()
                if(const != None):
                    dispelems.append(str(const));
            else:
                dispelems.append(obj.get_name());

        return " ".join(dispelems)
    
    def details(self):
        return self.get_name()

class BehaviorTreeObject:
    
    def __init__(self, type, name, ns, contents=None, parent=None):
        self.objecttype = type
        self.name = name
        self.namespace = ns
        self.objptrs = []
        # 'contents' is very generic and can point to any datastructure 
        self.contents = contents
        self.behaviorname = None
        self.isnegated = False
        self.instance_list = None
        self.constraints = None
        self.parentbehavior = parent
        self.rootbehavior = None
        self.tree = None
        # Pointer to instances matching this state object
        self.instances = None
        # Pointer to dependent state object
        self.dependent_state = None
        self.alias = ''

    def set_alias(self, alias):
        self.alias = alias
        if(self.is_behavior_object()):
            objlist = self.get_contents().get_objects()
            for obj in objlist:
                obj.set_alias(alias)
        else:
            self.alias = alias
    
    def get_alias(self):
        return self.alias
    
    def get_name(self):
        return self.name

    def get_type(self):
        return self.objecttype

    def get_fullname(self):
        return ".".join([self.namespace, self.name]) 

    def get_namespace(self):
        return self.namespace
    
    def set_namespace(self, ns):
        self.namespace = ns

    def add_instances(self, inlist):
        if (not self.instance_list):
            self.instance_list = inlist
        else:
            if(self.instance_list != inlist):
                self.instance_list.extend(inlist)

    def get_instances(self):
        return self.instance_list

    def set_constraints(self, constraints):
        self.constraints = constraints

    def get_constraints(self):
        return self.constraints

    def set_negation(self, bool):
        self.isnegated = bool

    def set_behaviorname(self, pname):
        self.behaviorname = pname

    def get_behaviorname(self):
        return self.behaviorname

    def set_rootbehavior(self, root):
        self.rootbehavior = root

    def get_rootbehavior(self):
        return self.rootbehavior

    def get_parent(self):
        return self.parentbehavior

    def set_parent(self, parent):
        self.parentbehavior = parent
        
    def get_tree(self):
        return self.tree

    def set_tree(self, tree):
        self.tree = tree
    
    def get_negation(self):
        return self.isnegated

    def is_name_anon(self):
        if(self.name.find("anonstate_") >= 0):
            return True
        return False

    def is_type_node(self):
        if(self.get_type().find("NODE") > 0):
            return True
        return False

    def is_type_recursion(self):
        if(self.get_type().find("RECURSION") >= 0):
            return True
        return False

    def is_type_op(self):
        if(self.get_type().find("OP") > 0):
            return True
        return False

    def is_qualifier(self):
        if(self.get_name() == "QUALIFIER"):
            return True
        return False

    def is_state_node(self):
        if(self.get_type() == "STATE_NODE"):
            return True
        return False

    def is_summ_node(self):
        if(self.get_type() == "SUMMARY_NODE"):
            return True
        return False

    def is_leadsto_op(self):
        if(self.get_type() == "LEADSTO_OP"):
            return True
        return False
    
    def is_xor_op(self):
        if(self.get_type() == "LOG_XOR_OP"):
            return True
        return False

    def is_or_op(self):
        if(self.get_type() == "LOG_OR_OP"):
            return True
        return False

    def is_and_op(self):
        if(self.get_type() == "LOG_AND_OP"):
            return True
        return False

    def is_not_op(self):
        if(self.get_type() == "LOG_NOT_OP"):
            return True
        return False

    def is_logical_op(self):
        if(self.get_type().find("LOG_") == 0):
            return True
        return False

    def is_connect_op(self):
        if(self.get_type() == "CONNECT_OP"):
            return True
        return False

    def is_summ_op(self):
        if(self.get_type() == "SUMM_OP"):
            return True
        return False

    def is_conc_op(self):
        if(self.get_type().find("CONC_") == 0):
            return True
        return False

    def is_olap_op(self):
        if(self.get_type() == "CONC_OLAP_OP"):
            return True
        return False

    def is_sw_op(self):
        if(self.get_type() == "CONC_SW_OP"):
            return True
        return False

    def is_ew_op(self):
        if(self.get_type() == "CONC_EW_OP"):
            return True
        return False

    def is_dur_op(self):
        if(self.get_type() == "CONC_DUR_OP"):
            return True
        return False

    def is_eq_op(self):
        if(self.get_type() == "CONC_EQ_OP"):
            return True
        return False


    def is_behavior_object(self):
        if(self.get_type() == "BEHAVIOR"):
            return True
        return False

    def get_contents(self):
        return self.contents

    def __repr__(self):
        return self.get_fullname()

    def details(self):
        context = "Root: %s Behavior: %s Object Name: %s Type: %s %s" % \
                             (self.get_rootbehavior(),
                              self.get_behaviorname(),
                              self.get_name(),
                              self.get_type(),
                              self.__class__.__name__)
        return context


