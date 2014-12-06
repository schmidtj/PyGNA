"""
IO class.

"""
__author__ = """\n""".join(['Jeffrey Schmidt (jschmid1@binghamton.edu',
                            'Hiroki Sayama (sayama@binghamton.edu)'])

__all__ = ['readUpperhalfMatrix']

#    Copyright (C) 2014 by
#    Jeffrey Schmidt <jschmid1@binghamton.edu>
#    Hiroki Sayama <sayama@binghamton.edu>
#    All rights reserved.
#    BSD license.

import networkx as nx
import NetworkFrames
import numpy
import os

class io(object):
    def __init__(self):
        self.inputgraph = None
        self.inputpath = None
    
    def getInputGraph(self):
        return self.inputgraph
    
    def resetData(self):
        self.inputgraph = None
        self.inputpath = None
    
    def readUpperhalfMatrix(self, path):
        try:
            f = open(path, 'r')
        except IOError as e:
            print "I/O error({0}): {1}" %(e.errno, e.strerror)
        else:
            #Save the path
            self.inputpath = path + ".graphML"
            
            #read the size of the matrix
            num = int(f.readline().lstrip("dl n="))
            
            #Check for upperhalf format
            format = f.readline().lstrip("format = ").rstrip()
            if format != "upperhalf":
                raise AttributeError('Format is not upperhalf')
            
            #Ignore line
            lines = f.readline()
            lines = f.readline().rstrip()
            
            #read labels
            nodes = []
            while lines != "data:":
                nodes.extend([int(x) for x in lines.split(",")])
                lines = f.readline().rstrip()
            
            #Add labels(nodes) to graph
            self.inputgraph = nx.Graph()
            self.inputgraph.name= path

            for node in nodes:
                self.inputgraph.add_node(node)
            
            #read upperhalf matrix
            toread = num
            totalLines = 0
            while toread > 0:
                for x in xrange(0, toread):
                    line = int(f.readline())
                    totalLines += 1
                    if line != 0:
                        self.inputgraph.add_edge(nodes[num-toread],nodes[x], value=line)
                toread -= 1
                
            f.close()
            #self.saveAsGraphML()
            
    def saveAsGraphML(self):
        if self.inputgraph != None:
            nx.graphml.write_graphml(self.inputgraph, self.inputpath)
                
if __name__ == "__main__":
    directory = raw_input("Please enter the directory where the data exists: ")
    if os.path.exists(directory):
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        files = sorted(files)
        frames = NetworkFrames.NetworkFrames()
        read = io()
        for file in files:
            read.readUpperhalfMatrix(os.path.join(directory, file))
            frames.addGraph(read.getInputGraph())
            read.resetData()
            
        networks = directory + "networks.graphML"
        frames.writeGraphs(networks)