#!/usr/bin/env python3
import argparse
import math
import threading
import subprocess
import time
import os
from datetime import datetime
import matplotlib.pyplot as plt
import glob

parser = argparse.ArgumentParser(description='Data analyzer for impact data')
parser.add_argument('-d', '--test_directory', help='Directory to store the test results', default='/home/adwiii/openpilot/tools/sim/test_results/2022-03-01T23_29_20.907060')

args = parser.parse_args()
test_directory = args.test_directory

intensities = []
for file in glob.glob(test_directory + '/**/collision_data.txt'):
  with open(file) as f:
    lines = f.readlines()
    intensities.append(eval(lines[-1]))
plt.hist(intensities)
plt.xlabel('Intensity of collisions')
plt.ylabel('Count of collisions')
plt.title('Histogram of collision intensities')
plt.show()
