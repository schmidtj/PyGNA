"""
NetworkFrames class.

"""
__author__ = """\n""".join(['Jeffrey Schmidt (jschmid1@binghamton.edu',
                            'Benjamin Bush (benjaminjamesbush@gmail.com)',
                            'Hiroki Sayama (sayama@binghamton.edu)'])

__all__ = ['readGraphML', 'readCompressedGraphML', 'addGraph',
           'writeDecompressedFrames', 'writeCompressedFrames',
           'compressNetworkFrames', 'decompressNetworkFrames',
           'getInputNetworks', 'getInputNetworkAt',
           'getExtractionSubgraphs', 'writeGraph', 'getStateName']


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
    allStates = [none, added, deleted, stateChange, stateChangedFrom, stateChangedTo, stateChangedName]
    
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
        self.inputFrames = []  # List of graphs that have been added during simulation or read in from graphML
        self.stateName = None  # String name of state used in input graph
        self.processedFrames = []  # List of graphs that the user has added with calculations performed on each frame
        self.compressedFrames = []  # The compressed list of graphs with the initial graph and the subsequent differences
        self.extractionSubgraphs = []  # List of LHS (left hand side) subgraphs that turn into the full compressed frame
        self.decompressedFrames = []  # The uncompressed list of graphs generated from decompressing the compressed frames
        self.graphML = nx.readwrite.graphml  # The internal networkx graphML object
        self.frameKey = 0  # The frame key used to created unique graph id's for the inputNetwork graphs
        self.compressedFrameKey = 0  # The frame key used to created unique graph id's for the compressed graphs
        self.decompressedFrameKey = 0  # The frame key used to created unique graph id's for the decompressed graphs
        self.processedFrameKey = 0  # The frame key used to create unique graph id's for the processed graphs
        self.extractionSubgraphKey = 0  # The subgraph key used to create unique graph id's for the extraction subgraphs
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
        
        new_graph = graph.copy()
        new_graph.name = str(self.frameKey)
        self.frameKey += 1
        self.inputFrames.append(new_graph)
    
    def setInputNetwork(self, input_network):
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
        self.inputFrames = copy.deepcopy(input_network)
        self._checkForStateName()
        
    def _setCompressedFrames(self, compressed_frames):
        # Sets the compressed frames list to the list passed in
        self.compressedFrames = copy.deepcopy(compressed_frames)
        
    def _addProcessedFrame(self, graph):
        # Reset the graph key if the processedFrames' length is 0
        if len(self.processedFrames) is 0:
            self.processedFrameKey = 0
        new_graph = graph.copy()
        new_graph.name = str(self.processedFrameKey)
        self.processedFrameKey += 1
        self.processedFrames.append(new_graph)
        
    def _addCompressedFrame(self, graph):
        #Reset the graphKey if the compressedFrames' length is 0
        if len(self.compressedFrames) is 0:
            self.compressedFrameKey = 0
        
        new_graph = graph.copy()
        new_graph.name = str(self.compressedFrameKey)
        self.compressedFrameKey += 1
        self.compressedFrames.append(new_graph)
        
    def _addDecompressedFrame(self, graph):

        #Reset the graphKey if the compressedFrames's length is 0
        if len(self.decompressedFrames) is 0:
            self.decompressedFrameKey = 0
        
        new_graph = graph.copy()
        new_graph.name = str(self.decompressedFrameKey)
        self.decompressedFrameKey += 1
        self.decompressedFrames.append(new_graph)
        
    def _addExtractionSubgraph(self, graph):
        #Reset the graphKey if the compressedFrames's length is 0
        if len(self.extractionSubgraphs) is 0:
            self.extractionSubgraphKey = 0
        
        new_graph = graph.copy()
        new_graph.name = str(self.extractionSubgraphKey)
        self.extractionSubgraphKey += 1
        self.extractionSubgraphs.append(new_graph)
        
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

    def writeSpecificGraphs(self, path, graph_list):
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
            writer.add_graphs(graph_list)
            writer.dump(f)      

    def writeCompressedFrames(self, path):
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
        >>>myNetworkFrames.readGraphML('file.graphML')
        >>>myNetworkFrames.compressNetworkFrames()
        >>>myNetworkFrames.writeCompressedFrames('compressed.graphML')
        """
        f = open(path, 'w')
        writer = nx.readwrite.GraphMLWriter()
        writer.add_graphs(self.compressedFrames)
        writer.dump(f)
        
    def writeDecompressedFrames(self, path):
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
        >>>myNetworkFrames.readGraphML('file.graphML')
        >>>myNetworkFrames.compressNetworkFrames()
        >>>myNetworkFrames.writeCompressedFrames('compressed.graphML')
        """
        f = open(path, 'w')
        writer = nx.readwrite.GraphMLWriter()
        writer.add_graphs(self.decompressedFrames)
        writer.dump(f)
        
    def writeProcessedFrames(self, path):
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
        >>>myNetworkFrames.readGraphML('file.graphML')
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
        
    def getInputNetworkAt(self, index, deepcopy=True):
        """ Gets an input network frame at the index value passed in.
        
        Parameters
        ----------
        index : integer index
        
        Returns
        ----------
        The network frame at the index passed into the method.  The frame returned is a deep copy of the 
        frame in the inputFrame list.
        
        """
        if 0 <= index < len(self.inputFrames):
            if deepcopy:
                return copy.deepcopy(self.inputFrames[index])
            else:
                return self.inputFrames[index]
        else:
            raise KeyError('Invalid index value')
        
    def _getCompressedNetworkAt(self, index, deepcopy=True):
        """ Gets a compressed network frame at the index value passed in.
        
        Parameters
        ----------
        index : integer index
        
        Returns
        ----------
        The network frame at the index passed into the method.  The frame returned is a deep copy of the 
        frame in the compressedFrame list.
        
        """
        if 0 <= index < len(self.compressedFrames):
            if deepcopy:
                return copy.deepcopy(self.compressedFrames[index])
            else:
                return self.compressedFrames[index]
        else:
            raise KeyError('Invalid index value')
     
    def getNumberOfChanges(self, index):
        network = self._getCompressedNetworkAt(index, False)
        changes = 0
        for node in network.nodes_iter():
            if compressState.added in network.node[node][compressState.tag] or \
               compressState.deleted in network.node[node][compressState.tag] or \
               compressState.stateChange in network.node[node][compressState.tag]:
                changes += 1
                
        for edge in network.edges_iter():
            start = edge[0]
            end = edge[1]
            if compressState.added in network.edge[start][end][compressState.tag] or \
               compressState.deleted in network.edge[start][end][compressState.tag] or \
               compressState.stateChange in network.edge[start][end][compressState.tag]:
                changes += 1
         
        return changes
    
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
        if 0 <= index < len(self.decompressedFrames):
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
        if 0 <= index < len(self.processedFrames):
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
        if 0 <= index < len(self.extractionSubgraphs):
            return copy.deepcopy(self.extractionSubgraphs[index])
        else:
            raise KeyError('Invalid index value')
        
    def compressNetworkFrames(self, processed=False):
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
        
        loop_network = None
        if processed:
            loop_network = self.processedFrames
        else:
            loop_network = self.inputFrames
            
        # If we have at least two network frames
        if len(loop_network) > 1:
            self._clearCompressedFrameList()
            # Add the initial network, i.e., first frame, to the compressed frames list
            self.compressedFrames.append(loop_network[0])
            past_frame = 0
            current_frame = 1
            # Loop over all frames
            while current_frame < len(loop_network):
                past_graph = loop_network[past_frame]
                current_graph = loop_network[current_frame]
                compressed_graph = nx.DiGraph() if past_graph.is_directed() else nx.Graph()
                # Check nodes for state changes and for additions
                for checkNode in current_graph.nodes_iter():
                    # If checkNode is in past graph check for state changes
                    if checkNode in past_graph.node:
                        # Loop over all states
                        state_same = True
                        state_name = ''
                        for states in current_graph.node[checkNode]:
                            # If node has a different state set
                            if states not in processState.allStates:
                                if not current_graph.node[checkNode][states] == past_graph.node[checkNode][states]:
                                    state_name = states
                                    state_same = False
                        if not state_same:
                            add_node = copy.deepcopy(current_graph.node[checkNode])
                            add_node[compressState.tag] = compressState.stateChange
                            add_node[compressState.stateChangedFrom] = past_graph.node[checkNode][state_name]
                            add_node[compressState.stateChangedTo] = current_graph.node[checkNode][state_name]
                            add_node[compressState.stateChangedName] = state_name
                            compressed_graph.add_node(checkNode, add_node)
                    # If node doesn't exist in pastGraph a new node was added to currentGraph
                    else:
                        add_node = copy.deepcopy(current_graph.node[checkNode])
                        add_node[compressState.tag] = compressState.added
                        compressed_graph.add_node(checkNode, add_node)
                # Check nodes for deletions
                for checkNode in past_graph.nodes_iter():
                    # If node doesn't exist in the current graph, it was deleted
                    if checkNode not in current_graph.node:
                        add_node = copy.deepcopy(past_graph.node[checkNode])
                        add_node[compressState.tag] = compressState.deleted
                        compressed_graph.add_node(checkNode, add_node)
                 
                # Check edges for additions
                for checkEdge in current_graph.edges_iter():
                    start = checkEdge[0]
                    end = checkEdge[1]
                    if start not in past_graph.edge or end not in past_graph.edge[start]:
                        # If the nodes don't exist add them to the compressed graph
                        if start not in compressed_graph.node:
                            add_node = copy.deepcopy(current_graph.node[start])
                            add_node[compressState.tag] = compressState.none
                            compressed_graph.add_node(start, add_node)
                        if end not in compressed_graph.node:
                            add_node = copy.deepcopy(current_graph.node[end])
                            add_node[compressState.tag] = compressState.none
                            compressed_graph.add_node(end, add_node)
                        edge_data = copy.deepcopy(current_graph.edge[start][end])
                        edge_data[compressState.tag] = compressState.added
                        # Add the edge to the compressed graph
                        compressed_graph.add_edge(start, end, edge_data)
                    #Check for state change
                    elif start in past_graph.edge and end in past_graph.edge[start] and \
                         start in current_graph.edge and end in current_graph[start]:
                        for states in past_graph[start][end]:
                            if states in current_graph[start][end] and current_graph[start][end][states] != past_graph[start][end][states]:
                                add_edge = copy.deepcopy(past_graph.edge[start][end])
                                add_edge[compressState.tag] = compressState.stateChange
                                add_edge[compressState.stateChangedFrom] = past_graph.edge[start][end][states]
                                add_edge[compressState.stateChangedTo] = current_graph.edge[start][end][states]
                                add_edge[compressState.stateChangedName] = states
                                compressed_graph.add_edge(start, end, add_edge)
                                if compressed_graph.node[start] == {}:
                                    compressed_graph.node[start][compressState.tag] = compressState.none
                                if compressed_graph.node[end] == {}:
                                    compressed_graph.node[end][compressState.tag] = compressState.none
                        
                # Check edges for deletions
                for checkEdge in past_graph.edges_iter():
                    start = checkEdge[0]
                    end = checkEdge[1]
                    if start not in current_graph.edge or end not in current_graph.edge[start]:
                        # If the nodes don't exist add them to the compressed graph
                        if start not in compressed_graph.node:
                            add_node = copy.deepcopy(past_graph.node[start])
                            add_node[compressState.tag] = compressState.none
                            compressed_graph.add_node(start, add_node)
                        if end not in compressed_graph.node:
                            add_node = copy.deepcopy(past_graph.node[end])
                            add_node[compressState.tag] = compressState.none
                            compressed_graph.add_node(end, add_node)
                        # Add the edge to the compressed graph
                        edge_data = copy.deepcopy(past_graph.edge[start][end])
                        edge_data[compressState.tag] = compressState.deleted
                        compressed_graph.add_edge(start, end, edge_data)
                        
                # Check to see if there are unchanging edges.
                for checkEdge in past_graph.edges_iter():
                    start = checkEdge[0]
                    end = checkEdge[1]
                    if (start in current_graph.edge and end in current_graph.edge[start]) and \
                       (start not in compressed_graph.edge or end not in compressed_graph.edge[start]) and \
                       start in compressed_graph.node and \
                       end in compressed_graph.node:
                        edgedata = copy.deepcopy(past_graph.edge[start][end])
                        edgedata[compressState.tag] = compressState.none
                        compressed_graph.add_edge(start, end, edgedata)
                        
                # Add the compressed graph to the internal list
                self._addCompressedFrame(compressed_graph)
                past_frame += 1
                current_frame += 1
                
    
    def decrompressNetworkFrames(self):
        """ Decompresses the compressed frames back into the original format of a list of networkX graphs
        
        """
        if len(self.compressedFrames) > 1:
            # Clear the decompressed frame list
            self.decompressedFrames = []
            # Add the first frame to the decompressed list
            self._addDecompressedFrame(self._getCompressedNetworkAt(0))
            focus_frame = self._getDecompressedNetworkAt(0)
            frame_index = 1
            while frame_index < len(self.compressedFrames):
                # Get the compressed frame at the frameIndex
                change_frame = self._getCompressedNetworkAt(frame_index)
                
                # Decompress this changeFrame
                self._decompress(focus_frame, change_frame)
                            
                # Add this uncompressed snapshot to the decompressed list
                self._addDecompressedFrame(focus_frame)
                frame_index += 1
        
    def _decompress(self, focus_frame, change_frame):
        """ Decompression function that takes the compressed graph: changeFrame, and "unpacks" it
        into the focusFrame.
        """
        # Loop over the nodes in the compressed frame
        for nodes in change_frame.nodes_iter():
            change = change_frame.node[nodes].pop(compressState.tag)
            # If the change state is 'Added', add node
            if change == compressState.added:
                add_node = nodes
                if nodes in focus_frame.nodes_iter():
                    add_node = max(focus_frame.nodes())+1
                    while add_node in change_frame.node:
                        add_node += 1
                    update_map = {nodes: add_node}
                    focus_frame.add_node(add_node, change_frame.node[nodes])
                    change_frame = nx.relabel_nodes(change_frame, update_map)
                else:
                    focus_frame.add_node(add_node, change_frame.node[nodes])
            # If the change state is 'Deleted', delete node
            elif change == compressState.deleted:
                focus_frame.remove_node(nodes)
            # If the change state is 'StateChanged', update with changed state
            elif change == compressState.stateChange:
                state_name = change_frame.node[nodes][compressState.stateChangedName]
                assert (focus_frame.node[nodes][state_name] == change_frame.node[nodes][compressState.stateChangedFrom])
                focus_frame.node[nodes][state_name] = change_frame.node[nodes][compressState.stateChangedTo]
        
        processed = []
        # Loop over the edges in the compressed frame
        for edges in change_frame.edges_iter():
            # Extract start and end nodes for the edge
            start = edges[0]
            end = edges[1]
            change = change_frame.edge[start][end].pop(compressState.tag)
            
            #skip undirected edges that have already been changed
            if not nx.is_directed(focus_frame) and (end, start) in processed:
                continue
            
            # Was this edge added
            if change == compressState.added:
                focus_frame.add_edge(start, end, change_frame.edge[start][end])
            # Or was it deleted
            elif change == compressState.deleted:
                # If it was deleted check to make sure the deletion of the nodes didn't already
                # clean the edges
                if start in focus_frame.edge and end in focus_frame.edge[start]:
                    focus_frame.remove_edge(start, end)
                    # If the change state is 'StateChanged', update with changed state
            elif change == compressState.stateChange:
                state_name = change_frame.edge[start][end][compressState.stateChangedName]
                assert (focus_frame.edge[start][end][state_name] == change_frame.edge[start][end][compressState.stateChangedFrom])
                focus_frame.edge[start][end][state_name] = change_frame.edge[start][end][compressState.stateChangedTo]
            processed.append((start, end))
                    
    def processNetworkFrames(self):
        """ Processes the input frams adding network statistics to the nodes.
          
        Parameters
        ----------
        None
        
        Returns
        ----------
        None
          
        """
        current_frame = 0
        # Loop over all frames
        while current_frame < len(self.inputFrames):
            processed_graph = self.getInputNetworkAt(current_frame)
            degree = processed_graph.degree()
            if processed_graph.is_directed():
                in_degree_centrality = processed_graph.in_degree()
                out_degree_centrality = processed_graph.out_degree()
            else:
                cluster_coefficient = nx.cluster.clustering(processed_graph)
            betweenness_centrality = nx.betweenness_centrality(processed_graph, normalized=False)
            closeness_centrality = nx.closeness.closeness_centrality(processed_graph, normalized=False)
            num_nodes = 0
            while num_nodes < len(processed_graph.nodes()):
                node = processed_graph.nodes()[num_nodes]
                processed_graph.node[node][processState.degree] = degree[node]
                if processed_graph.is_directed():
                    processed_graph.node[node][processState.degreeIn] = in_degree_centrality[node]
                    processed_graph.node[node][processState.degreeOut] = out_degree_centrality[node]
                else:
                    processed_graph.node[node][processState.cluster] = cluster_coefficient[node]
                processed_graph.node[node][processState.closeness] = closeness_centrality[node]
                processed_graph.node[node][processState.betweenness] = betweenness_centrality[node]
                num_nodes += 1
                
            self._addProcessedFrame(processed_graph)
            current_frame += 1
    
    def getNumNodesAdded(self, network):
        nodes_added = 0
        for nodes in network.nodes_iter():
            if compressState.tag in network.node[nodes]:
                change = network.node[nodes][compressState.tag]
                if change == compressState.added:
                    nodes_added += 1

        return nodes_added
    
    def getNumEdgesAdded(self, network):
        edges_added = 0
        for edges in network.edges_iter():
            # Extract start and end nodes for the edge
            start = edges[0]
            end = edges[1]
            if compressState.tag in network.edge[start][end]:
                change = network.edge[start][end][compressState.tag]
                if change == compressState.added:
                    edges_added += 1

        return edges_added
    
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