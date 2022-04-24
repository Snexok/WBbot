import sys

BOTS_NAME = ['Oleg', 'Einstein', 'Boulevard Depo']

# Присваиваем переменную качестве возвращаемого объекта при импорте
sys.modules[__name__] = BOTS_NAME
