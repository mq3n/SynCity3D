'''
Created on 03-02-2020

@author: rendering
'''
from scripting import *
import time


class sides:
    sides = set(['top', 'bottom', 'right', 'left', 'front', 'back'])
    top = [90, 0, 0, 'top']
    bottom = [270, 0, 0, 'bottom']
    right = [0, 90, 0, 'right']
    left = [0, 270, 0, 'left']
    front = [0, 0, 0, 'front'] 
    back = [0, 180, 0, 'back']

# get a CityEngine instance
ce = CE()
viewport = {}

def create90FOV(side, cnt):
    global viewport,sides, ce
    viewport.setCameraRotation(side[0], side[1] + 30, side[2])
    filename="/z_snapshot_%s_%s.png" % (side[3],cnt) 
    viewport.snapshot(ce.toFSPath('images') + filename, 1920, 1920)
    
    
def makeTmpSnapshot(filename): 
    global ce, viewport   
    viewport.snapshot(ce.toFSPath('images/tmp') + filename, 1920, 1920)
    

if __name__ == '__main__':
    global viewport
#    ce.setSelection(ce.getObjectsFrom(ce.scene,ce.withName("main_road")))
    mainRoad = ce.getObjectsFrom(ce.scene, ce.withName("major_edge"))
    vertices = ce.getVertices(mainRoad[0])
    viewport = ce.getObjectsFrom(ce.get3DViews(), ce.isViewport)[0]

    x = vertices[0] - 5 #at edge
    y = vertices[1] + 1.7 #height
    z1 = vertices[2] #street beginning
    z2 = vertices[5] #street end


#one shot for test
#    viewport.setCameraPosition(x, y, z2)
#    for sideName in sides.sides:
#        create90FOV(getattr(sides, sideName))
        
#    create90FOV(sides.bottom)
#    create90FOV(sides.right)
#    create90FOV(sides.left)
#    create90FOV(sides.front)
#    create90FOV(sides.back)

    counter = 0
    for z in range(z2,z1,10):
        viewport.setCameraPosition(x,y,z)
        viewport.setCameraRotation(0,270,0) 
        #time.sleep(2)
        counter += 1
        for sideName in sides.sides:
            create90FOV(getattr(sides, sideName), counter)

        

