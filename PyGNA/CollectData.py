"""
Data collection class.

"""
__author__ = """\n""".join(['Jeffrey Schmidt (jschmid1@binghamton.edu',
                            'Benjamin Bush (benjaminjamesbush@gmail.com)',
                            'Hiroki Sayama (sayama@binghamton.edu)'])

__all__ = ['nodesVSedges','nodesVSdiameter','dynamicsInfo','movingAverage']


#    Copyright (C) 2012 by
#    Jeffrey Schmidt <jschmid1@binghamton.edu>
#    Benjamin Bush <benjaminjamesbush@gmail.com>
#    Hiroki Sayama <sayama@binghamton.edu>
#    All rights reserved.
#    BSD license.

import networkx as nx
import NetworkFrames
import Display
import scipy

class CollectData(object):
    
    def __init__(self, observed, experimental):
        self.observedData = observed
        self.experimentalData = experimental
        
    def nodesVSedges(self):
        displayOutput = Display.display(True)
        
        count = 0
        while count < len(self.observedData ):
            network = self.observedData [count]
            displayOutput.addInputValues(network.number_of_nodes(), network.number_of_edges())
            count += 1
        
        count = 0
        while count < len(self.experimentalData):
            network = self.experimentalData[count]
            displayOutput.addExperimentalValues(network.number_of_nodes(), network.number_of_edges())
            count += 1
            
        displayOutput.loglogPlot("Nodes vs. Edges", "Num Nodes", "Num Edges")
        
    def nodesVSdiameter(self):
        displayOutput = Display.display(True)
                
        count = 0
        while count < len(self.observedData ):
            network = self.observedData [count]
            displayOutput.addInputValues(network.number_of_nodes(), nx.diameter(network))
            count += 1
        
        count = 0
        while count < len(self.experimentalData):
            network = self.experimentalData[count]
            displayOutput.addExperimentalValues(network.number_of_nodes(), nx.diameter(network))
            count += 1        
        
        displayOutput.show("Nodes vs. Diameter", "Num Nodes", "Diameter")
        
    def dynamicsInfo(self):
        displayNodesOutput = Display.display(True)
        displayEdgesOutput = Display.display(True)
        
        count = 0
        while count < len(self.observedData):
            network = self.observedData[count]
            nodesAdded = 0
            nodesDeleted = 0
            for nodes in network.nodes():
                if NetworkFrames.compressState.tag in network.node[nodes]:
                    change = network.node[nodes][NetworkFrames.compressState.tag]
                    if change == NetworkFrames.compressState.added:
                        nodesAdded += 1
                    if change == NetworkFrames.compressState.deleted:
                        nodesDeleted += 1
            edgesAdded = 0
            edgesDeleted = 0
            for edges in network.edges():
                # Extract start and end nodes for the edge
                start = edges[0]
                end = edges[1]
                if NetworkFrames.compressState.tag in network.edge[start][end]:
                    change = network.edge[start][end][NetworkFrames.compressState.tag]
                    if change == NetworkFrames.compressState.added:
                        edgesAdded += 1
                    if change == NetworkFrames.compressState.deleted:
                        edgesDeleted += 1
            displayNodesOutput.addInputValue(nodesAdded, nodesDeleted)
            displayEdgesOutput.addInputValue(edgesAdded, edgesDeleted)
            count += 1
            
        count = 0
        while count < len(self.experimentalData):
            network = self.experimentalData[count]
            nodesAdded = 0
            nodesDeleted = 0
            for nodes in network.nodes():
                if NetworkFrames.compressState.tag in network.node[nodes]:
                    change = network.node[nodes][NetworkFrames.compressState.tag]
                    if change == NetworkFrames.compressState.added:
                        nodesAdded += 1
                    if change == NetworkFrames.compressState.deleted:
                        nodesDeleted += 1
            edgesAdded = 0
            edgesDeleted = 0
            for edges in network.edges():
                # Extract start and end nodes for the edge
                start = edges[0]
                end = edges[1]
                if NetworkFrames.compressState.tag in network.edge[start][end]:
                    change = network.edge[start][end][NetworkFrames.compressState.tag]
                    if change == NetworkFrames.compressState.added:
                        edgesAdded += 1
                    if change == NetworkFrames.compressState.deleted:
                        edgesDeleted += 1
            displayNodesOutput.addExperimentalValue(nodesAdded, nodesDeleted)
            displayEdgesOutput.addExperimentalValue(edgesAdded, edgesDeleted)
            count += 1            
                
        displayDifference = Display.display(False)
        
        count = 0
        while count < len(displayEdgesOutput.yInputValues):
            displayDifference.addInputValue(abs(displayEdgesOutput.yInputValues[count] - displayEdgesOutput.yExperimentalValues[count]))
            count += 1
            
        #displayNodesOutput.lineGraphCompare("Node Dynamics", "Time Step", "Nodes Added", "Nodes Deleted")
        displayEdgesOutput.lineGraphCompare("Edge Dynamics", "Time Step", "Edges Added", "Edges Deleted")
        displayEdgesOutput.histogramCompare("Edges Added per Time Step", "Num. Edges Added","Count")
        displayNodesOutput.histogramCompare("Nodes Added per Time Step", "Num. Nodes Added", "Count")
        displayDifference.histogramCompare("Absolute Difference in Number of Edges Added per Time Step", "Edge Difference", "Count")
        self.movingAverage("Moving Average of Edges Added", "Time Step", "Avg. Edges Added", displayEdgesOutput, 25,True)
        
    def movingAverage(self, title, xValueLabel, yValueLabel, displayData, movingAverageSize, compare=False):
        
        if compare:
            assert(len(displayData.yInputValues) == len(displayData.yExperimentalValues))
        assert(movingAverageSize <= len(displayData.yInputValues))
        
        displayMovingAverage = Display.display(compare)
        
        index = 0
        while index + movingAverageSize < len(displayData.yInputValues):
            observedArray = []
            experimentalArray = []
            count = 0
            while count < movingAverageSize:
                observedArray.append(displayData.yInputValues[count+index])
                if compare:
                    experimentalArray.append(displayData.yExperimentalValues[count+index])
                count += 1
            
            displayMovingAverage.addInputValue(scipy.average(observedArray))
            if compare:
                displayMovingAverage.addExperimentalValue(scipy.average(experimentalArray))
            
            index += 1
            
        displayMovingAverage.lineGraph(title, xValueLabel, yValueLabel, "None")
        