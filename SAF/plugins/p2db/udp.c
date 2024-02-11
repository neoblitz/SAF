/*-------------------------------------------------------------------------
 * udp.c - Parses a UDP packet
 *
 * Copyright (C) Arun Viswanathan (aviswana@isi.edu)
 * This software is licensed under the GPLv3 license, included in
 * ./GPLv3-LICENSE.txt in the source distribution
 *------------------------------------------------------------------------*/

#include "headers.h"
#include "globals.h"
#include "eventattrs.h"
#include "packets.h"

/*-----------------------------------------------------------------------------
 * process_udp - Parses a UDP packet and stores its contents as a hash of
 * 				 values indexed by attributes
 *
 * Inputs
 *      @udp 	   - Pointer to start of UDP packet
 *      @kvhash    - Pointer to hashtable
 *
 * Returns
 *      SUCCESS / FAILURE
 *---------------------------------------------------------------------------*/
int process_udp(const struct sniff_udp *udp, ght_hash_table_t *kvhash)
{
	int status = SUCCESS;
	char tbuf[512];
	sprintf(tbuf, "%u", ntohs(udp->uh_sport));
	if (ght_insert(kvhash, strdup(tbuf), strlen("sport") + 1, "sport") < 0)
	{ //Source Port
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ntohs(udp->uh_dport));
	if (ght_insert(kvhash, strdup(tbuf), strlen("dport") + 1, "dport") < 0)
	{ //Destination Port
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ntohs(udp->uh_sum));
	if (ght_insert(kvhash, strdup(tbuf), strlen("udpcksum") + 1, "udpcksum")
			< 0)
	{ //Destination Port
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ntohs(udp->uh_ulen));
	if (ght_insert(kvhash, strdup(tbuf), strlen("udplen") + 1, "udplen") < 0)
	{ //Destination Port
		status = FAILURE;
		goto end;
	}

	end: return status;

}
