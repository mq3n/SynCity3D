"""
Created on 03-02-2020

@author: rendering
"""

# from scripting import *
from cityengine import *

ce = CE()
import time


class sides:
    sides = set(["top", "bottom", "right", "left", "front", "back"])
    top = [90, 0, 0, "top"]
    bottom = [270, 0, 0, "bottom"]
    right = [0, 90, 0, "right"]
    left = [0, 270, 0, "left"]
    front = [0, 0, 0, "front"]
    back = [0, 180, 0, "back"]


def create_90_FOV(side, cnt, prefix, tilt):
    global viewport, sides, ce
    viewport.setPoIDistance(50)
    viewport.setCameraRotation(side[0], side[1], side[2])
    ce.waitForUIIdle()
    filename = "/" + prefix + "_snapshot_%s_%s_%s.png" % (side[3], tilt, cnt)
    viewport.snapshot(ce.toFSPath("images") + filename, 1920, 1920)


def make_tmp_snapshot(filename):
    global ce, viewport
    viewport.snapshot(ce.toFSPath("images/tmp") + filename, 1024, 1024)


def create_photo_set(main_road="main_road", prefix="x", tilt=0, cameraStep = 50, cameraHeight=17 ):
    global viewport, ce
    print("generowanie zdjec dla zestawu " + prefix)
    #ce = CE()
    viewport = {}

    mainRoad = ce.getObjectsFrom(ce.scene, ce.withName(main_road))
    counter = 0
    for segment in mainRoad:
        vertices = ce.getVertices(segment)
        viewport = ce.get3DViews()[0]
        print(vertices)
        # vertices = [0,0,-1000,0,0,1000]
        x = vertices[0]  # at edge on segment begin
        x2 = vertices[3]  # at edge on segment end
        y = vertices[1] + cameraHeight  # height
        z1 = int(vertices[2])  # street beginning
        z2 = int(vertices[5])  # street end

        # test
        # z1 = 1000
        # z2 = -1000

        print("street from %d to %d" % (z2, z1))
        for z in range(z1, z2, cameraStep):
            x_on_edge = x2 - ((z2 - z) / (z2 - z1)) * (x2 - x)
            print("set camera on %f,%f,%f" % (x_on_edge, y, z))
            viewport.setCameraPosition(x_on_edge, y, z)
            # viewport.setCameraRotation(0,0,0)
            # time.sleep(2)
            counter += 1
            for sideName in sides.sides:
                create_90_FOV(getattr(sides, sideName), counter, prefix, tilt)
        print("generowanie zdjec zakonczone")


def make_one_shot():
    pass


# one shot for test
#    viewport.setCameraPosition(x, y, z2)
#    for sideName in sides.sides:
#        create90FOV(getattr(sides, sideName))

#    create90FOV(sides.bottom)
#    create90FOV(sides.right)
#    create90FOV(sides.left)
#    create90FOV(sides.front)
#    create90FOV(sides.back)
