import time
import sys
import getopt
import placerGUI
import random
import math
import numpy as np
import Tkinter as tk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg


class Placer():
    """ Circuit Cell placement using Simulated Annealing
        Circuit: A representation of a circuit by rows and columns
        Cell: Circuit component represented as a Graph node with connections to other Cells as edges
        Site: Possible location for a Cell (Is Free or is occupied by a Cell)
        Block: Graphic representation and data of a Site
    
     """  
    def __init__(self,master,argv):
        
        
        #=================Get options=================#
        inputfile = None
        try:
            opts, args = getopt.getopt(argv, "hi:", ["ifile="])
        except getopt.GetoptError:
            print 'test.py -i <inputfile>'
            sys.exit(2)
    
        for opt, arg in opts:
            if opt == '-h':
                print 'test.py -i <inputfile>'
                sys.exit()
            elif opt in ("-i", "--ifile"):
                inputfile = arg
                print "Read file " + inputfile
        
        if (not inputfile):
            print 'test.py -i <inputfile>'
            sys.exit(2)
               
        
        #=============Parse file to create cells graph===============#
        
        # Create Directed Graph and fill with input file
        self.G=nx.DiGraph()
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
        
        #TODO: Is this right?
        self.value_x = 0
        
        #================Draw Buttons and plots================#
        self.master = master
        self.initialize_buttons()
        self.initialize_plots()
        
        #===============Start conditions================#
        self.initialize_start()

    def initialize_buttons(self):
        """ Draw User Buttons on top of interface 
            Start: Begin placement process
            Stop: Stop process
            Clear: Erase Graph and Plot
            #TODO: At the end, complete these
        """
        self.start_button = tk.Button(self.master, text='Start', command = self.startRunning)
        self.start_button.grid(row=0, column=0)

        self.stop_button = tk.Button(self.master, text='Stop', command = self.stopRunning)
        self.stop_button.grid(row=0, column=1)

        self.clear_button = tk.Button(self.master, text='Clear', command = self.clearAll)
        self.clear_button.grid(row=0, column=2)
        
        self.display_button = tk.Button(self.master, text='No Display', command = self.setDisplay)
        self.display_button.grid(row=0, column=3)


    def initialize_start(self):
        """ #TODO: Using this? For initialization of flags
        """
        self.stop_button['state'] = 'disabled'
        self.clear_button['state'] = 'disabled'
        self.display_button['state'] = 'normal'  
        # Boolean switch to control flow of placement process
        self.running = False
        # Boolean switch to display placement connections and tags, turn off for faster processing
        self.display = True

    def f(self, t): #TODO: Remove
        return np.exp(-t) * np.cos(2*np.pi*t)

    def initialize_plots(self):
        """ Draw all graphic components as Canvases
            Circuit Canvas: Drawing of the Circuit Sites Rows and Columns to overlay Cell Placement and Connections
            Graph Canvas: Drawing of the Graph structure used for the representation of the Cells
            Cost Plot Canvas: Plotting of the Cost Function used in the Annealing Process
            Plot Toolbar: Toolbar options to explore the Graph and Cost Canvases (Zoom, Save, Move...)
         """
        #============================Draw circuit canvas=================================#
        # Draw Canvas with hardcoded width 600 and adjustable height to circuit input
        ckt_max_x = 600
        ckt_max_y = (ckt_max_x*(self.rows))/self.cols
        scale_x = round(ckt_max_x / self.cols)
        scale_y = round(ckt_max_y / self.rows)
        self.canvasCirkt = tk.Canvas(self.master,width=ckt_max_x,height=(ckt_max_y*2)+int(scale_y))
        self.canvasCirkt.grid(row=1,column=1,columnspan=3)

        # Draw border
        self.canvasCirkt.create_rectangle(1, 1, ckt_max_x, (ckt_max_y*2)+int(scale_y))
        
        # Draw cell rows spaced by routing channels
        blockIndex=0
        for cut in range(int(scale_y), int(ckt_max_y*2), int(scale_y)*2):
            for cut2 in range(1, int(ckt_max_x), int(scale_x)):
                # Coordinates for top and bottom points of rectangle
                points = (cut2, cut, cut2+scale_x-1, cut+scale_y)
                blockObj = placerGUI.Block(self.canvasCirkt,points,blockIndex,self.rows,self.cols)
                blockIndex+=1
                self.sites.append(blockObj)
                
        #===================================Draw Plots================================#
        # Draw Figure for 2 subplots (Connections Graph and Cost Function)        
        self.figure, self.axes = plt.subplots(2)
        self.figure.set_figwidth(4)
        self.axGraph = self.axes[0]
        self.axCost = self.axes[1]
                
        # Draw connection Graph
        nx.draw(self.G, ax=self.axGraph, with_labels=True)
        
        # Initialize cost function plot
        #t1 = np.arange(0.0, 5.0, 0.1) #TODO: Change for real cost function
        #t2 = np.arange(0.0, 5.0, 0.02)
                
        plt.sca(self.axCost)
        #plt.plot(t1, self.f(t1), 'bo', t2, self.f(t2), 'k')        
        self.lines, = self.axCost.plot([],[])
        # Draw Cost function Plot
        self.canvasPlot = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvasPlot.get_tk_widget().grid(row=1,column=0)
        
        # Draw Tool Bar
        self.toolbarFrame = tk.Frame(self.master)
        self.toolbarFrame.grid(row=2,column=0,columnspan=3,sticky="W")
        self.toolbarPlot = NavigationToolbar2TkAgg(self.canvasPlot,self.toolbarFrame)
        self.toolbarPlot.toolitems
        
    def clearAll(self):
        plt.clf()
        self.initialize_plot()
        self.initialize_start()

    def startRunning(self):
        self.start_button['state'] = 'disabled'
        self.stop_button['state'] = 'normal'
        self.clear_button['state'] = 'disabled'
        self.running = True
        self.start_timer = time.clock()
        self.start_button.config(text = "Continue",command=self.contRunning)
        self._startplacement()

    def contRunning(self):
        self.start_button['state'] = 'disabled'
        self.stop_button['state'] = 'normal'
        self.clear_button['state'] = 'disabled'
        self.running = True
        

    def stopRunning(self):
        self.start_button['state'] = 'normal'
        self.stop_button['state'] = 'disabled'
        self.clear_button['state'] = 'normal'
        self.running = False

    def setDisplay(self):
        self.display = not self.display
        if self.display:
            self.display_button['text'] = "No Display"
        else:
            self.display_button['text'] = "Display"
        

    def quitApp(self):
        self.master.destroy()
        self.master.quit()
          
    def getGraph(self, fin):
        """ Parse Input File to fill up Graph structure """
        tmpList = fin.readline().split()
        # Number of Cells to be placed
        self.cells = int(tmpList[0])
        # Number of Connections or Nets
        self.conns = int(tmpList[1])
        # Number of Circuit Rows
        self.rows =  int(tmpList[2])
        # Number of Circuit Columns
        self.cols =  int(tmpList[3])
        # Number of available sites in the Circuit
        self.sitesNum = self.rows*self.cols
        
        # Add nodes from 0 to number of Cells to graph structure        
        self.G.add_nodes_from(range(0,self.cells))
        
        # For every Net, add edges between corresponding nodes
        for conn in range(0,self.conns):
            tmpList = fin.readline().split()
            numBlocks = int(tmpList[0])
            srcBlock = int(tmpList[1])
            for block in range(2,numBlocks+1):
                self.G.add_edge(srcBlock, int(tmpList[block]))   


    
    def _startplacement(self):
        
        self.randPlace()
        oldCost = self.cost()
        
        if (self.display):
            self.drawConns()
            self.drawTags()
            self.updatePlot(oldCost)
        
        #while self.running:
                      
        T = 0.99
        while (T>0.1):
            
            for k in range(0,100): #TODO: Try other numbers
                
                if (self.running):
    
                    #time.sleep(1)
                    swapCell, swapSite = self.swapRand()
                    newCost = self.cost()
                    deltaNCost = 0-(newCost - oldCost)
                    
                    rand = random.random()
    
                    if (rand < math.exp(deltaNCost/T)):
                        # Take move
                        oldCost = newCost
                        if (self.display):
                            self.updateGraph()
                            self.updatePlot(newCost)
                        
                    else:
                        # Revert move  
                        self.swap(swapCell,swapSite)

            T=0.99*T
                
    def swapRand(self):
        """ Select Random Cell and swap into Random Site  """
        # Pick Random Cell so the move is always from an occupied to a free/occupied cell
        randCell = random.randint(0,self.cells-1)
        # Store Site of Cell to be swapped to use for Swap Back 
        randCellSite = self.G.node[randCell]["site"].getIndex()
        
        # Pick Random Site. Can be free
        randSite = random.randint(0,self.sitesNum-1)
        
        # Do swap
        self.swap(randCell,randSite)
        
        return randCell, randCellSite
    
    def swap(self,swapCell,swapSite):
        """ Swap Cell(occupying site) to given Target Site(could be free) """
        
        # Target Site can be empty
        if (self.sites[swapSite].isFree()):
            # Free Cell value of Random Cell
            self.G.node[swapCell]["site"].free()

        else:
            # Store Cell value of Target Site
            tgtSiteCell = self.sites[swapSite].getCell()
            # Write Cell value of Target Site into Swap Cell
            self.G.node[swapCell]["site"].setCell(tgtSiteCell)
            # Node of Target Site's Cell now points to Swap Cell's Site
            self.G.node[tgtSiteCell]["site"] = self.G.node[swapCell]["site"]
            
        # Write Cell value of Swap Cell into Target Site 
        self.sites[swapSite].setCell(swapCell)
        # Node of Swap Cell now points to Target Site
        self.G.node[swapCell]["site"] = self.sites[swapSite]
                 
    def updateGraph(self):
        self.delConns()
        self.delTags()
        self.drawConns()
        self.drawTags()
    
    def updatePlot(self,cost):

        timer = time.clock() - self.start_timer
        # Add new values to plot data set        
        self.lines.set_xdata(np.append(self.lines.get_xdata(), timer))
        self.lines.set_ydata(np.append(self.lines.get_ydata(), cost))
        
        # Re-scale
        self.axCost.relim()
        self.axCost.autoscale_view()
        # Update plot
        self.canvasPlot.draw()
        self.canvasPlot.flush_events()
        
        

    def randPlace(self):
        random.seed(30) #TODO: Adjustable Seed
        
        for node in self.G.nodes():
            randSite = random.randint(0,self.sitesNum-1)
            
            
            while (self.sites[randSite].isOcp()):
                randSite = random.randint(0,self.cells)    
            
            self.sites[randSite].setCell(node)
            self.G.node[node]["site"] = self.sites[randSite]
                                    
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
        
    def cost(self):
        """ Seeing the circuit as a matrix The distance units between sites can be found as the difference
        between their axes locations. 
        
        A=(0,0)    B=(3,0)    C=(0,3)
        
           v...........v
        >| A |   |   | B |    Cell Sites Row
        :#################    Routing Channel
        :|   |   |   |   |    Cell Sites Row
        :#################    Routing Channel
        :|   |   |   |   |    Cell Sites Row
        :#################    Routing Channel
        >| C |   |   |   |    Cell Sites Row
        
        Therefore:
            X Distance between the center of A and B
            DistX = BX-AX
            Y Distance between the center of A and C accounting for the Routing Channels
            DistY = (CX-AY)*2
        
        """
        
        cost = 0
        for node in self.G.nodes():
            # Initialize bounding box points on net source
            srcX,srcY = self.G.node[node]["site"].getBlockXY(self.cols,self.rows)
            minX, maxX = srcX, srcX
            minY, maxY = srcY, srcY
            
            # Find bounding box with min and max for X and Y
            for nb in self.G.neighbors(node):
                nbX,nbY = self.G.node[nb]["site"].getBlockXY(self.cols,self.rows)
                if (nbX>maxX):
                    maxX=nbX
                elif(nbX<minX):
                    minX=nbX
                if(nbY>maxY):
                    maxY=nbY
                elif(nbY<minY):
                    minY=nbY
            
            # Accumulate cost as Half Perimeter of Bounding Box for every net
            cost += (maxX-minX) + ((maxY-minY)*2)
        
         
        return cost

root = tk.Tk()
placer = Placer(root,sys.argv[1:])
root.protocol('WM_DELETE_WINDOW', placer.quitApp)
root.resizable(False, False)
root.mainloop()

