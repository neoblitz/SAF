"""
	Grammar Parsing Tests
"""

import sys
from simpleparse.common import numbers, strings, comments
from simpleparse.parser import Parser
from simpleparse.error import ParserSyntaxError
from simpleparse import generator

test_behaviors = [
	["S1 ~> S2\n", ""], 
	["S1 ~> S2 ~> S3 ~> S4",""],
	["S1 ~> (S2 ~> S3) ~> S4",""],
	["(S1 ~> S2 ~> S3 ~> S4)",""],
	["S1 ~> (S2) ~> S3 ~> (S4)",""],
	["(S1 ~> (S2) ~> S3 ~> (S4))",""],
	["S1 ~> S2 ~> S3 ~> S4 ~>S5 ~>(S6 or S7)~>(not S8)",""],
	["S1 ~>[<=10s] S2\n",""],
	["S1 ~>[> 10s] S2 ~> S3 ~> S4\n",""],
	["(S1 xor S2) [duration=0s]\n",""],
	["S1 ~> not S2\n",""],
	["S1 ~> (not S2)\n",""],
	["(S1 ~> S2) ~> (S3 ~> S4)",""],
	["(S1 and S2) ~> (S3 or S4)",""],
	["S1~>(S2 xor S3)\n",""],
	["S1 ~> ( S2 and S3 )\n",""],
	["(S1) [rate = 10]\n",""],
	["( S1 ~> S2 )[icount = 10]\n",""],
	["S ~> ( Sn )[bcount = 10]\n",""],
	["not S1\n",""],
	["( [] S1 )[duration=1s]",""],
	["(S ~> ( Sn )[bcount = 10])[icount=60s]",""],
	["(S ~> ( S1 and (S2 or S3) ))",""],
	["(S1 ~> [<= 37 ms](S2) ~> [< 50 s] S3)",""],
	["((S1) ~> [>= 370000ms] (S2 ~> [< 50ms] S3))",""],
	["{eventtype='PACKET_TCP'} or {eventtype='PACKET_UDP'}",""],
	["{eventtype='PACKET_TCP'} [_limit = 100]",""],
	["{eventtype='PACKET_TCP'} [_lmit >= 100]","ParserSyntaxError"],
	["{eventtype='PACKET_TCP' [_lmit >= 100]","ParserSyntaxError"],
	["a9 = ((tcp_pkt_syn) ~>[>= 90 ms] (tcp_pkt_synack) ~>[>= 0.045ms ] (tcp_pkt_ack))",""],
	["b_11 = ip_pkt_sd))",""],
	["PKTPAIR = (b_11 or)",""],
	["{eventtype='PACKET_TCP'}[_eventno=1000:2000]",""],
	["b3 = (sA ~> sB ~> (not sC))", ""],
	["{eventtype='PACKET_TCP'}[_eventno= -1000:2000]","ParserSyntaxError"]
	]

test_states = [
	["{a=10}",""],
	["{a=10, b=20}",""],
	["{ }",""],
	["{ a = 10, b =20, c=30, d=500}",""],
	["{ a = '10', b ='TEXT'}",""],
	["DNS.req()",""],
	["DNS.req( a=10, b=20)",""],
	["DNS.req( $TEST, a=10, b=20)",""],
	["DNS.req( $TEST)",""],
	["DNS.req( $TEST, a=$TEST.a)",""],
	["DNS.req( $TEST, a>$TEST.a)",""],
	["{a=$X.a, b=$X.b}",""],
	["DNS.req(a=10)[bcount >= 1]",""],
	["{a=10, b=20}[bcount>=1]",""],
	["{eventtype='PACKET_DNS'}",""],
	["{eventtype='PACKET_DNS',\
		a=100}",""],
	["DNS.req($TEST, a='fakeboka.com~~')",""],
	["DNS.req(a=$$)[bcount>1]",""],
	["{eventype=XX","ParserSyntaxError"],
	["{eventtype='PACKET_TCP'}[_eventno= --1000:2000]","ParserSyntaxError"],
	["not {a=10}", ""],
	["not TCPFLOW.TCPFLOW()", ""]
	]


def run_parser(ebnffile, production, testlist):
	decl = open(ebnffile).read()
	parser = Parser(decl)

	overall_status = True
	for (test_data,test_expectation) in testlist:
		try:
			sys.stderr.write("Parsing '%s'\n" % (test_data.rstrip('\n')))
			success, children, nextcharacter = \
		 					parser.parse(test_data,
										production=production)
			if (not success): 
				print """\t\tWasn't able to parse %s as %s (%s chars parsed of %s) returned value was %s""" %\
								 (repr(test_data),
									production,
									nextcharacter,
									len(test_data),
									(success, children, nextcharacter))
		except ParserSyntaxError as pse:
			t = """\tSyntax Error: Expected : %(expected)s Got : %(text)s"""
		 	print pse.messageFormat(template=t)
		 	success = False
			if(type(pse).__name__ == test_expectation):
					success = True
		except SyntaxError as se:
			#t = """Syntax Error: Expected : %(expected)s Got : %(text)s"""
		 	print se
		 	success = False
			if(type(se).__name__ == test_expectation):
					success = True
		except Exception as ex:
			print ex
		 	success = False			

	 	overall_status = overall_status and success
	return overall_status


def run_behavior_parse_tests(ebnffile):
	production = "behavior_decl"
	return run_parser(ebnffile, production, test_behaviors)
	
def run_state_parse_tests(ebnffile):
	production = "state_decl"
	return run_parser(ebnffile, production, test_states)


