'''
This is a wrapper for the networkx graphml read/writer so that the GNA can
read a graphml file with multiple graphs.  The current networkx read_graphml
only returns the first element in the graph list that is returned by the 
graphMLReader class.
'''
import networkx.readwrite.graphml as ml

def read_graphml(path,node_type=str):
    """Read graph in GraphML format from path.

    Parameters
    ----------
    path : file or string
       File or filename to write.  
       Filenames ending in .gz or .bz2 will be compressed.

    node_type: Python type (default: str)
       Convert node ids to this type 

    Returns
    -------
    list(graphs): List of NetworkX graphs
        If no parallel edges are found a Graph or DiGraph is returned.
        Otherwise a MultiGraph or MultiDiGraph is returned.
        
    """
    # **Deprecated **  fh=ml._get_fh(path,mode='rb')
    reader = ml.GraphMLReader(node_type=int)
    # need to check for multiple graphs
    glist=list(reader(path))
    #return glist[0] <---- The current networkx read_graphml return value
    return glist # <---- returns the full list of graphs read from a file