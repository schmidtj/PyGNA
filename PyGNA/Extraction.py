"""
GNA Extraction class.

"""
__author__ = """\n""".join(['Jeffrey Schmidt (jschmid1@binghamton.edu',
                            'Benjamin Bush (benjaminjamesbush@gmail.com)',
                            'Hiroki Sayama (sayama@binghamton.edu)'])

__all__ = ['setNetworkFrames','setModels','performExtraction',
           'getModelValueForNetworkChange','getModelValueForNode',
           'likelihoodPercentage','analyzeProperty','generateExtractionSubgraphs',
           'getExtractionSubgraphFromDelta','identifyExtractionDynamics']

#    Copyright (C) 2012 by
#    Jeffrey Schmidt <jschmid1@binghamton.edu>
#    Benjamin Bush <benjaminjamesbush@gmail.com>
#    Hiroki Sayama <sayama@binghamton.edu>
#    All rights reserved.
#    BSD license.

import NetworkFrames
import Models
import networkx as nx
from scipy import stats
import random
import csv
import math
import Utility

class propertyAvg:
    fullAvg = 'fullAvg'
    compressedAvg = 'compressedAvg'
    
class Extraction(object):
    def __init__(self):
        self.network = NetworkFrames.NetworkFrames()
        self.models = []
        self.results = {}
        for nodeProperty in NetworkFrames.processState.allStates:
            if not self.results.has_key(nodeProperty):
                self.results[nodeProperty] = {}
                self.results[nodeProperty][propertyAvg.fullAvg] = []
                self.results[nodeProperty][propertyAvg.compressedAvg] = []
        self.winningModel = None
        self.winningModelName = ""
        self.extractionNodeCountList = []
        self.metaNumDomList = []
        self.utility = Utility.utility()
        
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
        
    def setModels(self, models):
        """Mutator that sets the models to be used for Extraction

        Parameters
        ----------
        models : Dictionary of models
           Dictionary object , {modelName:modelFunction}, used for Extraction

        Returns
        -------
        void
        """
        self.models = models
    
    def identifyExtractionDynamics(self):
        """Identifies the underlying rules behind extraction subgraph selection  

        Parameters
        ----------
        None

        Returns
        -------
        void
        """
        print "Identifying Extraction Mechanism...\n"
        
        metaCumulativeLikelihoodList = []
        self.winningModelName  = 'None'
        highestValue = float('-inf')
        for model in self.models:
            try:
                print "\tAnalyzing " + model.getModelName() + "...\n",
                networkIndex = 1
                cummulativeLikelihood = 0.
                cummulativeLikelihoodList = []
                while networkIndex < len(self.network.getInputNetworks()):
                    Gprime = self.network._getCompressedNetworkAt(networkIndex)
                    Gprime = self.getExtractionSubgraphFromDelta(Gprime)
                    if len(Gprime.nodes()) > 0:
                        cummulativeLikelihood += model.getLikelihoodValue(self.network, networkIndex)
                        cummulativeLikelihoodList.append(cummulativeLikelihood)
                        if math.isnan(cummulativeLikelihood): 
                            raise ZeroDivisionError, "Model returned a zero likelihood for all the nodes."                          
                    networkIndex += 1
                
                print "\t" + str(cummulativeLikelihood)
                print "\t" + "---------------------"
                
                # Peek at likelihood values and numerator/denominator values.
                #if __debug__:
                #    metaCumulativeLikelihoodList.append(cummulativeLikelihoodList)
                #    model._printDebugData()
                    
                if cummulativeLikelihood > highestValue:
                    highestValue = cummulativeLikelihood
                    self.winningModelName = model.getModelName()
                    self.winningModel = model
            except Exception,e:
                print "\tWARNING: An error occured while evaluating this model:"
                print '\t  ', str(e)
                print "\t" + "---------------------"
                
        # Save debugging data to file for analysis
        #if __debug__:
        #    f = open('likelihood.csv','wb')
        #    writer = csv.writer(f)        
        #    writer.writerows(metaCumulativeLikelihoodList)   
        #    f.close()
            
        print "Done.\n"
        print "The winning model was: " + self.winningModelName + " with a likelihood exponent of: " + str(highestValue)
        
    def performExtraction(self, graph):
        """Performs the Extraction phase of the GNA framework.  

        Parameters
        ----------
        graph - NetworkX graph object
         - The graph that the extraction subgraph should be selected from.

        Returns
        -------
        extractionSubgraph: NetworkX graph object
        - The extraction subgraph generated from the graph that was passed in.
        """     
        extractedSubgraph = None
        # Determine how many nodes to add to this extraction subgraph
        extractionCandidates = []
        while len(extractionCandidates) < 1:
            subgraphCandidate = self.network._getExtractionSubgraphAt(random.randint(0,len(self.network.extractionSubgraphs)-1))
            if len(subgraphCandidate.nodes()) == 0:
                extractedSubgraph = subgraphCandidate
                return extractedSubgraph
            extractionCandidates = self.utility.findSubgraphInstances(graph, subgraphCandidate)
        
        extractionCandidateList = []
        for candidate in extractionCandidates:
            extractionCandidateList.append(graph.subgraph(candidate.values()))
            
        # Get winning model values and find total
        total = 0.
        choiceList = []
        correspondingNodeList = []
        networkVal = self.winningModel.getModel()(graph, graph, self.network.getStateName())
        for subgraph in extractionCandidateList:
            value = self.winningModel.getModel()(graph, subgraph, self.network.getStateName())/networkVal
            choiceList.append(value)
            total += value
            
        # Create a roulette wheel
        index = 0
        accumulate = 0.
        while index < len(choiceList):
            accumulate += choiceList[index]/total
            choiceList[index] = accumulate
            index += 1
            
        # Choose extracted subgraph  
        randVal = random.random()
        for index in range(0,len(choiceList)):
            if randVal <= choiceList[index]:
                extractedSubgraph = extractionCandidateList[index]
                break
                        
        return extractedSubgraph
            
    def generateExtractionSubgraphs(self):
        """ Generates the extraction subgraphs from the compressed data.  
          
        Parameters
        ----------
        None
        
        Returns
        ----------
        None
          
        """
        # Check to see if compression step has been perfomed
        if len(self.network.compressedFrames) > 0:
            # Skip first graph, since it's the initial configuration
            index = 1
            while index < len(self.network.compressedFrames):
                deltaGraph = self.network._getCompressedNetworkAt(index)
                extractionSubgraph = self.getExtractionSubgraphFromDelta(deltaGraph)
                self.network._addExtractionSubgraph(extractionSubgraph)
                index += 1
                
    def getExtractionSubgraphFromDelta(self, deltaGraph):
        """ Returns an extraction subgraph based on the "delta Graph" that's passed in.  This funciton
        reconstructs the extraction subgraph from the graph that represents the change that took place between
        one input network frame to another (t -> t+1).
          
        Parameters
        ----------
        deltaGraph - Networkx Graph() object
         - Graph that contains the changes from one time step to another
        
        Returns
        ----------
        extractionSubgraph - Network Graph() object
          - Graph that represents the subgraph before the rewriting even took place.
        """
        extractionSubgraph = NetworkFrames.nx.DiGraph() if deltaGraph.is_directed() else NetworkFrames.nx.Graph()
        deltaCopy = deltaGraph.copy()
        
        for node in deltaCopy.nodes():
            state = deltaCopy.node[node].pop(NetworkFrames.compressState.tag)
            # We are only interested in nodes that were deleted or none
            if state == NetworkFrames.compressState.deleted or \
               state == NetworkFrames.compressState.none:
                extractionSubgraph.add_node(node)
                extractionSubgraph.node[node] = deltaCopy.node[node]
            elif state == NetworkFrames.compressState.stateChange:
                extractionSubgraph.add_node(node)
                stateName = deltaCopy.node[node].pop(NetworkFrames.compressState.stateChangedName)
                previousStateValue = deltaCopy.node[node].pop(NetworkFrames.compressState.stateChangedFrom)
                nextStateValue = deltaCopy.node[node].pop(NetworkFrames.compressState.stateChangedTo)
                extractionSubgraph.node[node] = deltaCopy.node[node]
                extractionSubgraph.node[node][stateName] = previousStateValue
            

        # Look for any deleted edges that we need to add.
        for edge in deltaCopy.edges():
            start = edge[0]
            end = edge[1]
            change = deltaCopy.edge[start][end].pop(NetworkFrames.compressState.tag)
            if change == NetworkFrames.compressState.deleted or \
               change == NetworkFrames.compressState.none:
                if start not in deltaCopy.node or end not in deltaCopy.node:
                    print "Node not found prior to adding edge to extraction subgraph"
                extractionSubgraph.add_edge(start,end)
                
        return extractionSubgraph
    
    def binaryStateOpposite(self, x):
        if x == 1:
            return 0
        return 1
