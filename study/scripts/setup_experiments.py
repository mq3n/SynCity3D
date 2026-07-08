import os
from pathlib import Path
import json
import yaml
import datetime
import torch
import gc

import logging
import warnings


from detectron2.config import get_cfg, LazyConfig, instantiate
from detectron2 import model_zoo
from detectron2.checkpoint import DetectionCheckpointer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.engine import DefaultTrainer, default_argument_parser, default_setup, hooks, launch, AMPTrainer, SimpleTrainer, default_writers
from detectron2.utils.logger import setup_logger
from detectron2.engine.defaults import create_ddp_model
from detectron2.data.datasets import register_coco_instances
from detectron2.evaluation import COCOEvaluator, inference_on_dataset, print_csv_format
from detectron2.utils import comm


# ensure this path exists
COCO_DATASET_DIR = Path("C:\\Users\\WA\\Desktop\\badanie\\syncity3D\\COCO_DATASETS\\D4")
IMAGES_DIR = COCO_DATASET_DIR / "images"
ANNOTATIONS_DIR = COCO_DATASET_DIR / "annotations"


DATASET_TRAIN_M1 = "D4_M1_train"
DATASET_TRAIN_M2 = "D4_M2_train"
DATASET_VAL_M1 = "D4_M1_val"
DATASET_VAL_M2 = "D4_M2_val"
DATASET_TEST_M1 = "D4_M1_test"
DATASET_TEST_M2 = "D4_M2_test"



RESULTS_DIR = Path("./study/results")


# ścieżka do lokalnego detectronu? -> sprawdz venv
DETECTRON_DIR = Path("C:\\Users\\WA\\Desktop\\badanie\\syncity3D\\study\\detectron2")

# we use these
MASK_RCNN_BACKBONES = ["COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml", 
                        "COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml"]


VIT_BACKBONES = ["COCO/mask_rcnn_vitdet_b_100ep.py",
                 "COCO/mask_rcnn_vitdet_l_100ep.py",
                 "COCO/mask_rcnn_vitdet_h_75ep.py"]


logger = logging.getLogger("detectron2")

# Suppress deprecation FutureWarning about torch.cuda.amp.autocast
# emitted from detectron2 / torch versions. This avoids modifying
# library files while keeping the output clean for users.
warnings.filterwarnings(
    "ignore",
    message=".*torch.cuda.amp.autocast.*deprecated.*",
    category=FutureWarning,
)
# Also ignore FutureWarning originating from detectron2's train_loop module
warnings.filterwarnings("ignore", category=FutureWarning, module=".*detectron2.*train_loop.*")

try:
    from tqdm import tqdm
except Exception:
    tqdm = None


# FOR MASK R-CNN ARCHITECTURE 
class FacadeTrainer(DefaultTrainer):
    """Trainer z ewaluatorem COCO dla naszych customowych nazw datasetów."""

    @classmethod
    def build_evaluator(cls, cfg, dataset_name, output_folder=None):  # type: ignore[override]
        if output_folder is None:
            output_folder = os.path.join(cfg.OUTPUT_DIR, "inference")
        return COCOEvaluator(dataset_name, cfg, False, output_folder)


class ProgressBarHook(hooks.HookBase):
    """Hook pokazujący pasek postępu treningu w terminalu."""

    def __init__(self, max_iter, enabled=True):
        self.max_iter = max_iter
        self.enabled = enabled
        self.pbar = None

    def before_train(self):
        if not self.enabled:
            return
        start = getattr(self.trainer, "iter", 0)
        if tqdm is not None:
            self.pbar = tqdm(total=self.max_iter, initial=start, desc="Train", unit="iter")
        else:
            print(f"Starting training at iter {start}/{self.max_iter}")

    def after_step(self):
        if not self.enabled:
            return
        if self.pbar:
            self.pbar.update(1)
        else:
            cur = getattr(self.trainer, "iter", 0)
            if cur % 100 == 0:
                print(f"Iter {cur}/{self.max_iter}")

    def after_train(self):
        if self.pbar:
            self.pbar.close()




def clean_gpu():

    gc.collect()
    torch.cuda.empty_cache()
    # Resetuje statystyki i upewnia się, że VRAM wraca do systemu
    torch.cuda.reset_peak_memory_stats()

    print("GPU Memory cleared successfully.\n" + "-" * 40)



def build_maskrcnn_facade_config(backbone, dataset_train, dataset_val, num_classes, output_dir):
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file(backbone))

    cfg.DATASETS.TRAIN = (dataset_train,)
    cfg.DATASETS.TEST = (dataset_val,)
    cfg.DATALOADER.NUM_WORKERS = 2
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(backbone)  # Let training initialize from model zoo
    cfg.SOLVER.IMS_PER_BATCH = 12
    cfg.SOLVER.BASE_LR = 0.00025
    cfg.SOLVER.MAX_ITER = 500    
    cfg.SOLVER.STEPS = []     # do not decay learning rate
    #cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 256   # The "RoIHead batch size". 128 is faster, and good enough for this toy dataset (default: 512)
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = num_classes  #. (see https://detectron2.readthedocs.io/tutorials/datasets.html#update-the-config-for-new-datasets)
    cfg.INPUT.MASK_FORMAT = "bitmask"
    cfg.SOLVER.LOG_PERIOD = 20

    cfg.OUTPUT_DIR = output_dir
    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

    return cfg

def build_vitdet_facade_cfg(backbone, dataset_train, dataset_val, n_classes, output_dir):
    """Załadowanie i lekkie dostosowanie configu ViTDet do fasad."""

    cfg = LazyConfig.load(backbone)

    # Podmiana nazw zbiorów na Twoje fasady
    cfg.dataloader.train.dataset.names = dataset_train
    cfg.dataloader.test.dataset.names = dataset_val
    cfg.dataloader.evaluator.dataset_name = dataset_val

    # Mniejszy batch i liczba workerów – żeby było lżej pamięciowo
    #cfg.dataloader.train.total_batch_size = 12 # odpowiednik SOLVER.IMS_PER_BATCH
    #cfg.dataloader.train.num_workers = 2       # odpowiednik DATALOADER.NUM_WORKERS
    cfg.dataloader.train.total_batch_size = 1 #???
    cfg.dataloader.train.num_workers = 0

    # Nasze maski w COCO są w formacie RLE/bitmask, a nie polygon
    # W lazy-configach trzeba ustawić to na mapperze, nie w cfg.INPUT
    if hasattr(cfg.dataloader.train, "mapper"):
        cfg.dataloader.train.mapper.instance_mask_format = "bitmask"
    if hasattr(cfg.dataloader.test, "mapper"):
        cfg.dataloader.test.mapper.instance_mask_format = "bitmask"

    # Katalog wyjściowy na wyniki ViTDet
    cfg.train.output_dir = output_dir #os.path.join(this_dir, "output_vitdet_facade")

    # Ustawienie poprawnej liczby klas dla modeli Transformerowych
    if hasattr(cfg, "model") and hasattr(cfg.model, "roi_heads"):
        cfg.model.roi_heads.num_classes = n_classes


    # 2. Parametry uczenia i logowania (Odpowiedniki SOLVER)
    cfg.train.max_iter = 500          # odpowiednik SOLVER.MAX_ITER
    cfg.train.log_period = 20         # odpowiednik SOLVER.LOG_PERIOD
    cfg.train.checkpointer.period = 1000 # rzadziej niż max_iter, żeby nie śmiecić dysku


    os.makedirs(cfg.train.output_dir, exist_ok=True)

    return cfg


def register_dataset(name, annotation_path, image_path):
    if name not in DatasetCatalog:
        register_coco_instances(name, {}, annotation_path, image_path)
    else:
        print(f"Dataset {name} is already registered is detectron library.")


def register_datasets():

    train_images_dir = IMAGES_DIR / "train"
    val_images_dir = IMAGES_DIR / "val"
    test_images_dir = IMAGES_DIR / "test"

    # M1
    train_ann_m1_dir = ANNOTATIONS_DIR / "instances_train_m1.json"
    val_ann_m1_dir = ANNOTATIONS_DIR / "instances_val_m1.json"
    test_ann_m1_dir = ANNOTATIONS_DIR / "instances_test_m1.json"

    # M2
    train_ann_m2_dir = ANNOTATIONS_DIR / "instances_train_m2.json"
    val_ann_m2_dir = ANNOTATIONS_DIR / "instances_val_m2.json"
    test_ann_m2_dir = ANNOTATIONS_DIR / "instances_test_m2.json"


    register_dataset(DATASET_TRAIN_M1, train_ann_m1_dir, train_images_dir)
    register_dataset(DATASET_VAL_M1, val_ann_m1_dir, val_images_dir)
    register_dataset(DATASET_TEST_M1, test_ann_m1_dir, test_images_dir)

    register_dataset(DATASET_TRAIN_M2, train_ann_m2_dir, train_images_dir)
    register_dataset(DATASET_VAL_M2, val_ann_m2_dir, val_images_dir)
    register_dataset(DATASET_TEST_M2, test_ann_m2_dir, test_images_dir)

    print("Datasets registered.")




'''
# Decided to explicitly start training
def create_configs():

    m1_cats = 10
    m2_cats = 11

    configs_mrcnn = []
    configs_vit = []

    for backbone in MASK_RCNN_BACKBONES:
        architecture = backbone.split("/")[-1][:-5]
        print("ARCHITECTURE:", architecture)
        output_dir_m1 = RESULTS_DIR / f"M1_D4_{architecture}"
        output_dir_m2 = RESULTS_DIR / f"M2_D4_{architecture}"

        #print(output_dir)

        cfg_m1 = build_maskrcnn_facade_config(backbone, DATASET_TRAIN_M1, DATASET_VAL_M1, m1_cats, str(output_dir_m1))
        cfg_m2 = build_maskrcnn_facade_config(backbone, DATASET_TRAIN_M2, DATASET_VAL_M2, m2_cats, str(output_dir_m2))
        configs_mrcnn.append(cfg_m1)
        configs_mrcnn.append(cfg_m2)


    for backbone in VIT_BACKBONES:
        architecture = backbone.split("/")[-1][:-3]
        print("ARCHITECTURE:", architecture)
        output_dir_m1 = RESULTS_DIR / f"M1_D4_{architecture}"
        output_dir_m2 = RESULTS_DIR / f"M2_D4_{architecture}"


        vitdet_cfg_path = os.path.join(DETECTRON_DIR, "projects", "ViTDet", "configs", backbone)
        #print(output_dir)

        cfg_m1 = build_vitdet_facade_cfg(vitdet_cfg_path, DATASET_TRAIN_M1, DATASET_VAL_M1, str(output_dir_m1))
        cfg_m2 = build_vitdet_facade_cfg(vitdet_cfg_path, DATASET_TRAIN_M2, DATASET_VAL_M2, str(output_dir_m2))
        configs_vit.append(cfg_m1)
        configs_vit.append(cfg_m2)

    return configs_mrcnn, configs_vit

'''



def train_rcnn(backbone, dataset_train, dataset_val, n_cats, output_dir, resume_training=False):

    cfg = build_maskrcnn_facade_config(backbone, dataset_train, dataset_val, n_cats, str(output_dir))
    print(f"Training {cfg.OUTPUT_DIR.split('/')[-1]} started.")

    #trainer = FacadeTrainer(cfg) 
    #trainer.resume_or_load(resume=resume_training)
    #trainer.train()

    print(f"Training {cfg.OUTPUT_DIR.split('/')[-1]} finished. Results saved in {cfg.OUTPUT_DIR}")
    clean_gpu()


def _do_test(cfg, model):
    if "evaluator" in cfg.dataloader:
        ret = inference_on_dataset(
            model,
            instantiate(cfg.dataloader.test),
            instantiate(cfg.dataloader.evaluator),
        )
        print_csv_format(ret)
        return ret


def do_train(resume: bool, cfg) -> None:
    """Minimalna wersja lazyconfig_train_net.do_train skopiowana lokalnie.

    Dzięki temu nie potrzebujemy modułu detectron2.tools,
    który nie występuje w wersji conda.
    """

    model = instantiate(cfg.model)
    logger.info("Model:\n{}".format(model))
    model.to(cfg.train.device)

    cfg.optimizer.params.model = model
    optim = instantiate(cfg.optimizer)

    train_loader = instantiate(cfg.dataloader.train)

    model = create_ddp_model(model, **cfg.train.ddp)
    trainer = (AMPTrainer if cfg.train.amp.enabled else SimpleTrainer)(
        model, train_loader, optim
    )
    checkpointer = DetectionCheckpointer(
        model,
        cfg.train.output_dir,
        trainer=trainer,
    )
    trainer.register_hooks(
        [
            hooks.IterationTimer(),
            ProgressBarHook(cfg.train.max_iter, enabled=comm.is_main_process()),
            hooks.LRScheduler(scheduler=instantiate(cfg.lr_multiplier)),
            (
                hooks.PeriodicCheckpointer(checkpointer, **cfg.train.checkpointer)
                if comm.is_main_process()
                else None
            ),
            hooks.EvalHook(cfg.train.eval_period, lambda: _do_test(cfg, model)),
            (
                hooks.PeriodicWriter(
                    default_writers(cfg.train.output_dir, cfg.train.max_iter),
                    period=cfg.train.log_period,
                )
                if comm.is_main_process()
                else None
            ),
        ]
    )

    checkpointer.resume_or_load(cfg.train.init_checkpoint, resume=resume)
    if resume and checkpointer.has_checkpoint():
        start_iter = trainer.iter + 1
    else:
        start_iter = 0
    trainer.train(start_iter, cfg.train.max_iter)




def train_vit(backbone, dataset_train, dataset_val, n_classes, output_dir, resume_training=False):
    cfg = build_vitdet_facade_cfg(backbone, dataset_train, dataset_val, n_classes, output_dir)
    print(f"Training started.")

    #do_train(resume_training, cfg)

    print(f"Training finished. Results saved in {cfg.train.output_dir}")
    clean_gpu()



# explicit training configs
def train_rcnn_backbones():

    print("="*20)
    print("Training Mask RCNN architectures started")
    print("="*20)

    m1_cats = 10
    m2_cats = 11

    # 1st Mask RCNN - mask_rcnn_R_50_FPN_3x
    train_rcnn("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml",
                DATASET_TRAIN_M1, 
                DATASET_VAL_M1, 
                m1_cats, 
                str(RESULTS_DIR / "M1_D4_mask_rcnn_R_50_FPN_3x"))
    
    train_rcnn("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml",
                DATASET_TRAIN_M2, 
                DATASET_VAL_M2, 
                m2_cats, 
                str(RESULTS_DIR / "M2_D4_mask_rcnn_R_50_FPN_3x"))
    
    # 2nd Mask RCNN - mask_rcnn_R_101_FPN_3x
    train_rcnn("COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml",
                DATASET_TRAIN_M1, 
                DATASET_VAL_M1, 
                m1_cats, 
                str(RESULTS_DIR / "M1_D4_mask_rcnn_R_101_FPN_3x"))
    
    train_rcnn("COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml",
                DATASET_TRAIN_M2, 
                DATASET_VAL_M2, 
                m2_cats, 
                str(RESULTS_DIR / "M2_D4_mask_rcnn_R_101_FPN_3x"))
    

    print("="*20)
    print("Training Mask RCNN architectures finished")
    print("="*20)



def train_vit_backbones():
    m1_classes = 10
    m2_classes = 11

    print("="*20)
    print("Training ViTDet architectures started")
    print("="*20)

    # 1nd ViT - mask_rcnn_vitdet_b_100ep
    print("BACKBONE: mask_rcnn_vitdet_b_100ep\n")

    train_vit(str(DETECTRON_DIR / "projects" / "ViTDet" / "configs" / "COCO/mask_rcnn_vitdet_b_100ep.py"),
              DATASET_TRAIN_M1,
              DATASET_VAL_M1,
              m1_classes,
              str(RESULTS_DIR / f"M1_D4_mask_rcnn_vitdet_b_100ep"))


    train_vit(str(DETECTRON_DIR / "projects" / "ViTDet" / "configs" / "COCO/mask_rcnn_vitdet_b_100ep.py"),
              DATASET_TRAIN_M2,
              DATASET_VAL_M2,
              m2_classes,
              str(RESULTS_DIR / f"M2_D4_mask_rcnn_vitdet_b_100ep"))

    # 2nd ViT - mask_rcnn_vitdet_l_100ep
    print("BACKBONE: mask_rcnn_vitdet_l_100ep\n")

    train_vit(str(DETECTRON_DIR / "projects" / "ViTDet" / "configs" / "COCO/mask_rcnn_vitdet_l_100ep.py"),
              DATASET_TRAIN_M1,
              DATASET_VAL_M1,
              m1_classes,
              str(RESULTS_DIR / f"M1_D4_mask_rcnn_vitdet_l_100ep"))


    train_vit(str(DETECTRON_DIR / "projects" / "ViTDet" / "configs" / "COCO/mask_rcnn_vitdet_l_100ep.py"),
              DATASET_TRAIN_M2,
              DATASET_VAL_M2,
              m2_classes,
              str(RESULTS_DIR / f"M2_D4_mask_rcnn_vitdet_l_100ep"))


    # 3rd ViT - mask_rcnn_vitdet_h_75ep
    print("BACKBONE: mask_rcnn_vitdet_h_75ep\n")

    train_vit(str(DETECTRON_DIR / "projects" / "ViTDet" / "configs" / "COCO/mask_rcnn_vitdet_h_75ep.py"),
              DATASET_TRAIN_M1,
              DATASET_VAL_M1,
              m1_classes,
              str(RESULTS_DIR / f"M1_D4_mask_rcnn_vitdet_h_75ep"))


    train_vit(str(DETECTRON_DIR / "projects" / "ViTDet" / "configs" / "COCO/mask_rcnn_vitdet_h_75ep.py"),
              DATASET_TRAIN_M2,
              DATASET_VAL_M2,
              m2_classes,
              str(RESULTS_DIR / f"M2_D4_mask_rcnn_vitdet_h_75ep"))


    print("="*20)
    print("Training ViTDet architectures finished")
    print("="*20)

    


if __name__ == "__main__":
    print("START", "="*10)
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA version: {torch.version.cuda}")

    register_datasets()


    train_rcnn_backbones()
    train_vit_backbones()


    print("DONE", "="*10)
