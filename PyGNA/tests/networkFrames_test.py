from PyGNA import NetworkFrames
import sys
import os

testNetworks = NetworkFrames.NetworkFrames()

def setup_func(graphMLPath):
    import time
    sys.stderr.write("Processing: " + graphMLPath + "\n")
    start = time.clock()
    testNetworks.readGraphML(graphMLPath)
    sys.stderr.write("Read time - " + str(time.clock() - start) + "\n")
    #start = time.clock()
    #testNetworks.processNetworkFrames()
    #sys.stderr.write("Process time - " + str(time.clock() - start) + "\n")
    start = time.clock()
    testNetworks.compressNetworkFrames()
    sys.stderr.write("Compress time - " + str(time.clock() - start)+ "\n")
    start = time.clock()
    testNetworks.writeCompressedFrames('compressed.graphML')
    sys.stderr.write("Write Compressed Frames time - " + str(time.clock() - start)+ "\n")
    start = time.clock()
    testNetworks.decrompressNetworkFrames()
    sys.stderr.write("Decompress Frames time - " + str(time.clock() - start)+ "\n")
    start = time.clock()
    testNetworks.writeDecompressedFrames('decompressed.graphML')
    sys.stderr.write("Write Decompressed Frames time - " + str(time.clock() - start)+ "\n")
    
def teardown_func():
    global testNetworks
    testNetworks = NetworkFrames.NetworkFrames()
    if os.path.exists('compressed.graphML'):
        os.remove('compressed.graphML')
    if os.path.exists('decompressed.graphML'):
        os.remove('decompressed.graphML')
    
def network_frame_test():
    graphMLList = []
    teardown_func()
    for files in os.listdir(os.getcwd()):
        name, extension = os.path.splitext(files)
        if extension == '.graphML':
            graphMLList.append(files)
    for networks in graphMLList:
        setup_func(networks)
        yield compareOriginalToDecompressed
        teardown_func()
    teardown_func()
    
def compareOriginalToDecompressed():
    original = testNetworks.getInputNetworks()
    decompressed = testNetworks.getDecompressedFrames()
    returnValue = True
    
    if len(original) != len(decompressed):
        sys.stderr.write("The number of input network frames is inconsistant with the number of decompressed network frames.")
        returnValue = False
    
    if returnValue:
        returnValue = compareNetworkFrames(original, decompressed)
        
    assert returnValue

def compareNetworkFrames(firstFrames, secondFrames):
    returnValue = True
    frameIndex = 0
    while frameIndex < len(firstFrames) and returnValue:
        originalFrame = firstFrames[frameIndex]
        decompressedFrame = secondFrames[frameIndex]
        
        # Check number of nodes in each graph
        if len(originalFrame.nodes()) != len(decompressedFrame.nodes()):
            sys.stderr.write("Number of nodes inconsistant at index: " + str(frameIndex)+ "\n")
            returnValue = False
        # Check nodes
        else:
            # Check to see if each node in the original exists in the decompressed
            # Since the number of nodes is the same and duplicates aren't allowed it
            # should be sufficient to test in one direction
            for checkNode in originalFrame.nodes():
                if checkNode not in decompressedFrame.node:
                    sys.stderr.write("Node: " + str(checkNode) + " is not in decompressed graph at index: " + str(frameIndex)+ "\n")
                    returnValue = False
                else:
                    # Check node states
                    for states in originalFrame.node[checkNode]:
                        if states not in decompressedFrame.node[checkNode]:
                            sys.stderr.write("Decompressed frame at index: " + str(frameIndex) + " does not have state: " + str(states) + " for node: " + str(checkNode)+ "\n")
                            returnValue = False
                        elif originalFrame.node[checkNode][states] != decompressedFrame.node[checkNode][states]:
                            sys.stderr.write("State values are different for node: " + str(checkNode) + " for state: " + str(states)+ "\n")
                            returnValue = False
        if returnValue:
            # Check number of edges
            if len(originalFrame.edges()) != len(decompressedFrame.edges()):
                sys.stderr.write("Number of edges inconsistant at index: " + str(frameIndex)+ "\n")
                if len(originalFrame.edges()) > len(decompressedFrame.edges()):
                    for checkEdge in originalFrame.edges():
                        start = checkEdge[0]
                        end = checkEdge[1]
                        if start not in decompressedFrame.edge or end not in decompressedFrame.edge[start]:
                            sys.stderr.write("Edge (" + str(start) + "," + str(end) + ") does not exist in decompressed frame at index: " + str(frameIndex)+ "\n")
                else:
                    for checkEdge in decompressedFrame.edges():
                        start = checkEdge[0]
                        end = checkEdge[1]
                        if start not in originalFrame.edge or end not in originalFrame.edge[start]:
                            sys.stderr.write("Edge (" + str(start) + "," + str(end) + ") does not exist in input frame at index: " + str(frameIndex)+ "\n")
                returnValue = False
            # Check each edge for consistency
            else: 
                # Check to see that the individual edges are correct.  Since the number of edges are
                # the same and duplicates aren't allowed we should only have to check in one direction
                for checkEdge in originalFrame.edges():
                    start = checkEdge[0]
                    end = checkEdge[1]
                    if start not in decompressedFrame.edge or end not in decompressedFrame.edge[start]:
                        sys.stderr.write("Edge values inconsistent. Edge (" + str(start) + "," + str(end) + " does not exist in decompressed frame at index: " + str(frameIndex)+ "\n")
                        returnValue = False
                    if  returnValue:
                        for states in originalFrame.edge[start][end]:
                            if states not in decompressedFrame.edge[start][end]:
                                sys.stderr.write("Edge state does not exist.  Edge (" + str(start) + "," + str(end) +  ") with state: " + str(states) + ", does not exist in decompressed network at index: " + str(frameIndex) + "\n")
                                returnValue = False
                            elif originalFrame.edge[start][end][states] != decompressedFrame.edge[start][end][states]:
                                sys.stderr.write("Edge state inconsistant.  Edge (" + str(start) + "," + str(end) +  ") with value: " + str(originalFrame.edge[start][end][states] ) + \
                                                 ", has a different value from decompressed network; which has a value of:  " + + str(decompressedFrame.edge[start][end][states] ) + ".  At index: " + str(frameIndex) + "\n")
                                returnValue = False
                    
        frameIndex += 1
    
    return returnValue
