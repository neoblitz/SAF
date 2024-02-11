#
# Multiple anonymous states
#
[header]
NAMESPACE = TESTS
NAME = FT_QUALIFIER_4
QUALIFIER = {eventtype='PACKET_TCP'}  or {eventtype='PACKET_UDP'} or {eventtype='PACKET_DNS'}

[states]
ip_pkt_sd = {sipaddr = $1, dipaddr = $2, protocol=$3}
ip_pkt_ds = {sipaddr = $ip_pkt_sd.dipaddr , dipaddr = $ip_pkt_sd.sipaddr, protocol=$ip_pkt_sd.protocol}

[behavior]
# INIT is prepended to all behaviors by default
b = ip_pkt_sd ~> ip_pkt_ds

[model]
IP_PKTPAIR(eventno, eventtype, timestamp, timestampusec, sipaddr, dipaddr, protocol) = b 