###############################################################################
# Script Name 
#   DNSKAMINSKY
#
# Description      
#   Model of the DNS Kaminsky cache poisoning attack.
#   A detailed explanation of the attack and the corresponding model is 
#   can be found at http://thirdeye.deterlab.net/trac/wiki/ExampleDNSKaminsky. 
#   
# Input Requirements
#       Event Type: PACKET_DNS
#       Event Attributes: sipaddr,dipaddr,sport,dport, protocol, 
#                         dnsqrflag, dnsauth, dnsid, dnsquesname
#
# Output
#   Events satisfying either the SUCCESS or FAILURE behaviors.
#   
# Example Dataset(s)
#   http://thirdeye.deterlab.net/trac/browser/trunk/saf-data/db/nsdipaper_casestudy2_data.sqlite
# 
# SAF compatibility
#   0.2a and later
# 
# Depends On
#   NET.APP_PROTO.DNSREQRES
# 
# References
#   http://thirdeye.deterlab.net/trac/wiki/ExampleDNSKaminsky 
#       Contains a more detailed explanation of the model, input and output.
#
# Model Author(s)
#   Arun Viswanthan (aviswana@usc.edu)
# 
# Additional Notes
#   This model uses constant values for the 'dnsauth' variable.  Make sure 
#   to replace those constant values by appropriate values while using with 
#   other datasets.  A future version of the model will remove this 
#   limitation.
# 
# # Leave these lines unchanged.
# $URL: svn+ssh://arunvisw@www.arunviswanathan.com/svn/trunk/SAF/knowbase/net/attacks/dnskaminsky.b $  
# $LastChangedDate: 2011-08-07 13:53:27 -0700 (Sun, 07 Aug 2011) $
################################################################################ 

[header]
NAMESPACE = NET.ATTACKS
NAME = DNSKAMINSKY
QUALIFIER = {eventtype='PACKET_DNS'}

# Import the DNSREQRES model that already defines states and behaviors relevant 
# to the DNS protocol.
IMPORT = NET.APP_PROTO.DNSREQRES

[states]
#-----------------------------------------------------------------------------
# There are 5 possible states in the experiment that need to be captured.
# A, V and R are used to refer to Attacker, Victim nameserver and Real nameserver 
# respectively
#-----------------------------------------------------------------------------

#------------------------------------------------------------------------------
# State: Attacker sends a DNS query for a randomly generated name under the 
#        'domain' in question. 
#   
# This is done by directly importing the predefined state dns_req()
#-------------------------------------------------------------------------------
AtoV_query = DNSREQRES.dns_req()

#------------------------------------------------------------------------------
# State: The victim nameserver forwards it to the real nameserver for the domain. 
#
# The forwarded query is captured by importing dns_req() with the 
# following additional dependencies 
# (a) the sipaddr of this request must be the same as the dipaddr of the previous 
#      query, 
# (b) the dnsquesname must be same as the dnsquesname of the request. 
#------------------------------------------------------------------------------
VtoR_query = DNSREQRES.dns_req(sipaddr=$AtoV_query.dipaddr,
							  dnsquesname=$AtoV_query.dnsquesname)						  

#------------------------------------------------------------------------------
# State: The attacker sends a series of CORRECTLY forged DNS responses 
#        (containing the fake nameserver as authority) to the victim and 
#         spoofing  as the real nameserver. 
#
# To capture this, import the predefined DNS response with the additional
# constraints:
# (a) We make all values of this query dependent upon the values in the 
#     previous query since the attacker is spoofing the response.
# (b) We indicate that the only change in the response is the fake nameserver
#     by setting a constant value for the dnsauth variable.

# We use bcount to group all attacker events matching AtoV_resp into a single 
# instance.
#------------------------------------------------------------------------------
AtoV_resp = DNSREQRES.dns_res($VtoR_query, dnsauth='fakens.fakebofa.com')[bcount>=1]


#------------------------------------------------------------------------------
# State: The attacker sends a series of INCORRECTLY forged DNS responses (containing 
#        the fake nameserver as authority) to the victim and spoofing  as the real
#        nameserver. 
#
# This is captured by adding the constraint that dnsid guessed by the attacker
# does not match the correct dnsid in the forwarded query from VtoR. 
#------------------------------------------------------------------------------
AtoV_noresp = DNSREQRES.dns_res($VtoR_query, dnsid != $VtoR_query.dnsid)[bcount>1]

#------------------------------------------------------------------------------
# State: The real nameserver response.
#
# This is captured by importing the predefined DNS response with the additional
# constraints:
# (a) Make all values of this query dependent upon the values in the 
#     VtoR_query since this is a response to that request and all values would 
#     be appropriately dependent upon that state.
# (b) Define a constant value for the dnsauth variable 
#     indicating the correct value of dnsauth.  
#------------------------------------------------------------------------------
RtoV_resp = DNSREQRES.dns_res($VtoR_query, dnsauth='authns.bofa.com')

[behavior]
#-----------------------------------------------------------------------------
# There are four behaviors (3 failures and 1 success) we consider in the 
# model. Each behavior is a combination of the above states which correspond to 
# the 4 basic steps of the attack. 
#
# For all possible behaviors, the first two states are same. 
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Failure 1: Attacker responds with CORRECT responses but after the real 
#            nameserver responds 
#-----------------------------------------------------------------------------
b_1 = (AtoV_query ~> VtoR_query ~> RtoV_resp ~> AtoV_resp)

#-----------------------------------------------------------------------------
# Failure 2: Attacker responds with INCORRECT responses during the correct 
#            responses coming from the attacker.
# 
# The 'dur' (during) parallel operator captures the parallel responses of 
# attacker and victim.
#-----------------------------------------------------------------------------
b_2 = ((AtoV_query ~> VtoR_query) ~> (RtoV_resp dur AtoV_noresp))

#-----------------------------------------------------------------------------
# Failure 3: Attacker responds with INCORRECT responses before the real 
#            nameserver responds
#-----------------------------------------------------------------------------
b_3 = (AtoV_query ~> VtoR_query ~> AtoV_noresp ~> RtoV_resp)

#-----------------------------------------------------------------------------
# SUCCESS: Attacker responds with CORRECT response before the real 
#          nameserver responds
#-----------------------------------------------------------------------------
b_4 = (AtoV_query ~> VtoR_query ~> AtoV_resp ~> RtoV_resp)

#-----------------------------------------------------------------------------
# Group the behaviors explicity into FAILURE and SUCCESS. 
#
# Note that this grouping is useful to increase the readability of the model
# and the output. 
#-----------------------------------------------------------------------------
FAILURE = (b_1 or b_2 or b_3) 
SUCCESS = (b_4)
M = (FAILURE or SUCCESS)

[model]
DNSKAMINSKY(eventno,timestamp,timestampusec,sipaddr,dipaddr,sport,dport,dnsquesname, dnsid,dnsauth, dnsqrflag) = M

