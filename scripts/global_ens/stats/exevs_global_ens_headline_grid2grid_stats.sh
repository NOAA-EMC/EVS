#!/bin/ksh
#################################################################
# Purpose:   To run grid-to-grid verification on all global ensembles
#
# Log History:  12/01/2021 Binbin Zhou  
################################################################
set -x

export WORK=$DATA
cd $WORK

export MET_bin_exec='bin'
export log_met_output_to_metplus=''
export metplus_verbosity=2
export met_verbosity=2

export CLIMO=$FIXevs/climos/atmos
export MASKS=$FIXevs/masks

export ENS_LIST=$PARMevs/metplus_config/${COMPONENT}/atmos_grid2grid/prep
export GRID2GRID_CONF=$PARMevs/metplus_config/${COMPONENT}/${RUN}_grid2grid/${STEP}
export MET_CONFIG=${METPLUS_BASE}/parm/met_config
export maskpath=$MASKS

msg="$job HAS BEGUN"
postmsg "$jlogfile" "$msg"
export run_mpi=${run_mpi:-'yes'}
export gather=${gather:-'yes'}


export vday=$1
ens=$2 
verify_type=$3

#############################################################
# Step 0: Run copygb to convert URMA data to 4km WRF grid
#############################################################

if  [ $ens = gefs ] || [ $ens = naefs ] || [ $ens = gfs ] ; then
  if [ $verify_type = upper ] ; then

   if [ $ens = gfs ] || [ [ $ens = gefs ] ; then
    if [ ! -s ${COMIN}.${VDATE}/gefs/gfsanl.t00z.grid3.f000.grib2 ] ; then
         	       
       export subject="GFS analysis data missing for $ens headline stat job"
       echo "Warning: No GFS analysis available for ${VDATE}" > mailmsg 
       echo Missing file is ${COMIN}.${VDATE}/gefs/gfsanl.t00z.grid3.f000.grib2  >> mailmsg
       echo "Job ID: $jobid" >> mailmsg
       cat mailmsg | mail -s "$subject" $maillist
       exit
    fi
   fi

   if [ $ens = naefs ] ; then 
      if [ ! -s ${COMIN}.${VDATE}/cmce/cmcanl.t00z.grid3.f000.grib2 ] || [ ! -s ${COMIN}.${VDATE}/gefs/gfsanl.t00z.grid3.f000.grib2 ] ; then
        export subject="GFS or CMC analysis data missing for $ens headline stat job"
        echo "Warning: No GFS or CMC analysis available for ${VDATE}" > mailmsg
        echo Missing file is ${COMIN}.${VDATE}/gefs/gfsanl.t00z.grid3.f000.grib2 or ${COMIN}.${VDATE}/cmce/cmcanl.t00z.grid3.f000.grib2  >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $maillist
        exit
     fi
   fi
   echo "All data are available, continuing"
   $USHevs/global_ens/evs_global_ens_headline_grid2grid.sh $ens $verify_type 
 fi
fi


msg="JOB $job HAS COMPLETED NORMALLY"
postmsg "$jlogfile" "$msg"



exit 0
