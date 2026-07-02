'''
Created on Apr 23, 2026

@author: Pawel K
'''
import sys
if sys.platform.startswith('java'):
    from scripting import *
else:
    from cityengine import *
import os
import time
import random
from pathlib import Path
import numpy as np
import json

from generate_city.network import *
from generate_city.snapshot import *
from generate_city.environment import *
from generate_city.objects import *

from BD_normalize_filenames import *
from BD_create_spheric_photos import *


ce = CE()

CITY_NAME = "SynCity3D"

WORKSPACE_DIR = Path(r"C:\Users\WA\Desktop\badanie") # !! directory with our project and other projects (ESRI.lib)
BASE_DIR = WORKSPACE_DIR / "syncity3D" 
SCRIPTS_DIR = BASE_DIR / "scripts"

# stage 1 - snapshots back, right, front, left, top, bottom 
CE_SNAPSHOTS_DIR = BASE_DIR / "images"
# stage 2 - spheric 'photos' and their segmention/semantic color masks
SPHERIC_PHOTOS_DIR = BASE_DIR / "dataset_stages" / "spheric_photos_and_masks"
# final stage - COCO format ready dataset /images /annotations
COCO_DATASET_SPHERIC_DIR = BASE_DIR / "COCO_DATASETS" / "D7_SPHERIC" # D4!!!!!1
COCO_DATASET_SVI_DIR = BASE_DIR / "COCO_DATASETS" / "D7_SVI"


os.makedirs(COCO_DATASET_SPHERIC_DIR, exist_ok=True)
os.makedirs(COCO_DATASET_SVI_DIR, exist_ok=True)

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

REQUIRED_ESRI_LIBS = ["ESRI.lib", "ce.lib"]

# NOTE: we want to eliminate the possible influencing factors, so we stick with ONE Level of Detail, but cityengine makes it easy to produce buildings in multiple LODs
LODS = ["LOD3"]
#LODS = ["LOD1", "LOD2", "LOD3"]


# METHOD is a Parameter in CGA script
ANNOTATION_METHODS = [1, 2]


PANORAMA_MAPS = ["DawnSky", "BlueSky", "SunnySky", "CloudySky", "DuskSky", "NightSky"]

# NOTE: No use currently
# (ELEVATION, AZIMUTH, POSSIBLE_MAPS)
# elevation = (0 - sun set low, 90 - sun in zenith) 
# azimuth = (90 - sun on east, 270 - sun on west)
SCENES = {
    #  ["DawnSky" "CloudySky"] - redundance
    "DAWN": (10, 90, ["DawnSky"]),
    #  ["BlueSky", "SunnySky", "CloudySky"] -- redundance
    "MORNING": (25, 135, ["SunnySky"]),
    #  ["BlueSky", "SunnySky", "CloudySky"] - redundance
    "NOON": (50, 180, ["BlueSky"]),
    #  ["BlueSky", "SunnySky", "CloudySky"] - redundance
    "AFTERNOON": (25, 225, ["CloudySky"]),
    #  ["CloudySky", "DuskSky"] - redundance
    "DUSK": (10, 270, ["DuskSky"]),
    "NIGHT": (5, 270, ["NightSky"])
    }


# both are provided by ESRI by default, but we check consistency of workspace and project
def assert_esri_libs_exist(): 
    #print(os.getcwd())
    #print(os.listdir(WORKSPACE_DIR))
    
    for required_lib in REQUIRED_ESRI_LIBS:
        path = WORKSPACE_DIR / required_lib
        exists = path.exists()
        if exists is False:
            print("Library: ", required_lib, "is not present" )
            return False
    return True
 
# NOTE: currently we want to eliminate the possible influencing factors, so we stick with ONE scene
def get_scenery_configs():
    '''Create list of scene configurations which later can be used to enhance heterogenity'''
    configs = []
    for scene in SCENES.keys():
        solar_elevation, solar_azimuth = SCENES[scene][0], SCENES[scene][1]
        sky_options = SCENES[scene][2]
        for sky in sky_options:
            config = {"azimuth": solar_azimuth, "elevation": solar_elevation, "sky": sky}
            configs.append(config)          
    return configs


# CLEARS SCENE: doesn't work, throws major issues
def clear_scene():
    ce.delete(ce.getObjectsFrom(ce.scene))

# CLEARS SCENE: works, no issues, probably because of waitForUIIdle, but decided to delete by layers instead of by objects
def scene_reset():
    ce.setSelection(None)
    layers = ce.getObjectsFrom(ce.scene, ce.isLayer)
    if len(layers) > 0:
        ce.delete(layers)
    ce.waitForUIIdle()


if __name__ == '__main__':

    # just make sure everything is in place in workspace
    libs_present = assert_esri_libs_exist()
    if libs_present is False:
        sys.exit(1)

    print("="*10 + "START" + "="*10)


    n_of_parameters = 10
    # evenly distributed
    parameters_list = [round(param, 2) for param in np.linspace(0.5, 2.5, n_of_parameters).tolist()]

    start_time = time.time()

    hideGrid()

    ce.setSelection(None) 

    # only LOD3
    lod = LODS[0]

    # NOTE: currently we want to eliminate the possible influencing factors, so we stick with ONE scene
    #scene_configs = get_scenery_configs()
    scene = {"azimuth": 180, "elevation": 50, "sky": "BlueSky"}

    # if we would prefer multiple sceneries - now we stick with just 1
    #for scene in scene_configs[:]:

    #hidePanorama()
    #create_mask(True, CITY_NAME)
    #set_rule_attribute_value("METHOD", 1)

    #scene_sky = scene["sky"]
    #print("Scene sky:", scene_sky)

    #print("Clearing City")
    #scene_reset()

    # if we would like to have more data, 1 city ~ 200 photos
    n_of_cities = 5

    #for lod in LODS[:]:

    for i in range(n_of_cities):

        city_name = CITY_NAME
        #city_name = f"{CITY_NAME}_{lod}" 

        # sets the scene panorama, sun, lighting proporties etc
        # MODULE: environment.py
        set_environment_config(scene)


        # fresh start
        print("Clearing City" + "="*5)
        scene_reset()

        print("PARAMETERS LIST:", parameters_list)
        # MODULE: generate_city/network.py
        print("Creating City" + "="*5)
        create_random_city(city_name, level_of_detail=lod)
        set_rule_attribute_value("PARAMETERS_LIST", parameters_list)    #couldn't replace this list in previous (create_random_city) func, but this one works

        ce.setSelection(None) 
        showPanorama()
        #create_mask(False, city_name)
        
        print("Taking photos" + "="*5)
        # PHOTO TYPE: NORMAL
        # MODULE: generate_city/snapshot.py
        

        create_photo_set(cameraStep = 10, cameraHeight=5, prefix=city_name, space_type="Normal", city_number=i)

        hidePanorama()
        create_mask(True, city_name)
        
        
        #for element in COMPOSITIONAL_ELEMENTS[:]:
        for method in ANNOTATION_METHODS[:]:
            
            #set_rule_attribute_value("CHOSEN_ELEMENT", element)
            set_rule_attribute_value("ANNOTATION_METHOD", method)

            # PHOTO TYPE: MASK <element>
            create_photo_set(cameraStep = 10, cameraHeight=5, prefix=city_name, space_type=method, city_number=i)
            #pass           
        
        create_mask(False, city_name)
        showPanorama()

    print("Finished taking photos")

    photoshoot_time = time.time()
    
    time.sleep(5)   # just in case
    # MODULE: BD_normalize_filenames
    print("Normalizing filenames" + "="*5)
    rename_all_new_spheric_photos()
    rename_all_new_svi_photos()
   

    #time.sleep(5)   # just in case
    print("Creating 360photos" + "="*5)
    # MODULE: BD_create_spheric_photos
    convert_every_available_file()

    
    time.sleep(5)  # just in case
    #turned out to be unnecessary, so we skip it
    #print("Removing artefacts" + "="*5)
    clean_every_spheric_file()
    clean_every_svi_file()

    # NOTE: creating annotations is NOT included
    finish_time = time.time()
    print("="*10 + " DONE " + "="*10)


    city_parameters = {
        #"seed": SEED,
        "parameter_range": [0.5, 2.55],
        "parameters": parameters_list
    }

    city_parameters["creation_time"] = round(finish_time - start_time, 2)
    city_parameters["photoshoot_time"] = round(photoshoot_time - start_time, 2)
    
    
    # LATER
    #IMAGES_DIR =  Path("images")
    #DATASET_DIR = Path("dataset")

    # already removed
    #normal_images = [path for path in os.listdir(CE_SNAPSHOTS_DIR) if ("m-Normal" in path)]
    #m1_images = [path for path in os.listdir(CE_SNAPSHOTS_DIR) if ("m-1" in path)]
    #m2_images = [path for path in os.listdir(CE_SNAPSHOTS_DIR) if ("m-2" in path)]

    # spheric_normal_images = [path for path in os.listdir(SPHERIC_PHOTOS_DIR) if ("m-Normal" in path)]
    # spheric_m1_images = [path for path in os.listdir(SPHERIC_PHOTOS_DIR) if ("m-1" in path)]
    # spheric_m2_images = [path for path in os.listdir(SPHERIC_PHOTOS_DIR) if ("m-2" in path)]

    # # already removed
    # #city_parameters["total_n_of_photos"] = len(normal_images) + len(m1_images) + len(m2_images)
    # #city_parameters["n_normal_of_photos"] = len(normal_images) 
    # #city_parameters["n_m1_of_photos"] = len(m1_images) 
    # #city_parameters["n_m2_of_photos"] = len(m2_images) 

    # city_parameters["total_n_of_spheric_photos"] = len(spheric_normal_images) + len(spheric_m1_images) + len(spheric_m2_images)
    # city_parameters["n_spheric_normal_of_photos"] = len(spheric_normal_images) 
    # city_parameters["n_spheric_m1_of_photos"] = len(spheric_m1_images) 
    # city_parameters["n_spheric_m2_of_photos"] = len(spheric_m2_images) 

    
    # Coco dataset path - different location than previous just parameters on creation time stats
    city_parameters_spheric_path = COCO_DATASET_SPHERIC_DIR / "city_parameters.json"
    city_parameters_spheric_path.touch()
    city_parameters_svi_path = COCO_DATASET_SVI_DIR / "city_parameters.json"
    city_parameters_svi_path.touch()

    with open(city_parameters_spheric_path, mode="w") as file:
        json.dump(city_parameters, file, indent=2)
    
    with open(city_parameters_svi_path, mode="w") as file:
        json.dump(city_parameters, file, indent=2)
    
    print("DONE")
    #print("Building dataset took:", round(finish_time - start_time, 2), "s")
    