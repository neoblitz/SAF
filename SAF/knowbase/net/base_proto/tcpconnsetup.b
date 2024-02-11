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
#    tcpflags : TCP flags
############################################################### 

[header]
NAMESPACE = NET.BASE_PROTO
NAME = TCPCONNSETUP
QUALIFIER = {eventtype='PACKET_TCP'}
IMPORT = NET.BASE_PROTO.TCPPKTPAIR

[states]
tcp_pkt_syn =  TCPPKTPAIR.tcp_pkt_sd(tcpflags=2) 
tcp_pkt_synack = TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_syn,  tcpflags=18) 
tcp_pkt_ack =  TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_syn,  tcpflags=16 ) 
 

[behavior]
3way_handshake = (tcp_pkt_syn ~> tcp_pkt_synack ~> tcp_pkt_ack)

[model]
TCP_CONNSETUP(eventno,timestamp,timestampusec,sipaddr,dipaddr,sport,dport,tcpflags) =  (3way_handshake)
