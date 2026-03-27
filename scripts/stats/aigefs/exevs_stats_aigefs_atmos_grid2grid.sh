#!/bin/ksh
#************************************************************************************
# Purpose: 1. Set up environment parameters for grid2grid job that are not
#             defined in stats J-job 
#          2. Run grid2grid verification for:
#             (1) upper air fields grid2grid verification for gefs, aigefs, and hgefs
#             (2) precip verification for gefs, aigefs, and hgefs
#
# Updated: 10/14/2025 by L. Gwen Chen (lichuan.chen@noaa.gov)
#************************************************************************************
set -x

export WORK=$DATA
cd $WORK

export CLIMO=$FIXevs/climos/atmos
export MASKS=$FIXevs/masks

export ENS_LIST=$PARMevs/metplus_config/prep/${COMPONENT}/${RUN}_grid2grid
export GRID2GRID_CONF=$PARMevs/metplus_config/${STEP}/${COMPONENT}/${RUN}_grid2grid
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS

export run_mpi=${run_mpi:-'yes'}
export gather=${gather:-'yes'}

export vday=$1
ens=$2 
verif_case=$3

export gefs_number=30
export aigefs_number=31
export hgefs_number=62

if [ $verif_case = upper ] ; then
     if [ ! -s ${EVSIN}.${VDATE}/gefs/gfsanl.t00z.grid3.f000.grib2 ] ; then
        if [ $SENDMAIL = YES ]; then
          export subject="GFS analysis data missing"
          echo "Warning: No GFS analysis available for ${VDATE}" > mailmsg 
          echo "Missing file is ${EVSIN}.${VDATE}/gefs/gfsanl.t00z.grid3.f000.grib2" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
        fi
     else
        echo "All $ens $verif_case validation data are available, continuing ..."
        $USHevs/${COMPONENT}/evs_${COMPONENT}_atmos_grid2grid.sh $ens ${verif_case}
        export err=$?; err_chk
     fi
fi

if [ $verif_case = precip ] ; then
      if [ ! -s ${EVSIN}.${VDATE}/gefs/ccpa.t12z.grid3.24h.f00.nc ] ; then
        if [ $SENDMAIL = YES ]; then
          export subject="24h CCPA data missing"
          echo "Warning: No 24h CCPA data available for ${VDATE}" > mailmsg
          echo "Missing file is ${EVSIN}.${VDATE}/gefs/ccpa.t12z.grid3.24h.f00.nc" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
	fi
      else
        echo "All $verif_case validation data are available, continuing ..."
        $USHevs/${COMPONENT}/evs_${COMPONENT}_atmos_grid2grid.sh $ens $verif_case
        export err=$?; err_chk
      fi
fi 

