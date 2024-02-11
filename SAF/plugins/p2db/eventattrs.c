/*-------------------------------------------------------------------------
 * eventattrs.c - Contains attribute and attribute type definitions
 * 				  for events. Currently contains for IP, UDP, TCP,
 * 				  DNS and ICMP.
 *
 * Format of attributes
 * --------------------
 * 	Each line of attribute is of the following format
 * 	<attributename attributetype>
 *
 *  Currently supported types are "integer" and "text" and they should
 *  serve most needs.
 *
 * Required Attributes
 * -------------------
 * Each event specification must have the following attributes at a minimum
 * 		"eventno integer",
 *		"eventtype text",
 *		"timestamp integer",
 *		"timestampusec integer",
 *		"origin text",
 *
 * Attribute values
 * -----------------
 * All attribute values could be empty except the eventno and eventtype
 * attributes.
 *
 *
 * Copyright (C) Arun Viswanathan (aviswana@isi.edu)
 * This software is licensed under the GPLv3 license, included in
 * ./GPLv3-LICENSE.txt in the source distribution
 *------------------------------------------------------------------------*/
#include "eventattrs.h"

char * dns_attrs[] = {
		"eventno integer",
		"eventtype text",
		"timestamp integer",
		"timestampusec integer",
		"origin text",
		"sipaddr text",
		"dipaddr text",
		"sport integer",
		"dport integer",
		"totalpacketlen integer",
		"protocol integer",
		"tos integer",
		"ipid integer",
		"ipoffset integer",
		"ipcksum integer",
		"ipttl integer",
		"udplen integer",
		"udpcksum integer",
		"dnsid integer", "dnsaa integer", "dnsopcode integer", "dnsqrflag integer", "dnsnumques integer",
		"dnsnumans integer", "dnsnumadd integer","dnsnumauth integer", "dnsquestype integer", "dnsquesname text",
		"dnsquesclass integer", "dnsansarec text", "dnsansns text", "dnsanscname text", "dnsauth text",
		"dnsaddarec text", "dnsaddns text", "dnsaddcname text"
} ;
int num_dns_attrs = sizeof(dns_attrs)  / sizeof(char*);


char *udp_attrs[] = {
		"eventno integer",
		"eventtype text",
		"timestamp integer",
		"timestampusec integer",
		"origin text",
		"sipaddr text",
		"dipaddr text",
		"sport integer",
		"dport integer",
		"totalpacketlen integer",
		"protocol integer",
		"tos integer",
		"ipid integer",
		"ipoffset integer",
		"ipcksum integer",
		"ipttl integer",
		"udplen integer",
		"udpcksum integer"
} ;
int num_udp_attrs = sizeof(udp_attrs)  / sizeof(char*);


char * ip_attrs[] = {
		"eventno integer",
		"eventtype text",
		"timestamp integer",
		"timestampusec integer",
		"origin text",
		"sipaddr text",
		"dipaddr text",
		"totalpacketlen integer",
		"protocol integer",
		"tos integer",
		"ipid integer",
		"ipoffset integer",
		"ipcksum integer",
		"ipttl integer"
} ;
int num_ip_attrs = sizeof(ip_attrs)  / sizeof(char*);

char *tcp_attrs[] = {
		"eventno integer",
		"eventtype text",
		"timestamp integer",
		"timestampusec integer",
		"origin text",
		"sipaddr text",
		"dipaddr text",
		"sport integer",
		"dport integer",
		"totalpacketlen integer",
		"protocol integer",
		"tos integer",
		"ipid integer",
		"ipoffset integer",
		"ipcksum integer",
		"ipttl integer",
		"tcpseq integer",
		"tcpack integer",
		"tcpflags integer"
} ;
int num_tcp_attrs = sizeof(tcp_attrs)  / sizeof(char*);


char *icmp_attrs[] = {
		"eventno integer",
		"eventtype text",
		"timestamp integer",
		"timestampusec integer",
		"origin text",
		"sipaddr text",
		"dipaddr text",
		"totalpacketlen integer",
		"protocol integer",
		"tos integer",
		"ipid integer",
		"ipoffset integer",
		"ipcksum integer",
		"ipttl integer",
		"icmptype integer",
		"icmpcode integer",
		"icmpcksum integer"
} ;
int num_icmp_attrs = sizeof(icmp_attrs)  / sizeof(char*);

char *apphttpd_attrs[] = {
		"eventno integer",
		"eventtype text",
		"timestamp integer",
		"timestampusec integer",
		"origin text",
		"sipaddr text",
		"httpreq text",
		"httpstatus integer",
		"contentlength integer",
		"process text",
} ;
int num_apphttpd_attrs = sizeof(apphttpd_attrs)  / sizeof(char*);
