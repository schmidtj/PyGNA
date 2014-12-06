"""
GNA base class.

"""
__author__ = """\n""".join(['Jeffrey Schmidt (jschmid1@binghamton.edu',
                            'Benjamin Bush (benjaminjamesbush@gmail.com)',
                            'Hiroki Sayama (sayama@binghamton.edu)'])

__all__ = ['openGraphMLNetwork','runGNA','addGraphToReproducedInput', 'addUserExtractions','addDefaultModels',
           'initializeRewritingData','findExtractionMechanism']


#    Copyright (C) 2012 by
#    Jeffrey Schmidt <jschmid1@binghamton.edu>
#    Benjamin Bush <benjaminjamesbush@gmail.com>
#    Hiroki Sayama <sayama@binghamton.edu>
#    All rights reserved.
#    BSD license.

import networkx as nx
import copy
import graphMLRead
import NetworkFrames
import Extraction
import Rewriting
import Simulation
import Models
import csv
import CollectData
import Utility

class gna:
    def __init__(self):
        self.networkFrames = NetworkFrames.NetworkFrames()
        self.extraction = Extraction.Extraction()
        self.rewriting = Rewriting.Rewriting()
        self.models = Models.Models()
        self.utility = Utility.utility()
        self.simulation = Simulation.Simulation(self.extraction, self.rewriting, self.utility, self.networkFrames)
        self.simulationIterations = 1
        
    
    def addDefaultModels(self):
        """Adds the default Model objects to the list of models to try during Extraction
        
        Parameters
        ----------
        void

        Returns
        -------
        void
        """         
        self.models.addDefaultModelsToList()
        
    def addModel(self, model):
        """Adds a Model object to the list of model objects to try during Extraction

        Parameters
        ----------
        model : Model object
           Model object to be added to the list

        Returns
        -------
        void
        """        
        self.models.addModel(model)
         
    def addUserExtractions(self, userExtractionClass):
        """Adds user Model objects to the list of model objects to try during Extraction

        Parameters
        ----------
        userExtractionClass : user defined class (inherited from userExtractions object)
           Contains model objects to be added to the model list

        Returns
        -------
        void
        """
        userObject = userExtractionClass()
        super(type(userObject),userObject).buildModels()
        
        for model in super(type(userObject),userObject).getModels():
            self.addModel(model)
         
    def openGraphMLNetwork(self, path):
        """Reads a graphML file and stores the data in a list of networkx graph objects.

        Parameters
        ----------
        path : string path
           Path to the graphml file

        Returns
        -------
        void
        """
        print "Reading file...",
        self.networkFrames.readGraphML(path)
        print "Done"
        print "Analyzing dynamics...",
        self.networkFrames.compressNetworkFrames()
        print "Done."
        self.extraction.setNetworkFrames(self.networkFrames)

    def findExtractionMechanism(self):
        """ Identify the Extraction mechanism in the input data.
        Parameters
        ----------
        none

        Returns
        -------
        void
        """
        
        self.extraction.setModels(self.models.getModelList())
        self.extraction.generateExtractionSubgraphs()
        self.extraction.identifyExtractionDynamics()

    def initializeRewritingData(self):
        """ Initialize the Rewriting data structures.
        Parameters
        ----------
        none

        Returns
        -------
        void
        """
        self.rewriting.setNetworkFrames(self.networkFrames)
        self.rewriting.initializeRewritingData()
    
    def readExistingData(self, originalPath, generatedPath):
        """Reads existing input and generated data and produces graphical analysis of the two adaptive networks.
        Parameters
        ----------
        None

        Returns
        -------
        None
        """        
        original = NetworkFrames.NetworkFrames()
        generated = NetworkFrames.NetworkFrames()
        
        print "Reading original data..."
        original.readGraphML(originalPath)
        print "Done."
        print "Compressing Network Frames in original data..."
        original.compressNetworkFrames()
        print "Done."
        print "Reading generated data..."
        generated.readGraphML(generatedPath)
        print "Done."
        print "Compressing Network Frames in generated data..."
        generated.compressNetworkFrames()
        print "Done."
        
        print "Displaying Nodes vs. Edge data..."
        collectInputData= CollectData.CollectData(original.getInputNetworks(), generated.getInputNetworks())
        collectInputData.nodesVSedges()
        print "Done."
        
        print "Displaying Dynamics Information..."
        collectCompressedData = CollectData.CollectData(original._getCompressedNetworks(), generated._getCompressedNetworks())
        collectCompressedData.dynamicsInfo()
        print "Done."
        
        
    def runGNA(self, iterations):
        """Main GNA function that runs the Automaton
        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.simulation.setIterations(iterations)
        self.simulation.runSimulation()
                
            
if __name__ == "__main__":
    myGna = gna()
    query = raw_input("Do you want to process a new file? (Y/N) ")
    if query.strip() == "Y" or query.strip() == "y":
        path = raw_input("Enter file name: ")
        iterations = input("Enter number of simulation iterations: ")
        if iterations <= 0:
            iterations = 1
        myGna.openGraphMLNetwork(path)
        myGna.addDefaultModels()
        myGna.findExtractionMechanism()
        myGna.initializeRewritingData()
        myGna.runGNA(iterations)
    else:
        path = raw_input("Enter original data file: ")
        pathTwo = raw_input("Enter generated data file: ")
        myGna.readExistingData(path, pathTwo)
        
 
    