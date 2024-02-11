###############################################################
# Script  
#	TCPFLOW
#
# Domain  
#	NET/BASE_PROTO
#
# Description       
#	Summarizes a TCP Flow
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
NAME = TCPFLOW
QUALIFIER = {eventtype='PACKET_TCP'}
IMPORT = NET.BASE_PROTO.TCPPKTPAIR

[states]
tcp_pkt_syn =  TCPPKTPAIR.tcp_pkt_sd( tcpflags=2 ) 
tcp_pkt_synack = TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_syn,  tcpflags=18) 
tcp_pkt_ack =  TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_syn,  tcpflags=16 ) 
tcp_pkt_ack_ds =  TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_syn,  tcpflags=16 )  

# The FINs can be initiated by either end thus we define
# two variants for the following states. 
tcp_pkt_fin_sd =   TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_syn, tcpflags=1) 
tcp_pkt_fin_ds =   TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_syn, tcpflags=1)

tcp_pkt_piggyfin_sd =  TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_syn,tcpflags=17)
tcp_pkt_piggyfin_ds =  TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_syn,tcpflags=17)

tcp_pkt_finack_sd = TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_syn, tcpflags=17)
tcp_pkt_finack_ds = TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_syn, tcpflags=17)

# TCP Pkt Rsts
tcp_pkt_rst_sd = TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_syn, tcpflags=4)
tcp_pkt_rst_ds = TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_syn, tcpflags=4)

[behavior]
tcp_conn_setup = (tcp_pkt_syn ~> tcp_pkt_synack ~> tcp_pkt_ack)
tcp_conn_tdown_sd = tcp_pkt_piggyfin_sd ~> tcp_pkt_finack_ds ~> tcp_pkt_ack
tcp_conn_tdown_ds = tcp_pkt_piggyfin_ds ~> tcp_pkt_finack_sd ~> tcp_pkt_ack_ds

b1 = (tcp_conn_setup ~> tcp_conn_tdown_sd)
b2 = (tcp_conn_setup ~> tcp_conn_tdown_ds)
b3 = (tcp_conn_setup ~> tcp_pkt_rst_sd)
b4 = (tcp_conn_setup ~> tcp_pkt_rst_ds)

[model]
TCPFLOW_COMPLETE_SOURCE_TEARDOWN = b1
TCPFLOW_COMPLETE_DEST_TEARDOWN = b2 
#TCPFLOW_RST_SOURCE 	 = b3 
#TCPFLOW_RST_DEST 	 = b4

