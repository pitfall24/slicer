import cv2
import os
import nibabel as nib
import numpy as np
from PIL import Image
import pygame as pg

class ImageSet():
    def __init__(self, path, *args, **kwargs):
        self.path = path
        self.frames = []
        self.data = []
        
        self.load()
        
    def load(self):
        for i in os.listdir(self.path):
            self.frames.append(nib.load(os.path.join(self.path, i)))
        
        for i in self.frames:
            self.data.append(i.get_fdata())
            
    def slice(self, frame, index, axis=None):
        return np.take(self.data[frame], index, axis, mode='clip')
    
    def minmax(self):
        return [np.amin(self.data), np.amax(self.data)]
            
    def show(self, frame, indices, axis=None):
        ims = [Image.fromarray(np.take(self.data[frame], index, axis, mode='clip')) for index in indices]
        for i in ims:
            i.show()
            
def gray(image):
    image = 255 * (image / image.max())
    
    width, height = image.shape
    
    ret = np.empty((width, height, 3), dtype=np.uint8)
    ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = image
    
    return ret

def color(image, color):
    image = 255 * (image / image.max())
    
    width, height = image.shape
    
    ret = np.empty((width, height, 3), dtype=np.uint8)
    ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = image
    
    ret[:, :, 0] = ((ret[:, :, 0].astype(np.float32) * color[0]) / 255).astype(np.uint8)
    ret[:, :, 1] = ((ret[:, :, 1].astype(np.float32) * color[1]) / 255).astype(np.uint8)
    ret[:, :, 2] = ((ret[:, :, 2].astype(np.float32) * color[2]) / 255).astype(np.uint8)
    
    return ret

def get_edges(mask, toggle):
    if not toggle:
        return mask
    
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    out = np.zeros(mask.shape, dtype=np.uint8)
    
    for i in contours:
        for j in i:
            out[j[0][1], j[0][0]] = 255
    
    return out