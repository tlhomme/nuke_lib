import os
import nuke
import nodeutils as nu
import glob

import logging

# GUI
import gui.customwins as customwins
import fileSniffer as fs
import sgtk

def fetch():
    path_to_folder_shot = os.sep.join(nuke.root().name().split(os.sep)[:-5])+os.sep+"track_pr"
    prod_name = os.environ['PROD']
    split_path=path_to_folder_shot.split(os.sep)
    shot,seq = split_path[-2],split_path[-3]
    project_name = "%s-%s_%s-TRACK"%(prod_name,seq,shot)
    project_path = path_to_folder_shot + os.sep + project_name
    pathToTrackExport = project_path + os.sep + "export"
    logging.warning("||-- %s" % pathToTrackExport)
    files = [f for f in os.listdir(
        pathToTrackExport) if os.path.exists(pathToTrackExport +os.sep+ f) and f[-3:]==".py"]
    files = sorted(files, reverse=True)
    for name in files:
        try:
            logging.warning("||-- %s" % name)
        except:
            pass
    if len(files)>0:
        chooseBox = customwins.ChooseFromList(
            "Choose the track you wanna import !", files)
        result = chooseBox.pop()
        if result:
            selectedRenders = pathToTrackExport + os.sep +chooseBox.selected
            execfile(selectedRenders)
    else:
        nuke.message("No export found")