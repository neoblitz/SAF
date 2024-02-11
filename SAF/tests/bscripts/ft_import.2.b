[header]
NAMESPACE = TESTS
NAME = CONC_IPFLOWS_2
QUALIFIER = { eventtype='PACKET_TCP'}
IMPORT = NET.BASE_PROTO.IPPKTPAIR

[states]
flow_a = IPPKTPAIR.IP_PKTPAIR(dipaddr='204.11.246.48', sipaddr='*')
flow_b = IPPKTPAIR.IP_PKTPAIR(dipaddr=$flow_a.dipaddr)

[behavior]
# INIT is prepended to all behaviors by default
b = (flow_a olap flow_b)

[model]
CONCIPFLOW(eventno, eventtype,sipaddr, dipaddr, protocol) = b 