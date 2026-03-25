import os
import re
import json
import shutil
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image
from skimage.measure import label, regionprops
from pycocotools import mask as mask_utils
from tqdm import tqdm
from skimage.segmentation import expand_labels



@dataclass(frozen=True)
class ClassDef:
    name: str
    category_id: int


CLASSES = [
    ClassDef("poprawny", 1),  # fasada
]


def key_from_filename(fname: str, prefix: str) -> str:
    """
    Extract key from 'x_<id>_<angle>.<ext>' or 'y_<id>_<angle>.<ext>' -> '<id>_<angle>'
    """
    base = os.path.basename(fname)
    if not base.startswith(prefix):
        raise ValueError(f"File {base} does not start with {prefix}")
    stem = os.path.splitext(base)[0]
    return stem[len(prefix):]


def find_pairs(raw_dir: str) -> List[Tuple[str, str, str]]:
    """
    Returns list of (key, img_path, mask_path)
    """
    imgs = []
    masks = []
    for f in os.listdir(raw_dir):
        if f.startswith("x_"):
            imgs.append(f)
        elif f.startswith("y_"):
            masks.append(f)

    img_map = {key_from_filename(f, "x_"): os.path.join(raw_dir, f) for f in imgs}
    mask_map = {key_from_filename(f, "y_"): os.path.join(raw_dir, f) for f in masks}

    keys = sorted(set(img_map.keys()) & set(mask_map.keys()))
    if not keys:
        raise RuntimeError("No matching x_<id>_<angle> and y_<id>_<angle> pairs found.")

    pairs = [(k, img_map[k], mask_map[k]) for k in keys]
    return pairs


def rgb_masks_from_mask_image(mask_rgb: np.ndarray, thr: int = 200) -> Dict[str, np.ndarray]:
    """
    Class separation from RGB mask using dominant channel rule.
    - poprawny: green-dominant pixels
    - niepoprawny: blue-dominant pixels
    thr limits near-white/gray pixels that otherwise contaminate masks.
    """
    if mask_rgb.ndim == 2:
        mask_rgb = np.repeat(mask_rgb[:, :, None], 3, axis=2)

    R = mask_rgb[:, :, 0].astype(np.int16)
    G = mask_rgb[:, :, 1].astype(np.int16)
    B = mask_rgb[:, :, 2].astype(np.int16)

    poprawny = (G >= thr) & (G > R) & (G > B)
    niepoprawny = (B >= thr) & (B > R) & (B > G)

    return {"poprawny": poprawny, "niepoprawny": niepoprawny}



def instances_from_binary_mask(bin_mask: np.ndarray, min_area: int = 1) -> List[np.ndarray]:
    """
    Split a binary mask into instance masks using connected components.
    Returns list of HxW boolean masks.
    """
    lab = label(bin_mask.astype(np.uint8), connectivity=2)
    inst = []
    for r in regionprops(lab):
        if r.area < min_area:
            continue
        m = (lab == r.label)
        inst.append(m)
    return inst

def instances_from_channel_values(mask_rgb: np.ndarray, channel: int, thr: int = 1, min_area: int = 1):
    """
    Extract instance masks using unique channel values.
    Assumption: each instance is encoded with a unique intensity in a single channel.
    channel: 1 for green, 2 for blue
    """
    if mask_rgb.ndim == 2:
        mask_rgb = np.repeat(mask_rgb[:, :, None], 3, axis=2)

    ch = mask_rgb[:, :, channel].astype(np.uint8)

    vals = np.unique(ch)
    vals = vals[vals > thr]  # ignore background (0) and tiny noise

    inst = []
    for v in vals:
        m = (ch == v)
        if m.sum() < min_area:
            continue
        inst.append(m)
    return inst

def keep_only_pure_green(mask_rgb: np.ndarray) -> np.ndarray:
    """
    Keep only pixels that are exactly pure green of the form [0, G, 0] with G>0.
    Everything else is set to background [0,0,0].

    This removes obstacles [0,0,128], any anti-aliased edges, and any non-canonical colors.
    """
    if mask_rgb.ndim == 2:
        mask_rgb = np.repeat(mask_rgb[:, :, None], 3, axis=2)

    M = mask_rgb.astype(np.uint8)
    R = M[:, :, 0]
    G = M[:, :, 1]
    B = M[:, :, 2]

    pure_green = (R == 0) & (B == 0) & (G > 0)

    out = np.zeros_like(M)
    out[pure_green, 1] = G[pure_green]  # keep original G id
    return out


def facade_instances_from_green_ids(mask_rgb_clean: np.ndarray, min_area: int = 1):
    """
    Extract facade instances assuming:
      - facades are encoded as [0, G, 0] (pure green)
      - instance id = unique G value
    """
    M = mask_rgb_clean.astype(np.uint8)
    G = M[:, :, 1]
    # only values that actually appear (excluding 0 background)
    ids = np.unique(G)
    ids = ids[ids > 0]

    inst = []
    for v in ids:
        m = (G == v)
        if int(m.sum()) >= min_area:
            inst.append(m)
    return inst

def coco_rle_from_mask(mask: np.ndarray) -> Dict:
    """
    Use pycocotools to produce COCO RLE.
    mask must be Fortran-contiguous (column-major) for correct encoding.
    """
    m = np.asfortranarray(mask.astype(np.uint8))
    rle = mask_utils.encode(m)
    # pycocotools returns counts as bytes; convert to utf-8 string for JSON
    rle["counts"] = rle["counts"].decode("utf-8")
    return rle

def canonicalize_facades(mask_rgb: np.ndarray, tol: int = 20, thr_soft: int = 30, max_expand: int = 5) -> np.ndarray:
    """
    Produces a clean mask where facades are encoded as [0,G,0] with stable instance ids.
    - Seeds: exact pixels [0,G,0] (R==0,B==0,G>0)
    - Soft facade pixels: green-dominant near-pure pixels (handles anti-aliasing)
    - Expansion assigns soft pixels to nearest seed (instance), up to max_expand pixels.
    """
    M = mask_rgb.astype(np.uint8)
    R, G, B = M[:, :, 0], M[:, :, 1], M[:, :, 2]

    # 1) exact seeds for each instance id
    seed = (R == 0) & (B == 0) & (G > 0)
    label_img = np.zeros(G.shape, dtype=np.int32)

    # label by G value (instance id)
    # Note: assumes G values are manageable; if many, this is still OK for your sizes
    ids = np.unique(G[seed])
    for idx, v in enumerate(ids, start=1):
        label_img[seed & (G == v)] = idx

    # 2) soft facade pixels around edges (tolerant rule)
    soft = (G >= thr_soft) & (G > R) & (G > B) & (R <= tol) & (B <= tol)

    # 3) expand labels to cover soft pixels
    # expand_labels grows labels outward; we then keep labels only where soft is True
    expanded = expand_labels(label_img, distance=max_expand)
    expanded[~soft] = 0

    # 4) rebuild canonical RGB mask: [0, G_id, 0]
    out = np.zeros_like(M)
    # map back: label index -> original G value
    # build lookup array
    id_lookup = np.zeros((len(ids) + 1,), dtype=np.uint8)
    for idx, v in enumerate(ids, start=1):
        id_lookup[idx] = v

    out[:, :, 1] = id_lookup[expanded]
    return out

def bbox_from_mask(mask: np.ndarray) -> List[float]:
    ys, xs = np.where(mask)
    x0, x1 = xs.min(), xs.max()
    y0, y1 = ys.min(), ys.max()
    return [float(x0), float(y0), float(x1 - x0 + 1), float(y1 - y0 + 1)]


def export_split_to_coco(
    pairs: List[Tuple[str, str, str]],
    out_images_dir: str,
    out_json_path: str,
    copy_images: bool = False,
    thr: int = 200,
    min_area: int = 100,
):
    os.makedirs(out_images_dir, exist_ok=True)
    os.makedirs(os.path.dirname(out_json_path), exist_ok=True)

    images = []
    annotations = []
    categories = [{"id": c.category_id, "name": c.name, "supercategory": "object"} for c in CLASSES]

    ann_id = 1
    for img_id, (key, img_path, mask_path) in enumerate(tqdm(pairs, desc=f"Exporting {os.path.basename(out_json_path)}"), start=1):
        # Link/copy image
        img_name = os.path.basename(img_path)
        out_img_path = os.path.join(out_images_dir, img_name)

        if not os.path.exists(out_img_path):
            if copy_images:
                shutil.copy2(img_path, out_img_path)
            else:
                # symlink if supported; fallback to copy
                try:
                    os.symlink(os.path.abspath(img_path), out_img_path)
                except OSError:
                    shutil.copy2(img_path, out_img_path)

        with Image.open(img_path) as im:
            w, h = im.size

        images.append({"id": img_id, "file_name": img_name, "width": w, "height": h})

        mask_rgb = np.array(Image.open(mask_path).convert("RGB"))
        
        # 1) keep ONLY pure green pixels [0,G,0] — hard filter (wymaganie c)
        mask_clean = keep_only_pure_green(mask_rgb)
        
        # 2) binary mask: any green pixel = facade
        facade_binary = (mask_clean[:, :, 1] > 0)
        
        # 3) connected components → handles duplicate colors (wymaganie b)
        #    min_area filters small instances (wymaganie a)
        inst_masks = instances_from_binary_mask(facade_binary, min_area=min_area)
        
        # 4) write annotations: only category_id=1 ("poprawny"/facade)
        for m in inst_masks:
            rle = coco_rle_from_mask(m)
            area = float(mask_utils.area(rle))
            bbox = mask_utils.toBbox(rle).tolist()
        
            annotations.append({
                "id": ann_id,
                "image_id": img_id,
                "category_id": 1,     # fasada / poprawny
                "segmentation": rle,
                "area": area,
                "bbox": bbox,
                "iscrowd": 0,
            })
            ann_id += 1

    coco = {"images": images, "annotations": annotations, "categories": categories}
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(coco, f, ensure_ascii=False)

    return coco


def make_splits(pairs: List[Tuple[str, str, str]], seed: int = 0, train=0.8, val=0.1):
    rng = np.random.default_rng(seed)
    idx = np.arange(len(pairs))
    rng.shuffle(idx)

    n = len(pairs)
    n_train = int(round(train * n))
    n_val = int(round(val * n))
    n_test = n - n_train - n_val

    train_pairs = [pairs[i] for i in idx[:n_train]]
    val_pairs = [pairs[i] for i in idx[n_train:n_train+n_val]]
    test_pairs = [pairs[i] for i in idx[n_train+n_val:]]

    return train_pairs, val_pairs, test_pairs


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    RAW_DIR = os.path.join(BASE_DIR, "..", "jupyter", "data_raw")
    OUT_DIR = os.path.join(BASE_DIR, "..", "jupyter", "data_coco")
    
    RAW_DIR = os.path.abspath(RAW_DIR)
    OUT_DIR = os.path.abspath(OUT_DIR)

    pairs = find_pairs(RAW_DIR)

    train_pairs, val_pairs, test_pairs = make_splits(pairs, seed=0, train=0.8, val=0.1)

    export_split_to_coco(
        train_pairs,
        out_images_dir=os.path.join(OUT_DIR, "images", "train"),
        out_json_path=os.path.join(OUT_DIR, "annotations", "instances_train.json"),
        copy_images=False,
        thr=128,
        min_area=300,  # filter small instances (min 100 pixels)
    )
    export_split_to_coco(
        val_pairs,
        out_images_dir=os.path.join(OUT_DIR, "images", "val"),
        out_json_path=os.path.join(OUT_DIR, "annotations", "instances_val.json"),
        copy_images=False,
        thr=128,
        min_area=300,  # filter small instances
    )
    export_split_to_coco(
        test_pairs,
        out_images_dir=os.path.join(OUT_DIR, "images", "test"),
        out_json_path=os.path.join(OUT_DIR, "annotations", "instances_test.json"),
        copy_images=False,
        thr=128,
        min_area=300,  # filter small instances
    )

    # Zapis splitu dla reprodukowalności
    split_path = os.path.join(OUT_DIR, "split_keys.json")
    with open(split_path, "w", encoding="utf-8") as f:
        json.dump({
            "train": [k for (k, _, _) in train_pairs],
            "val": [k for (k, _, _) in val_pairs],
            "test": [k for (k, _, _) in test_pairs],
        }, f, ensure_ascii=False, indent=2)

    print("Done.")
