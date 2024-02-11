[header]
NAMESPACE = EXAMPLES
NAME = STATES
QUALIFIER = { }[_eventno=1:20]
IMPORT = NET.APP_PROTO.DNSREQRES

[states]
state_A  = {sipaddr = '10.1.11.2', dipaddr='10.1.4.2'}
state_B  = {sport > 53}
state_C  = {sipaddr=$state_A.dipaddr}
state_D  = {sport=$state_B.sport, dnsqrflag=1}
state_E = DNSREQRES.dns_req()
state_F = DNSREQRES.DNS_REQ_RES()
state_G = DNSREQRES.DNS_REQ_RES(sport > 30000)
state_H  = {sipaddr='10.1.*'}

[behavior]
# For now it is important to include the definition of the state on which the 
# dependent state is dependent  
b1 = (state_A  and state_C)
b2 = (state_B and  state_D)

[model]
CONSTANT_STATES_1(eventno, eventtype, sipaddr, dipaddr, sport, dport) = (state_A)
CONSTANT_STATES_2(eventno, eventtype, sipaddr, dipaddr, sport, dport) = (state_B)
DEPENDENT_STATES_1(eventno, eventtype, sipaddr, dipaddr, sport, dport) = b1
DEPENDENT_STATES_2(eventno, eventtype, sipaddr, dipaddr, sport, dport) = b2
IMPORTING_STATES(eventno, eventtype, sipaddr, dipaddr, sport, dport) = state_E
IMPORTING_BEHAVIORS_AS_STATE(eventno, eventtype, sipaddr, dipaddr, sport, dport) = state_F
IMPORTING_BEHAVIORS_AS_STATE_W_CUSTOMIZATION(eventno, eventtype, sipaddr, dipaddr, sport, dport) = state_G
WILDCARDING(eventno, eventtype, sipaddr, dipaddr, sport, dport) = state_H 