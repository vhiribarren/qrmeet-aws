import os

import yaml
from box import Box

import typing

CONFIG_DIR = "config"

class Conf(Box):
    pass

def load(env: str) -> Conf:
    filename = os.path.join(CONFIG_DIR, env + ".yaml")
    box = Box.from_yaml(filename=filename, Loader=yaml.FullLoader)
    box.env = env
    return typing.cast(Conf, box)