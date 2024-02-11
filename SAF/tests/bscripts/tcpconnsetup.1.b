###############################################################
# Script  
#	TCPCONNSETUP
#
# Domain  
#	NET/BASE_PROTO
#
# Description       
#	Summarizes a TCP connection setup
#
# Constraints Specified
#	 None
#
# Output    
#	Outputs a single record for each tcp connection setup 
#
# Output Event Name
#	 TCP_CONNSETUP 
#
#Output Attributes     
#	 sipaddr : Source address of  TCP flow
#	 dipaddr : Destination address of TCP Flow  
#	 sport    : Source port 
#	 dport    : Destination port
############################################################### 

[header]
NAMESPACE = TESTS
NAME = TCPCONNSETUP
QUALIFIER = {eventtype='PACKET_TCP'}
IMPORT = NET.BASE_PROTO.TCPPKTPAIR

[states]
tcp_pkt_syn =  TCPPKTPAIR.tcp_pkt_sd( tcpflags=2 ) 
tcp_pkt_synack = TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_syn,  tcpflags=18) 
tcp_pkt_ack =  TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_syn,  tcpflags=16 ) 
 

[behavior]

#-------------------------------------
# Tests for 'within'
#-------------------------------------
# INIT is prepended to all behaviors by default

# Success
b1 = tcp_pkt_syn ~>[within 1s] tcp_pkt_synack ~> tcp_pkt_ack
b2 = tcp_pkt_syn ~>[within 500 ms] tcp_pkt_synack ~> (tcp_pkt_ack)

# This should return records. The exact difference between test events 10 and 
# 17 is 92ms 
b4 = tcp_pkt_syn ~>[within 92 ms] tcp_pkt_synack ~> tcp_pkt_ack

# These will PASS too
b5 = tcp_pkt_syn ~>[within 370 ms] (tcp_pkt_synack ~> tcp_pkt_ack)
b6 = tcp_pkt_syn ~> (tcp_pkt_synack ~>[within 500ms] tcp_pkt_ack)
b7 = (tcp_pkt_syn ~> tcp_pkt_synack ~>[within 500ms] tcp_pkt_ack)
b8 = (tcp_pkt_syn ~> [within  370ms] tcp_pkt_synack ~>[within 0ms] tcp_pkt_ack)
b9 = (tcp_pkt_syn ~> (tcp_pkt_synack ~>[within 10ms] tcp_pkt_ack))

b11 = ((tcp_pkt_syn) ~> (tcp_pkt_synack ~> [within 0ms] tcp_pkt_ack))
b12 = ((tcp_pkt_syn) ~>[within 370000usecs] (tcp_pkt_synack ~>[within 60us] tcp_pkt_ack))
b13 = (tcp_pkt_syn ~> [within  370ms] tcp_pkt_synack ~>[within 0ms] tcp_pkt_ack)
b14 = ((tcp_pkt_syn) ~> (tcp_pkt_synack) ~> (tcp_pkt_ack))

# Failures
b3 = tcp_pkt_syn ~>[within 1ms] tcp_pkt_synack ~> (tcp_pkt_ack)
b10 = (tcp_pkt_syn ~>[within 20 us] (tcp_pkt_synack ~>[within 10ms] tcp_pkt_ack))

#-------------------------------------
# Tests for 'after'
#-------------------------------------

# Failures 
a1 = tcp_pkt_syn ~>[after 1s] tcp_pkt_synack ~> tcp_pkt_ack
a2 = tcp_pkt_syn ~>[after 1ms] tcp_pkt_synack ~>[after 100 usecs] (tcp_pkt_ack)
a7 = (tcp_pkt_syn ~> tcp_pkt_synack ~>[after 100ms] tcp_pkt_ack)
a5 = tcp_pkt_syn ~>[after 10 ms] (tcp_pkt_synack ~> tcp_pkt_ack)

# Success
a3 = tcp_pkt_syn ~>[after 90 ms] tcp_pkt_synack ~> (tcp_pkt_ack)
a4 = tcp_pkt_syn ~>[after 90 ms] tcp_pkt_synack ~>[after 40 usecs] (tcp_pkt_ack)
a6 = tcp_pkt_syn ~> (tcp_pkt_synack ~>[after 40 us] tcp_pkt_ack)
a8 = (tcp_pkt_syn ~> [after  22ms] tcp_pkt_synack ~>[after 0ms] tcp_pkt_ack)
a9 = ((tcp_pkt_syn) ~>[after 90000 usecs] (tcp_pkt_synack) ~>[after 45 us] (tcp_pkt_ack))


#-------------------------------------
# Tests combining 'within' and 'after'
#-------------------------------------
# Success
aw1 = tcp_pkt_syn ~>[after 90ms] tcp_pkt_synack ~>[within 500ms] tcp_pkt_ack
aw3 = ((tcp_pkt_syn) ~>[after 90000 usecs] (tcp_pkt_synack) ~>[within 0 s] (tcp_pkt_ack))

# Failure
aw2 = tcp_pkt_syn ~>[within 92000 us] tcp_pkt_synack ~>[after 100 usecs] (tcp_pkt_ack)

[spec]
TCP_CONNSETUP_WITHIN =  b1 || b2 || b3 || b4 || b5 || b6 || b7 || b8 || b9 || b10 || b11 ||b12 || b13 ||b14
TCP_CONNSETUP_AFTER =  a1 || a2 || a3 || a4 || a5 || a6|| a7 || a8 || a9 
TCP_CONNSETUP_WITHIN_AFTER =  aw1 || aw2 || aw3
 