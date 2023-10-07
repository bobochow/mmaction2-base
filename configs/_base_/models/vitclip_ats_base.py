# model settings
model = dict(
    type='Recognizer3D',
    backbone=dict(
        type='ViT_CLIP_ATS',
        pretrained='openaiclip',
        input_resolution=224,
        patch_size=16,
        num_frames=32,
        width=768,
        layers=12,
        heads=12,
        drop_path_rate=0.1),
    data_preprocessor=dict(
        type='ActionDataPreprocessor',
        mean=[122.769, 116.74, 104.04],
        std=[68.493, 66.63, 70.321],
        format_shape='NCTHW'),
    cls_head=dict(
        type='I3DHead',
        in_channels=768,
        num_classes=400,
        spatial_type='avg',
        dropout_ratio=0.5,
        average_clips='prob',
        ),
    )