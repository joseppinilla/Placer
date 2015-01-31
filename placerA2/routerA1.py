import sys
import getopt
import mazeRouter
from itertools import permutations
import routerGUI

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
    
    #=================Draw window with grid. Create blocks and nets=================#   
    blocks = []
    nets = []
    fin = open(inputfile,'r')
    win = routerGUI.drawRouter(fin,blocks,nets)
    fin.close()
    
    #===================Wait for user input on execution mode================#
    while(True):
        key = win.getKey()
        if key == 'q': #quit 
            sys.exit()     
        elif (key in ('r','s','t')): #Run, Stepped, Timed
            if (key=='t'):
                key = win.getKey() #X * 0.1s
            
            
            print nets
            
            allNets = list(permutations(nets))
            
            lenAll = len(allNets)
            i=0
            
            print allNets[0]
            
            while((not mazeRouter.start(win,blocks,allNets[i],key,verbose)) and i<lenAll):
                i += 1

            for net in nets:
                print "Wire Len ", net.id, net.wlen       
                fout = open(outputfile,'w+')
                fout.write("Wire Len " + str(net.id) + str(net.wlen))
                fout.close()
            break
    
    
    #Stop to observe result
    while (True):
        key = win.getKey()
        if key == 'q': #quit 
            sys.exit()                    

if __name__ == "__main__":
    main(sys.argv[1:])		



