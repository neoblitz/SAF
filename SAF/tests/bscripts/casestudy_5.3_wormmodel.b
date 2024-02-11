[header]
NAMESPACE = TESTS
NAME = WORMSPREAD
QUALIFIER = { }

[states]
scan_A = {eventtype = SCAN, sipaddr= $infect_A.host, dipaddr=$1} 
infect_A = {eventtype=INFECT, host=$scan_A.dst}

[behavior]
single_spread= (scan_A ~> infect_A)
spread_chain = (single_spread ~> spread_chain)

[model]
#WORM = single_spread
WORM = spread_chain
