#
# Independent state leading to dependent state
#
[header]
NAMESPACE = TESTS
NAME = FT_LEADSTOOP_2
QUALIFIER = {}[_limit=100]

[states]
ip_pkt_sd = {sipaddr = $1, dipaddr = $2, protocol=$3}
ip_pkt_cons = {sipaddr =  '201.199.184.56'}

[behavior]
# INIT is prepended to all behaviors by default
b = (ip_pkt_sd ~>ip_pkt_cons)

[model]
PKTPAIR(eventno, eventtype, timestamp, timestampusec, sipaddr, dipaddr, protocol, sport) = b 