import os

dirs = ["data", "orders"]
for dir in dirs:
    try:
        os.mkdir(dir)
    except:
        pass