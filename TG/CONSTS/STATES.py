import sys

STATES = {'ADMIN': 0, 'ADMIN_ADDRESS_DISTRIBUTION': 1, 'MAIN': 2, 'ORDER': 3, 'PVZ': 4, 'INSIDE': 5, 'PUP': 6}

# Присваиваем переменную качестве возвращаемого объекта при импорте
sys.modules[__name__] = STATES
