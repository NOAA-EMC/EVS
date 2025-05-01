#!/bin/ksh
#####################################################################
# Purpose:   Setup some paths and run href grid2obs stat ush scripts
# 
# Last updated 
#              01/10/2025: Add MPMD:  by  Binbin Zhou, Lynker@EMC/NCEP
#              06/25/2024: add restart: by  Binbin Zhou, Lynker@EMC/NCEP
#              10/30/2023: by  Binbin Zhou, Lynker@EMC/NCEP
#####################################################################
set -x


export machine=${machine:-"WCOSS2"}
export WORK=$DATA
cd $WORK
mkdir -p $WORK/scripts
export all_stats=$WORK/all_stats
mkdir -p $all_stats

#lvl = profile or sfc or both
export lvl='both'

#  verify_all = yes:  verify both profile and sfc (system + product)
#  if lvl is not both, verify_all = no
export verify_all=${verify_all:-'yes'}

export prepare='yes'
export verif_system='yes'
export verif_profile='yes'
export verif_product='yes'
export gather=${gather:-'yes'}
export verify=$VERIF_CASE

#*************************************
#check input data are available:
#*************************************
source $USHevs/$COMPONENT/evs_check_href_files.sh
export err=$?; err_chk
if [ -e $DATA/verif_all.no ] ; then
 export prepare='no'
 export verif_system='no'
 export verif_profile='no'
 export verif_product='no'
 export gather='no'
 echo "Either prepbufr or HREF forecast files do not exist, skip grid2obs verification!"
fi


export COMHREF=$COMINhref
export PREPBUFR=$COMINobsproc

export GATHER_CONF_PRECIP=$PRECIP_CONF
export GRID2OBS_CONF=$PARMevs/metplus_config/$STEP/$COMPONENT/grid2obs
export GATHER_CONF_GRID2OBS=$GRID2OBS_CONF
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS
export vday=$VDATE

#  domain = conus or alaska or all
export domain="all"

export COMOUTrestart=$COMOUTsmall/restart
[[ ! -d $COMOUTrestart ]] &&  mkdir -p $COMOUTrestart
[[ ! -d $COMOUTrestart/prepare ]] &&  mkdir -p $COMOUTrestart/prepare
[[ ! -d $COMOUTrestart/system ]]  &&  mkdir -p $COMOUTrestart/system
[[ ! -d $COMOUTrestart/profile ]] &&  mkdir -p $COMOUTrestart/profile
[[ ! -d $COMOUTrestart/product ]] &&  mkdir -p $COMOUTrestart/product

#***************************************
# Prepare the prepbufr data
# **************************************
if [ $prepare = yes ] ; then

  if [ -s $COMINobsproc/rap.${VDATE}/rap.t12z.prepbufr.tm00 ] && [ -s $COMINobsproc/gdas.${vday}/00/atmos/gdas.t00z.prepbufr ] ; then

     $USHevs/cam/evs_href_prepare.sh prepbufr $domain
     export err=$?; err_chk
     $USHevs/cam/evs_href_prepare.sh gfs_prepbufr $domain
     export err=$?; err_chk

  else
       export subject="GFS or RAP Prepbufr Data Missing for EVS ${COMPONENT}"
       export MAILTO=${MAILTO:-'andrew.benjamin@noaa.gov,binbin.zhou@noaa.gov'}
       echo "Warning:  No GFS or RAP Prepbufr data available for ${VDATE}" > mailmsg
       echo Missing file is $COMINobsproc/rap.${VDATE}/rap.t12z.prepbufr.tm00 or $COMINobsproc/gdas.${vday}/00/atmos/gdas.t00z.prepbufr  >> mailmsg
       echo "Job ID: $jobid" >> mailmsg
       cat mailmsg | mail -s "$subject" $MAILTO
       export verif_system=no
       export verif_profile=no
       export verif_product=no
  fi

fi 


#*****************************************
# Build a POE script to collect sub-jobs
#****************************************
>$DATA/scripts/run_href_all_grid2obs_poe

if [ $verif_system = yes ] ; then 
  $USHevs/cam/evs_href_grid2obs_system.sh 
  export err=$?; err_chk
  cat ${DATA}/scripts/run_all_href_system_poe.sh >> $DATA/scripts/run_href_all_grid2obs_poe
fi

if [ $verif_profile = yes ] ; then 
  $USHevs/cam/evs_href_grid2obs_profile.sh $domain
  export err=$?; err_chk
  cat ${DATA}/scripts/run_all_href_profile_poe.sh >> $DATA/scripts/run_href_all_grid2obs_poe 
fi 

if [ $verif_product = yes ] ; then
  $USHevs/cam/evs_href_grid2obs_product.sh
  export err=$?; err_chk
  cat ${DATA}/scripts/run_all_href_product_poe.sh >> $DATA/scripts/run_href_all_grid2obs_poe
fi


#totall: 72 jobs for all (both conus and alaska, profile, system and product)
chmod 775 $DATA/scripts/run_href_all_grid2obs_poe


#*************************************************
# Run the POE script to generate small stat files
#*************************************************
if [ -s $DATA/scripts/run_href_all_grid2obs_poe ] ; then
    mpiexec -np 72 -ppn 72 --cpu-bind verbose,depth cfp  ${DATA}/scripts/run_href_all_grid2obs_poe
    export err=$?; err_chk
fi

#******************************************************************
# Run gather job to combine the small stats to form a big stat file
#******************************************************************
if [ $gather = yes ] && [ -s $all_stats/*.stat ] ; then
  $USHevs/cam/evs_href_gather.sh $VERIF_CASE  
  export err=$?; err_chk
fi

