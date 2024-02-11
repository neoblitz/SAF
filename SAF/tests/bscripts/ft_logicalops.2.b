[header]
NAMESPACE = TESTS
NAME = LOGICAL_OPS_2
QUALIFIER = {eventtype='PACKET_TCP'}
IMPORT = NET.BASE_PROTO.TCPCONNSETUP

[states]
sA = TCPCONNSETUP.tcp_pkt_syn() 
sB = TCPCONNSETUP.tcp_pkt_synack($sA)
sC = TCPCONNSETUP.tcp_pkt_ack($sA)
sD = TCPCONNSETUP.tcp_pkt_syn(dipaddr != $sA.dipaddr, sipaddr = $sA.sipaddr)[bcount>0]

[behavior]

# Total number of connections attempted by code red
b0 = (sA)

# Find all scans from a single source to a destination
b1 = (sA ~> sD)

# No acks
b4 = (sA ~> (not sB))

[model]
CODERED_NOACKS(eventno,eventtype,sipaddr,dipaddr,sport,dport,tcpflags) = b4

#sqlite> select distinct sipaddr from PACKET_TCP;
#192.168.1.1
#192.168.1.105
#192.168.1.222
#sqlite> select count(*) from  PACKET_TCP where sipaddr='192.168.1.1';
#7
#sqlite> select count(*) from  PACKET_TCP where sipaddr='192.168.1.105';
#2712
#sqlite> select count(*) from  PACKET_TCP where sipaddr='192.168.1.222';
#10

#sqlite> select eventtype,sipaddr,dipaddr,sport,dport,tcpflags from  PACKET_TCP where sipaddr='192.168.1.105' and eventno between 10 and 40;
#eventtype   sipaddr        dipaddr        sport       dport       tcpflags  
#----------  -------------  -------------  ----------  ----------  ----------
#PACKET_TCP  192.168.1.105  32.89.246.214  1029        80          2         
#PACKET_TCP  192.168.1.105  71.234.107.18  1030        80          2         
#PACKET_TCP  192.168.1.105  110.123.123.9  1031        80          2         
#PACKET_TCP  192.168.1.105  149.12.241.68  1032        80          2         
#PACKET_TCP  192.168.1.105  188.157.102.1  1033        80          2         
#PACKET_TCP  192.168.1.105  10.192.81.247  1035        80          2         
#PACKET_TCP  192.168.1.105  49.81.199.50   1036        80          2         
#PACKET_TCP  192.168.1.105  88.226.60.110  1037        80          2         
#PACKET_TCP  192.168.1.105  40.129.180.16  1038        80          2         
#PACKET_TCP  192.168.1.105  166.4.40.229   1039        80          2         
#PACKET_TCP  192.168.1.105  205.149.157.3  1040        80          2         
#PACKET_TCP  192.168.1.105  27.184.136.15  1042        80          2         
#PACKET_TCP  192.168.1.105  66.73.254.210  1043        80          2         
#PACKET_TCP  192.168.1.105  105.218.13.20  1044        80          2         
#PACKET_TCP  192.168.1.105  144.107.131.5  1045        80          2         
#PACKET_TCP  192.168.1.105  183.252.248.6  1046        80          2         
#PACKET_TCP  192.168.1.105  222.141.110.1  1047        80          2         
#PACKET_TCP  192.168.1.105  5.31.228.183   1048        80          2         
#PACKET_TCP  192.168.1.105  44.176.89.243  1049        80          2         
#PACKET_TCP  192.168.1.105  83.65.207.46   1050        80          2         
#PACKET_TCP  192.168.1.105  122.210.68.10  1051        80          2         
#PACKET_TCP  192.168.1.105  161.99.186.16  1052        80          2         
#PACKET_TCP  192.168.1.105  200.244.47.22  1053        80          2         
#PACKET_TCP  192.168.1.105  22.23.27.88    1055        80          2         
#PACKET_TCP  192.168.1.105  61.168.144.14  1056        80          2         
#PACKET_TCP  192.168.1.105  100.57.160.13  1057        80          2         
#PACKET_TCP  192.168.1.105  139.202.21.19  1058        80          2         
#PACKET_TCP  192.168.1.105  178.91.139.1   1059        80          2         
#PACKET_TCP  192.168.1.105  217.236.0.61   1060        80          2         
#PACKET_TCP  192.168.1.105  0.126.118.120  1061        80          2      
