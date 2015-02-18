import sys
import getopt
import mazeRouter
from itertools import permutations
import routerGUI
import networkx as nx
import matplotlib.pyplot as plt

def main(argv):
    
    
    #=================Get options=================#
    inputfile = None
    verbose = False
    try:
        opts, args = getopt.getopt(argv, "hvi:", ["ifile="])
    except getopt.GetoptError:
        print 'test.py [-v] -i <inputfile>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -i <inputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-v", "--verbose"):
            verbose = True
    
    if (not inputfile):
        print 'test.py -i <inputfile>'
        sys.exit(2)
       
    outputfile = "../log.log"
    
    
    #=================Parse file to create graph=================#
    G=nx.Graph()
    fin = open(inputfile,'r')
    getGraph(fin,G,verbose)
    fin.close() 
    
      
    
def getGraph(file, G, verbose):
    tmpList = file.readline().split()
    cells = int(tmpList[0])
    conns = int(tmpList[1])
    rows =  int(tmpList[2])
    cols =  int(tmpList[3])
    
    G.add_nodes_from(range(0,cells))
    
    for conn in range(0,conns):
        tmpList = file.readline().split()
        numBlocks = int(tmpList[0])
        srcBlock = int(tmpList[1])
        for block in range(2,numBlocks+1):
            G.add_edge(srcBlock, int(tmpList[block]))   
    
    
    if verbose:
        nx.draw(G)
        plt.show()
   

if __name__ == "__main__":
    main(sys.argv[1:])		



