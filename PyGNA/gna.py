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
import MotifExtraction

class gna:
    def __init__(self, motif=False):
        self.networkFrames = NetworkFrames.NetworkFrames()
        self.extraction = Extraction.Extraction()
        self.motifExtraction = MotifExtraction.MotifExtraction()
        self.rewriting = Rewriting.Rewriting()
        #self.models = Models.Models()
        self.utility = Utility.utility()
        self.simulation = Simulation.Simulation(self.motifExtraction, self.rewriting, self.networkFrames)
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
    
    #----------------------------------------------------------------------
    def add_recipe_models(self):
        """"""
        self.models.add_recipe_models(self)
        
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
        #self.networkFrames.setInputNetwork([self.networkFrames.inputFrames[index] for index in range(9)])
        self.networkFrames.setInputNetwork(self.networkFrames.inputFrames)
        print "Done"
        print "Analyzing dynamics...",
        self.networkFrames.compressNetworkFrames()
        print "Done."
        self.extraction.setNetworkFrames(self.networkFrames)
        self.motifExtraction.setNetworkFrames(self.networkFrames)

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
        
        
    def runGNA(self, iterations, motifSize, motif=False, sampleSize=None):
        """Main GNA function that runs the Automaton
        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.simulation.setIterations(iterations)
        
        #self.simulation.runMotifSimulation(motifSize) if motif else self.simulation.runSimulation()
        self.simulation.runIterativeMotifSimulation(motifSize, sampleSize) if motif else self.simulation.runSimulation() 
        
    #----------------------------------------------------------------------
    def run_recipe_GNA(self):
        """"""
        self.simulation.run_recipe_simulation()
        

import cProfile, pstats, StringIO, time
if __name__ == "__main__":
    myGna = gna(True)
    query = raw_input("Do you want to process a new file? (Y/N) ")
    if query.strip() == "Y" or query.strip() == "y":
        path = raw_input("Enter file name: ")
        #motifSize = int(raw_input("Enter motif size: "))
        #iterations = input("Enter number of simulation iterations: ")
        #sampleSize = int(raw_input("Enter sample size: "))
        #if iterations <= 0:
        #    iterations = 1
            
        myGna.openGraphMLNetwork(path)   
        start = time.time()
        #myGna.motifExtraction.sampleNetwork(motifSize, sampleSize)
        elapsed = time.time() - start
        print elapsed
        #myGna.addDefaultModels()
        #myGna.add_recipe_models()
        #myGna.findExtractionMechanism()
        #myGna.initializeRewritingData()
        myGna.run_recipe_GNA()
    else:
        path = raw_input("Enter original data file: ")
        pathTwo = raw_input("Enter generated data file: ")
        myGna.readExistingData(path, pathTwo)
        
 
        ##Profile code:
               #pr = cProfile.Profile()
               #pr.enable()        
               #pr.disable()
               #s = StringIO.StringIO()
               #sortby = 'cumulative'
               #ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
               #ps.print_stats()
               #print s.getvalue()                