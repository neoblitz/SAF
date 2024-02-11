.. Semantic Analysis Framework documentation master file, created by
   sphinx-quickstart on Thu Jul 21 12:50:56 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Semantic Analysis Framework
============================

*SAF* is a framework for offline data analysis of networked and distributed 
system data. SAF enables users to analyse and reason over data using 
semantically meaningful abstractions and thus at a level closer to their 
understanding of system operation. Contrast this with the traditional analysis 
techniques that require users to operate over data at the low-level of 
attributes and values to infer semantic relationships from data.

Analysis using SAF can be broken down into two distinct phases. 

 **Modeling phase** 
   SAF enables system or domain experts to encode their high-level understanding 
   of system behavior as '''abstract models''' over data.  
   For example, the [source:/trunk/SAF/knowbase/net/base_proto/tcpconnsetup.b TCP connection setup model] 
   captures the abstract behavior of a TCP connection setup and the 
   [wiki:ExampleDNSKaminsky DNS Kaminsky Model] captures 
   behavior of the DNS Kaminsky experiment.  

   Models are written in a simple 
   [wiki:logic-based-modelling logic-based modeling language]. The modeling 
   language provides semantically relevant constructs to express relationships 
   such as causality, ordering, concurrency, exclusions, combinations and 
   dependency relationships between high-level system operations. 

 **Analysis phase** 
   Models drive analysis over data. Given timestamped raw-data, in the form of 
   syslogs, packet dumps, alert logs, kernel logs, or application logs, the 
   framework enables users to analyse the data by encoding their high-level 
   questions directly as semantically meaningful models over data. Users can 
   either write their own models from scratch or build one by composing 
   existing models from the knowledge-base. 

.. seealso::

    * Read :doc:`Comparison of SAF with other traditional approaches <files/comparison>`.
    * Read our `NSDI 2011 Semantic Analysis Framework paper <http://www.usenix.org/events/nsdi11/tech/full_papers/Viswanathan.pdf>`_.

Documentation
=============

    :doc:`Getting Started <files/comparison>`
        Simple documentation
        
    Details 
        More details
        




Examples
========

.. toctree::
   :maxdepth: 2

   srcmodules/modules





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

