_base_ = [
    '../../_base_/models/vitclip_base.py', '../../_base_/default_runtime.py'
]

# model settings
model = dict(
    backbone=dict(type='ViT_CLIP_ZEROI2V',drop_path_rate=0.2, adapter_scale=0.5, num_frames=32,with_t_cls_token=True,linear_adapter=False,bottleneck=128,share_adapter=False),
    cls_head=dict(num_classes=51,label_smooth_eps=0.02),
)

# dataset settings
dataset_type = 'VideoDataset'
data_root = 'data/hmdb51/videos'
data_root_val = 'data/hmdb51/videos'
ann_file_train = 'data/hmdb51/hmdb51_train_split_1_videos.txt'
ann_file_val = 'data/hmdb51/hmdb51_val_split_1_videos.txt'
ann_file_test = 'data/hmdb51/hmdb51_val_split_1_videos.txt'

# dataset_type = 'RawframeDataset'
# data_root = 'data/hmdb51/rawframes'
# data_root_val = 'data/hmdb51/rawframes'
# ann_file_train = 'data/hmdb51/hmdb51_train_split_1_rawframes.txt'
# ann_file_val = 'data/hmdb51/hmdb51_val_split_1_rawframes.txt'
# ann_file_test = 'data/hmdb51/hmdb51_val_split_1_rawframes.txt'

total_epochs = 30
num_frames=32

# work_dir = './work_dirs/vitclip_zeroI2V_base_hmdb51'

file_client_args = dict(io_backend='disk')
train_pipeline = [
    dict(type='DecordInit'),
    dict(type='UniformSample', clip_len=num_frames, num_clips=1),
    dict(type='DecordDecode'),
    # dict(type='RawFrameDecode', **file_client_args),
    dict(type='Resize', scale=(-1, 256)),
    dict(type='RandomResizedCrop'),
    dict(type='Resize', scale=(224, 224), keep_ratio=False),
    dict(type='Flip', flip_ratio=0.5),
    # dict(
    #     type='PytorchVideoWrapper',
    #     op='RandAugment',
    #     magnitude=7,
    #     num_layers=4),
    # dict(type='RandomErasing', erase_prob=0.25, mode='rand'),
    dict(type='FormatShape', input_format='NCTHW'),
    dict(type='PackActionInputs')
]

val_pipeline = [
    dict(type='DecordInit'),
    dict(type='UniformSample', clip_len=num_frames, num_clips=1,test_mode=True),
    dict(type='DecordDecode'),
    # dict(type='RawFrameDecode', **file_client_args),
    dict(type='Resize', scale=(-1, 256)),
    dict(type='CenterCrop', crop_size=224),
    dict(type='Flip', flip_ratio=0),
    dict(type='FormatShape', input_format='NCTHW'),
    dict(type='PackActionInputs')
]

test_pipeline = [
    dict(type='DecordInit'),
    dict(type='UniformSample', clip_len=num_frames, num_clips=4,test_mode=True),
    dict(type='DecordDecode'),
    # dict(type='RawFrameDecode', **file_client_args),
    dict(type='Resize', scale=(-1, 224)),
    dict(type='ThreeCrop', crop_size=224),
    dict(type='Flip', flip_ratio=0),
    dict(type='FormatShape', input_format='NCTHW'),
    dict(type='PackActionInputs')
]

batch_size=8
train_dataloader = dict(
    batch_size=batch_size,
    num_workers=8,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=True),
    dataset=dict(
        type=dataset_type,
        ann_file=ann_file_train,
        data_prefix=dict(video=data_root),
        # data_prefix=dict(img=data_root),
        pipeline=train_pipeline))
val_dataloader = dict(
    batch_size=batch_size,
    num_workers=8,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type=dataset_type,
        ann_file=ann_file_val,
        data_prefix=dict(video=data_root_val),
        # data_prefix=dict(img=data_root_val),
        pipeline=val_pipeline,
        test_mode=True))
test_dataloader = dict(
    batch_size=1,
    num_workers=1,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type=dataset_type,
        ann_file=ann_file_test,
        data_prefix=dict(video=data_root_val),
        # data_prefix=dict(img=data_root_val),
        pipeline=test_pipeline,
        test_mode=True))

val_evaluator = dict(type='AccMetric')
test_evaluator = val_evaluator

train_cfg = dict(
    type='EpochBasedTrainLoop', max_epochs=total_epochs, val_begin=2, val_interval=1)
val_cfg = dict(type='ValLoop')
test_cfg = dict(type='TestLoop')

# optimizer
optim_wrapper = dict(
    type='AmpOptimWrapper',
    optimizer=dict(
        type='AdamW', lr=3e-4, betas=(0.9, 0.999), weight_decay=0.05),
    paramwise_cfg=dict(
        class_embedding=dict(decay_mult=0.),
        positional_embedding=dict(decay_mult=0.),
        ln_1=dict(decay_mult=0.),
        ln_2=dict(decay_mult=0.),
        ln_pre=dict(decay_mult=0.),
        ln_post=dict(decay_mult=0.),
        ),
    
    )

# learning policy
param_scheduler = [
    dict(
        type='LinearLR',
        start_factor=0.1,
        by_epoch=True,
        begin=0,
        end=2.5,
        convert_to_iter_based=True),
    dict(
        type='CosineAnnealingLR',
        T_max=total_epochs,
        eta_min=0,
        by_epoch=True,
        begin=0,
        end=total_epochs)
]

# runtime settings
default_hooks = dict(
    checkpoint=dict(interval=5, max_keep_ckpts=1,save_best='auto'), 
    logger=dict(interval=100)
    )

custom_hooks = [dict(type='EarlyStoppingHook',
                    monitor='acc/top1',
                    rule='greater',
                    min_delta=0.001,
                    patience=8)]

project='vitclip_hmdb51_amp'
name='zeroI2V_tcls_noaug'

work_dir = f'./work_dirs/hmdb51/{project}/{name}'

visualizer = dict(
    type='ActionVisualizer',
    vis_backends=[
        dict(type='LocalVisBackend'),
        # dict(type='TensorboardVisBackend', save_dir=f'{work_dir}/tensorboard'),
        # dict(type='WandbVisBackend',init_kwargs=dict(project=project, name=name)),
    ],
)

auto_scale_lr = dict(enable=True, base_batch_size=64)

# activation_checkpointing=['backbone.transformer.resblocks.0', 'backbone.transformer.resblocks.1', 'backbone.transformer.resblocks.2',  'backbone.transformer.resblocks.3',
#                           'backbone.transformer.resblocks.4', 'backbone.transformer.resblocks.5', 'backbone.transformer.resblocks.6',  'backbone.transformer.resblocks.7',
#                           'backbone.transformer.resblocks.8', 'backbone.transformer.resblocks.9', 'backbone.transformer.resblocks.10', 'backbone.transformer.resblocks.11',]

