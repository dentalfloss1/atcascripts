import sys
import subprocess
import os
import shutil
from math import pi
import io
from contextlib import redirect_stdout,redirect_stderr
import numpy as np
import datetime
import matplotlib.pyplot as plt

modelfitcommand = ["""casa""","""--nologfile""","""--nologger""","""--nogui""","""--log2term""","""-c""","""'print("foo")'""" ]
print(modelfitcommand)
out = subprocess.check_output(modelfitcommand)
print(out)

start_epoch = datetime.datetime(1858, 11, 17, 00, 00, 00, 00)
