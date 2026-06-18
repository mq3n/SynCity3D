print('importing modules ')
from PIL import Image
import numpy as np
import py360convert
import PIL
import os
import matplotlib.pyplot as plt
import re
from pathlib import Path
from tqdm import tqdm

print('ok')

#IMAGES_DIR =  Path("./images").resolve()
#SPHERIC_PHOTO_DIR = Path("./dataset").resolve()


WORKSPACE_DIR = Path(r"C:\Users\WA\Desktop\badanie") # !! directory with our project and other projects (ESRI.lib)
BASE_DIR = WORKSPACE_DIR / "syncity3D" 
SCRIPTS_DIR = BASE_DIR / "scripts"

# stage 1 - snapshots back, right, front, left, top, bottom 
CE_SNAPSHOTS_DIR = BASE_DIR / "images"

# HERE - stage 2 - spheric 'photos' and their segmention/semantic color masks
SPHERIC_PHOTOS_DIR = BASE_DIR / "dataset_stages" / "spheric_photos_and_masks"


IMAGES_DIR = CE_SNAPSHOTS_DIR

SPACES = ["m-Normal", "m-1", "m-2"]
SIDES = ['back','right','front','left','top','bottom']


# just to check if we have every side of a photo we want to convert to 360
def check_sets_prefix(n, prefix="m-Normal"):
    sides_count = 0
    #filenames = []
    for side in SIDES:
        path = IMAGES_DIR / f"{prefix}_SynCity3D_snapshot_{side}_{n}.png"
        if os.path.exists(path):
            #filenames.append(path)
            sides_count += 1

    '''
    if m1 == 6:
        plt.figure(figsize=(15, 15))
        plt.subplot(2, 3, 1)
        plt.imshow(Image.open(filenames[0]))
        plt.title(filenames[0])
        plt.subplot(2, 3, 2)
        plt.imshow(Image.open(filenames[1]))
        plt.title(filenames[1])
        plt.subplot(2, 3, 3)
        plt.imshow(Image.open(filenames[2]))
        plt.title(filenames[2])
        plt.subplot(2, 3, 4)
        plt.imshow(Image.open(filenames[3]))
        plt.title(filenames[3])
        plt.subplot(2, 3, 5)
        plt.imshow(Image.open(filenames[4]))
        plt.title(filenames[4])
        plt.subplot(2, 3, 6)
        plt.imshow(Image.open(filenames[5]))
        plt.title(filenames[5])
        plt.show()
    '''

    if sides_count == 6:
        return True
    else:
        return False


def convertFromCE(index, prefix="m-Normal", tilt = 0):

    if check_sets_prefix(index, prefix):
        #print("Full set present")
        pass
    else:
        #print("Something is missing...")
        return

    #py360convert dict keys ['F', 'R', 'B', 'L', 'U', 'D'], yes, F and B are replaced
    faces2 = [ ('back', "F"), ('right', "R"), ('front', "B"), ('left', "L"),('top', "U"), ('bottom', "D")]
    
    cubmap_dict = {}

    for face, key in faces2:
        filepath = IMAGES_DIR / f"{prefix}_SynCity3D_snapshot_{face}_{index}.png"

        if not os.path.exists(filepath):
            return None
        
        img = Image.open(filepath)

        if face in ['top', 'bottom']:
            img = img.transpose(PIL.Image.ROTATE_180)
 
        cubmap_dict[key] = np.array(img)

    # Valid options: "nearest", "linear", "bilinear", "biquadratic", "quadratic", "quad", "bicubic", "cubic", "biquartic", "quartic", "biquintic", "quintic".
    #e = py360convert.c2e(image,3040,6080,cube_format='horizon')
    e = py360convert.c2e(cubmap_dict, 3040, 6080, cube_format='dict', mode="biquadratic")
    eqr = Image.fromarray(e.astype('uint8'))
    save_path = SPHERIC_PHOTOS_DIR / f"{prefix}_SynCity3D_{index}.png"
    #print("SAVE PATH:", save_path)
    try:
        eqr.save(save_path)
        print("saved:", save_path)

        

    except Exception:
        pass
    #eqr.save('./output/%s_%s_%s.png' % (prefix,index,tilt))
    try:
        for face, _ in faces2:
            filepath = IMAGES_DIR / f"{prefix}_SynCity3D_snapshot_{face}_{index}.png"
            filepath.unlink()

            #print("...and snaphots were removed for memory management")

    except Exception:
        pass

    return #eqr


# \dataset\SynCity3D_m-1_10.png
def clean_masks(spheric_photo_index):


    mask_1_path = SPHERIC_PHOTOS_DIR / f"m-1_SynCity3D_{spheric_photo_index}.png"
    mask_2_path = SPHERIC_PHOTOS_DIR / f"m-2_SynCity3D_{spheric_photo_index}.png"

    if not mask_1_path.exists() or not mask_2_path.exists():
        print("some issue occured, it doesn't matter either way")
        return


    mask_1_photo = Image.open(mask_1_path)
    mask_2_photo = Image.open(mask_2_path)

    mask_1_photo_channels = mask_1_photo.copy()
    _, _, m1_b = mask_1_photo_channels.split() 

    m1_b_array = np.array(m1_b)
    mask_filter = (m1_b_array > 0)

    mask_1_array = np.array(mask_1_photo)
    mask_2_array = np.array(mask_2_photo)

    mask_1_array[mask_filter] = 255
    mask_2_array[mask_filter] = 255

    mask_1_photo_f = Image.fromarray(mask_1_array)
    mask_2_photo_f = Image.fromarray(mask_2_array)

    mask_1_photo_f.save(mask_1_path)
    mask_2_photo_f.save(mask_2_path)

    return



def convert_every_available_file():
    # "images\SynCity3D_m-Normal_snapshot_back_2.png" - we assume filenames have been normalized (with continoues photo_id and split==5)
    # have to be initialized inside a function, so it updates os.listdir() after taking photos
    all_images = [path for path in os.listdir(IMAGES_DIR) if len(path.split("_")) == 5]
    #print("OS CONVERT:", os.getcwd())
    #print("IMAGES DIR:", IMAGES_DIR)

    #print("ALL IMAGES CONVERT:", all_images)
    if all_images:
        available_indexes = {int(path.split("_")[-1][:-4]) for path in all_images if re.search("SynCity3D", path)}
        min_id, max_id = min(available_indexes), max(available_indexes)
        for index in tqdm(range(min_id, max_id + 1)):
            
            if check_sets_prefix(index, "m-Normal") and check_sets_prefix(index, "m-1") and check_sets_prefix(index, "m-2"):
                convertFromCE(index, "m-Normal")
                convertFromCE(index, "m-1")
                convertFromCE(index, "m-2")


    print("Spheric Photos Created")


# separated because there were some issus if they were run immediately after creating
def clean_every_spheric_file():
    # "images\SynCity3D_m-Normal_snapshot_back_2.png" - we assume filenames have been normalized (with continoues photo_id)
    # it has to be initialized inside a function, so it updates os.listdir() after taking photos
    all_images = [path for path in os.listdir(IMAGES_DIR) if len(path.split("_")) == 5]

    #print("OS CLEAN:", os.getcwd())
    #print("IMAGES DIR:", IMAGES_DIR)

    #print("ALL IMAGES CLEAN:", all_IMAGES2)
    if all_images:
        available_indexes = {int(path.split("_")[-1][:-4]) for path in all_images if re.search("SynCity", path)}
        min_id, max_id = min(available_indexes), max(available_indexes)

        for index in range(min_id, max_id + 1):
            clean_masks(index)

    print("Cleaned")

if __name__ == "__main__": 
    #convert_every_available_file()
    pass