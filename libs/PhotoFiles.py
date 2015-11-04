#!/usr/bin/env python
import Filter
import os.path

photo_exts = ['png','jpg','jpeg','bmp','gif','ico','tif','tiff','tga','pcx','dng','nef','cr2','crw','orf','arw','erf','3fr','dcr','x3f','mef','raf','mrw','pef','sr2', 'mpo', 'jps', 'rw2']

# Remove files that aren't audios.
def Scan(path, files, mediaList, subdirs, root=None):
  
  # Filter out bad stuff.
  Filter.Scan(path, files, mediaList, subdirs, photo_exts, root)
