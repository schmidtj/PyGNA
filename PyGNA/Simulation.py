"""
Simulation class.

"""
__author__ = """\n""".join(['Jeffrey Schmidt (jschmid1@binghamton.edu',
                            'Benjamin Bush (benjaminjamesbush@gmail.com)',
                            'Hiroki Sayama (sayama@binghamton.edu)'])

__all__ = []


#    Copyright (C) 2013 by
#    Jeffrey Schmidt <jschmid1@binghamton.edu>
#    Benjamin Bush <benjaminjamesbush@gmail.com>
#    Hiroki Sayama <sayama@binghamton.edu>
#    All rights reserved.
#    BSD license.

import Display
import networkx as nx
import NetworkFrames
import Extraction
import MotifExtraction
import Rewriting
import Utility
import copy
import numpy
import random
import RecipeBuilder

class Simulation(object):
    def __init__(self):
        pass
    
    def __init__(self, extraction, rewriting, networkFrames):
        self.iterations = 1
        self.extraction = extraction
        self.rewriting = rewriting
        self.utility = Utility.utility()
        self.networkFrames = networkFrames
        self.avgShortestPathDisplay = Display.display(True)
        self.densityDisplay = Display.display(True)
        self.nodesDisplay = Display.display(True)
        self.edgesDisplay = Display.display(True)
        self.avgClusteringDisplay = Display.display(True)
        self.cumulativeDegreeDist = Display.display(True)
        self.bhattacharyyaDegreeDisplay = Display.display()
        self.simulationNetwork = []
        self.simulationNetworkList = []
        self.UESFrequencyList = []
        self.UESMeanFrequencyList = []
        self.UESStdFrequencyList = []
        self.UES_BDList = []
        self.AttemptList = []
        self.BDMeanIndex = 0
        self.UES_BDMean = 0.
        self.UES_BDStd = 0.
        self.simulationInputKey = 0
    
    def setIterations(self, iterations):
        self.iterations = iterations
    
    def addGraphToSimulatedNetwork(self, graph):
        if len(self.simulationNetwork) == 0:
            self.simulationInputKey = 0
            
        add_graph = graph.copy()
        add_graph.name = str(self.simulationInputKey)
        self.simulationNetwork.append(add_graph)
        self.simulationInputKey+=1

    def storeSimulatedNetwork(self):
        temp_frames = NetworkFrames.NetworkFrames()
        temp_frames.setInputNetwork(self.simulationNetwork)
        self.simulationNetworkList.append(temp_frames)
        
    def write_final_simulated_network(self):
        self.simulationNetworkList[-1].writeGraphs('simulated_network.graphML')
        
    def clearSimulatedNetwork(self):
        self.simulationNetwork = []

    def processSimulationData(self, index, current_network=False):
        for freqData in self.UESFrequencyList:
            self.UES_BDList.append(freqData.getBhattacharyyaDistance())
            
        self.UES_BDMean = numpy.mean(self.UES_BDList)
        self.UES_BDStd = numpy.std(self.UES_BDList)
        
        #self.findMeanBDIndex()
        #self.extractMeanNetwork()
        #self.findFrequencyStats()
        if current_network:
            self.generateDisplayDataAtIndex(index)
        else:
            self.generateDisplayData()
        
    def findFrequencyStats(self):
        input_frequency = self.UESFrequencyList[0].getHistInputData()
        frequency_array = []
        for data in self.UESFrequencyList:
            frequency_array.append(data.getHistSimulatedData())
        
        numpyArray = numpy.array(frequency_array)
        #tempDisplay = Display.display()
        index = 0
        while index < len(input_frequency):
            column = numpyArray[:, index]
            #tempDisplay.scatter(range(len(column)), column)
            std = numpy.std(column)*2
            mean = numpy.mean(column)
            self.UESMeanFrequencyList.append(mean)
            self.UESStdFrequencyList.append(std)
            
            index += 1
            
    def generateDisplayData(self):
        
        print "Generating Results..."
        first = True
        count = 0
        for networks in self.simulationNetworkList:
            frame_number = 0
            while frame_number < len(self.networkFrames.getInputNetworks())-1:
                print str(count+1),
                #Add input network data
                if first:
                    #Avg. shortest path length
                    try:
                        self.avgShortestPathDisplay.addInputValue(nx.average_shortest_path_length(self.networkFrames.getInputNetworkAt(frame_number)))
                    except Exception:
                        try:
                            self.avgShortestPathDisplay.addInputValue(nx.average_shortest_path_length(nx.connected_component_subgraphs(self.networkFrames.getInputNetworkAt(frame_number))[0]))
                        except Exception:
                            self.avgShortestPathDisplay.addInputValue(0)
                            
                    #Density
                    try:
                        self.densityDisplay.addInputValue(nx.density(self.networkFrames.getInputNetworkAt(frame_number)))
                    except Exception:
                        try:
                            self.densityDisplay.addInputValue(nx.density(nx.connected_component_subgraphs(self.networkFrames.getInputNetworkAt(frame_number))[0]))
                        except Exception:
                            self.densityDisplay.addInputValue(0)
                            
                    #Num Nodes display
                    try:
                        self.nodesDisplay.addInputValue(len(self.networkFrames.getInputNetworkAt(frame_number).nodes()))
                    except Exception:
                        self.nodesDisplay.addInputValue(0)
                    
                    #Edges display
                    try:
                        self.edgesDisplay.addInputValue(len(self.networkFrames.getInputNetworkAt(frame_number).edges()))
                    except Exception:
                        self.edgesDisplay.addInputValue(0)
                        
                    #Average Clustering
                    try:
                        self.avgClusteringDisplay.addInputValue(nx.average_clustering(self.networkFrames.getInputNetworkAt(frame_number)))
                    except Exception:
                        self.avgClusteringDisplay.addInputValue(0)
                        
                #Add Simulated data
                
                #Avg. Shortest Path
                try:
                    self.avgShortestPathDisplay.addExperimentalValue(nx.average_shortest_path_length(networks.getInputNetworkAt(frame_number)))
                except Exception:
                    try:
                        self.avgShortestPathDisplay.addExperimentalValue(nx.average_shortest_path_length(nx.connected_component_subgraphs(networks.getInputNetworkAt(frame_number))[0]))
                    except Exception:
                        self.avgShortestPathDisplay.addExperimentalValue(0)
                        
                #Density
                try:
                    self.densityDisplay.addExperimentalValue(nx.density(networks.getInputNetworkAt(frame_number)))
                except Exception:
                    try:
                        self.densityDisplay.addExperimentalValue(nx.density(nx.connected_component_subgraphs(networks.getInputNetworkAt(frame_number))[0]))
                    except Exception:
                        self.densityDisplay.addExperimentalValue(0)   
                        
                #Num Nodes display
                try:
                    self.nodesDisplay.addExperimentalValue(len(networks.getInputNetworkAt(frame_number).nodes()))
                except Exception:
                    self.nodesDisplay.addExperimentalValue(0)
                
                #Num edges display
                try:
                    self.edgesDisplay.addExperimentalValue(len(networks.getInputNetworkAt(frame_number).edges()))
                except Exception:
                    self.edgesDisplay.addExperimentalValue(0)
                    
                #Clustering
                try:
                    self.avgClusteringDisplay.addExperimentalValue(nx.average_clustering(networks.getInputNetworkAt(frame_number)))
                except Exception:
                    self.avgClusteringDisplay.addExperimentalValue(0)
                    
                # BD cumulative degree dist
                input_cum_degree = self.utility.generateCumulativeDegDist(self.networkFrames.getInputNetworkAt(frame_number))
                simulated_cum_degree = self.utility.generateCumulativeDegDist(networks.getInputNetworkAt(frame_number))
                processed_cum_degree = self.utility.processCumDegreeForBD(input_cum_degree, simulated_cum_degree)
                self.bhattacharyyaDegreeDisplay.addInputValue(self.utility.BhattacharyyaDistance(processed_cum_degree[0],processed_cum_degree[1]))
                
                frame_number += 1
                
            first = False
            count += 1
            
            self.avgShortestPathDisplay.appendExperimentalValuesToList()
            self.avgShortestPathDisplay.clearExperimentalValues()
            
            self.densityDisplay.appendExperimentalValuesToList()
            self.densityDisplay.clearExperimentalValues()
            
            self.nodesDisplay.appendExperimentalValuesToList()
            self.nodesDisplay.clearExperimentalValues()
            
            self.edgesDisplay.appendExperimentalValuesToList()
            self.edgesDisplay.clearExperimentalValues()
            
            self.avgClusteringDisplay.appendExperimentalValuesToList()
            self.avgClusteringDisplay.clearExperimentalValues()
            
            self.bhattacharyyaDegreeDisplay.appendInputValuesToList()
            self.bhattacharyyaDegreeDisplay.clearInputValues()
        
        input_cumulative_deg_dist = self.utility.generateCumulativeDegDist(self.networkFrames.getInputNetworkAt(len(self.networkFrames.getInputNetworks())-1))
        simulated_cumulative_deg_dist = self.utility.generateCumulativeDegDist(self.simulationNetworkList[-1].getInputNetworkAt(len(self.networkFrames.getInputNetworks())-1))
        self.cumulativeDegreeDist.addInputXValueList(input_cumulative_deg_dist[0])
        self.cumulativeDegreeDist.addInputYValueList(input_cumulative_deg_dist[1])
        self.cumulativeDegreeDist.addExperimentalXValueList(simulated_cumulative_deg_dist[0])
        self.cumulativeDegreeDist.addExperimentalYValueList(simulated_cumulative_deg_dist[1])
        print "Done."    
                             
    def generateDisplayDataAtIndex(self, index):
           
        print "Generating Results..."
        input_network = self.networkFrames.getInputNetworkAt(index)
        sim_network = self.simulationNetwork[index]
        frame_number = index

        #Avg. shortest path length
        try:
            self.avgShortestPathDisplay.addInputValue(nx.average_shortest_path_length(self.networkFrames.getInputNetworkAt(frame_number)))
        except Exception:
            try:
                self.avgShortestPathDisplay.addInputValue(nx.average_shortest_path_length(nx.connected_component_subgraphs(self.networkFrames.getInputNetworkAt(frame_number))[0]))
            except Exception:
                self.avgShortestPathDisplay.addInputValue(0)
                
        #Density
        try:
            self.densityDisplay.addInputValue(nx.density(self.networkFrames.getInputNetworkAt(frame_number)))
        except Exception:
            try:
                self.densityDisplay.addInputValue(nx.density(nx.connected_component_subgraphs(self.networkFrames.getInputNetworkAt(frame_number))[0]))
            except Exception:
                self.densityDisplay.addInputValue(0)
                
        #Num Nodes display
        try:
            self.nodesDisplay.addInputValue(len(self.networkFrames.getInputNetworkAt(frame_number).nodes()))
        except Exception:
            self.nodesDisplay.addInputValue(0)
        
        #Edges display
        try:
            self.edgesDisplay.addInputValue(len(self.networkFrames.getInputNetworkAt(frame_number).edges()))
        except Exception:
            self.edgesDisplay.addInputValue(0)
            
        #Average Clustering
        try:
            self.avgClusteringDisplay.addInputValue(nx.average_clustering(self.networkFrames.getInputNetworkAt(frame_number)))
        except Exception:
            self.avgClusteringDisplay.addInputValue(0)
                
        #Add Simulated data
        
        #Avg. Shortest Path
        try:
            self.avgShortestPathDisplay.addExperimentalValue(nx.average_shortest_path_length(self.simulationNetwork[frame_number]))
        except Exception:
            try:
                self.avgShortestPathDisplay.addExperimentalValue(nx.average_shortest_path_length(nx.connected_component_subgraphs(self.simulationNetwork[frame_number])[0]))
            except Exception:
                self.avgShortestPathDisplay.addExperimentalValue(0)
                
        #Density
        try:
            self.densityDisplay.addExperimentalValue(nx.density(self.simulationNetwork[frame_number]))
        except Exception:
            try:
                self.densityDisplay.addExperimentalValue(nx.density(nx.connected_component_subgraphs(self.simulationNetwork[frame_number])[0]))
            except Exception:
                self.densityDisplay.addExperimentalValue(0)   
                
        #Num Nodes display
        try:
            self.nodesDisplay.addExperimentalValue(len(self.simulationNetwork[frame_number].nodes()))
        except Exception:
            self.nodesDisplay.addExperimentalValue(0)
        
        #Num edges display
        try:
            self.edgesDisplay.addExperimentalValue(len(self.simulationNetwork[frame_number].edges()))
        except Exception:
            self.edgesDisplay.addExperimentalValue(0)
            
        #Clustering
        try:
            self.avgClusteringDisplay.addExperimentalValue(nx.average_clustering(self.simulationNetwork[frame_number]))
        except Exception:
            self.avgClusteringDisplay.addExperimentalValue(0)
            
        # BD cumulative degree dist
        input_cum_degree = self.utility.generateCumulativeDegDist(self.networkFrames.getInputNetworkAt(frame_number))
        simulated_cum_degree = self.utility.generateCumulativeDegDist(self.simulationNetwork[frame_number])
        processed_cum_degree = self.utility.processCumDegreeForBD(input_cum_degree, simulated_cum_degree)
        self.bhattacharyyaDegreeDisplay.addInputValue(self.utility.BhattacharyyaDistance(processed_cum_degree[0],processed_cum_degree[1]))
                    
        self.avgShortestPathDisplay.appendExperimentalValuesToList()
        self.avgShortestPathDisplay.clearExperimentalValues()
        
        self.densityDisplay.appendExperimentalValuesToList()
        self.densityDisplay.clearExperimentalValues()
        
        self.nodesDisplay.appendExperimentalValuesToList()
        self.nodesDisplay.clearExperimentalValues()
        
        self.edgesDisplay.appendExperimentalValuesToList()
        self.edgesDisplay.clearExperimentalValues()
        
        self.avgClusteringDisplay.appendExperimentalValuesToList()
        self.avgClusteringDisplay.clearExperimentalValues()
        
        self.bhattacharyyaDegreeDisplay.appendInputValuesToList()
        self.bhattacharyyaDegreeDisplay.clearInputValues()
        
        '''inputCumulativeDegDist = self.utility.generateCumulativeDegDist(self.networkFrames.getInputNetworkAt(len(self.networkFrames.getInputNetworks())-1))
        simulatedCumulativeDegDist = self.utility.generateCumulativeDegDist(self.meanNetwork.getInputNetworkAt(len(self.networkFrames.getInputNetworks())-1))
        self.cumulativeDegreeDist.addInputXValueList(inputCumulativeDegDist[0])
        self.cumulativeDegreeDist.addInputYValueList(inputCumulativeDegDist[1])
        self.cumulativeDegreeDist.addExperimentalXValueList(simulatedCumulativeDegDist[0])
        self.cumulativeDegreeDist.addExperimentalYValueList(simulatedCumulativeDegDist[1])'''
        print "Done."   
               
    def findMeanBDIndex(self):
        min_dist = float("inf")
        index = 0
        while index < len(self.UES_BDList):
            mean_dist = abs(self.UES_BDMean - self.UES_BDList[index])
            if mean_dist < min_dist:
                min_dist = mean_dist
                self.BDMeanIndex = index
            index += 1
            
    def extractMeanNetwork(self):
        self.meanNetwork = self.simulationNetworkList[self.BDMeanIndex]
        
    def runSimulation(self):
        if len(self.networkFrames.getInputNetworks()) > 0:
            
            print "Recreating Input Network..."
            # Set the initial configuration
            start_frame = self.networkFrames.getInputNetworkAt(0)
            
            for iteration in range(self.iterations):
                print str(iteration+1),
                focus_frame = start_frame.copy()
                self.addGraphToSimulatedNetwork(focus_frame)
                attempt_data_display = Display.display(False)
                
                frame_number = 0
                while frame_number < len(self.networkFrames.getInputNetworks())-1:
                    rewriting_event = None
                    
                    attempts = 0
                    while rewriting_event is None:
                        extraction_subgraph = self.extraction.performExtraction(focus_frame)
                        rewriting_event = self.rewriting.performRewriting(extraction_subgraph)
                        attempts += 1
                    
                    attempt_data_display.addInputValue(attempts)
                    self.networkFrames._decompress(focus_frame, rewriting_event)
                    self.addGraphToSimulatedNetwork(focus_frame)
                    frame_number += 1
                    
                self.storeSimulatedNetwork()
                self.clearSimulatedNetwork()
                self.UESFrequencyList.append(copy.deepcopy(self.rewriting.getDisplayData()))
                self.rewriting.resetDataDisplay()
    
            print "Done."
            self.processSimulationData()
            print "UES Mean BD: " + str(self.UES_BDMean)
            print "UES Std BD: " + str(self.UES_BDStd)
            #self.meanNetwork.writeSpecificGraphs("generatedOutputMeanNetwork.graphML", self.meanNetwork.getDecompressedFrames())
            ues_display = Display.display(False)
            ues_display.addInputValues([], self.UESFrequencyList[0].getHistInputData())
            ues_display.addExperimentalValues([] ,self.UESMeanFrequencyList)
            ues_display.UESBarPlot('Unique Extraction Subgraph Comparison', 'Times Selected', 'Subgraph Groups', self.UESMeanFrequencyList, self.UESStdFrequencyList, self.UES_BDMean)
            self.bhattacharyyaDegreeDisplay.lineGraph("Bhattacharyya Distance - Cumulative Degree Distribution", "Time Step", "Bhattacharyya Distance", multiLine=True)
            self.cumulativeDegreeDist.lineGraph("Cumulative Degree Distribution", "Degree (d)", "P(x >= d)")
            self.densityDisplay.lineGraph("Graph Density", "Time Step", "Graph Density", legloc="upper right", multiLine=True)
            self.avgShortestPathDisplay.lineGraph("Average Shortest Path Length", "Time Step", "Avg. Shortest Path", multiLine=True)
            self.avgClusteringDisplay.lineGraph("Average Clustering", "Time Step", "Average Clustering", legloc= "upper right", multiLine=True)
            #attemptDataDisplay.lineGraph("Attempts", "Time", "Attempts") 
            
    def runMotifSimulation(self, motifSize):
        if len(self.networkFrames.getInputNetworks()) > 0:    
            print "Recreating Input Network..."
            # Set the initial configuration
            self.extraction.generateExtractionTree()
            startFrame = self.networkFrames.getInputNetworkAt(0)
            bargraph = Display.display()
            for iteration in range(self.iterations):
                print str(iteration+1),
                focusFrame = startFrame.copy()
                self.addGraphToSimulatedNetwork(focusFrame)
                attemptDataDisplay = Display.display(False)
                motifSizeList = self.extraction.getMotifSizeList()
                
                frameNumber = 0
                while frameNumber < len(self.networkFrames.getInputNetworks())-1:
                    numchanges = 0
                    targetchanges = self.networkFrames.getNumberOfChanges(frameNumber+1)/motifSize
                    self.extraction.generateGTrieExtractionPool(focusFrame)
                    self.extraction.clearUsedRewritingRules()
                    self.extraction.resetRewritingRuleExclusionList()
                    self.extraction.generateProportionalSelectionData()
                    self.extraction.generateSampleComparisonData()
                    
                    while self.extraction.getSizeOfExtractionSubgraphGTrieMatch() > 0 and numchanges < targetchanges:
                        rewritingRule = None
                        extractionSubgraph = None
                        
                        while rewritingRule == None:
                            extractionSubgraph = self.extraction.chooseExtractionSubgraphGTrie(focusFrame)
                            rewritingRule = self.extraction.selectRewritingRuleGTrie(extractionSubgraph)
                            if rewritingRule == None:
                                self.extraction.removeExtractionSubgraphGTrieMatch(extractionSubgraph)
                                
                            if self.extraction.getSizeOfExtractionSubgraphGTrieMatch() == 0:
                                break
                                
                        if rewritingRule == None:
                            continue
                        
                        self.extraction.addUsedRewritingRules(rewritingRule)
                        self.networkFrames._decompress(focusFrame, rewritingRule)
                        numchanges += 1
                        
                    
                    #comparison = self.extraction.getComparisonData()
                    #bargraph.barCompare("Extraction Subgraph Compare", "Extraction Subgraph", "Frequency", comparison[0], comparison[1])
                    print "Number of changes: " + str(numchanges)
                    self.extraction.displayUsedRewritingRuleGraph()
                    self.addGraphToSimulatedNetwork(focusFrame)
                    frameNumber+=1
                    
                self.storeSimulatedNetwork()
                self.clearSimulatedNetwork()
                self.UESFrequencyList.append(copy.deepcopy(self.rewriting.getDisplayData()))
                self.rewriting.resetDataDisplay()
    
            print "Done."
            self.processSimulationData()
            print "UES Mean BD: " + str(self.UES_BDMean)
            print "UES Std BD: " + str(self.UES_BDStd)
            #self.meanNetwork.writeSpecificGraphs("generatedOutputMeanNetwork.graphML", self.meanNetwork.getDecompressedFrames())
            UES_Display = Display.display(False)
            UES_Display.addInputValues([],self.UESFrequencyList[0].getHistInputData())
            UES_Display.addExperimentalValues([],self.UESMeanFrequencyList)
            #UES_Display.UESBarPlot('Unique Extraction Subgraph Comparison', 'Times Selected', 'Subgraph Groups',self.UESMeanFrequencyList, self.UESStdFrequencyList, self.UES_BDMean)
            self.bhattacharyyaDegreeDisplay.lineGraph("Bhattacharyya Distance - Cumulative Degree Distribution", "Time Step", "Bhattacharyya Distance",multiLine=True)
            #self.cumulativeDegreeDist.loglogPlot("Cumulative Degree Distribution", "Degree (d)", "P(x >= d)", legloc="upper right",multiLine=False)
            self.densityDisplay.lineGraph("Graph Density", "Time Step", "Graph Density", legloc="upper right",multiLine=True)
            self.nodesDisplay.lineGraph("Number of Nodes", "Time Step", "Num Nodes", legloc="upper right", multiLine=True)
            self.edgesDisplay.lineGraph("Number of Edges","Time Step", "Num Edges", legloc="upper right", multiLine=True)
            self.avgShortestPathDisplay.lineGraph("Average Shortest Path Length", "Time Step", "Avg. Shortest Path",multiLine=True)
            self.avgClusteringDisplay.lineGraph("Average Clustering", "Time Step", "Average Clustering",legloc="upper right",multiLine=True)         
            #nx.write_graphml(self.simulationNetwork[-1], "Final_output.graphML")
            #nx.write_graphml(self.simulationNetwork[0], "Starting_output.graphML")
            
    def runIterativeMotifSimulation(self, motifSize, sampleSize):
        if len(self.networkFrames.getInputNetworks()) > 0:    
            print "Recreating Input Network..."
            # Set the initial configuration
            startFrame = self.networkFrames.getInputNetworkAt(0)
            focusFrame = startFrame.copy()
            self.addGraphToSimulatedNetwork(focusFrame)            
            for network_index in xrange(1,len(self.networkFrames._getCompressedNetworks())):
                self.extraction.sampleNetworkAt(sampleSize, network_index)
                self.extraction.generateExtractionTree() 
                print "Total Number of Changes: " + str(self.networkFrames.getNumberOfChanges(network_index))
                self.extraction.generateGTrieExtractionPool(focusFrame,self.networkFrames.getNumberOfChanges(network_index))
                self.extraction.clearUsedRewritingRules()
                self.extraction.resetRewritingRuleExclusionList()
                self.extraction.generateProportionalSelectionData()
                #self.extraction.analyzeGTrieExtractionPool()
                
                numchanges = 0
                lastchanges = 0
                targetchanges = int(self.networkFrames.getNumberOfChanges(network_index)/self.extraction.getAvgChanges())
                print "Target Changes: " + str(targetchanges)
                while self.extraction.getSizeOfExtractionSubgraphGTrieMatch() > 0 and numchanges < targetchanges:
                    rewritingRule = None
                    extractionSubgraph = None
                    
                    while rewritingRule == None:
                        extractionSubgraph = self.extraction.chooseExtractionSubgraphGTrie(focusFrame)
                        rewritingRule = self.extraction.selectRewritingRuleGTrie(extractionSubgraph)
                        if rewritingRule == None:
                            self.extraction.removeExtractionSubgraphGTrieMatch(extractionSubgraph)
                            
                        if self.extraction.getSizeOfExtractionSubgraphGTrieMatch() == 0:
                            print "Changes This Iteration: " + str(numchanges-lastchanges)
                            if (numchanges - lastchanges < .025 * targetchanges and numchanges > .75 * targetchanges) or \
                               numchanges == lastchanges:
                                break
                            self.extraction.generateGTrieExtractionPool(focusFrame, targetchanges)
                            self.extraction.generateProportionalSelectionData()
                            self.extraction.clearUsedRewritingRules()
                            self.extraction.resetRewritingRuleExclusionList()                            
                            #self.extraction.analyzeGTrieExtractionPool()
                            lastchanges = numchanges
                            #break
                            
                    if rewritingRule == None:
                        continue
                    
                    self.extraction.addUsedRewritingRules(rewritingRule)
                    self.networkFrames._decompress(focusFrame, rewritingRule)
                    #print "Size of Extraction Pool: " + str(self.extraction.getSizeOfGTrieExtractionPool())
                    numchanges += 1
                    
                print "Number of changes: " + str(numchanges)
                self.extraction.displayUsedRewritingRuleGraph(network_index)
                self.addGraphToSimulatedNetwork(focusFrame)
                self.displayComparisonData(network_index)
                    
            self.storeSimulatedNetwork()
            self.clearSimulatedNetwork()
            #self.UESFrequencyList.append(copy.deepcopy(self.rewriting.getDisplayData()))
            #self.rewriting.resetDataDisplay()
    
            print "Done."
    
    #----------------------------------------------------------------------
    def run_recipe_simulation(self):
        """"""
        if len(self.networkFrames.getInputNetworks()) > 0:    
            print "Recreating Input Network..."
            # Set the initial configuration
            startFrame = self.networkFrames.getInputNetworkAt(0)
            focusFrame = startFrame.copy()
            self.addGraphToSimulatedNetwork(focusFrame)
            recipe_builder = RecipeBuilder.RecipeBuilder(self.networkFrames)
            recipe = recipe_builder.union_method()
            for network_index in xrange(1,len(self.networkFrames._getCompressedNetworks())):
                recipe.generate_gtrie(network_index)
                recipe.generate_recipe_extraction_pool(focusFrame)
                rewriting_rule = recipe.select_rewriting_rule(focusFrame, network_index)
                self.networkFrames._decompress(focusFrame, rewriting_rule)
                self.addGraphToSimulatedNetwork(focusFrame)
                
    
            self.storeSimulatedNetwork()
            self.displayComparisonData(len(self.networkFrames._getCompressedNetworks())-1, False)
            self.write_final_simulated_network()
            self.clearSimulatedNetwork()
    
            print "Done."
            
    def displayComparisonData(self, index, current_Network=True):
        self.processSimulationData(index, current_Network)
        #self.meanNetwork.writeSpecificGraphs("generatedOutputMeanNetwork.graphML", self.meanNetwork.getDecompressedFrames())

        bhatt_title = "Bhattacharyya Distance - Cumulative Degree Distribution_" + str(index)
        dense_title = "Graph Density_" + str(index)
        nodes_title = "Number of Nodes" + str(index)
        edges_title = "Number of Edges" + str(index)
        avg_short_title = "Average Shortest Path Length" + str(index)
        avg_clust_title = "Average Clustering" + str(index)
        self.bhattacharyyaDegreeDisplay.lineGraph(bhatt_title, "Time Step", "Bhattacharyya Distance",multiLine=True)
        #self.cumulativeDegreeDist.loglogPlot("Cumulative Degree Distribution", "Degree (d)", "P(x >= d)", legloc="upper right",multiLine=False)
        self.densityDisplay.lineGraph(dense_title, "Time Step", "Graph Density", legloc="upper right",multiLine=True)
        self.nodesDisplay.lineGraph(nodes_title, "Time Step", "Num Nodes", legloc="upper right", multiLine=True)
        self.edgesDisplay.lineGraph(edges_title,"Time Step", "Num Edges", legloc="upper right", multiLine=True)
        self.avgShortestPathDisplay.lineGraph(avg_short_title, "Time Step", "Avg. Shortest Path",multiLine=True)
        self.avgClusteringDisplay.lineGraph(avg_clust_title, "Time Step", "Average Clustering",legloc="upper right",multiLine=True)         
  