import nuke
import os
import nukescripts as ns
from operator import itemgetter, attrgetter

import logging

# METHOD HELPER
def moveNode(node, offsetX, offsetY, bdHeight, i):
    x, y = node.xpos(), node.ypos()
    node.setXYpos(int(x + offsetX), int(y + offsetY + bdHeight * i))
    
def getBoundingBox(nodes=None):
    """
    Gets the bounding box of the given nodes.
    
    @param nodes: The nodes to use to find the bounding box. If not-specified, all nodes in the scenes are used
    @type nodes: list of nuke.Nodes
    
    @return: A tuple of xLeft, xRight, yTop, yBottom limits
    """
    
    xLeft = None
    xRight = None
    yTop = None
    yBottom = None
    
    if nodes is None:
        nodes = nuke.allNodes()
        
    for node in nodes:
        
        x = node.xpos()
        y = node.ypos()
        width = node.screenWidth()
        height = node.screenHeight()
        
        logging.debug("BBOX Search (%s): (%s, %s) (%s, %s)" % (node.name(), x, y, width, height))
        
        if x < xLeft or xLeft is None:
            xLeft = x
            
        if (x + width) > xRight or xRight is None:
            xRight = x + width
            
        if y < yTop or yTop is None:
            yTop = y
            
        if (y + height) > yBottom or yBottom is None:
            yBottom = y + height
            
    return xLeft, xRight, yTop, yBottom  
    
def moveBackdrop(node, x, y, relative=True):
    """
    Move a backdrop node and all its contents
    
    @param node: The backdrop node
    @type node: nuke.BackdropNode
    
    @param x: The X coordinate
    @type x: int
    
    @param y: The y coordinate
    @type y: int
    
    @param relative: To move the node relative or absolute
    @type relative: bool [Default=True]  
    """
    
    if relative:
        x = node.xpos() + x
        y = node.ypos() + y
        
    for nestedNode in getNodeOnBackDrop(node):
        
        offsetX = nestedNode.xpos() - node.xpos() 
        offsetY = nestedNode.ypos() - node.ypos()
        
        try:
            nestedNode.setXYpos(offsetX+x, offsetY+y)
            
        except:
            logging.error("Moving node %s failed [x=%s(%s), y=%s(%s), offsetX=%s(%s), offsetY=%s(%s)]" % (nestedNode.name(), x, type(x), y, type(y), offsetX, type(offsetX), offsetY, type(offsetX)))
            raise
        
    node.setXYpos(x, y)
    
def moveNodeOntoBackdrop(node, backdropNode, x, y):
    """
    Will move a node onto a backdrop. x,y will be clamped to ensure that
    node is withing the backdrop's boundaries
    
    @param node: The node to move
    @type node: nuke.Node
    
    @param backdropNode: The backdrop to move the node onto
    @type backdropNode: nuke.BackdropNode
    
    @param x: The x offset from the Backdrop
    @type x: int
    
    @param y: The y offset from the Backdrop
    @type y: int
    """
    
    logging.info("Moving node %s onto backdrop %s offset %d, %d" % (node.name(), backdropNode.name(), x,y))
        
    backdropX = backdropNode.xpos()
    backdropY = backdropNode.ypos()
    
    if x < 0:
        maxBackdropX = backdropNode.screenWidth()
        offsetX = maxBackdropX - min((abs(x), maxBackdropX))
        
    else:
        maxBackdropX = abs(backdropNode.screenWidth() - node.screenWidth())
        offsetX = min((x, maxBackdropX))
        
    if y < 0:
        maxBackdropY = backdropNode.screenHeight()
        offsetY = maxBackdropY - min((abs(y),maxBackdropY))
    
    else:
        maxBackdropY = abs(backdropNode.screenHeight() - node.screenHeight())        
        offsetY = min((y,maxBackdropY))
        
    logging.debug("Offset (X,Y, maxBackdropY): %s, %s, %s, %s" % (offsetX, offsetY, backdropNode.screenWidth(), node.screenWidth() ))
            
    nodeX = offsetX + backdropX
    nodeY = offsetY + backdropY
    
    node.setXYpos(nodeX, nodeY)


def orderNodeByXpos(nodes):
    newList = [(node, node.xpos(), index) for index, node in enumerate(nodes)]
    newList = sorted(newList, key=itemgetter(1))
    # newList = [item[0] for item in newList]
    return newList


def orderNodeByYpos(nodes):
    newList = [(node, node.ypos(), index) for index, node in enumerate(nodes)]
    newList = sorted(newList, key=itemgetter(1))
    # newList = [item[0] for item in newList]
    return newList


def orderNodeByIndex(nodes):
    # print [node.name() for node in nodes]
    print nodes
    newList = orderNodeByXpos(nodes)
    for i in range(1, len(newList)):
        tmp = newList[i]
        k = i
        while k > 0 and tmp[2] < newList[k - 1][2]:
            newList[k] = newList[k - 1]
            k -= 1
        switchPosition(newList[i][0], newList[k][0])
        newList[k] = tmp
        switchPosition(newList[i][0], newList[k][0])
    print newList


def switchPosition(node, node1):
    nodePos = (node.xpos(), node.ypos())
    node1Pos = (node1.xpos(), node1.ypos())
    node1.setXYpos(nodePos[0], nodePos[1])
    node.setXYpos(node1Pos[0], node1Pos[1])


def disableErrorNodes():
    for node in nuke.allNodes():
        if node.hasError() is True and node.Class() == "Read":
            node.knobs()['disable'].setValue(1)


def bdToggle(bd, state):
    for node in getNodeOnBackDrop(bd):
        node.knobs()['disable'].setValue(state)


def deselectAll():
    for node in nuke.allNodes():
        node['selected'].setValue(0)


def getNodeOnBackDrop(bgNode):
    bgNodes = []
    selection = nuke.selectedNodes()
    deselectAll()
    nodes = bgNode.selectNodes(True)
    bgNodes = nuke.selectedNodes()
    deselectAll()
    for node in selection:
        node['selected'].setValue(1)
    return bgNodes
