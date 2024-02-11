###############################################################
# Script  
#	DDOS_ALEFIYA
#
# Domain  
#	NET/ATTACKS
#
# Description       
#	
#
# Constraints Specified
#	 None
#
# Output    
#	Outputs a single record when a DNS request-response pair is matched
#
# Output Event Name
#	 DNS_REQ_RES
#
#Output Attributes     
#	 dipaddr : Destination Address of victim
#
# File History
#	08/20/2010		Arun Viswanathan (aviswana@isi.edu)
# 	
############################################################### 
[header]
NAMESPACE = TESTS
NAME = DDOS_ALEFIYA
QUALIFIER = {eventtype='PACKET_ICMP'}
IMPORT = NET.BASE_PROTO.IPPKTPAIR

[states]
sA = IPPKTPAIR.ip_pkt_sd()
sB = IPPKTPAIR.ip_pkt_sd(dipaddr=$sA.dipaddr)[bcount>= 1]

[behavior]
b = sA ~>[within 1s] (sB)[bcount >= 59]

[spec]
DDOSATTACK = b
