[header]
NAMESPACE = TESTS
NAME = FT_LEADSTO_OP_4
QUALIFIER = {eventtype='PACKET_ICMP'}[_limit=100]
IMPORT = NET.BASE_PROTO.IPPKTPAIR

[states]
sA = IPPKTPAIR.ip_pkt_sd()
sB = IPPKTPAIR.ip_pkt_sd(dipaddr=$sA.dipaddr)[bcount>1]

[behavior]
b = sA ~>[<=1s]((sB)[bcount >= 59])

[model]
DDOSATTACK(eventno,timestamp,timestampusec,sipaddr,dipaddr,eventtype) = b
