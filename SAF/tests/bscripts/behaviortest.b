[header]
NAMESPACE = BEHAVIOR.TEST
NAME = BEHAVIORS
QUALIFIER = {}
IMPORT = NET.BASE_PROTO.IPPKTPAIR

[states]
S1 = IPPKTPAIR.ip_pkt_sd()
S2 = IPPKTPAIR.ip_pkt_sd(dipaddr=$S1.dipaddr) 
S3 = IPPKTPAIR.ip_pkt_sd() 

[behavior]
b1 = S1 ~> S2,
b2 = S1 ~>[within 10s] S2
b3 = (S1, S2) [window=0s]
b4 = S1 ~> ! S2
b5 = S1 ~> (! S2)
b6 = S1~>(S2,S3)
b7 = S1 ~> ( S2 | S3 )
b8 = (S1) [count = 10]
b9 = ( S1 ~> S2 )[count = 10]
b10 = S1 ~> ( S2 )[count = 10]
b11 = (!S1)
b12 = <> S2 
b13 = ( [] S1 )[epoch=1s]
b14 = (S1 ~> ( S2 )[count = 10])[window=60s]
	
[spec]
BTEST = b1 || b2 || b3
	