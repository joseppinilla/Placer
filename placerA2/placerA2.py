import time
import sys
import getopt
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
               
        
        #=================Parse file to create graph=================#
        self.G=nx.Graph()
        fin = open(inputfile,'r')
        self.getGraph(fin)
        fin.close() 
        
        self.master = master
        self.initialize_buttons()
        self.initialize_plots()
        self.initialize_start()

    def initialize_buttons(self):
        self.start_button = tk.Button(self.master, text='start', command = self.startrecording)
        self.start_button.grid(row=0, column=0)

        self.stop_button = tk.Button(self.master, text='stop', command = self.stoprecording)
        self.stop_button.grid(row=0, column=1)

        self.clear_button = tk.Button(self.master, text='clear', command = self.clear_all)
        self.clear_button.grid(row=0, column=2)  


    def initialize_start(self):
        self.stop_button['state'] = 'disabled'
        self.clear_button['state'] = 'disabled'  

        self.firstmeasurement = True    # initialize counter of measurements
        self.isrecording = False

    def f(self, t):
        return np.exp(-t) * np.cos(2*np.pi*t)

    def initialize_plots(self):
        print "init plot start"
        
        t1 = np.arange(0.0, 5.0, 0.1)
        t2 = np.arange(0.0, 5.0, 0.02)
        
        # initialize figure        
        self.figure, self.axes = plt.subplots(2,figsize=(4,8))
        self.axGraph = self.axes[0]
        self.axCost = self.axes[1]
        
        nx.draw(self.G, ax=self.axGraph, with_labels=True)
                
        plt.sca(self.axCost)
        plt.plot(t1, self.f(t1), 'bo', t2, self.f(t2), 'k')        

        self.canvasPlot = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvasPlot.get_tk_widget().grid(row=1,column=2)
        
        ckt_max_x = 800
        self.canvasCirkt = tk.Canvas(self.master,width=ckt_max_x)
        self.canvasCirkt.grid(row=1,column=0,columnspan=2)
        
        
        ckt_max_y = (ckt_max_x*(self.rows*2))/self.cols
        scale_x = round(ckt_max_x / self.cols)
        scale_y = round(ckt_max_y / self.rows)
        
        #for cut in range(int(scale_y), int(win_max_y + 1), int(scale_y)):
    
         #   for cut2 in range(int(scale_x), int(win_max_x + 1), int(scale_x)):
        
          #      point1 = graphics.Point(cut2, cut)
           #     point2 = graphics.Point(cut2 - scale_x, cut - scale_y)           
            #    blockObj = Block(win,point1,point2)
             #   blocks.append(blockObj)
              #  blockIndex+=1

        


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
        
    def _startplacement(self):
        
        print "HERE" #TODO: Placement algorithm   
        time.sleep(2)
        self.axGraph.cla()
        self.G.remove_node(0)
        nx.draw(self.G, ax=self.axGraph, with_labels=True)
        self.canvasPlot.draw()
        self.canvasPlot.flush_events()            
    
    def getGraph(self, file):
        tmpList = file.readline().split()
        self.cells = int(tmpList[0])
        self.conns = int(tmpList[1])
        self.rows =  int(tmpList[2])
        self.cols =  int(tmpList[3])
        
        print tmpList
        
        self.G.add_nodes_from(range(0,self.cells))
        
        for conn in range(0,self.conns):
            tmpList = file.readline().split()
            numBlocks = int(tmpList[0])
            srcBlock = int(tmpList[1])
            for block in range(2,numBlocks+1):
                self.G.add_edge(srcBlock, int(tmpList[block]))   



root = tk.Tk()
placer = Placer(root,sys.argv[1:])
root.protocol('WM_DELETE_WINDOW', placer.quitApp)
root.mainloop()

