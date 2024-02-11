#
# Syntax Errors 
#
[header]
NAMESPACE = NET.BASE_PROTO
NAME = SYNTAX_ERROR_TEST_1
QUALIFIER = {}

[states]

# Missing parenthesis at the end
ip_pkt_sd = {sipaddr = $1, dipaddr = $2, protocol=$3

[behavior]

[model]
PKTPAIR = (b_1 or b_2 or b_3 or b_4 or b_5 or b_6)
