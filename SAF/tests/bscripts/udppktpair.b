###############################################################
# Script  
#	UDPPKTPAIR
#
# Domain  
#	NET/BASE_PROTO
#
# Description       
#	Summarizes a UDP packet pair based on SIP/DIP/sport/dport
#      (as seen at origin of capture)
#
# Constraints Specified
#	 None
#
# Output    
#	Outputs a single record when a source-destination pair is matched
#
# Output Event Name
#	 UDP_PKTPAIR
#
#Output Attributes     
#	 sipaddr : Source address of  UDP flow
#	 dipaddr : Destination address of UDP Flow  
#	 sport    : Source port 
#	 dport    : Destination port
############################################################### 
[header]
NAMESPACE = TESTS
NAME = UDPPKTPAIR
QUALIFIER = {eventtype='PACKET_DNS'}
IMPORT = NET.BASE_PROTO.IPPKTPAIR

[states]
udp_pkt_sd = {IPPKTPAIR.ip_pkt_sd(sport=$1, dport=$2, protocol=17)}
udp_pkt_ds = {IPPKTPAIR.ip_pkt_ds($udp_pkt_sd, sport=$udp_pkt_sd.dport, dport=$udp_pkt_sd.sport, protocol=17)}

[behavior]
# QUALIFIER is prepended to all behaviors by default
b = udp_pkt_sd ~> udp_pkt_ds

[model]
UDP_PKTPAIR(sipaddr, dipaddr, sport, dport, protocol) =  b
