[header]
NAMESPACE = TESTS
NAME = FT_LEADSTO_OP_3
QUALIFIER = {eventtype='PACKET_TCP'}
IMPORT = NET.BASE_PROTO.TCPCONNSETUP

[states]
sA = TCPCONNSETUP.tcp_pkt_syn() 
sD = TCPCONNSETUP.tcp_pkt_syn(dipaddr != $sA.dipaddr, sipaddr = $sA.sipaddr)[bcount>0]

[behavior]
# Total number of connections attempted by code red
b0 = (sA)

# Find all scans from a single source to a destination
b1 = (sA ~> sD)


[model]
CODERED_NOACKS(eventno,eventtype,sipaddr,dipaddr,sport,dport,tcpflags) = (b0 or b1)
