from nuke_lib import readFromWrite
reload(readFromWrite)
import nuke 

def read_from_write():
    if nuke.selectedNode().Class() == 'WriteTank':
        n = nuke.toNode(nuke.selectedNode().name()+".Write1")
        readFromWrite.readFromWrite(n.fullName()) 
    else:
        readFromWrite.readFromWrite()
