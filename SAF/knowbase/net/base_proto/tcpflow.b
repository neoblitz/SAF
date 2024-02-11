###############################################################
# Script  
#   TCP_FLOW
#
# Domain  
#   NET/BASE_PROTO
#
# Description       
#   Summarizes a TCP Flow
#
# Constraints Specified
#    None
#
# Output    
#   Outputs a single record for each tcp connection setup 
#
# Output Event Name
#    TCP_CONNSETUP 
#
#Output Attributes     
#    sipaddr : Source address of  TCP flow
#    dipaddr : Destination address of TCP Flow  
#    sport    : Source port 
#    dport    : Destination port
############################################################### 

[header]
NAMESPACE = NET.BASE_PROTO
NAME = TCPFLOW
QUALIFIER = {eventtype='PACKET_TCP'}
IMPORT = NET.BASE_PROTO.TCPCONNSETUP, NET.BASE_PROTO.TCPCONNTDOWN

[states]

tcp_3way_handshake =  TCPCONNSETUP.TCP_CONNSETUP()
tcp_conn_tdown     =  TCPCONNTDOWN.TCP_CONNTDOWN($tcp_3way_handshake)

[behavior]
tcpflow = (tcp_3way_handshake ~> tcp_conn_tdown)

[model]
TCPFLOW(eventno, timestamp, timestampusec, sipaddr, dipaddr, sport, dport, tcpflags) = (tcpflow)


