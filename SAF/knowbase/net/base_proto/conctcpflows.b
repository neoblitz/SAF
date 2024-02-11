###############################################################
# Script  
#    Concurrent TCP Handshakes
#
# Domain  
#   NET/BASE_PROTO
#
# Description       
#   Model for concurrent TCP handshakes 
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
NAMESPACE = NET.BASE_PROTO
NAME = CONCTCPHANDSHAKES
QUALIFIER = {eventtype='PACKET_TCP'}
IMPORT = NET.BASE_PROTO.TCPCONNSETUP

[states]
flow_a = TCPCONNSETUP.TCP_CONNSETUP()
flow_b = TCPCONNSETUP.TCP_CONNSETUP()

[behavior]
# INIT is prepended to all behaviors by default
#CONC_HSH = (flow_a olap flow_b)

[model]
# eventno, timestamp, timestampusec are exported by default
CONC_TCP_HANDSHAKES(eventno, timestamp, timestampusec, sipaddr, dipaddr, protocol) = (flow_a olap flow_b)