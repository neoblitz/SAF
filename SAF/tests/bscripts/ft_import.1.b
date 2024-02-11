[header]
NAMESPACE = TESTS
NAME = CONC_IPFLOWS_1
QUALIFIER = { eventtype='PACKET_TCP'} or {eventtype='PACKET_UDP'}
IMPORT = NET.BASE_PROTO.IPPKTPAIR

[states]
flow_s2d = IPPKTPAIR.ip_pkt_sd(sipaddr='*')
flow_a = IPPKTPAIR.IP_PKTPAIR(dipaddr='204.11.246.48', sipaddr='*')
flow_b = IPPKTPAIR.IP_PKTPAIR()
flow_c = {IPPKTPAIR.IP_PKTPAIR()}

[behavior]
# INIT is prepended to all behaviors by default
b = (flow_a olap flow_b)
singlepackets = flow_s2d

[model]
S2D(eventno,eventtype,sipaddr,dipaddr) = singlepackets 
FLOW_A(eventno,eventtype,sipaddr,dipaddr) = flow_a
FLOW_B(eventno,eventtype,sipaddr,dipaddr) = flow_b
CONCIPFLOW(eventno, eventtype,sipaddr, dipaddr, protocol) = b 