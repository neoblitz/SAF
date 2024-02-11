#
# Syntax Errors 
#
[header]
NAMESPACE = NET.BASE_PROTO
NAME = SYNTAX_ERROR_TEST_3
QUALIFIER = { } [_eventno >= asdasdasd ]

[states]

# Missing parenthesis
ip_pkt_sd = {sipaddr = $1, dipaddr = $2, protocol=$3}

# 
[behavior]
b_11 = (ip_pkt_sd))))

[model]
PKTPAIR = (b_11 or)
