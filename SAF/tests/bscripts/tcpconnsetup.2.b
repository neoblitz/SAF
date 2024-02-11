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

#-------------------
# Tests for 'window'
#-------------------
# Success

# All records are returned
w1 = (tcp_pkt_syn ~> tcp_pkt_synack ~> tcp_pkt_ack)[window <= 60s]

# 3 records are returned
w3 = (tcp_pkt_syn ~> tcp_pkt_synack ~> tcp_pkt_ack)[window rangei 10:50 ms]

# Return everything except the first and 4th records
w6 = (tcp_pkt_syn ~> tcp_pkt_synack ~> tcp_pkt_ack)[window != 92ms]

# 5 records are returned
w7 = (tcp_pkt_syn ~> tcp_pkt_synack ~> tcp_pkt_ack)[window rangei 20:100 ms]

#6 records are returned
w9 = ((tcp_pkt_syn ~> tcp_pkt_synack)[window > 10ms] ~> tcp_pkt_ack)
w11 = ((tcp_pkt_syn) ~> (tcp_pkt_synack)[window > 10ms] ~> (tcp_pkt_ack))
w12 = ((tcp_pkt_syn) ~> (tcp_pkt_synack)[window > 10ms] ~> (tcp_pkt_ack)[window > 10ms])

# Failure
# No records are returned 
w4 = (tcp_pkt_syn ~> tcp_pkt_synack ~> tcp_pkt_ack)[window rangee 10:20]
w2 = (tcp_pkt_syn ~> tcp_pkt_synack ~> tcp_pkt_ack)[window > 60]
w5 = (tcp_pkt_syn ~> tcp_pkt_synack ~> tcp_pkt_ack)[window rangei 15:19]

# This should return an Error
w8 = ((tcp_pkt_syn)[window > 10] ~> tcp_pkt_synack ~> tcp_pkt_ack)

#-----------------
# Tests for 'icount'
#-----------------
# Failure
c1 = (tcp_pkt_syn ~> tcp_pkt_synack ~> tcp_pkt_ack)[icount = 1]
c5 = (tcp_pkt_syn ~> (tcp_pkt_synack)[icount rangei 7:10] ~> tcp_pkt_ack)[icount = 6]

# Success
c2 = (tcp_pkt_syn ~> tcp_pkt_synack ~> tcp_pkt_ack)[icount > 1]
c3 = (tcp_pkt_syn ~> tcp_pkt_synack ~> tcp_pkt_ack)[icount = 6]
c4 = (tcp_pkt_syn ~> (tcp_pkt_synack)[icount > 3] ~> tcp_pkt_ack)[icount = 6]

#-----------------
# Tests for 'epoch'
#-----------------



[spec]
TCP_CONNSETUP_WINDOW =  w1 || w2 || w3 || w4 || w5 || w6 || w7 || w8 || w9 || w11 || w12
TCP_CONNSETUP_COUNT =  c1 || c2 || c3 || c4 || c5
#TCP_CONNSETUP_COUNT =  w9 
#TCP_CONNSETUP_EPOCH =  c1 || c2 || c3 || c4 || c5