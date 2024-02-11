###############################################################################
# Script Name  
#	TCPCONNTDOWN: TCP connection teardown model
#
# Description       
#   Models the possible ways in which TCP connection teardowns can happen
# 
# Event requirements for model
#   Works over PACKET_TCP events
#
# Depends On
#   NET.BASE.BASE_PROTO.TCPPKTPAIR
#
# Possible Behaviors 
#	 TCP_CONNTDOWN 
#
# Output Attributes
#	 sipaddr : Source address of TCP flow
#	 dipaddr : Destination address of TCP Flow  
#	 sport   : Source port 
#	 dport   : Destination port
#    tcpflags: Tcp flags field
#
# Model Author(s):
#   Arun Viswanathan (aviswana@isi.edu)
################################################################################ 

[header]
NAMESPACE = NET.BASE_PROTO
NAME = TCPCONNTDOWN
QUALIFIER = {eventtype='PACKET_TCP'}
IMPORT = NET.BASE_PROTO.TCPPKTPAIR, NET.BASE_PROTO.TCPCONNSETUP

[states]
tcp_pkt_syn      = TCPCONNSETUP.tcp_pkt_syn() 
tcp_pkt_fin      = TCPPKTPAIR.tcp_pkt_sd(tcpflags=1)
 
tcp_pkt_piggyfin = TCPPKTPAIR.tcp_pkt_sd(tcpflags=17)

tcp_pkt_finack_from_s   = TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_piggyfin, tcpflags=17)
tcp_pkt_finack_from_d   = TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_piggyfin, tcpflags=17)

tcp_pkt_ack_from_s      = TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_piggyfin, tcpflags=16)
tcp_pkt_ack_from_d      = TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_piggyfin, tcpflags=16)

# TCP packet resets
tcp_pkt_rst_sd          = TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_syn, tcpflags=4)
tcp_pkt_rst_ds          = TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_syn, tcpflags=4)

[behavior]
full_teardown          = (tcp_pkt_fin ~> tcp_pkt_finack_from_d ~> tcp_pkt_ack_from_s)
full_teardown_piggyfin = (tcp_pkt_piggyfin ~> tcp_pkt_finack_from_d ~> tcp_pkt_ack_from_s) 
half_close             = (tcp_pkt_piggyfin ~> tcp_pkt_ack_from_d)

# Connection close using packet resets
close_by_rst           = (tcp_pkt_syn ~> (tcp_pkt_rst_sd xor tcp_pkt_rst_ds))

[model]
TCP_CONNTDOWN(eventno,timestamp, timestampusec, sipaddr,dipaddr,sport,dport,tcpflags) = 
                            (full_teardown or full_teardown_piggyfin or half_close or close_by_rst)
                                                                
