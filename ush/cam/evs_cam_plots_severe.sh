#!/bin/bash

##################################################################################
# Name of Script: evs_cam_plots_severe.sh
# Contact(s):     Marcel G. Caron (marcel.caron@noaa.gov)
# Purpose of Script: This script runs METplus to generate severe
#                    verification graphics for deterministic and ensemble CAMs.
##################################################################################


set -x

export PLOT_TYPE=$1
export DOMAIN=$2
export LINE_TYPE=$3
export FCST_INIT_HOUR=$4
export FCST_LEAD=$5
export JOBNUM=$6
export job_name="job${JOBNUM}"

export SAVE_DIR=${DATA}/out/workdirs/job${JOBNUM}
export LOG_DIR=${SAVE_DIR}/logs
export LOG_TEMPLATE="${LOG_DIR}/EVS_verif_plotting_job${JOBNUM}_$($NDATE)_$$.out"


###################################################################
# Set some additional variables based on job arguments
###################################################################

if [ $DOMAIN = conus ]; then

   export NBR_WIDTH=1
   export INTERP_PNTS=1
   export VX_MASK_LIST="CONUS"

fi

export var_name="Prob_MXUPHL25_A24_geHWT"
export FCST_THRESHs=">=0.02 >=0.05 >=0.10 >=0.15 >=0.30 >=0.45 >=0.60"
export FCST_THRESH=">=0.02,>=0.05,>=0.10,>=0.15,>=0.30,>=0.45,>=0.60"
export FCST_LEVEL="A1"

export OBS_LEVEL="*,*"


if [ $LINE_TYPE = nbrcnt ] || [ $LINE_TYPE = nbrctc ]; then

   export INTERP="NBRHD_SQUARE"
   export OBS_THRESH=">=0.02,>=0.05,>=0.10,>=0.15,>=0.30,>=0.45,>=0.60"

elif [ $LINE_TYPE = pstd ]; then

   export INTERP="NEAREST"
   export OBS_THRESH=">=1.0"

fi




###################################################################
# Run python scripts for the specified plot type 
###################################################################

if [ $PLOT_TYPE = performance_diagram ]; then

   export STATS="sratio,pod,csi"
   python ${USHevs}/${COMPONENT}/${PLOT_TYPE}.py
   export err=$?; err_chk

elif [ $PLOT_TYPE = threshold_average ]; then

   if [ $LINE_TYPE = nbrcnt ]; then

      export STATS="fss"
      python ${USHevs}/${COMPONENT}/${PLOT_TYPE}.py
      export err=$?; err_chk

   elif [ $LINE_TYPE = nbrctc ]; then

      export STATS="csi"
      python ${USHevs}/${COMPONENT}/${PLOT_TYPE}.py
      export err=$?; err_chk

      export STATS="fbias"
      python ${USHevs}/${COMPONENT}/${PLOT_TYPE}.py
      export err=$?; err_chk

   elif [ $LINE_TYPE = pstd ]; then

      export STATS="bss_smpl"
      python ${USHevs}/${COMPONENT}/${PLOT_TYPE}.py
      export err=$?; err_chk

      export STATS="bs"
      python ${USHevs}/${COMPONENT}/${PLOT_TYPE}.py
      export err=$?; err_chk

   fi

elif [ $PLOT_TYPE = lead_average ]; then

   if [ $LINE_TYPE = pstd ]; then

      export STATS="bss_smpl"
      python ${USHevs}/${COMPONENT}/${PLOT_TYPE}.py
      export err=$?; err_chk

      export STATS="bs"
      python ${USHevs}/${COMPONENT}/${PLOT_TYPE}.py
      export err=$?; err_chk

   else

      for FCST_THRESH in ${FCST_THRESHs}; do

         OBS_THRESH=${FCST_THRESH}

         if [ $LINE_TYPE = nbrcnt ]; then

            export STATS="fss"
            python ${USHevs}/${COMPONENT}/${PLOT_TYPE}.py
            export err=$?; err_chk

         elif [ $LINE_TYPE = nbrctc ]; then

            export STATS="csi"
            python ${USHevs}/${COMPONENT}/${PLOT_TYPE}.py
            export err=$?; err_chk

            export STATS="fbias"
            python ${USHevs}/${COMPONENT}/${PLOT_TYPE}.py
            export err=$?; err_chk
         fi

      done
   
   fi

fi


exit
