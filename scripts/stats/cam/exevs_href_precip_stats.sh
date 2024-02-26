#!/bin/ksh
###################################################################
# Purpose:   Setup some paths and run href precip stat ush scripts
#
# Last updated 10/30/2023: by  Binbin Zhou, Lynker@EMC/NCEP
###################################################################

set -x
export machine=${machine:-"WCOSS2"}

#*************************************
#check input data are available:
#*************************************
source $USHevs/cam/evs_check_href_files.sh
export err=$?; err_chk

export WORK=$DATA
cd $WORK

export run_mpi=${run_mpi:-'yes'}
export verif_precip=${verif_precip:-'yes'}
export verif_snowfall=${verif_snowfall:-'yes'}
if [ "$verif_precip" = "no" ] && [ "$verif_snowfall" = "no" ] ; then
    export prepare='no'
fi
export prepare=${prepare:-'yes'}
export gather=${gather:-'yes'}
export verify='precip'

export COMHREF=$COMINhref
export COMCCPA=$COMINccpa
export COMSNOW=$DCOMINsnow
export COMMRMS=$DCOMINmrms

export PRECIP_CONF=$PARMevs/metplus_config/$STEP/$COMPONENT/precip
export SNOWFALL_CONF=$PARMevs/metplus_config/$STEP/$COMPONENT/snowfall
export GATHER_CONF_PRECIP=$PRECIP_CONF
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS
export vday=$VDATE


#**********************************
# Prepare CCPA data for validation
#**********************************
if [ $prepare = yes ] ; then
 for precip in ccpa01h03h ccpa24h apcp24h_conus  apcp24h_alaska mrms ; do
  $USHevs/cam/evs_href_prepare.sh  $precip
  export err=$?; err_chk
 done
fi

#***************************************
# Build a POE script to collect sub-jobs
# **************************************
> run_all_precip_poe.sh

# Build sub-jobs for precip
if [ $verif_precip = yes ] ; then
 $USHevs/cam/evs_href_precip.sh
 export err=$?; err_chk
 cat ${DATA}/run_all_href_precip_poe.sh >> run_all_precip_poe.sh
fi

# Build sub-jobs for snowfall
if [ $verif_snowfall = yes ] ; then
 source $USHevs/cam/evs_href_snowfall.sh
 export err=$?; err_chk
 cat ${DATA}/run_all_href_snowfall_poe.sh >> run_all_precip_poe.sh
fi

#*************************************************
# Run the POE script to generate small stat files
#*************************************************
if [ -s ${DATA}/run_all_precip_poe.sh ]  ; then
  chmod 775 run_all_precip_poe.sh

  if [ $run_mpi = yes ] ; then
    mpiexec  -n 44 -ppn 44 --cpu-bind core --depth=2 cfp ${DATA}/run_all_precip_poe.sh
    export err=$?; err_chk
  else
   ${DATA}/run_all_precip_poe.sh
    export err=$?; err_chk
  fi

fi


#******************************************************************
# Run gather job to combine the small stats to form a big stat file
#******************************************************************
if [ "$verif_precip" = "no" ] && [ "$verif_snowfall" = "no" ] ; then
    export gather='no'
fi
if [ $gather = yes ] ; then
  $USHevs/cam/evs_href_gather.sh precip
  export err=$?; err_chk
fi

# Cat the METplus log files
log_dirs1="$DATA/*/logs"
log_dirs2="$DATA/precip/*/logs"
for log_dir in $log_dirs1; do
    if [ -d $log_dir ]; then
        log_file_count=$(find $log_dir -type f | wc -l)
        if [[ $log_file_count -ne 0 ]]; then
            log_files=("$log_dir"/*)
            for log_file in "${log_files[@]}"; do
                if [ -f "$log_file" ]; then
                    echo "Start: $log_file"
                    cat "$log_file"
                    echo "End: $log_file"
                fi
            done
        fi
    fi
done
for log_dir in $log_dirs2; do
    if [ -d $log_dir ]; then
        log_file_count=$(find $log_dir -type f | wc -l)
        if [[ $log_file_count -ne 0 ]]; then
            log_files=("$log_dir"/*)
            for log_file in "${log_files[@]}"; do
                if [ -f "$log_file" ]; then
                    echo "Start: $log_file"
                    cat "$log_file"
                    echo "End: $log_file"
                fi
            done
        fi
    fi
done

export err=$?; err_chk
