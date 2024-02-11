Traditional analysis vs. Semantic analysis 
===========================================

For the sake of brevity, assume traditional analysis being done using a popular analysis tool like `wireshark <http://www.wireshark.org/>`_. 

 +-----------------------------+-----------------------------------------------------------+---------------------------------------------------------------------------+
 |                             |     Traditional Analysis                                  |           Semantic Analysis Framework                                     |
 +=============================+===========================================================+===========================================================================+
 | **Input data**              | Network packets.                                          | Any type of data (with available plugin).                                 |
 +-----------------------------+-----------------------------------------------------------+---------------------------------------------------------------------------+
 | **Data abstraction**        | Individual packets.                                       | Behaviors which are e                                                     |
 +-----------------------------+-----------------------------------------------------------+---------------------------------------------------------------------------+
 | **Analysis constructs**     | Simple boolean queries facilitate low-level               | Models capture abstract system behavior without any dependence            |
 |                             | analysis of [[br]] data using attributes and exact values.| on a specific data set.                                                   |
 +-----------------------------+-----------------------------------------------------------+---------------------------------------------------------------------------+
 | **Inferring relationships** | Requires cumbersome multi-step analysis from users        | Models capture semantically-meaningful relationships using operators      |
 |                             | to infer relationships between data                       | and constructs                                                            |
 +-----------------------------+-----------------------------------------------------------+---------------------------------------------------------------------------+
 | **Expertise**               | Lots of expertise required.                               | Models capture expertise and are readily available for reuse.             | 
 +-----------------------------+-----------------------------------------------------------+---------------------------------------------------------------------------+
 | **Sharing and reuse**       | Hard to share expertise in an abstract way.               | Models capture expertise and facilitate sharing and reuse.                |
 +-----------------------------+-----------------------------------------------------------+---------------------------------------------------------------------------+

The key differentiator of the semantic approach is the introduction of the 
notion of *behavior* - a sequence or a group of related facts - 
as a fundamental abstraction for analysis and reasoning over data. 

Behaviors can be composed using a rich set of operators to express 
semantically-relevant relationships. Behaviors capture system semantics 
and operators allow expressing sophisticated relationships between behaviors. 
This enables users to reason over data at higher levels and closer to their 
understanding of system operation.

.. seealso::
     Read the `NSDI'11 paper <http://www.usenix.org/events/nsdi11/tech/full_papers/Viswanathan.pdf>`_ (Section 2) 
     for a more detailed comparison with other approaches.
