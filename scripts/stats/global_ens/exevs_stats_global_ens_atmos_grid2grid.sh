#!/bin/ksh
#**********************************************************************************************
# Purpose:  1. Setup some running envirnment paramters for grid-to-grid job that are not
#              defined in stat J-job  
#           2. Run  grid-to-grid verifications for all global ensembles, including
#               (1) upper air fields grid2grid verification for gefs, cmce, ecme and naefs
#               (2) precip verification for gefs, cmce, ecme and naefs
#               (3) snowfall verification for gefs, cmce, and ecme 
#               (4) sea ice verification for gefs
#               (5) SST verification for gefs
#
# Last  updated 11/15/2023: by  Binbin Zhou, Lynker@EMC/NCEP
#
#**********************************************************************************************
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

if [ $ens = gefs ] && [ $verif_case = upper ] ; then
     if [ ! -s ${EVSIN}.${VDATE}/gefs/gfsanl.t00z.grid3.f000.grib2 ] ; then
        if [ $SENDMAIL = YES ]; then
          export subject="GFS analysis data missing"
          echo "Warning: No GFS analysis available for ${VDATE}" > mailmsg 
          echo "Missing file is ${EVSIN}.${VDATE}/gefs/gfsanl.t00z.grid3.f000.grib2"  >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
        fi
     else
        echo "All $ens $verif_case validation data are available, continuing ..."
        $USHevs/global_ens/evs_global_ens_atmos_grid2grid.sh $ens ${verif_case}
        export err=$?; err_chk
     fi
fi

if [ $ens = cmce ] && [ $verif_case = upper ] ; then
     if [ ! -s ${EVSIN}.${VDATE}/cmce/cmcanl.t00z.grid3.f000.grib2 ] ; then
       if [ $SENDMAIL = YES ]; then
         export subject="CMC analysis data missing "
         echo "Warning: No CMC analysis available for ${VDATE}" > mailmsg 
         echo "Missing file is ${EVSIN}.${VDATE}/cmce/cmcanl.t00z.grid3.f000.grib2"  >> mailmsg
         echo "Job ID: $jobid" >> mailmsg
         cat mailmsg | mail -s "$subject" $MAILTO
       fi
     else
       echo "All $ens $verif_case validation data are available, continuing ..."
       $USHevs/global_ens/evs_global_ens_atmos_grid2grid.sh $ens ${verif_case}
       export err=$?; err_chk
     fi
fi

if [ $ens = ecme ] && [ $verif_case = upper ] ; then
      if [ ! -s ${EVSIN}.${VDATE}/ecme/ecmanl.t00z.grid3.f000.grib1 ] ; then
        if [ $SENDMAIL = YES ]; then
          export subject="EC analysis data missing "
          echo "Warning: No EC analysis available for ${VDATE}" > mailmsg 
          echo "Missing file is ${EVSIN}.${VDATE}/ecme/ecmanl.t00z.grid3.f000.grib1"  >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
	fi
      else
        echo "All $ens $verif_case validation data are available, continuing ..."
        $USHevs/global_ens/evs_global_ens_atmos_grid2grid.sh $ens ${verif_case}
        export err=$?; err_chk
      fi
fi

if [ $ens = naefs ] && [ $verif_case = upper ] ; then
      if [ ! -s ${EVSIN}.${VDATE}/cmce/cmcanl.t00z.grid3.f000.grib2 ] || [ ! -s ${EVSIN}.${VDATE}/gefs/gfsanl.t00z.grid3.f000.grib2 ] ; then
        if [ $SENDMAIL = YES ]; then
          for naefs_verif_anl in GFS CMC; do
              if [ $naefs_verif_anl = GFS ]; then
                  naefs_verif_anl_file=${EVSIN}.${VDATE}/gefs/gfsanl.t00z.grid3.f000.grib2
              elif [ $naefs_verif_anl = CMC ]; then
                  naefs_verif_anl_file=${EVSIN}.${VDATE}/cmce/cmcanl.t00z.grid3.f000.grib2
              fi
              if [ ! -s $naefs_verif_anl_file ]; then
                 export subject="$naefs_verif_anl analysis data missing for NAEFS "
                 echo "Warning: No $naefs_verif_anl analysis available for ${VDATE}" > mailmsg 
                 echo "Missing file is $naefs_verif_anl_file"  >> mailmsg
                 echo "Job ID: $jobid" >> mailmsg
                 cat mailmsg | mail -s "$subject" $MAILTO
              fi
          done
	fi
      else
        echo "All $ens $verif_case validation data are available, continuing ..."
        $USHevs/global_ens/evs_global_ens_atmos_grid2grid.sh $ens ${verif_case}
        export err=$?; err_chk
      fi
fi

if [ $verif_case = precip ] ; then
      if [ ! -s ${EVSIN}.${VDATE}/gefs/ccpa.t12z.grid3.24h.f00.nc ] ; then
        if [ $SENDMAIL = YES ]; then
          export subject="24h CCAP data missing "
          echo "Warning: No 24hCCAP data available for ${VDATE}" > mailmsg 
          echo "Missing file is ${EVSIN}.${VDATE}/gefs/ccpa.t12z.grid3.24h.f00.nc"  >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
	fi
      else
        echo "All $verif_case validation data are available, continuing ..."
        $USHevs/global_ens/evs_global_ens_atmos_grid2grid.sh $ens $verif_case
        export err=$?; err_chk
      fi
fi 

if [ $verif_case = snowfall ] ; then
  day1=`$NDATE -24 ${VDATE}12`
  VDATE_1=${day1:0:8}
  if [ ! -s ${EVSIN}.${VDATE}/gefs/nohrsc.t00z.grid184.grb2 ] ; then
    if [ $SENDMAIL = YES ]; then
      export subject="NOHRSC Snowfall analysis data missing "
      echo "Warning: No NOHRSC snowfall analysis available for ${VDATE}" > mailmsg
      echo "Missing file is ${EVSIN}.${VDATE}/gefs/nohrsc.t00z.grid184.grb2"  >> mailmsg
      echo "Job ID: $jobid" >> mailmsg
      cat mailmsg | mail -s "$subject" $MAILTO
    fi
  else
    echo "All $verif_case validation data are available, continuing ..."  
    $USHevs/global_ens/evs_global_ens_atmos_${verif_case}.sh $ens ${verif_case}
    export err=$?; err_chk
  fi
fi


if [ $verif_case = sea_ice ] ; then
  day1=`$NDATE -24 ${VDATE}12`
  VDATE_1=${day1:0:8}
   if [ ! -s ${EVSIN}.${VDATE}/osi_saf/osi_saf.multi.${VDATE_1}00to${VDATE}00_G004.nc ] ; then
     if [ $SENDMAIL = YES ]; then
       export subject="OSI_SAF analysis data missing "
       echo "Warning: No OSI_SAF analysis available for ${VDATE}" > mailmsg 
       echo "Missing file is ${EVSIN}.${VDATE}/osi_saf/osi_saf.multi.${VDATE_1}00to${VDATE}00_G004.nc"  >> mailmsg
       echo "Job ID: $jobid" >> mailmsg
       cat mailmsg | mail -s "$subject" $MAILTO
     fi
   else
     echo "All $verif_case validation data are available, continuing ..."  
     $USHevs/global_ens/evs_global_ens_atmos_${verif_case}.sh $ens ${verif_case}
     export err=$?; err_chk
   fi
fi

if [ $verif_case = sst ] ; then
  if [ ! -s ${EVSIN}.${VDATE}/gefs/ghrsst.t00z.nc ] ; then
    if [ $SENDMAIL = YES ]; then
      export subject="GHRSST analysis data missing "
      echo "Warning: No GHRSST analysis available for ${VDATE}" > mailmsg 
      echo "Missing file is ${EVSIN}.${VDATE}/gefs/ghrsst.t00z.nc" >> mailmsg
      echo "Job ID: $jobid" >> mailmsg
      cat mailmsg | mail -s "$subject" $MAILTO
    fi
  else
    echo "All sst24h validation data are available, continuing ..."
    $USHevs/global_ens/evs_global_ens_atmos_${verif_case}.sh $ens sst24h
    export err=$?; err_chk
  fi
fi
