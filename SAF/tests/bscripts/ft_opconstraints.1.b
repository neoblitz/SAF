#
# Leadsto with operator constraints
#
[header]
NAMESPACE = TESTS
NAME = FTP_OPCONSTRAINTS_1
QUALIFIER = {eventtype='PACKET_TCP'}
IMPORT = NET.BASE_PROTO.TCPPKTPAIR

[states]
tcp_pkt_syn =  TCPPKTPAIR.tcp_pkt_sd( tcpflags=2 ) 
tcp_pkt_synack = TCPPKTPAIR.tcp_pkt_ds($tcp_pkt_syn,  tcpflags=18) 
tcp_pkt_ack =  TCPPKTPAIR.tcp_pkt_sd($tcp_pkt_syn,  tcpflags=16 ) 
 
[behavior]
#-------------------------------------
# Tests for '<='
#-------------------------------------

# Success
b1 = tcp_pkt_syn ~>[<= 1.0s] tcp_pkt_synack ~> tcp_pkt_ack
b2 = tcp_pkt_syn ~>[<= 500 ms] tcp_pkt_synack ~> (tcp_pkt_ack)

# This should return records. The exact difference between test events 10 and 
# 17 is 92.32ms 
b4 = tcp_pkt_syn ~>[<= 92.32 ms] tcp_pkt_synack ~> tcp_pkt_ack

# These will PASS too
b5 = tcp_pkt_syn ~>[<=370 ms] (tcp_pkt_synack ~> tcp_pkt_ack)
b6 = tcp_pkt_syn ~> (tcp_pkt_synack ~>[<=500ms] tcp_pkt_ack)
b7 = (tcp_pkt_syn ~> tcp_pkt_synack ~>[<=500ms] tcp_pkt_ack)
b8 = (tcp_pkt_syn ~> [<=370ms] tcp_pkt_synack ~>[<=100ms] tcp_pkt_ack)
b9 = (tcp_pkt_syn ~> (tcp_pkt_synack ~>[<=10ms] tcp_pkt_ack))

b11 = ((tcp_pkt_syn) ~> (tcp_pkt_synack ~> [<= 0ms] tcp_pkt_ack))
b12 = ((tcp_pkt_syn) ~>[<= 0.370000ms] (tcp_pkt_synack ~>[<= 60ms] tcp_pkt_ack))
b13 = (tcp_pkt_syn ~> [<=  370ms] tcp_pkt_synack ~>[<= 0ms] tcp_pkt_ack)
b14 = ((tcp_pkt_syn) ~> (tcp_pkt_synack) ~> (tcp_pkt_ack))

# Failures
b3 = tcp_pkt_syn ~>[<= 1 ms] tcp_pkt_synack ~> (tcp_pkt_ack)
b10 = (tcp_pkt_syn ~>[<= 1 ms] (tcp_pkt_synack ~>[<= 0.0001s] tcp_pkt_ack))

#-------------------------------------
# Tests for '>=' / > 
#-------------------------------------

# Failures 
a1 = tcp_pkt_syn ~>[>= 1s] tcp_pkt_synack ~> tcp_pkt_ack
a2 = tcp_pkt_syn ~>[> 1ms] tcp_pkt_synack ~>[>= 0.01 ms] (tcp_pkt_ack)
a7 = (tcp_pkt_syn ~> tcp_pkt_synack ~>[>= 100ms] tcp_pkt_ack)
a5 = tcp_pkt_syn ~>[> 10 ms] (tcp_pkt_synack ~> tcp_pkt_ack)

# Success
a3 = tcp_pkt_syn ~>[> 90 ms] tcp_pkt_synack ~> (tcp_pkt_ack)
a4 = tcp_pkt_syn ~>[>= 90 ms] tcp_pkt_synack ~>[> 0.040 ms] (tcp_pkt_ack)
a6 = tcp_pkt_syn ~> (tcp_pkt_synack ~>[>= 40 ms] tcp_pkt_ack)
a8 = (tcp_pkt_syn ~> [>= 22ms] tcp_pkt_synack ~>[>= 0ms] tcp_pkt_ack)
a9 = ((tcp_pkt_syn)~>[ >=90ms] (tcp_pkt_synack) ~>[ >= 0.045ms ] (tcp_pkt_ack))


#-------------------------------------
# Tests combining 'within' and 'after'
#-------------------------------------
# Success
aw1 = tcp_pkt_syn ~>[>90ms] tcp_pkt_synack ~>[<=500ms] tcp_pkt_ack
aw3 = ((tcp_pkt_syn) ~>[>=90ms] (tcp_pkt_synack) ~>[<= 0.22 s] (tcp_pkt_ack))

# Failure
aw2 = tcp_pkt_syn ~>[<=92.0ms] tcp_pkt_synack ~>[>0.1ms] (tcp_pkt_ack)

[model]
TCP_CONNSETUP_WITHIN(eventno,timestamp,timestampusec) =  (b1 or b2 or b4 or b5 or b6 or b7 or b8 or b9 or b11 or b12 or b13 or b14 or b3 or b10)
TCP_CONNSETUP_AFTER(eventno,timestamp,timestampusec) =  (a1 or a2 or a3 or a4 or a5 or a6 or a7 or a8 or a9) 
TCP_CONNSETUP_WITHIN_AFTER =  aw1 or aw2 or aw3
 