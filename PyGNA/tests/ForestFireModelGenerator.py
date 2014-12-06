import networkx as nx
from PyGNA import NetworkFrames
import networkGenerator
import random
import math

burnlist = []

def generateForrestFireNetwork(forwardProbability, backwardRatio, orphan, iterations,digraph=True):
    # Calculate n for the Binomial function
    n = int(math.ceil(1./(forwardProbability - pow(forwardProbability,2))))
    
    # Create graph and network frames.
    graph = nx.DiGraph(name='Forest Fire') if digraph else nx.Graph(name='Forest Fire')
    myNetworkFrames = NetworkFrames.NetworkFrames() 
    
    for v in xrange(iterations):
        graph.add_node(v)
        
        if len(graph.nodes()) > 1:
            ambassador = v
            while ambassador == v:
                ambassador = random.choice(graph.nodes())
                
            if random.random() > orphan:
                burnedList = []
                burn(forwardProbability, n, backwardRatio, graph, ambassador, burnedList)
                for u in burnedList:
                    graph.add_edge(v, u)
                    
        myNetworkFrames.addGraph(graph)
        
    myNetworkFrames.writeGraphs("ForestFire.graphML")

# Recursive burn function                   
def burn(p, n, r, graph, ambassador, burnlist):
    
    if ambassador in burnlist:
        return
    
    burnlist.append(ambassador)
    edgesToBurn = binomial(p,n)
    edgesToBurn = edgesToBurn if edgesToBurn <= len(graph.edge[ambassador]) else len(graph.edge[ambassador])
    edgesToBurnBack = int(math.floor(r*edgesToBurn))
    edgesToBurn -= edgesToBurnBack
    
    if edgesToBurn > 0:
        forwardEdges = graph.edge[ambassador].keys()
        for x in xrange(edgesToBurn):
            newAmbassador = random.choice(forwardEdges)
            forwardEdges.remove(newAmbassador)
            burn(p, n, r, graph, newAmbassador, burnlist)
            
        if edgesToBurnBack > 0:
            adjacencyList = graph.adjacency_list()
            backwardEdges = []
            for x in adjacencyList:
                if ambassador in x:
                    backwardEdges.append(graph.nodes()[adjacencyList.index(x)])
                    
            if len(backwardEdges) > 0:
                for x in xrange(edgesToBurnBack):
                    newAmbassador = random.choice(backwardEdges)
                    burn(p, n, r, graph, newAmbassador, burnlist)
        
    
                
def binomial(p, n):

    assert( 0. <= p and p <= 1. and n >= 1 )
    sum = 0
    for x in xrange(n):
        sum += bernoulli(p)
        
    return sum
    
def bernoulli(p):
    
    assert( 0. <= p and p <= 1. )    

    if random.random() < p:
        return 1
    else:
        return 0
    
if __name__ == "__main__":
    iterations = input("Please enter the number of iterations: ")
    forwardProb = input("Please enter the forward burning probability: ")
    backwardRatio = input("Please enter the backward burning ratio: ")
    orphanProb = input("Please enter the orphan probability: ")
    directional = input("Create a directed graph? (1 for yes/0 for no): ")
    directional = False if directional == 0 else True
    generateForrestFireNetwork(forwardProb, backwardRatio, orphanProb, iterations, directional)