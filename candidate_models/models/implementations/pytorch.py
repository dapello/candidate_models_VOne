import logging
from collections import OrderedDict

import networkx as nx
import numpy as np
import torch
from PIL import Image
from torch.autograd import Variable
from torchvision.models.alexnet import alexnet
from torchvision.models.resnet import resnet18
from torchvision.models.squeezenet import squeezenet1_0, squeezenet1_1
from torchvision.transforms import transforms

from candidate_models.models.implementations import DeepModel, Defaults

_logger = logging.getLogger(__name__)
logging.getLogger("PIL").setLevel(logging.WARNING)

SUBMODULE_SEPARATOR = '.'


class PytorchModel(DeepModel):
    def __init__(self, model_name, weights=Defaults.weights,
                 batch_size=Defaults.batch_size, image_size=Defaults.image_size):
        super().__init__(batch_size=batch_size, image_size=image_size)
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._logger.debug(f"Using device {self._device}")
        constructor = model_constructors[model_name]
        assert weights in ['imagenet', None]
        self._model = constructor(pretrained=weights == 'imagenet')
        self._model = self._model.to(self._device)

    def _load_image(self, image_filepath):
        with Image.open(image_filepath) as image:
            if image.mode.upper() != 'L':  # not binary
                # work around to https://github.com/python-pillow/Pillow/issues/1144,
                # see https://stackoverflow.com/a/30376272/2225200
                return image.copy()
            else:  # make sure potential binary images are in RGB
                image = Image.new("RGB", image.size)
                image.paste(image)
                return image

    def _preprocess_images(self, images, image_size):
        images = [self._preprocess_image(image, image_size) for image in images]
        images = np.concatenate(images)
        return images

    def _preprocess_image(self, image, image_size):
        if isinstance(image, np.ndarray):
            image = Image.fromarray(np.uint8(image * 255))
        image = torchvision_preprocess_input(image_size)(image)
        return image

    def _get_activations(self, images, layer_names):
        images = [torch.from_numpy(image) for image in images]
        images = Variable(torch.stack(images))
        images = images.to(self._device)

        layer_results = OrderedDict()

        def walk_pytorch_module(module, layer_name):
            for part in layer_name.split(SUBMODULE_SEPARATOR):
                module = module._modules.get(part)
                assert module is not None, "No submodule found for layer {}, at part {}".format(layer_name, part)
            return module

        def store_layer_output(layer_name, output):
            layer_results[layer_name] = output.cpu().data.numpy()

        for layer_name in layer_names:
            layer = walk_pytorch_module(self._model, layer_name)
            layer.register_forward_hook(
                lambda _layer, _input, output, name=layer_name: store_layer_output(name, output))

        self._model.eval()
        self._model(images)
        return layer_results

    def __repr__(self):
        return repr(self._model)

    def layers(self):
        return self._layers(self._model)

    @classmethod
    def _layers(cls, module, name_prefix=None):
        if not module._modules:
            module_name = name_prefix + SUBMODULE_SEPARATOR + module.__class__.__name__
            yield module_name, module
            return
        for submodule_name, submodule in module._modules.items():
            submodule_prefix = (name_prefix + SUBMODULE_SEPARATOR + submodule_name) if name_prefix is not None \
                else submodule_name
            yield from cls._layers(submodule, name_prefix=submodule_prefix)

    def graph(self):
        g = nx.DiGraph()
        for layer_name, layer in self.layers():
            g.add_node(layer_name, object=layer, type=type(layer))
        return g


def torchvision_preprocess_input(image_size, normalize_mean=[0.485, 0.456, 0.406], normalize_std=[0.229, 0.224, 0.225]):
    return transforms.Compose([
        transforms.Resize(image_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=normalize_mean, std=normalize_std),
        lambda img: img.unsqueeze(0)
    ])


model_constructors = {
    'alexnet': alexnet,  # https://arxiv.org/abs/1404.5997
    'squeezenet1_0': squeezenet1_0,  # https://arxiv.org/abs/1602.07360
    'squeezenet1_1': squeezenet1_1,  # https://github.com/DeepScale/SqueezeNet/tree/master/SqueezeNet_v1.1
    'resnet-18': resnet18,  # https://arxiv.org/abs/1512.03385
}