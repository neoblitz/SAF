###############################################################
# Script  
#	TCPPKTPAIR
#
# Domain  
#	NET/BASE_PROTO
#
# Description       
#	Summarizes a TCP packet pair based on SIP/DIP/sport/dport
#      (as seen at origin of capture)
#
# Constraints Specified
#	 None
#
# Output    
#	Outputs a single record when a source-destination pair is matched
#
# Output Event Name
#	 TCP_PKTPAIR
#
#Output Attributes     
#	 sipaddr : Source address of  TCP flow
#	 dipaddr : Destination address of TCP Flow  
#	 sport    : Source port 
#	 dport    : Destination port
############################################################### 
[header]
NAMESPACE = TESTS
NAME = TCPPKTPAIR
QUALIFIER = {eventtype='PACKET_TCP'}
IMPORT = NET.BASE_PROTO.IPPKTPAIR

[states]
tcp_pkt_sd = { IPPKTPAIR.ip_pkt_sd(sport=$3, dport=$4, protocol=6) }
tcp_pkt_ds = { IPPKTPAIR.ip_pkt_ds($tcp_pkt_sd, sport=$tcp_pkt_sd.dport, dport=$tcp_pkt_sd.sport, protocol=6)  }

[behavior]
# INIT is prepended to all behaviors by default
b = (tcp_pkt_sd ~> tcp_pkt_ds)

[model]
TCP_PKTPAIR(sipaddr,dipaddr,protocol,sport,dport,tcpflags) =  b
