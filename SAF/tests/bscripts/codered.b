[header]
NAMESPACE = TEST
NAME = CODERED
QUALIFIER = {eventtype='PACKET_TCP'}
IMPORT = NET.BASE_PROTO.TCPCONNSETUP

[states]
sA = TCPCONNSETUP.tcp_pkt_syn() 
sB = TCPCONNSETUP.tcp_pkt_synack($sA)
sC = TCPCONNSETUP.tcp_pkt_ack($sA)
sD = TCPCONNSETUP.tcp_pkt_syn(dipaddr != $sA.dipaddr, sipaddr = $sA.sipaddr)

[behavior]

# Total number of connections attempted by code red
b0 = (sA)
b1 = (sA ~> sD)

# Get number of complete connections
b2 = (sA ~> sB ~> sC)

# Get number of half open connections
b3 = (sA ~> sB ~> (not sC))

# No acks
b4 = (sA ~> (not sB))

[model]
CODERED_NUM_CONNS(sipaddr,dipaddr,sport,dport,tcpflags) = b1
#CODERED_COMPLETE_CONNS(sipaddr,dipaddr,sport,dport,tcpflags) = b2
#CODERED_NOACKS(sipaddr,dipaddr,sport,dport,tcpflags) = b4
#CODERED_HALFOPEN_CONNS = b3 
#CODERED_OVERLAP_CONNS(sipaddr,dipaddr,sport,dport,tcpflags) = b5
 