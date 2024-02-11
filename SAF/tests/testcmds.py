# testcmds.py 
#     Lists tests to be run by runtests.py
# 
# File Format 
# -------------
# Sections:
#     A section contains tests testing a specific aspect of the system. Sections
#     can be run individually. Sections are separated by comment headers.
#
# TestGroup: 
#     A TestGroup is a hash structure within a section and is a grouping of 
#     similar tests. Every TestGroup is viewed by PyUnit as a single test.
# 
# TestEntry:
#     A TestEntry is a single hash entry with the following format:
#         Hash key:  is the testid. The key is also used as an expected output 
#                    filename residing under the expected folder
#         Hash value: is a string of command option to main.py
# 
#
# Arun Viswanathan (aviswana@isi.edu)
#------------------------------------------------------------------------------     

#------------------------------------------------------------------------------
# Simple Feature Tests 
#    Tests basic features  
# 
# Command to run
#    python runtests.py --f
#------------------------------------------------------------------------------
featuretests_qualifier = {
# Empty qualifier expression
'ft_qualifier.1':"--db %s/tcpudpdns_mix_20rec.sqlite  --model tests/bscripts/ft_qualifier.1.b ",
# Multiple spaces for null
'ft_qualifier.1.1':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_qualifier.1.1.b ",
# Simple qualifier expression
'ft_qualifier.2':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_qualifier.2.b ",
# Complex qualifier expression with anonymous states
'ft_qualifier.3':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_qualifier.3.b ",
'ft_qualifier.3.1':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_qualifier.3.1.b --pretty",
'ft_qualifier.3.2':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_qualifier.3.2.b --pretty",
# Non-matching expression
'ft_qualifier.4':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_qualifier.4.b --pretty ",
# Multiple expressions
'ft_qualifier.5':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_qualifier.5.b ",
}

featuretests_wildcards = {
# Wildcards in values
'ft_qualifier.6':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_qualifier.6.b ",
# Wildcards in values
'ft_qualifier.6.1':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_qualifier.6.1.b ",
# Wildcards in values
'ft_qualifier.6.2':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_qualifier.6.2.b --pretty"
}

featuretests_relationalops = {
# Relational operators
'ft_qualifier.7':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_qualifier.7.b --pretty",
'ft_qualifier.8':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_qualifier.8.b --pretty"
}

featuretests_constraints = {
'ft_constraints.1':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_constraints.1.b --pretty",
'ft_constraints.2':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_constraints.2.b --pretty",
'ft_constraints.3':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_constraints.3.b --pretty",
'ft_constraints.4':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_constraints.4.b --pretty",
}

featuretests_bconstraints = {
'ft_bconstraint_rate.1':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_bconstraint_rate.1 --pretty",
'ft_bconstraint_rate.2':"--db %s/dnsflows_100rec.sqlite   --model tests/bscripts/ft_bconstraint_rate.2 --pretty",
'ft_bconstraint_rate.3':"--db %s/dnsflows_5000rec.sqlite   --model tests/bscripts/ft_bconstraint_rate.3",
'ft_bconstraint_icount.1':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_bconstraint_icount.1 --pretty",
'ft_bconstraint_duration.1':"--db %s/nsdipaper_casestudy1_2sec_data.sqlite  --model tests/bscripts/ft_bconstraint_duration.1 --pretty",
}

featuretests_sconstraints = {
'ft_sconstraint_bcount.1':"--db %s/dnsflows_100rec.sqlite --model tests/bscripts/ft_sconstraint_bcount.1 --pretty",
}


featuretests_opconstraints = {
'ft_opconstraints.1':"--db %s/tcpudpdns_mix_20rec.sqlite     --model tests/bscripts/ft_opconstraints.1.b ",
}

featuretests_logicalops = {
'ft_logicalops.1':"--db %s/nsdipaper_casestudy2_data.sqlite   --model tests/bscripts/ft_logicalops.1.b --pretty",
}

featuretests_concurrentops = {
'ft_overlapop.1':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_overlap.1.b --pretty",
'ft_overlapop.2':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_overlap.2.b --pretty"
}

featuretests_leadstoop = {
'ft_leadstoop.1':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_leadstoop.1.b",
'ft_leadstoop.2':"--db %s/nsdipaper_casestudy1_2sec_data.sqlite   --model tests/bscripts/ft_leadstoop.2.b --pretty",
'ft_leadstoop.3':"--db %s/codered.1.sqlite   --model tests/bscripts/ft_leadstoop.3.b --pretty",
'ft_leadstoop.4':"--db %s/nsdipaper_casestudy1_2sec_data.sqlite   --model tests/bscripts/ft_leadstoop.4.b --pretty",
}

featuretests_import = {
'ft_import.1':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_import.1.b --pretty",
}

featuretests_errors = {
'ft_errors.1':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_errors.1.b --pretty",
'ft_errors.2':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_errors.2.b --pretty",
'ft_errors.3':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ft_errors.3.b --pretty",
}
#------------------------------------------------------------------------------
# Basic Smoke Tests 
#    Tests Overall Functionality and sanity of the core algorithms and data 
#    structures. 
# 
# Command to run
#    python runtests.py --b
#------------------------------------------------------------------------------
basictests_dns = {
'dnsreqres.1':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/dnsreqres.b ",
'dnsreqres.2':"--db %s/tcpudpdns_mix_298rec.sqlite   --model tests/bscripts/dnsreqres.b ",
'dnsreqres.3':"--db %s/dnsflows_100rec.sqlite    --model tests/bscripts/dnsreqres.b ",
'dnsreqres.4':"--db %s/dnsflows_5000rec.sqlite   --model tests/bscripts/dnsreqres.b "
}

basictests_ip = {
'ippktpair.1':"--db %s/tcpudpdns_mix_20rec.sqlite   --model tests/bscripts/ippktpair.b ",
'ippktpair.2':"--db %s/tcpudpdns_mix_298rec.sqlite   --model tests/bscripts/ippktpair.b ",
}

basictests_tcp_pkt = {
'tcppktpair.1':"--db %s/tcpudpdns_mix_20rec.sqlite    --model tests/bscripts/tcppktpair.b ",
'tcppktpair.2':"--db %s/httpflows_1077rec.sqlite   --model tests/bscripts/tcppktpair.b ",
}

basictests_tcp_connsetup = {
'tcpconnsetup.1':"--db %s/tcpudpdns_mix_20rec.sqlite    --model tests/bscripts/tcpconnsetup.b ",
'tcpconnsetup.2':"--db %s/httpflows_1077rec.sqlite    --model tests/bscripts/tcpconnsetup.b ",
}

basictests_tcp_conntdown = {
'tcpconntdown.1':"--db %s/tcpudpdns_mix_298rec.sqlite     --model tests/bscripts/tcpconntdown.b ",
'tcpconntdown.2':"--db %s/httpflows_1077rec.sqlite    --model tests/bscripts/tcpconntdown.b ",
}

basictests_udp = {
'udppktpair.1':"--db %s/tcpudpdns_mix_20rec.sqlite    --model tests/bscripts/udppktpair.b ",
}


#------------------------------------------------------------------------------
# Paper case studies 
#    Tests the case studies in the paper
# 
# Command to run
#    python runtests.py --c
#------------------------------------------------------------------------------
casestudy_dnskaminsky = {
'dnskaminsky.1':"--db %s/nsdipaper_casestudy2_data.sqlite   --model tests/bscripts/dnskaminsky.1.b ",
'dnskaminsky.2':"--db %s/nsdipaper_casestudy2_data.sqlite   --model tests/bscripts/dnskaminsky.2.b "
}

casestudy_doshussain03 = {
'doshussain.1':"--db %s/nsdipaper_casestudy1_2sec_data.sqlite    --model tests/bscripts/doshussain03.b --pretty",
}


#------------------------------------------------------------------------------
# Plugin tests
#    Tests for ascii plugins
#
#------------------------------------------------------------------------------
syslog_plugin_test = {
'plugin_syslog.1':"-i %s/../rawdata/syslog -o /tmp/temp/syslog.sqlite -p syslog -v"
}

bind_plugin_test = {
'plugin_bind.1':"-i %s/../rawdata/bindquery.log -o /tmp/temp/syslog.sqlite -p bind -v"
}

basic_plugin_test = {
'plugin_basic.1':"""-i %s/../rawdata/argusflow_10recs_nondefault.log -o /tmp/temp/basic.sqlite -p basic -a stime:real|duration:real|sipaddr:t|dipaddr:t -v"""
}

argus_plugin_test = {
'plugin_argus.1':"-i %s/../rawdata/argusflow_1000recs_defaultoutput.log -o /tmp/temp/argus1.sqlite -p argus -v",
'plugin_argus.2':"-i %s/../rawdata/argusflow_10recs_nondefault.log -o /tmp/temp/argus2.sqlite -p argus -a stime:real|duration:real|sipaddr:t|dipaddr:t  -v",
'plugin_argus.3':"-i %s/../rawdata/argusflow_1000recs_defaultoutput_addedcols.log -o /tmp/temp/argus3.sqlite -p argus -v -x duration:real|tcprtt:real ",
'plugin_argus.4':"-i %s/../rawdata/argusflow_1000recs_defaultoutput_addedcols.log -o /tmp/temp/argus4.sqlite -p argus -v -x duration:real|tcprtt:real -s eventtype=SIMPLE "
}

mysql_plugin_test = {
'plugin_mysql.1':"-i %s/../rawdata/mysqld.log -o /tmp/temp/mysqld.sqlite -p mysql -v"
}

apache_plugin_test = {
'plugin_apache.1':"-i %s/../rawdata/access_combined.log -o /tmp/temp/apache.sqlite -p apache -v"
}

