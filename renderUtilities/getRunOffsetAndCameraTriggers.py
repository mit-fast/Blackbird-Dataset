#!/usr/bin/env python3

# Winter Guerra <winterg@mit.edu>
# August 3nd, 2018

# Takes pose files and centers them. Also makes sure that min altitude is 0m.

import fire
import glob2, os, sys, re, yaml, csv
import numpy as np

def getFilenamesForLog(logPath):
    fileStem = os.path.splitext(logPath)[0]
    print(fileStem)
    
    # Filenames
    filenames ={
        "paramFilename": fileStem + ".yaml",
        "poselistFilename": fileStem + "_poses.csv",
        "poselistCenteredFilename": fileStem + '_poses_centered.csv',
        "poseOffsetFilename": fileStem + '_poses_offset.csv'
    }
    return filenames
    

def offsetPoseList(fps, logPath):

    files = getFilenamesForLog(logPath)

    
    with open(files["paramFilename"], 'r') as paramFile:
   
        params = yaml.safe_load(paramFile)
        # Get the mocap room offset used for this particular run
        poseOffset = np.array(params["Controllers"]["Trajectory"]["offsetPos"])
        poseList = np.loadtxt(open(files["poselistFilename"], "rb"), delimiter=",")

        # Zero out z, such that min altitude is 0m (takes off from ground).
        minAlt = np.max(poseList[:,3])
        print("Min Alt: " + str(minAlt))
	poseOffset[2] = minAlt
        print(poseOffset)

        # Subtract the xyz offset
        poseList[:, 1:4] = poseList[:, 1:4] - poseOffset

        print("Original pose matrix: ")
        print(poseList.shape)

        lastTS = 0
        rowList = []
        # Prune poseList to fps
        frameLengthMicroseconds = (1.0e6/fps)*0.9
        for i,ts in enumerate(poseList[:,0]):
            if ( ts-lastTS >= frameLengthMicroseconds):
                lastTS = ts 
                rowList.append(i)

        # Select rows
        poseList = poseList[rowList, :]

        print("Pruned pose matrix shape:")
        print(poseList.shape)

        # Calculate nominal framerate
        dts = np.diff(poseList[:,0])
        nominaldts = np.average(dts)
        fps = 1.0e6/nominaldts
        print("Nominal FPS:")
        print(fps)
        # Calculate max gap
        maxGap = np.max(dts)
        print("max ms gap:")
        print(maxGap/1.0e3)
        print("Max frame gap: ")
        print(maxGap/8333.0)
        # Save offset
        np.savetxt(files["poseOffsetFilename"], poseOffset.reshape([1,3]), delimiter=",", fmt='%f')
        # Save new trajectory
        np.savetxt(files["poselistCenteredFilename"], poseList, delimiter=",", fmt=['%d','%f','%f','%f','%f','%f','%f','%f'])


if __name__ == '__main__':
    fire.Fire(offsetPoseList)
