#!/bin/ksh
#################################################################
# Script Name: verf_g2g_reflt.sh.sms $vday $vcyc
# Purpose:   To run grid-to-grid verification on reflectivity
#
# Log History:  Julia Zhu -- 2010.04.28 
################################################################
set -x


export WORK=$DATA
cd $WORK

export MET_bin_exec='bin'
export log_met_output_to_metplus=''
export metplus_verbosity=2
export met_verbosity=2

#check input data are available:
$USHevs/evs_check_href_files.sh 

#lvl = profile or sfc or both
export lvl='both'

#  verify_all = yes:  verify both profile and sfc (system + product)
#  if lvl is not both, verify_all = no
export verify_all='yes'

export prepare='yes'
export verif_system='yes'
export verif_profile='yes'
export verif_product='yes'
export gather=${gather:-'yes'}
export verify=$VERIF_CASE
export run_mpi=${run_mpi:-'yes'}

export COMHREF=$COMINhref
export PREPBUFR=$COMINprepbufr

export GATHER_CONF_PRECIP=$PRECIP_CONF
export GRID2OBS_CONF=$PARMevs/metplus_config/$COMPONENT/grid2obs/$STEP
export GATHER_CONF_GRID2OBS=$GRID2OBS_CONF
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS
export vday=$VDATE

#  domain = conus or alaska or all
export domain="all"
#export domain="HI"


msg="$job HAS BEGUN"
postmsg "$jlogfile" "$msg"

if [ $prepare = yes ] ; then

  if [ -s $COMINobsproc/rap.${VDATE}/rap.t12z.prepbufr.tm00 ] && [ -s $COMINobsproc/gdas.${vday}/00/atmos/gdas.t00z.prepbufr ] ; then

     $USHevs/cam/evs_href_preppare.sh prepbufr
     $USHevs/cam/evs_href_preppare.sh gfs_prepbufr

  else
       export subject="GFS or RAP Prepbufr Data Missing for EVS ${COMPONENT}"
       export maillist=${maillist:-'geoffrey.manikin@noaa.gov,binbin.zhou@noaa.gov'}
       echo "Warning:  No GFS or RAP Prepbufr data available for ${VDATE}" > mailmsg
       echo Missing file is $COMINobsproc/rap.${VDATE}/rap.t12z.prepbufr.tm00 or $COMINobsproc/gdas.${vday}/00/atmos/gdas.t00z.prepbufr  >> mailmsg
       echo "Job ID: $jobid" >> mailmsg
       cat mailmsg | mail -s "$subject" $maillist
       exit
  fi

fi 


>run_href_all_grid2obs_poe

#system: 10 jobs (8 on CONUS, 2 on Alaska)
if [ $verif_system = yes ] ; then 
  $USHevs/cam/evs_href_grid2obs_system.sh 
  cat ${DATA}/run_all_href_system_poe.sh >> run_href_all_grid2obs_poe
fi

#profile: total 10 jobs (4 for conus and 2 for alaska)
if [ $verif_profile = yes ] ; then 
  $USHevs/cam/evs_href_grid2obs_profile.sh $domain
  cat ${DATA}/run_all_href_profile_poe.sh >> run_href_all_grid2obs_poe 
fi 

#Product: 16 jobs
if [ $verif_product = yes ] ; then
  $USHevs/cam/evs_href_grid2obs_product.sh
  cat ${DATA}/run_all_href_product_poe.sh >> run_href_all_grid2obs_poe
fi


#totall: 36 jobs for all (both conus and alaska, profile, system and product)
chmod 775 run_href_all_grid2obs_poe


if [ $run_mpi = yes ] ; then

    export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH

    mpiexec -np 36 -ppn 36 --cpu-bind verbose,depth cfp  ${DATA}/run_href_all_grid2obs_poe

else
    ${DATA}/run_href_all_grid2obs_poe

fi

if [ $gather = yes ] && [ -s run_href_all_grid2obs_poe ] ; then
  $USHevs/cam/evs_href_gather.sh $VERIF_CASE  
fi

msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$jlogfile" "$msg"


exit 0
