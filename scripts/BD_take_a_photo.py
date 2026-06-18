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



if __name__ == '__main__':
    
    #selected = get_objects_from_selection()
    #set_rule_attribute_value_to_selected_objects(selected, "DATASET_METHOD", "1")
    #snapshot_selected()
    snapshot()
