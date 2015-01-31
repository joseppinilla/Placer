# mazeRouter.py

import graphics
import routerGUI
import time

class Subnet():
   
    def __init__(self,pins):
        self.pins = pins 
        self.center = 0


def start(win,blocks,nets,mode,verbose):
    """Start maze router process iterating over nets
        BLOCK:Draw unit. Contains information of Graphic Rectangle, state (free,obs,wire or pin), net and subnet
        PIN: Source or Sink of Net. Represented as X,Y tuple
        NET: Resources (Pins, Wires or Blocks) that are to be connected. Contains ID, Color of Net resources, Pins[]
        WIRE: Blocks used for connection. Belong to X net
        TAG: Block numbering for Lee-Moore algorithm. Can be ON/OFF with verbose option
        SUBNET: Group of Resources (Pins, Wires or Blocks) that are connected but have missing connections
        FREE: Block available for routing
        SOURCE: Pin from which the net fan-out       
        """

    for net in nets:
        
        #Add all Net pins to Queue
        pinsVisited, pinsQueue = set(), []      
        pinsQueue.extend(net.pins)
               
        pinsSrc = pinsQueue.pop(0)
        wireLen = 0
    
        #Initialize Subnets
        subnet = Subnet([pinsSrc])
        net.subnets.append(subnet)

        indexSrc = routerGUI.getBlockInd(win,pinsSrc)
        blocks[indexSrc].subnet = 1
       
        #CONNECT ALL PINS
        while pinsQueue:                  
            
            pinsVertex = pinsQueue.pop(0)
                
            if pinsVertex not in pinsVisited:
                pinsVisited.add(pinsVertex) 
                
                tags = [0]*len(blocks)
                
                vertexIndex = routerGUI.getBlockInd(win,pinsVertex)
                
                #If block is not already on subnet
                if (blocks[vertexIndex].subnet == 0):
                    pathLen, matchBlock = bfsNB(win,pinsSrc,blocks,pinsVertex,tags,net,mode,verbose)
                
                    if (matchBlock):
                        indexMatch = routerGUI.getBlockInd(win,matchBlock)
                          
                        subnetNum = blocks[indexMatch].subnet
                        if (subnetNum):
                            #Add vertex to subnet pins list
                            net.subnets[subnetNum-1].pins.append(pinsVertex)

                        else:
                            #Found terminal of same net. Create subnet with terminals
                            subnetNum = len(net.subnets)+1
                            net.subnets.append(Subnet([pinsVertex,matchBlock]))
                            blocks[indexMatch].subnet = subnetNum
                                 
                        if (pathLen!=0):
                            traceBack(win,matchBlock,pathLen,blocks,tags,net,subnetNum)
                    else:
                        print "Failed Routing"
                        return False
                        
                             
                    wireLen += (pathLen-2)
        #PINS CONNECTED
        
        if verbose:
            routerGUI.delTags(win,blocks)      
        
        print "PINS IN NETS"         
       
        
        net.wlen = wireLen
        print "Finished pins"
          
    print "Finished nets"
    return True


def closestBlock(netBlocks, targetBlock):
    """"From a list of blocks, find closest Manhattan distance"""    
    closestVal = abs(netBlocks[0][0] - targetBlock[0]) + abs(netBlocks[0][1] - targetBlock[1])
    closest = netBlocks[0]
    iterBlocks = iter(netBlocks)
    next(iterBlocks)

    for block in iterBlocks:
        dist = abs(block[0] - targetBlock[0]) + abs(block[1] - targetBlock[1])
        if (dist < closestVal):
            closestVal = dist
            closest = block
    
    return closest          


def findDist(block, targetBlock):
    """"Find Manhattan distance"""    
    return abs(block[0] - targetBlock[0]) + abs(block[1] - targetBlock[1])
              


def findCenter(netBlocks):
    """Find block at the geometric center of the net"""
    hiXVal, hiYVal = netBlocks[0][0], netBlocks[0][1]
    
    loXVal, loYVal = netBlocks[0][0], netBlocks[0][1]
          
    blockCnt = 1
    for block in netBlocks:
        if (block[0]>hiXVal):
            hiXVal = block[0]
            
        elif (block[0]<loXVal):
            loXVal = block[0]
            
            
        if (block[1]>hiYVal):
            hiYVal = block[1]
            
        elif (block[0]<loYVal):
            loYVal = block[1]
        blockCnt+=1
    
    #TODO: BFS around center to find non-obs, non-otherNet block
    
    return (int((loXVal+hiXVal)/2),int((loYVal+hiYVal)/2))

def traceBack(win,trackBlk,pathLen,blocks,tags,net,subnet):
    """Trace Back over tags by expanding around trackBlk. Mark blocks: Color, state:'wire', net, and subnet"""
        
    while(pathLen!=1):

        pathLen -= 1
        neighbours = routerGUI.getBlockNB(trackBlk)

        for neighbour in neighbours:
            indexNB = routerGUI.getBlockInd(win,neighbour)
            blockNB = blocks[indexNB]
             
            if (tags[indexNB]==(pathLen)):
                blockNB.setFill(net.color)
                blockNB.setState('wire')
                blockNB.net = net.id
                blockNB.subnet = subnet 
                trackBlk = neighbour
                break

#def bfstargetNB(win,pinsSrc,blocks,pinsVertex,tags,net,subnet,mode,verbose):

def bfsNB(win,pinsSrc,blocks,pinsVertex,tags,net,mode,verbose):
    """ Breadth First Search starting on pin Vertex looking for same Net """
    
    indexPin = routerGUI.getBlockInd(win,pinsVertex)
    tags[indexPin] = 1

    #tagsA[indexPin] = findDist(pinsVertex,pinsSrc) + 1 #Tag A*
    
    blocksVisited, blocksQueue = set(), [pinsVertex]                      

    while blocksQueue:
        
        blocksVertex = blocksQueue.pop(0)                                                    
        if blocksVertex not in blocksVisited:
            
            index = routerGUI.getBlockInd(win,blocksVertex)
            
            tag = tags[index]+1

            blocksVisited.add(blocksVertex)
                  
            for neighbour in routerGUI.getBlockNB(blocksVertex):
                #tagA = findDist(neighbour, pinsSrc) + tag #TagA*
                 
                indexNB = routerGUI.getBlockInd(win,neighbour)
                blockNB = blocks[indexNB]
                
                if ((tags[indexNB] == 0)):
                    if (blockNB.isFree()):
                        tags[indexNB] = tag
                        #tagsA[indexNB] = tag  #Tag A*
                        if verbose:
                            blockNB.setTag(win,tag)
                        blocksQueue.append(neighbour)
                        
                    elif (blockNB.net == net.id):
                        if (blockNB.isWire() or (neighbour == pinsSrc)): #IF wire
                            return tag, neighbour
                            
                        
            
        #Run mode (clocked, stepped)
        key = win.checkKey()
        if (key == 'c'):
            mode = 'r'      
        if (mode.isdigit()):
            time.sleep(int(mode)*0.1)
        if (mode=='s'):
            while (key != 's'):
                key = win.getKey()
                if (key == 'c'):
                    mode = 'r'
                    break
            
            
       
    return 0, None