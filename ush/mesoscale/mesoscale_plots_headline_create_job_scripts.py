#!/usr/bin/env python3
import os
import sys
from pathlib import Path

USH_DIR = os.environ['USH_DIR']
sys.path.insert(0, os.path.abspath(USH_DIR))
from mesoscale_plots_headline_graphx_defs import graphics
import mesoscale_util as mutil

USHevs = os.environ['USHevs']
COMPONENT = os.environ['COMPONENT']
STEP = os.environ['STEP']
VERIF_CASE = os.environ['VERIF_CASE']
njob = os.environ['njob']
for VERIF_TYPE in graphics[COMPONENT][VERIF_CASE]:
    for MODELS in graphics[COMPONENT][VERIF_CASE][VERIF_TYPE]:
        for PLOT_TYPE in graphics[COMPONENT][VERIF_CASE][VERIF_TYPE][MODELS]:
            plot_type_settings = graphics[COMPONENT][VERIF_CASE][VERIF_TYPE][MODELS][PLOT_TYPE]
            for EVAL_PERIOD in plot_type_settings['EVAL_PERIODS']:
                if plot_type_settings['DATE_TYPE'] == 'VALID':
                    ANTI_DATE_TYPE = 'INIT'
                    FCST_HOURS = plot_type_settings['FCST_VALID_HOURS']
                    if plot_type_settings['FCST_INIT_HOURS']:
                        ANTI_FCST_HOURS = plot_type_settings['FCST_INIT_HOURS']
                    else:
                        ANTI_FCST_HOURS = plot_type_settings['FCST_VALID_HOURS']
                elif plot_type_settings['DATE_TYPE'] == 'INIT':
                    ANTI_DATE_TYPE = 'VALID'
                    FCST_HOURS = plot_type_settings['FCST_INIT_HOURS']
                    if plot_type_settings['FCST_VALID_HOURS']:
                        ANTI_FCST_HOURS = plot_type_settings['FCST_VALID_HOURS']
                    else:
                        ANTI_FCST_HOURS = plot_type_settings['FCST_INIT_HOURS']
                else:
                    raise ValueError(f"Invalid DATE_TYPE: {plot_type_settings['DATE_TYPE']}")
                    sys.exit(1)
                for FCST_HOUR in FCST_HOURS:
                    for ANTI_FCST_HOUR in ANTI_FCST_HOURS:
                        for LINE_TYPE in plot_type_settings['VARIABLES']:
                            for VARIABLE in plot_type_settings['VARIABLES'][LINE_TYPE]:
                                for FCST_LEAD in plot_type_settings['VARIABLES'][LINE_TYPE][VARIABLE]['FCST_LEADS']:
                                    for STATS in plot_type_settings['VARIABLES'][LINE_TYPE][VARIABLE]['STATSs']: 
                                        for lev_idx, FCST_LEVEL in enumerate(plot_type_settings['VARIABLES'][LINE_TYPE][VARIABLE]['FCST_LEVELs']):
                                            for thresh_idx, FCST_THRESH in enumerate(plot_type_settings['VARIABLES'][LINE_TYPE][VARIABLE]['FCST_THRESHs']):
                                                for INTERP_PNTS in plot_type_settings['VARIABLES'][LINE_TYPE][VARIABLE]['INTERP_PNTSs']:
                                                    njob = int(njob)
                                                    os.environ['VERIF_TYPE'] = VERIF_TYPE
                                                    os.environ['MODELS'] = MODELS
                                                    os.environ['PLOT_TYPE'] = PLOT_TYPE
                                                    os.environ[f"FCST_{plot_type_settings['DATE_TYPE']}_HOUR"] = FCST_HOUR
                                                    os.environ[f"FCST_{ANTI_DATE_TYPE}_HOUR"] = ANTI_FCST_HOUR
                                                    os.environ['VALID_BEG'] = plot_type_settings['VALID_BEG']
                                                    os.environ['VALID_END'] = plot_type_settings['VALID_END']
                                                    os.environ['INIT_BEG'] = plot_type_settings['INIT_BEG']
                                                    os.environ['INIT_END'] = plot_type_settings['INIT_END']
                                                    os.environ['EVAL_PERIOD'] = EVAL_PERIOD
                                                    os.environ['DATE_TYPE'] = plot_type_settings['DATE_TYPE']
                                                    os.environ['FCST_LEVEL'] = plot_type_settings['VARIABLES'][LINE_TYPE][VARIABLE]['FCST_LEVELs'][lev_idx]
                                                    os.environ['OBS_LEVEL'] = plot_type_settings['VARIABLES'][LINE_TYPE][VARIABLE]['OBS_LEVELs'][lev_idx]
                                                    os.environ['VAR_NAME'] = VARIABLE
                                                    os.environ['VX_MASK_LIST'] = plot_type_settings['VX_MASK_LIST']
                                                    os.environ['FCST_LEAD'] = FCST_LEAD
                                                    os.environ['STATS'] = STATS
                                                    os.environ['LINE_TYPE'] = LINE_TYPE
                                                    os.environ['INTERP'] = plot_type_settings['VARIABLES'][LINE_TYPE][VARIABLE]['INTERP']
                                                    os.environ['FCST_THRESH'] = plot_type_settings['VARIABLES'][LINE_TYPE][VARIABLE]['FCST_THRESHs'][thresh_idx]
                                                    os.environ['OBS_THRESH'] = plot_type_settings['VARIABLES'][LINE_TYPE][VARIABLE]['OBS_THRESHs'][thresh_idx]
                                                    os.environ['CONFIDENCE_INTERVALS'] = plot_type_settings['VARIABLES'][LINE_TYPE][VARIABLE]['CONFIDENCE_INTERVALS']
                                                    os.environ['INTERP_PNTS'] = INTERP_PNTS
                                                    os.environ['DELETE_INTERMED_TOGGLE'] = plot_type_settings['VARIABLES'][LINE_TYPE][VARIABLE]['DELETE_INTERMED_TOGGLE']
                                                    mutil.run_shell_command(['python',f'{USHevs}/{COMPONENT}/{COMPONENT}_{STEP}_{VERIF_CASE}_create_job_script.py'])
                                                    njob+=1
                                                    os.environ['njob'] = str(njob)
sys.exit(0)





