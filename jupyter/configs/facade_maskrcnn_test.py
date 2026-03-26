_base_ = 'mmdet::mask_rcnn/mask-rcnn_r50_fpn_1x_coco.py'

data_root = 'data_coco/'
data_root = r'C:\Users\VR.VR_ASUS\Documents\SynCity3D\jupyter\data_coco\\'

metainfo = {
    'classes': ('poprawny',),
}

#env_cfg['mp_cfg']['mp_start_method']='spawn'
#mp_cfg=dict(mp_start_method='spawn')

train_dataloader = dict(
    batch_size=4,
    num_workers=4,
    persistent_workers=False,
    pin_memory=True,
    dataset=dict(
        type='CocoDataset',
        metainfo=metainfo,
        data_root=data_root,
        ann_file='annotations/instances_train.json',
        data_prefix=dict(img='images/train/'),
    )
)

val_dataloader = dict(
    batch_size=2,
    num_workers=4,
    pin_memory=True,
    persistent_workers=False,
    dataset=dict(
        type='CocoDataset',
        metainfo=metainfo,
        data_root=data_root,
        ann_file='annotations/instances_val.json',
        data_prefix=dict(img='images/val/'),
    )
)

test_dataloader = dict(
    batch_size=2,
    num_workers=4,
    pin_memory=True,
    persistent_workers=False,
    dataset=dict(
        type='CocoDataset',
        metainfo=metainfo,
        data_root=data_root,
        ann_file='annotations/instances_test.json',
        data_prefix=dict(img='images/test/'),
    )
)

val_evaluator = dict(
    ann_file=data_root + 'annotations/instances_val.json',
    metric=['bbox', 'segm'],
)

test_evaluator = dict(
    ann_file=data_root + 'annotations/instances_test.json',
    metric=['bbox', 'segm'],
)

model = dict(
    roi_head=dict(
        bbox_head=dict(num_classes=1),
        mask_head=dict(num_classes=1),
    )
)

# krótki trening tylko na test działania
train_cfg = dict(max_epochs=50, val_interval=1)

default_hooks = dict(
    checkpoint=dict(interval=1, max_keep_ckpts=1, save_best='auto')
)

# trochę lżejszy resize na start
train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations', with_bbox=True, with_mask=True),
    dict(type='Resize', scale=(1333, 800), keep_ratio=True),
    dict(type='RandomFlip', prob=0.5),
    dict(type='PackDetInputs')
]

test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='Resize', scale=(1333, 800), keep_ratio=True),
    dict(type='LoadAnnotations', with_bbox=True, with_mask=True),
    dict(type='PackDetInputs')
]

train_dataloader['dataset']['pipeline'] = train_pipeline
val_dataloader['dataset']['pipeline'] = test_pipeline
test_dataloader['dataset']['pipeline'] = test_pipeline