#-----------------------------------------------------------------------------
# Makefile for compiling p2db
#
#
# Copyright (C) Arun Viswanathan (aviswana@isi.edu)
# This software is licensed under the GPLv3 license, included in
# ./GPLv3-LICENSE.txt in the source distribution
#---------------------------------------------------------------------------
CC=gcc
DEBUGFLAG=
LDFLAGS=-lpthread -lsqlite3 -lghthash -lc -lpcap
CFLAGS=-Wall -g $(DEBUGFLAG) -fPIC 
INCLUDES=
OBJS= ip.o tcp.o udp.o dns.o icmp.o logging.o eventattrs.o db.o  p2db.o   
AOBJS= logging.o eventattrs.o db.o apache.o

all: p2db 

p2db: $(OBJS)
	$(CC) $(CFLAGS) ${OBJS} $(LDFLAGS) -o $@

%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

install: 
	-mv p2db /usr/local/bin/p2db

clean:
	-rm -f packets.sqlite
	-rm -f *.o p2db apache
