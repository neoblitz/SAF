/*-------------------------------------------------------------------------
 * ip.c - Parses an IP packet
 *
 * Copyright (C) Arun Viswanathan (aviswana@isi.edu)
 * This software is licensed under the GPLv3 license, included in
 * ./GPLv3-LICENSE.txt in the source distribution
 *------------------------------------------------------------------------*/
#include "headers.h"
#include "globals.h"
#include "eventattrs.h"
#include "packets.h"
#include "logging.h"
/*-----------------------------------------------------------------------------
 * process_ip - Parses a IP packet and stored its contents as a hash of
 * 				values indexed by attributes
 *
 * Inputs
 *      @p   	   - Pointer to the start of IP header
 *      @kvhash    - Pointer to hashtable
 *
 * Returns
 *      SUCCESS / FAILURE
 *---------------------------------------------------------------------------*/
int process_ip(const struct sniff_ip *ip, ght_hash_table_t * kvhash)
{
	int status = SUCCESS;
	char tbuf[MAX_TBUF_SIZE];
	//const struct sniff_ip *ip;

/*
    int len_link_header = 0;
	struct nullloopback *nullhdr = (struct nullloopback*) (p->packet);

	if((ntohl(nullhdr->afamily) ==  AFAMILY_IPV4_HO) ||
		(htonl(nullhdr->afamily) ==  AFAMILY_IPV4_NO) ){
		ip = (struct sniff_ip*) (p->packet + SIZE_NULLLOOPBACK);
		len_link_header = SIZE_NULLLOOPBACK;
	} else{
    	 Discard packets that are not IPV4 
		ip = (struct sniff_ip*) (p->packet + SIZE_ETHERNET);
		len_link_header = SIZE_ETHERNET;
	}
*/
	u_int size_ip = IP_HL(ip) * 4;
	if (size_ip < 20)
	{
		DEBUGLOG("   * Invalid IP header length: %u bytes\n", size_ip);
		status = FAILURE;
		goto end;
	}

	if (ght_insert(kvhash, strdup(inet_ntoa(ip->ip_src)),
			strlen("sipaddr") + 1, "sipaddr") < 0)
	{ //Source IP
		status = FAILURE;
		goto end;
	}

	if (ght_insert(kvhash, strdup(inet_ntoa(ip->ip_dst)),
			strlen("dipaddr") + 1, "dipaddr") < 0)
	{ //Dest IP
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%d", ip->ip_tos);
	if (ght_insert(kvhash, strdup(tbuf), strlen("tos") + 1, "tos") < 0)
	{ //Type of Service
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ntohs(ip->ip_len));
	if (ght_insert(kvhash, strdup(tbuf), strlen("totalpacketlen") + 1,
			"totalpacketlen") < 0)
	{ //Total Packet Len
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ip->ip_p);
	if (ght_insert(kvhash, strdup(tbuf), strlen("protocol") + 1, "protocol")
			< 0)
	{ //IP Protocol
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ntohs(ip->ip_id));
	if (ght_insert(kvhash, strdup(tbuf), strlen("ipid") + 1, "ipid") < 0)
	{ //IP ID
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ntohs(ip->ip_off));
	if (ght_insert(kvhash, strdup(tbuf), strlen("ipoffset") + 1, "ipoffset")
			< 0)
	{ //IP Offset
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ntohs(ip->ip_sum));
	if (ght_insert(kvhash, strdup(tbuf), strlen("ipcksum") + 1, "ipcksum") < 0)
	{ //IP Cksum
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ip->ip_ttl);
	if (ght_insert(kvhash, strdup(tbuf), strlen("ipttl") + 1, "ipttl") < 0)
	{ //IP TTL
		status = FAILURE;
		goto end;
	}
	end: return status;
}
