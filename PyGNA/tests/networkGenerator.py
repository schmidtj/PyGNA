import networkx as nx
import random
from PyGNA import NetworkFrames
import itertools
import copy

def generateSimpleGNA(timesteps, startingNodes, startingEdges):
    #graph = nx.DiGraph(name='Test Network')
    graph = nx.Graph(name='Test Network')
    myNetworkFrames = NetworkFrames.NetworkFrames()
    
    for nodes in xrange(startingNodes):
        addNodeSimple(graph,nodes)

    for edges in xrange(startingEdges):
        addEdge(graph)
            
    for timestep in xrange(timesteps):
        randNode = graph.nodes()[random.randint(0,len(graph.nodes())-1)]
        if randNode % 2 == 0:
            #If 'state' == 0 add node
            if graph.node[randNode]['state'] == 0:
                newNode = graph.nodes()[-1] + 1
                addNodeSimple(graph,newNode)  
            elif graph.node[randNode]['state'] == 1:
                delNode(graph, randNode)
        elif randNode % 3 == 0:
            changeMe = graph.nodes()[random.randint(0,len(graph.nodes())-1)]
            changeNodeState(graph, changeMe)
        
        randEdge = 0
        if len(graph.edges()) > 0:
            randEdge = random.randint(0,len(graph.edges())-1)
        if randEdge % 2 == 0:
            addEdge(graph)
        else:
            delEdge(graph,randEdge)
            
        myNetworkFrames.addGraph(graph)
        
    myNetworkFrames.writeGraphs("simpleNetwork.graphML")
    
def generateBinaryStateGNA(timesteps, rule=""):
    graph = nx.Graph()
    addNode(graph,0,0)
    myNetworkFrames = NetworkFrames.NetworkFrames()
    myNetworkFrames.addGraph(graph)
    replacementRules = {}
    if rule != "":
        digits = list(rule)
        replacementRules = {(1,1):int(digits[0]),(1,0):int(digits[1]),(0,1):int(digits[2]),(0,0):int(digits[3])}
    else:
        replacementRules = {(0,0):random.randint(0,9),(0,1):random.randint(0,9),(1,0):random.randint(0,9),(1,1):random.randint(0,9)}
    for time in xrange(timesteps):
        if len(graph.nodes()) > 0:
            randNode = graph.nodes()[random.randint(0, len(graph.nodes())-1)]
            replace(graph, randNode, replacementRules[getTuple(graph, randNode)])
            myNetworkFrames.addGraph(graph)
        else:
            break
        
    myNetworkFrames.writeGraphs("BinaryState.graphML")
    
def getTuple(graph, node):
    nodeState = graph.node[node]['state']
    majority = nodeState
    if len(graph.edges()) > 0:
        for nodes in graph.edge[node]:
            if nodes in graph.node:
                if graph.node[nodes]['state'] == 0:
                    majority -= 1
                else:
                    majority += 1
        if majority == 0:
            majority = random.randint(0,1)
        else:
            majority = 0 if majority < 0 else 1
    
    return (nodeState,majority)

def replace(graph, node, rewritingMethod):
    if rewritingMethod == 0:
        graph.remove_node(node)
    elif rewritingMethod == 1:
        return
    elif rewritingMethod == 2:
        graph.node[node]['state'] = 0 if graph.node[node]['state'] == 1 else 1
    elif rewritingMethod == 3:
        duplicateNodes(graph, node, 2, 0)
    elif rewritingMethod == 4:
        duplicateNodes(graph, node, 2, 1)
    elif rewritingMethod == 5:
        duplicateNodes(graph, node, 2, 2)
    elif rewritingMethod == 6:
        duplicateNodes(graph, node, 3, 0)
    elif rewritingMethod == 7:
        duplicateNodes(graph, node, 3, 1)
    elif rewritingMethod == 8:
        duplicateNodes(graph, node, 3, 3)
    elif rewritingMethod == 9:
        duplicateNodes(graph, node, 3, 2)
        
def duplicateNodes(graph, node, dup, divideType):
    originalEdges = copy.deepcopy(graph.edge[node])
    for edges in originalEdges:
        graph.remove_edge(node,edges)
    newNodes = []
    dups = 1
    unique = getUniqueNodeIdentifier(graph)
    while dups < dup:
        newNodes.append(unique)
        unique += 1
        dups += 1
    
    # Preserver node state
    if divideType == 0:
        for nodes in newNodes:
            addNode(graph, nodes, graph.node[node]['state'])
    # Invert node states
    elif divideType == 1:
        invert = 0 if graph.node[node]['state'] == 1 else 1
        for nodes in newNodes:
            addNode(graph, nodes, invert)
    # Invert one node state
    elif divideType == 2:
        invert = 0 if graph.node[node]['state'] == 1 else 1
        initial = graph.node[node]['state'] if dup == 3 else invert
        for nodes in newNodes:
            addNode(graph, nodes, initial)
            initial = 0 if initial == 1 else 1
    # invert two node states     
    elif divideType == 3:
        initial = graph.node[node]['state']
        flipped = 0
        for nodes in newNodes:
            addNode(graph, nodes, initial)
            if flipped == 0:
                initial = 0 if initial == 1 else 1
            flipped = 1
    
    # Prepare list for edge connection section
    newNodes.append(node)
    
    # Distribute original edges
    nodeTarget = 0
    for edges in originalEdges:
        graph.add_edge(newNodes[nodeTarget],edges)
        if nodeTarget == len(newNodes) -1:
            nodeTarget = 0
        else:
            nodeTarget += 1
            
    # Connect new nodes to eachother
    start = 0
    end = 1
    while start <= len(newNodes) - 1:
        graph.add_edge(newNodes[start],newNodes[end])
        start += 1
        end += 1
        if end > len(newNodes) - 1:
            end = 0
            
def getUniqueNodeIdentifier(graph):
    returnValue = 0
    if len(graph.nodes()) > 0:
        returnValue = graph.nodes()[-1]
        returnValue += 1
        while returnValue in graph.node:
            returnValue += 1
    return returnValue

def addNodeSimple(graph, node):
    nodeState = random.randint(0,1)
    graph.add_node(node,state=nodeState)
    
def addNode(graph, node, stateval):
    graph.add_node(node,state=stateval)
    
def changeNodeState(graph, node):
    if graph.node[node]['state'] == 0:
        graph.node[node]['state'] = 1
    else:
        graph.node[node]['state'] = 0

def delNode(graph, node):
    print node
    graph.remove_node(node)
    
def addEdge(graph):
    for attempts in xrange(len(graph.nodes())):
        start = graph.nodes()[random.randint(0,len(graph.nodes())-1)]
        end = start
        while start == end:
            end = graph.nodes()[random.randint(0,len(graph.nodes())-1)]
        if (start,end) not in graph.edges():
            graph.add_edge(start,end)
            break
        
def delEdge(graph, edge):
    remove = graph.edges()[edge]
    graph.remove_edge(remove[0],remove[1])
        
def readNetworks():
    myInNetworks = NetworkFrames.NetworkFrames()
    myOutNetworks = NetworkFrames.NetworkFrames()
    myInNetworks.readGraphML("output.graphML")
    fileNum = 1
    for network in myInNetworks.getInputNetwork():
        fileName = "output" + str(fileNum) + ".graphML"
        myOutNetworks.addGraph(network)
        myOutNetworks.writeGraphs(fileName)
        myOutNetworks.clearInputNetworks()
        fileNum += 1
        
if __name__ == "__main__":
    network = input("Enter 0 for simple network and 1 for binary state GNA: ")
    if int(network) == 0:
        numTime=input("Enter number of time steps: ")
        numNodes=input("Enter number of starting nodes: ")
        numEdges=input("Enter number of starting edges: ")
        generateSimpleGNA(int(numTime),int(numNodes),int(numEdges))
    else:
        numTime = input("Enter number of time steps: ")
        rnInput = input("Enter specific rule number >= 0 & <= 9999 or enter -1 for a random rule. ")
        ruleNumber = ""
        if rnInput != -1:
            ruleNumber = str(rnInput)
            while len(ruleNumber) < 4:
                ruleNumber = '0' + ruleNumber
            while len(ruleNumber) > 4:
                ruleNumber = ruleNumber[:-1]
        generateBinaryStateGNA(int(numTime),ruleNumber)
