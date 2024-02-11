###############################################################
# Script  
#	 IPPKTPAIR
#
# Domain  
#	NET/BASE_PROTO
#
# Description       
#	Summarizes two IP packets into an IP packet pair based on SIP/DIP 
#      (as seen at origin of capture)
#
# Constraints Specified
#	 None
#
# Output Event Name   
#	 IP_PKTPAIR
#
#Output Attributes     
#	 sipaddr : Source address of  IP flow
#	 dipaddr : Destination address of IP Flow  
#       protocol: The transport protocol 
############################################################### 
[header]
NAMESPACE = NET.BASE_PROTO
NAME = IPPKTPAIR
QUALIFIER = {}

[states]
ip_pkt_sd = {sipaddr = $1, dipaddr = $2, protocol=$3}
ip_pkt_ds = {sipaddr = $ip_pkt_sd.dipaddr , dipaddr = $ip_pkt_sd.sipaddr, 
                        protocol=$ip_pkt_sd.protocol}

[behavior]
# INIT is prepended to all behaviors by default
b = ip_pkt_sd ~> ip_pkt_ds

[model]
IP_PKTPAIR(eventno, eventtype, timestamp, timestampusec, sipaddr, dipaddr, protocol) = b 