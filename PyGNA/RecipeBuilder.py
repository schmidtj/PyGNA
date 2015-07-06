"""
RecipeBuilder class.

"""
__author__ = """\n""".join(['Jeffrey Schmidt (jschmid1@binghamton.edu',
                            'Hiroki Sayama (sayama@binghamton.edu)'])

__all__ = []


#    Copyright (C) 2015 by
#    Jeffrey Schmidt <jschmid1@binghamton.edu>
#    Hiroki Sayama <sayama@binghamton.edu>
#    All rights reserved.
#    BSD license.

import Motif
from Motif import ChangeData
import NetworkFrames
import networkx as nx
import Extraction
import Rewriting
import scipy.misc as scipymisc
import random
import itertools
import Utility
import copy
import Display
import math
from GTrie import *
import Models
import Recipe

class RecipeBuilder(object):
    #----------------------------------------------------------------------
    def __init__(self):
        """"""
        self.network = None
        self.gtrie = GTrie.GTrie()
        self.sample_size = 0
        self.models = Models.Models()
        self.models.add_recipe_models()
        self.util = Utility.utility()
        self.extraction = Extraction.Extraction()
    
    #----------------------------------------------------------------------
    def __init__(self, input_network):
        """"""
        self.network = input_network
        self.gtrie = GTrie.GTrie()
        self.gtrie.createGTrieWithFour()
        self.sample_size = 0        
        self.models = Models.Models()
        self.models.add_recipe_models()
        self.util = Utility.utility()
        self.extraction = Extraction.Extraction()
        
    #----------------------------------------------------------------------
    def set_sample_size(self, size):
        """Sets the sample size"""
        self.sample_size = size

    #----------------------------------------------------------------------
    def construct_lhs(self, input_network, subgraph):
        """Construct a motif object from the passed in subgraph."""
        local_data = [model.getModel()(input_network, subgraph) for model in self.models.getModelList()]
        return Motif.LHS(subgraph, local_data)
    
    #----------------------------------------------------------------------
    def construct_rhs(self, subgraph):
        """"""
        data = [0 for i in range(6)]
        for node in subgraph.nodes():
            state = subgraph.node[node][NetworkFrames.compressState.tag]
            if NetworkFrames.compressState.added == state:
                data[ChangeData.nodeAdded] += 1
            elif NetworkFrames.compressState.deleted == state:
                data[ChangeData.nodeDeleted] += 1
            elif NetworkFrames.compressState.stateChange == state:
                data[ChangeData.nodeStateChange] += 1
         
        for x, y in subgraph.edges():
            state = subgraph.edge[x][y][NetworkFrames.compressState.tag]
            if NetworkFrames.compressState.added == state:
                data[ChangeData.edgeAdded] += 1
            elif NetworkFrames.compressState.deleted == state:
                data[ChangeData.edgeDeleted] += 1
            elif NetworkFrames.compressState.stateChange == state:
                data[ChangeData.edgeStateChange] += 1
                
        return Motif.RHS(subgraph, data)
        
       
    #----------------------------------------------------------------------
    def union_method(self):
        """Generates a recipe by sampling all of the changes for each iteration."""
        
        recipe = Recipe.Recipe()
        transition_list = Motif.MotifTransitionList()
        #self.network.writeCompressedFrames("Forest_Fire_compressed.graphml")
        print "Building Recipe...",
        for networkIndex in range(1,len(self.network.getInputNetworks())):
            
            self.UES_data = []
            
            target_motif = self.network._getCompressedNetworkAt(networkIndex)
    
            #find the left hand side of the rewriting rule
            lefthandside = self.extraction.getExtractionSubgraphFromDelta(target_motif)
            
            print len(lefthandside.edges())
            lhs_motif = self.construct_lhs(self.network.getInputNetworkAt(networkIndex-1), lefthandside)
            rhs_motif = self.construct_rhs(target_motif)          
            
            transition_list.insert_motif_transition(lhs_motif, rhs_motif)
        
        transition_list.set_num_iterations(len(self.network.getInputNetworks()))
        recipe.add_transition_list(transition_list)    
        #transition_list.display_transitions()
        transition_list.write_lhs_to_disk('ff_lhs.graphML')
        print "Done."
        return recipe
   
    #----------------------------------------------------------------------
    def disjoint_method(self, connected_only=False):
        """Generates a recipe by sampling on a per iteration basis."""
        
        for networkIndex in range(len(self.network.getInputNetworks())):
            print "Sampling Network...",
            self.UES_data = []
            sampleTrie = GTrie.GTrie()
            sample = self.sampleCompressedNetworkAt(networkIndex)
            sampleCount = 0
            while sampleCount < self.sample_size:
                        
                if len(sample[1]) > 0:
                    sampleMotif = random.choice(sample[1])
                else:
                    print "Error: Empty Sample.  Aborting simulation"
                    raise IndexError
                
                #find the left hand side of the rewriting rule
                lefthandside = self.prev_extraction.getExtractionSubgraphFromDelta(sampleMotif)
                components = nx.connected_components(lefthandside)
                if connected_only == True and len(lefthandside) > 0 and not nx.is_connected(lefthandside):
                    continue
                component_len = [1 for x in components if len(x) > 1]           
                if len(lefthandside.nodes()) == 0 or (len(components) > 1 and sum(component_len) > 1):
                    continue
                        
                isomorphfound = False
                sampleTrie.GTrieMatch(lefthandside, [1,1,1,1,1], labels=True, states=True)
                matches = sampleTrie.getMatches(labels=True)
                for key in matches:
                    if self.util.isIsomorphicFast(self.UES_data[key][0], lefthandside):
                        self.UES_data[key][1].append(sampleMotif)
                        isomorphfound = True
                        sampleCount += 1
                        break
                
                if not isomorphfound:              
                    addExtraction = [lefthandside,[sampleMotif]]
                    sampleTrie.GTrieInsert(lefthandside, label=len(self.UES_data), states=True)
                    self.UES_data.append(addExtraction)
                    sampleCount += 1
            
            #Add exclusion list to extraction map
            for extraction in self.UES_data:
                extraction.append([x for x in range(len(extraction[1]))])
                
            self.generateProportionalSelectionData()
            self.calculateAvgChanges()
            self.generateInputComparisonDataAt(networkIndex)
            print "Done."        
        
    
    #----------------------------------------------------------------------
    def sample_compressed_network_at(self, index):
        """Samples the compressed network and the passed in index"""
        self.gtrie.setMaxMatches(self.sample_size)
        network = self.network._getCompressedNetworkAt(index)
        num_changes = self.network.getNumberOfChanges(index)
        value = 0.01 if num_changes > 5000 else 0.1
        value = 0.001 if num_changes > 7000 else value
        value - 0.001 if num_changes > 9000 else value
        self.gtrie.GTrieMatch(network, [1,1,1,math.sqrt(value), math.sqrt(value)])
        matches = self.gtrie.getMatches()
        return (len(matches), matches)