/*-------------------------------------------------------------------------
 * eventattrs.h - Contains extern definitions to be used from other modules
 *
 * Copyright (C) Arun Viswanathan (aviswana@isi.edu)
 * This software is licensed under the GPLv3 license, included in
 * ./GPLv3-LICENSE.txt in the source distribution
 *------------------------------------------------------------------------*/
#ifndef  EVENTATTR_H__
#define EVENTATTR_H__

extern char *udp_attrs[], *ip_attrs[], *tcp_attrs[], *icmp_attrs[],
		*dns_attrs[], *apphttpd_attrs[];
extern int num_udp_attrs, num_ip_attrs, num_icmp_attrs, num_tcp_attrs,
		num_dns_attrs, num_apphttpd_attrs;

/** Defines for event types */
#define EVENT_IP	"PACKET_IP"
#define EVENT_TCP	"PACKET_TCP"
#define EVENT_UDP	"PACKET_UDP"
#define EVENT_ICMP	"PACKET_ICMP"
#define EVENT_DNS	"PACKET_DNS"
#define EVENT_APP_HTTPD	"APP_HTTPD"
#endif
