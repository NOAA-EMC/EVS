'''
Name: global_det_atmos_plots_long_term.py
Contact(s): Mallory Row
Abstract: This script generates monthly and yearly long term stats plots.
'''

import sys
import os
import logging
import datetime
import calendar
import glob
import subprocess
import pandas as pd
pd.plotting.deregister_matplotlib_converters()
#pd.plotting.register_matplotlib_converters()
import numpy as np
import itertools
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
MET_ROOT = os.environ['MET_ROOT']
met_ver = os.environ['met_ver']
evs_run_mode = os.environ['evs_run_mode']
COMINmonthlystats = os.environ['COMINmonthlystats']
COMINyearlystats = os.environ['COMINyearlystats']
VDATEYYYY = os.environ['VDATEYYYY']
VDATEmm = os.environ['VDATEmm']

print("END: "+os.path.basename(__file__))
