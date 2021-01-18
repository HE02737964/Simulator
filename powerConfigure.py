import numpy as np
import random
import json

with open('config.json', 'r') as f:
    config = json.load(f)

N_db = config["N_dBm"]
bw = config["bw"]

N0 = (10**(N_db/10)) / 1000
N0 = N0 * bw

