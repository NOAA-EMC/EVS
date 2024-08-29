#!/bin/ksh
###################################################################
# Purpose:   Setup some paths and run refs precip stat ush scripts
#
# Last updated 
#             06/25/2024: Add restart, Binbin Zhou, Lynker@EMC/NCEP
#             10/30/2023: by  Binbin Zhou, Lynker@EMC/NCEP
###################################################################

set -x
export machine=${machine:-"WCOSS2"}

export WORK=$DATA
cd $WORK

export run_mpi=${run_mpi:-'yes'}
export verif_precip=${verif_precip:-'yes'}
export verif_snowfall=${verif_snowfall:-'yes'}
export prepare=${prepare:-'yes'}
export gather=${gather:-'yes'}
export verify='precip'

#*************************************
#check input data are available:
#*************************************
source $USHevs/cam/evs_check_refs_files.sh
export err=$?; err_chk

if [ -e $DATA/verif_precip.no ] ; then
   export verif_precip='no'
   echo "Either CCPA or REFS forecast files do not exist, skip verifying precip"
fi
if [ -e $DATA/verif_snowfall.no ] ; then
   export verif_snowfall='no'
   echo "Either NOHRSC or REFS forecast files do not exist, skip verifying snowfall"
fi

if [ -e $DATA/verif_precip.no ] && [ -e $DATA/verif_snowfall.no ] ; then
    export gather='no'
    export prepare='no'
fi

export COMREFS=$COMINrefs
export COMCCPA=$COMINccpa
export COMSNOW=$DCOMINsnow
export COMMRMS=$DCOMINmrms

export PRECIP_CONF=$PARMevs/metplus_config/$STEP/$COMPONENT/precip
export SNOWFALL_CONF=$PARMevs/metplus_config/$STEP/$COMPONENT/snowfall
export GATHER_CONF_PRECIP=$PRECIP_CONF
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS
export vday=$VDATE

#Generate directories For restart files
export COMOUTrestart=$COMOUTsmall/restart
[[ ! -d $COMOUTrestart ]] &&  mkdir -p $COMOUTrestart
[[ ! -d $COMOUTrestart/prepare/ccpa.${vday} ]] &&  mkdir -p $COMOUTrestart/prepare/ccpa.${vday}
[[ ! -d $COMOUTrestart/prepare/mrms.${vday} ]] &&  mkdir -p $COMOUTrestart/prepare/mrms.${vday}
[[ ! -d $COMOUTrestart/system ]]  &&  mkdir -p $COMOUTrestart/system
[[ ! -d $COMOUTrestart/prob ]] &&  mkdir -p $COMOUTrestart/prob
[[ ! -d $COMOUTrestart/eas ]] &&  mkdir -p $COMOUTrestart/eas
[[ ! -d $COMOUTrestart/mean ]] &&  mkdir -p $COMOUTrestart/mean
[[ ! -d $COMOUTrestart/pmmn ]] &&  mkdir -p $COMOUTrestart/pmmn
[[ ! -d $COMOUTrestart/lpmm ]] &&  mkdir -p $COMOUTrestart/lpmm
[[ ! -d $COMOUTrestart/avrg ]] &&  mkdir -p $COMOUTrestart/avrg
[[ ! -d $COMOUTrestart/snow ]] &&  mkdir -p $COMOUTrestart/snow

#**********************************
# Prepare CCPA data for validation
#**********************************
if [ $prepare = yes ] ; then
 for precip in ccpa01h03h ccpa24h apcp24h_conus  apcp24h_alaska mrms ; do
  $USHevs/cam/evs_refs_prepare.sh  $precip
  export err=$?; err_chk
 done
fi


#***************************************
# Build a POE script to collect sub-jobs
# **************************************
> run_all_precip_poe.sh

# Build sub-jobs for precip
if [ $verif_precip = yes ] ; then
 $USHevs/cam/evs_refs_precip.sh
 export err=$?; err_chk
 cat ${DATA}/run_all_refs_precip_poe.sh >> run_all_precip_poe.sh
fi

# Build sub-jobs for snowfall
if [ $verif_snowfall = yes ] ; then
 $USHevs/cam/evs_refs_snowfall.sh
 export err=$?; err_chk
 cat ${DATA}/run_all_refs_snowfall_poe.sh >> run_all_precip_poe.sh
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
if [ $gather = yes ] && [ -s $COMOUTsmall/*/*.stat ] ; then
  $USHevs/cam/evs_refs_gather.sh precip
  export err=$?; err_chk
fi
