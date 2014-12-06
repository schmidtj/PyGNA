import networkGenerator as netGen

def generateErdosRenyi(numNodes, numEdges):
    if numEdges <= numNodes:
        graph = netGen.nx.Graph()
        netFrames = netGen.NetworkFrames.NetworkFrames()
        
        # Add nodes to graph
        for node in range(numNodes):
            netGen.addNodeSimple(graph, node)
        
        # Add initial graph
        netFrames.addGraph(graph)
        
        # While number of edges is less the the number selected
        while len(graph.edges()) < numEdges:
            # Randomly choose a head and tail
            tail = netGen.random.choice(graph.nodes())
            head = netGen.random.choice(graph.nodes())
            while tail == head:
                head = netGen.random.choice(graph.nodes())
            
            # If a unique edge, add it to graph
            if tail not in graph.edge[head]:
                graph.add_edge(head,tail)
                netFrames.addGraph(graph)
        
        netFrames.writeGraphs('ErdosRenyi.graphML')

if __name__ == '__main__':
    numNodes = input("Enter the number of nodes: ")
    numEdges = input("Enter the number of edges: ")
    generateErdosRenyi(numNodes, numEdges)