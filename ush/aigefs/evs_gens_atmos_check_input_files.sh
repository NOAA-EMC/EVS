#!/bin/ksh
#**************************************************************************
# Purpose: check the required input forecast and validation data files
#          for aigefs stats jobs
# Input argument: 
#          var -- to specify the field to be checked
#
# Update: 10/14/2025 by Gwen Chen (lichuan.chen@noaa.gov)
#**************************************************************************
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

if [ $var = gfsanl_1.5deg ] ; then
  if [ ! -s ${EVSIN}.${vday}/gefs/gfsanl.t00z.deg1.5.f000.grib2 ] ; then
    err_exit "gfsanl_1.5deg file is missing"
  else
    echo "gfsanl_1.5deg data is OK!"
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
    err_exit "all of the prepbufr files are missing"
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
    err_exit "all of the prepbufr_profile files are missing"
  else
    echo "prepbufr_profile data are OK!"
  fi
fi

if [ $var = ccpa ] ; then
   if [ -s ${EVSIN}.${vday}/gefs/ccpa.t12z.grid3.24h.f00.nc ] ; then
      echo "CCPA24h data is OK"
   else
      err_exit "CCPA24h data is missing"
   fi
fi 

if [ $var = gefs ] ; then 
  ihour_fhr_ok=0
  ihour_fhr_missing=0
  if [ $var = gefs ] ; then
    ihours="00 06 12 18"
  else
    ihours="00 12"
  fi 
  for ihour in $ihours ; do 
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
  echo "ihour_fhr_ok=$ihour_fhr_ok"
  echo "ihour_fhr_missing=$ihour_fhr_missing"
  if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
  else
    echo "at least there are some gefs member files!"
    echo "Continue ..."
  fi    
fi 

if [ $var = aigefs ] ; then
  ihour_fhr_ok=0
  ihour_fhr_missing=0
  ihours="00 06 12 18"
  for ihour in $ihours ; do
    obsv_time=${vday}${ihour}
    fhr=06
    while [ $fhr -le 384 ] ; do
      hhh=$fhr
      typeset -Z3 hhh
      fcst_time=`$NDATE -$fhr $obsv_time`
      fday=${fcst_time:0:8}
      ihour=${fcst_time:8:2}
      aigefs_mbrs=0
      for mb in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
        aigefs=$EVSIN.${fday}/aigefs/aigefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2
        if [ -s $aigefs ] ; then
          aigefs_mbrs=$((aigefs_mbrs+1))
        fi
      done
      if [ $aigefs_mbrs -eq 31 ] ; then
        ihour_fhr_ok=$((ihour_fhr_ok+1))
      else
        ihour_fhr_missing=$((ihour_fhr_missing+1))
      fi
      fhr=$((fhr+6))
    done
  done
  echo "ihour_fhr_ok=$ihour_fhr_ok"
  echo "ihour_fhr_missing=$ihour_fhr_missing"
  if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
  else
    echo "at least there are some aigefs member files!"
    echo "Continue ..."
  fi
fi

if [ $var = hgefs ] ; then
  ihour_fhr_ok=0
  ihour_fhr_missing=0
  ihours="00 06 12 18"
  for ihour in $ihours ; do
    obsv_time=${vday}${ihour}
    fhr=06
    while [ $fhr -le 384 ] ; do
      hhh=$fhr
      typeset -Z3 hhh
      fcst_time=`$NDATE -$fhr $obsv_time`
      fday=${fcst_time:0:8}
      ihour=${fcst_time:8:2}
      hgefs_mbrs=0
      for mb in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 ; do
        hgefs=$EVSIN.${fday}/hgefs/hgefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2
        if [ -s $hgefs ] ; then
          hgefs_mbrs=$((hgefs_mbrs+1))
        fi
      done
      if [ $hgefs_mbrs -eq 62 ] ; then
        ihour_fhr_ok=$((ihour_fhr_ok+1))
      else
        ihour_fhr_missing=$((ihour_fhr_missing+1))
      fi
      fhr=$((fhr+6))
    done
  done
  echo "ihour_fhr_ok=$ihour_fhr_ok"
  echo "ihour_fhr_missing=$ihour_fhr_missing"
  if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
  else
    echo "at least there are some hgefs member files!"
    echo "Continue ..."
  fi
fi

if [ $var = gefs_apcp24h ] ; then 
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in 12 ; do 
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
   echo "ihour_fhr_ok=$ihour_fhr_ok"
   echo "ihour_fhr_missing=$ihour_fhr_missing"
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo "at least there are some gefs_apcp24h member files!"
    echo "Continue ..."
   fi    
fi 

if [ $var = aigefs_apcp24h ] ; then
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in 12 ; do
  obsv_time=${vday}${ihour}
  fhr=24
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    aigefs_apcp24h_mbrs=0
    for mb in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
      aigefs_apcp24h=$EVSIN.${fday}/aigefs/aigefs.ens${mb}.t${ihour}z.grid3.24h.f${hhh}.nc
      if [ -s $aigefs_apcp24h ] ; then
        aigefs_apcp24h_mbrs=$((aigefs_apcp24h_mbrs+1))
      fi
    done
    if [ $aigefs_apcp24h_mbrs -eq 31 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+12))
  done
 done
   echo "ihour_fhr_ok=$ihour_fhr_ok"
   echo "ihour_fhr_missing=$ihour_fhr_missing"
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo "at least there are some aigefs_apcp24h member files!"
    echo "Continue ..."
   fi
fi

if [ $var = hgefs_apcp24h ] ; then
 ihour_fhr_ok=0
 ihour_fhr_missing=0
 for ihour in 12 ; do
  obsv_time=${vday}${ihour}
  fhr=24
  while [ $fhr -le 384 ] ; do
    hhh=$fhr
    typeset -Z3 hhh
    fcst_time=`$NDATE -$fhr $obsv_time`
    fday=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    hgefs_apcp24h_mbrs=0
    for mb in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 ; do
      hgefs_apcp24h=$EVSIN.${fday}/hgefs/hgefs.ens${mb}.t${ihour}z.grid3.24h.f${hhh}.nc
      if [ -s $hgefs_apcp24h ] ; then
        hgefs_apcp24h_mbrs=$((hgefs_apcp24h_mbrs+1))
      fi
    done
    if [ $hgefs_apcp24h_mbrs -eq 62 ] ; then
      ihour_fhr_ok=$((ihour_fhr_ok+1))
    else
      ihour_fhr_missing=$((ihour_fhr_missing+1))
    fi
    fhr=$((fhr+12))
  done
 done
   echo "ihour_fhr_ok=$ihour_fhr_ok"
   echo "ihour_fhr_missing=$ihour_fhr_missing"
   if [ $ihour_fhr_ok -eq 0 ] ; then
    err_exit "ihour_missing_fhr=0 member files for all ihour and fhr are missing"
   else
    echo "at least there are some hgefs_apcp24h member files!"
    echo "Continue ..."
   fi
fi

