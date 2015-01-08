###    Splits each and every channel from the selected
###    layer on their own pipes using shuffle nodes.
###    ---------------------------------------------------------
###    splitChannels.py v1.0
###    Created: 08/08/2009
###    Modified: 08/08/2009
###    Written by Diogo Girondi
###    diogogirondi@gmail.com

import nuke

def splitChannels( node, layer=None ):
    
    '''
    Split each channel from the selected Layer to individual pipes.
    '''
    
    ch = node.channels()
    layers = list( set( [ each.split( '.' )[0] for each in nuke.channels( node ) ] ) )
    valid_channels = [ 'red', 'green', 'blue', 'alpha', 'black', 'white' ]
    
    if layer != None:
        split_layer = layer
        
    elif len( layers ) == 1:
        split_layer = layers.pop()
        
    else:
        p = nuke.Panel( 'Split Layer' )
        p.addEnumerationPulldown( 'Layer', ' '.join( layers ) )
        result = p.show()
        if result:
            split_layer = p.value( 'Layer' )
        else:
            return
            
    channels = []
    
    for layer in ch:
        if layer.startswith( split_layer ):
            channels.append( layer )
            
    for i in range( len( channels ) ):
        if i == 0:
            sh = nuke.createNode( 'Shuffle', 'in ' + split_layer + ' red red green red blue red alpha black', inpanel=False )
            sh.setInput( 0, node )
            sh['label'].setValue( channels[i] )
        elif i == 1:
            sh = nuke.createNode( 'Shuffle', 'in ' + split_layer + ' red green green green blue green alpha black', inpanel=False )
            sh.setInput( 0, node )
            sh['label'].setValue( channels[i] )
        elif i == 2:
            sh = nuke.createNode( 'Shuffle', 'in ' + split_layer + ' red blue green blue blue blue alpha black', inpanel=False )
            sh.setInput( 0, node )
            sh['label'].setValue( channels[i] )
        elif i == 3:
            sh = nuke.createNode( 'Shuffle', 'in ' + split_layer + ' red alpha green alpha blue alpha alpha black', inpanel=False )
            sh.setInput( 0, node )
            sh['label'].setValue( channels[i] )
        else:
            continue
            
            
            
            
            