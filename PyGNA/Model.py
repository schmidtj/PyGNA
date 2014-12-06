"""
Model base class used in the Extraction identification phase

"""
__author__ = """\n""".join(['Jeffrey Schmidt (jschmid1@binghamton.edu',
                            'Benjamin Bush (benjaminjamesbush@gmail.com)',
                            'Hiroki Sayama (sayama@binghamton.edu)'])

__all__ = ['addModel', 'getModelName','getModel','getLikelihoodValue']


#    Copyright (C) 2012 by
#    Jeffrey Schmidt <jschmid1@binghamton.edu>
#    Benjamin Bush <benjaminjamesbush@gmail.com>
#    Hiroki Sayama <sayama@binghamton.edu>
#    All rights reserved.
#    BSD license.

import NetworkFrames
import Extraction
import math
import csv

class Model(object):
    def __init__(self):
        self.modelFunction = None
        self.modelName = ''
        self.cumulativeExtraction = []
        self.cumulativeNetwork = []
        
    def __init__(self, model, name):
        self.modelFunction = model
        self.modelName = name
        self.cumulativeExtraction = []
        self.cumulativeNetwork = []    
        
    def _printDebugData(self):
        fileName = "incrementalLikelihood_%s.csv" % self.getModelName()
        f = open(fileName,'wb')
        writer = csv.writer(f)
        metaIncrementalLikelihoodList = []
        metaIncrementalLikelihoodList.append(self.cumulativeExtraction)
        metaIncrementalLikelihoodList.append(self.cumulativeNetwork)
        writer.writerows(metaIncrementalLikelihoodList)   
        f.close()        
        
    def addModel(self, model, modelName):
        """Mutator that adds a model to the model list and records the name of the model

        Parameters
        ----------
        model : Function object
           Model function to be used during extraction

        Returns
        -------
        void
        """
        self.modelFunction = model
        self.modelName = modelName
    
    def getModelName(self):
        """Accessor that returns the model name
        
        Parameters
        ----------
        None

        Returns
        -------
        modelName: string
           string name for the model
        """        
        return self.modelName
    
    def getModel(self):
        """Accessor that returns the model function
        
        Parameters
        ----------
        None

        Returns
        -------
        modelFunction: function object
           returns the function defined for this model
        """        
        return self.modelFunction
    
    def getLikelihoodValue(self, netFrames, index):
        """This function calculates a liklihood value for the network at the index passed in using
        the self.modelFunction that is defined
                
        Parameters
        ----------
        netFrames: NetworkFrames object
           The NetworkFrames object that the gna is currently analyzing
           
        index: integer
           Represents the index that we are currently working 

        Returns
        -------
        modelFunction: function object
           returns the function defined for this model
        """            
        extractionSubgraph = netFrames._getCompressedNetworkAt(index)
        extractionSubgraph = Extraction.Extraction().getExtractionSubgraphFromDelta(extractionSubgraph)        
        inputNetwork = netFrames.getInputNetworkAt(index-1)
        
        modelExtractionVal = 0.
        #for node in extractionSubgraph.nodes():
            #modelExtractionVal += self.getModel()(inputNetwork, node, netFrames.getStateName())
        modelExtractionVal = self.getModel()(inputNetwork, extractionSubgraph, netFrames.getStateName())
            
        modelNetworkVal = 0.
        #for node in inputNetwork.nodes():
         #   modelNetworkVal += self.getModel()(inputNetwork, node, netFrames.getStateName())
        modelNetworkVal = self.getModel()(inputNetwork, inputNetwork, netFrames.getStateName())
        
        logModelExtractionVal = float('-inf') if modelExtractionVal == 0. else math.log(modelExtractionVal)
        
        self.cumulativeExtraction.append(logModelExtractionVal)
        self.cumulativeNetwork.append(float('-inf')) if modelNetworkVal == 0. else self.cumulativeNetwork.append(math.log(modelNetworkVal))
        
        logLikelihoodVal = logModelExtractionVal - float('-inf') if modelNetworkVal == 0. else logModelExtractionVal - math.log(modelNetworkVal)
        
        return logLikelihoodVal
    
    