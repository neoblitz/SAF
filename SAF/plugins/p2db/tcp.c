/*-------------------------------------------------------------------------
 * tcp.c - Parses a TCP packet
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
 * process_tcp - Parses a tcp packet and stores its contents as a hash of
 * 				 values indexed by attributes
 *
 * Inputs
 *      @tcp 	   - Pointer to the start of tcp packet
 *      @kvhash    - Pointer to hashtable
 *
 * Returns
 *      SUCCESS / FAILURE
 *---------------------------------------------------------------------------*/
int process_tcp(const struct sniff_tcp *tcp, ght_hash_table_t *kvhash)
{
	int status = SUCCESS;
	char tbuf[MAX_TBUF_SIZE];
	u_int size_tcp = TH_OFF(tcp) * 4;

	/** Strdup is important because everything  is freed later */
	if (ght_insert(kvhash, strdup(EVENT_TCP), strlen("eventtype")
			+ 1, "eventtype") < 0)
	{
		status = FAILURE;
		goto end;
	}


	if (size_tcp < 20)
	{
		DEBUGLOG("   * Invalid TCP header length: %u bytes\n", size_tcp);
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ntohs(tcp->th_sport));
	if (ght_insert(kvhash, strdup(tbuf), strlen("sport") + 1, "sport") < 0)
	{ //Source Port
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ntohs(tcp->th_dport));
	if (ght_insert(kvhash, strdup(tbuf), strlen("dport") + 1, "dport") < 0)
	{ //Destination Port
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ntohl(tcp->th_seq));
	if (ght_insert(kvhash, strdup(tbuf), strlen("tcpseq") + 1, "tcpseq") < 0)
	{ //TCP Sequence Number
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ntohl(tcp->th_ack));
	if (ght_insert(kvhash, strdup(tbuf), strlen("tcpack") + 1, "tcpack") < 0)
	{ //TCP Ack Number
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%d", tcp->th_flags);
	if (ght_insert(kvhash, strdup(tbuf), strlen("tcpflags") + 1, "tcpflags")
			< 0)
	{ //TCP Flags
		status = FAILURE;
		goto end;
	}

	end: return status;

}
