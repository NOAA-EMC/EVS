#!/bin/bash

##################################################################################
# Name of Script: evs_cam_plots_radar.sh
# Contact(s):     Marcel G. Caron (marcel.caron@noaa.gov)
# Purpose of Script: This script runs METplus to generate radar
#                    verification graphics for deterministic and ensemble CAMs.
##################################################################################


set -x

export PLOT_TYPE="$1"
export DOMAIN="$2"
export var_name="$3"
export LINE_TYPE="$4"
export FCST_INIT_HOUR="$5"
export VX_MASK_LIST="$6"
export FCST_THRESH="$7" 
export JOBNUM="$8"
export job_name="job${JOBNUM}"

export OBS_THRESH=${FCST_THRESH}

export SAVE_DIR=${DATA}/out/workdirs/${job_name}
export LOG_DIR=${SAVE_DIR}/logs
export LOG_TEMPLATE="${LOG_DIR}/EVS_verif_plotting_${job_name}_$($NDATE)_$$.out"


###################################################################
# Set some additional variables based on job arguments
###################################################################

if [ $DOMAIN = conus ]; then

   export NBR_WIDTH=17
   export INTERP_PNTS=289

elif [ $DOMAIN = alaska ]; then

   export NBR_WIDTH=27
   export INTERP_PNTS=729

fi


if [ $var_name = REFC ]; then

   export FCST_LEVEL="L0"
   export OBS_LEVEL="Z500"

elif [ $var_name = RETOP ]; then

   export FCST_LEVEL="L0"
   export OBS_LEVEL="Z500"

fi


if [ $LINE_TYPE = nbrcnt ] || [ $LINE_TYPE = nbrctc ]; then
   export INTERP="NBRHD_SQUARE"
fi


###################################################################
# Run python scripts for the specified plot type 
###################################################################

if [[ -f "${RESTART_DIR}/${COMPLETED_JOBS_DIR}/${job_name}" ]]; then
    echo "NOTE: Jobs were restarted and ${job_name} has already completed.  Continuing."
else
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

       fi

    elif [ $PLOT_TYPE = lead_average ]; then

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

    fi
    python -c "import sys; sys.path.insert(0, '${USHevs}/${COMPONENT}'); import cam_util; cam_util.mark_job_completed('${RESTART_DIR}', '${DATA}', '${VERIF_CASE}', '${COMPLETED_JOBS_DIR}', '${job_name}')"

fi

exit
