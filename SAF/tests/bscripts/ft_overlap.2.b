

[header]
NAMESPACE = TESTS
NAME = FT_OVERLAP_2
QUALIFIER = {eventtype='PACKET_TCP'}
IMPORT = NET.BASE_PROTO.IPPKTPAIR

[states]
state_a = {sipaddr='192.168.1.51'}[bcount >1]
state_b = {sipaddr !='192.168.1.51'}[bcount>1]

[behavior]
# INIT is prepended to all behaviors by default
b = (state_b dur state_a) 

[model]
OVERLAPS(eventno, sipaddr, dipaddr, protocol) = b 