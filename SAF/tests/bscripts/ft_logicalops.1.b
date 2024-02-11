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
NAME = LOGICAL_OPS_1
QUALIFIER = {eventtype='PACKET_DNS'} [_eventno=2720:2735]
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

# Attacker to victim INCORRECT response case
AtoV_noresp = DNSREQRES.dns_res($VtoR_query, dnsid != $VtoR_query.dnsid)[bcount>1]

[behavior]
initial_query = (AtoV_query ~> VtoR_query)
b_1 = (initial_query ~> ((RtoV_resp ~> AtoV_resp) or (RtoV_resp dur AtoV_noresp)))
b_2 = (initial_query ~> AtoV_noresp ~> RtoV_resp)
b_3 = (initial_query ~> AtoV_resp ~> RtoV_resp)

[model]
DNSKAMINSKY_FAILURE(eventno,timestamp,timestampusec,sipaddr,dipaddr,sport,dport,dnsquesname, dnsid,dnsauth, dnsqrflag) = (b_1 or b_2)
DNSKAMINSKY_SUCCESS(eventno,timestamp, timestampusec,sipaddr,dipaddr,sport,dport,dnsquesname, dnsid,dnsauth, dnsqrflag) = (b_3)

#=====================
# Example failure case
#=====================
#
# AtoV_query = 2721 
# VtoR_query = 2722
# RtoV_resp  = 2726
# AtoV_noresp = 2727, 2729, 2730,2731,2732, 2733,2734

#eventno     timestamp   timestampusec  sipaddr     dipaddr     sport       dport       dnsid       dnsqrflag   dnsquesname                dnsauth   
#----------  ----------  -------------  ----------  ----------  ----------  ----------  ----------  ----------  -------------------------  ----------
#2721        1275515486  118260         10.1.11.2   10.1.4.2    6916        53          47217       0           i37wMaCelZuUSkyc.bofa.com            
#2722        1275515486  118372         10.1.4.2    10.1.6.3    32778       53          15578       0           i37wMaCelZuUSkyc.bofa.com            
#2723        1275515486  119010         10.1.6.3    10.1.4.2    53          32778       47217       1           i37wMaCelZuUSkyc.bofa.com  fakens.fak
#2724        1275515486  119016         10.1.6.3    10.1.4.2    53          32778       47217       1           i37wMaCelZuUSkyc.bofa.com  fakens.fak
#2725        1275515486  119760         10.1.6.3    10.1.4.2    53          32778       47217       1           i37wMaCelZuUSkyc.bofa.com  fakens.fak
#2726        1275515486  119765         10.1.6.3    10.1.4.2    53          32778       15578       1           i37wMaCelZuUSkyc.bofa.com  authns.bof
#2727        1275515486  119767         10.1.6.3    10.1.4.2    53          32778       47217       1           i37wMaCelZuUSkyc.bofa.com  fakens.fak
#2728        1275515486  119898         10.1.4.2    10.1.11.2   53          6916        47217       1           i37wMaCelZuUSkyc.bofa.com  authns.bof
#2729        1275515486  120011         10.1.6.3    10.1.4.2    53          32778       47217       1           i37wMaCelZuUSkyc.bofa.com  fakens.fak
#2730        1275515486  120509         10.1.6.3    10.1.4.2    53          32778       47217       1           i37wMaCelZuUSkyc.bofa.com  fakens.fak
#2731        1275515486  121009         10.1.6.3    10.1.4.2    53          32778       47217       1           i37wMaCelZuUSkyc.bofa.com  fakens.fak
#2732        1275515486  121014         10.1.6.3    10.1.4.2    53          32778       47217       1           i37wMaCelZuUSkyc.bofa.com  fakens.fak
#2733        1275515486  121509         10.1.6.3    10.1.4.2    53          32778       47217       1           i37wMaCelZuUSkyc.bofa.com  fakens.fak
#2734        1275515486  121514         10.1.6.3    10.1.4.2    53          32778       47217       1           i37wMaCelZuUSkyc.bofa.com  fakens.fak
