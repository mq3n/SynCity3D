'''
Take a snapshot of a current view in the scene
'''

import sys
if sys.platform.startswith('java'):
    from scripting import *
else:
    from cityengine import *

import datetime  

ce = CE()

PHOTO_FILES_PATH = "photos"
import time

    
def take_a_snapshot(view, add_info=""):
    
    current_time = datetime.datetime.now()
    path = f"/snapshot_{current_time.strftime('%a_%d_%b_%Y_%I_%M_%S')}-{add_info}.png"    
               
    ce.waitForUIIdle()
    ce.setSelection(None) 
    view.snapshot(ce.toFSPath(PHOTO_FILES_PATH) + path)


def snapshot():
    # snapshot current inspector view
    views = ce.getObjectsFrom(ce.get3DViews())
    if len(views) < 1: 
        print("no view found")
        return
    else :
        #in city engine you can open multiple 3D views
        view = views[0] 
    
    take_a_snapshot(view)


def set_rule_attribute_value(attribute, value): 
    rule_attribute = "/ce/rule/" + attribute
    
    buildings = ce.getObjectsFrom(ce.scene())

    print(f"Changing  {rule_attribute} to value: {value}")
    for building in buildings:
        ce.setAttributeSource(building, rule_attribute, "USER")
        ce.setAttribute(building, rule_attribute, value)

    ce.waitForUIIdle()
    print(f"Changed {rule_attribute} to value: {value}")
    

def set_rule_attribute_value_to_selected_objects(objects, attribute, value): 
    rule_attribute = "/ce/rule/" + attribute
    
    print(f"Changing {rule_attribute} to value: {value}")
    for building in objects:
        ce.setAttributeSource(building, rule_attribute, "USER")
        ce.setAttribute(building, rule_attribute, value)

    ce.waitForUIIdle()
    print(f"Changed {rule_attribute} to value: {value}")


def get_objects_from_selection():
    selected_buildings = ce.getObjectsFrom(ce.selection(), ce.isShape)
    return selected_buildings


def snapshot_selected():
    selected = get_objects_from_selection()

    views = ce.getObjectsFrom(ce.get3DViews())
    if len(views) < 1: 
        print("no view found")
        return
    else :
        view = views[0] 

    # adjusts camera view
    view.frame(selected)
    take_a_snapshot(view)


def snapshot_with_changing_params(attribute, parameter_values):
    rule_attribute = "/ce/rule/" + attribute
    
    selected_buildings = get_objects_from_selection()
    
    set_rule_attribute_value_to_selected_objects(selected_buildings, "CONSTRUCTION_DISPLAY", False)
    snapshot()
    set_rule_attribute_value_to_selected_objects(selected_buildings, "CONSTRUCTION_DISPLAY", True)
    
    for value in parameter_values:
        #for building in selected_buildings:
            #ce.setAttributeSource(building, rule_attribute, "USER")
            #ce.setAttribute(building, rule_attribute, value)
        print("value:", value)  
        set_rule_attribute_value_to_selected_objects(selected_buildings, attribute, value)
        #ce.waitForUIIdle()
        time.sleep(3)
        print("XX")
        snapshot()
    
    print("DONE")

def tilt_test():
    ce.get3DViews()[0].setCameraRotation(0,0,0)
    time.sleep(3)
    ce.get3DViews()[0].setCameraRotation(15,0,0)
    time.sleep(3)
    ce.get3DViews()[0].setCameraRotation(0,20,0)
    time.sleep(3)
    ce.get3DViews()[0].setCameraRotation(0,-20,0)
    time.sleep(3)
    ce.get3DViews()[0].setCameraRotation(10,-20,0)
    time.sleep(3)
    ce.get3DViews()[0].setCameraRotation(0,0,0)
    time.sleep(3)
    
    
    print("DONE")


if __name__ == '__main__':
    
    #selected = get_objects_from_selection()
    #set_rule_attribute_value_to_selected_objects(selected, "DATASET_METHOD", "1")
    #snapshot_selected()
    #snapshot()
    #snapshot_with_changing_params("METHOD", [1, 2])
    tilt_test()
    
    
