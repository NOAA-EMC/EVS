#!/bin/ksh

set +x
#For testing: 

#COMIN=/lfs/h2/emc/vpppg/noscrub/binbin.zhou/com/evs/v1.0/prep/global_ens/headline

var=$1
typeset -Z2 cyc


if [ $var = gfsanl ] ; then
  missing=0
  for cyc in 00 06 12 18 ; do
          if [ ! -s ${COMIN}.${vday}/gefs/gfsanl.t${cyc}z.grid3.f000.grib2 ] ; then
      missing=$((missing + 1 ))
    fi
  done

  echo "Missing gfsanl files = " $missing
  if [ $missing -eq 4  ] ; then
    echo "all of the gfsanl files are missing, exit execution!!!"
    exit
  else
    echo "gfsanl data are OK!"
  fi

fi


if [ $var = cmcanl ] ; then
  missing=0
  for cyc in 00 12 ; do
          if [ ! -s ${COMIN}.${vday}/cmce/cmcanl.t${cyc}z.grid3.f000.grib2 ] ; then
      missing=$((missing + 1 ))
    fi
  done

  echo "Missing cmcanl files = " $missing
  if [ $missing -eq 2  ] ; then
    echo "all of the cmcanl files are missing, exit execution!!!"
    exit
  else
    echo "cmcanl data are OK!"
  fi

fi


if [ $var = ecmanl ] ; then
  missing=0
  for cyc in 00 12 ; do
          if [ ! -s ${COMIN}.${vday}/ecme/ecmanl.t${cyc}z.grid3.f000.grib1 ] ; then
      missing=$((missing + 1 ))
    fi
  done

  echo "Missing ecmanl files = " $missing
  if [ $missing -eq 2  ] ; then
    echo "all of the ecmanl files are missing, exit execution!!!"
    exit
  else
    echo "ecmanl data are OK!"
  fi

fi


if [ $var = gfsanl_1.5deg ] ; then
  if [ ! -s ${COMIN}.${vday}/gefs/gfsanl.t00z.deg1.5.f000.grib2 ] ; then
    echo "gfsanl_1.5deg file is missing, exit execution!!!"
    exit
  else
    echo "gfsanl_1.5deg data is OK!"
  fi
fi

if [ $var = cmcanl_1.5deg ] ; then
  if [ ! -s ${COMIN}.${vday}/cmce/cmcanl.t00z.deg1.5.f000.grib2 ] ; then
      echo "cmcanl_1.5deg file is missing, exit execution!!!"
      exit
  else
      echo "cmcanl_1.5deg data is OK!"
  fi
fi




if [ $var = prepbufr ] ; then
  missing=0 
  for cyc in 00 06 12 18 ; do
	  if [ ! -s ${COMIN}.${vday}/gefs/gfs.t${cyc}z.prepbufr.f00.nc ] ; then
      missing=$((missing + 1 ))
    fi
  done

  echo "Missing prepbufr files = " $missing
  if [ $missing -eq 4  ] ; then
    echo "all of the preppbufr files are missing, exit execution!!!"
    exit
  else
    echo "prepbufr data are OK!" 
  fi

fi 


if [ $var = prepbufr_profile ] ; then
  missing=0
  for cyc in 00 06 12 18 ; do
          if [ ! -s ${COMIN}.${vday}/gefs/gfs.t${cyc}z.prepbufr_profile.f00.nc ] ; then
      missing=$((missing + 1 ))
    fi
  done

  echo "Missing prepbufr files = " $missing
  if [ $missing -eq 4  ] ; then
    echo "all of the preppbufr_profile files are missing, exit execution!!!"
    exit
  else
    echo "prepbufr_profile data are OK!"
  fi

fi


if [ $var = ccpa ] ; then

   if [ -s ${COMIN}.${vday}/gefs/ccpa.t12z.grid3.24h.f00.nc ] ; then
      echo "CCPA24h data is OK"
   else
      echo "CPA24h data is mssing"
      exit
   fi
fi 

if [ $var = osi_saf ]; then
    past=`$NDATE -24 ${vday}01`
    export vday1=${past:0:8}
    export period=multi.${vday1}00to${vday}00_G004

   if [ -s ${COMIN}.${vday}/osi_saf/osi_saf.${period}.nc ] ; then
        echo "OSI_SAF data is OK"
   else
        echo "OSI_SAF data is mssing"
        exit
   fi
fi

if [ $var = nohrsc ] ; then

   if [ -s ${COMIN}.${vday}/gefs/nohrsc.t00z.grid184.grb2 ] && [ -s ${COMIN}.${vday}/gefs/nohrsc.t12z.grid184.grb2 ] ; then
       echo "NOHRCS data is OK"
   else
      echo "NOHRSC data is mssing"
      exit
  fi
fi

if [ $var = ghrsst ] ; then

   if [ -s ${COMIN}.${vday}/gefs/ghrsst.t00z.nc ] ; then
       echo "GHRSST data is OK"
   else
       echo "GHRSST data is mssing"
       exit
  fi
fi


if [ $var = gefs ] || [ $var = gefs_bc ] ; then 

 cyc_fhr_ok=0
 cyc_fhr_missing=0
 if [  $var = gefs ] ; then
   cycs="00 06 12 18"
 else
   cycs="00 12"
 fi 

 for cyc in  $cycs ; do 

  obsv_cyc=${vday}${cyc}

  fhr=06

  while [ $fhr -le 384 ] ; do
    
    hhh=$fhr
    typeset -Z3 hhh

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    gefs_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do 
      gefs=$COMIN.${fday}/gefs/gefs.ens${mb}.t${fcyc}z.grid3.f${hhh}.grib2
      #echo $gefs

      if [ -s $gefs ] ; then
           gefs_mbrs=$((gefs_mbrs+1))
      fi	    
    done

    if [ $gefs_mbrs -eq 30 ] ; then
      #echo "gefs members = " $gefs_mbrs "  for cyc=$cyc  f${hhh} !!!"
      cyc_fhr_ok=$((cyc_fhr_ok+1))
    else  
      cyc_fhr_missing=$((cyc_fhr_missing+1))
    fi

    fhr=$((fhr+6))

  done
     
 done
   echo cyc_fhr_ok=$cyc_fhr_ok
   echo cyc_fhr_missing=$cyc_fhr_missing
   if [ $cyc_fhr_ok -eq 0 ] ; then
    echo cyc_missing_fhr=0 member files for all cyc and fhr are missing, exit execution of METPlus!
    exit
   else
    echo at least there are some gefs member files!
    echo Continue ...
   fi    
fi 




if [ $var = cmce ] || [ $var = cmce_bc ] ; then 

 cyc_fhr_ok=0
 cyc_fhr_missing=0
 for cyc in  00 12 ; do 

  obsv_cyc=${vday}${cyc}

  fhr=12

  while [ $fhr -le 384 ] ; do
    
    hhh=$fhr
    typeset -Z3 hhh

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    cmce_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do 
      cmce=$COMIN.${fday}/${var}/${var}.ens${mb}.t${fcyc}z.grid3.f${hhh}.grib2
      #echo $cmce

      if [ -s $cmce ] ; then
           cmce_mbrs=$((cmce_mbrs+1))
      fi	    
    done

    if [ $cmce_mbrs -eq 20 ] ; then
      #echo "cmce members = " $cmce_mbrs "  for cyc=$cyc  f${hhh} !!!"
      cyc_fhr_ok=$((cyc_fhr_ok+1))
    else  
      cyc_fhr_missing=$((cyc_fhr_missing+1))
    fi

    fhr=$((fhr+12))

  done
     
 done
   echo cyc_fhr_ok=$cyc_fhr_ok
   echo cyc_fhr_missing=$cyc_fhr_missing
   if [ $cyc_fhr_ok -eq 0 ] ; then
    echo cyc_missing_fhr=0 member files for all cyc and fhr are missing, exit execution of METPlus!
    exit
   else
    echo at least there are some cmce member files!
    echo Continue ...
   fi    
fi 




if [ $var = ecme ] ; then 

 cyc_fhr_ok=0
 cyc_fhr_missing=0
 for cyc in  00 12 ; do 

  obsv_cyc=${vday}${cyc}

  fhr=12

  while [ $fhr -le 384 ] ; do
    
    hhh=$fhr
    typeset -Z3 hhh

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    ecme_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 ; do 
      ecme=$COMIN.${fday}/ecme/ecme.ens${mb}.t${fcyc}z.grid4.f${hhh}.grib1
      #echo $ecme

      if [ -s $ecme ] ; then
           ecme_mbrs=$((ecme_mbrs+1))
      fi	    
    done

    if [ $ecme_mbrs -eq 50 ] ; then
      #echo "ecme members = " $ecme_mbrs "  for cyc=$cyc  f${hhh} !!!"
      cyc_fhr_ok=$((cyc_fhr_ok+1))
    else  
      cyc_fhr_missing=$((cyc_fhr_missing+1))
    fi

    fhr=$((fhr+12))

  done
     
 done
   echo cyc_fhr_ok=$cyc_fhr_ok
   echo cyc_fhr_missing=$cyc_fhr_missing
   if [ $cyc_fhr_ok -eq 0 ] ; then
    echo cyc_missing_fhr=0 member files for all cyc and fhr are missing, exit execution of METPlus!
    exit
   else
    echo at least there are some ecme member files!
    echo Continue ...
   fi    
fi 


if [ $var = gefs_apcp24h ] ; then 

 cyc_fhr_ok=0
 cyc_fhr_missing=0
 for cyc in  12 ; do 

  obsv_cyc=${vday}${cyc}

  fhr=24

  while [ $fhr -le 384 ] ; do
    
    hhh=$fhr
    typeset -Z3 hhh

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    gefs_apcp24h_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do 
    #for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 ; do 
      gefs_apcp24h=$COMIN.${fday}/gefs/gefs.ens${mb}.t${fcyc}z.grid3.24h.f${hhh}.nc
      #echo $gefs_apcp24h

      if [ -s $gefs_apcp24h ] ; then
           gefs_apcp24h_mbrs=$((gefs_apcp24h_mbrs+1))
      fi	    
    done

    if [ $gefs_apcp24h_mbrs -eq 30 ] ; then
      cyc_fhr_ok=$((cyc_fhr_ok+1))
    else  
      cyc_fhr_missing=$((cyc_fhr_missing+1))
    fi

    fhr=$((fhr+12))

  done
     
 done
   echo cyc_fhr_ok=$cyc_fhr_ok
   echo cyc_fhr_missing=$cyc_fhr_missing
   if [ $cyc_fhr_ok -eq 0 ] ; then
    echo cyc_missing_fhr=0 member files for all cyc and fhr are missing, exit execution of METPlus!
    exit
   else
    echo at least there are some gefs_apcp24h member files!
    echo Continue ...
   fi    
fi 




if [ $var = cmce_apcp24h ] ; then 

 cyc_fhr_ok=0
 cyc_fhr_missing=0
 for cyc in  12 ; do 

  obsv_cyc=${vday}${cyc}

  fhr=24

  while [ $fhr -le 384 ] ; do
    
    hhh=$fhr
    typeset -Z3 hhh

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    cmce_apcp24h_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do 
    #for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 ; do 
      cmce_apcp24h=$COMIN.${fday}/cmce/cmce.ens${mb}.t${fcyc}z.grid3.24h.f${hhh}.nc
      #echo $cmce_apcp24h

      if [ -s $cmce_apcp24h ] ; then
           cmce_apcp24h_mbrs=$((cmce_apcp24h_mbrs+1))
      fi	    
    done

    if [ $cmce_apcp24h_mbrs -eq 20 ] ; then
      cyc_fhr_ok=$((cyc_fhr_ok+1))
    else  
      cyc_fhr_missing=$((cyc_fhr_missing+1))
    fi

    fhr=$((fhr+12))

  done
     
 done
   echo cyc_fhr_ok=$cyc_fhr_ok
   echo cyc_fhr_missing=$cyc_fhr_missing
   if [ $cyc_fhr_ok -eq 0 ] ; then
    echo cyc_missing_fhr=0 member files for all cyc and fhr are missing, exit execution of METPlus!
    exit
   else
    echo at least there are some cmce_apcp24h member files!
    echo Continue ...
   fi    
fi 




if [ $var = ecme_apcp24h ] ; then 

 cyc_fhr_ok=0
 cyc_fhr_missing=0
 for cyc in  12 ; do 

  obsv_cyc=${vday}${cyc}

  fhr=24

  while [ $fhr -le 384 ] ; do
    
    hhh=$fhr
    typeset -Z3 hhh

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    ecme_apcp24h_mbrs=0
    #for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do 
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 ; do 
      ecme_apcp24h=$COMIN.${fday}/ecme/ecme.ens${mb}.t${fcyc}z.grid4.24h.f${hhh}.nc
      #echo $ecme_apcp24h

      if [ -s $ecme_apcp24h ] ; then
           ecme_apcp24h_mbrs=$((ecme_apcp24h_mbrs+1))
      fi	    
    done

    if [ $ecme_apcp24h_mbrs -eq 50 ] ; then
      cyc_fhr_ok=$((cyc_fhr_ok+1))
    else  
      cyc_fhr_missing=$((cyc_fhr_missing+1))
    fi

    fhr=$((fhr+12))

  done
     
 done
   echo cyc_fhr_ok=$cyc_fhr_ok
   echo cyc_fhr_missing=$cyc_fhr_missing
   if [ $cyc_fhr_ok -eq 0 ] ; then
    echo cyc_missing_fhr=0 member files for all cyc and fhr are missing, exit execution of METPlus!
    exit
   else
    echo at least there are some ecme_apcp24h member files!
    echo Continue ...
   fi    
fi 



if [ $var = gefs_icec_24h ] ; then 

 cyc_fhr_ok=0
 cyc_fhr_missing=0
 for cyc in 00 ; do 

  obsv_cyc=${vday}${cyc}

  fhr=24

  while [ $fhr -le 384 ] ; do
    
    hhh=$fhr
    typeset -Z3 hhh

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    gefs_icec_24h_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do 
    #for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 ; do 
      gefs_icec_24h=$COMIN.${fday}/gefs/gefs.ens${mb}.t${fcyc}z.grid3.icec_24h.f${hhh}.nc
      #echo $gefs_icec_24h

      if [ -s $gefs_icec_24h ] ; then
           gefs_icec_24h_mbrs=$((gefs_icec_24h_mbrs+1))
      fi	    
    done

    if [ $gefs_icec_24h_mbrs -eq 30 ] ; then
      cyc_fhr_ok=$((cyc_fhr_ok+1))
    else  
      cyc_fhr_missing=$((cyc_fhr_missing+1))
    fi

    fhr=$((fhr+12))

  done
     
 done
   echo cyc_fhr_ok=$cyc_fhr_ok
   echo cyc_fhr_missing=$cyc_fhr_missing
   if [ $cyc_fhr_ok -eq 0 ] ; then
    echo cyc_missing_fhr=0 member files for all cyc and fhr are missing, exit execution of METPlus!
    exit
   else
    echo at least there are some gefs_icec_24h member files!
    echo Continue ...
   fi    
fi 




if [ $var = gefs_sst24h ] ; then 

 cyc_fhr_ok=0
 cyc_fhr_missing=0
 for cyc in 00 ; do 

  obsv_cyc=${vday}${cyc}

  fhr=24

  while [ $fhr -le 384 ] ; do
    
    hhh=$fhr
    typeset -Z3 hhh

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    gefs_sst24h_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do 
    #for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 ; do 
      gefs_sst24h=$COMIN.${fday}/gefs/gefs.ens${mb}.t${fcyc}z.grid3.sst24h.f${hhh}.nc
      #echo $gefs_sst24h

      if [ -s $gefs_sst24h ] ; then
           gefs_sst24h_mbrs=$((gefs_sst24h_mbrs+1))
      fi	    
    done

    if [ $gefs_sst24h_mbrs -eq 30 ] ; then
      cyc_fhr_ok=$((cyc_fhr_ok+1))
    else  
      cyc_fhr_missing=$((cyc_fhr_missing+1))
    fi

    fhr=$((fhr+12))

  done
     
 done
   echo cyc_fhr_ok=$cyc_fhr_ok
   echo cyc_fhr_missing=$cyc_fhr_missing
   if [ $cyc_fhr_ok -eq 0 ] ; then
    echo cyc_missing_fhr=0 member files for all cyc and fhr are missing, exit execution of METPlus!
    exit
   else
    echo at least there are some gefs_sst24h member files!
    echo Continue
   fi    
fi 



if [ $var = gefs_WEASD ] ; then 

 cyc_fhr_ok=0
 cyc_fhr_missing=0
 for cyc in 00 12 ; do 

  obsv_cyc=${vday}${cyc}

  fhr=24

  while [ $fhr -le 384 ] ; do
    
    hhh=$fhr
    typeset -Z3 hhh

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    gefs_WEASD_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do 
    #for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 ; do 
      gefs_WEASD=$COMIN.${fday}/gefs/gefs.ens${mb}.t${fcyc}z.grid3.WEASD_24h.f${hhh}.nc
      #echo $gefs_WEASD

      if [ -s $gefs_WEASD ] ; then
           gefs_WEASD_mbrs=$((gefs_WEASD_mbrs+1))
      fi	    
    done

    if [ $gefs_WEASD_mbrs -eq 30 ] ; then
      cyc_fhr_ok=$((cyc_fhr_ok+1))
    else  
      cyc_fhr_missing=$((cyc_fhr_missing+1))
    fi

    fhr=$((fhr+12))

  done
     
 done
   echo cyc_fhr_ok=$cyc_fhr_ok
   echo cyc_fhr_missing=$cyc_fhr_missing
   if [ $cyc_fhr_ok -eq 0 ] ; then
    echo cyc_missing_fhr=0 member files for all cyc and fhr are missing, exit execution of METPlus!
    exit
   else
    echo at least there are some gefs_WEASD member files!
    echo Continue
   fi    
fi 



if [ $var = gefs_SNOD ] ; then 

 cyc_fhr_ok=0
 cyc_fhr_missing=0
 for cyc in 00 12 ; do 

  obsv_cyc=${vday}${cyc}

  fhr=24

  while [ $fhr -le 384 ] ; do
    
    hhh=$fhr
    typeset -Z3 hhh

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    gefs_SNOD_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do 
    #for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 ; do 
      gefs_SNOD=$COMIN.${fday}/gefs/gefs.ens${mb}.t${fcyc}z.grid3.SNOD_24h.f${hhh}.nc
      #echo $gefs_SNOD

      if [ -s $gefs_SNOD ] ; then
           gefs_SNOD_mbrs=$((gefs_SNOD_mbrs+1))
      fi	    
    done

    if [ $gefs_SNOD_mbrs -eq 30 ] ; then
      cyc_fhr_ok=$((cyc_fhr_ok+1))
    else  
      cyc_fhr_missing=$((cyc_fhr_missing+1))
    fi

    fhr=$((fhr+12))

  done
     
 done
   echo cyc_fhr_ok=$cyc_fhr_ok
   echo cyc_fhr_missing=$cyc_fhr_missing
   if [ $cyc_fhr_ok -eq 0 ] ; then
    echo cyc_missing_fhr=0 member files for all cyc and fhr are missing, exit execution of METPlus!
    exit
   else
    echo at least there are some gefs_SNOD member files!
    echo Continue
   fi    
fi 




if [ $var = cmce_SNOD ] ; then 

 cyc_fhr_ok=0
 cyc_fhr_missing=0
 for cyc in 00 12 ; do 

  obsv_cyc=${vday}${cyc}

  fhr=24

  while [ $fhr -le 384 ] ; do
    
    hhh=$fhr
    typeset -Z3 hhh

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    cmce_SNOD_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20; do 
    #for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 ; do 
      cmce_SNOD=$COMIN.${fday}/cmce/cmce.ens${mb}.t${fcyc}z.grid3.SNOD_24h.f${hhh}.nc
      #echo $cmce_SNOD

      if [ -s $cmce_SNOD ] ; then
           cmce_SNOD_mbrs=$((cmce_SNOD_mbrs+1))
      fi	    
    done

    if [ $cmce_SNOD_mbrs -eq 20 ] ; then
      cyc_fhr_ok=$((cyc_fhr_ok+1))
    else  
      cyc_fhr_missing=$((cyc_fhr_missing+1))
    fi

    fhr=$((fhr+12))

  done
     
 done
   echo cyc_fhr_ok=$cyc_fhr_ok
   echo cyc_fhr_missing=$cyc_fhr_missing
   if [ $cyc_fhr_ok -eq 0 ] ; then
    echo cyc_missing_fhr=0 member files for all cyc and fhr are missing, exit execution of METPlus!
    exit
   else
    echo at least there are some cmce_SNOD member files!
    echo Continue
   fi    
fi 





if [ $var = cmce_WEASD ] ; then 

 cyc_fhr_ok=0
 cyc_fhr_missing=0
 for cyc in 00 12 ; do 

  obsv_cyc=${vday}${cyc}

  fhr=24

  while [ $fhr -le 384 ] ; do
    
    hhh=$fhr
    typeset -Z3 hhh

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    cmce_WEASD_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20; do 
    #for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 ; do 
      cmce_WEASD=$COMIN.${fday}/cmce/cmce.ens${mb}.t${fcyc}z.grid3.WEASD_24h.f${hhh}.nc
      #echo $cmce_WEASD

      if [ -s $cmce_WEASD ] ; then
           cmce_WEASD_mbrs=$((cmce_WEASD_mbrs+1))
      fi	    
    done

    if [ $cmce_WEASD_mbrs -eq 20 ] ; then
      cyc_fhr_ok=$((cyc_fhr_ok+1))
    else  
      cyc_fhr_missing=$((cyc_fhr_missing+1))
    fi

    fhr=$((fhr+12))

  done
     
 done
   echo cyc_fhr_ok=$cyc_fhr_ok
   echo cyc_fhr_missing=$cyc_fhr_missing
   if [ $cyc_fhr_ok -eq 0 ] ; then
    echo cyc_missing_fhr=0 member files for all cyc and fhr are missing, exit execution of METPlus!
    exit
   else
    echo at least there are some cmce_WEASD member files!
    echo Continue
   fi    
fi 




if [ $var = ecme_weasd ] ; then 

 cyc_fhr_ok=0
 cyc_fhr_missing=0
 for cyc in 00 12 ; do 

  obsv_cyc=${vday}${cyc}

  fhr=24

  while [ $fhr -le 384 ] ; do
    
    hhh=$fhr
    typeset -Z3 hhh

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    ecme_weasd_mbrs=0
    #for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20; do 
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 ; do 
      ecme_weasd=$COMIN.${fday}/ecme/ecme.ens${mb}.t${fcyc}z.grid4.weasd_24h.f${hhh}.nc
      #echo $ecme_weasd

      if [ -s $ecme_weasd ] ; then
           ecme_weasd_mbrs=$((ecme_weasd_mbrs+1))
      fi	    
    done

    if [ $ecme_weasd_mbrs -eq 50 ] ; then
      cyc_fhr_ok=$((cyc_fhr_ok+1))
    else  
      cyc_fhr_missing=$((cyc_fhr_missing+1))
    fi

    fhr=$((fhr+12))

  done
     
 done
   echo cyc_fhr_ok=$cyc_fhr_ok
   echo cyc_fhr_missing=$cyc_fhr_missing
   if [ $cyc_fhr_ok -eq 0 ] ; then
    echo cyc_missing_fhr=0 member files for all cyc and fhr are missing, exit execution of METPlus!
    exit
   else
    echo at least there are some ecme_weasd member files!
    echo Continue ...
   fi    
fi 




if [ $var = headline_gefs ] ; then 

 cyc_fhr_ok=0
 cyc_fhr_missing=0

 for cyc in  00 ; do 

  obsv_cyc=${vday}${cyc}

  fhr=024

  while [ $fhr -le 384 ] ; do
    
    hhh=$fhr
    typeset -Z3 hhh

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    gefs_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do 
      gefs=$COMIN.${fday}/gefs/gefs.ens${mb}.t${fcyc}z.grid3.f${hhh}.grib2
      #echo $gefs

      if [ -s $gefs ] ; then
           gefs_mbrs=$((gefs_mbrs+1))
      fi	    
    done

    if [ $gefs_mbrs -eq 30 ] ; then
      #echo "gefs members = " $gefs_mbrs "  for cyc=$cyc  f${hhh} !!!"
      cyc_fhr_ok=$((cyc_fhr_ok+1))
    else  
      cyc_fhr_missing=$((cyc_fhr_missing+1))
    fi

    fhr=$((fhr+24))

  done
     
 done
   echo cyc_fhr_ok=$cyc_fhr_ok
   echo cyc_fhr_missing=$cyc_fhr_missing
   if [ $cyc_fhr_ok -eq 0 ] ; then
    echo cyc_missing_fhr=0 member files for all cyc and fhr are missing, exit execution of METPlus!
    exit
   else
    echo at least there are some gefs member files!
    echo Continue ...
   fi    
fi 



if [ $var = headline_cmce ] ; then 

 cyc_fhr_ok=0
 cyc_fhr_missing=0
 for cyc in  00 ; do 

  obsv_cyc=${vday}${cyc}

  fhr=024

  while [ $fhr -le 384 ] ; do
    
    hhh=$fhr
    typeset -Z3 hhh

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    cmce_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do 
      cmce=$COMIN.${fday}/cmce/cmce.ens${mb}.t${fcyc}z.grid3.f${hhh}.grib2
      #echo $cmce

      if [ -s $cmce ] ; then
           cmce_mbrs=$((cmce_mbrs+1))
      fi	    
    done

    if [ $cmce_mbrs -eq 20 ] ; then
      #echo "cmce members = " $cmce_mbrs "  for cyc=$cyc  f${hhh} !!!"
      cyc_fhr_ok=$((cyc_fhr_ok+1))
    else  
      cyc_fhr_missing=$((cyc_fhr_missing+1))
    fi

    fhr=$((fhr+24))

  done
     
 done
   echo cyc_fhr_ok=$cyc_fhr_ok
   echo cyc_fhr_missing=$cyc_fhr_missing
   if [ $cyc_fhr_ok -eq 0 ] ; then
    echo cyc_missing_fhr=0 member files for all cyc and fhr are missing, exit execution of METPlus!
    exit
   else
    echo at least there are some cmce member files!
    echo Continue ...
   fi    
fi 

if [ $var = headline_gfsanl ] ; then
    if [ ! -s ${COMIN}.${vday}/gefs/gfsanl.t00z.grid3.f000.grib2 ] ; then
      echo " gfsanl file missing, exit execution!!!"
      exit
     else
       echo "gfsanl data is OK!"
       echo Continue ...
     fi
fi

if [ $var = headline_cmcanl ] ; then
    if [ ! -s ${COMIN}.${vday}/cmce/cmcanl.t00z.grid3.f000.grib2 ] ; then
        echo " cmcanl file missing, exit execution!!!"
        exit
    else
         echo "cmcanl data is OK!"
	 echo Continue ...
    fi
fi


if [ $var = headline_gfs ] ; then 

 for cyc in  00 ; do 

  obsv_cyc=${vday}${cyc}
  fhr=024

  while [ $fhr -le 384 ] ; do
    
    hhh=$fhr
    typeset -Z3 hhh

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    gfs=$COMIN.${fday}/gefs/gfs.t${fcyc}z.grid3.f${hhh}.grib2
    if [ ! -s $gfs ] ; then
      echo $gfs not existing, exit METplus execution!
      exit
    fi 

    fhr=$((fhr+24))

  done
     
 done

    echo Continue ...
fi 





if [ $var = wmo_cmce ] ; then 

 echo COM_IN=$COM_IN
 cyc_fhr_ok=0
 cyc_fhr_missing=0
 for cyc in  00 ; do 

  obsv_cyc=${vday}${cyc}

  fhr=024

  while [ $fhr -le 384 ] ; do
    
    hhh=$fhr
    typeset -Z3 hhh

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    cmce_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do 
      cmce=$COM_IN/atmos.${fday}/cmce/cmce.ens${mb}.t${fcyc}z.grid3.f${hhh}.grib2
      #echo $cmce

      if [ -s $cmce ] ; then
           cmce_mbrs=$((cmce_mbrs+1))
      fi	    
    done

    if [ $cmce_mbrs -eq 20 ] ; then
      cyc_fhr_ok=$((cyc_fhr_ok+1))
    else  
      cyc_fhr_missing=$((cyc_fhr_missing+1))
    fi

    fhr=$((fhr+24))

  done
     
 done
   echo cyc_fhr_ok=$cyc_fhr_ok
   echo cyc_fhr_missing=$cyc_fhr_missing
   if [ $cyc_fhr_ok -eq 0 ] ; then
    echo cyc_missing_fhr=0 member files for all cyc and fhr are missing, exit execution of METPlus!
    exit
   else
    echo at least there are some cmce member files!
    echo Continue ...
   fi    
fi 

if [ $var = wmo_cmcanl ] ; then
  if [ ! -s ${COM_IN}/atmos.${vday}/cmce/cmcanl.t00z.grid3.f000.grib2 ] ; then
      echo " cmcanl file missing, exit execution!!!"
      exit
  else
     echo "cmcanl data is OK!"
     echo Continue ...
  fi
fi




if [ $var = wmo_gefs ] ; then 

 cyc_fhr_ok=0
 cyc_fhr_missing=0
 for cyc in  00 ; do 

  obsv_cyc=${vday}${cyc}

  fhr=024

  while [ $fhr -le 384 ] ; do
    
    hhh=$fhr
    typeset -Z3 hhh

    fcst_time=`$NDATE -$fhr $obsv_cyc`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

    gefs_mbrs=0
    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30; do 
      gefs=$COM_IN/atmos.${fday}/gefs/gefs.ens${mb}.t${fcyc}z.grid3.f${hhh}.grib2
      #echo $gefs

      if [ -s $gefs ] ; then
           gefs_mbrs=$((gefs_mbrs+1))
      fi	    
    done

    if [ $gefs_mbrs -eq 30 ] ; then
      cyc_fhr_ok=$((cyc_fhr_ok+1))
    else  
      cyc_fhr_missing=$((cyc_fhr_missing+1))
    fi

    fhr=$((fhr+24))

  done
     
 done
   echo cyc_fhr_ok=$cyc_fhr_ok
   echo cyc_fhr_missing=$cyc_fhr_missing
   if [ $cyc_fhr_ok -eq 0 ] ; then
    echo cyc_missing_fhr=0 member files for all cyc and fhr are missing, exit execution of METPlus!
    exit
   else
    echo at least there are some gefs member files!
    echo Continue ...
   fi    
fi 


if [ $var = wmo_gfsanl ] ; then
   if [ ! -s ${COM_IN}/atmos.${vday}/gefs/gfsanl.t00z.grid3.f000.grib2 ] ; then
       echo " gfsanl file missing, exit execution!!!"
       exit
   else
       echo "gfsanl data is OK!"
       echo Continue ...
   fi
fi

