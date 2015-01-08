from nuke_lib import extraLib
reload(extraLib) 

def fetch_vfx_source():
    extraLib.sniff_vfx_sources()