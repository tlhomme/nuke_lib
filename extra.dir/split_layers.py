from nuke_lib import splitLayers
reload(splitLayers)
import nuke 

def split_layers():
    if len(nuke.selectedNode())>0:
        splitLayers.splitLayers(nuke.selectedNode())

