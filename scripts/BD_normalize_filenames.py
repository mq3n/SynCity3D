import os
from pathlib import Path
import re

# f.e
#PATH: images\SynCity3D_m-1_<0>_snapshot_back_<2>.png
#OLD FILENAME: SynCity3D_m-1_1_snapshot_back_1.png
#NEW FILENAME: m-1_SynCity3D_snapshot_back_11.png

print(os.getcwd())
IMAGES_DIR =  Path("images")
#ALL_IMAGES = [path for path in os.listdir(IMAGES_DIR) if re.search(".*\.png", path) and len(path.split("_")) == 6]
COUNTER_MAP = {}

def set_counter_mapping(city_index):
    n_of_cities = {city for city, _ in city_index}
    for city in n_of_cities:
        COUNTER_MAP[str(int(city))] = max([index for _, index in city_index])
    
    #print(COUNTER_MAP)
    n_of_cities = list(n_of_cities)
    n_of_cities.sort()

    for city in n_of_cities:
        COUNTER_MAP[city] += COUNTER_MAP[str(int(city)-1)]
    
    COUNTER_MAP['0'] = 0

    print(n_of_cities)
    print(COUNTER_MAP)

# actualize photo index, so city_id gets obsolete, we previously keep it, so files don't get overwritten 
def get_new_index(current_index, n_city):
    return str(int(current_index) + int(COUNTER_MAP[n_city]))


def rename_photo(path):
    path_split = path.split("_")
    new_path = path_split[1] + "_" + path_split[0] + "_" + path_split[3] + "_" \
            + path_split[4] + "_" + get_new_index(path_split[5][:-4], path_split[2]) + ".png"
    
    #print("OLD:", IMAGES_DIR / path)
    #print("NEW:", IMAGES_DIR / new_path)

    try:
        os.rename(IMAGES_DIR / path, IMAGES_DIR / new_path)
        #print("Ok")
    except FileNotFoundError:
        #print("file not found")
        pass
    except FileExistsError:
        #print("file already exists")
        pass
    

def rename_all_new_photos():
    # "images\SynCity3D_m-Normal_snapshot_back_2.png" - we assume filenames have NOT been normalized
    # have to be initialized inside a function, so it updates os.listdir() after taking photos
    all_images = [path for path in os.listdir(IMAGES_DIR) if len(path.split("_")) == 6]
    #print("OS RENAME:", os.getcwd())
    #print("IMAGES DIR:", IMAGES_DIR)
    #print(os.listdir(IMAGES_DIR))


    #print("ALL IMAGES rename:", len(all_images))
    if all_images:
        city_index = [(path.split('_')[2], int(path.split('_')[5][:-4]) ) for path in all_images]
        set_counter_mapping(city_index)
    
        for file in all_images:
            rename_photo(file)

    print("renamed all files in ../images")


if __name__ == "__main__":
    #rename_all_new_photos()
    pass
