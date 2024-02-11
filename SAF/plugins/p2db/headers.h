/*-----------------------------------------------------------------------------
 * headers.h - All the headers in one place
 *
 * Copyright (C) Arun Viswanathan (aviswana@isi.edu)
 * This software is licensed under the GPLv3 license, included in
 * ./GPLv3-LICENSE.txt in the source distribution
 *---------------------------------------------------------------------------*/

#ifndef __HEADERS_H__
#define __HEADERS_H__

#define _GNU_SOURCE

/*Insert all common headers here */
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/time.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <sys/wait.h>
#include <signal.h>
#include <netdb.h>
#include <stdarg.h>
#include <libgen.h>
#include <unistd.h>

/* For Sqlite3 databases */
#include <sqlite3.h>

/* Hash Table Libraries */
#include <ght_hash_table.h>

/* For loading Shared Libraries */
#include <dlfcn.h>
#include <pcap.h>

#include <pthread.h>

#endif
