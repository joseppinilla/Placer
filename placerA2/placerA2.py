import time
import sys
import getopt
import placerGUI
import random
import numpy as np
import Tkinter as tk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg


class Placer():
      
    def __init__(self,master,argv):
        
        
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
                print 'test.py [-v] -i <inputfile>'
                sys.exit()
            elif opt in ("-i", "--ifile"):
                inputfile = arg
                print "Read file " + inputfile
            elif opt in ("-v", "--verbose"):
                print "Setup Verbose"
                self.verbose = True
        
        if (not inputfile):
            print 'test.py -i <inputfile>'
            sys.exit(2)
               
        
        #=============Parse file to create cells graph===============#
        self.G=nx.Graph()
        fin = open(inputfile,'r')
        self.getGraph(fin)
        fin.close() 
        
        
        #================Create Data Structures================# 
        # Array of Line objects to draw connections
        self.connLines = []
        # Array of Block objects drawing the rectangles for each site on the circuit, tracks occupancy
        self.sites = []
        # Array of Text objects noting the name of the node assigned to a cell site 
        self.tags = []
        
        #================Draw Buttons and plots================#
        self.master = master
        self.initialize_buttons()
        self.initialize_plots()
        
        #===============Start conditions================#
        self.initialize_start()

    def initialize_buttons(self):
        """"""
        self.start_button = tk.Button(self.master, text='start', command = self.startrecording)
        self.start_button.grid(row=0, column=0)

        self.stop_button = tk.Button(self.master, text='stop', command = self.stoprecording)
        self.stop_button.grid(row=0, column=1)

        self.clear_button = tk.Button(self.master, text='clear', command = self.clear_all)
        self.clear_button.grid(row=0, column=2)  


    def initialize_start(self):
        """"""
        self.stop_button['state'] = 'disabled'
        self.clear_button['state'] = 'disabled'  

        self.firstmeasurement = True    # initialize counter of measurements
        self.isrecording = False

    def f(self, t):
        return np.exp(-t) * np.cos(2*np.pi*t)

    def initialize_plots(self):
        """"""
        # Draw circuit canvas with hard coded width 600 and adjustable height to circuit input
        ckt_max_x = 600
        ckt_max_y = (ckt_max_x*(self.rows))/self.cols
        scale_x = round(ckt_max_x / self.cols)
        scale_y = round(ckt_max_y / self.rows)
        
        self.canvasCirkt = tk.Canvas(self.master,width=ckt_max_x,height=(ckt_max_y*2)+int(scale_y))
        self.canvasCirkt.grid(row=1,column=0,columnspan=2)
        
        # Draw border
        self.canvasCirkt.create_rectangle(1, 1, ckt_max_x, (ckt_max_y*2)+int(scale_y))
        
        #====Draw cell rows spaced by routing channels=====#
        
        for cut in range(int(scale_y), int(ckt_max_y*2), int(scale_y)*2):
            for cut2 in range(1, int(ckt_max_x), int(scale_x)):
                # Coordinates for top and bottom points of rectangle
                points = (cut2, cut, cut2+scale_x-1, cut+scale_y)
                blockObj = placerGUI.Block(self.canvasCirkt,points)
                self.sites.append(blockObj)
                
        print "NUMBER OF SITES ", len(self.sites)
        # Draw Figure for 2 subplots (Connections Graph and Cost Function)        
        self.figure, self.axes = plt.subplots(2)
        self.figure.set_figwidth(4)
        self.axGraph = self.axes[0]
        self.axCost = self.axes[1]
                
        # Draw connection Graph
        nx.draw(self.G, ax=self.axGraph, with_labels=True)
        
        # Initialize cost function plot
        t1 = np.arange(0.0, 5.0, 0.1)
        t2 = np.arange(0.0, 5.0, 0.02)
                
        plt.sca(self.axCost)
        plt.plot(t1, self.f(t1), 'bo', t2, self.f(t2), 'k')        

        self.canvasPlot = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvasPlot.get_tk_widget().grid(row=1,column=2)
        
    def clear_all(self):
        plt.clf()
        self.initialize_plot()
        self.initialize_start()


    def startrecording(self):
        self.start_button['state'] = 'disabled'
        self.stop_button['state'] = 'normal'
        self.clear_button['state'] = 'disabled'
        self.isrecording = True
        self._startplacement()

    def stoprecording(self):
        self.start_button['state'] = 'normal'
        self.stop_button['state'] = 'disabled'
        self.clear_button['state'] = 'normal'

        self.isrecording = False

    def quitApp(self):
        self.master.destroy()
        self.master.quit()
          
    def getGraph(self, fin):
        tmpList = fin.readline().split()
        self.cells = int(tmpList[0])
        self.conns = int(tmpList[1])
        self.rows =  int(tmpList[2])
        self.cols =  int(tmpList[3])
        
        print tmpList
        
        self.G.add_nodes_from(range(0,self.cells))
        
        for conn in range(0,self.conns):
            tmpList = fin.readline().split()
            numBlocks = int(tmpList[0])
            srcBlock = int(tmpList[1])
            self.G.node[srcBlock]["net"] = conn
            for block in range(2,numBlocks+1):
                sinkBlock = int(tmpList[block])
                self.G.node[sinkBlock]["net"] = conn               
                self.G.add_edge(srcBlock, sinkBlock)   


    
    def _startplacement(self):
        
        self.randPlace()
        
#         print "HERE" #TODO: Placement algorithm   
#         time.sleep(2)
#         self.axGraph.cla()
#         self.G.remove_node(0)
#         nx.draw(self.G, ax=self.axGraph, with_labels=True)
#         self.canvasPlot.draw()
#         self.canvasPlot.flush_events()            


    def randPlace(self):
        random.seed(30) #TODO: Adjustable Seed
        sitesNum = self.rows*self.cols-1
        for node in self.G.nodes():
            randSite = random.randint(0,sitesNum)
            while (self.sites[randSite].isOcp()):
                randSite = random.randint(0,self.cells)    
            
            self.sites[randSite].setCell(node)
            self.G.node[node]["site"] = self.sites[randSite]
                        
        self.drawConns()
        time.sleep(3)
        self.drawTags()
        time.sleep(3)
        self.delConns()
        time.sleep(3)
        self.delTags()
            
    def drawConns(self):
        """ Extract center point from each node and draw connection to other nodes """
        #TODO: Draw each connection once
        for node in self.G.nodes():
                       
            pX,pY = self.G.node[node]["site"].getCenter()
            for nb in self.G.neighbors(node):
                nbX,nbY = self.G.node[nb]["site"].getCenter()
                self.connLines.append(self.canvasCirkt.create_line(pX,pY,nbX,nbY))

            self.canvasCirkt.update()
            
    
    def drawTags(self):
        """ Extract center point from each node and draw node Tag """
        for node in self.G.nodes():
            pX,pY = self.G.node[node]["site"].getCenter()
            self.tags.append(self.canvasCirkt.create_text(pX, pY, text=node))            
        self.canvasCirkt.update()
    
    def delConns(self):
        """ Delete Connections on Circuit using array of Line objects """
        for line in self.connLines:
            self.canvasCirkt.delete(line)
        self.canvasCirkt.update()    
            
    def delTags(self):
        """ Delete Tags on Circuit using array of Text objects """
        for tag in self.tags:
            self.canvasCirkt.delete(tag)
        self.canvasCirkt.update()
        
            
        
            
    



root = tk.Tk()
placer = Placer(root,sys.argv[1:])
root.protocol('WM_DELETE_WINDOW', placer.quitApp)
root.mainloop()

