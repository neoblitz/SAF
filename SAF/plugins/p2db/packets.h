/*-----------------------------------------------------------------------------
 * packets.h - Packet structure definitions, relevant macros and functions
 * 			   for parsing individual packets
 *
 * Copyright (C) Arun Viswanathan (aviswana@isi.edu)
 * This software is licensed under the GPLv3 license, included in
 * ./GPLv3-LICENSE.txt in the source distribution
 *---------------------------------------------------------------------------*/

#ifndef PACK_H_
#define PACK_H_

#define SIZE_NULLLOOPBACK 4
#define AFAMILY_IPV4_NO 0x00000002
#define AFAMILY_IPV4_HO 0x02000000
struct nullloopback{
	u_int afamily;
};


/*
 * Following packet structures are taken from
 * http://www.tcpdump.org/pcap.htm
 */

/* Ethernet addresses are 6 bytes */
#define ETHER_ADDR_LEN  6
#define SIZE_ETHERNET 14


#define ETHERTYPE_IP    0x0800
/* Ethernet header */
struct sniff_ethernet
{
	u_char ether_dhost[ETHER_ADDR_LEN]; /* Destination host address */
	u_char ether_shost[ETHER_ADDR_LEN]; /* Source host address */
	u_short ether_type; /* IP? ARP? RARP? etc */
};

/* IP header */
struct sniff_ip
{
	u_char ip_vhl; /* version << 4 | header length >> 2 */
	u_char ip_tos; /* type of service */
	u_short ip_len; /* total length */
	u_short ip_id; /* identification */
	u_short ip_off; /* fragment offset field */
#define IP_RF 0x8000        /* reserved fragment flag */
#define IP_DF 0x4000        /* dont fragment flag */
#define IP_MF 0x2000        /* more fragments flag */
#define IP_OFFMASK 0x1fff   /* mask for fragmenting bits */
	u_char ip_ttl; /* time to live */
	u_char ip_p; /* protocol */
	u_short ip_sum; /* checksum */
	struct in_addr ip_src, ip_dst; /* source and dest address */
};
#define IP_HL(ip)       (((ip)->ip_vhl) & 0x0f)
#define IP_V(ip)        (((ip)->ip_vhl) >> 4)

/* TCP header */
struct sniff_tcp
{
	u_short th_sport; /* source port */
	u_short th_dport; /* destination port */
	u_int th_seq; /* sequence number */
	u_int th_ack; /* acknowledgement number */

	u_char th_offx2; /* data offset, rsvd */
#define TH_OFF(th)  (((th)->th_offx2 & 0xf0) >> 4)
	u_char th_flags;
#define TH_FIN 0x01
#define TH_SYN 0x02
#define TH_RST 0x04
#define TH_PUSH 0x08
#define TH_ACK 0x10
#define TH_URG 0x20
#define TH_ECE 0x40
#define TH_CWR 0x80
#define TH_FLAGS (TH_FIN|TH_SYN|TH_RST|TH_ACK|TH_URG|TH_ECE|TH_CWR)
	u_short th_win; /* window */
	u_short th_sum; /* checksum */
	u_short th_urp; /* urgent pointer */
};

struct sniff_udp
{
	u_short uh_sport; /* source port */
	u_short uh_dport; /* destination port */
	u_short uh_ulen; /* udp length */
	u_short uh_sum; /* udp checksum */
};

struct sniff_icmp
{
	u_char type; /* Type */
	u_char code; /* Code */
	u_short checksum; /* Checksum */
};

/**
 *Credits for DNS: http://www.codeproject.com/KB/IP/dns_query.aspx
 * 				  http://www.netfor2.com/dns.htm
 */

typedef struct
{
	unsigned id :16; /* query identification number */
#if BYTE_ORDER == BIG_ENDIAN
	/* fields in third byte */
	unsigned qr :1; /* response flag */
	unsigned opcode :4; /* purpose of message */
	unsigned aa :1; /* authoritive answer */
	unsigned tc :1; /* truncated message */
	unsigned rd :1; /* recursion desired */
	/* fields in fourth byte */
	unsigned ra :1; /* recursion available */
	unsigned unused :3; /* unused bits (MBZ as of 4.9.3a3) */
	unsigned rcode :4; /* response code */
#endif
#if BYTE_ORDER == LITTLE_ENDIAN || BYTE_ORDER == PDP_ENDIAN
	/* fields in third byte */
	unsigned rd :1; /* recursion desired */
	unsigned tc :1; /* truncated message */
	unsigned aa :1; /* authoritive answer */
	unsigned opcode :4; /* purpose of message */
	unsigned qr :1; /* response flag */
	/* fields in fourth byte */
	unsigned rcode :4; /* response code */
	unsigned unused :3; /* unused bits (MBZ as of 4.9.3a3) */
	unsigned ra :1; /* recursion available */
#endif
	/* remaining bytes */
	unsigned qdcount :16; /* number of question entries */
	unsigned ancount :16; /* number of answer entries */
	unsigned nscount :16; /* number of authority entries */
	unsigned arcount :16; /* number of resource entries */
} dnsheader;

typedef struct
{
	unsigned short qtype;
	unsigned short qclass;
} dnsquestion;

typedef struct
{
	unsigned short type;
	unsigned short _class;
	unsigned int ttl;
	unsigned short data_len;
} dnsrdata;
#define DNS_RDATA_LENGTH 10
/** Length is defined as a macro to get over compiler structure packing.
 * FIXME: Use GCC macros to prevent this */

typedef struct
{
	unsigned char *name;
	dnsrdata *resource;
	unsigned char *rdata;
} dnsresrecord;

typedef struct
{
	unsigned char *name;
	dnsquestion *ques;
} dnsquery;

/**
 * Function Defines
 */

int process_ip(const struct sniff_ip *ip, ght_hash_table_t * kvhash);
int process_tcp(const struct sniff_tcp *tcp, ght_hash_table_t *kvhash);
int process_udp(const struct sniff_udp *udp, ght_hash_table_t *kvhash);
int process_dns(const dnsheader *dns, ght_hash_table_t *kvhash);
int process_icmp(const struct sniff_icmp *icmp, ght_hash_table_t *kvhash);
unsigned char * convert_from_dnsformat(unsigned char *reader,
		unsigned char *buffer, int *count);

#endif
