#---
# iPIN - iPhone PNG Images Normalizer v1.0
# Copyright (C) 2007
#
# Author:
#  Axel E. Brzostowski
#  http://www.axelbrz.com.ar/
#  axelbrz@gmail.com
# 
# References:
#  http://iphone.fiveforty.net/wiki/index.php/PNG_Images
#  http://www.libpng.org/pub/png/spec/1.2/PNG-Contents.html
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
#---

from struct import *
from zlib import *
import stat
import sys
import os

def getNormalizedPNG(filename):
    pngheader = "\x89PNG\r\n\x1a\n"

    
    file = open(filename, "rb")
    oldPNG = file.read()
    file.close()

    if oldPNG[:8] != pngheader:
        return None
    
    newPNG = oldPNG[:8]
    
    chunkPos = len(newPNG)
    ptr = 0
    chunkD = []
    
    # For each chunk in the PNG file
    while chunkPos < len(oldPNG):
        
        # Reading chunk
        chunkLength = oldPNG[chunkPos:chunkPos+4]
        chunkLength = unpack(">L", chunkLength)[0]
        chunkType = oldPNG[chunkPos+4 : chunkPos+8]
        chunkData = oldPNG[chunkPos+8:chunkPos+8+chunkLength]
        chunkCRC = oldPNG[chunkPos+chunkLength+8:chunkPos+chunkLength+12]
        chunkCRC = unpack(">L", chunkCRC)[0]
        chunkPos += chunkLength + 12


        # Parsing the header chunk
        if chunkType == "IHDR":
            width = unpack(">L", chunkData[0:4])[0]
            height = unpack(">L", chunkData[4:8])[0]
            newPNG += pack(">L", chunkLength)
            newPNG += chunkType
            if chunkLength > 0:
                newPNG += chunkData
            newPNG += pack(">L", chunkCRC)       


        # Parsing the image chunk
        if chunkType == "IDAT":
            # Uncompressing the image chunk
            bufSize = width * height * 4 + height
            ptr += len(chunkData)
            chunkD.append(chunkData)

        # Stopping the PNG file parsing
        if chunkType == "IEND":
            # Swapping red & blue bytes for each pixel
            joinD = "".join(chunkD)
            bufSize = width * height * 4 + height
            try:
                decompressD = decompress(joinD, -8, bufSize)

                newdata = ""
                for y in xrange(height):
                    i = len(newdata)
                    newdata += decompressD[i]
                    for x in xrange(width):
                        i = len(newdata)
                        newdata += decompressD[i+2]
                        newdata += decompressD[i+1]
                        newdata += decompressD[i+0]
                        newdata += decompressD[i+3]
                DchunkData = compress(newdata)
                DchunkLength = len(DchunkData)

                DchunkCRC = crc32("IDAT")
                DchunkCRC = crc32(DchunkData, DchunkCRC)
                DchunkCRC = (DchunkCRC + 0x100000000) % 0x100000000
                newPNG += pack(">L", DchunkLength)

                # Compressing the image chunk
                newPNG += "IDAT"
                if DchunkLength > 0:
                    newPNG += DchunkData
                newPNG += pack(">L", DchunkCRC)       
            except error:
                print "Could not process %s" % filename
                pass


            
            newPNG += pack(">L", chunkLength)
            newPNG += chunkType
            if chunkLength > 0:
                newPNG += chunkData
            newPNG += pack(">L", chunkCRC)       


    return newPNG

def updatePNG(filename):
    data = getNormalizedPNG(filename)
    if data != None:
        print "Processing %s" % filename
        file = open(filename, "w")
        file.write(data)
        file.close()
        return True
    else:
        print "Could not process %s" % filename
    return data

def getFiles(base):
    global _dirs
    global _pngs
    if base == ".":
        _dirs = []
        _pngs = []
        
    if base in _dirs:
        return

    files = os.listdir(base)
    for  file in files:
        filepath = os.path.join(base, file)
        try:
            st = os.lstat(filepath)
        except os.error:
            continue
        
        if stat.S_ISDIR(st.st_mode):
            if not filepath in _dirs:
                getFiles(filepath)
                _dirs.append( filepath )
                
        elif file[-4:].lower() == ".png":
            if not filepath in _pngs:
                _pngs.append( filepath )
            
    if base == ".":
        return _dirs, _pngs


