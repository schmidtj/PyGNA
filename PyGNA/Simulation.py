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
import Rewriting
import Utility
import copy
import numpy

class Simulation(object):
    def __init__(self):
        pass
    
    def __init__(self, extraction, rewriting, utility, networkFrames):
        self.iterations = 1
        self. extraction = extraction
        self.rewriting = rewriting
        self.utility = utility
        self.networkFrames = networkFrames
        self.avgShortestPathDisplay = Display.display(True)
        self.densityDisplay = Display.display(True)
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
        self.simulationInputKey = 0
    
    def setIterations(self, iterations):
        self.iterations = iterations
    
    def addGraphToSimulatedNetwork(self, graph):
        if len(self.simulationNetwork) == 0:
            self.simulationInputKey = 0
            
        addGraph = graph.copy()
        addGraph.name = str(self.simulationInputKey)
        self.simulationNetwork.append(addGraph)
        self.simulationInputKey+=1

    def storeSimulatedNetwork(self):
        tempFrames = NetworkFrames.NetworkFrames()
        tempFrames.setInputNetwork(self.simulationNetwork)
        self.simulationNetworkList.append(tempFrames)
        
    def clearSimulatedNetwork(self):
        self.simulationNetwork = []

    def processSimulationData(self):
        for freqData in self.UESFrequencyList:
            self.UES_BDList.append(freqData.getBhattacharyyaDistance())
            
        self.UES_BDMean = numpy.mean(self.UES_BDList)
        self.UES_BDStd = numpy.std(self.UES_BDList)
        
        self.findMeanBDIndex()
        self.extractMeanNetwork()
        self.findFrequencyStats()
        self.generateDisplayData()
        
    def findFrequencyStats(self):
        inputFrequency = self.UESFrequencyList[0].getHistInputData()
        frequencyArray = []
        for data in self.UESFrequencyList:
            frequencyArray.append(data.getHistSimulatedData())
        
        numpyArray = numpy.array(frequencyArray)
        #tempDisplay = Display.display()
        index = 0
        while index < len(inputFrequency):
            column = numpyArray[:,index]
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
            frameNumber = 0
            while frameNumber < len(self.networkFrames.getInputNetworks())-1:
                print str(count+1),
                #Add input network data
                if first:
                    #Avg. shortest path length
                    try:
                        self.avgShortestPathDisplay.addInputValue(nx.average_shortest_path_length(self.networkFrames.getInputNetworkAt(frameNumber)))  
                    except Exception:
                        try:
                            self.avgShortestPathDisplay.addInputValue(nx.average_shortest_path_length(nx.connected_component_subgraphs(self.networkFrames.getInputNetworkAt(frameNumber))[0]))
                        except Exception:
                            self.avgShortestPathDisplay.addInputValue(0)
                            
                    #Density
                    try:
                        self.densityDisplay.addInputValue(nx.density(self.networkFrames.getInputNetworkAt(frameNumber)))  
                    except Exception:
                        try:
                            self.densityDisplay.addInputValue(nx.density(nx.connected_component_subgraphs(self.networkFrames.getInputNetworkAt(frameNumber))[0]))
                        except Exception:
                            self.densityDisplay.addInputValue(0)
                            
                    #Average Clustering
                    try:
                        self.avgClusteringDisplay.addInputValue(nx.average_clustering(self.networkFrames.getInputNetworkAt(frameNumber)))
                    except Exception:
                        self.avgClusteringDisplay.addInputValue(0)
                        
                #Add Simulated data
                
                #Avg. Shortest Path
                try:
                    self.avgShortestPathDisplay.addExperimentalValue(nx.average_shortest_path_length(networks.getInputNetworkAt(frameNumber)))
                except Exception:
                    try:
                        self.avgShortestPathDisplay.addExperimentalValue(nx.average_shortest_path_length(nx.connected_component_subgraphs(networks.getInputNetworkAt(frameNumber))[0]))
                    except Exception:
                        self.avgShortestPathDisplay.addExperimentalValue(0)
                        
                #Density
                try:
                    self.densityDisplay.addExperimentalValue(nx.density(networks.getInputNetworkAt(frameNumber)))
                except Exception:
                    try:
                        self.densityDisplay.addExperimentalValue(nx.density(nx.connected_component_subgraphs(networks.getInputNetworkAt(frameNumber))[0]))
                    except Exception:
                        self.densityDisplay.addExperimentalValue(0)   
                        
                #Clustering
                try:
                    self.avgClusteringDisplay.addExperimentalValue(nx.average_clustering(networks.getInputNetworkAt(frameNumber)))
                except Exception:
                    self.avgClusteringDisplay.addExperimentalValue(0)
                    
                # BD cumulative degree dist
                inputCumDegree = self.utility.generateCumulativeDegDist(self.networkFrames.getInputNetworkAt(frameNumber))
                simulatedCumDegree = self.utility.generateCumulativeDegDist(networks.getInputNetworkAt(frameNumber))
                processedCumDegree = self.utility.processCumDegreeForBD(inputCumDegree, simulatedCumDegree)
                self.bhattacharyyaDegreeDisplay.addInputValue(self.utility.BhattacharyyaDistance(processedCumDegree[0],processedCumDegree[1]))            
                
                frameNumber += 1
                
            first = False
            count += 1
            
            self.avgShortestPathDisplay.appendExperimentalValuesToList()
            self.avgShortestPathDisplay.clearExperimentalValues()
            
            self.densityDisplay.appendExperimentalValuesToList()
            self.densityDisplay.clearExperimentalValues()
            
            self.avgClusteringDisplay.appendExperimentalValuesToList()
            self.avgClusteringDisplay.clearExperimentalValues()
            
            self.bhattacharyyaDegreeDisplay.appendInputValuesToList()
            self.bhattacharyyaDegreeDisplay.clearInputValues()
        
        inputCumulativeDegDist = self.utility.generateCumulativeDegDist(self.networkFrames.getInputNetworkAt(len(self.networkFrames.getInputNetworks())-1))
        simulatedCumulativeDegDist = self.utility.generateCumulativeDegDist(self.meanNetwork.getInputNetworkAt(len(self.networkFrames.getInputNetworks())-1))
        self.cumulativeDegreeDist.addInputXValueList(inputCumulativeDegDist[0])
        self.cumulativeDegreeDist.addInputYValueList(inputCumulativeDegDist[1])
        self.cumulativeDegreeDist.addExperimentalXValueList(simulatedCumulativeDegDist[0])
        self.cumulativeDegreeDist.addExperimentalYValueList(simulatedCumulativeDegDist[1])
        print "Done."    
                             
    
    def findMeanBDIndex(self):
        minDist = float("inf")
        index = 0
        while index < len(self.UES_BDList):
            meanDist = abs(self.UES_BDMean - self.UES_BDList[index])
            if meanDist < minDist:
                minDist = meanDist
                self.BDMeanIndex = index
            index += 1
            
    def extractMeanNetwork(self):
        self.meanNetwork = self.simulationNetworkList[self.BDMeanIndex]
        
    def runSimulation(self):
        if len(self.networkFrames.getInputNetworks()) > 0:
            
            print "Recreating Input Network..."
            # Set the initial configuration
            startFrame = self.networkFrames.getInputNetworkAt(0)
            
            for iteration in range(self.iterations):
                print str(iteration+1),
                focusFrame = startFrame.copy()
                self.addGraphToSimulatedNetwork(focusFrame)
                attemptDataDisplay = Display.display(False)
                
                frameNumber = 0
                while frameNumber < len(self.networkFrames.getInputNetworks())-1:
                    rewritingEvent = None
                    
                    attempts = 0
                    while rewritingEvent == None:
                        extractionSubgraph = self.extraction.performExtraction(focusFrame)
                        rewritingEvent = self.rewriting.performRewriting(extractionSubgraph)
                        attempts+=1
                    
                    attemptDataDisplay.addInputValue(attempts)
                    self.networkFrames._decompress(focusFrame, rewritingEvent)
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
            UES_Display.UESBarPlot('Unique Extraction Subgraph Comparison', 'Times Selected', 'Subgraph Groups',self.UESMeanFrequencyList, self.UESStdFrequencyList, self.UES_BDMean)
            self.bhattacharyyaDegreeDisplay.lineGraph("Bhattacharyya Distance - Cumulative Degree Distribution", "Time Step", "Bhattacharyya Distance",multiLine=True)
            self.cumulativeDegreeDist.lineGraph("Cumulative Degree Distribution", "Degree (d)", "P(x >= d)")
            self.densityDisplay.lineGraph("Graph Density", "Time Step", "Graph Density", legloc="upper right",multiLine=True)
            self.avgShortestPathDisplay.lineGraph("Average Shortest Path Length", "Time Step", "Avg. Shortest Path",multiLine=True)
            self.avgClusteringDisplay.lineGraph("Average Clustering", "Time Step", "Average Clustering",legloc="upper right",multiLine=True)
            #attemptDataDisplay.lineGraph("Attempts", "Time", "Attempts") 