###############################################################
# Script  
#	DNSREQRES
#
# Domain  
#	NET/APP_PROTO
#
# Description       
#	Summarizes a DNS flow based on 
#      SIP/DIP/sport/dport/qname/dnsid/dnsquesname/dnsqrflag
#      (as seen at origin of capture)
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
#	 sipaddr : Source address of  UDP flow
#	 dipaddr : Destination address of UDP Flow  
#	 sport    : Source port 
#	 dport    : Destination port
# 	 dnsquesname  : DNS Question  
# 	 dnsid    : Transaction ID
#    dnsqrflag : DNS Query/Response Flag
############################################################### 
[header]
NAMESPACE = TEST
NAME = DNSREQRES
QUALIFIER = {eventtype='PACKET_DNS'}
IMPORT = NET.BASE_PROTO.UDPPKTPAIR

[states]
dns_req = {UDPPKTPAIR.udp_pkt_sd(dnsid=$1, dnsqrflag=0, dnsquesname=$2, dport=53)}
dns_res = {UDPPKTPAIR.udp_pkt_ds($dns_req, dnsid=$dns_req.dnsid, dnsquesname=$dns_req.dnsquesname, dnsqrflag=1, sport=53)}

[behavior]
b = dns_req ~> dns_res

[model]
DNS_REQ_RES(eventno, timestamp, timestampusec, sipaddr,dipaddr,sport,dport,dnsquesname,dnsid,dnsqrflag) =  b
