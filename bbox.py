import nuke
import os
import nukelib as nl
import nodeutils as nu
import sceneBuilder as sb
import fileSniffer as fs
from operator import itemgetter, attrgetter


# GUI
import gui.customwins as customwins

# THIRD PARTY
import thirdparty.backdropTools as backdropTools


TOOLS_PATH = os.getenv('TOOLS_PATH')


class Bbox():
    def __init__(self, nodeList=None, cleanUp=True, bdrop=None):
        self.topLeft = (0, 0)
        self.bottomRight = (0, 0)
        self.width = 0
        self.height = 0
        self.bdrop = None
        if bdrop:
            self.bdrop = bdrop
            self.getBboxBdrop(self.bdrop)
        if nodeList:
            self.getBbox(nodeList)
        if cleanUp:
            self.cleanUp()
        self.calcSize()

    def getBbox(self, nodeList):
        xposList = []
        yposList = []
        if len(nodeList) > 0:
            for node in nodeList:
                xposList.append((node.xpos(), node))
                yposList.append((node.ypos(), node))

            xposList = sorted(xposList, key=itemgetter(0))
            yposList = sorted(yposList, key=itemgetter(0))
            size = len(nodeList) - 1
            self.topLeft = (xposList[0][1].xpos(), yposList[0][1].ypos())
            self.bottomRight = (
                xposList[size - 1][1].xpos(), yposList[size - 1][1].ypos())

    def getBboxBdrop(self, bdrop):
        self.topLeft = (bdrop.xpos(), bdrop.ypos())
        self.bottomRight = (
            bdrop.xpos() + bdrop['bdwidth'].value(), bdrop.ypos() + bdrop['bdheight'].value())

    def calcSize(self):
        self.width = self.bottomRight[0] - self.topLeft[0]
        self.height = self.bottomRight[1] - self.topLeft[1]

    def move(self, x=0, y=0):
        self.topLeft = (self.topLeft[0] + x, self.topLeft[1] + y)
        self.bottomRight = (self.bottomRight[0] + x, self.bottomRight[1] + y)

    def cleanUp(self):
        self.expand(50, 50, 100, 50)

    def expand(self, x=0, y=0, x1=0, y1=0):
        self.topLeft = (self.topLeft[0] - x, self.topLeft[1] - y)
        self.bottomRight = (self.bottomRight[0] + x1, self.bottomRight[1] + y1)
        self.calcSize()
        if self.bdrop:
            self.bdrop['bdwidth'].setValue(self.width)
            self.bdrop['bdheight'].setValue(self.height)

    def createBackdrop(self, name, label="\ ", textSize=10):
        newBD = nuke.createNode(
            "BackdropNode", "bdwidth %d bdheight %d label %s note_font_size %d note_font Impact" %
            (self.width, self.height, label, textSize), inpanel=False)
        newBD.setName(name)
        newBD.setXYpos(int(self.topLeft[0]), int(self.topLeft[1]))
        self.bdrop = newBD
        backdropTools.spreadBackdropHues()
        backdropTools.fixBackdropDepth()

    def moveBackdrop(self, x=0, y=0, isOffset=False):
        if self.bdrop:
            nodes = nu.getNodeOnBackDrop(self.bdrop)
            nodes.append(self.bdrop)
            oldPos = (self.bdrop.xpos(), self.bdrop.ypos())
            offset = (x - oldPos[0], y - oldPos[1])
            if isOffset:
                offset = (x, y)
            for node in nodes:
                nu.moveNode(node, offset[0], offset[1], 0, 0)
            self.move(x, y)

    def moveContent(self, x=0, y=0):
        if self.bdrop:
            nodes = nu.getNodeOnBackDrop(self.bdrop)
            for node in nodes:
                node.setXYpos(int(node.xpos() + x), int(node.ypos() + y))

    def getContent(self):
        nodes = []
        if self.bdrop:
            nodes = nu.getNodeOnBackDrop(self.bdrop)
        return nodes

    def setWidth(self, width):
        self.bottomRight = (self.topLeft[0] + width, self.bottomRight[1])
        self.calcSize()

    def setHeight(self, height):
        self.bottomRight = (self.bottomRight[0], self.topLeft[1] + height)
        self.calcSize()

    def setBgColor(self, color):
        bgColor = self.bdrop.knobs()['tile_color']
        bgColor.setValue(color)

    def increaseLuma(self, nbTimes):
        nu.deselectAll()
        self.bdrop['selected'].setValue(1)
        for i in range(0, nbTimes + 1):
            backdropTools.shiftBackdropLuma(0.05)
        nu.deselectAll()

    def setPub(self):
        bgColor = self.bdrop.knobs()['tile_color']
        bgColor.setValue(741112575)

    def setWork(self):
        bgColor = self.bdrop.knobs()['tile_color']
        bgColor.setValue(2290649088)


class AovBox(Bbox):

    def __init__(self, nodeList=None, cleanUp=True, bdrop=None, layerName="", name="", index=(0, 0), orientation=False, gridOrigin=(200, 650), color=None):
        nu.deselectAll()
        self.layerName = layerName
        self.name = name
        self.index = index
        Bbox.__init__(
            self, nodeList=self.initRead(), cleanUp=cleanUp, bdrop=bdrop)
        bdName = "%s_%s_BD" % (layerName, name)
        self.createBackdrop(
            name=bdName, label="%s" % name.upper(), textSize=20)
        self.expand(x=0, y=0, x1=0, y1=50)
        self.padding = 15
        self.layerBdrop = nuke.toNode(layerName)
        
        if self.layerBdrop is None:
            raise Exception ("Layer %s doesn't exist" % layerName)
        
        self.gridOrigin = (self.layerBdrop.xpos() + gridOrigin[
                           0], self.layerBdrop.ypos() + gridOrigin[1])
        if "id" in self.name:
            self.expand(x=0, y=0, x1=0, y1=-65)
            self.padding = 50
        else:
            if orientation is True:
                self.padding = 30
            self.expand(x=0, y=0, x1=0, y1=-30)

        self.moveContent(-40)
        self.expand(x=-50, y=0, x1=0, y1=0)
        self.placeOnGrid()
        if color:
            self.setBgColor(color)
            if orientation is False:
                self.increaseLuma(index[0])
            else:
                print self.name
                self.increaseLuma(index[1])
        nu.deselectAll()

    def initRead(self):
        nu.deselectAll()
        readNode = nuke.toNode("%s_%s" % (self.layerName, self.name))
        nu.deselectAll()
        readNode['selected'].setValue(1)
        reformatNode = nuke.createNode('Reformat', inpanel=False)
        reformatNode.setName("%s_%s_RF" % (self.layerName, self.name))
        reformatNode.setYpos(reformatNode.ypos() + 20)
        nu.deselectAll()
        reformatNode['selected'].setValue(1)
        dotNode = nuke.createNode('Dot', inpanel=False)
        dotNode.setName("%s_%s_DOT" % (self.layerName, self.name))
        dotNode.setYpos(dotNode.ypos() + 10)
        nu.deselectAll()
        redShuffle = None
        returnList = [readNode, reformatNode, dotNode]
        if "id" in self.name:
            dotNode.setXYpos(reformatNode.xpos() - 10, reformatNode.ypos() + 4)
            redShuffle = nuke.createNode('Shuffle', inpanel=False)
            redShuffle.setXYpos(dotNode.xpos() - 100, dotNode.ypos() - 60)
            redShuffle.setName("%s_%s_RED" % (self.layerName, self.name))
            redShuffle.setInput(0, dotNode)
            redShuffle.knobs()['red'].setValue('red')
            redShuffle.knobs()['green'].setValue('red')
            redShuffle.knobs()['blue'].setValue('red')
            redShuffle.knobs()['alpha'].setValue('red')
            redDot = nuke.createNode('Dot', inpanel=False)
            redDot.setName("%s_%s_RED_DOT" % (self.layerName, self.name))
            redDot.setXYpos(dotNode.xpos() - 150, dotNode.ypos() - 56)
            redDot.setInput(0, redShuffle)
            redDot.knobs()['label'].setValue('RED\n\n')
            redDot.knobs()['note_font_size'].setValue(20)
            redDot.knobs()['note_font_color'].setValue(4278190335)
            returnList.append(redShuffle)
            returnList.append(redDot)
            #
            greenShuffle = nuke.createNode('Shuffle', inpanel=False)
            greenShuffle.setXYpos(dotNode.xpos() - 100, dotNode.ypos() - 4)
            greenShuffle.setName("%s_%s_GREEN" % (self.layerName, self.name))
            greenShuffle.setInput(0, dotNode)
            greenShuffle.knobs()['red'].setValue('green')
            greenShuffle.knobs()['green'].setValue('green')
            greenShuffle.knobs()['blue'].setValue('green')
            greenShuffle.knobs()['alpha'].setValue('green')
            greenDot = nuke.createNode('Dot', inpanel=False)
            greenDot.setName("%s_%s_GREEN_DOT" % (self.layerName, self.name))
            greenDot.setXYpos(dotNode.xpos() - 150, dotNode.ypos())
            greenDot.setInput(0, greenShuffle)
            greenDot.knobs()['label'].setValue('GREEN\n\n')
            greenDot.knobs()['note_font_size'].setValue(20)
            greenDot.knobs()['note_font_color'].setValue(16711935)
            returnList.append(greenShuffle)
            returnList.append(greenDot)
            #
            blueShuffle = nuke.createNode('Shuffle', inpanel=False)
            blueShuffle.setXYpos(dotNode.xpos() - 100, dotNode.ypos() + 50)
            blueShuffle.setName("%s_%s_BLUE" % (self.layerName, self.name))
            blueShuffle.setInput(0, dotNode)
            blueShuffle.knobs()['red'].setValue('blue')
            blueShuffle.knobs()['green'].setValue('blue')
            blueShuffle.knobs()['blue'].setValue('blue')
            blueShuffle.knobs()['alpha'].setValue('blue')
            blueDot = nuke.createNode('Dot', inpanel=False)
            blueDot.setName("%s_%s_BLUE_DOT" % (self.layerName, self.name))
            blueDot.setXYpos(dotNode.xpos() - 150, dotNode.ypos() + 54)
            blueDot.setInput(0, blueShuffle)
            blueDot.knobs()['label'].setValue('BLUE\n\n')
            blueDot.knobs()['note_font_size'].setValue(20)
            blueDot.knobs()['note_font_color'].setValue(65535)
            returnList.append(blueShuffle)
            returnList.append(blueDot)

        nu.deselectAll()
        return returnList

    def getRfNode(self):
        nodes = nu.getNodeOnBackDrop(self.bdrop)
        for node in nodes:
            if node.Class() == "Reformat":
                return node

    def getDotNode(self):
        nodes = nu.getNodeOnBackDrop(self.bdrop)
        for node in nodes:
            if node.Class() == "Dot" and node.name() == "%s_%s_DOT" % (self.layerName, self.name):
                return node

    def placeOnGrid(self):
        posX = self.gridOrigin[0] + self.index[0] * (100 + self.padding)
        posY = self.gridOrigin[1] + self.index[1] * (192 + self.padding)
        # posX = self.gridOrigin[0]+self.index[0]*(self.width+self.padding)
        # posY = self.gridOrigin[1]+self.index[1]*(self.height+self.padding)
        self.moveBackdrop(posX, posY)