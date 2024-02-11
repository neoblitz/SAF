/*-----------------------------------------------------------
 * p2db.h
 *
 * Copyright (C) Arun Viswanathan (aviswana@isi.edu)
 * This software is licensed under the GPLv3 license, included in
 * ./GPLv3-LICENSE.txt in the source distribution
 *-------------------------------------------------------------*/

#ifndef PCONVERT_H_
#define PCONVERT_H_

void printstats();

void usage(char *prog);

void sigint_handler();

void free_hash(ght_hash_table_t * hash);

int create_sql_table(sqlite3* db, char *tname, char *targs[], int len);

void cleanup();

void process_packet(u_char *args, const struct pcap_pkthdr *header,
		const u_char *packet);
ght_hash_table_t * dissect_packet(u_char *args,
		const struct pcap_pkthdr *header, const u_char *packet, long count);
#endif
