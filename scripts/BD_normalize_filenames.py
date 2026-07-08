import os
from pathlib import Path
import re

# f.e
#PATH: images\SynCity3D_m-1_<0>_snapshot_back_<2>.png
#OLD FILENAME: SynCity3D_m-1_1_snapshot_back_1.png
#NEW FILENAME: m-1_SynCity3D_snapshot_back_11.png



WORKSPACE_DIR = Path(r"C:\Users\WA\Desktop\badanie") # !! directory with our project and other projects (ESRI.lib)
BASE_DIR = WORKSPACE_DIR / "syncity3D" 
SCRIPTS_DIR = BASE_DIR / "scripts"

# stage 1 - snapshots back, right, front, left, top, bottom 
CE_SNAPSHOTS_DIR = BASE_DIR / "images"

SNAPSHOT_DIR = Path(r"C:\Users\WA\Desktop\badanie\syncity3D\dataset_stages")
SIDES_IMAGE_DIR = SNAPSHOT_DIR / "snapshot_sides"
SVI_IMAGE_DIR = SNAPSHOT_DIR / "snapshot_svi"


# MOUNT_DIR = Path(r"C:\Users\WA\Desktop\photo_size_test_mount")
# SIDES_IMAGE_DIR = MOUNT_DIR / "images_sides"
# SVI_IMAGE_DIR = MOUNT_DIR / "1024x2048_svi"


print(os.getcwd())
IMAGES_DIR = SIDES_IMAGE_DIR #CE_SNAPSHOTS_DIR #Path("images")
#ALL_IMAGES = [path for path in os.listdir(IMAGES_DIR) if re.search(".*\.png", path) and len(path.split("_")) == 6]
COUNTER_MAP_COUNT = {}
COUNTER_MAP_ADD = {}

def set_counter_mapping(city_index):
    n_of_cities = {city for city, _ in city_index}
    for city in n_of_cities:
        COUNTER_MAP_COUNT[str(int(city))] = max([index for city_id, index in city_index if city_id == city])
    
    #print(COUNTER_MAP_COUNT)
    n_of_cities = list(n_of_cities)
    n_of_cities.sort()

    
    # move 1 key right
    #COUNTER_MAP_ADD = {str(city): COUNTER_MAP_COUNT[str(int(city)-1)] for city in n_of_cities[1:] }
    for city in n_of_cities[1:]:
        COUNTER_MAP_ADD[str(city)] = COUNTER_MAP_COUNT[str(int(city)-1)]

    COUNTER_MAP_ADD["0"] = 0
    print(COUNTER_MAP_ADD)
    
    for city in n_of_cities[1:]:
        COUNTER_MAP_ADD[city] += COUNTER_MAP_ADD[str(int(city)-1)]
    
    print(n_of_cities)
    print(COUNTER_MAP_ADD)


# actualize photo index, so city_id gets obsolete, we previously keep it, so files don't get overwritten 
def get_new_index(current_index: str, n_city: str):
    return str(int(current_index) + int(COUNTER_MAP_ADD[n_city]))


def rename_photo(images_dir, path, photo_type="spheric"):
    path_split = path.split("_")
    new_path = path_split[1] + "_" + path_split[0] + "_" + path_split[3] + "_" \
            + path_split[4] + "_" + get_new_index(path_split[5][:-4], path_split[2]) + ".png"
    
    if photo_type == "spheric":
        new_path = path_split[1] + "_" + path_split[0] + "_" + path_split[3] + "_" \
            + path_split[4] + "_" + get_new_index(path_split[5][:-4], path_split[2]) + ".png"
    else:
        new_path = path_split[1] + "_" + path_split[0]  + "_" \
            + path_split[4] + "_" + get_new_index(path_split[5][:-4], path_split[2]) + ".png"

    #print("OLD:", IMAGES_DIR / path)
    #print("NEW:", IMAGES_DIR / new_path)

    try:
        os.rename(images_dir / path, images_dir / new_path)
        #print("Ok")
    except FileNotFoundError:
        #print("file not found")
        pass
    except FileExistsError:
        #print("file already exists")
        pass
    

def rename_all_new_spheric_photos():
    # "images\SynCity3D_m-Normal_snapshot_back_2.png" - we assume filenames have NOT been normalized
    # have to be initialized inside a function, so it updates os.listdir() after taking photos
    all_images = [path for path in os.listdir(SIDES_IMAGE_DIR) if len(path.split("_")) == 6]
    #print("OS RENAME:", os.getcwd())
    #print("IMAGES DIR:", IMAGES_DIR)
    #print(os.listdir(IMAGES_DIR))


    #print("ALL IMAGES rename:", len(all_images))
    if all_images:
        city_index = [(path.split('_')[2], int(path.split('_')[5][:-4]) ) for path in all_images]
        #print("CITY INDEX:", city_index) 

        set_counter_mapping(city_index)
    
        for file in all_images:
            rename_photo(SIDES_IMAGE_DIR, file)

    print("renamed all files in ../images")




def rename_all_new_svi_photos():
    # "images\SynCity3D_m-Normal_snapshot_back_2.png" - we assume filenames have NOT been normalized
    # have to be initialized inside a function, so it updates os.listdir() after taking photos
    all_images = [path for path in os.listdir(SVI_IMAGE_DIR) if (len(path.split("_")) == 6 and path.startswith("SynCity3D"))]
    #print("OS RENAME:", os.getcwd())
    #print("IMAGES DIR:", IMAGES_DIR)
    #print(os.listdir(IMAGES_DIR))


    #print("ALL IMAGES rename:", len(all_images))
    if all_images:
        city_index_svi = [(path.split('_')[2], int(path.split('_')[5][:-4]) ) for path in all_images]
        #print("CITY INDEX:", city_index) 

        set_counter_mapping(city_index_svi)
    
        for file in all_images:
            rename_photo(SVI_IMAGE_DIR, file, photo_type="svi")


    print("renamed all files in ../images")

if __name__ == "__main__":
    #rename_all_new_photos()
    pass
