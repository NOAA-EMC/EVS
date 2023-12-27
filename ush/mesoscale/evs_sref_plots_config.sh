#!/bin/ksh

# ================================================================================================
# NCEP EMC PYTHON PLOTTING OF SREF VERIFICATION
# 
# CONTRIBUTORS:     Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
#
# PURPOSE:          Set up configurations to plot METPLUS output statistics
#
# DESCRIPTION:      This configuration file defines environment variables that are meant to be 
#                   edited by the user and that are called by python scripts at runtime to define 
#                   the plotting task, resulting in one or more graphics output files. 
#
# BEFORE YOU BEGIN: Make sure to set up verif_plotting if you haven't already.  To set up, 
#                   clone the Github repository:
#
#                   $ git clone https://github.com/MarcelCaron-NOAA/verif_plotting 
#
#                   or, if on the NOAA WCOSS supercomputer, choose any directory that will house 
#                   verif_plotting.  As an example, we'll call that directory PY_PLOT_DIR.  Then on 
#                   the command line:
#
#                   $ PY_PLOT_DIR="/path/to/my/verif/plotting/home/directory"
#                   $ mkdir -p ${PY_PLOT_DIR}/out/logs ${PY_PLOT_DIR}/data ${PY_PLOT_DIR}/ush
#                   $ cp -r ${BASE_DIR}/ush/* ${PY_PLOT_DIR}/ush/.
#                   $ cp ${BASE_DIR}/py_plotting.config ${PY_PLOT_DIR}/.
#
# CONFIGURATION:    After setting up verif_plotting, edit the exported variables below.  Each 
#                   variable is a string that will be ingested by the python code.  You'll need to 
#                   be able to point to a correctly structured metplus statistics archive (see the 
#                   comment for Directory Settings below for details).  
#
#                   LIMITATIONS   
#                   In some cases, possible values for exported variables will be limited to what 
#                   is listed in the metplus .stat files or the statistics archive you are using 
#                   (e.g., values for FCST_LEAD or MODEL).  In other cases, possible values will be 
#                   limited to what has been predefined elsewhere in verif_plotting (e.g., values 
#                   for EVAL_PERIOD).  Finally, some settings must match certain allowable settings, 
#                   which are defined in ${USH_DIR}/settings.py in the case_type attribute of the 
#                   Reference() class.  Two asterisks mark these latter settings in the 
#                   comments below. 
#
#                   CONFIGURING PLOT TYPE
#                   The plot type is requested via the last export variable.  Replace the string with 
#                   the desired plot type as explained in the comment.  In most cases, a plot will 
#                   include all of the listed settings; for example, the python code will attempt to
#                   plot all of the listed models in MODEL on the same plot, as well as all of the 
#                   init/valid hours in FCST_INIT/VALID_HOUR and lead times in FCST_LEAD.  
#                   Exceptions to this are any listed var_names and listed domains (VX_MASK_LIST), 
#                   for which individual plots will be made. Listed levels are also plotted 
#                   separately unless the plot type is stat_by_level.
#
# EXECUTION:        After configuring this script, it can be run on the command line:
#
#                   $ /bin/sh ${PY_PLOT_DIR}/py_plotting.config
#
#                   ... which will set the environment variables and run the python code. The python 
#                   code then follows these steps:
#                   (1) Save environment variables as global python variables. Check these variables
#                       and throw an error if an issue is encountered and throw warnings as needed. 
#                       Make sure the datatype for each variable is correct
#                   (2) Send the settings to ${USH_DIR}/df_preprocessing.py, which pulls and prunes 
#                       the .stat files--creating temporary data files in the process and storing 
#                       those files in PRUNE_DIR--then loads the data as pandas dataframes, which 
#                       are filtered several times according to user settings. 
#                   (3) Send the dataframe and user settings to a plotting function, which creates a 
#                       figure object, filters the data, plots the data, adjusts plot features, then 
#                       saves the plot as a png.
#
# DEBUGGING:        Part of the configuration for this script involves setting a logfile path. 
#                   Running the script will print the logfile path for your specific task, which you 
#                   can check for debugging.  The lowest log level that is currently functional is 
#                   "INFO". "DEBUG" statements may be included in a later implementation.
#                
# ================================================================================================
set -x

# Case type settings are used to check if settings are allowed. **
export VERIF_CASE=$verif_case
export VERIF_TYPE=$verif_type

# Used to name the graphics ouput files. File names will start with the URL_HEADER, followed by plot 
# details.  Leave blank ("") to include only plot details in the file names.
export URL_HEADER=""

# Directory Settings.  Make sure USH_DIR, PRUNE_DIR, and SAVE_DIR point to desired .../ush, 
# .../data, and .../out directories.  OUTPUT_BASE_DIR is the location of the metplus stat archive.  
# The default format that plotting scripts use to look for .stat files in the archive is 
# ${OUTPUT_BASE_DIR}/${VERIF_CASE}/${MODEL_NAME}/${Ym}/${MODEL_NAME}*.stat
# This format can be changed by editing the output_base_template variable in the Templates class in
# ${USH_DIR}/settings.py  
export USH_DIR=$ush_dir
export PRUNE_DIR=$prune_dir
export SAVE_DIR=$save_dir
export OUTPUT_BASE_DIR=$output_base_dir


# Logfile settings. Log level options are "DEBUG", "INFO", "WARNING", "ERROR", and "CRITICAL"
#export LOG_METPLUS="${SAVE_DIR}/logs/RRFS_verif_plotting_job_`date '+%Y%m%d-%H%M%S'`_$$.out"
#export LOG_LEVEL="INFO"
export LOG_METPLUS=$log_metplus
export LOG_LEVEL=$log_level

# Version of MET listed in the metplus .stat files used to create graphics
export MET_VERSION=$(echo $met_ver | cut -d'.' -f1-2)

# Will use statistics for all comma-separated models.  Names must match the model naming convention
# in ${OUTPUT_BASE_DIR}
#export MODEL="FV3LAM, FV3LAMDA, FV3LAMDAX, CONUSNEST, HRRR, GFS"
export MODEL="model_list"

# Will use valid or init datetimes based on the setting below. Options are "VALID" or "INIT"
export DATE_TYPE=$date_type

# Will choose a valid or init range based on a preset EVAL_PERIOD.  Use "TEST" if you want to use 
# the custom-defined range below. Presets are defined in ${USH_DIR}/settings.py in the Presets() 
# class. 
#export EVAL_PERIOD="PAST30DAYS"
export EVAL_PERIOD=$eval_period

# If EVAL_PERIOD="TEST", will use statistics from the valid or init range below. If not, ignores 
# these settings. DATE_TYPE decides whether valid or init is used.
#export VALID_BEG="20220213"
#export VALID_END="20220214"
#export INIT_BEG="20220213"
#export INIT_END="20220314"
export VALID_BEG=$valid_beg
export VALID_END=$valid_end
export INIT_BEG=$init_beg
export INIT_END=$init_end

# Will use statistics for all comma-separated valid or init hours. DATE_TYPE decides whether valid 
# or init is used.
#export FCST_INIT_HOUR="0,12"
#export FCST_VALID_HOUR="0,6,12,18"
export FCST_INIT_HOUR="fcst_init_hour"
export FCST_VALID_HOUR="fcst_valid_hour"



# Settings below are used to select desired variable and domain. **
#export FCST_LEVEL="L0"
#export OBS_LEVEL="L0"
#export var_name="VISsfc"
#export VX_MASK_LIST="apl"
export FCST_LEVEL=$fcts_level
export OBS_LEVEL=$obs_level
export var_name=$var_name
export VX_MASK_LIST="$vx_mask_list"


# Will use statistics for all comma-separated lead times 
#export FCST_LEAD="0,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57,60"
export FCST_LEAD="fcst_lead"

# Line type in metplus .stat files used to compute desired metric(s). **
#export LINE_TYPE="ctc"
export LINE_TYPE=$line_type

# Interpolation, as listed in metplus .stat files. **
#export INTERP="BILIN"
export INTERP=$interp

# Will use statistics for all comma-separated thresholds. Use symbols (e.g., >=) to define 
# thresholds. **
#export FCST_THRESH="<805,<1609,<4828,<8045,<16090"
#export OBS_THRESH="<805,<1609,<4828,<8045,<16090"
export FCST_THRESH="thresh_fcst"
export OBS_THRESH="thresh_obs"


# Will plot all comma-separated metrics.  For performance diagram, metrics must be "sratio,pod,csi". 
# Depending on the VERIF_CASE, VERIF_TYPE, and LINE_TYPE, only some settings are allowed. **
#export STATS="sratio, pod, csi"
export STATS="stat_list"

# String of True or False. If "True", will plot bootstrap confidence intervals. Other confidence 
# interval settings can be configured in ${USH_DIR}/settings.py
export CONFIDENCE_INTERVALS="False"

# Will use statistics for all comma-separated interpolation points
#export INTERP_PNTS="3969"
export INTERP_PNTS=interp_pnts


# String defining the type of plot to make. Options are "lead_average", "performance_diagram", 
# "stat_by_level", "threshold_average", "time_series", and "valid_hour_average".
#export PLOT_TYPE="performance_diagram"

# Executes the desired python script.  No need to edit this. 
python $USH_DIR/${PLOT_TYPE}.py
export err=$?; err_chk
