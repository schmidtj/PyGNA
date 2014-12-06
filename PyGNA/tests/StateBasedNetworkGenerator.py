import networkGenerator as netGen

def generateStateBasedNetwork(timeSteps):
    graph = netGen.nx.Graph(name='State Network')
    myNetworkFrames = netGen.NetworkFrames.NetworkFrames()
    
    for nodes in xrange(3):
        netGen.addNodeSimple(graph,nodes)
    
    for edges in xrange(2):
        netGen.addEdge(graph)
    
    myNetworkFrames.addGraph(graph)
    
    for t in range(timeSteps):
        selection = [n for n in graph.node.iterkeys() if graph.node[n]['state'] == 1]
        if len(selection) > 0:
            head = netGen.random.choice(selection)
            tail = netGen.random.choice(graph.nodes())
            while head == tail:
                tail = netGen.random.choice(graph.nodes())
            newNode = netGen.getUniqueNodeIdentifier(graph)
            graph.add_edge(head,tail)
            netGen.addNodeSimple(graph, newNode)
        else:
            netGen.addNodeSimple(graph,netGen.getUniqueNodeIdentifier(graph))
            
        myNetworkFrames.addGraph(graph)
    
    myNetworkFrames.writeGraphs("StateBasedNetwork.graphML")
        
if __name__ == '__main__':
    timeSteps = input("Enter the number of time steps: ")
    generateStateBasedNetwork(timeSteps)
        
    