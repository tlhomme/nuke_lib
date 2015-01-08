import os
import re
import glob 
import nuke

class FileBase(object):
    
    def __init__(self, inputPath):
        
        self.inputPath = inputPath
        self.directory, self.fileName = os.path.split(self.inputPath)
        self.baseName, self.typeExt = os.path.splitext(self.fileName)
        self.files = {}
        self.genSrc = None
        
    def getId(self, full=True):
        id = '%s'%self.fileName
        if full:
            id = '%s/%s'%(self.directory, id)
        return id
    
    def getShortId(self):
        return self.getId(full=False)

    def getFullId(self):
        return self.getId(full=True)
        
    def makeThumbnail(self, thumbnail_path):
        thumb_args = ['convert', self.files[0], '-resize', '240x240', '-quality', '80']
        if self.typeExt == '.dpx':
            thumb_args += ['-set', 'colorspace', 'Log']
        thumb_args += [thumbnail_path]
        return subprocess.call(thumb_args) == 0
    
    def isSequence(self):
        return False
        
    def getGenSrc(self, ext='*'):
        if self.genSrc:
            return glob.glob('%s.%s'%(self.genSrc, ext))

class File(FileBase):
    
    def __init__(self, inputPath):
        super(File, self).__init__(inputPath)
        self.files[0] = inputPath
        
   
class FileSequence(FileBase):

    ChannelGroups = [
            'aov',
            'bty',
            'data',
            'diff',
            'extra',
            'mask',
            'puzz',
            'shad',
            'spec',
    ] 

    def __init__(self, inputPath, skipSize=None):
        super(FileSequence, self).__init__(inputPath)
        self.suffixFormat = ''
        self.paddingExt = ''
        self.frameExt = ''
        self.padding = 0
        self.skipSize = skipSize
        self.indexSeparator = '.'
        self.index = None
        self.type = ''
        #
        if self.typeExt != '':
            
            # last token is a number ( ex: abc.0001 or abc.dpx.0001)
            if self.typeExt.replace('.','').isdigit():
                self.index = self.typeExt.replace('.','')               
                self.frameExt = self.typeExt
                self.suffixFormat = '.%FRAME%'
                
                # we have a type ext (ex: abc.dpx.0001)
                baseName, typeExt = os.path.splitext(self.baseName)
                if typeExt:
                    self.baseName = baseName
                    self.typeExt = typeExt   
                    self.suffixFormat = '.%TYPE%' + self.suffixFormat
                    
            # last token is a file type ( ex: abc.dpx or abc.0001.dpx )
            else:                
                self.suffixFormat = '.%TYPE%'
            
            self.type = self.typeExt.replace('.', '')
                
        if not self.frameExt:
           
            findIndex = re.compile('[0-9]+$').findall(self.baseName)
            if len(findIndex):
                self.index = findIndex[-1]
                
                findSuffix = re.compile('[^a-zA-Z0-9]+[0-9]+$').findall(self.baseName)
                if len(findSuffix):
                    self.indexSeparator = findSuffix[-1].replace(self.index, '')
                else:
                    self.indexSeparator = ''
                    
                self.frameExt = self.indexSeparator + self.index
                self.baseName = self.baseName.replace(self.frameExt, '')
                
                self.suffixFormat = self.indexSeparator + '%FRAME%' + self.suffixFormat
                
        if self.frameExt:
            
            self.padding = len(self.index)
            self.paddingId = '#' * self.padding
            self.paddingExt = self.indexSeparator +  self.paddingId
                
            outdir, outbase = os.path.split(inputPath)
            self.genSrc = '%s/.%s'%(outdir, self.getBaseName(self.paddingId))
    
    def isConform(self):
        return self.suffixFormat == '.%FRAME%.%TYPE%' 
    
    def isValid(self):
        return self.frameExt != '' and self.frameExt != None
    
    def isSequence(self):
        return self.isValid()
    
    def missingFrames(self):
        frames = self.getFrames()
        return sorted(list(set(range(frames[0], frames[-1]+1)).difference(set(frames))))
    
    def badFrames(self, minSize=1024):
        frames = []
        for frame in self.files.keys():
            if os.path.getsize(self.files[frame]) < minSize:
                frames.append(frame)
        return sorted(frames)
    
    def isComplete(self):
        return len(self.missingFrames()) == 0
        
    def getSuffix(self, frame=None):
        
        if frame is None and self.index is not None:
            frame = self.index
                
        strframe = str(frame)
        if strframe.isdigit():
            strframe = strframe.zfill(self.padding)
            
        suffix = self.suffixFormat
        suffix = suffix.replace('%FRAME%', strframe)
        suffix = suffix.replace('%TYPE%', self.type)
        
        return suffix

    def getBaseName(self, frame):
        return self.baseName + self.getSuffix(frame)
    
    def getId(self, full=True):
        id = '%s'%self.getBaseName(self.paddingId)
        if full:
            id = '%s/%s'%(self.directory, id)
        return id
    
    def getRegExPath(self):
        if self.isValid():
            return '%s/%s'%(self.directory, self.getBaseName('[0-9]'*self.padding))
    
    def listFiles(self):
        regExPath = self.getRegExPath()
        
        if regExPath:
            files = glob.glob(regExPath)
            for file in files:
                index = FileSequence(file).index
                
                if index.isdigit():
                    if self.skipSize is None or os.path.getsize(file) > self.skipSize: 
                        self.files[int(index)] = file
                    
    def getFileName(self, frame=None):
        return '%s/%s%s'%(self.directory, self.getBaseName(frame))
    
    def getFrames(self):
        frames = self.files.keys()
        frames.sort()
        return frames
    
    def getConformName(self, asId=False):
        
        frame = self.index.zfill(self.padding)
        if asId:
            frame = self.paddingId
        
        baseName = self.baseName
        if baseName == '':
            baseName = os.path.split(os.path.abspath(self.directory))[1]
            
        return '%s/%s.%s%s'%(self.directory, baseName, frame, self.typeExt) 
    
    def makeThumbnail(self, thumbnail_path, filmstrip_path=None, rand_thumb=False):
        
        thumbSuccess = False
        stripSuccess = False
        
        frames = self.getFrames()
        if len(frames):
        
            thunm_idx = 0
            if rand_thumb:
                thunm_idx = random.randrange(0, len(frames)) 
                
            thumb_args = ['convert', self.files[frames[thunm_idx]], '-resize', '240x240', '-quality', '80']
            if self.typeExt == '.dpx':
                thumb_args += ['-set', 'colorspace', 'Log']
            thumb_args += [thumbnail_path]
            
            thumbSuccess = subprocess.call(thumb_args) == 0
            
            if filmstrip_path and len(frames) >= 5:
                
                filmstrip_args = ['convert']
                
                # 3 frames per sec
                nbframes = int(len(frames) / 8)
                if nbframes < 5:
                    nbframes = 5
                elif nbframes > 100:
                    nbframes = 100
                    
                step = int(len(frames) / nbframes)
                for i in range(0, len(frames), step):
                    filmstrip_args += [ self.files[frames[i]], '-resize', '240x240',]
                    
                filmstrip_args += ['+append', '-quality', '80']
                if self.typeExt == '.dpx':
                    filmstrip_args += ['-set', 'colorspace', 'Log']
                filmstrip_args += [filmstrip_path]
                
                stripSuccess = subprocess.call(filmstrip_args) == 0
            
        return [thumbSuccess, stripSuccess]
    
    @classmethod
    def find(cls, directory, file='*', frame='.*', extensions=['.*'], recurse=True, skipSize=None, onlyConform=True, includeSingle=False):
        
        sequences = {}
        
        for ext in extensions:
            
            files = glob.glob('%s/%s%s%s'%(directory, file, frame, ext))
            
            for f in files:
                
                sequence = cls(f, skipSize=skipSize)
                if not sequence.isSequence():
                    if includeSingle and f not in sequences.keys():
                        sequences[f] = File(f)
                    else:
                        continue
                
                if onlyConform and not sequence.isConform():
                    continue
                
                if sequence.getId() in sequences.keys():
                    continue
                
                sequence.listFiles()
                sequences[sequence.getId()] = sequence
             
        if recurse:
            for item in os.listdir(directory):
                itempath = '%s/%s'%(directory, item)
                if os.path.isdir(itempath):
                    subsequences = cls.find(itempath, file=file, frame=frame, extensions=extensions, recurse=recurse, skipSize=None, onlyConform=onlyConform, includeSingle=includeSingle)
                    for sequenceId in subsequences.keys():
                        if sequenceId not in sequences.keys():
                            sequences[sequenceId] = subsequences[sequenceId]
                
        return sequences

    @classmethod
    def filterMulti(cls, sequences):
            
        result = {}
        
        for id in sorted(sequences.keys()):  
            
            s = sequences[id]
            
            short_id = s.getId(full=False)
            
            seq_key = short_id
            
            id_split = short_id.split('.')[0].split('_')
            
            last_tok = id_split[-1]
            
            if last_tok in cls.ChannelGroups:
                seq_key = seq_key.replace('_' + last_tok, '')
                changrp = last_tok
                
                # for stereo
                last_tok = id_split[-2]
            else:
                changrp = 'bty'
            
            if last_tok == 'l' or last_tok == 'r':
                view = last_tok
                seq_key = seq_key.replace('_%s.'%view, '_%v.')
            else:
                view = 'm'  
            
            seq_key = os.path.split(s.getId())[0] + "/" + seq_key
            
            if seq_key not in result:
                result[seq_key] = {}
                 
            if changrp not in result[seq_key]:
                result[seq_key][changrp] = {}
                
            result[seq_key][changrp][view] = s
        
        return result
    
    @classmethod
    def multiLabel(cls, multi_item):
        
        chan_label = ''
        chan_keys = sorted(multi_item.keys())
        if chan_keys != ['bty'] :
            chan_label = '( %s )'%string.join(chan_keys)
        
        view_content = []
        for chan_key in chan_keys:
            view_keys = sorted(multi_item[chan_key].keys())
            
            if 'm' in view_keys and 'mono' not in view_content:
                view_content.append('mono')
                
            if 'l' in view_keys and 'r' in view_keys and 'stereo' not in view_content:
                view_content.append('stereo')
                
            if 'l' in view_keys and 'r' not in view_keys and 'left' not in view_content:
                view_content.append('left')
                
            if 'r' in view_keys and 'l' not in view_keys and 'right' not in view_content:
                view_content.append('right')
                
        view_label = ''
        if len(view_content) and view_content != ['mono']:
            view_label = '( %s )'%string.join(view_content)
            
        return "%s %s"%(chan_label, view_label)

def readelements(elementPath):
    ''' Importe les sequences d'images, Cree le Copy All CHannel, la distortion et le MergeAOV au besoin
    '''    
    readPlate, mAovs, element_read, copy, element = None, None, None, None, None

    createdNode = []      
    elements = FileSequence.find(elementPath, recurse = 0)
    # print elements
    i=0
    if (len(elements.keys()) > 0): 
        readNameList = []                  
        ## Stereo
        #stereoTest = _stereoPath(elements)
        #elements = stereoTest[0]
        #stereoRead = stereoTest[1]

        for sequ in elements.keys():
            ##On  cree un read par element
            ##################################################           
            element = elements[elements.keys()[i]]
            element_frames = element.getFrames()
            # print element_frames
            element_read = nuke.nodes.Read(file=sequ)
            element_read.knobs()['first'].setValue(element_frames[0])
            element_read.knobs()['last'].setValue(element_frames[-1])
            # print element
            createdNode.append(element_read)
        return createdNode,True
    else:
        return createdNode,False

def readimage(elementPath):
    ''' Importe les sequences d'images, Cree le Copy All CHannel, la distortion et le MergeAOV au besoin
    '''    
    readPlate, mAovs, element_read, copy, element = None, None, None, None, None

    createdNode = []      
    print elementPath
    elements = FileSequence.find(elementPath, frame = "",recurse = 0,includeSingle=True,)
    print elements
    i=0
    if (len(elements.keys()) > 0): 
        readNameList = []                  
        ## Stereo
        #stereoTest = _stereoPath(elements)
        #elements = stereoTest[0]
        #stereoRead = stereoTest[1]

        for sequ in elements.keys():
            ##On  cree un read par element
            ##################################################           
            element = elements[elements.keys()[i]]
            # print element_frames
            element_read = nuke.nodes.Read(file=sequ)
            # print element
            createdNode.append(element_read)
        return createdNode,True
    else:
        return createdNode,False

def createReadFromSequence(sequence):
    ''' Create reads from FileSequence
    '''  
    path,fileSequence = sequence
    element_read = None
    if path:              
        ##On  cree un read par element
        ##################################################
        element_frames =[]
        element_read = nuke.nodes.Read(file=path)
        if isinstance(fileSequence, FileSequence):  
            element_frames = fileSequence.getFrames()
            element_read.knobs()['first'].setValue(element_frames[0])
            element_read.knobs()['last'].setValue(element_frames[-1])
        else:      
            return element_read,False
        return element_read,True
    else:
        return element_read,False
