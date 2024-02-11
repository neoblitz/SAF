/*-----------------------------------------------------------
 * db.c - Database Related Functions
 *
 * Copyright (C) Arun Viswanathan (aviswana@isi.edu)
 * This software is licensed under the GPLv3 license, included in
 * ./GPLv3-LICENSE.txt in the source distribution
 *-------------------------------------------------------------*/

#include "headers.h"
#include "globals.h"
#include "eventattrs.h"
#include "db.h"
#include "logging.h"


/*-----------------------------------------------------------------------------
 * init_database - Creates a database (if it does not exist), opens it and
 * 				   configures it with default pragmas for fast processing.
 * Inputs
 * 		@db   - Double pointer to a Sqlite3 database
 * 		@name - Name of the database file
 *
 * Returns
 *---------------------------------------------------------------------------*/
int init_database(sqlite3 **db, char *name)
{
	int retval = SUCCESS;
	char * buffer = NULL;

	/* If file not present then create the database*/
	if (fopen(name, "r") == NULL)
	{
		buffer = (char *) malloc(strlen(name) + strlen("sqlite ") + strlen(
				" .databases") + 3);
		if (!buffer)
		{
			CRITLOG("Memory allocation failed!\n");
			exit(EXIT_FAILURE);
		}
		strcpy(buffer, "sqlite3 ");
		strcat(buffer, name);
		strcat(buffer, " .databases");
		CRITLOG("Creating database '%s' \n", buffer);

		/* TODO: Make sure that we are executing only what we want
		 * and not something that someone else wants*/
		if (system(buffer) < 0)
		{
			CRITLOG("Sqlite database creation failed !!\n");
			exit(EXIT_FAILURE);
		}
	} else {
		CRITLOG("Database %s already exists. Please  use a different name !\n", name);
		exit(EXIT_FAILURE);
	}

	if (buffer)
		free(buffer);

	retval = sqlite3_open(name, db);
	if (retval)
	{
		CRITLOG("Can't open database: %s\n", sqlite3_errmsg(*db));
		exit(2);
	}

	/* Set a timeout of 5sec to try for record insertion. This is the pysqlite default*/
	sqlite3_busy_timeout(*db, 5000);

	/*
	 *  Database optimzations to improve performance
	 *  http://web.utk.edu/~jplyon/sqlite/SQLite_optimization_FAQ.html
	 *  http://www.sqlite.org/pragma.html
	 */

	/* Reclaims unused space */
	execute_sql(*db, "PRAGMA auto_vacuum=None");

	/* Makes sure that the database does not wait for disk operations to complete
	 * This gives maximum speedup*/
	execute_sql(*db, "PRAGMA synchronous=off");

	/* Puts temporary indices and tables in memory. Speeds up operation drastically*/
	execute_sql(*db, "PRAGMA temp_store=MEMORY");

	/* Default cache_size */
	execute_sql(*db, "PRAGMA default_cache_size=32000");

	execute_sql(*db, "PRAGMA journal_mode=OFF");

	return retval;
}

/*-----------------------------------------------------------------------------
 * create_tables - Create the default tables for ICMP, TCP, IP, UDP, DNS
 * 				The attributes for each of these are defined in eventattrs.c
 * Inputs
 * 		@db  - Pointer to a Sqlite3 database
 *
 * Returns
 *---------------------------------------------------------------------------*/
int create_tables(sqlite3 *db)
{
	int retval = SUCCESS;

	/* Create table in record database*/
	if (create_sql_table(db, EVENT_ICMP, icmp_attrs, num_icmp_attrs)
			!= SUCCESS)
	{
		CRITLOG("ERROR: Failure while creating table name %s\n",  EVENT_ICMP);
		retval = FAILURE;
		goto end;
	}

	if (create_sql_table(db, EVENT_TCP, tcp_attrs, num_tcp_attrs) != SUCCESS)
	{
		CRITLOG("ERROR: Failure while creating table name %s\n",  EVENT_TCP);
		retval = FAILURE;
		goto end;
	}

	if (create_sql_table(db, EVENT_UDP, udp_attrs, num_udp_attrs) != SUCCESS)
	{
		CRITLOG("ERROR: Failure while creating table name %s\n",  EVENT_UDP);
		retval = FAILURE;
		goto end;
	}

	if (create_sql_table(db, EVENT_IP, ip_attrs, num_ip_attrs) != SUCCESS)
	{
		CRITLOG("ERROR: Failure while creating table name %s\n",  EVENT_IP);
		retval = FAILURE;
		goto end;
	}

	if (create_sql_table(db, EVENT_DNS, dns_attrs, num_dns_attrs) != SUCCESS)
	{
		printf("ERROR: Failure while creating table name %s\n",  EVENT_DNS);
		retval = FAILURE;
		goto end;
	}

	if (create_sql_table(db, EVENT_APP_HTTPD, apphttpd_attrs, num_apphttpd_attrs) != SUCCESS)
	{
		printf("ERROR: Failure while creating table name %s\n",  EVENT_DNS);
		retval = FAILURE;
		goto end;
	}


	end: return retval;
}

/*-----------------------------------------------------------------------------
 * callback - The callback function to sqlite3_exec
 *
 * Inputs
 *
 * Returns
 *---------------------------------------------------------------------------*/
 static int callback(void *NotUsed, int argc, char **argv, char **azColName)
{
	int i;
	for (i = 0; i < argc; i++)
	{
		printf("%s = %s\n", azColName[i], argv[i] ? argv[i] : "NULL");
	}
	printf("\n");
	return 0;
}

/*-----------------------------------------------------------------------------
 * execute_sql -Executes a  SQL Statement
 *
 * Inputs
 *      @db  - Pointer to a Sqlite3 database
 *      @sql - A SQL Statement to execute
 *
 * Returns
 *      A pointer to the database
 *---------------------------------------------------------------------------*/

int execute_sql(sqlite3* db, char *sql)
{
	int retval = 0;
	char *errmsg = NULL;

	retval = sqlite3_exec(db, sql, callback, 0, &errmsg);
	if (retval != SQLITE_OK)
	{
		if (strstr(errmsg, "already exists"))
		{
			retval = 1;
		}
		DEBUGLOG("SQL error: %s (%d)\n", errmsg, retval);
		sqlite3_free(errmsg);
		goto end;
	}

	end: return retval;
}

/*-----------------------------------------------------------------------------
 * create_sql_table - Creates a SQL table if a table with same name does not
 *                    exist
 *
 * Inputs
 *      @db  - Pointer to a Sqlite3 database
 *      @tname - Table Name
 *      @targs - Pointer to 'create table' arguments
 *
 * Returns
 *      SUCCESS / Error Code
 *---------------------------------------------------------------------------*/
int create_sql_table(sqlite3* db, char *tname, char **targs, int len)
{
	int retval = SUCCESS;
	char *sqlcmd = "create table "; /* Include space */
	char *avstring = malloc(1024);
	if (!avstring)
	{
		CRITLOG("Malloc failed \n");
		return FAILURE;
	}

	int i = 0;
	strcpy(avstring, "(");
	for (i = 0; i < len; i++)
	{
		//DEBUGLOG("Processing attributes: %s\n", targs[i]);
		int lenkey = strlen(targs[i]);
		int currlen = strlen(avstring);
		int totallen = currlen + lenkey + 3;
		if (totallen > 1024)
		{
			avstring = (char *) realloc(avstring, totallen * 2);
			DEBUGLOG("\tResizing the AV string \n");
			if (!avstring)
			{
				CRITLOG("Error REallocating memory for attr=value string\n");
				continue;
			}
		}

		strcat(avstring, targs[i]);
		strcat(avstring, ",");
	}
	avstring[strlen(avstring) - 1] = '\0';
	strcat(avstring, ");");
	DEBUGLOG("String for sqlcmd : \n\t%s\n", avstring);

	char *sqlstmt = (char *) malloc(strlen(sqlcmd) + strlen(tname) + strlen(
			avstring) + 3);
	if (!sqlstmt)
	{
		CRITLOG("Malloc failed \n");
		retval = FAILURE;
		goto end;
	}
	strcpy(sqlstmt, sqlcmd);
	strcat(sqlstmt, tname);
	strcat(sqlstmt, avstring);

	DEBUGLOG("Executing SQL statement: \n\t%s\n", sqlstmt);
	if ((retval = execute_sql(db, sqlstmt)) != SUCCESS)
	{
		if (retval == FAILURE)
		{
			CRITLOG("Error while creating add statement '%s'\n",
					sqlite3_errmsg(db));
			retval = FAILURE;
			goto end;
		}
	}

	end: if (sqlstmt)
		free(sqlstmt);
	if (avstring)
		free(avstring);
	return retval;
}

/*-----------------------------------------------------------------------------
 * prepare_stmt - Creates a SQL Prepared Statement for SQL inserts
 *
 * Inputs
 *      @db  	- Pointer to a Sqlite3 database
 *      @ppStmt - Double Pointer to the statement
 *      @tablename - Tablename to insert into
 *      @attrs     - A pointer to list of attributes
 *      @len       - Length of the attribute list
 *
 * Returns
 *      SUCCESS / FAILURE
 *---------------------------------------------------------------------------*/

int prepare_stmt(sqlite3 *db, sqlite3_stmt **ppStmt, char *tablename,
		char *attrs[], int len)
{
	char sqlcmd[1024];
	int retval = SUCCESS;
	int i = 0;

	sprintf(sqlcmd, "insert into %s values(", tablename);
	for (i = 0; i < len; i++)
	{
		strcat(sqlcmd, "?,");
	}
	sqlcmd[strlen(sqlcmd) - 1] = '\0';
	strcat(sqlcmd, ");");
	DEBUGLOG("Executing SQL  '%s'\n", sqlcmd);
	if (sqlite3_prepare_v2(db, sqlcmd, -1, ppStmt, NULL) != SQLITE_OK)
	{
		CRITLOG("Error while creating add statement '%s'\n", sqlite3_errmsg(db));
		retval = FAILURE;
		goto end;
	}

	INFOLOG("Statement preparation successful for %s\n", tablename);
	end: return retval;
}

/*-----------------------------------------------------------------------------
 * insert_into_table - Inserts a record(given as a hash of attributes/values)
 * 					   using a previously prepared statement
 *
 * Inputs
 *      @db  	- Pointer to a Sqlite3 database
 *      @kvhash - Hash of attributes and values (the
 *      @ppStmt - Pointer to the previously prepared statement
 *      @attrs  - A pointer to list of attributes
 *      @len    - Length of the attribute list
 *
 * Note:  kvhash must contain all attrs present in the attribute list.
 *
 * Returns
 *      SUCCESS / FAILURE
 *---------------------------------------------------------------------------*/
int insert_into_table(sqlite3* dbr, ght_hash_table_t *kvhash,
		sqlite3_stmt *ppStmt, char *attrs[], int len)
{
	int retval = SUCCESS;
	int i = 0;

	for (i = 0; i < len; i++)
	{
		char *newstr = strdup(attrs[i]);
		char *attr = strtok(newstr, " ");
		char * type = strtok(NULL, " ");
		//DEBUGLOG("Processing attr '%s' of type '%s'\n", attr, type);

		if (strcmp(type, "integer") == 0)
		{
			char *val = ght_get(kvhash, strlen(attr) + 1, attr);
			if (val != NULL)
			{
				if (sqlite3_bind_int64(ppStmt, i + 1, strtol(val, NULL, 0))
						!= SQLITE_OK)
				{
					CRITLOG("Error while binding data. '%s'\n", sqlite3_errmsg(
							dbr));
				}
			}
			else
			{
				DEBUGLOG("Got  NULL val for '%s'\n", attr);
			}
		}

		if (strcmp(type, "text") == 0)
		{
			char *val = ght_get(kvhash, strlen(attr) + 1, attr);
			if (val != NULL)
			{
				if (sqlite3_bind_text(ppStmt, i + 1, val, -1, SQLITE_STATIC)
						!= SQLITE_OK)
				{
					CRITLOG("Error while binding data. '%s'\n", sqlite3_errmsg(
							dbr));
				}
			}
			else
			{
				DEBUGLOG("Got  NULL val for '%s'\n", attr);
			}
		}

		if (newstr)
			free(newstr);
	}

	if (SQLITE_DONE != sqlite3_step(ppStmt))
	{
		CRITLOG("Error while inserting data. '%s'\n", sqlite3_errmsg(dbr));
		retval = FAILURE;
	}
	sqlite3_reset(ppStmt);
	return retval;
}
