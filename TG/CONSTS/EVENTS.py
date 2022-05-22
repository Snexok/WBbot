import sys

EVENTS = {'FULL_NAME': 0, 'ADDRESSES': 1, 'END': 2}

# Присваиваем переменную качестве возвращаемого объекта при импорте
sys.modules[__name__] = EVENTS
