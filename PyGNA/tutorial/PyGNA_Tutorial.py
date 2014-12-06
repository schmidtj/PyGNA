#
#       8888888b.            .d8888b.  888b    888        d8888 
#       888   Y88b          d88P  Y88b 8888b   888       d88888 
#       888    888          888    888 88888b  888      d88P888 
#       888   d88P 888  888 888        888Y88b 888     d88P 888 
#       8888888P"  888  888 888  88888 888 Y88b888    d88P  888 
#       888        888  888 888    888 888  Y88888   d88P   888 
#       888        Y88b 888 Y88b  d88P 888   Y8888  d8888888888 
#       888         "Y88888  "Y8888P88 888    Y888 d88P     888 
#                       888                                     
#                  Y8b d88P                                     
#                   "Y88P"                                      

__author__ = """\n""".join(['Jeffrey Schmidt (jschmid1@binghamton.edu)',
                            'Benjamin Bush (benjaminjamesbush@gmail.com)',
                            'Hiroki Sayama (sayama@binghamton.edu)'])

#   Welcome to the executable PyGNA tutorial. You can use this tutorial to
#   learn how to use PyGNA. This tutorial is executable, which means you
#   can run it using Python. You may also modify the code in this tutorial
#   in order to to run PyGNA on your own adaptive network data.


#   --- WHAT IS PyGNA? ------------------------------------------------------
#   PyGNA is a Python implementation of Generative Network Automata (GNA), which is
#   a generalized framework for modeling adaptive network dynamics using
#   graph rewritings.
#
#   A GNA is a mechanism for generating a sequence of graphs, such as
#
#                   ( G_0, G_1, G_2, G_3, ... )
#
#   The GNA framework assumes that the transition function which maps each
#   graph to its successor can be separated into the following two mechanisms:
#
#   1. Extraction:  The extraction mechanism selects the subgraph of the
#                   current graph that is to be changed to create the next
#                   graph. This subgraph is called the "extracted subgraph."
#
#   2. Replacement: The replacement mechanism maps the extracted subgraph to
#                   the new subgraph (called the "replacement subgraph") that
#                   is to take its place. The replacement mechanism also
#                   provides a node correspondence function, which specifies
#                   exactly how the replacement subgraph is to be reinserted
#                   into the empty space left behind when the extracted
#                   subgraph was removed from the original graph.
#
#   The temporal dynamics of any particular GNA can be defined as a triple
#
#                   (E, R, I)
#
#   Where E is an extraction mechanism, R is a replacement mechanism, and I
#   is the initial configuration, i.e. the first graph of the sequence.
#
#   PyGNA can be used to automatically discover extraction and replacement
#   mechanisms which capture both state transition and topological
#   transformation in the data associated with the spatio-temporal evolution
#   of a complex network.
#
#   More information and documentation on the project can be found at the
#   project's homepage: http://gnaframework.sourceforge.net/
#   Funding for this project was provided by the National Science Foundation.
#   Information about this grant can be found at
#   http://coco.binghamton.edu/NSF-CDI.html
#   You may also wish to contact the authors of the software, listed above.


#   --- SETTING UP THE PyGNA system -----------------------------------------
#   The first thing we have to do is import the PyGNA module and create a new
#   gna object.

import PyGNA
myGNA = PyGNA.gna.gna()


#   --- CREATING AND IMPORTING ADAPTIVE NETWORK DATA -------------------------
#   PyGNA stores data in a container called the NetworkFrames object. The
#   NetworkFrames object holds the sequence of graphs that you want to
#   analyze. In this tutorial, we will be creating a NetworkFrames object
#   from scratch and populating it with simulated data that we generate on
#   the fly.
#
#   First, we must create a new NetworkFrames object.

myNetworkFrames = PyGNA.NetworkFrames.NetworkFrames()

#   Now we will populate the NetworkFrames object with data. The following
#   code generates a sequence of graphs based on a simplified version of the
#   Barabasi-Albert preferential attachment model. Read about it at
#   http://en.wikipedia.org/wiki/Barabasi-Albert_model

import random
import networkx as nx
G = nx.Graph()
G.add_edge(0,1)
myNetworkFrames.addGraph(G) #adds initial graph to the NetworkFrames object.
for i in range(2,101):
    nodeList = []
    for node in G.nodes():
        nodeList += [node for x in xrange(G.degree(node))]
    selectedNode = random.choice(nodeList)
    G.add_edge(selectedNode, i)
    myNetworkFrames.addGraph(G) #add next graph to the networkFrames object.

#   Now that we have populated our NetworkFrames object with data, it is best
#   to write it to disk. PyGNA reads and writes network data using a format
#   called graphML. GraphML is an XML file format that is unique in that it
#   uses well defined XML syntax to represent network data.  Through the use
#   of GraphML's <graph> tags, multiple graphs can be contained in the same
#   file, making it an ideal format to represent adaptive networks.
#   More information on the GraphML file format can be found at
#   http://graphml.graphdrawing.org/
#
#   We write the data in our NetworkFrames object to a graphML file like so:

myNetworkFrames.writeGraphs('myNetworkData.graphML')

#   We are now ready to load the data into our GNA object. We do this by
#   reading the graphML file from the disk. 

myGNA.openGraphMLNetwork('myNetworkData.graphML')

#   Note that if you already have a pre-existing graphML file, it can also be
#   loaded in this way. You can use this method to import empirical network
#   data into PyGNA.


#   --- CREATE A CLASS CONTAINING USER DEFINED EXTRACTION MECHANISMS --------
#   PyGNA uses EXTRACTION MECHANISMS, described above, to try to find patterns
#   in the parts of the network that are changing at any given time. When
#   analyzing adaptive network data, PyGNA will test each extraction mechanism
#   and determine which mechanism does the best job of explaining the data.
#   PyGNA allows you to easily create extraction mechanisms with a custom
#   domain specific language that runs ontop of Python. Currently,
#   user-created extraction mechanisms are limited to subgraphs consisting of
#   a single node. This limitation will be relaxed in future versions of the
#   software.
#
#   To define extraction mechanisms, users must use a set of predefined
#   keywords, which we describe below:
#
#   degree              The number of links adjacent to the extracted node.
#
#   state               The state of the extractd node.
#
#   clustering          The clustering coefficient of the extracted node.
#                       (see http://tinyurl.com/nx-clustering for info)
#
#   bCentrality         The betweenness centrality of the extracted node.
#                       (see http://tinyurl.com/nx-bcentrality for info)
#
#   cCentrality         The closeness centrality of the extracted node.
#                       (see http://tinyurl.com/nx-ccentrality for info)
#
#   neighborStates      A Python list containing the states of each node that
#                       is connected to the extracted node by a link.
#
#   inDegree            The number of arrows pointing to the extracted node.
#   
#   outDegree           The number of arrows pointing away from the extracted
#                       node.
#
#   inNeighborStates    A Python list containing the states of each node that
#                       is connected to the extracted node via an arrow that
#                       points toward the extracted node.
#
#   outNeighborStates   A Python list containing the states of each node that
#                       is connected to the extracted node via an arrow that
#                       points away from the extracted node.
#
#   The user can use these keywords to create set of functions. These
#   functions must always evaluate to a non-negative real number. The
#   functions must be wrapped in a special user defined class which inherits
#   from PyGNA's UserExtractions class, as we show in the examples below.

from PyGNA import UserExtractions
class myExtractions(UserExtractions.UserExtractions):

    def nodeDegree():
        return degree
    
    def betweenness():
        return bCentrality

    def closeness():
        return cCentrality

    def clusteringCoefficient():
        return clustering

    def greaterNeighborhoodState():
        avg_neighbor_state = sum(neighborStates) / degree
        if state >= avg_neighbor_state:
            return 1
        else:
            return 0

    def netIn():
        netIn = inDegree - outDegree
        return max(netIn, 0)

#   Note: These examples were chosen to illustrate how to define extraction
#   mechanisms, not to be used in any paticular application. In your own work
#   you should define your own extraction mechanisms based on your knowledge
#   of the system that you are investigating.


#   --- IMPORT USER DEFINED EXTRACTION MECHANISMS INTO THE GNA OBJECT -------
#   Now that you have created your user extractions class, you must tell your
#   GNA object that you want to use it.

myGNA.addUserExtractions(myExtractions)

#   --- FIND THE BEST EXTRACTION MECHANISM ----------------------------------
#   Finally, the time has come for PyGNA to do some work for us. We will tell
#   PyGNA to test each of the extraction mechanisms it knows about (both the
#   preloaded mechanisms as well as the user defined mechanisms) and tell us
#   which best describes the data. Please note that this computation may take
#   several minutes or even hours to execute, depending on the size of the
#   data, the number of extraction mechanisms to be tested, and the
#   complexity of the extraction mechanisms.

myGNA.findExtractionMechanism()

#   --- SAMPLE OUTPUT -------------------------------------------------------
#   Upon running the above code you should get the something simillar to the
#   follwing output, assuming that you have not yet modified the code of this
#   tutorial file.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#Reading file... Done
#Analyzing dynamics... Done.
#Identifying Extraction Mechanism...
#
#	Analyzing betweenness...
#	WARNING: An error occured while evaluating this model:
#	   Model returned a zero likelihood for all the nodes.
#	---------------------
#	Analyzing closeness...
#	-360.617421422
#	---------------------
#	Analyzing clusteringCoefficient...
#	WARNING: An error occured while evaluating this model:
#	   Model returned a zero likelihood for all the nodes.
#	---------------------
#	Analyzing greaterNeighborhoodState...
#	WARNING: An error occured while evaluating this model:
#	   'state and neighborStates can not be defined for this graph, as it contains no state information.'
#	---------------------
#	Analyzing netIn...
#	WARNING: An error occured while evaluating this model:
#	   'inDegree is not defined for undirected graphs.'
#	---------------------
#	Analyzing nodeDegree...
#	-348.723058743
#	---------------------
#Done.
#
#The winning model was: nodeDegree with a likelihood exponent of: -348.723058743
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
#   Notice the warnings. If any error should occur during the evaluation of
#   an extraction mechanism, the error is reported as a warning and PyGNA
#   skips it, moving on to the next extraction mechanism.
#   In this case, the built in extraction mechanism "degree" is the one that
#   best explains the data.
