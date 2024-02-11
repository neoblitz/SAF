###############################################################
# Script  
#	TCPCONNTDOWN
#
# Domain  
#	NET/BASE_PROTO
#
# Description       
#	Summarizes a TCP connection teardown
#
# Constraints Specified
#	 None
#
# Output    
#	Outputs a single record for each tcp connection completion  
#
# Output Event Name
#	 TCP_CONNTDOWN 
#
#Output Attributes     
#	 sipaddr : Source address of  TCP flow
#	 dipaddr : Destination address of TCP Flow  
#	 sport    : Source port 
#	 dport    : Destination port
############################################################### 

[header]
NAMESPACE = TESTS
NAME = TCPCONNTDOWN
QUALIFIER = {eventtype='PACKET_TCP'}
IMPORT = NET.BASE_PROTO.TCPPKTPAIR

[states]
tcp_pkt_fin =   TCPPKTPAIR.tcp_pkt_sd(tcpflags=1) 
tcp_pkt_piggyfin =  TCPPKTPAIR.tcp_pkt_sd(tcpflags=17)
tcp_pkt_finack = TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_piggyfin, tcpflags=17)
tcp_pkt_ack = TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_piggyfin, tcpflags=16)

[behavior]
# INIT is prepended to all behaviors by default
bclean = ((tcp_pkt_fin ~> tcp_pkt_finack) ~> tcp_pkt_ack)
bpiggy = ((tcp_pkt_piggyfin ~> tcp_pkt_finack) ~> (tcp_pkt_ack)) 

[model]
TCP_CONNTDOWN(eventno,sipaddr,dipaddr,sport,dport,tcpflags) =  (bpiggy or bclean)
#TCP_CONNTDOWN_BPIGGY = bpiggy
