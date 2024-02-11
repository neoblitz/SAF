/*--------------------------------------------------------------------------------------------------------------------------
 * db.h - Database Related Functions
 *
 * Copyright (C) Arun Viswanathan (aviswana@isi.edu)
 * This software is licensed under the GPLv3 license, included in
 * ./GPLv3-LICENSE.txt in the source distribution
 *--------------------------------------------------------------------------------------------------------------------------*/

#ifndef  DB_H__
#define DB_H__

int create_tables(sqlite3 *db);
int init_database(sqlite3 **db, char *name);
int execute_sql(sqlite3* db, char *sql);
int create_sql_table(sqlite3* db, char *tname, char *targs[], int len);

int insert_into_table(sqlite3* dbr,
                              ght_hash_table_t *kvhash,
                              sqlite3_stmt *ppStmt,
                              char *attrs[],
                              int len);

void end_insert_transaction(sqlite3 *db, sqlite3_stmt* ppStmt) ;
int prepare_stmt(sqlite3 *db, sqlite3_stmt **ppStmt, char *tablename, char *attrs[], int len);
#endif
