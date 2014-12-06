"""
NetworkFrames class.

"""
__author__ = """\n""".join(['Jeffrey Schmidt (jschmid1@binghamton.edu',
                            'Benjamin Bush (benjaminjamesbush@gmail.com)',
                            'Hiroki Sayama (sayama@binghamton.edu)'])

__all__ = ['readGraphML','readCompressedGraphML','addGraph',
           'writeDecompressedFrames','writeCompressedFrames',
           'compressNetworkFrames','decompressNetworkFrames',
           'getInputNetworks','getInputNetworkAt',
           'getExtractionSubgraphs','writeGraph','getStateName']


#    Copyright (C) 2012 by
#    Jeffrey Schmidt <jschmid1@binghamton.edu>
#    Benjamin Bush <benjaminjamesbush@gmail.com>
#    Hiroki Sayama <sayama@binghamton.edu>
#    All rights reserved.
#    BSD license.

import networkx as nx
import copy
import graphMLRead
import Display

class compressState:
    """ "Enum" Class used to indicate network changes between frames.
    """
    tag = 'compressState'
    none = 'None'
    added = 'Added'
    deleted = 'Deleted'
    stateChange = 'StateChanged'
    stateChangedTo = 'StateChangedTo'
    stateChangedFrom = 'StateChangedFrom'
    stateChangedName = 'StateChangedName'
    allStates = [none,added,deleted,stateChange,stateChangedFrom,stateChangedTo,stateChangedName]
    
class processState:
    """ 'Enum' Class used to indicate network statistics for individual nodes.
    """
    degree = 'degree'
    degreeIn = 'InDegree'
    degreeOut = 'OutDegree'
    cluster = 'ClusterCoefficient'
    closeness = 'ClosenessCentrality'
    betweenness = 'BetweennessCentrality'
    allStates = [degree,degreeIn,degreeOut,cluster,closeness,betweenness]

class NetworkFrames(object):
    def __init__(self):
        self.inputFrames = [] # List of graphs that have been added during simulation or read in from graphML
        self.stateName = None # String name of state used in input graph
        self.processedFrames = [] # List of graphs that the user has added with calculations performed on each frame and added to node states
        self.compressedFrames = [] # The compressed list of graphs that includes the initial graph and the subsequent differences
        self.extractionSubgraphs = [] # List of LHS (left hand side) subgraphs that turn into the full compressed frame 
        self.decompressedFrames = [] # The uncompressed list of graphs generated from decompressin the compressed frames
        self.graphML = nx.readwrite.graphml # The internal networkx graphML object
        self.frameKey = 0 # The frame key used to created unique graph id's for the inputNetwork graphs
        self.compressedFrameKey = 0  # The frame key used to created unique graph id's for the comressed graphs
        self.decompressedFrameKey = 0 # The frame key used to created unique graph id's for the decomressed graphs
        self.processedFrameKey = 0 # The frame key used to create unique graph id's for the processed graphs
        self.extractionSubgraphKey = 0 # The subgraph key used to create unique graph id's for the extraction subgraphs
        self.nodesAddedWhenEdgesData = Display.display(False)
        
    def readGraphML(self, path):
        """Reads a graphML file and stores the data in a list of networkx graph objects in
        self.inputFrames.

        Parameters
        ----------
        path : string path
           Path to the graphml file

        Returns
        -------
        None
        """
        self.inputFrames = graphMLRead.read_graphml(path)
        self._checkForStateName()
        
    def _checkForStateName(self):
        """Checks the nodes in the network to see if there is a state value used in the network and records it's name
        
        Parameters
        ----------
        None

        Returns
        -------
        None
        """        
        if len(self.inputFrames) > 0:
            count = 0
            while len(self.inputFrames[count].nodes()) == 0 and count < len(self.inputFrames):
                count += 1
            node = self.inputFrames[count].nodes()[0]
            if len(self.inputFrames[count].node[node]) > 0:
                # We do not support multiple states at the current time, so we will use the first state that we find.
                self.stateName = self.inputFrames[count].node[node].keys()[0]
                
    def getStateName(self):
        """Checks the nodes in the network to see if there is a state value used in the network and records it's name
                
       Parameters
       ----------
       None
    
       Returns
       -------
       stateName: string or None
       - The string name of the state used in the networks or returns None if no state is defined.
       """             
        return self.stateName
     
    def readCompressedGraphML(self, path):
        """Reads a graphML file and stores the data in a list of networkx graph objects in
        self.compressedFrames.

        Parameters
        ----------
        path : string path
           Path to the graphml file

        Returns
        -------
        void
        """
        self.compressedFrames = graphMLRead.read_graphml(path)
        
    def addGraph(self, graph):
        """Adds a networkx graph to an internal list giving each graph a unique numeric name.

        Parameters
        ----------
        graph : networkx graph
           The networkx graph object to append to the gna

        Returns
        -------
        None
        
        Example
        -------
        
        >>>myNetworkFrames = NetworkFrames.NetworkFrames()
        >>>G=networkx.erdos_renyi_graph(10,10)
        >>>myNetworkFrames.addGraph(G)
        >>>G1=networkx.erdos_renyi_graph(15,10)
        >>>myNetworkFrames.addGraph(G1)
        """
        #Reset the graphKey if the inputNetwork's length is 0
        if len(self.inputFrames) is 0:
            self.frameKey = 0
        
        newGraph = graph.copy()
        newGraph.name = str(self.frameKey)
        self.frameKey += 1
        self.inputFrames.append(newGraph)
    
    def setInputNetwork(self, inputNetwork):
        """Sets the input networkx graph list to the one passed in
        
                Parameters
                ----------
                list : networkx graphs
                   List of networkx graph objects
        
                Returns
                -------
                None
                
                Example
                -------
                
                >>>myNetworkFrames = NetworkFrames.NetworkFrames()
                >>>G=networkx.erdos_renyi_graph(10,10)
                >>>G1=networkx.erdos_renyi_graph(15,10)
                >>>graphList = [G, G1]
                >>>myNetworkFrames.setInputNetwork(graphList)
                """
        self.inputFrames = copy.deepcopy(inputNetwork)
        
    def _setCompressedFrames(self, compressedFrames):
        # Sets the compressed frames list to the list passed in
        self.compressedFrames = copy.deepcopy(compressedFrames)
        
    def _addProcessedFrame(self, graph):
        # Reset the graph key if the processedFrames' length is 0
        if len(self.processedFrames) is 0:
            self.processedFrameKey = 0
        newGraph = graph.copy()
        newGraph.name = str(self.processedFrameKey)
        self.processedFrameKey += 1
        self.processedFrames.append(newGraph)
        
    def _addCompressedFrame(self, graph):
        #Reset the graphKey if the compressedFrames' length is 0
        if len(self.compressedFrames) is 0:
            self.compressedFrameKey = 0
        
        newGraph = graph.copy()
        newGraph.name = str(self.compressedFrameKey)
        self.compressedFrameKey += 1
        self.compressedFrames.append(newGraph)
        
    def _addDecompressedFrame(self, graph):

        #Reset the graphKey if the compressedFrames's length is 0
        if len(self.decompressedFrames) is 0:
            self.decompressedFrameKey = 0
        
        newGraph = graph.copy()
        newGraph.name = str(self.decompressedFrameKey)
        self.decompressedFrameKey += 1
        self.decompressedFrames.append(newGraph)
        
    def _addExtractionSubgraph(self, graph):
        #Reset the graphKey if the compressedFrames's length is 0
        if len(self.extractionSubgraphs) is 0:
            self.extractionSubgraphKey = 0
        
        newGraph = graph.copy()
        newGraph.name = str(self.extractionSubgraphKey)
        self.extractionSubgraphKey += 1
        self.extractionSubgraphs.append(newGraph)
        
    def _clearCompressedFrameList(self):
        self.compressedFrames = []
        
    def _clearProcessedFrameList(self):
        self.processedFrames = []
        
    def writeGraphs(self, path):
        """Writes all of the graphs the GNA has accumulated through addGraph or through readGraphML to disk
        as a graphML file.

        Parameters
        ----------
        path : string path
           The file path and/or file name of the graphML output


        Returns
        -------
        void
        
        Example
        -------
        
        >>>myNetworkFrames = NetworkFrames.NetworkFrames()
        >>>G=networkx.erdos_renyi_graph(10,10)
        >>>myNetworkFrames.addGraph(G)
        >>>myNetworkFrames.writeGraphs('output.graphml')
        >>>myNetworkFrames.writeGraphs('C:\output.graphml')
        """
        f = open(path, 'w')
        writer = nx.readwrite.GraphMLWriter()
        writer.add_graphs(self.inputFrames)
        writer.dump(f)

    def writeSpecificGraphs(self, path, graphList):
            """Writes all of the graphs the GNA has accumulated through addGraph or through readGraphML to disk
            as a graphML file.
    
            Parameters
            ----------
            path : string path
               The file path and/or file name of the graphML output
               
            graphList : list of graphs
               The list of graphs to be written to file.  Default is the input frames.
    
            Returns
            -------
            void
            
            """
            f = open(path, 'w')
            writer = nx.readwrite.GraphMLWriter()
            writer.add_graphs(graphList)
            writer.dump(f)      

    def writeCompressedFrames(self,path):
        """Writes all of the compressed frames to a graphML file with the path specified

        Parameters
        ----------
        path : string path
           The file path and/or file name of the graphML output

        Returns
        -------
        void
        
        Example
        -------
        
        >>>myNetworkFrames = NetworkFrames.NetworkFrames()
        >>>myNetworkFrames.readGraphML('file.graphML;)
        >>>myNetworkFrames.compressNetworkFrames()
        >>>myNetworkFrames.writeCompressedFrames('compressed.graphML')
        """
        f = open(path, 'w')
        writer = nx.readwrite.GraphMLWriter()
        writer.add_graphs(self.compressedFrames)
        writer.dump(f)
        
    def writeDecompressedFrames(self,path):
        """Writes all of the compressed frames to a graphML file with the path specified

        Parameters
        ----------
        path : string path
           The file path and/or file name of the graphML output

        Returns
        -------
        void
        
        Example
        -------
        
        >>>myNetworkFrames = NetworkFrames.NetworkFrames()
        >>>myNetworkFrames.readGraphML('file.graphML;)
        >>>myNetworkFrames.compressNetworkFrames()
        >>>myNetworkFrames.writeCompressedFrames('compressed.graphML')
        """
        f = open(path, 'w')
        writer = nx.readwrite.GraphMLWriter()
        writer.add_graphs(self.decompressedFrames)
        writer.dump(f)
        
    def writeProcessedFrames(self,path):
        """Writes all of the processed frames to a graphML file with the path specified

        Parameters
        ----------
        path : string path
           The file path and/or file name of the graphML output

        Returns
        -------
        void
        
        Example
        -------
        
        >>>myNetworkFrames = NetworkFrames.NetworkFrames()
        >>>myNetworkFrames.readGraphML('file.graphML;)
        >>>myNetworkFrames.processNetworkFrames()
        >>>myNetworkFrames.writeProcessedFrames('processed.graphML')
        """
        f = open(path, 'w')
        writer = nx.readwrite.GraphMLWriter()
        writer.add_graphs(self.processedFrames)
        writer.dump(f)
        
    def getInputNetworks(self):
        """ Gets the current list of input network frames

        Returns
        -------
        inputNetwork : list(networkx.Graph())
           Returns a list of networkx graphs
        Example
        -------
        
        >>>myNetworkFrames = NetworkFrames.()
        >>>G=networkx.erdos_renyi_graph(10,10)
        >>>myNetworkFrames.addGraph(G)
        >>>G=networkx.erdos_renyi_graph(15,10)
        >>>myNetworkFrames.addGraph(G)
        >>>myNetworkFrames.getInputNetwork()
        [<networkx.classes.graph.Graph object at 0x0000000002E88940>, <networkx.classes.graph.Graph object at 0x0000000002E88CC0>]
        """
        return self.inputFrames
    
    def _getCompressedNetworks(self):
        """ *** Internal Use Only***
        Gets the current list of compressed network frames 
        """     
        return self.compressedFrames
    
    def getDecompressedFrames(self):
        """ Gets the current list of decompressed network frames

        Returns
        -------
        inputNetwork : list(networkx.Graph())
           Returns a list of networkx graphs
        Example
        -------
        
        >>>myNetworkFrames = NetworkFrames.()
        >>>G=networkx.erdos_renyi_graph(10,10)
        >>>myNetworkFrames.addGraph(G)
        >>>G=networkx.erdos_renyi_graph(15,10)
        >>>myNetworkFrames.addGraph(G)
        >>>myNetworkFrames.compressNetworkFrames()
        >>>myNetworkFrames.decompressNetworkFrames()
        >>>myNetworkFrames.getDecompressedFrames()
        [<networkx.classes.graph.Graph object at 0x0000000002E88940>, <networkx.classes.graph.Graph object at 0x0000000002E88CC0>]
        """
        return self.decompressedFrames
    
    def getExtractionSubgraphs(self):
        """ Gets the list of extraction subgraphs
        
        Returns
        -------
        extractionSubgraphs : list (networkx.graph())
          - A list of networkx graphs
        
        """
        return self.extractionSubgraphs
    
    def clearInputNetworks(self):
        """Clears the inputNetowork list of networkx graphs in the NetworkFrames object.

        Parameters
        ----------
        void

        Returns
        -------
        void
        """
        self.inputFrames = []
        
    def getInputNetworkAt(self, index):
        """ Gets an input network frame at the index value passed in.
        
        Parameters
        ----------
        index : integer index
        
        Returns
        ----------
        The network frame at the index passed into the method.  The frame returned is a deep copy of the 
        frame in the inputFrame list.
        
        """
        if index >= 0 and index < len(self.inputFrames):
            return copy.deepcopy(self.inputFrames[index])
        else:
            raise KeyError('Invalid index value')
        
    def _getCompressedNetworkAt(self, index):
        """ Gets a compressed network frame at the index value passed in.
        
        Parameters
        ----------
        index : integer index
        
        Returns
        ----------
        The network frame at the index passed into the method.  The frame returned is a deep copy of the 
        frame in the compressedFrame list.
        
        """
        if index >= 0 and index < len(self.compressedFrames):
            return copy.deepcopy(self.compressedFrames[index])
        else:
            raise KeyError('Invalid index value')
        
    def _getDecompressedNetworkAt(self, index):
        """ Gets a decompressed network frame at the index value passed in.
        
        Parameters
        ----------
        index : integer index
        
        Returns
        ----------
        The network frame at the index passed into the method.  The frame returned is a deep copy of the 
        frame in the decompressedFrame list.
        
        """
        if index >= 0 and index < len(self.decompressedFrames):
            return copy.deepcopy(self.decompressedFrames[index])
        else:
            raise KeyError('Invalid index value')
    def _getProcessedNetworkAt(self, index):
        """ Gets a processed network frame at the index value passed in.
        
        Parameters
        ----------
        index : integer index
        
        Returns
        ----------
        The network frame at the index passed into the method.  The frame returned is a deep copy of the 
        frame in the processedFrames list.
        
        """
        if index >= 0 and index < len(self.processedFrames):
            return copy.deepcopy(self.processedFrames[index])
        else:
            raise KeyError('Invalid index value')
        
    def _getExtractionSubgraphAt(self, index):
        """ Gets an extraction subgraph at the index value passed in.
        
        Parameters
        ----------
        index : integer index
        
        Returns
        ----------
        The network frame at the index passed into the method.  The subgraph returned is a deep copy of the 
        subgraph in the extractionSubgraphs list.
        
        """
        if index >= 0 and index < len(self.extractionSubgraphs):
            return copy.deepcopy(self.extractionSubgraphs[index])
        else:
            raise KeyError('Invalid index value')
        
    def compressNetworkFrames(self,processed=False):
        """ Compresses the inputFrames into a list of NetworkX graph objects such that each new frame only
        includes the changes from the previous frame.  This is used prepare the data for input into a GNA
        instance.
        
        Current assumptions:
          - All nodes in the graphs have the same number of state types
          - All of the state types have the same value type
          - Edge properties are not considered
          
          Parameters
        ----------
        processed : boolean
         - The parameter controls the source of the compression.  Default is the processed data.
        
        Returns
        ----------
        None
          
        """
        
        loopNetwork = None
        if processed:
            loopNetwork = self.processedFrames
        else:
            loopNetwork = self.inputFrames
            
        # If we have at least two network frames
        if (len(loopNetwork) > 1):
            self._clearCompressedFrameList()
            # Add the initial network, i.e., first frame, to the compressed frames list
            self.compressedFrames.append(loopNetwork[0])
            pastFrame = 0
            currentFrame = 1
            # Loop over all frames
            while currentFrame < len(loopNetwork):
                pastGraph = loopNetwork[pastFrame]
                currentGraph = loopNetwork[currentFrame]
                compressedGraph = nx.DiGraph() if pastGraph.is_directed() else nx.Graph()
                # Check nodes for state changes and for additions
                for checkNode in currentGraph.nodes():
                    # If checkNode is in past graph check for state changes
                    if checkNode in pastGraph.node:
                        # Loop over all states
                        stateSame = True
                        stateName = ''
                        for states in currentGraph.node[checkNode]:
                            # If node has a different state set
                            if states not in processState.allStates:
                                if not currentGraph.node[checkNode][states] == pastGraph.node[checkNode][states]:
                                    stateName= states
                                    stateSame = False
                        if not stateSame:
                            addNode = copy.deepcopy(currentGraph.node[checkNode])
                            addNode[compressState.tag] = compressState.stateChange
                            addNode[compressState.stateChangedFrom] = pastGraph.node[checkNode][stateName]
                            addNode[compressState.stateChangedTo] = currentGraph.node[checkNode][stateName]
                            addNode[compressState.stateChangedName] = stateName
                            compressedGraph.add_node(checkNode,addNode)
                    # If node doesn't exist in pastGraph a new node was added to currentGraph
                    else:
                        addNode = copy.deepcopy(currentGraph.node[checkNode])
                        addNode[compressState.tag] = compressState.added
                        compressedGraph.add_node(checkNode,addNode)
                # Check nodes for deletions
                for checkNode in pastGraph.nodes():
                    # If node doesn't exist in the current graph, it was deleted
                    if checkNode not in currentGraph.node:
                        addNode = copy.deepcopy(pastGraph.node[checkNode])
                        addNode[compressState.tag] = compressState.deleted
                        compressedGraph.add_node(checkNode,addNode)
                        
                # Check edges for additions
                for checkEdge in currentGraph.edges():
                    start = checkEdge[0]
                    end = checkEdge[1]
                    if start not in pastGraph.edge or end not in pastGraph.edge[start]:
                        # If the nodes don't exist add them to the compressed graph
                        if start not in compressedGraph.node:
                            addNode = copy.deepcopy(currentGraph.node[start])
                            addNode[compressState.tag] = compressState.none
                            compressedGraph.add_node(start,addNode)
                        if end not in compressedGraph.node:
                            addNode = copy.deepcopy(currentGraph.node[end])
                            addNode[compressState.tag] = compressState.none
                            compressedGraph.add_node(end,addNode)
                        # Add the edge to the compressed graph
                        compressedGraph.add_edge(start, end,compressState=compressState.added)
                        
                # Check edges for deletions
                for checkEdge in pastGraph.edges():
                    start = checkEdge[0]
                    end = checkEdge[1]
                    if start not in currentGraph.edge or end not in currentGraph.edge[start]:
                        # If the nodes don't exist add them to the compressed graph
                        if start not in compressedGraph.node:
                            addNode = copy.deepcopy(pastGraph.node[start])
                            addNode[compressState.tag] = compressState.none
                            compressedGraph.add_node(start, addNode)
                        if end not in compressedGraph.node:
                            addNode = copy.deepcopy(pastGraph.node[end])
                            addNode[compressState.tag] = compressState.none
                            compressedGraph.add_node(end, addNode)
                        # Add the edge to the compressed graph
                        compressedGraph.add_edge(start, end, compressState=compressState.deleted)
                        
                # Check to see if there are unchanging edges.
                for checkEdge in pastGraph.edges():
                    start = checkEdge[0]
                    end = checkEdge[1]
                    if (start in currentGraph.edge and end in currentGraph.edge[start]) and \
                       (start not in compressedGraph.edge or end not in compressedGraph.edge[start]) and \
                       start in compressedGraph.node and \
                       end in compressedGraph.node:
                        compressedGraph.add_edge(start, end, compressState=compressState.none)
                        
                # Add the compressed graph to the internal list
                self._addCompressedFrame(compressedGraph)
                pastFrame += 1
                currentFrame += 1
                
    
    def decrompressNetworkFrames(self):
        """ Decompresses the compressed frames back into the original format of a list of networkX graphs
        
        """
        if len(self.compressedFrames) > 1:
            # Clear the decompressed frame list
            self.decompressedFrames = []
            # Add the first frame to the decompressed list
            self._addDecompressedFrame(self._getCompressedNetworkAt(0))
            focusFrame = self._getDecompressedNetworkAt(0)
            frameIndex = 1
            while frameIndex < len(self.compressedFrames):
                # Get the compressed frame at the frameIndex
                changeFrame = self._getCompressedNetworkAt(frameIndex)
                
                # Decompress this changeFrame
                self._decompress(focusFrame, changeFrame)
                            
                # Add this uncompressed snapshot to the decompressed list
                self._addDecompressedFrame(focusFrame)
                frameIndex += 1
        
    def _decompress(self, focusFrame, changeFrame):
        """ Decompression function that takes the compressed graph: changeFrame, and "unpacks" it
        into the focusFrame.
        """
        # Loop over the nodes in the compressed frame
        for nodes in changeFrame.nodes():
            change = changeFrame.node[nodes].pop(compressState.tag)
            # If the change state is 'Added', add node
            if change == compressState.added:
                addNode = nodes
                if nodes in focusFrame.nodes():
                    addNode = max(focusFrame.nodes())+1
                    while addNode in changeFrame.nodes():
                        addNode+=1
                    updateMap = {nodes:addNode}
                    focusFrame.add_node(addNode, changeFrame.node[nodes])
                    changeFrame = nx.relabel_nodes(changeFrame,updateMap)
                else:
                    focusFrame.add_node(addNode, changeFrame.node[nodes])
            # If the change state is 'Deleted', delete node
            elif change == compressState.deleted:
                focusFrame.remove_node(nodes)
            # If the change state is 'StateChanged', update with changed state
            elif change == compressState.stateChange:
                stateName = changeFrame.node[nodes][compressState.stateChangedName]
                assert (focusFrame.node[nodes][stateName] == changeFrame.node[nodes][compressState.stateChangedFrom])
                focusFrame.node[nodes][stateName] = changeFrame.node[nodes][compressState.stateChangedTo]

        # Loop over the edges in the compressed frame
        for edges in changeFrame.edges():
            # Extract start and end nodes for the edge
            start = edges[0]
            end = edges[1]
            change = changeFrame.edge[start][end].pop(compressState.tag)
            # Was this edge added
            if change == compressState.added:
                focusFrame.add_edge(start,end)
            # Or was it deleted
            elif change == compressState.deleted:
                # If it was deleted check to make sure the deletion of the nodes didn't already
                # clean the edges
                if start in focusFrame.edge and end in focusFrame.edge[start]:
                    focusFrame.remove_edge(start,end)
                    
    def processNetworkFrames(self):
        """ Processes the input frams adding network statistics to the nodes.
          
        Parameters
        ----------
        None
        
        Returns
        ----------
        None
          
        """
        currentFrame = 0
        # Loop over all frames
        while currentFrame < len(self.inputFrames):
            processedGraph = self.getInputNetworkAt(currentFrame)
            degree = processedGraph.degree()
            if processedGraph.is_directed():
                inDegreeCentrality = processedGraph.in_degree()
                outDegreeCentrality = processedGraph.out_degree()
            else:
                clusterCoefficient = nx.cluster.clustering(processedGraph)
            betweennessCentrality = nx.betweenness_centrality(processedGraph,normalized=False)
            closenessCentrality = nx.closeness.closeness_centrality(processedGraph,normalized=False)
            numNodes = 0
            while numNodes < len(processedGraph.nodes()):
                node = processedGraph.nodes()[numNodes]
                processedGraph.node[node][processState.degree] = degree[node]
                if processedGraph.is_directed():
                    processedGraph.node[node][processState.degreeIn] = inDegreeCentrality[node]
                    processedGraph.node[node][processState.degreeOut] = outDegreeCentrality[node]
                else:
                    processedGraph.node[node][processState.cluster] = clusterCoefficient[node]
                processedGraph.node[node][processState.closeness] = closenessCentrality[node]
                processedGraph.node[node][processState.betweenness] = betweennessCentrality[node]
                numNodes += 1
                
            self._addProcessedFrame(processedGraph)
            currentFrame += 1
    
    def getNumNodesAdded(self, network):
        nodesAdded = 0
        for nodes in network.nodes():
            if compressState.tag in network.node[nodes]:
                change = network.node[nodes][compressState.tag]
                if change == compressState.added:
                    nodesAdded += 1

        return nodesAdded
    
    def getNumEdgesAdded(self, network):
        edgesAdded = 0

        for edges in network.edges():
            # Extract start and end nodes for the edge
            start = edges[0]
            end = edges[1]
            if compressState.tag in network.edge[start][end]:
                change = network.edge[start][end][compressState.tag]
                if change == compressState.added:
                    edgesAdded += 1

                    
        return edgesAdded
    
    def displayData(self):
        self.nodesAddedWhenEdgesData.lineGraphCompare("Nodes Added When Edges Added", "Time Step", "Num Nodes Added")
            
    
if __name__ == "__main__":
    import time
    start = time.clock()
    test = NetworkFrames()
    test.readGraphML('digraph.graphML')
    print "Read time - " + str(time.clock() - start)
    start = time.clock()
    test.compressNetworkFrames()
    print "Copmpress time - " + str(time.clock() - start)
    start = time.clock()
    test.writeCompressedFrames('compressed.graphML')
    print "Write Compressed Frames time - " + str(time.clock() - start)
    start = time.clock()
    test.decrompressNetworkFrames()
    print "Decompress Frames time - " + str(time.clock() - start)
    start = time.clock()
    test.writeDecompressedFrames('decompressed.graphML')
    print "Write Decompressed Frames time - " + str(time.clock() - start)