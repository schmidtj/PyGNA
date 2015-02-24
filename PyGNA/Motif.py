"""
Motif related classes.

"""
__author__ = """\n""".join(['Jeffrey Schmidt (jschmid1@binghamton.edu',
                            'Hiroki Sayama (sayama@binghamton.edu)'])

__all__ = ['get_subgraph','set_subgraph','set_local_data',
           'append_tuple_to_local_data','choose_value_set','get_rhs',
           'get_lhs','get_occurance_num','set_num_iterations',
           'get_num_iterations', 'add_motif_transition',
           'choose_motif_transition','get_left_hand_sides',
           'get_right_hand_sides']


#    Copyright (C) 2015 by
#    Jeffrey Schmidt <jschmid1@binghamton.edu>
#    Hiroki Sayama <sayama@binghamton.edu>
#    All rights reserved.
#    BSD license.

import random
import networkx
import Utility
import math
import matplotlib.pyplot as plt
import NetworkFrames


class ChangeData(object):
    nodeAdded = 0
    nodeDeleted = 1
    nodeStateChange = 2
    edgeAdded = 3
    edgeDeleted = 4
    edgeStateChange = 5
    all_data = [nodeAdded, nodeDeleted, nodeStateChange, edgeAdded, edgeDeleted,edgeStateChange]
    
class Motif(object):
    #----------------------------------------------------------------------
    def __init__(self):
        """Default constructor"""
        self.subraph = None
        self.data = []
        self.mapping = {}
        self.util = Utility.utility() 
        self.p = 1
    
    #----------------------------------------------------------------------
    def __init__(self, subgraph, data):
        """Initialization"""
        self.subgraph = subgraph
        self.data = data
        self.mapping = {}
        self.util = Utility.utility()         
        self.p = 1
        
    #----------------------------------------------------------------------
    def __eq__(self, motif):
        """"""
        ret_val = False
        if self.util.isIsomorphicFast(self.subgraph, motif.get_subgraph()):
            ret_val = True
        return ret_val
    #----------------------------------------------------------------------
    def get_subgraph(self):
        """Accessor for internal networkx graph"""
        return self.subgraph
    
    #----------------------------------------------------------------------
    def set_subgraph(self, subgraph):
        """Sets the internal subgraph object"""
        self.subraph = subgraph.copy()
    
    #----------------------------------------------------------------------
    def set_data(self, data):
        """Sets the local data for this motif"""
        self.data = data
    
    #----------------------------------------------------------------------
    def get_data(self):
        """"""
        return self.data
    #----------------------------------------------------------------------
    def append_to_data(self, data):
        """Appends a tuple to the local data list"""
        self.data.append(data)
        
    #----------------------------------------------------------------------
    def choose_value_set(self):
        """Function to get a random tuple of values from local_data"""
        return random.choice(self.data)
    
    #----------------------------------------------------------------------
    def calculate_distance(self, lhs):
        """Calculate the distance between self and the lhs passed in."""    
        accum = 0.
        for i in xrange(len(self.data)):
            accum += abs(self.data[i] - lhs.get_data()[i]) ** self.p
            
        return accum ** (1 / self.p)
    
########################################################################
class LHS(Motif):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Default Constructor"""
        super(LHS, self).__init__()
        self.p = 21.
       
    #----------------------------------------------------------------------
    def __init__(self, subgraph, data):
        """Constructor"""
        super(LHS, self).__init__(subgraph, data)
        self.p = 1.
        
class RHS(Motif):
    
    #----------------------------------------------------------------------
    def __init__(self):
        """Default Constructor"""
        super(RHS, self).__init__()
        self.p = 0.5

    #----------------------------------------------------------------------
    def __init__(self, subgraph, data):
        """Constructor"""
        super(RHS, self).__init__(subgraph, data)
        self.p = 0.5
        
class MotifTransition(object):
    #----------------------------------------------------------------------
    def __init__(self):
        """Default constructor"""
        self.lhs = None
        self.rhs = None
        self.mapping = {}
        self.num_occurance = 0
        
    #----------------------------------------------------------------------
    def __init__(self, lhs, rhs, num_occurances, mapping={}):
        """"""
        self.lhs = lhs
        self.rhs = rhs
        self.mapping = mapping
        self.num_occurance = num_occurances
        
    #----------------------------------------------------------------------
    def get_rhs(self):
        """Get the 'right hand side' of the motif transition"""
        return self.rhs
    
    #----------------------------------------------------------------------
    def get_lhs(self):
        """Get the 'left hand side' of the motif transition"""
        return self.lhs
    
    #----------------------------------------------------------------------
    def get_occurance_num(self):
        """Get the number of occurances for this motif transition"""
        return self.num_occurance
    
    #----------------------------------------------------------------------
    def inc_occurance_num(self):
        """"""
        self.num_occurance += 1
        
    #----------------------------------------------------------------------
    def set_mapping(self, mapping):
        """"""
        self.mapping = mapping
        
    #----------------------------------------------------------------------
    def get_mapping(self):
        """"""
        return self.mapping
    
class MotifTransitionList(object):
    
    #----------------------------------------------------------------------
    def __init__(self):
        """Default constructor"""
        self.transition_list = []
        self.total_occurances = 0
        self.num_iterations = 0
        self.total_changes = 0
        self.util = Utility.utility()
    
    #----------------------------------------------------------------------
    def set_num_iterations(self, iterations):
        """Set the number of iterations to run this motif transtion list"""
        self.num_iterations = iterations
        
    #----------------------------------------------------------------------
    def get_num_iterations(self):
        """Get the number of iterations to run this motif transition list"""
        return self.num_iterations
    
    #----------------------------------------------------------------------
    def get_transitions(self):
        """Gets the motif transitions"""
        return self.transition_list
    
    #----------------------------------------------------------------------
    def get_num_transitions(self):
        """Gets the number of transitions in this transition list"""
        return len(self.transition_list)
    
    #----------------------------------------------------------------------
    def set_num_changes(self):
        """Sets the total number of changes required for this motif transition
        list"""
        self.total_changes = sum([transition.get_occurance_num() for transition in self.transition_list])
        
    #----------------------------------------------------------------------
    def get_num_changes(self):
        """Gets the total number of changes required for this motif transition
        list"""
        return self.total_changes
    
    #----------------------------------------------------------------------
    def get_transition_probabilities(self):
        """Gets the probability distribution for the motif transitions"""
        return [trans.get_occurance_num()/float(self.total_occurances) for trans in self.transition_list]
    
    #----------------------------------------------------------------------
    def add_motif_transition(self, transition):
        """Add a motif transition to the transition list"""
        self.transition_list.append(transition)
        self.total_occurances += transition.get_occurance_num()
        
    #----------------------------------------------------------------------
    def choose_motif_transition(self, options):
        """Proportionally select a motif transition"""
        self.set_num_changes()
        choice_list = [self.transition_list[index] for index in options]
        total_changes = sum([choice.get_occurance_num() for choice in choice_list])
        val = random.randint(0, total_changes)
        accum = 0
        for transition in choice_list:
            accum += transition.get_occurance_num()
            if accum >= val:
                return (self.transition_list.index(transition),transition)
            
    #----------------------------------------------------------------------
    def get_left_hand_sides(self):
        """Returns a list of all the left hand sides for all transitions"""
        return [trans.get_lhs() for trans in self.transition_list]
    
    #----------------------------------------------------------------------
    def get_right_hand_sides(self):
        """Returns a list of all right hand sides for all transitions"""
        return [trans.get_rhs() for trans in self.transition_list]
        
    #----------------------------------------------------------------------
    def insert_motif_transition(self, lhs, rhs):
        """"""
        iso_found = False
        for transition in self.transition_list:
            if lhs == transition.get_lhs():
                if rhs == transition.get_rhs():
                    transition.inc_occurance_num()
                    iso_found = True
                    
            if iso_found:
                break
            
        if not iso_found:
            transition = MotifTransition(lhs, rhs, 1)
            self.add_motif_transition(transition)
            
    #----------------------------------------------------------------------
    def display_transitions(self):
        """"""     
        for transition in self.transition_list:
            lhs = transition.get_lhs().get_subgraph()
            rhs = transition.get_rhs().get_subgraph()
            plt.figure(1)
            pos=networkx.fruchterman_reingold_layout(lhs)         
            networkx.draw(lhs, pos)
            plt.figure(2)
            pos_1 = networkx.fruchterman_reingold_layout(rhs)
            networkx.draw(rhs, pos_1)
            plt.show()
            
    #----------------------------------------------------------------------
    def write_lhs_to_disk(self, path):
        """"""
        net_frame = NetworkFrames.NetworkFrames()
        for transition in self.transition_list:
            lhs = transition.get_lhs().get_subgraph()
            net_frame.addGraph(lhs)
            
        net_frame.writeGraphs(path)