/*-------------------------------------------------------------------------
 * dns.c - Parses a DNS request / response packet
 * 		   Currently Only A, NS and CNAME are supported
 *
 *Credits
 * 	Logic behind the parsing adopted from
 * 	http://www.codeproject.com/KB/IP/dns_query.aspx
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
 * process_dns - Parses a dns packet and stored its contents as a hash of
 * 				 values indexed by attributes
 *
 * Inputs
 *      @packet	   - Pointer to the complete packet
 *      @kvhash    - Pointer to hashtable
 *
 * Returns
 *      SUCCESS / FAILURE
 *---------------------------------------------------------------------------*/
//int process_dns(const unsigned char *packet, ght_hash_table_t *kvhash)
//int process_dns(const struct sniff_ip *ip, ght_hash_table_t *kvhash)
int process_dns(const dnsheader *dns, ght_hash_table_t *kvhash)
{
	int status = SUCCESS;
	char tbuf[MAX_TBUF_SIZE];

	//const struct sniff_ip *ip; /* The IP header */
	//const struct sniff_udp *udp; /* The UDP header */
	//const dnsheader *dns; /* DNS Header */
    /* int len_link_header = 0;
	struct nullloopback *nullhdr = (struct nullloopback*) (packet);

	if((ntohl(nullhdr->afamily) ==  AFAMILY_IPV4_HO) ||
		(htonl(nullhdr->afamily) ==  AFAMILY_IPV4_NO) ){
		ip = (struct sniff_ip*) (packet + SIZE_NULLLOOPBACK);
		len_link_header = SIZE_NULLLOOPBACK;
	} else{
	     Discard packets that are not IPV4 
		ip = (struct sniff_ip*) (packet + SIZE_ETHERNET);
		len_link_header = SIZE_ETHERNET;
	}*/

	//u_int size_ip;
	//u_int size_udp;

	/* DNS Replies*/
	dnsresrecord answers[20], auth[20];

	/*ip = (struct sniff_ip*) (packet + len_link_header);*/
	//size_ip = IP_HL(ip) * 4;

	//udp = (struct sniff_udp*) (packet + len_link_header + size_ip);
	//size_udp = ntohs(udp->uh_ulen);

	/** Put the eventtype */
	if (ght_insert(kvhash, strdup(EVENT_DNS),
			strlen("eventtype") + 1, "eventtype") < 0)
	{
		status = FAILURE;
		goto end;
	}

	//int size_udp_header = 8;
	//dns = (dnsheader*) (packet + len_link_header + size_ip + size_udp_header);

	sprintf(tbuf, "%u", ntohs(dns->id));
	if (ght_insert(kvhash, strdup(tbuf), strlen("dnsid") + 1, "dnsid") < 0)
	{ //DNSID
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", dns->aa);
	if (ght_insert(kvhash, strdup(tbuf), strlen("dnsaa") + 1, "dnsaa") < 0)
	{ //DNSAA
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", dns->opcode);
	if (ght_insert(kvhash, strdup(tbuf), strlen("dnsopcode") + 1, "dnsopcode")
			< 0)
	{ //DNSAA
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", dns->qr);
	if (ght_insert(kvhash, strdup(tbuf), strlen("dnsqrflag") + 1, "dnsqrflag")
			< 0)
	{ //DNSAA
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ntohs(dns->qdcount));
	if (ght_insert(kvhash, strdup(tbuf), strlen("dnsnumques") + 1, "dnsnumques")
			< 0)
	{ //DNS Num Ques
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ntohs(dns->ancount));
	if (ght_insert(kvhash, strdup(tbuf), strlen("dnsnumans") + 1, "dnsnumans")
			< 0)
	{ //DNS Num Ques
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ntohs(dns->nscount));
	if (ght_insert(kvhash, strdup(tbuf), strlen("dnsnumauth") + 1, "dnsnumauth")
			< 0)
	{ //DNS Num Ques
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ntohs(dns->arcount));
	if (ght_insert(kvhash, strdup(tbuf), strlen("dnsnumadd") + 1, "dnsnumadd")
			< 0)
	{ //DNS Num Ques
		status = FAILURE;
		goto end;
	}

	int stop = 0;
	unsigned char *queryname = (unsigned char *) ((unsigned char *)dns + sizeof(dnsheader));
	//unsigned char *queryname = (unsigned char *) (packet + len_link_header
	//		+ size_ip + size_udp_header + sizeof(dnsheader));
	unsigned char *qname = convert_from_dnsformat(queryname,
			(unsigned char *) dns, &stop);
	if (qname == NULL)
	{
		status = FAILURE;
		goto end;
	}

	if (strlen((char*) qname) == 0)
	{
		/** Special condition for ROOT query*/
		free(qname);
		qname = (unsigned char *) malloc(5);
		strcpy((char*) qname, "root");
	}

	sprintf(tbuf, "%s", qname);
	if (ght_insert(kvhash, strdup(tbuf), strlen("dnsquesname") + 1,
			"dnsquesname") < 0)
	{ //DNS Num Ques
		status = FAILURE;
		goto end;
	}

	dnsquestion *ques = (dnsquestion *) (queryname + strlen((char*) queryname)
			+ 1);

	sprintf(tbuf, "%u", ntohs(ques->qclass));
	if (ght_insert(kvhash, strdup(tbuf), strlen("dnsquesclass") + 1,
			"dnsquesclass") < 0)
	{ //DNS Ques Class
		status = FAILURE;
		goto end;
	}

	sprintf(tbuf, "%u", ntohs(ques->qtype));
	if (ght_insert(kvhash, strdup(tbuf), strlen("dnsquestype") + 1,
			"dnsquestype") < 0)
	{ //DNS Ques Type
		status = FAILURE;
		goto end;
	}

	DEBUGLOG("Query=> %s Length: %d Class: %u Type: %u\n", qname, strlen(
			(char*) qname), ntohs(ques->qclass), ntohs(ques->qtype));
	free(qname);

	/** Only process A, NS and CNAME*/
	if ((ntohs(ques->qtype) != 1) && (ntohs(ques->qtype) != 2) && (ntohs(
			ques->qtype) != 5))
	{
		DEBUGLOG("Unrecognized DNS question type %d!\n", ntohs(ques->qtype));
		status = FAILURE;
		goto end;
	}
	/** Reading answers
	 *
	 * QUESTION FORMAT
	 * OCTET 1,2,…n    QNAME
	 * OCTET n+1,n+2   QTYPE
	 * OCTET n+3,n+4   QCLASS
	 *
	 * ANSWER, AUTHORITY, ADDITIONAL FORMAT
	 * OCTET 1,2,..n       NAME
	 * OCTET n+1,n+2       TYPE
	 * OCTET n+3,n+4       CLASS
	 * OCTET n+5,n+6,n+7,n+8   TTL
	 * OCTET n+9,n+10      RDLENGTH
	 * OCTET n+11,n+12,….. RDATA
	 **/
	stop = 0;
	int i = 0, j = 0;
	char *dnsansarec = (char *) malloc(MAX_BUF_LENGTH);
	if (!dnsansarec)
	{
		CRITLOG("MALLOC Failed here ! Aborting");
		status = FAILURE;
		goto end;
	}
	*dnsansarec = '\0';

	char *dnsansns = (char *) malloc(MAX_BUF_LENGTH);
	if (!dnsansns)
	{
		CRITLOG("MALLOC Failed here ! Aborting");
		status = FAILURE;
		goto end;
	}
	*dnsansns = '\0';

	char *dnsanscname = (char *) malloc(MAX_BUF_LENGTH);
	if (!dnsanscname)
	{
		CRITLOG("MALLOC Failed here ! Aborting");
		status = FAILURE;
		goto end;
	}
	*dnsanscname = '\0';

	unsigned char * reader = (unsigned char *) ((unsigned char*) ques
			+ sizeof(dnsquestion));
	for (i = 0; i < ntohs(dns->ancount); i++)
	{
		answers[i].name = convert_from_dnsformat(reader, (unsigned char *) dns,
				&stop);
		if (answers[i].name == NULL)
		{
			status = FAILURE;
			goto end;
		}

		if (strlen((char *) answers[i].name) == 0)
		{
			/** Special condition for ROOT query*/
			free(answers[i].name);
			answers[i].name = (unsigned char *) malloc(5);
			strcpy((char*) answers[i].name, "root");
		}
		reader += stop;

		answers[i].resource = (dnsrdata*) (reader);
		reader += DNS_RDATA_LENGTH;

		DEBUGLOG("\tAnswer=> Name: %s Class: %d Type: %d Datalen: %d ",
				answers[i].name, ntohs(answers[i].resource->_class), ntohs(
						answers[i].resource->type), ntohs(
						answers[i].resource->data_len));

		/** Only process A, NS and CNAME*/
		if ((ntohs(answers[i].resource->type) != 1) && (ntohs(
				answers[i].resource->type) != 2) && (ntohs(
				answers[i].resource->type) != 5))
		{
			reader += ntohs(answers[i].resource->data_len);
			free(answers[i].name);
			continue;
		}

		/** A Record  */
		if (ntohs(answers[i].resource -> type) == 0x0001)
		{
			answers[i].rdata = (unsigned char *) malloc(ntohs(
					answers[i].resource->data_len) + 1);
			if (answers[i].rdata == NULL)
			{
				status = FAILURE;
				goto end;
			}

			if (strlen((char*) answers[i].rdata) == 0)
			{
				/** Special condition for ROOT query*/
				free(answers[i].rdata);
				answers[i].rdata = (unsigned char *) malloc(5);
				strcpy((char *) answers[i].rdata, "root");
			}

			for (j = 0; j < ntohs(answers[i].resource->data_len); j++)
				answers[i].rdata[j] = reader[j];
			answers[i].rdata[ntohs(answers[i].resource->data_len)] = '\0';
			reader += ntohs(answers[i].resource->data_len);

			long *p = (long*) answers[i].rdata;
			struct sockaddr_in a;
			a.sin_addr.s_addr = (*p);
			char *ip = inet_ntoa(a.sin_addr);
			if ((strlen(dnsansarec) + strlen(ip) + 3) < MAX_BUF_LENGTH)
			{
				strcat(dnsansarec, ip);
				//strcat(dnsansarec, "~~");
			}
			DEBUGLOG("Rdata: %s\n", ip);
		}
		else if (ntohs(answers[i].resource -> type) == 0x0005)
		{
			/** CNAME  */
			answers[i].rdata = convert_from_dnsformat(reader,
					(unsigned char *) dns, &stop);
			if (answers[i].rdata == NULL)
			{
				status = FAILURE;
				goto end;
			}

			if (strlen((char*) answers[i].rdata) == 0)
			{
				/** Special condition for ROOT query*/
				free(answers[i].rdata);
				answers[i].rdata = (unsigned char *) malloc(5);
				strcpy((char*) answers[i].rdata, "root");
			}

			reader += stop;
			if ((strlen(dnsanscname) + strlen((char*) answers[i].rdata) + 3)
					< MAX_BUF_LENGTH)
			{
				strcat(dnsanscname, (char*) answers[i].rdata);
				//strcat(dnsanscname, "~~");
			}
			DEBUGLOG("Rdata: %s\n", answers[i].rdata);
		}
		else if (ntohs(answers[i].resource -> type) == 0x0002)
		{
			answers[i].rdata = convert_from_dnsformat(reader,
					(unsigned char *) dns, &stop);
			if (answers[i].rdata == NULL)
			{
				status = FAILURE;
				goto end;
			}

			if (strlen((char*) answers[i].rdata) == 0)
			{
				/** Special condition for ROOT query*/
				free(answers[i].rdata);
				answers[i].rdata = (unsigned char *) malloc(5);
				strcpy((char*) answers[i].rdata, "root");
			}

			reader += stop;
			if ((strlen(dnsansns) + strlen((char*) answers[i].rdata) + 3)
					< MAX_BUF_LENGTH)
			{
				strcat(dnsansns, (char*) answers[i].rdata);
				//strcat(dnsansns, "~~");
			}
			DEBUGLOG("Rdata: %s\n", answers[i].rdata);
		}

		free(answers[i].rdata);
		free(answers[i].name);
	}

	if (ght_insert(kvhash, strdup(dnsansarec), strlen("dnsansarec") + 1,
			"dnsansarec") < 0)
	{ //DNS Answer
		status = FAILURE;
		goto end;
	}

	if (ght_insert(kvhash, strdup(dnsansns), strlen("dnsansns") + 1, "dnsansns")
			< 0)
	{ //DNS Answer
		status = FAILURE;
		goto end;
	}

	if (ght_insert(kvhash, strdup(dnsanscname), strlen("dnsanscname") + 1,
			"dnsanscname") < 0)
	{ //DNS Answer
		status = FAILURE;
		goto end;
	}

	free(dnsansarec);
	free(dnsanscname);
	free(dnsansns);

	char * dnsrec = (char *) malloc(MAX_BUF_LENGTH);
	if (!dnsrec)
	{
		CRITLOG("MALLOC Failed here ! Aborting");
		return FAILURE;
	}
	*dnsrec = '\0';

	/** Read authorities */
	for (i = 0; i < ntohs(dns->nscount); i++)
	{
		auth[i].name = convert_from_dnsformat(reader, (unsigned char *) dns,
				&stop);
		if (auth[i].name == NULL)
		{
			status = FAILURE;
			goto end;
		}

		if (strlen((char*) auth[i].name) == 0)
		{
			/** Special condition for ROOT query*/
			free(auth[i].name);
			auth[i].name = (unsigned char *) malloc(5);
			strcpy((char*) auth[i].name, "root");
		}
		reader += stop;
		auth[i].resource = (dnsrdata*) (reader);
		reader += DNS_RDATA_LENGTH;
		auth[i].rdata = convert_from_dnsformat(reader, (unsigned char *) dns,
				&stop);
		if (auth[i].rdata == NULL)
		{
			status = FAILURE;
			goto end;
		}

		if (strlen((char*) auth[i].rdata) == 0)
		{
			/** Special condition for ROOT query*/
			free(auth[i].rdata);
			auth[i].rdata = (unsigned char *) malloc(5);
			strcpy((char*) auth[i].rdata, "root");
		}

		reader += stop;
		if ((strlen(dnsrec) + strlen((char*) auth[i].rdata) + 3)
				< MAX_BUF_LENGTH)
		{
			strcat(dnsrec, (char*) auth[i].rdata);
			//strcat(dnsrec, "~~");
		}
		free(auth[i].name);
		free(auth[i].rdata);
	}

    
	if (ght_insert(kvhash, strdup(dnsrec), strlen("dnsauth") + 1, "dnsauth")
			< 0)
	{ //DNS Answer
		status = FAILURE;
		goto end;
	}
	free(dnsrec);

	/** Additional Records */

	char *dnsaddarec = (char *) malloc(MAX_BUF_LENGTH);
	if (!dnsaddarec)
	{
		CRITLOG("MALLOC Failed here ! Aborting");
		status = FAILURE;
		goto end;
	}
	*dnsaddarec = '\0';

	char *dnsaddns = (char *) malloc(MAX_BUF_LENGTH);
	if (!dnsaddns)
	{
		CRITLOG("MALLOC Failed here ! Aborting");
		status = FAILURE;
		goto end;
	}
	*dnsaddns = '\0';

	char *dnsaddcname = (char *) malloc(MAX_BUF_LENGTH);
	if (!dnsaddcname)
	{
		CRITLOG("MALLOC Failed here ! Aborting");
		status = FAILURE;
		goto end;
	}
	*dnsaddcname = '\0';

	for (i = 0; i < ntohs(dns->arcount); i++)
	{
		answers[i].name = convert_from_dnsformat(reader, (unsigned char *) dns,
				&stop);
		if (answers[i].name == NULL)
		{
			status = FAILURE;
			goto end;
		}

		if (strlen((char*) answers[i].name) == 0)
		{
			/** Special condition for ROOT query*/
			free(answers[i].name);
			answers[i].name = (unsigned char *) malloc(5);
			strcpy((char*) answers[i].name, "root");
		}

		reader += stop;

		answers[i].resource = (dnsrdata*) (reader);
		reader += DNS_RDATA_LENGTH;

		if ((ntohs(answers[i].resource->type) != 1) && (ntohs(
				answers[i].resource->type) != 2) && (ntohs(
				answers[i].resource->type) != 5))
		{
			reader += ntohs(answers[i].resource->data_len);
			free(answers[i].name);
			continue;
		}
		/** A Record  */
		if (ntohs(answers[i].resource -> type) == 0x0001)
		{
			answers[i].rdata = (unsigned char *) malloc(ntohs(
					answers[i].resource->data_len) + 1);
			if (answers[i].rdata == NULL)
			{
				status = FAILURE;
				goto end;
			}

			if (strlen((char*) answers[i].rdata) == 0)
			{
				/** Special condition for ROOT query*/
				free(answers[i].rdata);
				answers[i].rdata = (unsigned char *) malloc(5);
				strcpy((char*) answers[i].rdata, "root");
			}

			for (j = 0; j < ntohs(answers[i].resource->data_len); j++)
				answers[i].rdata[j] = reader[j];
			answers[i].rdata[ntohs(answers[i].resource->data_len)] = '\0';
			reader += ntohs(answers[i].resource->data_len);

			long *p = (long*) answers[i].rdata;
			struct sockaddr_in a;
			a.sin_addr.s_addr = (*p);
			char *ip = inet_ntoa(a.sin_addr);
			DEBUGLOG("IPv4 address : %s", ip);
			if ((strlen(dnsaddarec) + strlen(ip) + 3) < MAX_BUF_LENGTH)
			{
				strcat(dnsaddarec, ip);
				//strcat(dnsaddarec, "~~");
			}
		}
		else if (ntohs(answers[i].resource -> type) == 0x0005)
		{
			/** CNAME  */
			answers[i].rdata = convert_from_dnsformat(reader,
					(unsigned char *) dns, &stop);
			if (answers[i].rdata == NULL)
			{
				status = FAILURE;
				goto end;
			}

			if (strlen((char*) answers[i].rdata) == 0)
			{
				/** Special condition for ROOT query*/
				free(answers[i].rdata);
				answers[i].rdata = (unsigned char *) malloc(5);
				strcpy((char*) answers[i].rdata, "root");
			}

			reader += stop;
			if ((strlen(dnsaddcname) + strlen((char*) answers[i].rdata) + 3)
					< MAX_BUF_LENGTH)
			{
				strcat(dnsaddcname, (char*) answers[i].rdata);
				//strcat(dnsaddcname, "~~");
			}
		}
		else if (ntohs(answers[i].resource -> type) == 0x0002)
		{
			answers[i].rdata = convert_from_dnsformat(reader,
					(unsigned char *) dns, &stop);
			if (answers[i].rdata == NULL)
			{
				status = FAILURE;
				goto end;
			}

			if (strlen((char*) answers[i].rdata) == 0)
			{
				/** Special condition for ROOT query*/
				free(answers[i].rdata);
				answers[i].rdata = (unsigned char *) malloc(5);
				strcpy((char*) answers[i].rdata, "root");
			}

			reader += stop;
			if ((strlen(dnsaddns) + strlen((char*) answers[i].rdata) + 3)
					< MAX_BUF_LENGTH)
			{
				strcat(dnsaddns, (char*) answers[i].rdata);
				//strcat(dnsaddns, "~~");
			}
		}
		DEBUGLOG("\tAnswer=> Name: %s Class: %d Type: %d Datalen: %d Dnsaddns: %s Rdata: %s\n",
				answers[i].name, ntohs(answers[i].resource->_class), ntohs(
						answers[i].resource->type), ntohs(
						answers[i].resource->data_len), dnsaddns, answers[i].rdata);

		free(answers[i].rdata);
		free(answers[i].name);
	}

	if (ght_insert(kvhash, strdup(dnsaddarec), strlen("dnsaddarec") + 1,
			"dnsaddarec") < 0)
	{ //DNS Answer
		status = FAILURE;
		goto end;
	}

	if (ght_insert(kvhash, strdup(dnsaddns), strlen("dnsaddns") + 1, "dnsaddns")
			< 0)
	{ //DNS Answer
		status = FAILURE;
		goto end;
	}

	if (ght_insert(kvhash, strdup(dnsaddcname), strlen("dnsaddcname") + 1,
			"dnsaddcname") < 0)
	{ //DNS Answer
		status = FAILURE;
		goto end;
	}

	free(dnsaddarec);
	free(dnsaddcname);
	free(dnsaddns);

	end: return status;
}

/*-----------------------------------------------------------------------------
 * convert_from_dnsformat - Convert from DNS name format
 *
 *
 * Description
 *
 * If google.com were to occur 10 times in the packet then it will written as
 * google.com for the first time and after that a pointer will be placed at every
 * next occurence of google.com to the position offset of the beginning of the
 * first occurence.The starting of the dns header being the offset 0. For example
 * if www.google.com is written starting at a offset of say 12 and some where later
 * ns.google.com is to be written then it will be written as ns.16 which means
 * point to offset 16(where g of google is).To implement this pointer technique 2
 * bytes are used where the first 2 bits are 1 and the rest 14 bits are the
 * offset.so for 16 as offset the number u wud need is 1100000000000000 + 1000
 *
 *---------------------------------------------------------------------------*/
unsigned char * convert_from_dnsformat(unsigned char *reader,
		unsigned char *buffer, int *count)
{
	unsigned char *name;
	unsigned int p = 0, jumped = 0, offset;
	int i, j;
	name = (unsigned char*) malloc(256);
	if (!name)
	{
		CRITLOG("Malloc Error !\n");
		return NULL;
	}

	name[0] = '\0';
	*count = 1;

	/** read the names in 3www6google3com format */
	while ((unsigned char) *reader != 0x00)
	{
		if (*reader >= 0xc0)
		{
			offset = ((unsigned char) *reader) * 256 + (unsigned char) *(reader
					+ 1) - (unsigned int) 0xc000; //11000000 00000000
			reader = buffer + offset - 1;
			jumped = 1; //we have jumped to another location so counting wont go up!
		}
		else
		{
			name[p++] = *reader;
		}
		reader = reader + 1;
		if (jumped == 0)
			*count = *count + 1;
	}

	name[p] = '\0'; //string complete
	if (jumped == 1)
		*count = *count + 1;

	//now convert 3www6google3com0 to www.google.com
	for (i = 0; i < (int) strlen((const char*) name); i++)
	{
		p = name[i];
		for (j = 0; j < (int) p; j++)
		{
			name[i] = name[i + 1];
			i = i + 1;
		}
		name[i] = '.';
	}
	name[i - 1] = '\0'; //remove the last dot
	return name;
}

