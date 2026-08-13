#!/usr/bin/env python3
"""
spatial_map.py
CONTRIBUTORS: Marcel Caron, marcel.caron@noaa.gov
----------------------
Executes precip spatial map plotting for the cam component.

Environment Variables (Inputs):
    Various, including DATE_TYPE, PLOT_TYPE, FCST_LEAD, EVAL_PERIOD,
    FCST_VALID_HOUR, VALID_END, MODELS, VX_MASK_LIST, SAVE_DIR,
    STAT_OUTPUT_BASE_DIR, FIXevs, VERIF_TYPE, RESTART_DIR

Outputs:
    - Runs spatial map plotting using input variables and imported functions.
    - Handles lists of models and verification masking regions.

This script is intended to be run as part of the cam component to automate
precip spatial map plotting and configuration.
"""

# Standard library imports
import datetime
import logging
import os
import sys
from urllib.parse import urlparse, parse_qs

# Local imports
USH_DIR = os.environ['USH_DIR']
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
SPATIAL_MAPS_OUTPUT_BASE_DIR = check_STAT_OUTPUT_BASE_DIR(os.environ['SPATIAL_MAPS_OUTPUT_BASE_DIR'])
FIXevs = os.environ['FIXevs']
VERIF_TYPE = os.environ['VERIF_TYPE']
RESTART_DIR = os.environ['RESTART_DIR']

# Define Settings
OUTPUT_DIR = SAVE_DIR
LOGO_DIR = os.path.join(FIXevs, 'logos')
if VERIF_TYPE == 'ccpa':
    MODEL_INFO_DICT = {}
else:
    MODEL_INFO_DICT = {
        'obs': {'name': VERIF_TYPE,
                'plot_name': model_info.model_alias[VERIF_TYPE]['plot_name'],
                'obs_name': 'OBS',
                'input_dir': STAT_OUTPUT_BASE_DIR}
    }
models = []
model_queries = []
for MODEL in MODELS:
    parsed_model = urlparse(MODEL)
    models.append(parsed_model.path)
    model_queries.append(parse_qs(parsed_model.query))

for m, model in enumerate(models):
    if model in model_info.model_alias:
        model_plot_name = model_info.model_alias[model]['plot_name']
    else:
        model_plot_name = model
    if model == 'rap':
        model_input_dir = STAT_OUTPUT_BASE_DIR
    else:
        model_input_dir = SPATIAL_MAPS_OUTPUT_BASE_DIR
    if 'shift' in model_queries[m]:
        shift = int(model_queries[m]['shift'][0])
    else:
        shift = 0
    MODEL_INFO_DICT[model] = {'name': model,
                              'plot_name': model_plot_name,
                              'obs_name': 'NA',
                              'input_dir': model_input_dir,
                              'shift': shift}
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
        logger, OUTPUT_DIR, RESTART_DIR, MODEL_INFO_DICT, 
        DATE_INFO_DICT, PLOT_INFO_DICT, MET_INFO_DICT, 
        LOGO_DIR
    )
    p.make_precip_spatial_map()
