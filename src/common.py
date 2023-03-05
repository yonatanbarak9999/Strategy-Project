"""
Author: Yonatan Barak
Date: 05/3/2023
"""
# ------ Imports ------ #
import os

# ------ Consts ------ #

ASSETS_PATH = os.path.join('..', 'assets')


# ------ Functions ------ #

def create_assets_dir():
    try:
        os.mkdir(ASSETS_PATH)
    except FileExistsError:
        pass
