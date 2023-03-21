#!/bin/bash

set -x

if [ ${VAR_NAME} = "HGT" ]; then
  export FCST_VAR1_NAME="HGT"
  export FCST_VAR1_LEVELS="P1000, P925, P850, P700, P500, P400, P300, P250, P200, P150, P100, P50, P20, P10"
  export OBS_VAR1_NAME="HGT"
  export OBS_VAR1_LEVELS="P1000, P925, P850, P700, P500, P400, P300, P250, P200, P150, P100, P50, P20, P10"
  
  # 'CTC': 'NONE',; # 'SL1L2': 'STAT',; # 'VL1L2': 'NONE',; # 'CNT': 'NONE',
fi

if [ ${VAR_NAME} = "TMP" ]; then
  export FCST_VAR1_NAME="TMP"
  export FCST_VAR1_LEVELS="P1000, P925, P850, P700, P500, P400, P300, P250, P200, P150, P100, P50, P20, P10"
  export OBS_VAR1_NAME="TMP"
  export OBS_VAR1_LEVELS="P1000, P925, P850, P700, P500, P400, P300, P250, P200, P150, P100, P50, P20, P10"

  # 'CTC': 'NONE',; # 'SL1L2': 'STAT',; # 'VL1L2': 'NONE',; # 'CNT': 'NONE',
fi


if [ ${VAR_NAME} = "UGRD" ]; then
  export FCST_VAR1_NAME="UGRD"
  export FCST_VAR1_LEVELS="P1000, P925, P850, P700, P500, P400, P300, P250, P200, P150, P100, P50, P20, P10"
  export OBS_VAR1_NAME="UGRD"
  export OBS_VAR1_LEVELS="P1000, P925, P850, P700, P500, P400, P300, P250, P200, P150, P100, P50, P20, P10"
  
  #     'CTC': 'NONE',;   #     'SL1L2': 'STAT',;   #     'VL1L2': 'NONE',;   #     'CNT': 'NONE',
fi

if [ ${VAR_NAME} = "VGRD" ]; then
  export FCST_VAR1_NAME="VGRD"
  export FCST_VAR1_LEVELS="P1000, P925, P850, P700, P500, P400, P300, P250, P200, P150, P100, P50, P20, P10"
  export OBS_VAR1_NAME="VGRD"
  export OBS_VAR1_LEVELS="P1000, P925, P850, P700, P500, P400, P300, P250, P200, P150, P100, P50, P20, P10"
  
  #     'CTC': 'NONE',;   #     'SL1L2': 'STAT',;   #     'VL1L2': 'NONE',;   #     'CNT': 'NONE',
fi


if [ ${VAR_NAME} = "UGRD_VGRD" ]; then
  export FCST_VAR1_NAME="UGRD"
  export FCST_VAR1_LEVELS="P1000, P925, P850, P700, P500, P400, P300, P250, P200, P150, P100, P50, P20, P10"
  export OBS_VAR1_NAME="UGRD"
  export OBS_VAR1_LEVELS="P1000, P925, P850, P700, P500, P400, P300, P250, P200, P150, P100, P50, P20, P10"
  
  export FCST_VAR2_NAME="VGRD"
  export FCST_VAR1_LEVELS="P1000, P925, P850, P700, P500, P400, P300, P250, P200, P150, P100, P50, P20, P10"
  export OBS_VAR2_NAME="VGRD"
  export OBS_VAR1_LEVELS="P1000, P925, P850, P700, P500, P400, P300, P250, P200, P150, P100, P50, P20, P10"
  
  #     'CTC': 'NONE',;   #     'SL1L2': 'NONE',;   #     'VL1L2': 'STAT',;   #     'CNT': 'NONE',
fi


if [ ${VAR_NAME} = "SPFH" ]; then
  export FCST_VAR1_NAME="SPFH"
  export FCST_VAR1_LEVELS="P1000, P925, P850, P700, P500, P400, P300, P250, P200, P150, P100, P50, P20, P10"
  export FCST_VAR1_OPTIONS="set_attr_units = \\"g/kg\\"; convert(x)=x*1000"
  export OBS_VAR1_NAME="SPFH"
  export OBS_VAR1_LEVELS="P1000, P925, P850, P700, P500, P400, P300, P250, P200, P150, P100, P50, P20, P10"
  export OBS_VAR1_OPTIONS="set_attr_units = \\"g/kg\\"; convert(x)=x*1000"
  
  #     'CTC': 'NONE',;   #     'SL1L2': 'STAT',;   #     'VL1L2': 'NONE',;   #     'CNT': 'NONE',
fi

