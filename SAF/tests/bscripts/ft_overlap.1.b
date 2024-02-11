###############################################################
# Script  
#    Concurrent IP Flows
#
# Domain  
#   NET/BASE_PROTO
#
# Description       
#   Models overlapping IP flows 
#
# Constraints Specified
#    None
#
# Output Event Name   
#    CONCIPFLOWS
#
# Output Attributes     
#    sipaddr : Source address of  IP flow
#    dipaddr : Destination address of IP Flow  
#    protocol: The transport protocol 
############################################################### 
[header]
NAMESPACE = TESTS
NAME = FT_OVERLAP_1
QUALIFIER = {eventtype='PACKET_TCP'}
IMPORT = NET.BASE_PROTO.IPPKTPAIR

[states]
flow_a = IPPKTPAIR.IP_PKTPAIR()
flow_b = IPPKTPAIR.IP_PKTPAIR()

[behavior]
# INIT is prepended to all behaviors by default
b = (flow_a olap flow_b)

[model]
# eventno, timestamp, timestampusec are exported by default
CONCIPFLOW(eventno, sipaddr, dipaddr, protocol) = b 
