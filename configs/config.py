import pathlib

import yaml
import sys

parent_dir = str(pathlib.Path(__file__).parent.resolve())

with open(parent_dir+"/config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# Присваиваем переменную configs в качестве возвращаемого объекта при импорте
sys.modules[__name__] = config