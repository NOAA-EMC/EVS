#!/usr/bin/env python3
# =============================================================================
#
# NAME: cam_create_output_dirs.py
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Define working/ output directories and create them if they don't
#          exist.
# DEPENDENCIES: os.path.join([
#                   SCRIPTSevs,COMPONENT,STEP,
#                   "_".join(["exevs",MODELNAME,VERIF_CASE,STEP+".sh"]
#               )]
#
# =============================================================================

import os
import re
from datetime import datetime, timedelta as td
from cam_plots_grid2obs_graphx_defs import graphics as graphics_g2o
from cam_plots_precip_graphx_defs import graphics as graphics_pcp
import cam_util as cutil

print(f"BEGIN: {os.path.basename(__file__)}")

# Read in environment variables
evs_ver = os.environ['evs_ver']
COMIN = os.environ['COMIN']
COMOUT = os.environ['COMOUT']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
COMPONENT = os.environ['COMPONENT']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
MODELNAME = os.environ['MODELNAME']
VDATE = os.environ['VDATE']
vdate_dt = datetime.strptime(VDATE, '%Y%m%d')
if VERIF_CASE == "precip":
    if STEP == 'prep':
        FHR_END_FULL = os.environ['FHR_END_FULL']
        FHR_END_SHORT = os.environ['FHR_END_SHORT']
        fhr_end_max = max(int(FHR_END_FULL), int(FHR_END_SHORT))
        start_date_dt = vdate_dt - td(hours=fhr_end_max)
        VERIF_TYPE = os.environ['VERIF_TYPE']
        OBSNAME = os.environ['OBSNAME']
    elif STEP == 'stats':
        FHR_END_FULL = os.environ['FHR_END_FULL']
        FHR_END_SHORT = os.environ['FHR_END_SHORT']
        fhr_end_max = max(int(FHR_END_FULL), int(FHR_END_SHORT))
        start_date_dt = vdate_dt - td(hours=fhr_end_max)
        VERIF_TYPE = os.environ['VERIF_TYPE']
        OBSNAME = os.environ['OBSNAME']
    elif STEP == 'plots':
        all_eval_periods = cutil.get_all_eval_periods(graphics_pcp)
elif VERIF_CASE == "grid2obs":
    if STEP == 'prep':
        NEST = os.environ['NEST']
    if STEP == 'stats':
        NEST = os.environ['NEST']
        FHR_END_FULL = os.environ['FHR_END_FULL']
        FHR_END_SHORT = os.environ['FHR_END_SHORT']
        fhr_end_max = max(int(FHR_END_FULL), int(FHR_END_SHORT))
        start_date_dt = vdate_dt - td(hours=fhr_end_max)
        VERIF_TYPE = os.environ['VERIF_TYPE']
        OBSNAME = os.environ['OBSNAME']
    elif STEP == 'plots':
        all_eval_periods = cutil.get_all_eval_periods(graphics_g2o)
if STEP == 'stats':
    job_type = os.environ['job_type']


# Define data base directorie
data_base_dir = os.path.join(DATA, VERIF_CASE, 'data')
data_dir_list = [data_base_dir]
if VERIF_CASE == 'precip':
    if STEP == 'prep':
        data_dir_list.append(os.path.join(data_base_dir, MODELNAME))
        data_dir_list.append(os.path.join(data_base_dir, OBSNAME))
    if STEP == 'stats':
        data_dir_list.append(os.path.join(data_base_dir, MODELNAME))
        data_dir_list.append(os.path.join(data_base_dir, OBSNAME))
elif VERIF_CASE == 'grid2obs':
    if STEP == 'stats':
        data_dir_list.append(os.path.join(data_base_dir, MODELNAME))

# Create data directories and subdirectories
for data_dir in data_dir_list:
    if not os.path.exists(data_dir):
        print(f"Creating data directory: {data_dir}")
        os.makedirs(data_dir, mode=0o755)

# Create job script base directory
job_scripts_dirs = []
if STEP == 'prep':
    job_scripts_dirs.append(os.path.join(DATA, VERIF_CASE, STEP, 'prep_job_scripts'))
if STEP == 'stats':
    job_scripts_dirs.append(os.path.join(DATA, VERIF_CASE, 'METplus_job_scripts', 'reformat'))
    job_scripts_dirs.append(os.path.join(DATA, VERIF_CASE, 'METplus_job_scripts', 'generate'))
    job_scripts_dirs.append(os.path.join(DATA, VERIF_CASE, 'METplus_job_scripts', 'gather'))
    job_scripts_dirs.append(os.path.join(DATA, VERIF_CASE, 'METplus_job_scripts', 'gather2'))
    job_scripts_dirs.append(os.path.join(DATA, VERIF_CASE, 'METplus_job_scripts', 'gather3'))
if STEP == 'plots':
    job_scripts_dirs.append(os.path.join(DATA, VERIF_CASE, STEP, 'plotting_job_scripts'))
for job_scripts_dir in job_scripts_dirs:
    if not os.path.exists(job_scripts_dir):
        print(f"Creating job script directory: {job_scripts_dir}")
        os.makedirs(job_scripts_dir, mode=0o755)

# Define working and COMOUT directories
working_dir_list = []
COMOUT_dir_list = []
if STEP == 'prep':
    if VERIF_CASE == 'grid2obs':
        working_output_base_dir = os.path.join(
            DATA, VERIF_CASE
        )
        working_dir_list.append(working_output_base_dir)
        working_dir_list.append(os.path.join(
            working_output_base_dir, 'data', 
            NEST+'.'+vdate_dt.strftime('%Y%m%d')
        ))
        COMOUT_dir_list.append(os.path.join(
            COMOUT, 
            NEST+'.'+vdate_dt.strftime('%Y%m%d')
        ))
elif STEP == 'stats':
    if VERIF_CASE == 'precip':
        if job_type == 'reformat':
            working_output_base_dir = os.path.join(
                DATA, VERIF_CASE, 'METplus_output', VERIF_TYPE
            )
        if job_type == 'generate':
            working_output_base_dir = os.path.join(
                DATA, VERIF_CASE, 'METplus_output', VERIF_TYPE
            )
        if job_type == 'gather':
            working_output_base_dir = os.path.join(
                DATA, VERIF_CASE, 'METplus_output', 'gather_small'
            )
        if job_type == 'gather2':
            working_output_base_dir = os.path.join(
                DATA, VERIF_CASE, 'METplus_output'
            )
        if job_type == 'gather3':
            working_output_base_dir = os.path.join(
                DATA, VERIF_CASE, 'METplus_output'
            )
        working_dir_list.append(working_output_base_dir)
        if job_type == 'reformat':
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'pcp_combine', 'confs'
            ))
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'pcp_combine', 'logs'
            ))
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'pcp_combine', 'tmp'
            ))
        if job_type == 'generate':
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'grid_stat', 'confs'
            ))
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'grid_stat', 'logs'
            ))
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'grid_stat', 'tmp'
            ))
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'grid_stat', 
                MODELNAME+'.'+vdate_dt.strftime('%Y%m%d')
            ))
        if job_type in ['gather', 'gather2', 'gather3']:
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'stat_analysis', 'confs'
            ))
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'stat_analysis', 'logs'
            ))
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'stat_analysis', 'tmp'
            ))
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'stat_analysis', 
                MODELNAME+'.'+vdate_dt.strftime('%Y%m%d')
            ))
        date_dt = start_date_dt
        while date_dt <= vdate_dt+td(days=1):
            COMOUT_dir_list.append(os.path.join(
                COMOUT, 
                MODELNAME+'.'+date_dt.strftime('%Y%m%d')
            ))
            if job_type == 'reformat':
                working_dir_list.append(os.path.join(
                    working_output_base_dir, 'pcp_combine', 
                    OBSNAME+'.'+date_dt.strftime('%Y%m%d')
                ))
                working_dir_list.append(os.path.join(
                    working_output_base_dir, 'pcp_combine', 
                    MODELNAME+'.'+date_dt.strftime('init%Y%m%d')
                ))
            date_dt+=td(days=1)
    elif VERIF_CASE == "grid2obs":
        if job_type == 'reformat':
            working_output_base_dir = os.path.join(
                DATA, VERIF_CASE, 'METplus_output', VERIF_TYPE
            )
        if job_type == 'generate':
            working_output_base_dir = os.path.join(
                DATA, VERIF_CASE, 'METplus_output', VERIF_TYPE
            )
        if job_type == 'gather':
            working_output_base_dir = os.path.join(
                DATA, VERIF_CASE, 'METplus_output', 'gather_small'
            )
        if job_type == 'gather2':
            working_output_base_dir = os.path.join(
                DATA, VERIF_CASE, 'METplus_output'
            )
        if job_type == 'gather3':
            working_output_base_dir = os.path.join(
                DATA, VERIF_CASE, 'METplus_output'
            )
        working_dir_list.append(working_output_base_dir)
        if job_type == 'reformat':
            working_dir_list.append(os.path.join(
                working_output_base_dir, NEST, 'pb2nc', 'confs'
            ))
            working_dir_list.append(os.path.join(
                working_output_base_dir, NEST, 'pb2nc', 'logs'
            ))
            working_dir_list.append(os.path.join(
                working_output_base_dir, NEST, 'pb2nc', 'tmp'
            ))
            if NEST in ['spc_otlk', 'firewx']:
                working_dir_list.append(os.path.join(
                    working_output_base_dir, 'genvxmask', 'confs'
                ))
                working_dir_list.append(os.path.join(
                    working_output_base_dir, 'genvxmask', 'logs'
                ))
                working_dir_list.append(os.path.join(
                    working_output_base_dir, 'genvxmask', 'tmp'
                ))
                working_dir_list.append(os.path.join(
                    working_output_base_dir, 'genvxmask',
                    NEST+'.'+vdate_dt.strftime('%Y%m%d')
                ))
        if job_type == 'generate':
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'point_stat', 'confs'
            ))
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'point_stat', 'logs'
            ))
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'point_stat', 'tmp'
            ))
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'point_stat', 
                MODELNAME+'.'+vdate_dt.strftime('%Y%m%d')
            ))
        if job_type in ['gather', 'gather2', 'gather3']:
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'stat_analysis', 'confs'
            ))
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'stat_analysis', 'logs'
            ))
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'stat_analysis', 'tmp'
            ))
            working_dir_list.append(os.path.join(
                working_output_base_dir, 'stat_analysis', 
                MODELNAME+'.'+vdate_dt.strftime('%Y%m%d')
            ))
        date_dt = start_date_dt
        while date_dt <= vdate_dt+td(days=1):
            COMOUT_dir_list.append(os.path.join(
                COMOUT, 
                MODELNAME+'.'+date_dt.strftime('%Y%m%d')
            ))
            if job_type == 'reformat':
                working_dir_list.append(os.path.join(
                    working_output_base_dir, NEST, 'pb2nc', 
                    OBSNAME+'.'+date_dt.strftime('%Y%m%d')
                ))
                working_dir_list.append(os.path.join(
                    working_output_base_dir, NEST, 'pb2nc', 
                    MODELNAME+'.'+date_dt.strftime('init%Y%m%d')
                ))
            date_dt+=td(days=1)
elif STEP == 'plots':
    if VERIF_CASE == 'grid2obs':

        working_output_base_dir = os.path.join(
            DATA, VERIF_CASE
        )
        working_dir_list.append(working_output_base_dir)
        working_dir_list.append(os.path.join(
            working_output_base_dir, 'data'
        ))
        working_dir_list.append(os.path.join(
            working_output_base_dir, 'out'
        ))
        working_dir_list.append(os.path.join(
            working_output_base_dir, 'out', 'logs'
        ))
        COMOUT_dir_list.append(os.path.join(
            COMOUT, 
        ))
        for plot_group in [
                'aq', 'aviation', 'cape', 'ceil_vis', 'precip', 
                'radar', 'rtofs_sfc', 'sfc_upper'
            ]:
            for eval_period in all_eval_periods:
                working_dir_list.append(os.path.join(
                    working_output_base_dir, 'out', str(plot_group).lower(), 
                    str(eval_period).lower()
                ))
    if VERIF_CASE == 'precip':
        working_output_base_dir = os.path.join(
            DATA, VERIF_CASE
        )
        working_dir_list.append(working_output_base_dir)
        working_dir_list.append(os.path.join(
            working_output_base_dir, 'data'
        ))
        working_dir_list.append(os.path.join(
            working_output_base_dir, 'out'
        ))
        working_dir_list.append(os.path.join(
            working_output_base_dir, 'out', 'logs'
        ))
        COMOUT_dir_list.append(os.path.join(
            COMOUT, 
        ))
        for plot_group in ['precip', 'radar', 'rtofs_sfc', 'sfc_upper']:
            for eval_period in all_eval_periods:
                working_dir_list.append(os.path.join(
                    working_output_base_dir, 'out', str(plot_group).lower(), 
                    str(eval_period).lower()
                ))
# Create working output and COMOUT directories
for working_dir in working_dir_list:
    if not os.path.exists(working_dir):
        print(f"Creating working output directory: {working_dir}")
        os.makedirs(working_dir, mode=0o755, exist_ok=True)
    else:
        print(f"Tried creating working output directory but already exists: {working_dir}")
for COMOUT_dir in COMOUT_dir_list:
    if not os.path.exists(COMOUT_dir):
        print(f"Creating COMOUT directory: {COMOUT_dir}")
        os.makedirs(COMOUT_dir, mode=0o755, exist_ok=True)

print(f"END: {os.path.basename(__file__)}")
