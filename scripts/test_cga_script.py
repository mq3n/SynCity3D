'''
Created on Apr 19, 2026

@author: pawel

Changing values of specific <test_cga_script.cga> rule attribute - param_height
'''
import sys
if sys.platform.startswith('java'):
    from scripting import *
else:
    from cityengine import *
    
import random
import time
import datetime

# get a CityEngine instance
ce = CE()
# exists in Project in workspace
PHOTO_FILES_PATH = "photos"


def print_shape_attributes(shapes):
    print("\nPRINT SHAPE ATTRIBUTES ---")
    for shape in shapes:
        print("-"*10)
        print(f"Name: {ce.getName(shape)}, obejctID: {ce.getOID(shape)}")
        print(f"Object Attributes: {ce.getAttributeList(shape)}")
        print(f"Rule assigned to object: {ce.getRuleFile(shape)}")
        
        #if ce.getRuleFile(shape):
        #print("RULE INFO")
        rule_info = ce.getRuleFileInfo(ce.getRuleFile(shape))
        if rule_info:
            for key, value in rule_info.items():
                print("KEY:", key)
                print("VALUE:", value)
            

def change_shape_attribute_values(shapes):
    print("\nCHANGE SHAPE_ATTRIBUTES ---")
    for shape in shapes:
        new_value_1 = random.randint(1, 10)
        new_value_2 = random.randint(11, 20)
        
        # attribute names in RULE and OBJECT have to match
        object_param_name = "param_height"
        rule_param_name = "/ce/rule" + object_param_name
        
        #if object_param_name in ce.getAttributeList(shape):
        object_param_value = ce.getAttribute(shape, object_param_name)
        print(f"1 - Current {object_param_name} value:", object_param_value)
        
        time.sleep(5)
        #assign new value to object attribute {object_param_name}; creates this attribute if it doesn't exist
        ce.setAttribute(shape, object_param_name, new_value_1)
        #bound rule attribute to object attribute
        print(ce.getAttributeSource(shape, object_param_name))
        ce.setAttributeSource(shape, rule_param_name, 'OBJECT')
        
        object_param_value = ce.getAttribute(shape, object_param_name)
        print(f"2 - Current {object_param_name} value:", object_param_value)
        
        time.sleep(5)
        ce.setAttribute(shape, object_param_name, new_value_2)
        
        object_param_value = ce.getAttribute(shape, object_param_name)
        print(f"2 - Current {object_param_name} value:", object_param_value)


def set_rule_attribute_value(attribute, value): 
    rule_attribute = "/ce/rule/" + attribute
    buildings = ce.getObjectsFrom(ce.scene())
    
    for building in buildings:
        ce.setAttributeSource(building, rule_attribute, "USER")
        ce.setAttribute(building, rule_attribute, value)
    
    print(f"CHANGED {rule_attribute} to value: {value}")
    
    ce.waitForUIIdle()

def change_visibility(shapes):
    print("\nCHANGE VISIBILITY ---")
    shape_1 = shapes[0]
    visibleLayers = ce.getObjectsFrom(ce.scene, ce.isVisible)
    print(len(visibleLayers), visibleLayers)
    

    
def take_a_snapshot(view,add_info=""):
    
    current_time = datetime.datetime.now()
    ct = current_time.strftime('%a-%d-%b-%Y-%I:%M%p')
    path = f"/snapshot_{current_time.strftime('%a_%d_%b_%Y_%I_%M_%S')}-{add_info}.png"
    #print("PATH:", path)        
               
    ce.waitForUIIdle()
            
    # take a snapshot
    view.snapshot(ce.toFSPath(PHOTO_FILES_PATH)+ path)


def print_render_settings(view):
        print("\nRENDER SETTINGS")
        renderSettings = view.getRenderSettings()
        print("Render Mode:", renderSettings.getMode())
        print("WireframeOnShaded:", renderSettings.getWireframeOnShaded())
        print("Shadows:", renderSettings.getShadows())
        print("Ambient Occlusion", renderSettings.getAmbientOcclusion())
        print("Camera on Light", renderSettings.getOnCameraLight())
        print("Single Side Lighting:", renderSettings.getSingleSidedLighting())
        print("Back Face Culling", renderSettings.getBackFaceCulling())
        print("InfoDisplay Visible:", renderSettings.getInfoDisplayVisible())
        print("Axes Visible:", renderSettings.getAxesVisible())
        print("Compass Visible:", renderSettings.getCompassVisible())
        print("Grid Visible:", renderSettings.getGridVisible())
        print("Gizmos Visible:", renderSettings.getGizmosVisible())


def print_camera_info(view):
        print("="*10)
        print("CAMERA INFO:")
        print("Camera Perspective:", view.getCameraPerspective())
        print("Camera Angle of View:", view.getCameraAngleOfView())
        cam_poi = view.getCameraPoI()
        print("Camera Point of Interest:", [cam_poi[0], cam_poi[1], cam_poi[2]])
        cam_pos = view.getCameraPosition()
        print("Camera Position:", [cam_pos[0], cam_pos[1], cam_pos[2]])
        cam_rot = view.getCameraRotation()
        print("Camera Rotation:", [cam_rot])
        print("Camera 2 point Perspective Correction:", view.getCameraTwoPointPerspectiveCorrection())
        print("Camera Perspective:", view.getCameraPerspective())


def print_camera_position(view):
    print("\nCAMERA POSITION")
    cam_pos = view.getCameraPosition()
    pos_list = [cam_pos[0], cam_pos[1], cam_pos[2]]
    print("Camera Position: x, y, z:", pos_list)

def snapshot_test():
    print("\nSNAPSHOTS TEST")
    
    # snapshot current inspector view
    views = ce.getObjectsFrom(ce.get3DViews())
    
    if len(views) < 1: 
        print("no view found")
    else :
        
        #in city engine you can open multiple 3D views
        view = views[0] 
        print_render_settings(view)
        
        shapes = ce.getObjectsFrom(ce.scene, ce.isShape)
        print("SHAPES:", shapes)
        print(len(shapes))
        
        print("\nNO FRAME")
        take_a_snapshot(view, "no_frame")
        print_camera_info(view)
        
        #default is none, it somehow adjust view to.. i dont know yet
        print("\nFRAME NONE")
        view.frame()
        time.sleep(1)
        take_a_snapshot(view, "frame_none")
        print_camera_info(view)
        
        print("\nFRAME SHAPE[0]")
        view.frame(shapes[0])
        time.sleep(1)
        take_a_snapshot(view, "frame_shape_0")
        print_camera_info(view)
        
        print("\nFRAME SHAPE[1]")
        view.frame(shapes[1])
        time.sleep(1)
        take_a_snapshot(view, "frame_shape_1")
        print_camera_info(view)
        
        print("\nFRAME SHAPES")
        view.frame(shapes)
        take_a_snapshot(view, "frame_shapes")
        print_camera_info(view)
        
        
        #print_camera_info(view)

  
     

if __name__ == '__main__':
    print("\nScript initiated")
    
    print(ce.scene())
    
    #get a list of all shapes in the scene
    shapes = ce.getObjectsFrom(ce.scene, ce.isShape)
    print("Shapes:", shapes,", it's type is:", type(shapes), "\n")
    
    #print_shape_attributes(shapes)
    set_rule_attribute_value("MY_LIST", [20, 30, 40, 50])
    
    
    #change_shape_attribute_values(shapes)
    #change_visibility(shapes)   
    #snapshot_test()
          
    print("Done.")
        
        
        