import networkGenerator as netGen

''' Modify this algorithm to use a second node property for extraction selection
probably state
'''

stateName = 'value'

def generateDegreeState(numStartingNodes, edgesPer, timestep):
    if edgesPer <= numStartingNodes:
        graph = netGen.nx.Graph()
        netFrames = netGen.NetworkFrames.NetworkFrames()
        for node in range(numStartingNodes):
            stateVal = netGen.random.randint(0,1)
            addNode(graph, node,stateVal)
        netFrames.addGraph(graph)
    
        for time in range(timestep):
            stateVal = netGen.random.randint(0,1)
            
            nodeDegree = []
            if stateVal == 0:
                nodeDegree = [[node, graph.degree(node)] for node in graph.nodes() if graph.node[node][stateName] == stateVal]
            else:
                nodeDegree = [[node, graph.degree(node)] for node in graph.nodes()]
            degreeSum = 0
            if len(nodeDegree) > 0:
                degreeSum = sum([item[1] for item in nodeDegree])
            degreeSum = -1 if degreeSum == 0 else degreeSum
            degreeProbability = [[deg[0],float(deg[1])/float(degreeSum)] for deg in nodeDegree]
            cumulativeProbability = []
            total = 0
            for degree in degreeProbability:
                total += degree[1]
                appendMe = [degree[0],total]
                cumulativeProbability.append(appendMe)
        
            # Check to see if we have any valid states yet
            noValidStates = False
            if stateVal == 0 and reduce(or2, getBoolStateList(graph,-1,stateVal)) == False:
                noValidStates = True
                
            uniqueNode = netGen.getUniqueNodeIdentifier(graph)
            addNode(graph, uniqueNode,stateVal)            
            if not noValidStates and len(cumulativeProbability) > 0:
                for edges in range(edgesPer):
                    newEdge = False
                    while not newEdge and edges < len(cumulativeProbability):
                        randNode = netGen.random.random()
                        index = 0 if not degreeSum == -1 else netGen.random.randint(0,len(cumulativeProbability)-1)
                        while randNode > cumulativeProbability[index][1] and degreeSum > 0:
                            index += 1
                        index = graph.nodes().index(cumulativeProbability[index][0])
                        if not graph.nodes()[index] in graph.edge[uniqueNode]:   
                            graph.add_edge(uniqueNode, graph.nodes()[index])
                            newEdge = True
                            if graph.node[uniqueNode][stateName] == 1:
                                graph.node[graph.nodes()[index]][stateName] = graph.node[uniqueNode][stateName]
                        
            netFrames.addGraph(graph)
            
        fileName = "DegreeState.graphML"
        netFrames.writeGraphs(fileName)

        
def addNode(graph, node, stateVal):
    graph.add_node(node)
    graph.node[node][stateName] = stateVal
        
def or2(x,y):
    return (x or y)

def add(x,y):
    return x + y

def opposite(x):
    if x == 1:
        return 0
    return 1

def getBoolStateList(graph, ignoreIndex, targetState):
    returnList = []
    for node in graph.node:
        if node != ignoreIndex:
            if graph.node[node][stateName] == targetState:
                returnList.append(True)
            else:
                returnList.append(False)
    return returnList

def getStateList(graph, ignoreIndex):
    returnList = []
    for node in graph.node:
        if node != ignoreIndex:
            returnList.append(opposite(graph.node[node][stateName]))
    return returnList
        
if __name__ == "__main__":
    startingNodes = input("Enter number of starting nodes: ")
    edgesPer = input("Enter number of edges added per time step: ")
    timesteps = input("Enter number of time steps: ")
    
    generateDegreeState(startingNodes, edgesPer, timesteps)