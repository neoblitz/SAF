/*-------------------------------------------------------------------------
 * icmp.c - Parses an ICMP packet
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
 * process_icmp - Parses ICMP packet minimally.
 *
 * Inputs
 *      @p 	   	   - Pointer to start of the icmp header
 *      @kvhash    - Pointer to hashtable
 *
 * Returns
 *      SUCCESS / FAILURE
 *---------------------------------------------------------------------------*/
int process_icmp(const struct sniff_icmp *icmp, ght_hash_table_t *kvhash)
{
	int status = SUCCESS;
	char tbuf[MAX_TBUF_SIZE];
	if (ght_insert(kvhash, strdup(EVENT_ICMP), strlen("eventtype") + 1,
			"eventtype") < 0)
	{
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", icmp->type);
	if (ght_insert(kvhash, strdup(tbuf), strlen("icmptype") + 1, "icmptype")
			< 0)
	{ //Type
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", icmp->code);
	if (ght_insert(kvhash, strdup(tbuf), strlen("icmpcode") + 1, "icmpcode")
			< 0)
	{ //Type
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ntohs(icmp->checksum));
	if (ght_insert(kvhash, strdup(tbuf), strlen("icmpcksum") + 1, "icmpcksum")
			< 0)
	{ //Checksum
		status = FAILURE;
		goto end;
	}

	end: return status;

}
