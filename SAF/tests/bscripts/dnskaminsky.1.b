###############################################################
# Script  
#	DNSKAMINSKY
#
# Domain  
#	NET/ATTACKS
#
# Description       
#	Summarizes the Kaminsky DNS attack as a SUCCESS or a FAILURE. 
#      Four possibilities are considered:
#      a. Attacker responds to Victim CORRECTLY before the Real NS. ==> SUCCESS 
#      b. Attacker responds before Victim
#
# Constraints Specified
#	 None
#
# Output    
#	Outputs a single record when a DNS request-response pair is matched
#
# Output Event Name
#
# Output Attributes     
#	 sipaddr  : Source address of  UDP flow
#	 dipaddr  : Destination address of UDP Flow  
#	 sport    : Source port 
#	 dport    : Destination port
# 	 dnsquesname  : DNS Question  
# 	 dnsid    : Transaction ID
#    dnsqrflag : DNS Query/Response Flag
# 	
############################################################### 
[header]
NAMESPACE = TESTS
NAME = DNSKAMINSKY_1
QUALIFIER = {eventtype='PACKET_DNS'}[_eventno=8000:10000]
IMPORT = NET.APP_PROTO.DNSREQRES

[states]
# Attacker to victim query
AtoV_query = DNSREQRES.dns_req()

# Victim to real ns query
VtoR_query = DNSREQRES.dns_req(sipaddr=$AtoV_query.dipaddr,
							  dnsquesname=$AtoV_query.dnsquesname)

# Real NS to victim real response
RtoV_resp = DNSREQRES.dns_res($VtoR_query, dnsauth='authns.bofa.com')

# Attacker to victim CORRECT fake response 
AtoV_resp = DNSREQRES.dns_res($VtoR_query, dnsauth='fakens.fakebofa.com')[bcount>=1]
#AtoV_resp = DNSREQRES.dns_res($VtoR_query, dnsid=$VtoR_query.dnsid)[bcount>1]

# Attacker to victim INCORRECT response case
AtoV_noresp = DNSREQRES.dns_res($VtoR_query, dnsid!=$VtoR_query.dnsid)[bcount>1]

[behavior]
b_1 = (AtoV_query ~> VtoR_query ~> RtoV_resp ~> AtoV_resp)
b_2 = ((AtoV_query ~> VtoR_query) ~> (RtoV_resp dur AtoV_noresp))
b_3 = (AtoV_query ~> VtoR_query ~> AtoV_noresp ~> RtoV_resp)
b_4 = (AtoV_query ~> VtoR_query ~> AtoV_resp ~> RtoV_resp)
FAILURE = (b_1 or b_2 or b_3) 
SUCCESS = (b_4)
M = (FAILURE or SUCCESS)

[model]
DNSKAMINSKY(sipaddr,dipaddr,sport,dport,dnsquesname, dnsid,dnsauth, dnsqrflag) = M

