import sys

PUP_STATES = {'FULL_NAME': 0, 'ADRESSES': 1, 'END': 2}

# Присваиваем переменную качестве возвращаемого объекта при импорте
sys.modules[__name__] = PUP_STATES
