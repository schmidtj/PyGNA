import math
import networkx as nx
import copy
from itertools import groupby
import random

class utility(object):
    def __init__(self):
        self.state = None

    def getSubgraphFrequency(self, Graph, subgraph, symbreak=True):
        return len(self.findSubgraphInstances(Graph, subgraph))
    
    def findSubgraphInstances(self, Graph, subgraph,symbreak=True):
        ''' Grochow-Kellis Algorithm defined in
        Grochow, J., Kellis, M. "Network motif discovery using subgraph enumeration and symmetry-breaking."
        ''' 
        instances = []
        baseGraph = copy.deepcopy(Graph)
        
        # Set state name if it exists
        if len(Graph.nodes()) > 0 and len(subgraph.nodes()) > 0:
            graphNode = Graph.nodes()[0]
            subgraphNode = subgraph.nodes()[0]
            if len(Graph.node[graphNode]) > 0:
                if ((len(Graph.node[graphNode]) == len(subgraph.node[subgraphNode])) and
                    (Graph.node[graphNode].keys()[0] == subgraph.node[subgraphNode].keys()[0])):
                    # We do not support multiple states at the current time, so we will use the first state that we find.
                    self.state = Graph.node[graphNode].keys()[0]
                else:
                    raise AttributeError, "Incompatible state information between the two graphs"
            
        # Find the symmetry conditions if the flag has been set
        conditions = self.symmetryConditions(subgraph) if symbreak else []
        
        # Sort nodes by degree then by neighbor degree sequence
        graphNodesSorted = sorted(Graph.nodes(),
                                  cmp=lambda x,y: baseGraph.degree(x) - baseGraph.degree(y))
        '''graphNodesSorted = sorted(graphNodesSorted,
                                  cmp=lambda x,y:sum([baseGraph.degree(i)for i in baseGraph.neighbors(x)]) - 
                                  sum([baseGraph.degree(j) for j in baseGraph.neighbors(y)]))'''
        
        # Iterate over all graph nodes
        while len(graphNodesSorted)>0 and len(baseGraph.nodes()) >= len(subgraph.nodes()):
            baseNode = graphNodesSorted[0]
            for queryNode in subgraph.nodes():
                stateTest = True if not self.state else baseGraph.node[baseNode][self.state] == subgraph.node[queryNode][self.state]
                degreeTest = (baseGraph.in_degree(baseNode) >= subgraph.in_degree(queryNode) and 
                              baseGraph.out_degree(baseNode) >= subgraph.out_degree(queryNode)) if baseGraph.is_directed() else (baseGraph.degree(baseNode) >= subgraph.degree(queryNode))
                if degreeTest and stateTest:
                    f = {}
                    f[queryNode] = baseNode
                    isomorphs = self.isomorphicExtensions(f, baseGraph, subgraph,conditions, symbreak)
                    instances.extend(isomorphs)
            # Remove the node from the sorted list and from the graph
            graphNodesSorted.remove(baseNode)
            baseGraph.remove_node(baseNode)
        # Return list of isomorphs
        return instances

    def symmetryConditions(self, subgraph):
        ''' Symmetry breaking condition function defined in:
        Ribeiro, P., Silva, F. "G-Tries: an efficient data structure for discovering network motifs." 
        '''
        conditions = []
        # Find all the automorphisms of the subgraph
        aut = self.findSubgraphInstances(subgraph, subgraph, False)
        # Generate symmetry breaking conditions
        while len(aut) > 1:
            m = min([x for y in aut for x in y.keys() if y[x] != x])
            for v in set([x[m] for x in aut if x[m] != m]):
                conditions.append((m,v))
            aut = [x for x in aut if x[m] == m]
        return conditions
    
    def isomorphicExtensions(self, mapDict, Graph, subgraph, conditions, symbreak=True):
        ''' Grochow-Kellis Algorithm defined in
        Grochow, J., Kellis, M. "Network motif discovery using subgraph enumeration and symmetry-breaking."
        '''         
        isomorphs = []
        # If all the nodes of the query subgraph "subgraph" exist in the dictionary
        # append this isomorphic dictionary mapping to the list and return
        if reduce(lambda x, y: x and y, [x in mapDict.keys() for x in subgraph.nodes()]):       
            isomorphs.append(mapDict)
            return isomorphs
        
        # Look for candidates that have neighbors in the domain
        constrainedNeighbor = 0
        candidates = []
        candList = [x for x in subgraph.nodes() if x not in mapDict.keys()]
        for candidate in candList:
            for neighbor in subgraph.neighbors(candidate):
                if neighbor in mapDict.keys():
                    candidates.append(candidate)
                    break
        if len(candidates) > 1:
            #Sort by degree then largest neighborhood degree sequence
            candidates = sorted(candidates,
                                cmp=lambda x,y: subgraph.degree(x) - subgraph.degree(y),
                                reverse=True)
            '''candidates = sorted(candidates,
                                cmp=lambda x,y:sum([subgraph.degree(i) for i in subgraph.neighbors(x)]) - 
                                sum([subgraph.degree(j) for j in subgraph.neighbors(y)]),
                                reverse=True)'''
        if candidates == []:
            neighbors = []
            [neighbors.extend(x) for x in [subgraph.neighbors(y) for y in mapDict.keys()]]
            neighbors = set(neighbors) - set(mapDict.keys())
            constrainedNeighbor = list(neighbors)[0] if len(neighbors) > 0 else random.choice(candList)
        else:       
            constrainedNeighbor = candidates[0]
        
        # Identify all neighbors in the range
        neighbors = []
        # Find all the Graph neighbors of the current range of mapDict
        [neighbors.extend(x) for x in [Graph.neighbors(y) for y in mapDict.values()]]
        if Graph.is_directed():
            [neighbors.append(x) for x in Graph.nodes() for y in mapDict.values() if y in Graph.edge[x]]
        # Don't consider the neighbors that already exist in the range
        neighbors = set(neighbors) - set(mapDict.values())
        if ( (len(neighbors) < 1 and len(Graph.nodes()) > len(mapDict.values())) or
             0 in subgraph.degree().values()):
            neighbors = set(Graph.nodes()) - set(mapDict.values())
            #print "Fixed!"
        
        issue = False
        for rangeneighbors in neighbors:
            # Skip candidate if the degree of the node in the graph is less than the degree of the node in the subgraph or
            # if the states are incompatable
            stateTest = False if not self.state else Graph.node[rangeneighbors][self.state] != subgraph.node[constrainedNeighbor][self.state]
            degreeTest = (Graph.in_degree(rangeneighbors) < subgraph.in_degree(constrainedNeighbor) and 
                                          Graph.out_degree(rangeneighbors) < subgraph.out_degree(constrainedNeighbor)) if Graph.is_directed() else (Graph.degree(rangeneighbors) < subgraph.degree(constrainedNeighbor))            
            if degreeTest or stateTest:
                continue
            
            for key in mapDict.keys():
                if not (subgraph.has_edge(constrainedNeighbor, key) == Graph.has_edge(rangeneighbors, mapDict[key]) and 
                    subgraph.has_edge(key, constrainedNeighbor) == Graph.has_edge(mapDict[key], rangeneighbors)):
                    issue = True
                    
            if symbreak:
                # Apply symmetry breaking conditions
                breaking = [x for x in conditions if constrainedNeighbor in x]
                for condition in breaking:
                    if constrainedNeighbor == condition[0] and condition[1] in mapDict:
                        issue = True if rangeneighbors > mapDict[condition[1]] else issue
                    elif constrainedNeighbor == condition[1] and condition[0] in mapDict:
                        issue = True if mapDict[condition[0]] > rangeneighbors else issue
                        
            # Skip candidate if any issues were found          
            if issue:
                issue = False
                continue
            
            # Create a new map, add the new candidate, recursively call IsomorphicExtensions
            newMap = copy.deepcopy(mapDict)
            newMap[constrainedNeighbor] = rangeneighbors
            isomorphs.extend(self.isomorphicExtensions(newMap, Graph, subgraph,conditions, symbreak))
        
        # return a list of the isomorphs (also remove empty lists)
        return [x for x in isomorphs if x]    
        
    def BhattacharyyaDistance(self, pList, qList):
        returnVal = 0.
        try:
            returnVal = math.log(self.BhattacharyyaCoefficient(pList, qList)) * -1
        except ValueError:
            pass
        
        return  returnVal
    
    def BhattacharyyaCoefficient(self, pList, qList):
        assert(len(pList) == len(qList))
        
        returnValue = 0.
        index = 0
        while index < len(qList):
            returnValue += math.sqrt(pList[index]*qList[index])
            index += 1
        return returnValue
    
    def generateCumulativeDegDist(self, network):
        cumulative_deg = []
        deg_seq = sorted(nx.degree(network).values())
        freq_seq = dict((key, float(len(list(group)))) for key, group in groupby(deg_seq))
        sumVal = sum(freq_seq.values())
        
        cum_sum = 0
        for key in freq_seq.iterkeys():
            cumulative_deg.append(sum([freq_seq[x] for x in freq_seq.iterkeys() if x >= key])/sumVal)
            
        return [freq_seq.keys(), cumulative_deg]
    
    def processCumDegreeForBD(self, firstCumDegreeDist, secondCumDegreeDist):
        firstSumVal = sum(firstCumDegreeDist[1])
        secondSumVal = sum(secondCumDegreeDist[1])
        setOne = set(firstCumDegreeDist[0])
        setTwo = set(secondCumDegreeDist[0])
        diff = setOne.symmetric_difference(setTwo)
        
        for x in list(diff):
            if x not in firstCumDegreeDist[0]:
                firstCumDegreeDist[0].append(x)
                firstCumDegreeDist[0] = sorted(firstCumDegreeDist[0])
                index = firstCumDegreeDist[0].index(x)
                firstCumDegreeDist[1].insert(index, 0.)
            if x not in secondCumDegreeDist[0]:
                secondCumDegreeDist[0].append(x)
                secondCumDegreeDist[0] = sorted(secondCumDegreeDist[0])
                index = secondCumDegreeDist[0].index(x)
                secondCumDegreeDist[1].insert(index, 0.)
                        
        firstConvert = [float(x/firstSumVal) for x in firstCumDegreeDist[1]]
        secondConvert = [float(x/secondSumVal) for x in secondCumDegreeDist[1]]
        
        return [firstConvert,secondConvert]
    
if __name__ == "__main__":
    import graphMLRead
    import Rewriting
    util = utility()
    rewrite = Rewriting.Rewriting()
    #Graph = graphMLRead.read_graphml("generatedOutputMeanNetwork.graphML")
    #subgraph = graphMLRead.read_graphml("UniqueExtractedSubgraphs.graphML")
    #Graph = nx.read_graphml("nonisomorphicInputGraph.graphML")
    #subgraph = nx.read_graphml("nonisomorhicUES.graphML")
    #print util.getSubgraphFrequency(Graph, subgraph)
    Graph = nx.read_graphml("isoFailureGraph_1_of_2.graphML")
    subgraph = nx.read_graphml("isoFailureGraph_2_of_2.graphML")
    print util.getSubgraphFrequency(Graph, subgraph)    
    '''nonIsoFound = False
    count = 0
    for inputGraph in Graph:
        count += 1
        print count
        for subgraphs in subgraph:
            isomorphs = util.findSubgraphInstances(inputGraph, subgraphs)
            if isomorphs == []:
                nonIsoFound = True
                print "Empty Morphs"
                nx.write_graphml(inputGraph, "emptyIsomorphicInputGraph.graphML")
                nx.write_graphml(subgraphs, "emptyNonisomorhicUES.graphML")             
            isoGraphList = []
            for iso in isomorphs:
                isoGraphList.append(inputGraph.subgraph(iso.values()))
            for graphs in isoGraphList:
                if not rewrite.isIsomorphic(subgraphs, graphs):
                    nonIsoFound = True
                    print "Number of isomorphic graphs: " + str(len(isoGraphList))
                    nx.write_graphml(inputGraph, "nonisomorphicInputGraph.graphML")
                    nx.write_graphml(subgraphs, "nonisomorhicUES.graphML")
                    nx.write_graphml(graphs, "nonisomorhicCandidate.graphML")
                    break
            if nonIsoFound:
                break
        if nonIsoFound:
            break'''