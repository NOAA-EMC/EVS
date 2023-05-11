#! /usr/bin/env python3

import sys
import logging
import re
from pathlib import Path

# Variables to check:
# VERIF_CASE
# info case: 
# warning case: should match one of the known verif cases
# error case: should be string (in quotes), should not be empty
def check_VERIF_CASE(VERIF_CASE):
    if not isinstance(VERIF_CASE, str):
        sys.exit(f"The provided VERIF_CASE ('{VERIF_CASE}') is not a string."
                     + f"  VERIF_CASE must be a string. Check the plotting"
                     + f" configuration file.")
        ##sys.exit(1)
    if not VERIF_CASE:
        sys.exit(f"The provided VERIF_CASE is empty. VERIF_CASE cannot be"
                     + f" empty. Check the plotting configuration file.")
        ##sys.exit(1)
    return VERIF_CASE

# VERIF_TYPE
# info case:
# warning case:should match one of the the known verif cases
# error case: should be a string(in quotes), shouild not be empty
def check_VERIF_TYPE(VERIF_TYPE):
    if not isinstance(VERIF_TYPE, str):
        sys.exit(f"The provided VERIF_TYPE ('{VERIF_TYPE}') is not a string."
                     + f"  VERIF_TYPE must be a string. Check the plotting"
                     + f" configuration file.")
        ##sys.exit(1)
    if not VERIF_TYPE:
        sys.exit(f"The provided VERIF_TYPE is empty. VERIF_TYPE cannot be"
                     + f" empty. Check the plotting configuration file.")
        ##sys.exit(1)
    return VERIF_TYPE

# URL_HEADER
# info case: whether or not an empty string is provided
# warning case:
# error case:should be a string (in quotes), should be alphanumeric, should follow file naming conventions
def check_URL_HEADER(URL_HEADER):
    if not isinstance(URL_HEADER, str):
        sys.exit(f"The provided URL_HEADER ('{URL_HEADER}') is not a string."
                     + f"  URL_HEADER must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if re.search(r'[^A-Za-z0-9_\-\\]', URL_HEADER):
        sys.exit(f"The provided URL_HEADER string ('{URL_HEADER}') contains"
                     + f" invalid characters. URL_HEADER must be made of"
                     + f" alphanumeric characters, hyphen, and/or underscore."
                     + f" Check the plotting configuration file.")
        #sys.exit(1)
    if not URL_HEADER:
        print(f"The provided URL_HEADER is empty. Plot file names will"
                     + f" not include a header.")
    return URL_HEADER

# USH_DIR
# info case:whether or not an empty string is provided
# warning case:
# error case:should be a string, should follow proper directory structure
def check_USH_DIR(USH_DIR):
    if not isinstance(USH_DIR, str):
        sys.exit(f"The provided USH_DIR ('{USH_DIR}') is not a string."
                     + f"  USH_DIR must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if not Path(USH_DIR).exists():
        print(f"WARNING: The provided USH_DIR ('{USH_DIR}') does not exist on the"
                       + f" current system.")
    if not Path(USH_DIR).is_dir():
        print(f"WARNING: The provided USH_DIR ('{USH_DIR}') is not a directory.")
    if not USH_DIR:
        print(f"The provided USH_DIR is empty. Will look for USH files"
                     + f" in the current working directory.")
    return USH_DIR

# PRUNE_DIR
# info case: whether or not an empty string is provided
# warning case:
# error case: should be a string, should follow proper directory structure
def check_PRUNE_DIR(PRUNE_DIR):
    if not isinstance(PRUNE_DIR, str):
        sys.exit(f"The provided PRUNE_DIR ('{PRUNE_DIR}') is not a string."
                     + f"  PRUNE_DIR must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if not Path(PRUNE_DIR).exists():
        print(f"WARNING: The provided PRUNE_DIR ('{PRUNE_DIR}') does not exist on the"
                       + f" current system.")
    if not Path(PRUNE_DIR).is_dir():
        print(f"WARNING: The provided PRUNE_DIR ('{PRUNE_DIR}') is not a directory.")
    if not PRUNE_DIR:
        print(f"The provided PRUNE_DIR is empty. Will store pruned stat files"
                     + f" in the current working directory.")
    return PRUNE_DIR

# SAVE_DIR
# info case:whether or not an empty string is provided
# warning case:
# error case: should be a string, should follow proper directory structure
def check_SAVE_DIR(SAVE_DIR):
    if not isinstance(SAVE_DIR, str):
        sys.exit(f"The provided SAVE_DIR ('{SAVE_DIR}') is not a string."
                     + f"  SAVE_DIR must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if not Path(SAVE_DIR).exists():
        print(f"WARNING: The provided SAVE_DIR ('{SAVE_DIR}') does not exist on the"
                       + f" current system.")
    if not Path(SAVE_DIR).is_dir():
        print(f"WARNING: The provided SAVE_DIR ('{SAVE_DIR}') is not a directory.")
    if not SAVE_DIR:
        print(f"The provided SAVE_DIR is empty. Will store plots"
                     + f" in the current working directory.")
    return SAVE_DIR

# OUTPUT_BASE_DIR
# info case: whether or not an empty string is provided
# warning case:
# error case:should be a string, should follow proper directory structure
def check_OUTPUT_BASE_DIR(OUTPUT_BASE_DIR):
    if not isinstance(OUTPUT_BASE_DIR, str):
        sys.exit(f"The provided OUTPUT_BASE_DIR ('{OUTPUT_BASE_DIR}') is not a string."
                     + f"  OUTPUT_BASE_DIR must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if not Path(OUTPUT_BASE_DIR).exists():
        print(f"WARNING: The provided OUTPUT_BASE_DIR ('{OUTPUT_BASE_DIR}') does not exist on the"
                       + f" current system.")
    if not Path(OUTPUT_BASE_DIR).is_dir():
        print(f"WARNING: The provided OUTPUT_BASE_DIR ('{OUTPUT_BASE_DIR}') is not a directory.")
    if not OUTPUT_BASE_DIR:
        print(f"The provided OUTPUT_BASE_DIR is empty. Will look for stat files"
                     + f" in the current working directory.")
    return OUTPUT_BASE_DIR

# LOG_METPLUS
# info case:
# warning case:
# error case: should be a string, should follow proper directory structure, should not be empty
def check_LOG_METPLUS(LOG_METPLUS):
    if not isinstance(LOG_METPLUS, str):
        sys.exit(f"The provided LOG_METPLUS ('{LOG_METPLUS}') is not a string."
                     + f"  LOG_METPLUS must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if not LOG_METPLUS:
        print(f"WARNING: The provided LOG_METPLUS is empty. The logger will be"
                       + f" the root logger of the hierarchy.")
    return LOG_METPLUS

# LOG_LEVEL
# info case: 
# warning case: whether or not log level is currently supported
# error case: should be a string, should match one of the possible log levels
def check_LOG_LEVEL(LOG_LEVEL):
    if not isinstance(LOG_LEVEL, str):
        sys.exit(f"The provided LOG_LEVEL ('{LOG_LEVEL}') is not a string."
                     + f" LOG_LEVEL must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if str(LOG_LEVEL).upper() not in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]:
        print(f"WARNING: The provided LOG_LEVEL ('{LOG_LEVEL}') may not be"
                       + f" supported by the logger.  Consider using one of"
                       + f" 'DEBUG', 'INFO', 'WARNING', 'ERROR', or"
                       + f" 'CRITICAL'.")
    if str(LOG_LEVEL).upper() not in ["ERROR", "WARNING", "INFO", "DEBUG"]:
        print(f"WARNING: You provided the following LOG_LEVEL: '{LOG_LEVEL}'."
                       + f" Note that the plotting scripts currently only log at"
                       + f" 'ERROR', 'WARNING', 'INFO' and 'DEBUG' levels.")
    if not LOG_LEVEL:
        sys.exit(f"The provided LOG_LEVEL is empty. LOG_LEVEL cannot be"
                     + f" empty. Check the plotting configuration file.")
        #sys.exit(1)
    return LOG_LEVEL

# MET_VERSION
# info case: 
# warning case:
# error case: string be a string, string should contain an integer or a floating point number
def check_MET_VERSION(MET_VERSION):
    if not isinstance(MET_VERSION, str):
        sys.exit(f"The provided MET_VERSION ('{MET_VERSION}') is not a string."
                     + f" MET_VERSION must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if not re.search(r'^[1-9]\d*(\.\d+)?$', MET_VERSION):
        sys.exit(f"The provided MET_VERSION ('{MET_VERSION}') is not a"
                     + f" parseable number. Check the plotting configuration"
                     + f" file.")
        #sys.exit(1)
    return MET_VERSION

# MODEL
# info case:
# warning case:
# error case: should be a string, should be comma-separated or contain no other symbols than letters, numbers, dashes, and underlines
def check_MODEL(MODEL):
    if not isinstance(MODEL, str):
        sys.exit(f"The provided MODEL ('{MODEL}') is not a string."
                     + f" MODEL must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if not re.search(r'(^[ A-Za-z0-9,\-_]+)$', MODEL):
        sys.exit(f"The provided MODEL ('{MODEL}') is not valid. MODEL may"
                     + f" contain letters, numbers, hyphens, underscores,"
                     + f" commas, and spaces only. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    return MODEL

# DATE_TYPE
# info case:
# warning case:
# error case: should be a string, should be either INIT or VALID
def check_DATE_TYPE(DATE_TYPE):
    if not isinstance(DATE_TYPE, str):
        sys.exit(f"The provided DATE_TYPE ('{DATE_TYPE}') is not a string."
                     + f" DATE_TYPE must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if str(DATE_TYPE).upper() not in ['INIT', 'VALID']:
        sys.exit(f"You provided the following DATE_TYPE: '{DATE_TYPE}'."
                     + f" DATE_TYPE must be either 'INIT' or 'VALID'. Check"
                     + f" the plotting configuration file.")
        #sys.exit(1)
    return DATE_TYPE


# EVAL_PERIOD
# info case: Whether or not a TEST will be used and what that means
# warning case: Should be either TEST or a valid EVAL PERIOD
# error case: should be a string, should be alphanumeric, 
def check_EVAL_PERIOD(EVAL_PERIOD):
    if not isinstance(EVAL_PERIOD, str):
        sys.exit(f"The provided EVAL_PERIOD ('{EVAL_PERIOD}') is not a string."
                     + f" EVAL_PERIOD must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if re.search(r'[^A-Za-z0-9_\-\\]', EVAL_PERIOD):
        sys.exit(f"The provided EVAL_PERIOD string ('{EVAL_PERIOD}') contains"
                     + f" invalid characters. EVAL_PERIOD must be made of"
                     + f" alphanumeric characters, hyphen, and/or underscore."
                     + f" Check the plotting configuration file.")
        #sys.exit(1)
    if EVAL_PERIOD=="TEST":
        print(f"Since the EVAL_PERIOD is set to 'TEST', will use a"
                    + f" custom INIT/VALID period.")
    else:
        print(f"Since the EVAL_PERIOD is not set to 'TEST', will use a"
                    + f" preset INIT/VALID period (check ush/settings.py for"
                    + f" possible presets).")
    return EVAL_PERIOD


# VALID_BEG
# info case:
# warning case:
# error case: should be a string, if DATE_TYPE="VALID" or plot is valid_hour_average then should contain numbers only, should be YYYYMMDD format only, should be earlier than VALID_END, and cannot be blank 
def check_VALID_BEG(VALID_BEG, DATE_TYPE, EVAL_PERIOD, plot_type=None):
    if not isinstance(VALID_BEG, str):
        sys.exit(f"The provided VALID_BEG ('{VALID_BEG}') is not a string."
                     + f" VALID_BEG must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if ((str(DATE_TYPE).upper() == "VALID" 
                or str(plot_type).lower() == "valid_hour_average")
            and EVAL_PERIOD == "TEST"):
        if not VALID_BEG:
            sys.exit(f"The provided VALID_BEG is empty. Since DATE_TYPE is"
                         + f" '{str(DATE_TYPE).upper()}', plot_type is"
                         + f" '{str(plot_type).lower()}', and EVAL_PERIOD is"
                         + f" '{str(EVAL_PERIOD).upper()}', VALID_BEG cannot be"
                         + f" empty. Check the plotting configuration file.")
            #sys.exit(1)
        if not VALID_BEG.isdigit():
            sys.exit(f"The provided VALID_BEG ('{VALID_BEG}') contains"
                         + f" non-numeric characters. VALID_BEG may only"
                         + f" contain numeric characters. Check the plotting"
                         + f" configuration file.")
            #sys.exit(1)
        if not len(VALID_BEG) == 8:
            sys.exit(f"The provided VALID_BEG ('{VALID_BEG}') is too short"
                         + f" or too long.  VALID_BEG must be a date"
                         + f" in the form of YYYYMMDD. Check the plotting"
                         + f" configuration file.")
            #sys.exit(1)
    return VALID_BEG



# VALID_END
# info case:
# warning case:
# error case: should be a string, if DATE_TYPE="VALID" or plot is valid_hour_average then should contain numbers only, should be YYYYMMDD format only, should be later than VALID_BEG, and cannot be blank 
def check_VALID_END(VALID_END, DATE_TYPE, EVAL_PERIOD, plot_type=None):
    if not isinstance(VALID_END, str):
        sys.exit(f"The provided VALID_END ('{VALID_END}') is not a string."
                     + f" VALID_END must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if ((str(DATE_TYPE).upper() == "VALID" 
                or str(plot_type).lower() == "valid_hour_average")
            and EVAL_PERIOD == "TEST"):
        if not VALID_END:
            sys.exit(f"The provided VALID_END is empty. Since DATE_TYPE is"
                         + f" '{str(DATE_TYPE).upper()}', plot_type is"
                         + f" '{str(plot_type).lower()}', and EVAL_PERIOD is"
                         + f" '{str(EVAL_PERIOD).upper()}', VALID_END cannot be"
                         + f" empty. Check the plotting configuration file.")
            #sys.exit(1)
        if not VALID_END.isdigit():
            sys.exit(f"The provided VALID_END ('{VALID_END}') contains"
                         + f" non-numeric characters. VALID_END may only"
                         + f" contain numeric characters. Check the plotting"
                         + f" configuration file.")
            #sys.exit(1)
        if not len(VALID_END) == 8:
            sys.exit(f"The provided VALID_END ('{VALID_END}') is too short"
                         + f" or too long.  VALID_END must be a date"
                         + f" in the form of YYYYMMDD. Check the plotting"
                         + f" configuration file.")
            #sys.exit(1)
    return VALID_END


# INIT_BEG
# info case:
# warning case:
# error case: should be a string, if DATE_TYPE="INIT" then should contain numbers only, should be YYYYMMDD format only, should be earlier than INIT_END, and cannot be blank 
def check_INIT_BEG(INIT_BEG, DATE_TYPE, EVAL_PERIOD, plot_type=None):
    if not isinstance(INIT_BEG, str):
        sys.exit(f"The provided INIT_BEG ('{INIT_BEG}') is not a string."
                     + f" INIT_BEG must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if ((str(DATE_TYPE).upper() == "INIT" 
                or str(plot_type).lower() == "valid_hour_average")
            and EVAL_PERIOD == "TEST"):
        if not INIT_BEG:
            sys.exit(f"The provided INIT_BEG is empty. Since DATE_TYPE is"
                         + f" '{str(DATE_TYPE).upper()}', plot_type is"
                         + f" '{str(plot_type).lower()}', and EVAL_PERIOD is"
                         + f" '{str(EVAL_PERIOD).upper()}', INIT_BEG cannot be"
                         + f" empty. Check the plotting configuration file.")
            #sys.exit(1)
        if not INIT_BEG.isdigit():
            sys.exit(f"The provided INIT_BEG ('{INIT_BEG}') contains"
                         + f" non-numeric characters. INIT_BEG may only"
                         + f" contain numeric characters. Check the plotting"
                         + f" configuration file.")
            #sys.exit(1)
        if not len(INIT_BEG) == 8:
            sys.exit(f"The provided INIT_BEG ('{INIT_BEG}') is too short"
                         + f" or too long.  INIT_BEG must be a date"
                         + f" in the form of YYYYMMDD. Check the plotting"
                         + f" configuration file.")
            #sys.exit(1)
    return INIT_BEG


# INIT_END
# info case:
# warning case:
# error case: should be a string, if DATE_TYPE="INIT" then should contain numbers only, should be YYYYMMDD format only, should be later than INIT_BEG, and cannot be blank 
def check_INIT_END(INIT_END, DATE_TYPE, EVAL_PERIOD, plot_type=None):
    if not isinstance(INIT_END, str):
        sys.exit(f"The provided INIT_END ('{INIT_END}') is not a string."
                     + f" INIT_END must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if ((str(DATE_TYPE).upper() == "INIT" 
                or str(plot_type).lower() == "valid_hour_average")
            and EVAL_PERIOD == "TEST"):
        if not INIT_END:
            sys.exit(f"The provided INIT_END is empty. Since DATE_TYPE is"
                         + f" '{str(DATE_TYPE).upper()}', plot_type is"
                         + f" '{str(plot_type).lower()}', and EVAL_PERIOD is"
                         + f" '{str(EVAL_PERIOD).upper()}', INIT_END cannot be"
                         + f" empty. Check the plotting configuration file.")
            #sys.exit(1)
        if not INIT_END.isdigit():
            sys.exit(f"The provided INIT_END ('{INIT_END}') contains"
                         + f" non-numeric characters. INIT_END may only"
                         + f" contain numeric characters. Check the plotting"
                         + f" configuration file.")
            #sys.exit(1)
        if not len(INIT_END) == 8:
            sys.exit(f"The provided INIT_END ('{INIT_END}') is too short"
                         + f" or too long.  INIT_END must be a date"
                         + f" in the form of YYYYMMDD. Check the plotting"
                         + f" configuration file.")
            #sys.exit(1)
    return INIT_END

# FCST_INIT_HOUR
# info case:
# warning case:
# error case: should be a string, if DATE_TYPE="INIT" then should be a comma-separated list of numbers between and including  0 and 23 (leading zeros are fine), no symbols other than numbers, commas, and spaces, should not be blank
def check_FCST_INIT_HOUR(FCST_INIT_HOUR, DATE_TYPE, plot_type=None):
    if not isinstance(FCST_INIT_HOUR, str):
        sys.exit(f"The provided FCST_INIT_HOUR ('{FCST_INIT_HOUR}') is not a string."
                     + f" FCST_INIT_HOUR must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if (str(DATE_TYPE).upper() == "INIT" 
            or str(plot_type).lower() == "valid_hour_average"):
        if not FCST_INIT_HOUR:
            sys.exit(f"The provided FCST_INIT_HOUR is empty. Since DATE_TYPE is"
                         + f" '{str(DATE_TYPE).upper()}' and plot type is"
                         + f" '{str(plot_type).lower()}', FCST_INIT_HOUR cannot be"
                         + f" empty. Check the plotting configuration file.")
            #sys.exit(1)
        if not re.search(r'(^[ 0-9,]+)$', FCST_INIT_HOUR):
            sys.exit(f"The provided FCST_INIT_HOUR ('{FCST_INIT_HOUR}') is"
                         + f" not valid. FCST_INIT_HOUR may contain numbers,"
                         + f" commas, and spaces only. Check the plotting"
                         + f" configuration file.")
        #sys.exit(1)
    return FCST_INIT_HOUR

# FCST_VALID_HOUR
# info case:
# warning case:
# error case: should be a string, if DATE_TYPE="VALID" then should be a comma-separated list of numbers between and including  0 and 23 (leading zeros are fine), no symbols other than numbers, commas, and spaces, should not be blank
def check_FCST_VALID_HOUR(FCST_VALID_HOUR, DATE_TYPE, plot_type=None):
    if not isinstance(FCST_VALID_HOUR, str):
        sys.exit(f"The provided FCST_VALID_HOUR ('{FCST_VALID_HOUR}') is not a string."
                     + f" FCST_VALID_HOUR must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if (str(DATE_TYPE).upper() == "VALID" 
            or str(plot_type).lower() == "valid_hour_average"):
        if not FCST_VALID_HOUR:
            sys.exit(f"The provided FCST_VALID_HOUR is empty. Since DATE_TYPE is"
                         + f" '{str(DATE_TYPE).upper()}' and plot type is"
                         + f" '{str(plot_type).lower()}', FCST_VALID_HOUR cannot be"
                         + f" empty. Check the plotting configuration file.")
            #sys.exit(1)
        if not re.search(r'(^[ 0-9,]+)$', FCST_VALID_HOUR):
            sys.exit(f"The provided FCST_VALID_HOUR ('{FCST_VALID_HOUR}') is"
                         + f" not valid. FCST_VALID_HOUR may contain numbers,"
                         + f" commas, and spaces only. Check the plotting"
                         + f" configuration file.")
        #sys.exit(1)
    return FCST_VALID_HOUR

# FCST_LEVEL
# info case:
# warning case: should be a valid level (start with a valid letter)
# error case: should be a string, should not be blank
def check_FCST_LEVEL(FCST_LEVEL):
    if not isinstance(FCST_LEVEL, str):
        sys.exit(f"The provided FCST_LEVEL ('{FCST_LEVEL}') is not a string."
                     + f" FCST_LEVEL must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if not FCST_LEVEL:
        sys.exit(f"The provided FCST_LEVEL is empty. FCST_LEVEL cannot be"
                     + f" empty. Check the plotting configuration file.")
        #sys.exit(1)
    return FCST_LEVEL

# OBS_LEVEL
# info case: whether or not OBS_LEVEL matches FCST_LEVEL
# warning case: should be a valid level (start with a valid letter)
# error case: should be a string, should not be blank
def check_OBS_LEVEL(OBS_LEVEL):
    if not isinstance(OBS_LEVEL, str):
        sys.exit(f"The provided OBS_LEVEL ('{OBS_LEVEL}') is not a string."
                     + f" OBS_LEVEL must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if not OBS_LEVEL:
        sys.exit(f"The provided OBS_LEVEL is empty. OBS_LEVEL cannot be"
                     + f" empty. Check the plotting configuration file.")
        #sys.exit(1)
    return OBS_LEVEL

# var_name
# info case:
# warning case:
# error case: should be a string, should not be blank
def check_var_name(var_name):
    if not isinstance(var_name, str):
        sys.exit(f"The provided var_name ('{var_name}') is not a string."
                     + f" var_name must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if not var_name:
        sys.exit(f"The provided var_name is empty. var_name cannot be"
                     + f" empty. Check the plotting configuration file.")
        #sys.exit(1)
    if re.search(r'[^ A-Za-z0-9,_\-]', var_name):
        sys.exit(f"The provided var_name string ('{var_name}') contains"
                     + f" invalid characters. var_name must be made of"
                     + f" alphanumeric characters, hyphen, underscore, commas"
                     + f" and/or spaces only. Check the plotting configuration"
                     + f" file.")
        #sys.exit(1)
    return var_name

# VX_MASK_LIST
# info case:
# warning case: 
# error case: should be a string, should not be blank
def check_VX_MASK_LIST(VX_MASK_LIST):
    if not isinstance(VX_MASK_LIST, str):
        sys.exit(f"The provided VX_MASK_LIST ('{VX_MASK_LIST}') is not a string."
                     + f" VX_MASK_LIST must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if not VX_MASK_LIST:
        sys.exit(f"The provided VX_MASK_LIST is empty. VX_MASK_LIST cannot be"
                     + f" empty. Check the plotting configuration file.")
        #sys.exit(1)
    if re.search(r'[^ A-Za-z0-9,_\-]', VX_MASK_LIST):
        sys.exit(f"The provided VX_MASK_LIST string ('{VX_MASK_LIST}') contains"
                     + f" invalid characters. VX_MASK_LIST must be made of"
                     + f" alphanumeric characters, hyphen, underscore, commas"
                     + f" and/or spaces only. Check the plotting configuration"
                     + f" file.")
        #sys.exit(1)
    return VX_MASK_LIST

# FCST_LEAD
# info case:
# warning case:
# error case: should be a string, should not be blank, should be a comma-separated list of positive numbers 
def check_FCST_LEAD(FCST_LEAD):
    if not isinstance(FCST_LEAD, str):
        sys.exit(f"The provided FCST_LEAD ('{FCST_LEAD}') is not a string."
                     + f" FCST_LEAD must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if not FCST_LEAD:
        sys.exit(f"The provided FCST_LEAD is empty. FCST_LEAD cannot be"
                     + f" empty. Check the plotting configuration file.")
        #sys.exit(1)
    if re.search(r'[^ 0-9,]', FCST_LEAD):
        sys.exit(f"The provided FCST_LEAD string ('{FCST_LEAD}') contains"
                     + f" invalid characters. FCST_LEAD must be made of"
                     + f" numerics, commas and/or spaces only. Check the"
                     + f" plotting configuration file.")
        #sys.exit(1)
    return FCST_LEAD

# LINE_TYPE
# info case:
# warning case: should matcha known line type
# error case: should be a string, should not be blank
def check_LINE_TYPE(LINE_TYPE):
    if not isinstance(LINE_TYPE, str):
        sys.exit(f"The provided LINE_TYPE ('{LINE_TYPE}') is not a string."
                     + f" LINE_TYPE must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if not LINE_TYPE:
        sys.exit(f"The provided LINE_TYPE is empty. LINE_TYPE cannot be"
                     + f" empty. Check the plotting configuration file.")
        #sys.exit(1)
    if re.search(r'[^ A-Za-z0-9]', LINE_TYPE):
        sys.exit(f"The provided LINE_TYPE string ('{LINE_TYPE}') contains"
                     + f" invalid characters. LINE_TYPE must be made of"
                     + f" alphanumeric characters only. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    return LINE_TYPE

# INTERP
# info case:
# warning case: should match a known interp
# error case: should be a string, should not be blank
def check_INTERP(INTERP):
    if not isinstance(INTERP, str):
        sys.exit(f"The provided INTERP ('{INTERP}') is not a string."
                     + f" INTERP must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if not INTERP:
        sys.exit(f"The provided INTERP is empty. INTERP cannot be"
                     + f" empty. Check the plotting configuration file.")
        #sys.exit(1)
    if re.search(r'[^A-Za-z0-9_\-]', INTERP):
        sys.exit(f"The provided INTERP string ('{INTERP}') contains"
                     + f" invalid characters. INTERP must be made of"
                     + f" alphanumeric characters, hyphens, and/or underscores"
                     + f" only. Check the plotting configuration file.")
        #sys.exit(1)
    return INTERP

# FCST_THRESH
# info case:
# warning case:
# error case: should be a string, if line type is CTC, MCTC, PCT, NBRCTC then should not be blank, should contain comma-separated list of symbols and numbers, symbols should precede numbers, symbols should be either >,>=,<,<=,==,!=
def check_FCST_THRESH(FCST_THRESH, LINE_TYPE):
    if not isinstance(FCST_THRESH, str):
        sys.exit(f"The provided FCST_THRESH ('{FCST_THRESH}') is not a"
                     + f" string. FCST_THRESH must be a string. Check the"
                     + f" plotting configuration file.")
        #sys.exit(1)
    if str(LINE_TYPE).upper() in ['CTC','MCTC','PCT','NBRCTC']:
        if not FCST_THRESH:
            sys.exit(f"The provided FCST_THRESH is empty. Since the"
                         + f" provided line type is '{LINE_TYPE}', FCST_THRESH"
                         + f" cannot be empty. Check the plotting"
                         + f" configuration file.")
            #sys.exit(1)
        if re.search(r'[^A-Za-z0-9<>=.,! /-]', FCST_THRESH):
            sys.exit(f"The provided FCST_THRESH string ('{FCST_THRESH}') contains"
                         + f" invalid characters. FCST_THRESH must be made of"
                         + f" alphanumeric characters, comparison operators,"
                         + f" periods, hyphens, commas and/or spaces only. Check the"
                         + f" plotting configuration file.")
            #sys.exit(1)
        if re.search(r'^((?![<=!>]).)*$', FCST_THRESH):
            sys.exit(f"The provided FCST_THRESH string ('{FCST_THRESH}')"
                         + f" does not contain a valid comparison operator"
                         + f" (<,>,<=,>=,!=,==). FCST_THRESH must contain a"
                         + f" valid comparison operator.  Check the plotting"
                         + f" configuration file.")
            #sys.exit(1)
        if re.search(r'^((?![0-9]).)*$', FCST_THRESH):
            sys.exit(f"The provided FCST_THRESH string ('{FCST_THRESH}')"
                         + f" contains no numerics (digits 0-9). FCST_THRESH"
                         + f" must contain an integer or decimal in order to"
                         + f" be valid.  Check the plotting configuration"
                         + f" file.")
            #sys.exit(1)
    return FCST_THRESH

# OBS_THRESH
# info case:
# warning case: whether or not it matches FCST_THRESH
# error case: should be a string, if line type is CTC, MCTC, PCT, NBRCTC then should not be blank, should contain comma-separated list of symbols and numbers, symbols should precede numbers, symbols should be either >,>=,<,<=,==,!=
def check_OBS_THRESH(OBS_THRESH, FCST_THRESH, LINE_TYPE):
    if not isinstance(OBS_THRESH, str):
        sys.exit(f"The provided OBS_THRESH ('{OBS_THRESH}') is not a"
                     + f" string. OBS_THRESH must be a string. Check the"
                     + f" plotting configuration file.")
        #sys.exit(1)
    if str(LINE_TYPE).upper() in ['CTC','MCTC','PCT','NBRCTC']:
        if not OBS_THRESH:
            sys.exit(f"The provided OBS_THRESH is empty. Since the"
                         + f" provided line type is '{LINE_TYPE}', OBS_THRESH"
                         + f" cannot be empty. Check the plotting"
                         + f" configuration file.")
            #sys.exit(1)
        if re.search(r'[^A-Za-z0-9<>=.,! /-]', OBS_THRESH):
            sys.exit(f"The provided OBS_THRESH string ('{OBS_THRESH}') contains"
                         + f" invalid characters. OBS_THRESH must be made of"
                         + f" alphanumeric characters, comparison operators,"
                         + f" periods, hyphens, commas and/or spaces only. Check the"
                         + f" plotting configuration file.")
            #sys.exit(1)
        if re.search(r'^((?![<=!>]).)*$', OBS_THRESH):
            sys.exit(f"The provided OBS_THRESH string ('{OBS_THRESH}')"
                         + f" does not contain a valid comparison operator"
                         + f" (<,>,<=,>=,!=,==). OBS_THRESH must contain a"
                         + f" valid comparison operator.  Check the plotting"
                         + f" configuration file.")
            #sys.exit(1)
        if re.search(r'^((?![0-9]).)*$', OBS_THRESH):
            sys.exit(f"The provided OBS_THRESH string ('{OBS_THRESH}')"
                         + f" contains no numerics (digits 0-9). OBS_THRESH"
                         + f" must contain an integer or decimal in order to"
                         + f" be valid.  Check the plotting configuration"
                         + f" file.")
            #sys.exit(1)
        if (OBS_THRESH.replace(' ','') != FCST_THRESH.replace(' ','')
                or len(re.split(r'[\s,]+', OBS_THRESH)) 
                != len(re.split(r'[\s,]+', FCST_THRESH))):
            print(f"WARNING: The provided OBS_THRESH string ('{OBS_THRESH}')"
                           + f" is not equivalent to the provided FCST_THRESH"
                           + f" string ('{FCST_THRESH}').")
    return OBS_THRESH

# STATS
# info case:
# warning case:
# error case: should be a string, should not be blank, 
def check_STATS(STATS):
    if not isinstance(STATS, str):
        sys.exit(f"The provided STATS ('{STATS}') is not a string."
                     + f" STATS must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if not STATS:
        sys.exit(f"The provided STATS is empty. STATS cannot be"
                     + f" empty. Check the plotting configuration file.")
        #sys.exit(1)
    if re.search(r'[^ A-Za-z0-9,_\-]', STATS):
        sys.exit(f"The provided STATS string ('{STATS}') contains"
                     + f" invalid characters. STATS must be made of"
                     + f" alphanumeric characters, hyphen, underscore, commas"
                     + f" and/or spaces only. Check the plotting configuration"
                     + f" file.")
        #sys.exit(1)
    return STATS

# CONFIDENCE_INTERVALS
# info case:
# warning case: should not be blank
# error case: should be a string
def check_CONFIDENCE_INTERVALS(CONFIDENCE_INTERVALS):
    if not isinstance(CONFIDENCE_INTERVALS, str):
        sys.exit(f"The provided CONFIDENCE_INTERVALS ('{CONFIDENCE_INTERVALS}') is not a string."
                     + f" CONFIDENCE_INTERVALS must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if not CONFIDENCE_INTERVALS:
        print(f"WARNING: The provided CONFIDENCE_INTERVALS is empty."
                       + f" Confidence intervals will not be plotted. Set to"
                       + f" 'True' if confidence intervals should be plotted.")
    return CONFIDENCE_INTERVALS

# INTERP_PTS
# info case:
# warning case: 
# error case: should be a string, should be a comma-separated list of positive numbers 
def check_INTERP_PTS(INTERP_PTS):
    if not isinstance(INTERP_PTS, str):
        sys.exit(f"The provided INTERP_PTS ('{INTERP_PTS}') is not a string."
                     + f" INTERP_PTS must be a string. Check the plotting"
                     + f" configuration file.")
        #sys.exit(1)
    if re.search(r'[^ 0-9,]', INTERP_PTS):
        sys.exit(f"The provided INTERP_PTS string ('{INTERP_PTS}') contains"
                     + f" invalid characters. INTERP_PTS must be made of"
                     + f" numerics, commas and/or spaces only. Check the"
                     + f" plotting configuration file.")
        #sys.exit(1)
    return INTERP_PTS
