/*-----------------------------------------------------------------------------
 * globals.h - Contains global defines and structures used throughout
 *
 * Copyright (C) Arun Viswanathan (aviswana@isi.edu)
 * This software is licensed under the GPLv3 license, included in
 * ./GPLv3-LICENSE.txt in the source distribution
 *---------------------------------------------------------------------------*/

#include "headers.h"
#ifndef __GLOBALS_H__
#define __GLOBALS_H__

#define FAILURE 				1
#define SUCCESS 				0
#define MAX_BUF_LENGTH 			1024
#define MAX_LOG_BUFFER 			8192
#define ENABLE_CONSOLE_PRINT 	1
#define MAX_TBUF_SIZE 			512
#define false 					0
#define true  					1


typedef struct _pcap_packet
{
	struct pcap_pkthdr header; /* The header that pcap gives us */
	const unsigned char *packet; /* The actual packet */
	pcap_t* pcap_file; /* Pointer to open PCAP file*/
} pcap_packet;


#endif
