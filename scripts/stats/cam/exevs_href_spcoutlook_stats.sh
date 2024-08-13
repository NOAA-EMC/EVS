#!/bin/ksh
##############################################################
# Purpose:   Setup some paths and run href spcoutlook job
# 
# Last updated 
#       05/04/2024: add restart, Binbin Zhou, Lynker@EMC/NCEP
#       10/30/2023: by  Binbin Zhou, Lynker@EMC/NCEP
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

export COMOUTrestart=$COMOUTsmall/restart
[[ ! -d $COMOUTrestart ]] &&  mkdir -p $COMOUTrestart
[[ ! -d $COMOUTrestart/prepare ]] &&  mkdir -p $COMOUTrestart/prepare
[[ ! -d $COMOUTrestart/prepare/prepbufr.${vday} ]] &&  mkdir -p $COMOUTrestart/prepare/prepbufr.${vday}
[[ ! -d $COMOUTrestart/spcoutlook ]] &&  mkdir -p $COMOUTrestart/spcoutlook



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
if [ -s run_href_all_grid2obs_poe ] ; then
 if [ $run_mpi = yes ] ; then
    mpiexec -np 2 -ppn 2 --cpu-bind verbose,core cfp  ${DATA}/run_href_all_grid2obs_poe
    export err=$?; err_chk
 else
    ${DATA}/run_href_all_grid2obs_poe
    export err=$?; err_chk
 fi
fi

#*******************************************************************
# Run gather job to combine small stat files to form a big stat file
# ******************************************************************
if [ $gather = yes ] && [ -s $COMOUTsmall/*.stat ] ; then
  $USHevs/cam/evs_href_gather.sh $VERIF_CASE  
  export err=$?; err_chk
fi

