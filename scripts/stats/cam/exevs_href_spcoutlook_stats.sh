#!/bin/ksh
##############################################################
# Purpose:   Setup some paths and run href spcoutlook job
# 
# Last updated 10/30/2023: by  Binbin Zhou, Lynker@EMC/NCEP
##############################################################
set -x


export machine=${machine:-"WCOSS2"}
export WORK=$DATA
cd $WORK

#*********************************
#check input data are available:
#*********************************
source $USHevs/cam/evs_check_href_files.sh 
export err=$?; err_chk

#lvl = profile or sfc or both
export lvl='both'

#  verify_all = yes:  verify both profile and sfc (system + product)
#  if lvl is not both, verify_all = no
export verify_all=${verify_all:-'yes'}

export prepare='yes'
export verif_system='yes'
export verif_profile='yes'
export verif_product='yes'
export verif_spcoutlook='yes'
export gather=${gather:-'yes'}
export verify=$VERIF_CASE
export run_mpi=${run_mpi:-'yes'}

export COMHREF=$COMINhref
export PREPBUFR=$COMINobsproc

export GATHER_CONF_PRECIP=$PRECIP_CONF
export GRID2OBS_CONF=$PARMevs/metplus_config/$STEP/$COMPONENT/grid2obs
export GATHER_CONF_GRID2OBS=$GRID2OBS_CONF
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS
export vday=$VDATE

#Define the spc outlook reqions mask file path
export SPCoutlookMask=$EVSINspcotlk/$MODELNAME/spc.$VDATE



#  domain = conus or alaska or all
export domain="all"
#export domain="HI"

#*********************************
# Prepare prepbufr data files
# ********************************
if [ $prepare = yes ] ; then
  $USHevs/cam/evs_href_prepare.sh prepbufr CONUS
  export err=$?; err_chk
fi 

#****************************************
# Build a POE script to collect sub-jobs
# ***************************************
>run_href_all_grid2obs_poe

#Spc_outlook: 2 job
if [ $verif_spcoutlook = yes ] ; then
  $USHevs/cam/evs_href_spcoutlook.sh
  export err=$?; err_chk
  cat ${DATA}/run_all_href_spcoutlook_poe.sh >> run_href_all_grid2obs_poe
fi

chmod 775 run_href_all_grid2obs_poe

#****************************************
# Run POE script to get small stat files
# ***************************************
if [ $run_mpi = yes ] ; then
    mpiexec -np 4 -ppn 4 --cpu-bind verbose,core cfp  ${DATA}/run_href_all_grid2obs_poe
    export err=$?; err_chk
else
    ${DATA}/run_href_all_grid2obs_poe
    export err=$?; err_chk

fi

#*******************************************************************
# Run gather job to combine small stat files to form a big stat file
# ******************************************************************
if [ $gather = yes ] && [ -s ${DATA}/run_href_all_grid2obs_poe ] ; then
  $USHevs/cam/evs_href_gather.sh $VERIF_CASE  
  export err=$?; err_chk
fi

# Cat the METplus log files
log_dirs1="$DATA/*/logs"
log_dirs2="$DATA/grid2obs/*/logs"
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
