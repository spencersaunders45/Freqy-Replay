from tomlkit.toml_file import TOMLFile
import multiprocessing as mp
import threading as th

from uhd_interface import SDR

try:
    import cupy as np
except:
    import numpy as np

settings = TOMLFile('config.toml').read()

""" 
TODO: add arguments to view all saved frequencies
TODO: add argument to select saved frequency
"""

class ReplayAttack:
    """ Pwn wireless communication """
    def __init__(self):
        pass

    def 

if __name__ == '__main__':
    ReplayAttack()
