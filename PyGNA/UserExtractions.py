"""
UserExtraction base class.  Used for generating user defined
models to input into PyGNA.

"""
__author__ = """\n""".join(['Jeffrey Schmidt (jschmid1@binghamton.edu',
                            'Benjamin Bush (benjaminjamesbush@gmail.com)',
                            'Hiroki Sayama (sayama@binghamton.edu)'])

__all__ = ['getModels','buildModels']


#    Copyright (C) 2012 by
#    Jeffrey Schmidt <jschmid1@binghamton.edu>
#    Benjamin Bush <benjaminjamesbush@gmail.com>
#    Hiroki Sayama <sayama@binghamton.edu>
#    All rights reserved.
#    BSD license.

import inspect
import string
import re
import itertools
import copy
import Model
import gna

class UserExtractions(object):

    def __init__(self):
        self.models = []

    def getModels(self):  
        return self.models
    
    def buildModels(self):
        """Only to be used in an intanciated object of a user class that
        inherits from UserExtractions. Reads the code written by the user,
        which is written in a domain specific language, and interprets it
        within the context of several predefined prmitive functions to create
        a list of Models that can be imported into PyGNA via
        gna.addUserExtractions

        Parameters
        ----------
        void

        Returns
        -------
        void
        """  
        for fName in [fName for fName in dir(self) if fName not in dir(UserExtractions())]:
            sourceLines = inspect.getsourcelines(eval('self.' + fName))[0]
            indent = re.search('\w', sourceLines[0]).start()
            sourceLines = [line[indent:] for line in sourceLines] #indentation removed
            s = string.join(sourceLines) #the source that goes with the function with the name fName
            x = ""
            x += "def f314159(G, nodeID, stateName):\n"#1   #this is the costructed function
            x += "    errorString = False\n"
            x += '    sourceText = """'+ s +'"""\n'
            x += "    import networkx as nx\n" #2
            x += "    degree = G.degree(nodeID)\n"#3
            x += "    useState = True\n"#4
            x += "    for n in G.nodes():\n"#5
            x += "        if stateName not in G.node[n]:\n"#6
            x += "            useState = False\n"#7
            x += "            if stateName != None:\n"
            x += "                raise KeyError('At some point, node ' + str(n) + ' did not contain information about ' + str(stateName))\n"
            x += "    if useState:\n"#8
            x += "        state = G.node[nodeID][stateName]\n"#9
            x += "        neighborStates = [G.node[neighborID][stateName] for neighborID in G.neighbors(nodeID)]\n"#12
            x += "    elif 'state' in sourceText or 'neighborStates' in sourceText:\n"
            x += "        raise KeyError('state and neighborStates can not be defined for this graph, as it contains no state information.')\n"
            x += "    if 'predecessors' in dir(G) and  'successors' in dir(G):\n"#13
            x += "        inDegree = G.in_degree(nodeID)\n"#14
            x += "        outDegree = G.out_degree(nodeID)\n"#15
            x += "        if 'clustering' in sourceText:\n"
            x += "            raise KeyError('Clustering is not defined for directed graphs.')\n"
            x += "        if useState:\n"#16
            x += "            inNeighborStates = [G.node[neighborID][stateName] for neighborID in G.predecessors(nodeID)]\n"#17
            x += "            outNeighborStates = [G.node[neighborID][stateName] for neighborID in G.successors(nodeID)]\n"#18
            x += "    else:\n"#19
            x += "        clustering = nx.clustering(G,nodeID)\n"#20
            x += "        if 'inDegree' in sourceText:\n"
            x += "            raise KeyError('inDegree is not defined for undirected graphs.')\n"
            x += "        if 'outDegree' in sourceText:\n"
            x += "            raise KeyError('outDegree is not defined for undirected graphs.')\n"
            x += "        if 'inNeighborStates' in sourceText:\n"
            x += "            raise KeyError('inNeighborSates is not defined for undirected graphs.')\n"
            x += "        if 'outNeighborStates' in sourceText:\n"
            x += "            raise KeyError('outNeighborSates is not defined for undirected graphs.')\n"
            x += "    betweennessCentrality = nx.betweenness_centrality(G)[nodeID]\n"#21
            x += "    bCentrality = betweennessCentrality\n"#22
            x += "    closenessCentrality = nx.closeness_centrality(G)[nodeID]\n"#23
            x += "    cCentrality = closenessCentrality\n"#The environment to do what the user wanted is now set up #24
            x += "    assert nodeID in G.nodes()\n"#25
            x += "    "+s+"\n"#

            x += "    userFunction = "+fName+"\n"#27
            x += "    return userFunction()\n"#28
            exec(x) in locals(), globals()
            self.models.append(Model.Model(f314159,fName))
        
    
