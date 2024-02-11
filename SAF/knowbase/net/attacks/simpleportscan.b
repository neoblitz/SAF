###############################################################################
# Script Name 
#   <Name of the script>
#
# Description      
#    
#
# Input Requirements
#   <What type of events does this model work on?>
#       Event Type: 
#       Event Attributes: 
#       <Describe each event and its attributes>
#
# Output
#   <What events are output? How can one make sense of those?>
#   
# Example Dataset(s)
#   <Add URLs of example raw-data or SQLite databases on which the model can be
#    tested ?>
# 
# SAF compatibility
#   <What versions of SAF will the model work with?>
# 
# Depends On
#  <What other models does this model depend on? Write the fully qualified
#   name.>
# 
# References
#  <Any references to papers or other relevant resources.>
#
# Model Author(s)
#   aviswana@usc.edu
# 
# # Leave these lines unchanged.
# $URL: http://thirdeye.deterlab.net/svn/trunk/SAF/knowbase/modeltemplate.b $  
# $LastChangedDate: 2011-07-04 16:56:35 -0700 (Mon, 04 Jul 2011) $
################################################################################ 

[header]
# The namespace to which this model belongs. Namespace need not be dotted.
NAMESPACE = NET.BASE_PROTO

# A name for the model. Name can contain only the following characters: A-Z,a-z,0-9_].
NAME = HORIZSCAN

# Defines any necessary conditions for qualifying events
QUALIFIER = {  }

# A comma separated list of models that are imported
#IMPORT = NET.BASE_PROTO.TCPCONNSETUP

[states]
sA = {sipaddr = $1, dipaddr=$2, dport = $3} 
sB = {sipaddr=$sA.sipaddr, dipaddr != $sA.dipaddr, dport=$sA.dport}[bcount >= 1]
sC = {sipaddr=$sA.sipaddr, dipaddr != $sA.dipaddr, dport!=$sA.dport}[bcount >= 1]
sD = {sipaddr=$sA.sipaddr, dipaddr = $sA.dipaddr, dport != $sA.dport}[bcount >= 1]

[behavior]
horizscan_singleport = (sA ~> sB)
horizscan_diffports  = (sA ~> sC)
vertscan             = (sA ~> sD)

[model]
SCAN(sipaddr, dipaddr, dport) = (horizscan_singleport or 
                                 horizscan_diffports  or 
                                 vertscan)