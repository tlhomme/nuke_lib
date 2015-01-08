from nuke_lib import clipboard
reload(clipboard) 

def paste_clipboard():
    clipboard.pasteClipboard()