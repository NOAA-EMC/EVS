#!/bin/ksh
#**************************************************************************
#  Purpose: check the required input forecast and validation data files
#           for global_ens stat jobs
#           Input arguments: 
#                  var, to specify the field to be checked
#
#  Last update: 11/16/2023, by Binbin Zhou Lynker@EMC/NCEP
#************************************************************************
set -x

var=$1
typeset -Z2 ihour

if [ $var = gfsanl ] ; then
  missing=0
  for ihour in 00 06 12 18 ; do
    if [ ! -s ${EVSIN}.${vday}/gefs/gfsanl.t${ihour}z.grid3.f000.grib2 ] ; then
      missing=$((missing + 1 ))
    fi
  done
  echo "Missing gfsanl files = " $missing
  if [ $missing -eq 4  ] ; then
    err_exit "all of the gfsanl files are missing"
    exit
  else
    echo "gfsanl data are OK!"
  fi
fi

if [ $var = cmcanl ] ; then
  missing=0
  for ihour in 00 12 ; do
    if [ ! -s ${EVSIN}.${vday}/cmce/cmcanl.t${ihour}z.grid3.f000.grib2 ] ; then
      missing=$((missing + 1 ))
    fi
  done
  echo "Missing cmcanl files = " $missing
  if [ $missing -eq 2  ] ; then
    err_exit "all of the cmcanl files are missing"
  else
    echo "cmcanl data are OK!"
  fi
fi

if [ $var = ecmanl ] ; then
  missing=0
  for ihour in 00 12 ; do
    if [ ! -s ${EVSIN}.${vday}/ecme/ecmanl.t${ihour}z.grid3.f000.grib1 ] ; then
      missing=$((missing + 1 ))
    fi
  done
  echo "Missing ecmanl files = " $missing
  if [ $missing -eq 2  ] ; then
    err_exit "all of the ecmanl files are missing"
  else
    echo "ecmanl data are OK!"
  fi
fi

if [ $var = gfsanl_1.5deg ] ; then
  if [ ! -s ${EVSIN}.${vday}/gefs/gfsanl.t00z.deg1.5.f000.grib2 ] ; then
    err_exit "gfsanl_1.5deg file is missing"
  else
    echo "gfsanl_1.5deg data is OK!"
  fi
fi

if [ $var = cmcanl_1.5deg ] ; then
  if [ ! -s ${EVSIN}.${vday}/cmce/cmcanl.t00z.deg1.5.f000.grib2 ] ; then
      err_exit "cmcanl_1.5deg file is missing"
  else
      echo "cmcanl_1.5deg data is OK!"
  fi
fi

if [ $var = prepbufr ] ; then
  missing=0 
  for ihour in 00 06 12 18 ; do
    if [ ! -s ${EVSIN}.${vday}/gefs/gfs.t${ihour}z.prepbufr.f00.nc ] ; then
      missing=$((missing + 1 ))
    fi
  done
  echo "Missing prepbufr files = " $missing
  if [ $missing -eq 4  ] ; then
    err_exit "all of the preppbufr files are missing"
  else
    echo "prepbufr data are OK!" 
  fi
fi 


if [ $var = prepbufr_profile ] ; then
  missing=0
  for ihour in 00 06 12 18 ; do
    if [ ! -s ${EVSIN}.${vday}/gefs/gfs.t${ihour}z.prepbufr_profile.f00.nc ] ; then
      missing=$((missing + 1 ))
    fi
  done
  echo "Missing prepbufr files = " $missing
  if [ $missing -eq 4  ] ; then
    err_exit "all of the preppbufr_profile files are missing"
  else
    echo "prepbufr_profile data are OK!"
  fi
fi

if [ $var = ccpa ] ; then
   if [ -s ${EVSIN}.${vday}/gefs/ccpa.t12z.grid3.24h.f00.nc ] ; then
      echo "CCPA24h data is OK"
   else
      err_exit "CPA24h data is missing"
   fi
fi 

if [ $var = osi_saf ]; then
    past=`$NDATE -24 ${vday}01`
    export vday1=${past:0:8}
    export period=multi.${vday1}00to${vday}00_G004
   if [ -s ${EVSIN}.${vday}/osi_saf/osi_saf.${period}.nc ] ; then
        echo "OSI_SAF data is OK"
   else
        err_exit "OSI_SAF data is missing"
   fi
fi

if [ $var = nohrsc ] ; then
   if [ -s ${EVSIN}.${vday}/gefs/nohrsc.t00z.grid184.grb2 ] && [ -s ${EVSIN}.${vday}/gefs/nohrsc.t12z.grid184.grb2 ] ; then
       echo "NOHRCS data is OK"
   else
      err_exit "NOHRSC data is missing"
  fi
fi

if [ $var = ghrsst ] ; then
   if [ -s ${EVSIN}.${vday}/gefs/ghrsst.t00z.nc ] ; then
       echo "GHRSST data is OK"
   else
       err_exit "GHRSST data is missing"
  fi
fi


if [ $var = gefs ] || [ $var = gefs_bc ] ; then 
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 if [  $var = gefs ] ; then
   ihours="00 06 12 18"
 else
   ihours="00 12"
 fi 
 for ihour in  $ihours ; do 
  obsv_time=${vday}${ihour}
  fhr=06
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    gefs_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do 
      gefs=$EVSIN.${fday}/gefs/gefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2
      if [ -s $gefs ] ; then
           gefs_mbrs=$((gefs_mbrs+1))
      fi	    
    done
    if [ $gefs_mbrs -eq 30 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else  
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+6))
  done
 done
   echo ihour_fhr_ok=$ihour_fhr_ok
   echo ihour_fhr_missing=$ihour_fhr_missing
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo at least there are some gefs member files!
    echo Continue ...
   fi    
fi 

if [ $var = cmce ] || [ $var = cmce_bc ] ; then 
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in  00 12 ; do 
  obsv_time=${vday}${ihour}
  fhr=12
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    cmce_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do 
      cmce=$EVSIN.${fday}/${var}/${var}.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2
      if [ -s $cmce ] ; then
           cmce_mbrs=$((cmce_mbrs+1))
      fi	    
    done
    if [ $cmce_mbrs -eq 20 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else  
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+12))
  done
 done
   echo ihour_fhr_ok=$ihour_fhr_ok
   echo ihour_fhr_missing=$ihour_fhr_missing
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo at least there are some cmce member files!
    echo Continue ...
   fi    
fi 

if [ $var = ecme ] ; then 
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in  00 12 ; do 
  obsv_time=${vday}${ihour}
  fhr=12
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    ecme_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 ; do 
      ecme=$EVSIN.${fday}/ecme/ecme.ens${mb}.t${ihour}z.grid4.f${hhh}.grib1
      if [ -s $ecme ] ; then
           ecme_mbrs=$((ecme_mbrs+1))
      fi	    
    done
    if [ $ecme_mbrs -eq 50 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else  
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+12))
  done
 done
   echo ihour_fhr_ok=$ihour_fhr_ok
   echo ihour_fhr_missing=$ihour_fhr_missing
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo at least there are some ecme member files!
    echo Continue ...
   fi    
fi 

if [ $var = gefs_apcp24h ] ; then 
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in  12 ; do 
  obsv_time=${vday}${ihour}
  fhr=24
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    gefs_apcp24h_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do 
      gefs_apcp24h=$EVSIN.${fday}/gefs/gefs.ens${mb}.t${ihour}z.grid3.24h.f${hhh}.nc
      if [ -s $gefs_apcp24h ] ; then
           gefs_apcp24h_mbrs=$((gefs_apcp24h_mbrs+1))
      fi	    
    done
    if [ $gefs_apcp24h_mbrs -eq 30 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else  
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+12))
  done
 done
   echo ihour_fhr_ok=$ihour_fhr_ok
   echo ihour_fhr_missing=$ihour_fhr_missing
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo at least there are some gefs_apcp24h member files!
    echo Continue ...
   fi    
fi 

if [ $var = cmce_apcp24h ] ; then 
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in  12 ; do 
  obsv_time=${vday}${ihour}
  fhr=24
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    cmce_apcp24h_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do 
      cmce_apcp24h=$EVSIN.${fday}/cmce/cmce.ens${mb}.t${ihour}z.grid3.24h.f${hhh}.nc
      if [ -s $cmce_apcp24h ] ; then
           cmce_apcp24h_mbrs=$((cmce_apcp24h_mbrs+1))
      fi	    
    done
    if [ $cmce_apcp24h_mbrs -eq 20 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else  
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+12))
  done
 done
   echo ihour_fhr_ok=$ihour_fhr_ok
   echo ihour_fhr_missing=$ihour_fhr_missing
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo at least there are some cmce_apcp24h member files!
    echo Continue ...
   fi    
fi 

if [ $var = ecme_apcp24h ] ; then 
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in  12 ; do 
  obsv_time=${vday}${ihour}
  fhr=24
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    ecme_apcp24h_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 ; do 
      ecme_apcp24h=$EVSIN.${fday}/ecme/ecme.ens${mb}.t${ihour}z.grid4.24h.f${hhh}.nc
      if [ -s $ecme_apcp24h ] ; then
           ecme_apcp24h_mbrs=$((ecme_apcp24h_mbrs+1))
      fi	    
    done
    if [ $ecme_apcp24h_mbrs -eq 50 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else  
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+12))
  done
 done
   echo ihour_fhr_ok=$ihour_fhr_ok
   echo ihour_fhr_missing=$ihour_fhr_missing
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo at least there are some ecme_apcp24h member files!
    echo Continue ...
   fi    
fi 

if [ $var = gefs_icec_24h ] ; then 
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in 00 ; do 
  obsv_time=${vday}${ihour}
  fhr=24
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    gefs_icec_24h_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do 
      gefs_icec_24h=$EVSIN.${fday}/gefs/gefs.ens${mb}.t${ihour}z.grid3.icec_24h.f${hhh}.nc
      if [ -s $gefs_icec_24h ] ; then
           gefs_icec_24h_mbrs=$((gefs_icec_24h_mbrs+1))
      fi	    
    done
    if [ $gefs_icec_24h_mbrs -eq 30 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else  
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+12))
  done
 done
   echo ihour_fhr_ok=$ihour_fhr_ok
   echo ihour_fhr_missing=$ihour_fhr_missing
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo at least there are some gefs_icec_24h member files!
    echo Continue ...
   fi    
fi 

if [ $var = gefs_sst24h ] ; then 
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in 00 ; do 
  obsv_time=${vday}${ihour}

  fhr=24

  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    gefs_sst24h_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do 
      gefs_sst24h=$EVSIN.${fday}/gefs/gefs.ens${mb}.t${ihour}z.grid3.sst24h.f${hhh}.nc
      if [ -s $gefs_sst24h ] ; then
           gefs_sst24h_mbrs=$((gefs_sst24h_mbrs+1))
      fi	    
    done
    if [ $gefs_sst24h_mbrs -eq 30 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else  
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+12))
  done
 done
   echo ihour_fhr_ok=$ihour_fhr_ok
   echo ihour_fhr_missing=$ihour_fhr_missing
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo at least there are some gefs_sst24h member files!
    echo Continue
   fi    
fi 

if [ $var = gefs_WEASD ] ; then 
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in 00 12 ; do 
  obsv_time=${vday}${ihour}
  fhr=24
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    gefs_WEASD_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do 
      gefs_WEASD=$EVSIN.${fday}/gefs/gefs.ens${mb}.t${ihour}z.grid3.WEASD_24h.f${hhh}.nc
      if [ -s $gefs_WEASD ] ; then
           gefs_WEASD_mbrs=$((gefs_WEASD_mbrs+1))
      fi	    
    done
    if [ $gefs_WEASD_mbrs -eq 30 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else  
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+12))
  done
 done
   echo ihour_fhr_ok=$ihour_fhr_ok
   echo ihour_fhr_missing=$ihour_fhr_missing
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo at least there are some gefs_WEASD member files!
    echo Continue
   fi    
fi 

if [ $var = gefs_SNOD ] ; then 
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in 00 12 ; do 
  obsv_time=${vday}${ihour}
  fhr=24
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    gefs_SNOD_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do 
      gefs_SNOD=$EVSIN.${fday}/gefs/gefs.ens${mb}.t${ihour}z.grid3.SNOD_24h.f${hhh}.nc
      if [ -s $gefs_SNOD ] ; then
           gefs_SNOD_mbrs=$((gefs_SNOD_mbrs+1))
      fi	    
    done
    if [ $gefs_SNOD_mbrs -eq 30 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else  
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+12))
  done
 done
   echo ihour_fhr_ok=$ihour_fhr_ok
   echo ihour_fhr_missing=$ihour_fhr_missing
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo at least there are some gefs_SNOD member files!
    echo Continue
   fi    
fi 

if [ $var = cmce_SNOD ] ; then 
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in 00 12 ; do 
  obsv_time=${vday}${ihour}
  fhr=24
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    cmce_SNOD_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20; do 
      cmce_SNOD=$EVSIN.${fday}/cmce/cmce.ens${mb}.t${ihour}z.grid3.SNOD_24h.f${hhh}.nc
      if [ -s $cmce_SNOD ] ; then
           cmce_SNOD_mbrs=$((cmce_SNOD_mbrs+1))
      fi	    
    done
    if [ $cmce_SNOD_mbrs -eq 20 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else  
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+12))
  done
 done
   echo ihour_fhr_ok=$ihour_fhr_ok
   echo ihour_fhr_missing=$ihour_fhr_missing
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo at least there are some cmce_SNOD member files!
    echo Continue
   fi    
fi 

if [ $var = cmce_WEASD ] ; then 
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in 00 12 ; do 
  obsv_time=${vday}${ihour}
  fhr=24
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    cmce_WEASD_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20; do 
      cmce_WEASD=$EVSIN.${fday}/cmce/cmce.ens${mb}.t${ihour}z.grid3.WEASD_24h.f${hhh}.nc
      if [ -s $cmce_WEASD ] ; then
           cmce_WEASD_mbrs=$((cmce_WEASD_mbrs+1))
      fi	    
    done
    if [ $cmce_WEASD_mbrs -eq 20 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else  
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+12))
  done
 done
   echo ihour_fhr_ok=$ihour_fhr_ok
   echo ihour_fhr_missing=$ihour_fhr_missing
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo at least there are some cmce_WEASD member files!
    echo Continue
   fi    
fi 

if [ $var = ecme_weasd ] ; then 
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in 00 12 ; do 
  obsv_time=${vday}${ihour}
  fhr=24
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    ecme_weasd_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 ; do 
      ecme_weasd=$EVSIN.${fday}/ecme/ecme.ens${mb}.t${ihour}z.grid4.weasd_24h.f${hhh}.nc
      if [ -s $ecme_weasd ] ; then
           ecme_weasd_mbrs=$((ecme_weasd_mbrs+1))
      fi	    
    done
    if [ $ecme_weasd_mbrs -eq 50 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else  
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+12))
  done
 done
   echo ihour_fhr_ok=$ihour_fhr_ok
   echo ihour_fhr_missing=$ihour_fhr_missing
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo at least there are some ecme_weasd member files!
    echo Continue ...
   fi    
fi 

if [ $var = headline_gefs ] ; then 
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in  00 ; do 
  obsv_time=${vday}${ihour}
  fhr=024
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    gefs_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do 
      gefs=$EVSIN.${fday}/gefs/gefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2
      if [ -s $gefs ] ; then
           gefs_mbrs=$((gefs_mbrs+1))
      fi	    
    done
    if [ $gefs_mbrs -eq 30 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else  
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+24))
  done
 done
   echo ihour_fhr_ok=$ihour_fhr_ok
   echo ihour_fhr_missing=$ihour_fhr_missing
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo at least there are some gefs member files!
    echo Continue ...
   fi    
fi 

if [ $var = headline_cmce ] ; then 
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in  00 ; do 
  obsv_time=${vday}${ihour}
  fhr=024
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}

    cmce_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do 
      cmce=$EVSIN.${fday}/cmce/cmce.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2
      if [ -s $cmce ] ; then
           cmce_mbrs=$((cmce_mbrs+1))
      fi	    
    done
    if [ $cmce_mbrs -eq 20 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else  
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+24))
  done
 done
   echo ihour_fhr_ok=$ihour_fhr_ok
   echo ihour_fhr_missing=$ihour_fhr_missing
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo at least there are some cmce member files!
    echo Continue ...
   fi    
fi 

if [ $var = headline_gfsanl ] ; then
    if [ ! -s ${EVSIN}.${vday}/gefs/gfsanl.t00z.grid3.f000.grib2 ] ; then
      err_exit "gfsanl file missing"
     else
       echo "gfsanl data is OK!"
       echo Continue ...
     fi
fi

if [ $var = headline_cmcanl ] ; then
    if [ ! -s ${EVSIN}.${vday}/cmce/cmcanl.t00z.grid3.f000.grib2 ] ; then
        echo " cmcanl file missing"
    else
         echo "cmcanl data is OK!"
	 echo Continue ...
    fi
fi

if [ $var = headline_gfs ] ; then 
 for ihour in  00 ; do 
  obsv_time=${vday}${ihour}
  fhr=024
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    gfs=$EVSIN.${fday}/gefs/gfs.t${ihour}z.grid3.f${hhh}.grib2
    if [ ! -s $gfs ] ; then
      err_exit "$gfs not existing"
      exit
    fi 
    fhr=$((fhr+24))
  done
 done
    echo Continue ...
fi 

if [ $var = wmo_cmce ] ; then 
 echo COM_IN=$COM_IN
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in  00 ; do 
  obsv_time=${vday}${ihour}
  fhr=024
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    cmce_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do 
      cmce=$COM_IN/atmos.${fday}/cmce/cmce.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2
      if [ -s $cmce ] ; then
           cmce_mbrs=$((cmce_mbrs+1))
      fi	    
    done
    if [ $cmce_mbrs -eq 20 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else  
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+24))
  done
 done
   echo ihour_fhr_ok=$ihour_fhr_ok
   echo ihour_fhr_missing=$ihour_fhr_missing
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo at least there are some cmce member files!
    echo Continue ...
   fi    
fi 

if [ $var = wmo_cmcanl ] ; then
  if [ ! -s ${COM_IN}/atmos.${vday}/cmce/cmcanl.t00z.grid3.f000.grib2 ] ; then
      err_exit " cmcanl file missing"
  else
     echo "cmcanl data is OK!"
     echo Continue ...
  fi
fi

if [ $var = wmo_gefs ] ; then 
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in  00 ; do 
  obsv_time=${vday}${ihour}
  fhr=024
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    gefs_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30; do 
      gefs=$COM_IN/atmos.${fday}/gefs/gefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2
      if [ -s $gefs ] ; then
           gefs_mbrs=$((gefs_mbrs+1))
      fi	    
    done
    if [ $gefs_mbrs -eq 30 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else  
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+24))
  done
 done
   echo ihour_fhr_ok=$ihour_fhr_ok
   echo ihour_fhr_missing=$ihour_fhr_missing
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo at least there are some gefs member files!
    echo Continue ...
   fi    
fi 

if [ $var = wmo_gfsanl ] ; then
   if [ ! -s ${COM_IN}/atmos.${vday}/gefs/gfsanl.t00z.grid3.f000.grib2 ] ; then
       err_exit "gfsanl file missing"
   else
       echo "gfsanl data is OK!"
       echo Continue ...
   fi
fi
