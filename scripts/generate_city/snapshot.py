"""
Created on 03-02-2020

@author: rendering
"""

# from scripting import *
from cityengine import *
from .environment import *

ce = CE()
import time
from pathlib import Path
import random
import shutil
import os
import numpy as np

# it lasts forever...
# MOUNT_DIR = Path(r"C:\Users\WA\Desktop\photo_size_test_mount")
# SIDES_IMAGE_DIR = MOUNT_DIR / "images_sides"
# SVI_IMAGE_DIR = MOUNT_DIR / "1920x1080_svi"


SNAPSHOT_DIR = Path(r"C:\Users\WA\Desktop\badanie\syncity3D\dataset_stages")
SIDES_IMAGE_DIR = SNAPSHOT_DIR / "snapshot_sides"
SVI_IMAGE_DIR = SNAPSHOT_DIR / "snapshot_svi"


class sides:
    sides = set(["top", "bottom", "right", "left", "front", "back"])
    top = [90, 0, 0, "top"]
    bottom = [270, 0, 0, "bottom"]
    right = [0, 90, 0, "right"]
    left = [0, 270, 0, "left"]
    front = [0, 0, 0, "front"]
    back = [0, 180, 0, "back"]


def create_90_FOV(side, cnt, prefix):
    global viewport, sides, ce
    
    #pos = ce.get3DViews()[0].getCameraPosition()    #!
    #ce.get3DViews()[0].setCameraPoI([pos[0] + 1000, pos[1], pos[2] + 1000]) #!

    viewport.setPoIDistance(50)
    viewport.setCameraRotation(side[0], side[1], side[2])
    viewport.setCameraAngleOfView(90) #!
    ce.waitForUIIdle()

    filename = f"{prefix}_snapshot_{side[3]}_{cnt}.png"
    #filename = f"/{prefix}_snapshot_{side[3]}_{tilt}_{cnt}.png"
    #filename = "/" + prefix + "_snapshot_%s_%s_%s.png" % (side[3], tilt, cnt)
    #viewport.snapshot(ce.toFSPath("images") + filename, 1920, 1920)
    local_file_path = os.path.join(ce.toFSPath("images"), filename)
    file_path = SIDES_IMAGE_DIR / filename

    viewport.snapshot(str(file_path), 1920, 1920)

    # credentials...
    # try:
    #     shutil.move(str(local_file_path), str(rclone_file_path))
    # except Exception as e:
    #     print(f"Error rclone: {e}")

    #viewport.snapshot(str(SIDES_IMAGE_DIR / filename), 1920, 1920)
    print("SIDE saved:" + prefix + "_" + side[3] + "_" +str(cnt))


def create_90_FOV_svi(rng, cnt, prefix):
    viewport.setPoIDistance(50)
    
    vertical_tilt = int(rng.integers(0, 20))
    horizontal_tilt = int(rng.integers(-30, 30))
    angle_of_view = int(rng.choice([90, 121, 54])) # values taken from cityengine corresponding to 18mm, 10mm fisheye and 50mm lens
    #viewport.setCameraAngleOfView(90) #!
    viewport.setCameraAngleOfView(angle_of_view)
    viewport.setCameraRotation(vertical_tilt, horizontal_tilt, 0)

    filename = f"{prefix}_snapshot_{angle_of_view}_{cnt}.png"

    #local_file_path = os.path.join(ce.toFSPath("images"), filename)
    file_path = SVI_IMAGE_DIR / filename

    viewport.snapshot(str(file_path), 1920, 1080)

    # credentials...
    # try:
    #     shutil.move(str(local_file_path), str(rclone_file_path))
    # except Exception as e:
    #     print(f"Error rclone: {e}")


    #viewport.snapshot(str(SVI_IMAGE_DIR / filename), 1024, 2048)
    print("SVI saved:" + prefix + "_" +str(cnt))

    ce.waitForUIIdle()
    return



def make_tmp_snapshot(filename):
    global ce, viewport
    viewport.snapshot(ce.toFSPath("images/tmp") + filename, 1024, 1024)


def create_mask(value, scene_name):
    set_shadows(not value)
    set_street_visibility(not value, scene_name)
    set_scene_env_for_mask(value)
    set_rule_attribute_value("CONSTRUCTION_DISPLAY", value)
    

def set_rule_attribute_value(attribute, value): 
    rule_attribute = "/ce/rule/" + attribute
    buildings = ce.getObjectsFrom(ce.scene(), ce.withName("lot"))
    print("rendering... atribute value change:" + attribute + "=" + str(value))
    
    for building in buildings:
        ce.setAttributeSource(building, rule_attribute, "USER")
        ce.setAttribute(building, rule_attribute, value)
    
    print(f"CHANGED {rule_attribute} to value: {value}")
    
    ce.waitForUIIdle()


#create_photo_set(cameraStep = 10, cameraHeight=5, prefix=city_name, set_type=element, city_number=i)
def create_photo_set(main_road="main_road", prefix="x", space_type="Normal", city_number=0, tilt=0, cameraStep = 50, cameraHeight=17):
    global viewport, ce
    print("taking a photo set:", prefix, ", ", space_type, ", ", city_number)

    # for svi !!!
    rng=np.random.default_rng(0)
    
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
            
            # test
            if counter == 100:
                break
            
            counter += 1
            # for sideName in sides.sides:
            #     #print("PHOTO SIDE:" + sideName)
            
            #     # sky config is important as it 'resets' the counter for LOD x Space
            #     # prefix for photos is: <city: e.g. SynCity3D_<space: Normal/Building/Door/Windows_<city_number: 0, 1, etc.>>
            #     create_90_FOV(getattr(sides, sideName), counter, prefix + "_m-"  + str(space_type) + "_" + str(city_number))
        
            create_90_FOV_svi(rng, counter, prefix + "_m-"  + str(space_type) + "_" + str(city_number))

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
