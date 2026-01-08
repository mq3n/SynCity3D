'''
Created on 03-02-2020

@author: rendering
'''
from scripting import *
import time

# get a CityEngine instance
ce = CE()

if __name__ == '__main__':
#    ce.setSelection(ce.getObjectsFrom(ce.scene,ce.withName("main_road")))
    mainRoad = ce.getObjectsFrom(ce.scene,ce.withName("major_edge"))
    vertices = ce.getVertices(mainRoad[0])
    viewport = ce.getObjectsFrom(ce.get3DViews(), ce.isViewport)[0]

    x = vertices[0]-5 #at edge
    y = vertices[1]+10 #height
    z1 = vertices[2] #street beginning
    z2 = vertices[5] #street end

    counter = 0
    for z in range(z2,z1,10):
        viewport.setCameraPosition(x,y,z)
        viewport.setCameraRotation(0,270,0)
        #time.sleep(2)
        counter += 1
        filename = "/i_snapshot_%s.png" % counter
        viewport.snapshot(ce.toFSPath('images') + filename,1920, 1920)
        
