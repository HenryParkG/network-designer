PREDEFINED_MODELS={
    # LeNet-5 (MNIST)
    "LeNet-5": [
        {"type": "Conv2d", "params": {"in_channels": 1, "out_channels": 6, "kernel_size": 5}},
        {"type": "ReLU", "params": {}},
        {"type": "AvgPool2d", "params": {"kernel_size": 2, "stride": 2}},
        {"type": "Conv2d", "params": {"in_channels": 6, "out_channels": 16, "kernel_size": 5}},
        {"type": "ReLU", "params": {}},
        {"type": "AvgPool2d", "params": {"kernel_size": 2, "stride": 2}},
        {"type": "Flatten", "params": {}},
        {"type": "Linear", "params": {"in_features": 16*4*4, "out_features": 120}},
        {"type": "ReLU", "params": {}},
        {"type": "Linear", "params": {"in_features": 120, "out_features": 84}},
        {"type": "ReLU", "params": {}},
        {"type": "Linear", "params": {"in_features": 84, "out_features": 10}}
    ],

    # AlexNet (ImageNet) - full sequential version
    "AlexNet": [
        {"type": "Conv2d", "params": {"in_channels": 3, "out_channels": 96, "kernel_size": 11, "stride": 4, "padding": 0}},
        {"type": "ReLU", "params": {}},
        {"type": "MaxPool2d", "params": {"kernel_size": 3, "stride": 2}},

        {"type": "Conv2d", "params": {"in_channels": 96, "out_channels": 256, "kernel_size": 5, "stride": 1, "padding": 2}},
        {"type": "ReLU", "params": {}},
        {"type": "MaxPool2d", "params": {"kernel_size": 3, "stride": 2}},

        {"type": "Conv2d", "params": {"in_channels": 256, "out_channels": 384, "kernel_size": 3, "stride": 1, "padding": 1}},
        {"type": "ReLU", "params": {}},
        {"type": "Conv2d", "params": {"in_channels": 384, "out_channels": 384, "kernel_size": 3, "stride": 1, "padding": 1}},
        {"type": "ReLU", "params": {}},
        {"type": "Conv2d", "params": {"in_channels": 384, "out_channels": 256, "kernel_size": 3, "stride": 1, "padding": 1}},
        {"type": "ReLU", "params": {}},
        {"type": "MaxPool2d", "params": {"kernel_size": 3, "stride": 2}},

        {"type": "Flatten", "params": {}},
        {"type": "Linear", "params": {"in_features": 256*6*6, "out_features": 4096}},
        {"type": "ReLU", "params": {}},
        {"type": "Dropout", "params": {"p": 0.5}},
        {"type": "Linear", "params": {"in_features": 4096, "out_features": 4096}},
        {"type": "ReLU", "params": {}},
        {"type": "Dropout", "params": {"p": 0.5}},
        {"type": "Linear", "params": {"in_features": 4096, "out_features": 1000}}
    ],

    # VGG16 (ImageNet) - full
    "VGG16": [
        {"type": "Conv2d", "params": {"in_channels": 3, "out_channels": 64, "kernel_size": 3, "padding": 1}},
        {"type": "ReLU", "params": {}},
        {"type": "Conv2d", "params": {"in_channels": 64, "out_channels": 64, "kernel_size": 3, "padding": 1}},
        {"type": "ReLU", "params": {}},
        {"type": "MaxPool2d", "params": {"kernel_size": 2, "stride": 2}},

        {"type": "Conv2d", "params": {"in_channels": 64, "out_channels": 128, "kernel_size": 3, "padding": 1}},
        {"type": "ReLU", "params": {}},
        {"type": "Conv2d", "params": {"in_channels": 128, "out_channels": 128, "kernel_size": 3, "padding": 1}},
        {"type": "ReLU", "params": {}},
        {"type": "MaxPool2d", "params": {"kernel_size": 2, "stride": 2}},

        {"type": "Conv2d", "params": {"in_channels": 128, "out_channels": 256, "kernel_size": 3, "padding": 1}},
        {"type": "ReLU", "params": {}},
        {"type": "Conv2d", "params": {"in_channels": 256, "out_channels": 256, "kernel_size": 3, "padding": 1}},
        {"type": "ReLU", "params": {}},
        {"type": "Conv2d", "params": {"in_channels": 256, "out_channels": 256, "kernel_size": 3, "padding": 1}},
        {"type": "ReLU", "params": {}},
        {"type": "MaxPool2d", "params": {"kernel_size": 2, "stride": 2}},

        {"type": "Conv2d", "params": {"in_channels": 256, "out_channels": 512, "kernel_size": 3, "padding": 1}},
        {"type": "ReLU", "params": {}},
        {"type": "Conv2d", "params": {"in_channels": 512, "out_channels": 512, "kernel_size": 3, "padding": 1}},
        {"type": "ReLU", "params": {}},
        {"type": "Conv2d", "params": {"in_channels": 512, "out_channels": 512, "kernel_size": 3, "padding": 1}},
        {"type": "ReLU", "params": {}},
        {"type": "MaxPool2d", "params": {"kernel_size": 2, "stride": 2}},

        {"type": "Conv2d", "params": {"in_channels": 512, "out_channels": 512, "kernel_size": 3, "padding": 1}},
        {"type": "ReLU", "params": {}},
        {"type": "Conv2d", "params": {"in_channels": 512, "out_channels": 512, "kernel_size": 3, "padding": 1}},
        {"type": "ReLU", "params": {}},
        {"type": "Conv2d", "params": {"in_channels": 512, "out_channels": 512, "kernel_size": 3, "padding": 1}},
        {"type": "ReLU", "params": {}},
        {"type": "MaxPool2d", "params": {"kernel_size": 2, "stride": 2}},

        {"type": "Flatten", "params": {}},
        {"type": "Linear", "params": {"in_features": 512*7*7, "out_features": 4096}},
        {"type": "ReLU", "params": {}},
        {"type": "Dropout", "params": {"p": 0.5}},
        {"type": "Linear", "params": {"in_features": 4096, "out_features": 4096}},
        {"type": "ReLU", "params": {}},
        {"type": "Dropout", "params": {"p": 0.5}},
        {"type": "Linear", "params": {"in_features": 4096, "out_features": 1000}}
    ],

    # ResNet-18 (ImageNet) - represented with block placeholders
    # Note: residual connections are represented here as "ResidualBlock" items
    # which assume your system supports a ResidualBlock type that expands into the
    # appropriate sequence of convolutions + skip connections when exported.
    "ResNet-18": [
        {"type": "Conv2d", "params": {"in_channels": 3, "out_channels": 64, "kernel_size": 7, "stride": 2, "padding": 3}},
        {"type": "BatchNorm2d", "params": {"num_features": 64}},
        {"type": "ReLU", "params": {}},
        {"type": "MaxPool2d", "params": {"kernel_size": 3, "stride": 2, "padding": 1}},

        {"type": "ResidualBlock", "params": {"in_channels": 64, "out_channels": 64, "stride": 1, "repeats": 2}},
        {"type": "ResidualBlock", "params": {"in_channels": 64, "out_channels": 128, "stride": 2, "repeats": 2}},
        {"type": "ResidualBlock", "params": {"in_channels": 128, "out_channels": 256, "stride": 2, "repeats": 2}},
        {"type": "ResidualBlock", "params": {"in_channels": 256, "out_channels": 512, "stride": 2, "repeats": 2}},

        {"type": "AdaptiveAvgPool2d", "params": {"output_size": (1, 1)}},
        {"type": "Flatten", "params": {}},
        {"type": "Linear", "params": {"in_features": 512, "out_features": 1000}}
    ],

    # GoogLeNet / Inception-v1 - represented with Inception module placeholders
    # Each Inception entry assumes your system can expand an "Inception" module
    # into its internal branches when exporting. If not supported, consider adding
    # custom Inception layer handling in export_utils.
    "GoogLeNet": [
        {"type": "Conv2d", "params": {"in_channels": 3, "out_channels": 64, "kernel_size": 7, "stride": 2, "padding": 3}},
        {"type": "ReLU", "params": {}},
        {"type": "MaxPool2d", "params": {"kernel_size": 3, "stride": 2, "padding": 1}},
        {"type": "Conv2d", "params": {"in_channels": 64, "out_channels": 64, "kernel_size": 1}},
        {"type": "Conv2d", "params": {"in_channels": 64, "out_channels": 192, "kernel_size": 3, "padding": 1}},
        {"type": "MaxPool2d", "params": {"kernel_size": 3, "stride": 2, "padding": 1}},

        {"type": "Inception", "params": {"in_channels": 192, "out_1x1": 64, "out_3x3_reduce": 96, "out_3x3": 128, "out_5x5_reduce": 16, "out_5x5": 32, "out_pool_proj": 32}},
        {"type": "Inception", "params": {"in_channels": 256, "out_1x1": 128, "out_3x3_reduce": 128, "out_3x3": 192, "out_5x5_reduce": 32, "out_5x5": 96, "out_pool_proj": 64}},
        {"type": "MaxPool2d", "params": {"kernel_size": 3, "stride": 2, "padding": 1}},

        {"type": "Inception", "params": {"in_channels": 480, "out_1x1": 192, "out_3x3_reduce": 96, "out_3x3": 208, "out_5x5_reduce": 16, "out_5x5": 48, "out_pool_proj": 64}},
        {"type": "Inception", "params": {"in_channels": 512, "out_1x1": 160, "out_3x3_reduce": 112, "out_3x3": 224, "out_5x5_reduce": 24, "out_5x5": 64, "out_pool_proj": 64}},
        {"type": "Inception", "params": {"in_channels": 512, "out_1x1": 128, "out_3x3_reduce": 128, "out_3x3": 256, "out_5x5_reduce": 24, "out_5x5": 64, "out_pool_proj": 64}},
        {"type": "Inception", "params": {"in_channels": 512, "out_1x1": 112, "out_3x3_reduce": 144, "out_3x3": 288, "out_5x5_reduce": 32, "out_5x5": 64, "out_pool_proj": 64}},
        {"type": "Inception", "params": {"in_channels": 528, "out_1x1": 256, "out_3x3_reduce": 160, "out_3x3": 320, "out_5x5_reduce": 32, "out_5x5": 128, "out_pool_proj": 128}},
        {"type": "MaxPool2d", "params": {"kernel_size": 3, "stride": 2, "padding": 1}},

        {"type": "Inception", "params": {"in_channels": 832, "out_1x1": 256, "out_3x3_reduce": 160, "out_3x3": 320, "out_5x5_reduce": 32, "out_5x5": 128, "out_pool_proj": 128}},
        {"type": "Inception", "params": {"in_channels": 832, "out_1x1": 384, "out_3x3_reduce": 192, "out_3x3": 384, "out_5x5_reduce": 48, "out_5x5": 128, "out_pool_proj": 128}},

        {"type": "AdaptiveAvgPool2d", "params": {"output_size": (1, 1)}},
        {"type": "Flatten", "params": {}},
        {"type": "Linear", "params": {"in_features": 1024, "out_features": 1000}}
    ],
}