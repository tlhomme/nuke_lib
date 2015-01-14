# -*- coding: utf-8 -*-


import os
import nuke
import nodeutils as nu
import glob

# FETCHERS

# GUI
import gui.customwins as customwins
import fileSniffer as fs
DEBUG = True


def fetchTrackWindow():
    mainInfs = nuke.toNode("main_infos")
    if mainInfs:
        assetName = mainInfs.knobs()['asset_name'].getValue()
        projName = mainInfs.knobs()['proj_name'].getValue()
        if projName == "test":
            projName = "mune"
        assetType = mainInfs.knobs()['type'].getValue()
        print "||================="
        print "||-- Starting to fecth renders for %s" % assetName
        choiceBox = customwins.EnterValue(
            msg="Enter shot slug", value=assetName)
        result = choiceBox.pop()
        if result:
            shot = choiceBox.obj.getValue()
            fetchRenderForShot(shot)


def fetchTrackForShot(shot):
    mainInfs = nuke.toNode("main_infos")
    if mainInfs and shot != "":
        projName = mainInfs.knobs()['proj_name'].getValue()
        if projName == "test":
            projName = "mune"
        assetType = mainInfs.knobs()['type'].getValue()
        print "||================="
        print "||-- Starting to fecth renders for %s" % shot

        pathToRenders = os.getenv('APERO_PUB') + os.sep + projName + \
            os.sep + assetType + os.sep + \
            shot + os.sep + "comp/"
        print "||-- %s" % pathToRenders
        files = [f for f in os.listdir(
            pathToRenders) if os.path.isdir(pathToRenders + f)]
        files = sorted(files, reverse=True)
        for name in files:
            try:
                print "||-- %s" % name
            except:
                pass
        camBox = customwins.ChooseFromList(
            "Choose the renders you wanna import !", files)
        result = camBox.pop()
        if result:
            selectedRenders = pathToRenders + camBox.selected
            print selectedRenders
            elements, found = fs.readelements(selectedRenders)
            print elements, found
            if found is True:
                readNode = elements[0]
                readNode.setName("Read_%s" % camBox.selected.replace('-','_').replace('.','_'))
                pb = nuke.toNode('Playblasts')
                if pb :
                    readNode.setXYpos(pb.xpos()+50,pb.ypos()+150)
                    nu.deselectAll()
                    nodes = nu.getNodeOnBackDrop(pb)
                    for node in nodes:
                        nuke.autoplace(node)
                    nu.deselectAll()

    else:
        print "||-- No renders to fetch"
