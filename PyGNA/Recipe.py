"""
Recipe class.

"""
__author__ = """\n""".join(['Jeffrey Schmidt (jschmid1@binghamton.edu',
                            'Hiroki Sayama (sayama@binghamton.edu)'])

__all__ = ['get_total_iterations','add_transition_list','choose_motif_transition',
           'read_recipe','write_recipe','is_new_iteration','get_lhs_for_iteration']


#    Copyright (C) 2015 by
#    Jeffrey Schmidt <jschmid1@binghamton.edu>
#    Hiroki Sayama <sayama@binghamton.edu>
#    All rights reserved.
#    BSD license.

import Motif
import pickle
import GTrie
import sys
import random
import NetworkFrames
import Models
import Utility
import networkx as nx
import Extraction

class Recipe(object):
    
    #----------------------------------------------------------------------
    def __init__(self):
        """Default constructor"""
        self.transition_sets = []
        self.total_iterations = 0
        self.recipe_tree = GTrie.GTrie.GTrie()
        self.recipe_extraction_pool = None
        self.models = Models.Models()
        self.models.add_recipe_models()        
        self.util = Utility.utility()
        self.extraction = Extraction.Extraction()
        
    #----------------------------------------------------------------------
    def get_total_iterations(self):
        """Get the total number of iterations for this recipe"""
        return self.total_iterations
    
    #----------------------------------------------------------------------
    def set_total_iterations(self):
        """Uses the internal transition sets to calculate the total iterations"""
        self.total_iterations = 0
        for t_list in self.transition_sets:
            self.total_iterations += t_list.get_num_iterations()
        
    #----------------------------------------------------------------------
    def add_transition_list(self, transition_list):
        """Adds transition list to the global set of transitions"""
        self.transition_sets.append(transition_list)
        self.total_iterations += transition_list.get_num_iterations()
    
    #----------------------------------------------------------------------
    def choose_motif_transition(self, iteration, options):
        """Choose a motif transtion based on the current iteration"""
        if iteration < self.total_iterations:
            accum = 0
            for transition_list in self.transition_sets:
                accum += transition_list.get_num_iterations()
                if iteration <= accum:
                    return transition_list.choose_motif_transition(options)
        else:
            raise IndexError("The interation value passed exceeds total_iterations.")        
    
    #----------------------------------------------------------------------
    def get_transition_list_for_iteration(self, iteration):
        """"""
        if iteration < self.total_iterations:
            accum = 0
            for transition_list in self.transition_sets:
                accum += transition_list.get_num_iterations()
                if iteration <= accum:
                    return transition_list
            else:
                raise IndexError("The interation value passed exceeds total_iterations.")  
    #----------------------------------------------------------------------
    def get_num_changes_this_iteration(self, iteration):
        """Gets the number of changes required for this iteration"""
        if iteration < self.total_iterations:
            accum = 0
            for transition_list in self.transition_sets:
                accum += transition_list.get_num_iterations()
                if iteration <= accum:
                    return transition_list.get_num_changes() / transition_list.get_num_iterations()
        else:
            raise IndexError("The interation value passed exceeds total_iterations.")
        
    #----------------------------------------------------------------------
    def get_lhs_for_iteration(self, iteration):
        """Gets all the left hand sides for the current iteration"""
        if iteration < self.total_iterations:
            accum = 0
            for transition_list in self.transition_sets:
                accum += transition_list.get_num_iterations()
                if iteration <= accum:
                    return transition_list.get_left_hand_sides()
        else:
            raise IndexError("The interation value passed exceeds total_iterations.")        
    
    #----------------------------------------------------------------------
    def is_new_iteration(self, iteration):      
        """Determines if the current iteration uses a new motif transition
        list"""
        if iteration < self.total_iterations:
            accum = 0
            index = 0
            while accum < iteration:
                if iteration == accum + 1:
                    return True 
                
                t_list = self.transition_sets[index]
                accum += t_list.get_num_iterations()
                index += 1
                
            return False
    
    #----------------------------------------------------------------------
    def generate_gtrie(self, iteration):
        """"""
        if self.is_new_iteration(iteration):
            lhs_list = self.get_lhs_for_iteration(iteration)
            self.recipe_tree = GTrie.GTrie.GTrie()
            for index in xrange(len(lhs_list)):
                lhs = lhs_list[index]
                self.recipe_tree.GTrieInsert(lhs.get_subgraph(), index, states=True)        
    
    #----------------------------------------------------------------------
    def generate_recipe_extraction_pool(self, network):
        """"""
        print "Generating GTrie Extraction Pool...",
        self.recipe_tree.GTrieMatch(network,labels=True, states=True)
        print "Done."
        
        self.recipe_extraction_pool = self.recipe_tree.getMatches(labels=True)
        print "Pool key size: " , len([key for key in self.recipe_extraction_pool.iterkeys()])
        for keys in self.recipe_extraction_pool.iterkeys():
            subgraphs = self.recipe_extraction_pool[keys]
            new_data = []
            for subgraph in subgraphs:
                local_data = [model.getModel()(network, subgraph) for model in self.models.getModelList()]
                new_lhs = Motif.LHS(subgraph, local_data)
                new_data.append(new_lhs)
            self.recipe_extraction_pool[keys] = new_data
            print len(self.recipe_extraction_pool[keys])        
    
    #----------------------------------------------------------------------
    def select_rewriting_rule(self, network, iteration):
        """"""
        #Note that not all the LHSs in the motif transition list will exist
        #in the extraction pool.  This is especially true for early iterations
        available_keys = [key for key in self.recipe_extraction_pool.iterkeys()]
        transition = self.choose_motif_transition(iteration, available_keys)
        t_lhs = transition[1].get_lhs()
        best_subgraphs = []
        best_index = 0
        best_val = sys.float_info.max
        candidates = self.recipe_extraction_pool[transition[0]]
        distances = [t_lhs.calculate_distance(candidate) for candidate in candidates]
        max_val = max(distances) + 1
        normalized = [abs(distance - max_val) for distance in distances]
        normalized_sum = sum(normalized)

        val = random.uniform(0, normalized_sum)
        accum = 0
        index = 0
        while index < len(normalized):
            accum += normalized[index]
            if accum >= val:
                choices = [pick for pick in range(index, len(normalized)) if distances[pick] == distances[index]]
                choice = candidates[random.choice(choices)]
                break
            index += 1
                
        t_rhs = transition[1].get_rhs().get_subgraph().copy()
        delta = self.util.makeNodeLabelsDisjoint(choice.get_subgraph(), t_rhs)
        delta = self.util.makeNodeLabelsDisjoint(network, delta)
        new_lhs = self.extraction.getExtractionSubgraphFromDelta(delta)
        mapping = self.util.findSubgraphInstances(choice.get_subgraph(), new_lhs, False)  
        if len(mapping) > 1:
            pass
        rewriting_rule = nx.relabel_nodes(delta,mapping[0],copy=True) if len(mapping) > 0 else delta
     
        if not self.is_new_iteration(iteration + 1):
            candidates.remove(choice)
            
        return rewriting_rule
    
                
    #----------------------------------------------------------------------
    def read_recipe(self, path):
        """Reads a recipe from disk"""
        self.transition_sets = pickle.load( open( path, "rb" ) )
        self.set_total_iterations()
    
    #----------------------------------------------------------------------
    def write_recipe(self, path):
        """Writes a recipe to disk"""
        pickle.dump( self.transition_sets, open( path, "wb" ) )