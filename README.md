
# Semantic Analysis Framework (SAF)
-- Last Update: Arun Viswanathan (11/09/2014)

SAF is a framework for offline data analysis of networked and distributed system data. SAF enables users to analyse and reason over data using semantically meaningful abstractions and thus at a level closer to their understanding of system operation. Contrast this with the traditional analysis techniques that require users to operate over data at the low-level of attributes and values to infer semantic relationships from data.

Analysis using SAF can be broken down into two distinct phases.

**Modeling phase**
SAF enables system or domain experts to encode their high-level understanding of system behavior as ‘’‘abstract models’‘’ over data. For example, the [source:/trunk/SAF/knowbase/net/base_proto/tcpconnsetup.b TCP connection setup model] captures the abstract behavior of a TCP connection setup and the [wiki:ExampleDNSKaminsky DNS Kaminsky Model] captures behavior of the DNS Kaminsky experiment.

Models are written in a simple [wiki:logic-based-modelling logic-based modeling language]. The modeling language provides semantically relevant constructs to express relationships such as causality, ordering, concurrency, exclusions, combinations and dependency relationships between high-level system operations.

**Analysis phase**
Models drive analysis over data. Given timestamped raw-data, in the form of syslogs, packet dumps, alert logs, kernel logs, or application logs, the framework enables users to analyse the data by encoding their high-level questions directly as semantically meaningful models over data. Users can either write their own models from scratch or build one by composing existing models from the knowledge-base.


## Directory contents

SAF    
* Framework related README, source code and tests. Also contains source for various plugins to convert raw data to sqlite  

saf-documentation 
* Contains detailed documentation on framework basics, installation 
          and usage example as a set of PDFs exported from the thirdeye website. Pointers to relevant PDFs below.
* Contains autogenerated documentation of SAF source modules 
    
saf-data
* Example data in both raw and sqlite formats used to test SAF 

saf-releases 
* SAF release tars
 

# Pointers to Documentation

## SAF Installation Instructions
saf-documentation/wikipdfs/thirdeye.deterlab.net/dependencies.pdf

saf-documentation/wikipdfs/thirdeye.deterlab.net/installation.pdf

saf-documentation/wikipdfs/thirdeye.deterlab.net/directorylayout.pdf

saf-documentation/wikipdfs/thirdeye.deterlab.net/p2db.pdf

### SAF Getting started and Examples

saf-documentation/wikipdfs/thirdeye.deterlab.net/simpleanalysis.pdf

saf-documentation/wikipdfs/thirdeye.deterlab.net/ExampleDNSKaminsky.pdf

saf-documentation/wikipdfs/thirdeye.deterlab.net/ExampleHypothesis.pdf

### List of SAF plugins
saf-documentation/wikipdfs/thirdeye.deterlab.net/plugins.pdf

### SAF framework details

saf-documentation/wikipdfs/thirdeye.deterlab.net/WikiStart.pdf

saf-documentation/wikipdfs/thirdeye.deterlab.net/modelanatomy.pdf

saf-documentation/wikipdfs/thirdeye.deterlab.net/ex_attr_const_values.pdf

saf-documentation/wikipdfs/thirdeye.deterlab.net/composemodels.pdf

saf-documentation/wikipdfs/thirdeye.deterlab.net/logic-based-modelling.pdf

saf-documentation/wikipdfs/thirdeye.deterlab.net/knowledgebase.pdf

saf-documentation/wikipdfs/thirdeye.deterlab.net/completestategrammar.pdf

saf-documentation/wikipdfs/thirdeye.deterlab.net/analyze.pdf

saf-documentation/wikipdfs/thirdeye.deterlab.net/simpleanalysis.pdf

saf-documentation/wikipdfs/thirdeye.deterlab.net/architecture.pdf

saf-documentation/wikipdfs/thirdeye.deterlab.net/applications.pdf

saf-documentation/wikipdfs/thirdeye.deterlab.net/languagesyntaxandsemantics.pdf
