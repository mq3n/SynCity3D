from mmengine.config import Config
from mmdet.registry import RUNNERS


def a():
    #CFG_PATH = 'configs/facade_maskrcnn_test.py'
    #WORK_DIR = './work_dirs/facade_maskrcnn_test'
    CFG_PATH = 'configs/swin_transformer.py'
    WORK_DIR = './work_dirs/swin_transformer'

    cfg = Config.fromfile(CFG_PATH)
    cfg.work_dir = WORK_DIR

    runner = RUNNERS.build(cfg)
    runner.train()

if __name__ == '__main__':
    a() 