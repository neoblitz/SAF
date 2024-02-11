###############################################################################
# Script Name 
#   DOSHUSSAIN03
#
# Description      
#   Model to identify a DoS by modeling the detection heuristics from the 
#   below mentioned paper as hypotheses over network traffic captured at an ISP.
# 
#   In the paper, a threshold-based heuristic was presented to identify DDoS 
#   attacks in traces captured at an ISP. Attacks on a victim were identified by 
#   testing for two thresholds on anonymized traces: 
#   (a) the number of sources that connect to the same destination within one 
#        second exceeds 60, or 
#   (b) the traffic rate exceeds 40,000 packets/secs.
# 
#   Conditions (a) and (b) are modeled as hypothesis_1 and hypothesis_2.
#
# Input Requirements
#   Event Type: PACKET_*
#   Event Attributes: sipaddr, dipaddr
#
# Output
#   PACKET_* events satisfying either hypothesis 1 or hypothesis 2.
#   The output would help a user quickly identify the DDoS sources and targets.
#   
#   See sample output at:
#      http://thirdeye.deterlab.net/trac/wiki/ExampleHypothesis#OutputfromSAF      
#   
# Example Dataset(s)
#   http://thirdeye.deterlab.net/trac/browser/trunk/saf-data/db/nsdipaper_casestudy1_2sec_data.sqlite
# 
# SAF compatibility
#   SAF v0.2a and later
# 
# Depends On
#   IPPKTPAIR Model
# 
# References
#   Hussain, A., Heidemann, J., and Papadapoulos, C. A Framework For Classifying
#   Denial of Service Attacks. Proceedings of the Conference on Applications, 
#   Technologies, Architectures, and Protocols for Computer Communication - 
#   SIGCOMM (2003), 99. 
#
# Model Author(s)
#   Arun Viswanathan (aviswana@isi.edu)
# 
# $URL: svn+ssh://arunvisw@www.arunviswanathan.com/svn/trunk/SAF/knowbase/usermodels/doshussain03.b $  
# $LastChangedDate: 2011-07-14 10:21:46 -0700 (Thu, 14 Jul 2011) $
################################################################################ 
[header]
NAMESPACE = USERMODELS
NAME = DOSHUSSAIN03
QUALIFIER = {eventtype='*'}
IMPORT = NET.BASE_PROTO.IPPKTPAIR

[states]
#-------------------------------------------------------------------------------
# We first define the basic events and event groups required for 
# verifying hypothesis 1 and 2 
#  
# Hyp 1. Capture PACKET_* events from many sources (not necessarily 
#        unique) to a single destination.
# Hyp 2. Capture any PACKET_* event from a source to a destination.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Packets from many sources to a single destinations are captured as follows
#  1. Capture a single PACKET event from some source to some destination 
#     (defined as sA).  
#  2. For each such event capture all following events that their 'dipaddr' 
#     equal to the 'dipaddr' of the event.  (defined as sB) 
# 
#  sA provides the context for sB.
# 
#  The 'bcount' attribute for sB forces all events matching sB to be 
#  treated as a single instance comprising of a group of events.
#-------------------------------------------------------------------------------
sA = IPPKTPAIR.ip_pkt_sd()
sB = IPPKTPAIR.ip_pkt_sd(dipaddr=$sA.dipaddr) [bcount >=1]

#-------------------------------------------------------------------------------
# For hypothesis 2, we define sC similar to sB but only group events if 
# we have atleast 40,000 
#-------------------------------------------------------------------------------
sC = IPPKTPAIR.ip_pkt_sd(dipaddr=$sA.dipaddr)[bcount >= 40000]

[behavior]
#-------------------------------------------------------------------------------
# 
# Hyp 1. Verifing hypothesis_1 requires us to define a behavior such that 
#        that there be atleast 1 event matching sA followed by 59 events 
#        matching sB and all within a duration of  1 second. 
#
# Hyp 2. Verifying hypothesis_2 requires us to define a behavior such that the
#        the rate of PACKET_* events matching sA is >= 40000.
#        
#  Note: Hypothesis_2 as modeled here may not always work correctly since 
#        application of the 'rate' keyword considers the entire dataset by default. 
#-------------------------------------------------------------------------------
hypothesis_1 = (sA ~> (sB)[bcount >= 59])[duration <= 1s]
hypothesis_2 = (sC)[rate >= 40000]

[model]
DDOSATTACK(eventno, eventtype,timestamp,timestampusec,sipaddr,dipaddr,eventtype) = (hypothesis_1 or hypothesis_2)
