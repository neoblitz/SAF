/*-----------------------------------------------------------------------------
 * logging.h - Macros / defines and function prototypes of logging.c
 *
 *
 * verbosity    Meaning
 * --------------------
 *     1        Critical
 *     2        Informational
 *     3        Error
 *     4        Debug
 *
 * Copyright (C) Arun Viswanathan (aviswana@isi.edu)
 * This software is licensed under the GPLv3 license, included in
 * ./GPLv3-LICENSE.txt in the source distribution
 *---------------------------------------------------------------------------*/

#ifndef _LOGGING_H_
#define _LOGGING_H_

/*
 * MACRO definitions
 */

#define LOG_CRITICAL 1
#define LOG_INFO     2
#define LOG_ERROR    3
#define LOG_DEBUG    4

#define CRITLOG(fmt, ...)      mainlog(LOG_CRITICAL, fmt, ## __VA_ARGS__)
#define INFOLOG(fmt, ...)      mainlog(LOG_INFO, fmt, ## __VA_ARGS__)
#define ERRLOG(fmt, ...)       mainlog(LOG_ERROR, fmt, ## __VA_ARGS__)
#define DEBUGLOG(fmt, ...)     mainlog(LOG_DEBUG, fmt, ## __VA_ARGS__)

/* ERROR Definitions */
#define    ERR_OPENING_FILE   -1
#define    LOG_SUCCESS         0

/*
 * Function Prototypes
 **/
void mainlog(int loglevel, char *fmt, ...);
void set_verbosity(int value);
int init_logger(char *filename);
int get_verbosity();
void deinit_logger();

#endif
