[header]
NAMESPACE = TESTS
NAME = LOGICAL_OPS_3
QUALIFIER = {}
IMPORT = NET.BASE_PROTO.TCPFLOW

[states]
all = {eventtype='*'}
sA = {sipaddr='192.168.1.51'}

# Need everything except events with sipaddr=192.168.1.51
sB = not {sipaddr='192.168.1.51'}

# Need everything but instances matching TCPFLOWS()
sC = TCPFLOW.TCPFLOW()
sD = not TCPFLOW.TCPFLOW()

[behavior]
b0 = (all)
b1 = (sA)
b2 = (sB)
b3 = (sC)
b4 = (sD)
 
[model]
#B0(eventno,eventtype,sipaddr,dipaddr,sport,dport,tcpflags) = b0
#B1(eventno,eventtype,sipaddr,dipaddr,sport,dport,tcpflags) = b1
#B2(eventno,eventtype,sipaddr,dipaddr,sport,dport,tcpflags) = b2
#B4(eventno,eventtype,sipaddr,dipaddr,sport,dport,tcpflags) = b3
B5(eventno,eventtype,sipaddr,dipaddr,sport,dport,tcpflags) = b4