"""
GNA  Motif Extraction class.

"""
__author__ = """\n""".join(['Jeffrey Schmidt (jschmid1@binghamton.edu',
                            'Hiroki Sayama (sayama@binghamton.edu)'])

__all__ = []

#    Copyright (C) 2014 by
#    Jeffrey Schmidt <jschmid1@binghamton.edu>
#    Hiroki Sayama <sayama@binghamton.edu>
#    All rights reserved.
#    BSD license.

import NetworkFrames
import networkx as nx
import Extraction
import Rewriting
import scipy.misc as scipymisc
import random
import itertools
import Utility
import copy
import Display
import math
from GTrie import *

class RuleCategory:
    """ 'Enum' Class used to indicate network statistics for individual nodes.
    """
    nodes = 'nodes'
    edges = 'edges'
    allCategories = [nodes,edges]

class MotifExtraction(object):
    
    def __init__(self):
        self.network = NetworkFrames.NetworkFrames()
        self.util = Utility.utility()
        self.prev_extraction = Extraction.Extraction()
        self.rewriting = Rewriting.Rewriting()
        self.sample_num = 0
        self.sample_motifs = []
        self.extractionMap = []
        self.extractionPool = {}
        self.gtrieExtractionPool = {}
        self.proportionalSelection = []
        self.display = Display.display()
        self.gtrie = GTrie.GTrie()
        self.gtrie.createGTrieWithFour()
        self.simulationgtrie = GTrie.GTrie()
        self.usedRewritingRules = {}
        self.avg_changes = 0.
    
    def getAvgChanges(self):
        return self.avg_changes
    
    def calculateAvgChanges(self):
        changes_each_rule = []
        for element in self.extractionMap: 
            for graph in element[1]:
                changes = 0
                for node in graph.node:
                    nodeTag = graph.node[node][NetworkFrames.compressState.tag]
                    if nodeTag != NetworkFrames.compressState.none:
                        changes += 1
                        
                for edge in graph.edges_iter():
                    changes += 1
                    
                changes_each_rule.append(changes)
            
        self.avg_changes = sum(changes_each_rule) / float(len(changes_each_rule))
                
    
    def setSampleNum(self, sample_num):
        self.sample_num = sample_num
        
    def setNetworkFrames(self, network):
        self.network = network
        
    def clearUsedRewritingRules(self):
        self.usedRewritingRules = {}
        #self.usedRewritingRules[RuleCategory.nodes] = []
        #self.usedRewritingRules[RuleCategory.edges] = []
        self.usedRewritingRules[NetworkFrames.compressState.added] = {}
        self.usedRewritingRules[NetworkFrames.compressState.added][RuleCategory.nodes] = []
        self.usedRewritingRules[NetworkFrames.compressState.added][RuleCategory.edges] = []        
        self.usedRewritingRules[NetworkFrames.compressState.deleted] = {}
        self.usedRewritingRules[NetworkFrames.compressState.deleted][RuleCategory.nodes] = []
        self.usedRewritingRules[NetworkFrames.compressState.deleted][RuleCategory.edges] = []
        self.usedRewritingRules[NetworkFrames.compressState.stateChange] = {}
        self.usedRewritingRules[NetworkFrames.compressState.stateChange][RuleCategory.nodes] = []
        self.usedRewritingRules[NetworkFrames.compressState.stateChange][RuleCategory.edges] = []
        
    def addUsedRewritingRules(self, rewritingRule):
        for node in rewritingRule.nodes_iter():
            compressedState = rewritingRule.node[node][NetworkFrames.compressState.tag]
            if compressedState != NetworkFrames.compressState.none:
                self.usedRewritingRules[compressedState][RuleCategory.nodes].append(node)
        
        for edge in rewritingRule.edges_iter():
            first = edge[0]
            second = edge[1]
            compressedState = rewritingRule.edge[first][second][NetworkFrames.compressState.tag]
            if compressedState != NetworkFrames.compressState.none:
                self.usedRewritingRules[compressedState][RuleCategory.edges].append(edge)
                
    def isRewritingRuleInUsed(self, rewritingRule):
        found = False
        for node in rewritingRule.nodes_iter():
            compressedState = rewritingRule.node[node][NetworkFrames.compressState.tag]
            if compressedState != NetworkFrames.compressState.none:
                if node in self.usedRewritingRules[compressedState][RuleCategory.nodes]:
                    found = True
                    break
            
        if not found:    
            for edge in rewritingRule.edges_iter():
                first = edge[0]
                second = edge[1]
                compressedState = rewritingRule.edge[first][second][NetworkFrames.compressState.tag]
                if compressedState != NetworkFrames.compressState.none:
                    if rewritingRule.is_directed():
                        if first in self.usedRewritingRules[NetworkFrames.compressState.deleted][RuleCategory.nodes] or \
                           second in self.usedRewritingRules[NetworkFrames.compressState.deleted][RuleCategory.nodes] or \
                           edge in self.usedRewritingRules[NetworkFrames.compressState.added][RuleCategory.edges] or \
                           edge in self.usedRewritingRules[NetworkFrames.compressState.deleted][RuleCategory.edges] or \
                           edge in self.usedRewritingRules[NetworkFrames.compressState.stateChange][RuleCategory.edges]:
                            found = True
                            break
                    else:
                        if first in self.usedRewritingRules[NetworkFrames.compressState.deleted][RuleCategory.nodes] or \
                           second in self.usedRewritingRules[NetworkFrames.compressState.deleted][RuleCategory.nodes] or \
                           (first,second) in self.usedRewritingRules[NetworkFrames.compressState.added][RuleCategory.edges] or \
                           (first,second) in self.usedRewritingRules[NetworkFrames.compressState.deleted][RuleCategory.edges] or \
                           (first,second) in self.usedRewritingRules[NetworkFrames.compressState.stateChange][RuleCategory.edges] or \
                           (second,first) in self.usedRewritingRules[NetworkFrames.compressState.added][RuleCategory.edges] or \
                           (second,first) in self.usedRewritingRules[NetworkFrames.compressState.deleted][RuleCategory.edges] or \
                           (second,first) in self.usedRewritingRules[NetworkFrames.compressState.stateChange][RuleCategory.edges]:
                            found = True
                            break
        
        return found
    
    def displayUsedRewritingRuleGraph(self, iteration):

        usedTotal = 0.
        usedNodeData = {tag:0 for tag in NetworkFrames.compressState.allStates}
        usedEdgeData = {tag:0 for tag in NetworkFrames.compressState.allStates}
         
        for key in self.usedRewritingRules:
            numNodeChanges = len(self.usedRewritingRules[key][RuleCategory.nodes])
            numEdgeChanges = len(self.usedRewritingRules[key][RuleCategory.edges])
            
            usedNodeData[key] += numNodeChanges
            usedEdgeData[key] += numEdgeChanges
            usedTotal += numNodeChanges + numEdgeChanges
        
        samTotal = 0.
        samNodeData = {tag:0 for tag in NetworkFrames.compressState.allStates}
        samEdgeData = {tag:0 for tag in NetworkFrames.compressState.allStates}            
        for element in self.extractionMap:
            for graph in element[1]:
                for node in graph.node:
                    nodeTag = graph.node[node][NetworkFrames.compressState.tag]
                    if nodeTag != NetworkFrames.compressState.none:
                        samNodeData[nodeTag] += 1
                        samTotal += 1
                    
                for edge in graph.edges_iter():
                    start = edge[0]
                    end = edge[1]
                    edgeTag = graph.edge[start][end][NetworkFrames.compressState.tag]
                    samEdgeData[edgeTag] += 1
                    samTotal += 1  
                        
        labels = ['Noop','Node Added', 'Node Deleted', 'Edge Added', 'Edge Deleted', 'Edge Statechange']
        usedData = [(usedNodeData[NetworkFrames.compressState.none] + usedEdgeData[NetworkFrames.compressState.none])/usedTotal,
                     usedNodeData[NetworkFrames.compressState.added]/usedTotal,
                     usedNodeData[NetworkFrames.compressState.deleted]/usedTotal,
                     usedEdgeData[NetworkFrames.compressState.added]/usedTotal,
                     usedEdgeData[NetworkFrames.compressState.deleted]/usedTotal,
                     usedEdgeData[NetworkFrames.compressState.stateChange]/usedTotal]    
        samData = [(samNodeData[NetworkFrames.compressState.none]+samEdgeData[NetworkFrames.compressState.none])/samTotal,
                    samNodeData[NetworkFrames.compressState.added]/samTotal,
                    samNodeData[NetworkFrames.compressState.deleted]/samTotal,
                    samEdgeData[NetworkFrames.compressState.added]/samTotal,
                    samEdgeData[NetworkFrames.compressState.deleted]/samTotal,
                    samEdgeData[NetworkFrames.compressState.stateChange]/samTotal]
        
        sim_title = "Simulation_Changes_" + str(iteration)
        sam_title = "Sampled_Changes_" + str(iteration)
        self.display.pieChart(sim_title, usedData, labels)
        self.display.pieChart(sam_title, samData, labels)
    
    def analyzeGTrieExtractionPool(self):
        nodes = {}
        edges = {}
        for key in self.gtrieExtractionPool.iterkeys():
            for graphs in self.gtrieExtractionPool[key]:
                for node in graphs.nodes_iter():
                    if node in nodes:
                        nodes[node] += 1
                    else:
                        nodes[node] = 1
                        
                for edge in graphs.edges_iter():
                    first = edge[0]
                    second = edge[1]
                    pair = (first, second) if first < second else (second, first)
                    if pair in edges:
                        edges[pair] += 1
                    else:
                        edges[pair] = 1
                        
        node_overlap = len(nodes)/float(sum([value for value in nodes.itervalues()]))
        edge_overlap = len(edges)/float(sum([value for value in edges.itervalues()]))
        
        print "Num Unique Nodes: " + str(len(nodes)) + " , Percent Overlap: " + str(node_overlap)
        print "Num Unique Edges: " + str(len(edges)) + " , Percent Overlap: " + str(edge_overlap)
        
    def resetRewritingRuleExclusionList(self):
        for extraction in self.extractionMap:
            extraction[2] = [x for x in range(len(extraction[1]))]
            
    def sampleCompressedNetworks(self):
        self.gtrie.setMaxMatches(self.sample_num)
        for index in range(1,len(self.network.compressedFrames)):
            network = self.network._getCompressedNetworkAt(index)
            self.gtrie.GTrieMatch(network, [1,1,1,math.sqrt(0.0001), math.sqrt(0.0001)])
            matches = self.gtrie.getMatches()
            self.sample_motifs.append((len(matches), matches))
            print ".",
            
    def sampleCompressedNetworkAt(self, networkIndex):
        self.gtrie.setMaxMatches(self.sample_num)
        network = self.network._getCompressedNetworkAt(networkIndex)
        num_changes = self.network.getNumberOfChanges(networkIndex)
        #value = .911 * math.exp(-0.000797 * num_changes)
        value = 0.01 if num_changes > 5000 else 0.1
        value = 0.001 if num_changes > 7000 else value
        value - 0.001 if num_changes > 9000 else value
        self.gtrie.GTrieMatch(network, [1,1,1,math.sqrt(value), math.sqrt(value)])
        matches = self.gtrie.getMatches()
        return (len(matches), matches)
    
    def sampleNetworkAt(self, sampleNumber, networkIndex, connected_only=False):
        #Sample from the chosen network time step
        print "Sampling Network...",
        self.setSampleNum(sampleNumber)
        self.extractionMap = []
        sampleTrie = GTrie.GTrie()
        sample = self.sampleCompressedNetworkAt(networkIndex)
        sampleCount = 0
        while sampleCount < sampleNumber:
                    
            if len(sample[1]) > 0:
                sampleMotif = random.choice(sample[1])
            else:
                print "Error: Empty Sample.  Aborting simulation"
                raise IndexError
            
            #find the left hand side of the rewriting rule
            lefthandside = self.prev_extraction.getExtractionSubgraphFromDelta(sampleMotif)
            components = nx.connected_components(lefthandside)
            if connected_only == True and len(lefthandside) > 0 and not nx.is_connected(lefthandside):
                continue
            component_len = [1 for x in components if len(x) > 1]           
            if len(lefthandside.nodes()) == 0 or (len(components) > 1 and sum(component_len) > 1):
                continue
                    
            isomorphfound = False
            sampleTrie.GTrieMatch(lefthandside, [1,1,1,1,1], labels=True, states=True)
            matches = sampleTrie.getMatches(labels=True)
            for key in matches:
                if self.util.isIsomorphicFast(self.extractionMap[key][0], lefthandside):
                    self.extractionMap[key][1].append(sampleMotif)
                    isomorphfound = True
                    sampleCount += 1
                    break
                
            ############
            if not isomorphfound:
                for element in self.extractionMap:
                    if self.util.isIsomorphicFast(element[0], lefthandside):
                        print "Error found in GTrie isomorphism."
            ############
            
            if not isomorphfound:              
                addExtraction = [lefthandside,[sampleMotif]]
                sampleTrie.GTrieInsert(lefthandside, label=len(self.extractionMap), states=True)
                self.extractionMap.append(addExtraction)
                sampleCount += 1
        
        #Add exclusion list to extraction map
        for extraction in self.extractionMap:
            extraction.append([x for x in range(len(extraction[1]))])
            
        self.generateProportionalSelectionData()
        self.calculateAvgChanges()
        self.generateInputComparisonDataAt(networkIndex)
        print "Done."        
               
    def sampleNetwork(self, motifSize, sampleNumber):
        """Samples "motifs" of size motifSize from the input network

        Parameters
        ----------
        motifSize - int
         - The size of the motifs to be sampled
         
         sampleNumber - int
         - The number of samples to be chosen

        Returns
        -------
        None
        """  
        print "Sampling Network... ",
        self.setSampleNum(sampleNumber)
        self.sampleCompressedNetworks()
        #Roulette wheel selection
        sampleTrie = GTrie.GTrie()
        numNodeList = []
        numNodeList.append(float(scipymisc.comb(len(self.network.getInputNetworkAt(0, False).nodes()), motifSize)))
        for i in range(1, len(self.network.getInputNetworks())-2):
            numNodeList.append(numNodeList[i-1] + scipymisc.comb(len(self.network.getInputNetworkAt(i, False).nodes()) , motifSize) )
            
        selection = []
        for _ in range(sampleNumber):
            rand = random.random() * numNodeList[-1]
            for val in numNodeList:
                if rand <= val:
                    selection.append(numNodeList.index(val))
                    break
         
         #Sample from the chosen network time step
        sampleCount = 0
        while sampleCount < sampleNumber:
            sample = None
            max_val = sum([match[0] for match in self.sample_motifs])
            randVal = random.randint(0, max_val)
            
            #get the network to sample from
            current = 0
            for num, match in self.sample_motifs:
                current += num
                if current > randVal:
                    sample = match
                    break
                    
            if len(sample) > 0:
                sampleMotif = random.choice(sample)
            else:
                continue
            
            #find the left hand side of the rewriting rule
            lefthandside = self.prev_extraction.getExtractionSubgraphFromDelta(sampleMotif)
            components = nx.connected_components(lefthandside)
            component_len = [1 for x in components if len(x) > 1]           
            if len(lefthandside.nodes()) == 0 or (len(components) > 1 and sum(component_len) > 1):
                continue
            
            '''lefthandside = nx.Graph() if not nx.is_directed(inputnetwork) else nx.DiGraph()
            
            for nodes in sampleMotif.nodes_iter():
                if nodes in inputnetwork.node:
                    nodedata = inputnetwork.node[nodes]
                    lefthandside.add_node(nodes, nodedata)
                    
            for edge in sampleMotif.edges_iter():
                start = edge[0]
                end = edge[1]
                if start in inputnetwork.edge and end in inputnetwork.edge[start]:
                    edgedata = inputnetwork.edge[start][end]
                    lefthandside.add_edge(start, end, edgedata)'''
                    
            isomorphfound = False
            sampleTrie.GTrieMatch(lefthandside, [1,1,1,1,1], labels=True, states=True)
            matches = sampleTrie.getMatches(labels=True)
            for key in matches:
                if self.util.isIsomorphicFast(self.extractionMap[key][0], lefthandside):
                    self.extractionMap[key][1].append(sampleMotif)
                    isomorphfound = True
                    sampleCount += 1
                    break
                
            ############
            if not isomorphfound:
                for element in self.extractionMap:
                    if self.util.isIsomorphicFast(element[0], lefthandside):
                        print "Error found in GTrie isomorphism."
            ############
            
            if not isomorphfound:              
                addExtraction = [lefthandside,[sampleMotif]]
                sampleTrie.GTrieInsert(lefthandside, label=len(self.extractionMap), states=True)
                self.extractionMap.append(addExtraction)
                sampleCount += 1
        
        #Add exclusion list to extraction map
        for extraction in self.extractionMap:
            extraction.append([x for x in range(len(extraction[1]))])
            
        self.generateProportionalSelectionData()
        self.generateInputComparisonData()
        print "Done."
    
    def generateRandomSample(self,  motifSize, network):
        sampleMotif = nx.Graph() if nx.is_directed(network) else nx.DiGraph() 
        #choose random nodes for motif
        for _ in range(motifSize):
            randNode = random.choice(network.nodes())
            while randNode in sampleMotif.nodes():
                randNode = random.choice(network.nodes())
            node  = copy.deepcopy(network.node[randNode])
            sampleMotif.add_node(randNode, node)
        
        #add edges to the sample motif
        for outer in sampleMotif.nodes_iter():
            for inner in sampleMotif.nodes_iter():
                if outer != inner:
                    if outer in network.edge and inner in network.edge[outer]:
                        edge = copy.deepcopy(network.edge[outer][inner])
                        sampleMotif.add_edge(outer, inner, edge)        
        
        return sampleMotif
    
    def generateInputComparisonData(self):
        inputTotal = 0.
        inputNodeTotal = 0.
        inputNodeData = {tag:0 for tag in NetworkFrames.compressState.allStates}
        inputEdgeData = {tag:0 for tag in NetworkFrames.compressState.allStates}
        for index in range(1, len(self.network.compressedFrames)-1):
            frame = self.network._getCompressedNetworkAt(index)
            for node in frame.node:
                nodeTag = frame.node[node][NetworkFrames.compressState.tag]
                inputNodeData[nodeTag] += 1
                inputTotal += 1
                inputNodeTotal += 1
                
            for edge in frame.edges_iter():
                start = edge[0]
                end = edge[1]
                edgeTag = frame.edge[start][end][NetworkFrames.compressState.tag]
                inputEdgeData[edgeTag] += 1
                inputTotal += 1
        
        samTotal = 0.
        elem_wise_states = []
        samNodeData = {tag:0 for tag in NetworkFrames.compressState.allStates}
        samEdgeData = {tag:0 for tag in NetworkFrames.compressState.allStates}            
        for element in self.extractionMap:
            edge_data = {tag:0 for tag in NetworkFrames.compressState.allStates}   
            for graph in element[1]:
                for node in graph.node:
                    nodeTag = graph.node[node][NetworkFrames.compressState.tag]
                    samNodeData[nodeTag] += 1
                    samTotal += 1
                    
                for edge in graph.edges_iter():
                    start = edge[0]
                    end = edge[1]
                    edgeTag = graph.edge[start][end][NetworkFrames.compressState.tag]
                    samEdgeData[edgeTag] += 1
                    edge_data[edgeTag] += 1
                    samTotal += 1
            elem_wise_states.append(copy.deepcopy(edge_data))
        
                   
        labels = ['Noop','Node Added', 'Node Deleted', 'Edge Added', 'Edge Deleted', 'Edge Statechange']
        inputData = [(inputNodeData[NetworkFrames.compressState.none] + inputEdgeData[NetworkFrames.compressState.none])/inputTotal,
                     inputNodeData[NetworkFrames.compressState.added]/inputTotal,
                     inputNodeData[NetworkFrames.compressState.deleted]/inputTotal,
                     inputEdgeData[NetworkFrames.compressState.added]/inputTotal,
                     inputEdgeData[NetworkFrames.compressState.deleted]/inputTotal,
                     inputEdgeData[NetworkFrames.compressState.stateChange]/inputTotal]
        inputNodeData = [(inputNodeData[NetworkFrames.compressState.none] )/inputNodeTotal,
                     inputNodeData[NetworkFrames.compressState.added]/inputNodeTotal,
                     inputNodeData[NetworkFrames.compressState.deleted]/inputNodeTotal,
                     0.,
                     0.,
                     0.]
        samData = [(samNodeData[NetworkFrames.compressState.none]+samEdgeData[NetworkFrames.compressState.none])/samTotal,
                   samNodeData[NetworkFrames.compressState.added]/samTotal,
                   samNodeData[NetworkFrames.compressState.deleted]/samTotal,
                   samEdgeData[NetworkFrames.compressState.added]/samTotal,
                   samEdgeData[NetworkFrames.compressState.deleted]/samTotal,
                   samEdgeData[NetworkFrames.compressState.stateChange]/samTotal]
        self.display.pieChart("Input Network Changes", inputData, labels)
        self.display.pieChart("Input Network Node Changes", inputNodeData, labels)
        self.display.pieChart("Sampled Network Changes", samData, labels)

    def generateInputComparisonDataAt(self, index):
        inputTotal = 0.
        inputNodeTotal = 0.
        inputNodeData = {tag:0 for tag in NetworkFrames.compressState.allStates}
        inputEdgeData = {tag:0 for tag in NetworkFrames.compressState.allStates}
        frame = self.network._getCompressedNetworkAt(index)
        for node in frame.node:
            nodeTag = frame.node[node][NetworkFrames.compressState.tag]
            if nodeTag != NetworkFrames.compressState.none:
                inputNodeData[nodeTag] += 1
                inputTotal += 1
                inputNodeTotal += 1
            
        for edge in frame.edges_iter():
            start = edge[0]
            end = edge[1]
            edgeTag = frame.edge[start][end][NetworkFrames.compressState.tag]
            if edgeTag != NetworkFrames.compressState.none:
                inputEdgeData[edgeTag] += 1
                inputTotal += 1
        
        samTotal = 0.
        elem_wise_states = []
        samNodeData = {tag:0 for tag in NetworkFrames.compressState.allStates}
        samEdgeData = {tag:0 for tag in NetworkFrames.compressState.allStates}            
        for element in self.extractionMap:
            edge_data = {tag:0 for tag in NetworkFrames.compressState.allStates}   
            for graph in element[1]:
                for node in graph.node:
                    nodeTag = graph.node[node][NetworkFrames.compressState.tag]
                    if nodeTag != NetworkFrames.compressState.none:
                        samNodeData[nodeTag] += 1
                        samTotal += 1
                    
                for edge in graph.edges_iter():
                    start = edge[0]
                    end = edge[1]
                    edgeTag = graph.edge[start][end][NetworkFrames.compressState.tag]
                    if edgeTag != NetworkFrames.compressState.none:
                        samEdgeData[edgeTag] += 1
                        edge_data[edgeTag] += 1
                        samTotal += 1
            elem_wise_states.append(copy.deepcopy(edge_data))
        
                   
        labels = ['Noop','Node Added', 'Node Deleted', 'Edge Added', 'Edge Deleted', 'Edge Statechange']
        inputData = [(inputNodeData[NetworkFrames.compressState.none] + inputEdgeData[NetworkFrames.compressState.none])/inputTotal,
                     inputNodeData[NetworkFrames.compressState.added]/inputTotal,
                     inputNodeData[NetworkFrames.compressState.deleted]/inputTotal,
                     inputEdgeData[NetworkFrames.compressState.added]/inputTotal,
                     inputEdgeData[NetworkFrames.compressState.deleted]/inputTotal,
                     inputEdgeData[NetworkFrames.compressState.stateChange]/inputTotal]
        inputNodeData = [(inputNodeData[NetworkFrames.compressState.none] )/inputNodeTotal,
                     inputNodeData[NetworkFrames.compressState.added]/inputNodeTotal,
                     inputNodeData[NetworkFrames.compressState.deleted]/inputNodeTotal,
                     0.,
                     0.,
                     0.]
        samData = [(samNodeData[NetworkFrames.compressState.none]+samEdgeData[NetworkFrames.compressState.none])/samTotal,
                   samNodeData[NetworkFrames.compressState.added]/samTotal,
                   samNodeData[NetworkFrames.compressState.deleted]/samTotal,
                   samEdgeData[NetworkFrames.compressState.added]/samTotal,
                   samEdgeData[NetworkFrames.compressState.deleted]/samTotal,
                   samEdgeData[NetworkFrames.compressState.stateChange]/samTotal]
        self.display.pieChart("Input Network Changes_" + str(index), inputData, labels)
        #self.display.pieChart("Input Network Node Changes", inputNodeData, labels)
        self.display.pieChart("Sampled Network Changes_" + str(index) , samData, labels) 
                
    def generateSampleComparisonData(self):
        gtrieTotal = 0.
        gtrieNodeTotal = 0.
        samTotal = 0.
        gtrieNodeData = {tag:0 for tag in NetworkFrames.compressState.allStates}
        gtrieEdgeData = {tag:0 for tag in NetworkFrames.compressState.allStates}
        samNodeData = {tag:0 for tag in NetworkFrames.compressState.allStates}
        samEdgeData = {tag:0 for tag in NetworkFrames.compressState.allStates}           
        for index in range(len(self.extractionMap)):
            element = self.extractionMap[index]

            for graph in element[1]:
                for node in graph.node:
                    nodeTag = graph.node[node][NetworkFrames.compressState.tag]
                    samNodeData[nodeTag] += 1
                    samTotal += 1
                    if index in self.gtrieExtractionPool and len(self.gtrieExtractionPool[index]) > 0:
                        gtrieNodeData[nodeTag] += 1
                        gtrieTotal += 1      
                    
                for edge in graph.edges_iter():
                    start = edge[0]
                    end = edge[1]
                    edgeTag = graph.edge[start][end][NetworkFrames.compressState.tag]
                    samEdgeData[edgeTag] += 1
                    samTotal += 1
                    if index in self.gtrieExtractionPool and len(self.gtrieExtractionPool[index]) > 0:
                        gtrieEdgeData[edgeTag] += 1
                        gtrieTotal + 1
        
                   
        labels = ['Noop','Node Added', 'Node Deleted', 'Edge Added', 'Edge Deleted', 'Edge Statechange']
        inputData = [(gtrieNodeData[NetworkFrames.compressState.none] + gtrieEdgeData[NetworkFrames.compressState.none])/gtrieTotal,
                     gtrieNodeData[NetworkFrames.compressState.added]/gtrieTotal,
                     gtrieNodeData[NetworkFrames.compressState.deleted]/gtrieTotal,
                     gtrieEdgeData[NetworkFrames.compressState.added]/gtrieTotal,
                     gtrieEdgeData[NetworkFrames.compressState.deleted]/gtrieTotal,
                     gtrieEdgeData[NetworkFrames.compressState.stateChange]/gtrieTotal]
        '''gtrieNodeData = [(gtrieNodeData[NetworkFrames.compressState.none] )/gtrieNodeTotal,
                     gtrieNodeData[NetworkFrames.compressState.added]/gtrieNodeTotal,
                     gtrieNodeData[NetworkFrames.compressState.deleted]/gtrieNodeTotal,
                     0.,
                     0.,
                     0.]'''
        samData = [(samNodeData[NetworkFrames.compressState.none]+samEdgeData[NetworkFrames.compressState.none])/samTotal,
                   samNodeData[NetworkFrames.compressState.added]/samTotal,
                   samNodeData[NetworkFrames.compressState.deleted]/samTotal,
                   samEdgeData[NetworkFrames.compressState.added]/samTotal,
                   samEdgeData[NetworkFrames.compressState.deleted]/samTotal,
                   samEdgeData[NetworkFrames.compressState.stateChange]/samTotal]
        self.display.pieChart("Gtrie Changes", inputData, labels)
        #self.display.pieChart("Gtrie Node Changes", gtrieNodeData, labels)
        self.display.pieChart("Sampled Network Changes", samData, labels)
        
    def generateProportionalSelectionData(self):
        self.proportionalSelection = []
        for element in self.extractionMap:
            if self.proportionalSelection == []:
                self.proportionalSelection.append([element[0], len(element[1]), 0])
                continue
            value = self.proportionalSelection[-1][1] + len(element[1])
            self.proportionalSelection.append([element[0], value, 0])
            
    def rebalanceProportionalSelectionData(self, itemToRemove):
        #Save rebalance value
        size = len(self.extractionMap[itemToRemove][1])
        
        #Rebalance the proportional selection
        for index in range(itemToRemove, len(self.proportionalSelection)):
            self.proportionalSelection[index][1] = self.proportionalSelection[index][1] - size
        
        #Remove the index in question
        #self.proportionalSelection.pop(itemToRemove)
        
    def selectRewritingRule(self, subgraph):
        returnGraph = None
        
        for element in self.extractionMap:
            if self.util.isIsomorphicFast(element[0], subgraph):
                returnGraph = copy.deepcopy(random.choice(element[1]))
                break
        return returnGraph
    
    def selectRewritingRuleGTrie(self, subgraph):
        rewritingRule = None
        if self.util.isIsomorphicFast(self.extractionMap[subgraph[1]][0], subgraph[0]):
            candidateList = self.extractionMap[subgraph[1]][2]
            while rewritingRule == None and len(candidateList) > 0:
                selection = random.choice(candidateList)
                rewritingSubgraph = copy.deepcopy(self.extractionMap[subgraph[1]][1][selection])
                delta = self.rewriting.makeNodeLabelsDisjoint(subgraph[0], rewritingSubgraph)
                associatedExtraction = self.prev_extraction.getExtractionSubgraphFromDelta(delta)
                mapping = self.util.findSubgraphInstances(subgraph[0], associatedExtraction)
                if len(mapping) < 1:
                    print "Error in mapping rewriting during simulation!"
                rewritingRule = nx.relabel_nodes(delta,mapping[0],copy=True) if len(mapping) > 0 else delta
                rewritingRule = None if self.isRewritingRuleInUsed(rewritingRule) else rewritingRule
                candidateList.remove(selection)
        else:
            print "Error has occured while selecting rewriting rule for Gtrie."
            print subgraph[0].edge
            print subgraph[1]
            print self.extractionMap[subgraph[1]][0].edge
            
        return rewritingRule
        
            
    def getMotifSizeList(self):
        sizeList = []
        for element in self.extractionMap:
            sizeList.append(len(element[0].nodes()))
            
        return sizeList
    
    def generateNewExtractionPool(self, network):
        #Generate extraction candidates for each key in the extraction map
        import time
        totalstart = time.time()
        self.extractionPool = {}
        connected = 0
        
        #***************************************
        for element in self.extractionMap:
            if nx.is_connected(element[0]):
                connected += 1
        print "Total number of extracted subgraphs: " + str(len(self.extractionMap))
        print "Number of connected subgraphs: " + str(connected)   
        #***************************************
        
        for element in self.extractionMap: 
            substart = time.time()
            if nx.is_connected(element[0]):
                connected += 1
            extractionCandidates = self.util.findSubgraphInstances(network, element[0])
            print "Subpool size: " + str(len(extractionCandidates))
            subelapsed = time.time() - substart
            print "Subpool elapsed time: " + str(subelapsed)
            self.extractionPool[element[0]] = extractionCandidates
        
        print "Number of connected subgraphs: " + str(connected) 
        totalelapsed = time.time()- totalstart
        print "Total elapsed pool time: " + str(totalelapsed)
        import sys
        print "Total size of extraction pool in Bytes: " + str(sys.getsizeof(self.extractionPool))
    
    def generateGTrieExtractionPool(self, network, num_changes = 5001):
        print "Generating GTrie Extraction Pool...",
        self.simulationgtrie.setMaxMatches(self.sample_num)
        value = 0.001 if num_changes > 5000 else 0.01
        value = 0.0001 if num_changes > 6000 else value
        value = 0.00001 if num_changes > 7000 else value
        value = 0.000005 if num_changes > 10000 else value
        value = 0.000001 if num_changes > 20000 else value
        self.simulationgtrie.GTrieMatch(network, [1,1,1,math.sqrt(value),math.sqrt(value)], labels=True, states=True)
        print "Done."
        self.gtrieExtractionPool = self.simulationgtrie.getMatches(labels=True)
        for keys in self.gtrieExtractionPool.iterkeys():
            print len(self.gtrieExtractionPool[keys])
        
    def generateExtractionTree(self):
        self.simulationgtrie = GTrie.GTrie()
        for index in range(len(self.extractionMap)):
            subgraph = self.extractionMap[index][0]
            self.simulationgtrie.GTrieInsert(subgraph, index, states=True)
                
    def chooseExtractionSubgraph(self, network):
        #Select extraction subgraph based on input network probability distribution
        returnSubgraph = None
        rand = random.random() * self.proportionalSelection[-1][1]
        for candidate in self.proportionalSelection:
            val = candidate[1]
            if rand <= val and len(self.extractionPool[candidate[0]]):
                index = random.randint(0, len(self.extractionPool[candidate[0]])-1)
                subgraphMap = self.extractionPool[candidate[0]].pop(index)
                returnSubgraph = network.subgraph(subgraphMap.values()).copy()
                candidate[2] += 1
                break
        
        if returnSubgraph == None:
            self.chooseExtractionSubgraph(network)
            
        return returnSubgraph
    
    def chooseExtractionSubgraphGTrie(self, network): 
        #Select extraction subgraph based on input network probability distribution
        returnSubgraph = None
        returnIndex = -1
        choice = -1
        while returnIndex == -1:
            rand = random.random() * self.proportionalSelection[-1][1]
            for index in range(len(self.proportionalSelection)):
                val = self.proportionalSelection[index][1]
                if index in self.gtrieExtractionPool and rand <= val and len(self.gtrieExtractionPool[index]):
                    pick = random.randint(0, len(self.gtrieExtractionPool[index])-1)
                    choice = pick
                    returnSubgraph = self.gtrieExtractionPool[index][pick]
                    returnIndex = index
                    self.proportionalSelection[index][2] += 1
                    break
            
        return (returnSubgraph,returnIndex,choice)
    
    def removeExtractionSubgraphGTrieMatch(self, subgraphTuple):
        self.gtrieExtractionPool[subgraphTuple[1]].pop(subgraphTuple[2])
        if len(self.gtrieExtractionPool[subgraphTuple[1]]) == 0:
            self.rebalanceProportionalSelectionData(subgraphTuple[1])

    def getSizeOfExtractionSubgraphGTrieMatch(self):
        length = 0
        for key in self.gtrieExtractionPool.iterkeys():
            length += len(self.gtrieExtractionPool[key])
            
        return length
    
    def getSizeOfGTrieExtractionPool(self):
        return len(self.gtrieExtractionPool)
    
    def getComparisonData(self):
        inputCount = []
        simulationCount = []
        
        for element in self.extractionMap:
            inputCount.append(len(element[1]))
            
        for candidate in self.proportionalSelection:
            simulationCount.append(candidate[2])
            
        return [inputCount,simulationCount]