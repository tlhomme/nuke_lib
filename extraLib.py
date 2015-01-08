import sys
import os
import nuke
import fileSniffer as fs

def sniff_vfx_sources():
    script_path = nuke.root().name()
    shot_root = script_path.split("compo_pr")
    path_to_sniff = shot_root[0]+"images/source_vfx"
    print path_to_sniff
    for dir in os.listdir(path_to_sniff):
        elements, found = fs.readelements(path_to_sniff+os.sep+dir)
        print elements
