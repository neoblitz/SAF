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
NAME = TCPFLOW_COMPLETE
QUALIFIER = {eventtype='PACKET_TCP'}
IMPORT = NET.BASE_PROTO.TCPPKTPAIR

[states]

tcp_pkt_syn = {sipaddr = $1, dipaddr=$2, sport=$3, dport=$4, protocol=$5, tcpflags=2}
tcp_pkt_synack = {sipaddr = $tcp_pkt_syn.dipaddr, dipaddr=$tcp_pkt_syn.sipaddr, sport=$tcp_pkt_syn.dport, dport=$tcp_pkt_syn.sport, protocol=$5, tcpflags=18}
tcp_pkt_ack = {sipaddr = $tcp_pkt_syn.sipaddr, dipaddr=$tcp_pkt_syn.dipaddr, sport=$tcp_pkt_syn.sport, dport=$tcp_pkt_syn.dport, protocol=$5, tcpflags=16}

tcp_pkt_pshack_from_s = {sipaddr = $tcp_pkt_syn.sipaddr, dipaddr=$tcp_pkt_syn.dipaddr, sport=$tcp_pkt_syn.sport, dport=$tcp_pkt_syn.dport, protocol=$5, tcpflags=24}
tcp_pkt_dack_from_d = {sipaddr = $tcp_pkt_syn.dipaddr, dipaddr=$tcp_pkt_syn.sipaddr, sport=$tcp_pkt_syn.dport, dport=$tcp_pkt_syn.sport, protocol=$5, tcpflags=16}
tcp_pkt_pshack_from_d = {sipaddr = $tcp_pkt_syn.dipaddr, dipaddr=$tcp_pkt_syn.sipaddr, sport=$tcp_pkt_syn.dport, dport=$tcp_pkt_syn.sport, protocol=$5, tcpflags=24}
tcp_pkt_dack_from_s = {sipaddr = $tcp_pkt_syn.sipaddr, dipaddr=$tcp_pkt_syn.dipaddr, sport=$tcp_pkt_syn.sport, dport=$tcp_pkt_syn.dport, protocol=$5, tcpflags=16}


#
#TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_syn.sipaddr=,  tcpflags=24 ) [bcount>=1]#
#tcp_pkt_dack_from_d = TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_syn,  tcpflags=16) [bcount>=1]
#tcp_pkt_pshack_from_d = TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_syn,  tcpflags=24 ) [bcount >=1 ]
#tcp_pkt_dack_from_s = TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_syn,  tcpflags=16) [bcount>=1]

#tcp_pkt_syn =  TCPPKTPAIR.tcp_pkt_sd(tcpflags=2) 
#tcp_pkt_synack = TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_syn,  tcpflags=18) 
#tcp_pkt_ack =  TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_syn,  tcpflags=16 ) 

#tcp_pkt_pshack_from_s = TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_syn.sipaddr=,  tcpflags=24 ) [bcount>=1]#
#tcp_pkt_dack_from_d = TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_syn,  tcpflags=16) [bcount>=1]
#tcp_pkt_pshack_from_d = TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_syn,  tcpflags=24 ) [bcount >=1 ]
#tcp_pkt_dack_from_s = TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_syn,  tcpflags=16) [bcount>=1]

#tcp_pkt_fin      = TCPPKTPAIR.tcp_pkt_sd(tcpflags=1)
#tcp_pkt_piggyfin = TCPPKTPAIR.tcp_pkt_sd(tcpflags=17)
#tcp_pkt_finack_from_s   = TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_piggyfin, tcpflags=17)
#tcp_pkt_finack_from_d   = TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_piggyfin, tcpflags=17)

#tcp_pkt_ack_from_s      = TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_piggyfin, tcpflags=16)
#tcp_pkt_ack_from_d      = TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_piggyfin, tcpflags=16)

# TCP packet resets
#tcp_pkt_rst_sd          = TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_syn, tcpflags=4)
#tcp_pkt_rst_ds          = TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_syn, tcpflags=4)

[behavior]
flow_1 = (tcp_pkt_syn ~> tcp_pkt_synack ~> tcp_pkt_ack ~> tcp_pkt_pshack_from_d)
#flow_1 = (tcp_pkt_syn ~> tcp_pkt_synack ~> tcp_pkt_ack ~> tcp_pkt_pshack_from_d ~> tcp_pkt_dack_from_s)
flow_2 =  (tcp_pkt_syn ~> tcp_pkt_synack ~> tcp_pkt_ack ~> tcp_pkt_pshack_from_s ~> tcp_pkt_dack_from_d)
#tcp_data_2 = (tcp_pkt_pshack_from_s ~> tcp_pkt_dack_from_d)
#[bcount>=1]
    
#full_teardown          = (tcp_pkt_fin ~> tcp_pkt_finack_from_d ~> tcp_pkt_ack_from_s)
#full_teardown_piggyfin = (tcp_pkt_piggyfin ~> tcp_pkt_finack_from_d ~> tcp_pkt_ack_from_s) 
#half_close             = (tcp_pkt_piggyfin ~> tcp_pkt_ack_from_d)

# Connection close using packet resets
#close_by_rst           = (tcp_pkt_syn ~> (tcp_pkt_rst_sd xor tcp_pkt_rst_ds))

#tcp_conn_tdown = (full_teardown or full_teardown_piggyfin or half_close or close_by_rst)

#flow1 =  (3way_handshake ~> tcp_pkt_pshack_from_s ~> tcp_pkt_dack_from_d ~> tcp_conn_tdown) 
#flow2 =  (3way_handshake ~> tcp_pkt_pshack_from_d ~> tcp_pkt_dack_from_s ~> tcp_conn_tdown) 
#flow1 =  (3way_handshake ~> tcp_data_2)

[model]
TCP_FLOW(eventno,timestamp,timestampusec,sipaddr,dipaddr,sport,dport,tcpflags) =  (flow_1)
