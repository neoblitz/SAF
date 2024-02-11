/*-----------------------------------------------------------------------------
 * logging.c - Common API for logging according to debug levels
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

#include "logging.h"
#include "globals.h"
#include "headers.h"

/* File specfic globals */
static int verbosity = LOG_CRITICAL;
static FILE *fpfile = NULL;
static char buffer[MAX_LOG_BUFFER];
static pthread_mutex_t m_log; /* Mutex to protect writing to the log */

/*-----------------------------------------------------------------------------
 * mainlog(): Logs the specified string to file or console depending on
 *           'loglevel'
 *
 *----------------------------------------------------------------------------*/

void mainlog(int loglevel, char *fmt, ...)
{
	va_list argptr;
	char *ptr = buffer;

	pthread_mutex_lock(&m_log);
	va_start(argptr, fmt);

	if (verbosity >= loglevel)
	{
		vsnprintf(ptr, MAX_LOG_BUFFER, fmt, argptr);
		if (ENABLE_CONSOLE_PRINT)
		{
			if (loglevel == LOG_ERROR)
				fprintf(stderr, "%s", buffer);
			else
				fprintf(stdout, "%s", buffer);
		}

		if (fpfile)
		{
			fprintf(fpfile, "%s", buffer);
		}

	}
	fflush(fpfile);
	va_end(argptr);
	pthread_mutex_unlock(&m_log);
}

/*----------------------------------------------------------------------------
 * set_verbosity : Sets the desired verbosity
 *
 *----------------------------------------------------------------------------*/

void set_verbosity(int value)
{
	verbosity = value;
}

/*----------------------------------------------------------------------------
 * get_verbosity : Returns the current verbosity level
 *
 *----------------------------------------------------------------------------*/

int get_verbosity()
{
	return verbosity;
}

/*-----------------------------------------------------------------------------
 * init_logger : Initializes the logging
 *
 *-----------------------------------------------------------------------------*/

int init_logger(char *logfile)
{
	int retval = LOG_SUCCESS;

	fpfile = NULL;

	/*Check if a logfile name has been specified*/
	if (logfile)
	{
		fpfile = fopen(logfile, "w");
		if (!fpfile)
		{
			perror("Opening logfile failed");
			retval = ERR_OPENING_FILE;
		}
	}

	/* Initialize the mutex */
	pthread_mutex_init(&m_log, NULL);

	return retval;
}

/*-----------------------------------------------------------------------------
 * deinit_logger : Closes the log file and frees up resources
 *
 *-----------------------------------------------------------------------------*/
void deinit_logger()
{
	if (fpfile)
		fclose(fpfile);
}

