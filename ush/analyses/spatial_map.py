#!/usr/bin/env python3

###############################################################################
#
# Name:          spatial_map.py
# Contact(s):    Marcel Caron
# Developed:     Feb. 01, 2023 by Marcel Caron 
# Last Modified: Feb. 01, 2023 by Marcel Caron             
# Title:         Precip spatial map execution script
# Abstract:      Defines input variables for precip spatial map functions, 
#                imports the functions from 
#                {USHevs}/cam_plots_precip_spatial_map.py, and runs the spatial
#                map. Lists of models and verification masking regions can be
#                provided; otherwise, single values must be provided to inputs.  
#
###############################################################################

import sys
import os
import datetime
import logging

USH_DIR = os.environ['USH_DIR']

# Load cam and global_det modules
MODULES_DIR1 = "global_det"
MODULES_DIR2 = "cam"
sys.path.insert(0, os.path.abspath(os.path.join(USH_DIR, MODULES_DIR1)))
sys.path.insert(0, os.path.abspath(os.path.join(USH_DIR, MODULES_DIR2)))
import cam_plots_precip_spatial_map
from settings import ModelSpecs
model_info = ModelSpecs()
from check_variables import *

# Load Env Vars
DATE_TYPE = check_DATE_TYPE(os.environ['DATE_TYPE'])
PLOT_TYPE = os.environ['PLOT_TYPE']
FCST_LEAD = check_FCST_LEAD(os.environ['FCST_LEAD'])
EVAL_PERIOD = check_EVAL_PERIOD(os.environ['EVAL_PERIOD'])
FCST_VALID_HOUR = check_FCST_VALID_HOUR(os.environ['FCST_VALID_HOUR'], DATE_TYPE)
VALID_END = check_VALID_END(os.environ['VALID_END'], DATE_TYPE, EVAL_PERIOD, plot_type=PLOT_TYPE)
MODELS = check_MODELS(os.environ['MODELS']).replace(' ','').split(',')
VX_MASK_LIST = check_VX_MASK_LIST(os.environ['VX_MASK_LIST']).replace(' ','').split(',')
SAVE_DIR = check_SAVE_DIR(os.environ['SAVE_DIR'])
STAT_OUTPUT_BASE_DIR = check_STAT_OUTPUT_BASE_DIR(os.environ['STAT_OUTPUT_BASE_DIR'])
FIXevs = os.environ['FIXevs']
cartopyDataDir = os.environ['cartopyDataDir']
VERIF_TYPE = os.environ['VERIF_TYPE']

# Define Settings
INPUT_DIR = STAT_OUTPUT_BASE_DIR
OUTPUT_DIR = SAVE_DIR
LOGO_DIR = FIXevs
MODEL_INFO_DICT = {
    'obs': {'name': VERIF_TYPE,
            'plot_name': model_info.model_alias[VERIF_TYPE]['plot_name'],
            'obs_name': 'OBS'}
}
for MODEL in MODELS:
    if MODEL in model_info.model_alias:
        MODEL_INFO_DICT[MODEL] = {'name': MODEL,
                                  'plot_name': model_info.model_alias[MODEL]['plot_name'],
                                  'obs_name': 'NA'}
    else:
        MODEL_INFO_DICT[MODEL] = {'name': MODEL,
                                  'plot_name': MODEL,
                                  'obs_name': 'NA'}
DATE_INFO_DICT = {
    'end_date': VALID_END,
    'valid_hr_end': FCST_VALID_HOUR,
    'forecast_hour': FCST_LEAD,
}
MET_INFO_DICT = {}

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
logging_dir = os.path.join(OUTPUT_DIR, 'logs')
if not os.path.exists(logging_dir):
    os.makedirs(logging_dir)
job_logging_file = os.path.join(
    logging_dir, 
    os.path.basename(__file__)
    + '_runon'+datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    + '.log'
)
logger = logging.getLogger(job_logging_file)
logger.setLevel('DEBUG')
formatter = logging.Formatter(
    '%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d) %(levelname)s: '
    + '%(message)s',
    '%m/%d %H:%M:%S'
)
file_handler = logging.FileHandler(job_logging_file, mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger_info = f"Log file: {job_logging_file}"
print(logger_info)
logger.info(logger_info)

for VX_MASK in VX_MASK_LIST:
    PLOT_INFO_DICT = {
        'vx_mask': VX_MASK,
    }
    p = cam_plots_precip_spatial_map.PrecipSpatialMap(
        logger, INPUT_DIR, OUTPUT_DIR, MODEL_INFO_DICT, 
        DATE_INFO_DICT, PLOT_INFO_DICT, MET_INFO_DICT, 
        LOGO_DIR, cartopyDataDir
    )
    p.make_precip_spatial_map()
