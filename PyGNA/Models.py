"""
Models class holds the different models used during Extraction

"""
__author__ = """\n""".join(['Jeffrey Schmidt (jschmid1@binghamton.edu',
                            'Benjamin Bush (benjaminjamesbush@gmail.com)',
                            'Hiroki Sayama (sayama@binghamton.edu)'])

__all__ = ['addModel','getModelList','addDefaultModelsToList']


#    Copyright (C) 2012 by
#    Jeffrey Schmidt <jschmid1@binghamton.edu>
#    Benjamin Bush <benjaminjamesbush@gmail.com>
#    Hiroki Sayama <sayama@binghamton.edu>
#    All rights reserved.
#    BSD license.

import Model
import networkx as nx

class Models(object):
    def __init__(self):
        self.modelList = []
        
    def addModel(self, model):
        """Mutator that adds a model to the model list

        Parameters
        ----------
        model : Function object
           Model function to be used during extraction

        Returns
        -------
        void
        """
        self.modelList.append(model)
    
    def getModelList(self):
        """Accessor that returns the model list

        Parameters
        ----------
        None

        Returns
        -------
        modelList : List of model instances
           List of model instances to be used for Extraction
        """
        return self.modelList
    
    def addDefaultModelsToList(self):
        """Function that adds a default set of model classes to the model list

        Parameters
        ----------
        None

        Returns
        -------
        Void
        """
        def state(G, nodeID, state):
            
            stateVal = 0.001
            if state in G.node[nodeID]:
                if nodeID in G.nodes():
                    if state in G.node[nodeID]:
                        stateVal = 0.001 if G.node[nodeID][state] == 0 else G.node[nodeID][state]
                else: raise KeyError, "The nodeID: #%d does not exist in the graph." %nodeID
            else: raise KeyError, "State information does not exist for this graph."
            
            return stateVal
        
        def ImprovedState(G, subgraph, state):
            states = [G.node[node][state] for node in G.nodes()]
            uniqueStates = set(states)
            uniqueStateOccuranceMap = {}
            for states in uniqueStates:
                uniqueStateOccuranceMap[states] = len([node for node in G.nodes() if G.node[node][state] == states])
                
            stateCheck = [(state in G.node[x]) for x in subgraph.nodes()]
            if False in stateCheck:
                raise KeyError, "State information does not exist for this graph."
            else:
                retVal = 0.
                for node in subgraph.nodes():
                    currentState = G.node[node][state]
                    retVal += (1.0/uniqueStateOccuranceMap[currentState] ) * ( 1.0/len(uniqueStates))
                    
                return retVal
                
        
        def degree(G, subgraph, state):
            degreeVal = 0.
            nodeTest = [node in G.nodes() for node in subgraph.nodes()]
            if False in nodeTest:
                raise KeyError, "The nodeID: #%d does not exist in the graph." %subgraph.nodes()[nodeTest.index(False)]  
            else: 
                for nodes in subgraph:
                    degreeVal += G.degree(nodes)
                
            degreeVal = 0.001 if degreeVal == 0 else degreeVal
            
            return degreeVal
        
        def stateDegree(G, nodeID, state):
            stateDegreeVal = 0.
            if nodeID in G.nodes():
                if state in G.node[nodeID]:
                    stateVal = 0.001 if G.node[nodeID][state] == 0 else G.node[nodeID][state]
                    degreeVal = 0.001 if G.degree(nodeID) == 0 else G.degree(nodeID)
                    stateDegreeVal = degreeVal * stateVal
                else: raise KeyError, "State information does not exist for this graph."
                
            else: raise KeyError, "The nodeID: #%d does not exist in the graph." %nodeID
            stateDegreeVal = 0.001 if stateDegreeVal == 0 else stateDegreeVal
            
            return stateDegreeVal
        
        def degreeState(G, subgraph, state):
            nodeTest = [node in G.nodes() for node in subgraph.nodes()]
            if False in nodeTest:
                raise KeyError, "The nodeID: #%d does not exist in the graph." %subgraph.nodes()[nodeTest.index(False)]  
            else:
                stateCheck = [(state in G.node[x]) for x in subgraph.nodes()]
                if False in stateCheck:
                    raise KeyError, "State information does not exist for this graph."
                else:
                    retVal = 0.
                    states = [G.node[node][state] for node in G.nodes()]
                    uniqueStates = set(states)
                    degreeTotalForStateMap = {}
                    for states in uniqueStates:
                        degreeTotalForStateMap[states] = sum([G.degree(node)+1 for node in G.nodes() if G.node[node][state] == states])
                        
                    for node in subgraph:
                        currentState = G.node[node][state]
                        retVal += ((G.degree(node)+1.0)/degreeTotalForStateMap[currentState] ) * ( 1.0/len(uniqueStates))
                    return retVal
                
                              
        
        def baseCase(G, nodeID, state):
            return 1
        
        degreeModel = Model.Model(degree, 'degree')
        stateModel = Model.Model(ImprovedState, 'state')
        degreeStateModel = Model.Model(degreeState, 'degreeState')
        baseModel = Model.Model(baseCase, 'baseCase')
        self.addModel(degreeModel)
        self.addModel(stateModel)
        self.addModel(degreeStateModel)
        #self.addModel(baseModel)
        
    #----------------------------------------------------------------------
    def add_recipe_models(self):
        """Adds the set of models used for the Recipe Method"""
        
        def avg_degree(G, subgraph):
            
            accum_degree = 0
            for node in subgraph.nodes():
                accum_degree += G.degree(node)
                
            return accum_degree / float(len(subgraph.nodes()))
        
        def avg_neighborhood_degree(G, subgraph):
            
            result = nx.average_neighbor_degree(G, nodes=subgraph.nodes())
            accum = 0
            for key in result.iterkeys():
                accum += result[key]
                
            return accum / float(len(subgraph.nodes()))
        
        def avg_clustering(G, subgraph):
            G = G.to_undirected() if nx.is_directed(G) else G
            return nx.average_clustering(G, subgraph.nodes())
            
        average_degree = Model.Model(avg_degree, 'avgDegree')  
        average_neigh_degree = Model.Model(avg_neighborhood_degree, 'avgNeighDegree')
        #average_clustering = Model.Model(avg_clustering, 'avgClustering')
        self.addModel(average_degree)
        self.addModel(average_neigh_degree)
        #self.addModel(average_clustering)