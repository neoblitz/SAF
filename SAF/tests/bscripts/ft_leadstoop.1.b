#
# Independent state leading to independent state
#
[header]
NAMESPACE = NET.BASE_PROTO
NAME = FT_LEADSTOOPS
QUALIFIER = {}

[states]
# Independent state
ip_pkt_sd = {sipaddr = $1, dipaddr = $2, protocol=$3}

# Constant state
ip_pkt_cons = {sipaddr = '192.168.1.51'}

# Dependent state
ip_pkt_ds = {sipaddr = $ip_pkt_sd.dipaddr , 
             dipaddr = $ip_pkt_sd.sipaddr, 
             protocol=$ip_pkt_sd.protocol}


[behavior]

# Independent state leadsto a constant state
b_1 = ip_pkt_sd ~>ip_pkt_cons

# Independent state leadsto a dependent state
b_2 = (ip_pkt_sd ~>[<1s] ip_pkt_ds)

# Independent state leadsto a constant state but with grouping
b_3 = ((ip_pkt_sd) ~> (ip_pkt_cons))

# Independent state leadsto a dependent state
b_4 = ((((((((((ip_pkt_sd ~>ip_pkt_cons))))))))))

# Individual state
b_5 = ((((((((((ip_pkt_sd))))))))))

# Individual states
b_6 = (ip_pkt_sd)

[model]
PKTPAIR(eventno, eventtype, timestamp, timestampusec, sipaddr, dipaddr, protocol, sport) = (b_1 or b_2 or b_3 or b_4 or b_5 or b_6)
