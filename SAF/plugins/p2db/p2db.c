/*-----------------------------------------------------------
 * p2db.c - Logs packets from a PCAP to a Sqlite database
 *
 * Description
 * 		p2db converts IP,UDP,TCP,DNS (A,NS,CNAME)and ICMP
 * 		packets to a sqlite database. Each protocol has its
 * 		own table with columns as attributes defined in the
 * 		file eventattrs.c.
 *
 * Usage:
 * 		Make sure to have run setup.py (as root).
 * 		./p2db <pcapfilename> <output database>
 *
 *
 * Copyright (C) Arun Viswanathan (aviswana@isi.edu)
 * This software is licensed under the GPLv3 license, included in
 * ./GPLv3-LICENSE.txt in the source distribution
 *-------------------------------------------------------------*/
#include "headers.h"
#include "globals.h"
#include "db.h"
#include "packets.h"
#include "eventattrs.h"
#include "p2db.h"
#include "logging.h"

/**
 * File Globals
 */

/** Packet Counters */
long count = 0;
long tcp_packet = 0;
long udp_packet = 0;
long ip_packet = 0;
long icmp_packet = 0;
long unk_packet = 0;
long dns_packet = 0;
long invalid_ip = 0;
long ipv6_packet = 0;

/** Prepared statement objects for sqlite*/
sqlite3_stmt *ppStmt, *ppStmt_icmp, *ppStmt_udp, *ppStmt_tcp, *ppStmt_ip,
		*ppStmt_dns;

/** Start and endtimes */
time_t starttime;
time_t endtime;

/** Time of first event/ Time of last event */
time_t firstev_time;
time_t lastev_time;

/* Pointer to open PCAP file*/
pcap_t *handle;

/* Pointer to database*/
sqlite3 *db;

/** Number of packets to process before committing them to database
 * WARNING: This is an empirical value and adjusting it upwards can have
 * 			memory consequences and adjusting it downwards will affect speed.
 */
int transactionsize = 20000;

/** If set program prints only statistics */
int stats = false;

/*-----------------------------------------------------------------------------
 * main - Program Entry point
 *
 * Inputs
 * 		@filename   - PCAP file to process
 * 		@outdb      - Name of the output database file
 *
 *---------------------------------------------------------------------------*/
int main(int argc, char **argv)
{
	char errbuf[PCAP_ERRBUF_SIZE]; /* error buffer */
	char * filename = NULL;
	unsigned int numpackets = -1;
	char *database = NULL;

	if (argc == 3)
	{
		if(strcmp(argv[2],"stats") == 0){
			filename = argv[1];
			stats = true;
			printf("Statistics Mode set to true!\n");
		} else {
			filename = argv[1];
			database = argv[2];
		}
	}
	else if ((argc > 3) || (argc < 2))
	{
		usage(argv[0]);
		exit(EXIT_FAILURE);
	}

	if ((filename == NULL))
	{
		usage(argv[0]);
		exit(EXIT_FAILURE);
	}

	/** Set verbosity to INFO by default */
	set_verbosity(2);

	/* Set up the signal handler proc */
	struct sigaction act_1, act_2;
	act_1.sa_handler = sigint_handler;
	sigemptyset(&act_1.sa_mask);
	act_1.sa_flags = 0;
	sigaction(SIGINT, &act_1, NULL);

	act_2.sa_handler = sigint_handler;
	sigemptyset(&act_2.sa_mask);
	act_2.sa_flags = 0;
	sigaction(SIGTERM, &act_2, NULL);

	/** Open pcap */
	handle = pcap_open_offline(filename, errbuf);
	if (!handle)
	{
		CRITLOG("pcap_open Error: %s\n", errbuf);
		exit(EXIT_FAILURE);
	}

	/** Init the required databases */
	if(!stats){
		init_database(&db, database);
		if (db == NULL)
		{
			CRITLOG("Database creation failed  !\n");
			exit(EXIT_FAILURE);
		}
		INFOLOG("Created database !\n");

		if (create_tables(db) == FAILURE)
		{
			CRITLOG("FAILURE while creating tables !\n");
			exit(EXIT_FAILURE);
		}
		INFOLOG("Created Tables !\n");
	}

	starttime = time(NULL);
	INFOLOG("Starting to read packets - time : %s", ctime(&starttime));
	INFOLOG("Transaction Size:  %d packets \n\n", transactionsize);
	pcap_dispatch(handle, numpackets, process_packet, (u_char*) db);

	/** Commit the transaction to send the last processed batch to disk*/
	if(!stats)
		execute_sql(db, "COMMIT");

	cleanup();
	printstats();
	return 0;
}

/*-----------------------------------------------------------------------------
 * process_packet - Handler called from pcap_dispatch for every packet
 *
 *---------------------------------------------------------------------------*/
void process_packet(u_char *args, const struct pcap_pkthdr *header,
		const u_char *packet)
{
	const struct sniff_ethernet *ethernet; /* Ethernet header */
	const struct sniff_ip *ip; /* IP header */
	const struct sniff_udp *udp; /* UDP header */
	sqlite3 *db = (sqlite3 *) args;

	char * tablename = NULL;
	char ** tableattrs = NULL;
	int len_link_header = 0;
    int ltype = 0;

	/** Increment count irrespective of valid or invalid packet */
	count++;
    

    /**
     * TODO: The below case of nullloopback should be done with the more
     *       efficient linktype check above.
     */

	/** Check for the special case of null/loopback packets
	 * which dont contain an ethernet header but instead a 4-byte address family/
	 * protocol family value for the protocol running atop the link-layer.
	 *
	 * Read more at http://wiki.wireshark.org/NullLoopback
	 **/
	struct nullloopback *nullhdr = (struct nullloopback*) (packet);

	if((ntohl(nullhdr->afamily) ==  AFAMILY_IPV4_HO) ||
		(htonl(nullhdr->afamily) ==  AFAMILY_IPV4_NO) ){
		DEBUGLOG("    Found NULL/LOOPBACK header in place of ETHERNET. Value : %x\n",ntohl(nullhdr->afamily));
		ip = (struct sniff_ip*) (packet + SIZE_NULLLOOPBACK);
		len_link_header = SIZE_NULLLOOPBACK;
	} else{
		/* Start with ethernet  */
		ethernet = (struct sniff_ethernet*) (packet);
		/* Discard packets that are not IPV4 */
		ip = (struct sniff_ip*) (packet + SIZE_ETHERNET);
		len_link_header = SIZE_ETHERNET;
	}

    /*
     * A reference list of all available link layer types is available at 
     * http://www.winpcap.org/docs/docs_40_2/html/group__wpcapfunc.html
     * under function pcap_datalink()
     */
    
    ltype = pcap_datalink((pcap_t*) handle);
    char *ltype_name = (char *) pcap_datalink_val_to_name(ltype);
    DEBUGLOG("    Link Type:%s (%s)\n", ltype_name, pcap_datalink_val_to_description(ltype));
    /* If the linktype is Raw IP then packet begins with an IP header*/
    if (strcmp(ltype_name,"RAW")==0){
		ip = (struct sniff_ip*) (packet);
		len_link_header = 0;
    }    

	int size_ip = IP_HL(ip) * 4;
	u_int ip_ver = IP_V(ip);
	if (ip_ver == 6)
	{
		ipv6_packet++;
		return;
	}
	/* Discard packets that are corrupted */
	if (size_ip < 20)
	{
		DEBUGLOG("   * Invalid IP header length: %u bytes (pkt %d) \n", size_ip, count);
		invalid_ip++;
		return;
	}

	ght_hash_table_t *kvhash = NULL;
	kvhash = dissect_packet(args, header, packet, count);
	if (kvhash == NULL)
	{
		DEBUGLOG("Packet could not be parsed!Hash returned is NULL\n");
		unk_packet++;
		return;
	}


	/* print source and destination IP addresses */
	DEBUGLOG("       From: %s\n", inet_ntoa(ip->ip_src));
	DEBUGLOG("         To: %s\n", inet_ntoa(ip->ip_dst));
	int len = 0;
	/* determine protocol */
	switch (ip->ip_p)
	{
	case IPPROTO_TCP:
		DEBUGLOG("   Protocol: TCP\n");
		tcp_packet++;
		tablename = EVENT_TCP;
		tableattrs = tcp_attrs;
		ppStmt = ppStmt_tcp;
		len = num_tcp_attrs;
		break;
	case IPPROTO_UDP:
		udp = (struct sniff_udp*) (packet + len_link_header + size_ip);
		int dport = ntohs(udp->uh_dport);
		int sport = ntohs(udp->uh_sport);
		if ((sport == 53) || (dport == 53))
		{
			DEBUGLOG("   Protocol: DNS\n");
			tablename = EVENT_DNS;
			tableattrs = dns_attrs;
			ppStmt = ppStmt_dns;
			len = num_dns_attrs;
			dns_packet++;
		}
		else
		{
			DEBUGLOG("   Protocol: UDP\n");
			tablename = EVENT_UDP;
			tableattrs = udp_attrs;
			ppStmt = ppStmt_udp;
			len = num_udp_attrs;
			udp_packet++;
		}
		break;
	case IPPROTO_ICMP:
		DEBUGLOG("   Protocol: ICMP\n");
		icmp_packet++;
		tablename = EVENT_ICMP;
		tableattrs = icmp_attrs;
		ppStmt = ppStmt_icmp;
		len = num_icmp_attrs;
		break;
	case IPPROTO_IP:
		DEBUGLOG("   Protocol: IP\n");
		ip_packet++;
		tablename = EVENT_IP;
		tableattrs = ip_attrs;
		ppStmt = ppStmt_ip;
		len = num_ip_attrs;
		break;
	default:
		unk_packet++;
		DEBUGLOG("   Protocol: unknown\n");
		tablename = NULL;
	}

	if(count == 1) {
		firstev_time = header->ts.tv_sec;
	} else {
		lastev_time = header->ts.tv_sec;
	}



	if ((tablename != NULL) && (stats == false))
	{
		DEBUGLOG("Inserting record into table %s with tableattrs\n", tablename);
//		kvhash = dissect_packet(args, header, packet, count);
//		if (kvhash == NULL)
//		{
//			DEBUGLOG("Hash returned is NULL\n");
//			return;
//		}

		/** Start a transaction when the first packet is received*/
		if (count == 1)
		{
			if (execute_sql(db, "BEGIN") != 0)
			{
				CRITLOG("BEGIN Transaction failed !\n");
				return;
			}
		}

		/** Commit transaction after every transactionsize packets and start a new one*/
		if (count % transactionsize == 0)
		{
			if (execute_sql(db, "COMMIT") != 0)
			{
				return;
			}
			endtime = time(NULL);
			long timespent = endtime - starttime;
			INFOLOG("Processed %ld records in %ld secs (%lf sec per record)\n",
					count, timespent, (double) (timespent / count));
			if (execute_sql(db, "BEGIN") != 0)
			{
				return;
			}
		}

		if ((strcmp(tablename,  EVENT_ICMP) == 0) && (icmp_packet == 1))
		{
			DEBUGLOG("Preparing statement for %s\n", tablename);
			len = num_icmp_attrs;
			prepare_stmt(db, &ppStmt_icmp, tablename, tableattrs, len);
			ppStmt = ppStmt_icmp;
		}
		if ((strcmp(tablename,  EVENT_IP) == 0) && (ip_packet == 1))
		{
			DEBUGLOG("Preparing statement for %s\n", tablename);
			len = num_ip_attrs;
			prepare_stmt(db, &ppStmt_ip, tablename, tableattrs, len);
			ppStmt = ppStmt_ip;
		}
		if ((strcmp(tablename,  EVENT_TCP) == 0) && (tcp_packet == 1))
		{
			DEBUGLOG("Preparing statement for %s\n", tablename);
			len = num_tcp_attrs;
			prepare_stmt(db, &ppStmt_tcp, tablename, tableattrs, len);
			ppStmt = ppStmt_tcp;
		}
		if ((strcmp(tablename,  EVENT_UDP) == 0) && (udp_packet == 1))
		{
			DEBUGLOG("Preparing statement for %s\n", tablename);
			len = num_udp_attrs;
			prepare_stmt(db, &ppStmt_udp, tablename, tableattrs, len);
			ppStmt = ppStmt_udp;
		}
		if ((strcmp(tablename,  EVENT_DNS) == 0) && (dns_packet == 1))
		{
			DEBUGLOG("Preparing statement for %s\n", tablename);
			len = num_dns_attrs;
			prepare_stmt(db, &ppStmt_dns, tablename, tableattrs, len);
			ppStmt = ppStmt_dns;
		}

		DEBUGLOG("Inserting into table %s (attrlen: %d) \n", tablename, len);
		if (insert_into_table(db, kvhash, ppStmt, tableattrs, len) != SUCCESS)
		{
			CRITLOG("Inserting into table %s failed\n", tablename);
		}

	}

	if (kvhash)
		free_hash(kvhash);

	return;
}

/*-----------------------------------------------------------------------------
 * dissect_packet- Dissect contents of TCP, UDP, IP, ICMP, DNS packets
 * 						and return a hash of attributes and values
 *
 *---------------------------------------------------------------------------*/

ght_hash_table_t *dissect_packet(u_char *args,
		const struct pcap_pkthdr *header, const u_char *packet, long count)
{
	char tbuf[512];
    int status = SUCCESS;

	ght_hash_table_t *kvhash = ght_create(100);
	if (!kvhash)
	{
		status = FAILURE;
		goto end;
	}

	pcap_packet *p = (pcap_packet*) malloc(sizeof(pcap_packet));
	p->header.caplen = header->caplen;
	p->header.len = header->len;
	p->header.ts = header->ts;
	p->packet = packet;
	p->pcap_file = NULL;
	struct timeval t = header ->ts;

	const struct sniff_ethernet *ethernet; /* The ethernet header */
	const struct sniff_ip *ip; /* The IP header */
	const struct sniff_tcp *tcp; /* The TCP header */
	const struct sniff_udp *udp; /* The UDP header */
	const struct sniff_icmp *icmp; /* The ICMP header */
	u_int size_ip;
	int	is_ip = false;
	int len_link_header = 0;

    /**
     * TODO: Do not repeat the link checking already done in process_packet
     */

    struct nullloopback *nullhdr = (struct nullloopback*) (p->packet);

	if((ntohl(nullhdr->afamily) ==  AFAMILY_IPV4_HO) ||
		(htonl(nullhdr->afamily) ==  AFAMILY_IPV4_NO) ){
		ip = (struct sniff_ip*) (packet + SIZE_NULLLOOPBACK);
		is_ip = true;
		len_link_header = SIZE_NULLLOOPBACK;
	} else{
		/* Start with ethernet  */
		ethernet = (struct sniff_ethernet*) (p->packet);
		/* Discard packets that are not IPV4 */
		ip = (struct sniff_ip*) (packet + SIZE_ETHERNET);
		if (ethernet->ether_type == ntohs(ETHERTYPE_IP)) {
			is_ip = true;
			len_link_header = SIZE_ETHERNET;
		}
	}
    
    int ltype = pcap_datalink((pcap_t*) handle);
    char *ltype_name = (char *)pcap_datalink_val_to_name(ltype);
    /* If the linktype is Raw IP then packet begins with an IP header*/
    if (strcmp(ltype_name,"RAW")==0){
		ip = (struct sniff_ip*) (p->packet);
        is_ip = true;
		len_link_header = 0;
    }    
	

	/*
	 *  IP Packet
	 */
	if (is_ip)
	{
		/**
		 * Insert the preamble eventno, timestamp, timestampusec, origin
		 */
		sprintf(tbuf, "%lu", count);
		if (ght_insert(kvhash, strdup(tbuf), strlen("eventno") + 1, "eventno")
				< 0)
		{ //Eventno
			status = FAILURE;
			goto end;
		}

		sprintf(tbuf, "%lu", (unsigned long) t.tv_sec);
		if (ght_insert(kvhash, strdup(tbuf), strlen("timestamp") + 1,
				"timestamp") < 0)
		{ //Timestamp
			status = FAILURE;
			goto end;
		}

		sprintf(tbuf, "%lu", (unsigned long) t.tv_usec);
		if (ght_insert(kvhash, strdup(tbuf), strlen("timestampusec") + 1,
				"timestampusec") < 0)
		{ //Timestamp usec
			status = FAILURE;
			goto end;
		}

		if (ght_insert(kvhash, strdup("localhost"), strlen("origin") + 1,
				"origin") < 0)
		{//Origin
			status = FAILURE;
			goto end;
		}

		ip = (struct sniff_ip*) (p->packet + len_link_header);
		size_ip = IP_HL(ip) * 4;
		if (size_ip < 20)
		{
			DEBUGLOG("   * Invalid IP header length: %u bytes (pkt %d)\n", size_ip, count);
			invalid_ip++;
			if (ip_packet != 0)
				ip_packet--;
			status = FAILURE;
			goto end;
		}

		/** Process every packet as IP */
		if (process_ip(ip, kvhash) != SUCCESS)
		{
			status = FAILURE;
			goto end;
		}

		/* Process TCP */
		if (ip->ip_p ==IPPROTO_TCP)
		{
			tcp = (struct sniff_tcp*) (p->packet + len_link_header + size_ip);
			if (process_tcp(tcp, kvhash) != SUCCESS)
			{
				status = FAILURE;
				goto end;
			}

		}
		else if (ip->ip_p == IPPROTO_UDP) /* UDP Packets */
		{
			udp = (struct sniff_udp*) (p->packet + len_link_header + size_ip);
			if (process_udp(udp, kvhash) != SUCCESS)
			{
				status = FAILURE;
				goto end;
			}

			/* Process UDP data to check for DNS packets*/
			int dport = ntohs(udp->uh_dport);
			int sport = ntohs(udp->uh_sport);
			if ((sport == 53) || (dport == 53))
			{
                const unsigned char *dns = (const unsigned char *)udp + 8;
				if (process_dns((dnsheader *)dns, kvhash) != SUCCESS)
				{
					status = FAILURE;
				    free(kvhash);
                    kvhash = NULL;		
					goto end;
				}

			}
			else
			{
				/** Set the default eventtype to UDP*/
				if (ght_insert(kvhash, strdup(EVENT_UDP),
						strlen("eventtype") + 1, "eventtype") < 0)
				{
					status = FAILURE;
					goto end;
				}
			}
		}
		else if (ip->ip_p == IPPROTO_ICMP) /* ICMP Packets */
		{
			icmp = (struct sniff_icmp*) (p->packet + len_link_header + size_ip);
			if (process_icmp(icmp, kvhash) != SUCCESS)
			{
				status = FAILURE;
				goto end;
			}
		}
		else
		{	/** Set the default eventtype to IP if its an unknown IP type.
			 * These are most likely corrupted packets or attack packets or probe packets
			 * */
			if (ght_insert(kvhash, strdup( EVENT_IP),
					strlen("eventtype") + 1, "eventtype") < 0)
			{
				status = FAILURE;
				goto end;
			}
		}

	}

	end: free(p);
	return kvhash;
}

/*-----------------------------------------------------------------------------
 * sigint_handler - Handle Ctrl-C signals
 *
 *---------------------------------------------------------------------------*/
void sigint_handler()
{
	printf("\n<Ctrl + C> Processing interrupted ... \n");
	fflush(stdout);
	pcap_breakloop(handle);
}

/*-----------------------------------------------------------------------------
 * cleanup - Terminates the program gracefully
 *
 *---------------------------------------------------------------------------*/
void cleanup()
{
	printf("Cleaning up... \n");

	if(!stats){
		printf("Committing pending transactions... \n");
		execute_sql(db, "COMMIT");
	}
	printf("Freeing pcap resources... \n");
	pcap_close(handle);

	if(!stats){
	printf("Freeing sqlite resources... \n");
		sqlite3_finalize(ppStmt_icmp);
		sqlite3_finalize(ppStmt_dns);
		sqlite3_finalize(ppStmt_ip);
		sqlite3_finalize(ppStmt_tcp);
		sqlite3_finalize(ppStmt_udp);
	}
}

/*-----------------------------------------------------------------------------
 * free_hash - Frees the elements in the hashtable and then the hash table
 *
 *---------------------------------------------------------------------------*/
void free_hash(ght_hash_table_t * hash)
{
	const void *p_key;
	void *p_e;
	ght_iterator_t iterator;

	for (p_e = ght_first(hash, &iterator, &p_key); p_e; p_e = ght_next(hash,
			&iterator, &p_key))
	{
		if (p_e)
			free(p_e);
	}

	ght_finalize(hash);
}

/*-----------------------------------------------------------------------------
 * usage - Program Help
 *
 *---------------------------------------------------------------------------*/
void usage(char *prog)
{
	printf("Usage: %s filename (outdb|\"stats\")\n", prog);
	printf("\n");
	printf("Options:\n");
	printf("    filename    PCAP File to process.\n");
	printf("    outdb       Sqlite database file for output.\n");
	printf("    stats       Just display event stats.\n");
	printf("\n");
	return;
}

/*-----------------------------------------------------------------------------
 * printstats - Prints time and packet processing information
 *
 *---------------------------------------------------------------------------*/
void printstats()
{
	/* Summary*/
	endtime = time(NULL);
	long timespent = endtime - starttime;
	INFOLOG("\nStarted processing packets at : %s", ctime(&starttime));
	INFOLOG("Finished processing packets at: %s", ctime(&endtime));
	printf("\n\n");
	printf("========\n");
	printf("SUMMARY\n");
	printf("========\n");
	printf("Processed %ld records in %ld secs (%f sec per record)\n", count,
			timespent, (double) (timespent / count));
	printf("%20s: %-10ld\n", "Time of First Event", firstev_time);
	printf("%20s: %-10ld\n", "Time of Last Event", lastev_time);
	printf("%20s: %-10ld\n", "TCP Packets", tcp_packet);
	printf("%20s: %-10ld\n", "UDP Packets", udp_packet);
	printf("%20s: %-10ld\n", "DNS Packets", dns_packet);
	printf("%20s: %-10ld\n", "ICMP Packets", icmp_packet);
	printf("%20s: %-10ld\n", "IP Packets", ip_packet);
	printf("%20s: %-10ld\n", "Invalid IP Packets", invalid_ip);
	printf("%20s: %-10ld\n", "IPv6 Packets", ipv6_packet);
	printf("%20s: %-10ld\n", "Unknown Packets", unk_packet);
}
