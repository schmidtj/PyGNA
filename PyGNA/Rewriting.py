"""
GNA Rewriting class.

"""
__author__ = """\n""".join(['Jeffrey Schmidt (jschmid1@binghamton.edu',
                            'Benjamin Bush (benjaminjamesbush@gmail.com)',
                            'Hiroki Sayama (sayama@binghamton.edu)'])

__all__ = ['setNetworkFrames','initializeRewritingData','performRewriting',
           'makeNodeLabelsDisjoint']

#    Copyright (C) 2012 by
#    Jeffrey Schmidt <jschmid1@binghamton.edu>
#    Benjamin Bush <benjaminjamesbush@gmail.com>
#    Hiroki Sayama <sayama@binghamton.edu>
#    All rights reserved.
#    BSD license.

import NetworkFrames
import Extraction
import MotifExtraction
import itertools
import random
import copy
import Display
import Utility

class Rewriting(object):
    def __init__(self):
        self.network = NetworkFrames.NetworkFrames()
        self.subgraphPair = []
        self.leftSubgraphs = []
        self.rightSubgraphs = []
        self.uniqueExtractionSubgraphs = {}
        self.firstRun = True
        self.dataDisplay = Display.display(False)
        self.utility = Utility.utility()
        
    def getDisplayData(self):
        return self.dataDisplay
    
    def resetDataDisplay(self):
        self.dataDisplay.clearExperimentalValues()
        
    def setNetworkFrames(self, networkFrames):
        """Mutator that sets the current network frame object to the one passed in.

        Parameters
        ----------
        networkFrames : NetworkFrames object
           Object representing the dynamic network to be processed.

        Returns
        -------
        void
        """
        self.network = networkFrames
        
    def initializeRewritingData(self):
        """Initialization function that populates internal data structures maintaining
        unique subgraphs and unique subgraph rewritings.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        
        print "Initializing Rewriting Data..."
        
        # Clear the extraction subgraph list
        self.uniqueExtractionSubgraphs = {}
        
        # Find all the unique extraction subgraphs from the adaptive network.
        index = 1
        self.uniqueExtractionSubgraphs[self.network._getExtractionSubgraphAt(0)] = [index]
        self.dataDisplay.addInputValue(int(self.network._getExtractionSubgraphAt(0).name))
        while index < len(self.network.getExtractionSubgraphs()):
            isoFound = False
            compareGraph = self.network._getExtractionSubgraphAt(index)
            for graph in self.uniqueExtractionSubgraphs.iterkeys():
                if self.utility.isIsomorphic(graph,compareGraph):
                    isoFound = True
                    self.uniqueExtractionSubgraphs[graph].append(index+1)
                    self.dataDisplay.addInputValue(int(graph.name))
                    break
            if not isoFound:
                self.uniqueExtractionSubgraphs[compareGraph] = [index+1]
                self.dataDisplay.addInputValue(int(compareGraph.name))
            index += 1
        
        print "Done.\n"
    
    def performRewriting(self, extractionSubgraph, rewritingSubgraph=None):
        ''' Performs rewriting on the extraction subgraph that is passed into the function.  The rewriting analysis needs to occur first in order to 
        determine what the appropriate rewriting rule needs to be applied.

        Parameters
        ----------
        extractionSubgraph : Networkx Graph()
         - The extraction subgraph that will undergo change.

        Returns
        -------
         rewritingEvent : Networkx Graph() containing the changes that took place to the extraction subgraph that was passed in
        '''     
        rewritingEvent = None
        if self.firstRun and __debug__:
            graphList = []
            for uniqueGraph in self.uniqueExtractionSubgraphs.iterkeys():
                graphList.append(uniqueGraph)
            self.network.writeSpecificGraphs("UniqueExtractedSubgraphs.graphML", graphList)   
            self.firstRun = False
            
        for uniqueGraph in self.uniqueExtractionSubgraphs.iterkeys():
            if self.utility.isIsomorphic(extractionSubgraph,uniqueGraph):
                rewritingIndex = random.choice(self.uniqueExtractionSubgraphs[uniqueGraph])
                delta = self.network._getCompressedNetworkAt(rewritingIndex)
                delta = self.makeNodeLabelsDisjoint(extractionSubgraph, delta)
                associatedExtraction = Extraction.Extraction().getExtractionSubgraphFromDelta(delta)
                #mapping = self.isIsomorphic(associatedExtraction, extractionSubgraph,True)
                mapping = self.utility.findSubgraphInstances(extractionSubgraph, associatedExtraction)
                #if len(mapping) < 1:
                   #print "Error in mapping rewriting during simulation!"
                rewritingEvent = NetworkFrames.nx.relabel_nodes(delta,mapping[0],copy=True) if len(mapping) > 0 else delta
                #rewritingEvent = self._generateRewritingEventFromExtraction(extractionSubgraph, delta, mapping)
                
                assert(self.network.getNumEdgesAdded(rewritingEvent) == self.network.getNumEdgesAdded(delta))
                self.dataDisplay.addExperimentalValue(int(uniqueGraph.name))
                break
        

        return rewritingEvent
    
    '''
    def performMotifRewriting(self, extractionSubgraph, rewritingSubgraph):
        rewritingEvent = None
        if self.firstRun and __debug__:
            graphList = []
            for uniqueGraph in self.uniqueExtractionSubgraphs.iterkeys():
                graphList.append(uniqueGraph)
            self.network.writeSpecificGraphs("UniqueExtractedSubgraphs.graphML", graphList)   
            self.firstRun = False
        
        
        delta = self.makeNodeLabelsDisjoint(extractionSubgraph, rewritingSubgraph)
        associatedExtraction = Extraction.Extraction().getExtractionSubgraphFromDelta(delta)
        #mapping = self.isIsomorphic(associatedExtraction, extractionSubgraph,True)
        mapping = self.utility.findSubgraphInstances(extractionSubgraph, associatedExtraction)
        #if len(mapping) < 1:
           #print "Error in mapping rewriting during simulation!"
        rewritingEvent = NetworkFrames.nx.relabel_nodes(delta,mapping[0],copy=True) if len(mapping) > 0 else delta
        #rewritingEvent = self._generateRewritingEventFromExtraction(extractionSubgraph, delta, mapping)
        
        assert(self.network.getNumEdgesAdded(rewritingEvent) == self.network.getNumEdgesAdded(delta))
            
        return rewritingEvent  '''       
             
    def makeNodeLabelsDisjoint(self, keepLabels, makeUnique):
        ''' Makes sure that second graph passed in has no overlapping node id's with the
        first graph passed in.

        Parameters
        ----------
        keepLabels : Networkx Graph()
         - The graph that contains the node id's we want to avoid duplicating.
         
        makeUnique : Networkx Graph()
         - The graph that we want to alter node id's to make them unique from keepLabels graph().

        Returns
        -------
         Networkx Graph() with unique node id's with respect to keepLabels networkx graph().
        '''
        
        index = 0
        while index < len(makeUnique.nodes()):
            if makeUnique.nodes()[index] in keepLabels.nodes():
                currentNode = makeUnique.nodes()[index]
                changeMap = {currentNode:max(makeUnique.nodes())+1}
                makeUnique = NetworkFrames.nx.relabel_nodes(makeUnique,changeMap,copy=True)
                index = 0
            else:
                index += 1
        
        return makeUnique
        
    def _generateRewritingEventFromExtraction(self, extraction, rewriting, mapping):
        """ Generates the rewriting event given the extraction, rewriting rules, and mapping
        """
        mapDict = {}
        index = 0
        while index < len(mapping):
            mapDict[mapping[index]] = extraction.nodes()[index]
            index+=1
        newDelta = NetworkFrames.nx.relabel_nodes(rewriting,mapDict,copy=True)
        return newDelta
    
    
    