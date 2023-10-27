#!/bin/ksh
set -x

#check input data are available:
$USHevs/cam/evs_check_href_files.sh

export WORK=$DATA
cd $WORK

export run_mpi=${run_mpi:-'yes'}
export prepare=${prepare:-'yes'}
export verif_precip=${verif_precip:-'yes'}
export verif_snowfall=${verif_snowfall:-'yes'}
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


msg="$job HAS BEGUN"
postmsg "$jlogfile" "$msg"


if [ $prepare = yes ] ; then
 for precip in ccpa01h03h ccpa24h apcp24h_conus  apcp24h_alaska mrms ; do
  $USHevs/cam/evs_href_preppare.sh  $precip
 done
fi


> run_all_precip_poe.sh
if [ $verif_precip = yes ] ; then
 $USHevs/cam/evs_href_precip.sh
 cat ${DATA}/run_all_href_precip_poe.sh >> run_all_precip_poe.sh
fi

if [ $verif_snowfall = yes ] ; then
 $USHevs/cam/evs_href_snowfall.sh
 cat ${DATA}/run_all_href_snowfall_poe.sh >> run_all_precip_poe.sh
fi


if [ -s ${DATA}/run_all_precip_poe.sh ]  ; then
  chmod 775 run_all_precip_poe.sh

  if [ $run_mpi = yes ] ; then
    mpiexec  -n 44 -ppn 44 --cpu-bind core --depth=2 cfp ${DATA}/run_all_precip_poe.sh
  else
   ${DATA}/run_all_precip_poe.sh
  fi

fi

if [ $gather = yes ] ; then
  $USHevs/cam/evs_href_gather.sh precip
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

msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$jlogfile" "$msg"



exit 0
