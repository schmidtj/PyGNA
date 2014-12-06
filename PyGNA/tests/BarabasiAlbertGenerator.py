import networkGenerator as netGen

''' Modify this algorithm to use a second node property for extraction selection
probably state
'''
def generateBarabasiAlbert(numStartingNodes, edgesPer, timestep, stateSelect=False):
    if edgesPer <= numStartingNodes:
        graph = netGen.nx.Graph()
        netFrames = netGen.NetworkFrames.NetworkFrames()
        for node in range(numStartingNodes):
            addNode(graph, node)
        netFrames.addGraph(graph)
        
        # Check to see if we have any valid states yet
        noValidStates = False
        if stateSelect and reduce(or2, getBoolStateList(graph,-1)) == False:
            noValidStates = True
        
        for time in range(timestep):
            nodeDegree = [graph.degree(node) for node in graph.nodes()]
            degreeSum = sum(nodeDegree)
            degreeSum = -1 if degreeSum == 0 else degreeSum
            degreeProbability = [float(deg)/float(degreeSum) for deg in nodeDegree]
            cumulativeProbability = []
            total = 0
            for degree in degreeProbability:
                total += degree
                cumulativeProbability.append(total)
                
            uniqueNode = netGen.getUniqueNodeIdentifier(graph)
            addNode(graph, uniqueNode)
            for edges in range(edgesPer):
                newEdge = False
                while not newEdge:
                    randNode = netGen.random.random()
                    index = 0 if not degreeSum == -1 else netGen.random.randint(0,len(graph.nodes())-2)
                    while randNode > cumulativeProbability[index] and degreeSum > 0:
                        index += 1
                    if not graph.nodes()[index] in graph.edge[uniqueNode]:
                        if stateSelect:
                            if noValidStates:
                                # Short circuit, it is not possible to create an edge
                                if reduce(or2, getBoolStateList(graph,uniqueNode)) == False:
                                    newEdge = True
                                else:
                                    noValidStates = False
                                
                            if graph.node[graph.nodes()[index]]['state'] == 1:
                                graph.add_edge(uniqueNode, graph.nodes()[index])
                                newEdge = True
                            # If there are not enough nodes with state 1 finish the edge creation
                            # short circuit
                            elif reduce(add,getStateList(graph, uniqueNode)) < edgesPer:
                                newEdge = True
                        else:
                            graph.add_edge(uniqueNode, graph.nodes()[index])
                            newEdge = True
                
            netFrames.addGraph(graph)
            
        fileName = "BAPlusState.graphML" if stateSelect else "BarabasiAlbert.graphML"
        netFrames.writeGraphs(fileName)

        
def addNode(graph, node):
    stateVal = netGen.random.randint(0,1)
    graph.add_node(node)
        
def or2(x,y):
    return (x or y)

def add(x,y):
    return x + y

def getBoolStateList(graph, ignoreIndex):
    returnList = []
    for node in graph.node:
        if node != ignoreIndex:
            if graph.node[node]['state'] == 1:
                returnList.append(True)
            else:
                returnList.append(False)
    return returnList

def getStateList(graph, ignoreIndex):
    returnList = []
    for node in graph.node:
        if node != ignoreIndex:
            returnList.append(graph.node[node]['state'])
    return returnList
        
if __name__ == "__main__":
    startingNodes = input("Enter number of starting nodes: ")
    edgesPer = input("Enter number of edges added per time step: ")
    timesteps = input("Enter number of time steps: ")
    #stateSelect = raw_input("Only add edges to nodes with state = 1?: ")
    stateSelect = False
    
    generateBarabasiAlbert(startingNodes, edgesPer, timesteps, stateSelect)