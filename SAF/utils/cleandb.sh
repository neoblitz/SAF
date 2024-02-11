#!/bin/bash
#cleandb.sh - Simple script to delete indices created in a SQLite database
#
# Copyright (C) 2011 University of Southern California.
# All rights reserved.
#
# Redistribution and use in source and binary forms are permitted
# provided that the above copyright notice and this paragraph are
# duplicated in all such forms and that any documentation, advertising
# materials, and other materials related to such distribution and use
# acknowledge that the software was developed by the University of
# Southern California, Information Sciences Institute.  The name of the
# University may not be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND WITHOUT ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
# 
# Author: Arun Viswanathan (aviswana@usc.edu)
#------------------------------------------------------------------------------

# 
#  Usage: ./cleandb.sh <name of database file or directory containing many database files>
# 


if [ "$1" != "" ]; then
	for db in `ls $1`; do
		dbpath=$1"/"$db
		echo "Cleaning indices in $dbpath"
		for t in `sqlite3 $dbpath .table`; do
			echo "Table --> $t"
			indices=$(sqlite3 $dbpath ".indices $t")
			for ind in $indices; do
				echo "Index --> $ind"
				sqlite3 $dbpath "drop index $ind"
			done
		done
	done
else
	echo "Enter a single valid database name or a directory containing databasese to clean!"
fi

