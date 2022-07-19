# DO NOT DO THIS IT JUST MAKES VS CODE LOOK BETTER
import random as slicer
# --------------------------------------------------
import os
import time

def createFrames(directory):
  '''
  Create a dictionary of frames from a directory of images.
  :param directory: directory in which images are stored
  :return frames: dictionary of frames
  '''
  files = []
  for filename in os.listdir(directory):
    file = os.path.join(directory, filename)
    if os.path.isfile(file):
      files.append(file)
  
  frames = {i:{'path':file} for i, file in enumerate(sorted(files, key=lambda file: int(file[-11:-7])))}
  
  return frames

def loadVolumes(frames, namePrefix=None, **kwargs):
  '''
  Add files from frames to Scene as nodes (labelmaps for this).
  :param frames: dictionary of frames
  Let kwargs be a dictionary of arguments to pass to slicer.util.loadVolume()
  :return frames: dictionary of frames
  '''
  for frame, value in frames.items():
    path = value['path']
    
    if namePrefix:
      kwargs['name'] = namePrefix + '_' + value['path'][-11:-7]
    node = slicer.util.loadVolume(path, kwargs)
    frames[frame]['node'] = node
  
  return frames

def createClosedSurfaceOfSegmentation(frames, namePrefix=None):
  '''
  Create 3D representation of segmentation.
  :param frames: dictionary of frames
  :return frames: dictionary of frames
  '''
  for frame, value in frames.items():
    seg = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentationNode')
    slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(value['node'], seg)
    seg.SetName(namePrefix + '_' + value['path'][-11:-7])
    seg.CreateClosedSurfaceRepresentation()
    
    frames[frame]['opacity'] = 1
    frames[frame]['segmentation'] = seg
    
  return frames

def combineSegmentationsAndVolumes(segmentations, volumes):
  '''
  Combine segmentations and volumes into single dictionary.
  :param segmentation: dictionary of segmentations
  :param volumes: dictionary of volumes
  :return frames: dictionary of frames
  '''
  frames = {}
  for (frame, segment), (framev, volume) in zip(segmentations.items(), volumes.items()):
    frames[frame] = {'path':segment['path'], 'volumePath':volume['path'], 'node':segment['node'], 'volume':volume['node']}
    
  return frames

def toggleVolumeRenderingVisibility(volume):
  '''
  Toggle visibility of a specific volumes render in 3D.
  :param volume: volume to toggle
  :return visibility: boolean of visibility
  '''
  volRenLogic = slicer.modules.volumerendering.logic()
  displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volume)
  displayNode.SetVisibility(not displayNode.GetVisibility())
  
  return displayNode.GetVisibility()

def setSegmentationVisibility(frames, opacity, indices):
  '''
  Set opacity of specific segmentations.
  :param frames: dictionary of frames
  :param opacity: opacity to set
  :param indices: indices of frames to set
  '''
  for frame in indices:
    displayNode = frames[frame]['segmentation'].GetDisplayNode()
    displayNode.SetOpacity3D(opacity)
    frames[frame]['opacity'] = opacity

def setAllSegmentationVisibility(frames, opacity):
  '''
  Set opacity of all segmentations.
  :param frames: dictionary of frames
  :param opacity: opacity to set
  '''
  for frame in frames:
    displayNode = frames[frame]['segmentation'].GetDisplayNode()
    displayNode.SetOpacity3D(opacity)
    frames[frame]['opacity'] = opacity

def prepareMarching(frames, startframe=0):
  '''
  Prepare to be able to march through frames.
  :param frames: dictionary of frames
  :param startframe: frame to start marching from
  :return currentFrame: current frame marching from
  '''
  setAllSegmentationVisibility(frames, 0)
  setSegmentationVisibility(frames, 1, [startframe])
  currentFrame = startframe
  
  return currentFrame

def step(frames, currentFrame, step=1, display=True):
  '''
  March current frame forward by step.
  :param frames: dictionary of frames
  :param currentFrame: current frame marching from
  :param step: step to march by
  :param display: boolean of whether to display frame number as text
  :return currentFrame: current frame marching from
  '''
  previousFrame = currentFrame
  currentFrame += step
  
  if currentFrame >= len(frames) - 1:
    currentFrame = 0
  
  setSegmentationVisibility(frames, 0, range(previousFrame, currentFrame))
  setSegmentationVisibility(frames, 1, [currentFrame])
  
  if display:
    print(f'Went from {previousFrame} to {currentFrame}')
    
  return currentFrame

def marchSingleFrame(frames, currentFrame, newFrame):
  '''
  March to a specific frame number.
  :param frames: dictionary of frames
  :param newFrame: frame to march to
  :return currentFrame: current frame marching from
  '''
  if newFrame in frames.keys():
    setSegmentationVisibility(frames, 0, [currentFrame])
    setSegmentationVisibility(frames, 1, [newFrame])
    currentFrame = newFrame
    
  return currentFrame

def marchStepRange(frames, currentFrame, step=1, breadth=1, display=True):
  '''
  :param frames: dictionary of frames
  :param currentFrame: current frame marching from
  :param step: step to march by
  :param breadth: viewable range of frames
  :param display: boolean of whether to display frame number as text
  :return currentFrame: current frame marching from
  '''
  for _ in range(step):
    if currentFrame >= len(frames) - 1:
      currentFrame = 0
      
    setSegmentationVisibility(frames, 0, [currentFrame])
    currentFrame += 1
  
  for i in range(breadth):
    setSegmentationVisibility(frames, 1, [(currentFrame + i) % (len(frames) - 1)])
    
  if display:
    print(f'Went from {list(range(currentFrame - step, currentFrame + breadth - 1))} to {list(range(currentFrame, currentFrame + breadth))}')
  
  return currentFrame

def viewable(frames):
  '''
  :param frames: dictionary of frames
  '''
  out = []
  
  for frame, value in frames.items():    
    if value['opacity'] > 0:
      out.append(frame)
  
  if len(out) > 0:  
    print('Visible frames:', ', '.join(str(i) for i in out))
  else:
    print('No visible frames')

# Sample run
directory = '/Users/pscovel/Documents/data/placenta-segmentation/test_inference/MAP-C517-L2'

segmentations = createFrames(directory + '/predicted_segmentation')
volumes = createFrames(directory + '/volume')

segmentations = loadVolumes(segmentations, namePrefix='Segmentation', labelmap=True)
volumes = loadVolumes(volumes, namePrefix='Volume')

frames = combineSegmentationsAndVolumes(segmentations, volumes)
frames = createClosedSurfaceOfSegmentation(frames, namePrefix='ClosedSurface')

currentFrame = prepareMarching(frames)
viewable(frames)

currentFrame = marchStepRange(frames, currentFrame, breadth=2, display=True)
currentFrame = marchStepRange(frames, currentFrame, breadth=2, display=True)
currentFrame = marchStepRange(frames, currentFrame, breadth=2, display=True)
viewable(frames)

setAllSegmentationVisibility(frames, 1)
#etc...