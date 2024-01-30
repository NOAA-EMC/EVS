#!/bin/ksh
################################################################################################
# Purpose: 
#             1. Retrive/regrid analysis/observational data (to1 degree and to 1.5 degree for WMO)
#             2. Retrive required fields from large opreational global ensemble forecast
#                member files (grib2 GEFS, CMCE, and grib1 ECME ) and form smaller member files
#             3. Regrid the smaller files to required grid (1x1 degree) for GEFS and CMCE
#                But the retrived grib1 ECME files are still kept in original grid since wgrib
#                has limited regrid capability for regriding grib1 files. The regrid for ECME
#                will be done by METplus during the verification processes
#             4. For CMCE grib2 files, reverse North-South direction (by wgrib2) since the CMCE
#                grib2 files have reversed North-South direction to GEFS member files
#             5. Store the well-formed analysis/observational, and  smaller ensemble member
#                files in the evs prep sub-directory /prep/global_ens/atmos.YYYYMMDD
#
# Last updated 11/15/2023: by  Binbin Zhou, Lynker@EMC/NCEP
#
##################################################################################################
set -x

modnam=$1
gens_ihour=$2
fhr_beg=$3
fhr_end=$4

export vday=${INITDATE:-$PDYm2}    #for ensemble, use past-2 day as validation day
export vdate=${vdate:-$vday$ihour}

cd $WORK

####################################################################################
#Get gfs analysis grib2 data in GRID#3 (1-degree global)
#  and WMO 1.5 deg verification for 00Z
# NOTE: There are no U10, V10 in GFS analysis, so use GFS*f000 as alternative
###################################################################################
if [ $modnam = gfsanl ]; then
  for ihour in 00 06 12 18 ; do
    if [ ! -s $COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.anl ] ; then
      if [ $SENDMAIL = YES ]; then
        export subject="GFS Analysis Data Missing for EVS ${COMPONENT}"
        echo "Warning: No GFS analysis available for ${vday}${ihour}" > mailmsg
        echo "Missing file is $COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.anl" >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $MAILTO
      fi
    else
      cpreq -v $COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.anl $WORK/gfsanl.t${ihour}z.grid3.f000.grib2
    fi
    if [ ! -s $COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.f000 ]; then
      if [ $SENDMAIL = YES ]; then
        export subject="GFS F000 Data Missing for EVS ${COMPONENT}"
        echo "Warning: No GFS F000 available for ${vday}${ihour}" > mailmsg
        echo "Missing file is $COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.f000" >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $MAILTO
      fi
    else
      GFSf000=$COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.f000
      $WGRIB2  $GFSf000|grep "UGRD:10 m above ground"|$WGRIB2 -i $GFSf000 -grib $WORK/U10_f000.${ihour}
      cat $WORK/U10_f000.${ihour} >> $WORK/gfsanl.t${ihour}z.grid3.f000.grib2
      $WGRIB2  $GFSf000|grep "VGRD:10 m above ground"|$WGRIB2 -i $GFSf000 -grib $WORK/V10_f000.${ihour}
      cat $WORK/V10_f000.${ihour} >> $WORK/gfsanl.t${ihour}z.grid3.f000.grib2
    fi
    [[ $SENDCOM="YES" ]] && cpreq -v $WORK/gfsanl.t${ihour}z.grid3.f000.grib2 $COMOUTgefs/gfsanl.t${ihour}z.grid3.f000.grib2
 done
 if [ -s $COMOUTgefs/gfsanl.t00z.grid3.f000.grib2 ]; then
    $WGRIB2 $COMOUTgefs/gfsanl.t00z.grid3.f000.grib2 -set_grib_type same -new_grid_winds earth -new_grid latlon 0:240:1.5 -90:121:1.5 $WORK/gfsanl.t00z.deg1.5.f000.grib2
    [[ $SENDCOM="YES" ]] && cpreq -v $WORK/gfsanl.t00z.deg1.5.f000.grib2 $COMOUTgefs/gfsanl.t00z.deg1.5.f000.grib2
 fi
fi

#############################################################
#Get cmc analysis grib2 data in GRID#3 (1-degree global)
#  and WMO 1.5 deg verification for 00Z
# NOTE: CMCE has no DPT
#############################################################
if [ $modnam = cmcanl ]; then

  pat=pattern.$modnam
  # Create a file of patterns to use with grep.  This way we only need one grep
  if [ -e ${pat} ]; then rm ${pat}; fi
  >${pat}
  # Upper air
  for level in 10 50 100 200 250 300 400 500 700 850 925 1000 ; do
   echo "UGRD:$level mb" >> ${pat}
   echo "VGRD:$level mb" >> ${pat}
  done
  echo "HGT:" >> ${pat}
  echo "TMP:" >> ${pat}
  echo "UGRD:10 m " >> ${pat}
  echo "VGRD:10 m " >> ${pat}
  # Surface
  echo "PRMSL:" >> ${pat}
  echo "RH:" >> ${pat}

  for ihour in 00 12; do
      origin=$COMINcmce/cmce.$vday/$ihour/pgrb2ap5
      if [ -s $COMINcmce/cmce.$vday/$ihour/pgrb2ap5/cmc_gec00.t${ihour}z.pgrb2a.0p50.anl ] ; then
        cmcanl=$origin/cmc_gec00.t${ihour}z.pgrb2a.0p50.anl
      elif [ -s $COMINcmce/cmce.$vday/$ihour/pgrb2ap5/cmc_gec00.t${ihour}z.pgrb2a.0p50.f000 ] ; then
        cmcanl=$origin/cmc_gec00.t${ihour}z.pgrb2a.0p50.f000	
        echo "WARNING: $COMINcmce/cmce.$vday/$ihour/pgrb2ap5/cmc_gec00.t${ihour}z.pgrb2a.0p50.anl does not exist, using $origin/cmc_gec00.t${ihour}z.pgrb2a.0p50.f000"
      else
        echo "WARNING: No $COMINcmce/cmce.$vday/$ihour/pgrb2ap5/cmc_gec00.t${ihour}z.pgrb2a.0p50.anl or $origin/cmc_gec00.t${ihour}z.pgrb2a.0p50.f000 file available"
      fi
      if [ ! -s $cmcanl ] ; then
       if [ $SENDMAIL = YES ]; then
         export subject="CMC Analysis Data Missing for EVS ${COMPONENT}"
         echo "Warning: No CMC analysis available for ${vday}${ihour}" > mailmsg
         echo "Missing file is $cmcanl" >> mailmsg
         echo "Job ID: $jobid" >> mailmsg
         cat mailmsg | mail -s "$subject" $MAILTO
       fi
      else
       >$WORK/cmce.upper.${ihour}.gec00.anl
       >$WORK/cmce.sfc.${ihour}.gec00.anl

       $WGRIB2 $cmcanl | grep --file=${pat} | grep "anl:ENS=low-res" | $WGRIB2 -i $cmcanl -grib ${WORK}/grabcmcanl.${ihour}
#       $WGRIB2 $WORK/cmce.upper.${ihour}.gec00.anl -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003 $WORK/cmcanl.t${ihour}z.grid3.f000.grib2
        $WGRIB2 ${WORK}/grabcmcanl.${ihour} -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003 $WORK/cmcanl.t${ihour}z.grid3.f000.grib2 
	
       [[ $SENDCOM="YES" ]] && cpreq -v $WORK/cmcanl.t${ihour}z.grid3.f000.grib2 $COMOUTcmce/cmcanl.t${ihour}z.grid3.f000.grib2
    fi
  done

   for ihour in 00 12; do
    rm ${WORK}/grabcmcanl.${ihour}
   done
   rm ${pat}

  if [ -s $COMOUTcmce/cmcanl.t00z.grid3.f000.grib2 ]; then
      $WGRIB2 $COMOUTcmce/cmcanl.t00z.grid3.f000.grib2 -set_grib_type same -new_grid_winds earth -new_grid latlon 0:240:1.5 -90:121:1.5 $WORK/cmcanl.t00z.deg1.5.f000.grib2
      [[ $SENDCOM="YES" ]] && cpreq -v $WORK/cmcanl.t00z.deg1.5.f000.grib2 $COMOUTcmce/cmcanl.t00z.deg1.5.f000.grib2
  fi
fi

############################################################
#Get GEFS member grib2 file in grid3 
#  Note: for GEFS get data at all 4 cycles 00,06,12 and 18Z
#        specified by $gens_ihour
###########################################################
if [ $modnam = gefs ] ; then
  total=30

  if [ ! -s $WORK/gefs.ens30.t12z.grid3.f384.grib2 ] ; then
    tmpDir=$WORK/${modnam}.${fhr_beg}
    mkdir -p $tmpDir

    # Create a file of patterns to use with grep.  This way we only need one grep
    pat0=${tmpDir}/pattern0.${modnam}.${gens_ihour}.${fhr_beg}
    pat1=${tmpDir}/pattern1.${modnam}.${gens_ihour}.${fhr_beg}

    if [ -e ${pat0} ]; then rm ${pat0}; fi
    >${pat0}

    for level in 10 50 100 200 250 300 400 500 700 850 925 1000 ; do
         echo "UGRD:$level mb" >> ${pat0}
         echo "VGRD:$level mb" >> ${pat0}
    done
    # Upper air
    echo "HGT:" >> ${pat0}
    echo "TMP:" >> ${pat0} 
    echo "UGRD:10 m" >> ${pat0}
    echo "VGRD:10 m" >> ${pat0}
    echo "RH:" >> ${pat0}
    # Surface
    echo "TCDC:" >> ${pat0}
    echo "APCP:" >> ${pat0}
    echo "WEASD:" >> ${pat0}
    echo "SNOD:" >> ${pat0}
    echo "PRMSL:" >> ${pat0}

    # Upper from CVC
    if [ -e ${pat1} ]; then rm ${pat1}; fi
    >${pat1}
    echo "DPT:2 m" >> ${pat1}
    echo "VIS:surface" >> ${pat1}
    echo "CAPE:surface" >> ${pat1}
    echo "HGT:cloud ceiling" >> ${pat1}
    echo "ICEC:surface" >> ${pat1}
    echo "TMP:surface" >> ${pat1}
    #echo "SPFH:" >> ${pat1}


  for ihour in $gens_ihour  ; do
    origin=$COMINgefs/gefs.$vday/$ihour/atmos/pgrb2ap5
    origin_cvc=$COMINgefs/gefs.$vday/$ihour/atmos/pgrb2bp5
    mbr=1
    while [ $mbr -le $total ] ; do
      mb=$mbr
      typeset -Z2 mb
      nfhrs=$fhr_beg
      while [ $nfhrs -le $fhr_end ] ; do
        hhh=$nfhrs
        typeset -Z3 hhh
        gefs=$origin/gep${mb}.t${ihour}z.pgrb2a.0p50.f${hhh}
        gefs_cvc=$origin_cvc/gep${mb}.t${ihour}z.pgrb2b.0p50.f${hhh} 
        >$WORK/gefs.upper.${ihour}.${mb}.${hhh}
        >$WORK/gefs.sfc.${ihour}.${mb}.${hhh}
        if [ ! -s $gefs ]; then
          if [ $SENDMAIL = YES ]; then
            export subject="GEFS Member ${mb} F${hhh} Data Missing for EVS ${COMPONENT}"
            echo "Warning: No GEFS Member ${mb} F${hhh} available for ${vday}${ihour}" > mailmsg
            echo "Missing file is $gefs" >> mailmsg
            echo "Job ID: $jobid" >> mailmsg
            cat mailmsg | mail -s "$subject" $MAILTO
          fi
        else
          grabgefs=${tmpDir}/grabgefs.${ihour}.${mb}.${hhh}
	  x=${tmpDir}/x.${ihour}.${mb}.${hhh}

	  $WGRIB2 $gefs     | grep --file=${pat0} | $WGRIB2 -i $gefs     -grib ${grabgefs}
        fi
        if [ ! -s $gefs_cvc ]; then
          if [ $SENDMAIL = YES ]; then
            export subject="GEFS Member ${mb} F${hhh} Data Missing for EVS ${COMPONENT}"
            echo "Warning: No GEFS Member ${mb} F${hhh} available for ${vday}${ihour}" > mailmsg
            echo "Missing file is $gefs_cvc" >> mailmsg
            echo "Job ID: $jobid" >> mailmsg
            cat mailmsg | mail -s "$subject" $MAILTO
          fi
        else
          $WGRIB2 $gefs_cvc | grep --file=${pat1} | $WGRIB2 -i $gefs_cvc -grib ${x}
	  cat ${x} >> ${grabgefs}
        fi
#        $WGRIB2 $WORK/gefs.upper.${ihour}.${mb}.${hhh} -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003  $WORK/gefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2
        $WGRIB2 ${grabgefs} -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003 $WORK/gefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2 
        [[ $SENDCOM="YES" ]] && cpreq -v $WORK/gefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2 $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2
        nfhrs=`expr $nfhrs + 6`
      done # forecast hour

      for hhh in $(seq --format=%03g $fhr_beg 6 $fhr_end ); do
         rm ${tmpDir}/grabgefs.${ihour}.${mb}.${hhh}
      done

      mbr=`expr $mbr + 1`
    done # member
  done # ihour
  rm ${pat0} ${pat1}
 fi # check if file not existing
fi

##############################################################
#Get CMCE member grib2 file in grid3 
#  Note: for CMCE, get data at 2 cycles 00 and 12Z
#        specified by $gens_ihour
##############################################################
if [ $modnam = cmce ] ; then
  total=20

   tmpDir=$WORK/${modnam}
   mkdir -p ${tmpDir}

  # Create a file of patterns to use with grep.  This way we only need one grep
  pat=${tmpDir}/pattern.${gens_ihour}.${fhr_beg}
  if [ -e ${pat} ]; then rm ${pat}; fi
  >${pat}
  for level in 10 50 100 200 250 300 400 500 700 850 925 1000 ; do
     echo "UGRD:$level mb" >> ${pat}
     echo "VGRD:$level mb" >> ${pat}
  done
  # Upper air
  echo "HGT:" >> ${pat}
  echo "TMP:" >> ${pat}
  echo "UGRD:10 m" >> ${pat}
  echo "VGRD:10 m" >> ${pat}
  echo "RH:" >> ${pat}
  # Surface
  echo "TCDC:local level" >> ${pat}
  echo "APCP:" >> ${pat}
  echo "WEASD:" >> ${pat}
  echo "SNOD:" >> ${pat}
  echo "PRMSL:" >> ${pat}
  echo "CAPE:atmos col" >> ${pat}
  #echo "SPFH:" >> ${pat}

  for ihour in $gens_ihour ; do
    origin=$COMINcmce/cmce.$vday/$ihour/pgrb2ap5
    mbr=1
    while [ $mbr -le $total ] ; do
      mb=$mbr
      typeset -Z2 mb
      nfhrs=$fhr_beg
      while [ $nfhrs -le $fhr_end ] ; do
        h3=$nfhrs
        typeset -Z3 h3
        cmce=$origin/cmc_gep${mb}.t${ihour}z.pgrb2a.0p50.f${h3}
        >$WORK/cmce.upper.${ihour}.${mb}.${h3}
        >$WORK/cmce.sfc.${ihour}.${mb}.${h3}
        if [ ! -s $cmce ]; then
          if [ $SENDMAIL = YES ]; then
            export subject="CMCE Member ${mb} F${h3} Data Missing for EVS ${COMPONENT}"
            echo "Warning: No CMCE Member ${mb} F${h3} available for ${vday}${ihour}" > mailmsg
            echo "Missing file is $cmce" >> mailmsg
            echo "Job ID: $jobid" >> mailmsg
            cat mailmsg | mail -s "$subject" $MAILTO
          fi
        else
	 
	  grabcmce=${tmpDir}/grabcmce.${ihour}.${mb}.${h3}

	  $WGRIB2  $cmce|grep --file=${pat}|$WGRIB2 -i $cmce -grib ${grabcmce}


	  #****************************************************************************************
	  #Note:  SPFH is still not available. So close this one
          #$WGRIB2 $cmce|grep "SPFH:"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
          #cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.sfc.${ihour}.${mb}.${h3}
          #echo "cmce.upper" | $EXECevs_g2g/evs_g2g_adjustCMC.x
          #cat $WORK/cmce.sfc >> $WORK/cmce.upper.adjusted
          #*****************************************************************************************

	  #********************************************************************************
          #In MET, not necessary to adjust upper level fields for CMCE members since
          #MET  uses string of field name to read data
          #Hrer, use WGRIB2 to reverse N-S grid direction and convert 0.5x0.5 deg to 1x1 deg
	  #********************************************************************************
          $WGRIB2 ${grabcmce} -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003  $WORK/cmce.ens${mb}.t${ihour}z.grid3.f${h3}.grib2
          [[ $SENDCOM="YES" ]] && cpreq -v $WORK/cmce.ens${mb}.t${ihour}z.grid3.f${h3}.grib2 $COMOUTcmce/cmce.ens${mb}.t${ihour}z.grid3.f${h3}.grib2
        fi 
        nfhrs=`expr $nfhrs + 12`
      done # forecast hour


     for h3 in $(seq --format=%03g $fhr_beg 12 $fhr_end ); do
       rm ${tmpDir}/grabcmce.${ihour}.${mb}.${h3}
     done

      mbr=`expr $mbr + 1`
    done # member
  done # ihour
  rm ${pat}
fi

###########################################
#Get ECM members
# NOTE: all files are in non-NCEP but in ECMWF GRIB1 format
###########################################
if [ $modnam = ecme ] ; then
  echo "getting ECMWF ensemble member files ...."
  export outdata=$COMOUTecme
  for ihour in 00 12 ; do
    $USHevs/global_ens/evs_process_atmos_ecme.sh ${vday}${ihour} ${ihour} 
  done 
fi

#############################################################
# Run GDAS prepbufr files through PB2NC
#############################################################
if [ $modnam = prepbufr ] ; then
   > run_pb2nc.sh
   for ihour in 00 06 12 18 ; do
      > run_pb2nc.${ihour}.sh
      echo  "export output_base=${WORK}/pb2nc" >> run_pb2nc.${ihour}.sh
      echo  "export vbeg=${ihour}" >> run_pb2nc.${ihour}.sh
      echo  "export vend=${ihour}" >> run_pb2nc.${ihour}.sh
      if [ -s $COMINobsproc/gdas.${vday}/${ihour}/atmos/gdas.t${ihour}z.prepbufr ] ; then
        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsGFS_Prepbufr.conf" >> run_pb2nc.${ihour}.sh  
        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsGFS_Prepbufr_Profile.conf" >> run_pb2nc.${ihour}.sh  
      else
	if [ $SENDMAIL = YES ]; then
          export subject="Prepbufr  Data Missing for EVS ${COMPONENT}"
          echo "Warning:  No prepbufr analysis available for ${vday}${ihour}" > mailmsg
          echo "Missing file is $COMINobsproc/gdas.${vday}/${ihour}/atmos/gdas.t${ihour}z.prepbufr"  >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
	fi
      fi 
      chmod +x run_pb2nc.${ihour}.sh
      echo "${DATA}/run_pb2nc.${ihour}.sh" >> run_pb2nc.sh
  done
  echo "chmod 640 ${WORK}/pb2nc/prepbufr_nc/*prepbufr*.nc" >> run_pb2nc.sh
  echo "chgrp rstprod ${WORK}/pb2nc/prepbufr_nc/*prepbufr*.nc" >> run_pb2nc.sh
  echo "cpreq -v ${WORK}/pb2nc/prepbufr_nc/*.nc $COMOUTgefs" >> run_pb2nc.sh
  echo "chmod 640 $COMOUTgefs/*prepbufr*.nc" >> run_pb2nc.sh
  echo "chgrp rstprod $COMOUTgefs/*prepbufr*.nc" >> run_pb2nc.sh
  chmod +x run_pb2nc.sh
  ${DATA}/run_pb2nc.sh
fi  

#############################################################
# Get CCPA 6 hour accumulation and run through PCPCombine
#  to get 24 hour accumulation
#############################################################
if [ $modnam = ccpa ] ; then
  day1=$($NDATE -24 ${vday}12)
  export vday_1=${day1:0:8}
  for ihour in 00 06 12 18 ; do
    if [ -s $COMINccpa/ccpa.${vday}/$ihour/ccpa.t${ihour}z.06h.1p0.conus.gb2 ] ; then
      $WGRIB2 $COMINccpa/ccpa.${vday}/$ihour/ccpa.t${ihour}z.06h.1p0.conus.gb2 -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003  $WORK/ccpa.t${ihour}z.grid3.06h.f00.grib2
      [[ $SENDCOM="YES" ]] && cpreq -v $WORK/ccpa.t${ihour}z.grid3.06h.f00.grib2 ${COMOUTgefs}/ccpa.t${ihour}z.grid3.06h.f00.grib2
    else
        if [ $SENDMAIL = YES ]; then
          export subject="CCPA  Data Missing for EVS ${COMPONENT}"
          echo "Warning:  No CCPA analysis available for ${INITDATE}${ihour}" > mailmsg
          echo "Missing file is $COMINccpa/ccpa.${vday}/$ihour/ccpa.t${ihour}z.06h.1p0.conus.gb2"  >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
	fi
    fi 
  done
  export output_base=${WORK}/precip
  export ccpa24=${WORK}/ccpa24
  mkdir -p $ccpa24
  for ihour in 12 ; do
    nccpa_file=1
    while [ $nccpa_file -le 4 ]; do
        if [ $nccpa_file -eq 1 ]; then
            source_ccpa_file=${COMIN}/$STEP/${COMPONENT}/atmos.${vday}/gefs/ccpa.t12z.grid3.06h.f00.grib2
        elif [ $nccpa_file -eq 2 ]; then
            source_ccpa_file=${COMIN}/$STEP/${COMPONENT}/atmos.${vday}/gefs/ccpa.t06z.grid3.06h.f00.grib2
        elif [ $nccpa_file -eq 3 ]; then
            source_ccpa_file=${COMIN}/$STEP/${COMPONENT}/atmos.${vday}/gefs/ccpa.t00z.grid3.06h.f00.grib2
        elif [ $nccpa_file -eq 4 ]; then
            source_ccpa_file=${COMIN}/$STEP/${COMPONENT}/atmos.${vday_1}/gefs/ccpa.t18z.grid3.06h.f00.grib2
        fi
        if [ -s $source_ccpa_file ]; then
            cpreq -v $source_ccpa_file ${WORK}/ccpa24/ccpa${nccpa_file}
        else
            if [ $SENDMAIL = YES ]; then
                export subject="06h CCPA Data Missing for 24h CCPA generation"
                echo "Warning: A 06h CCPA file is missing for 24h CCPA generation at ${vday}${ihour}" > mailmsg
                echo "Missing file is $source_ccpa_file"  >> mailmsg
                echo "Job ID: $jobid" >> mailmsg
                cat mailmsg | mail -s "$subject" $MAILTO
            fi
        fi
        nccpa_file=`expr $nccpa_file + 1`
    done
    if [ -s ${WORK}/ccpa24/ccpa1 ] && [ -s ${WORK}/ccpa24/ccpa2 ] && [ -s ${WORK}/ccpa24/ccpa3 ] && [ -s ${WORK}/ccpa24/ccpa4 ] ; then
       ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_obsCCPA24h.conf
       [[ $SENDCOM="YES" ]] && cpreq -v $output_base/ccpa.t12z.grid3.24h.f00.nc $COMOUTgefs/.
    fi  
  done
fi

###########################################
#Get GEFS members APCP 6 hour accumulation
###########################################
if [ $modnam = gefs_apcp06h ] ; then
   for ihour in $gens_ihour ; do
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
       typeset -Z3 hhh
       fhr=06
       while [ $fhr -le 384 ] ; do
         hhh=$fhr
         if [ -s $COMINgefs/gefs.$vday/$ihour/atmos/pgrb2ap5/gep${mb}.t${ihour}z.pgrb2a.0p50.f${hhh} ] ; then
           gefs=$COMINgefs/gefs.$vday/$ihour/atmos/pgrb2ap5/gep${mb}.t${ihour}z.pgrb2a.0p50.f${hhh}
           $WGRIB2 -match "APCP" $gefs|$WGRIB2 -i $gefs -grib gefs.ens${mb}.t${ihour}z.grid4.06h.f${hhh}.grib2
           $WGRIB2 gefs.ens${mb}.t${ihour}z.grid4.06h.f${hhh}.grib2 -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003 $WORK/gefs.ens${mb}.t${ihour}z.grid3.06h.f${hhh}.grib2 
        else
           echo "WARNING: $COMINgefs/gefs.$vday/$ihour/atmos/pgrb2ap5/gep${mb}.t${ihour}z.pgrb2a.0p50.f${hhh} does not exist, using $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2"
           gefs=$COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2
           if [ -s $gefs ]; then
             $WGRIB2 -match "APCP" $gefs|$WGRIB2 -i $gefs -grib $WORK/gefs.ens${mb}.t${ihour}z.grid3.06h.f${hhh}.grib2 
           else
             echo "WARNING: $gefs does not exist"
           fi
        fi
        [[ $SENDCOM="YES" ]] && cpreq -v $WORK/gefs.ens${mb}.t${ihour}z.grid3.06h.f${hhh}.grib2 $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.06h.f${hhh}.grib2
        fhr=$((fhr+6))
       done
    done
   done
fi 

###############################################################
#Get GEFS members APCP 24 hour accumulation through PcpCombine
###############################################################
if [ $modnam = gefs_apcp24h ] ; then
    export output_base=${WORK}/precip/gefs_apcp24h
    export model=gefs
    export modelpath=$COMOUTgefs
    export ihour
    export mb
    export lead
    for ihour in $gens_ihour ; do
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
        typeset -a lead_arr
        for lead_chk in 024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384; do
         if [ -s $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.f${lead_chk}.grib2 ] ; then 	
            lead_arr[${#lead_arr[*]}+1]=${lead_chk}
         else
            echo "WARNING: $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.f${lead_chk}.grib2 does not exist"
	 fi
        done
        lead=$(echo $(echo ${lead_arr[@]}) | tr ' ' ',')
        ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_APCP24h.conf  
        unset lead_arr
      done
    done
    [[ $SENDCOM="YES" ]] && cpreq -v ${output_base}/*.nc $COMOUTgefs/.
fi

###########################################
#Get CMCE members APCP 6 hour accumulation
###########################################
if [ $modnam = cmce_apcp06h ] ; then
    for ihour in $gens_ihour ; do
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do
       typeset -Z3 hhh
       fhr=06
       while [ $fhr -le 384 ] ; do
         hhh=$fhr
         cmce=$COMINcmce/cmce.$vday/$ihour/pgrb2ap5/cmc_gep${mb}.t${ihour}z.pgrb2a.0p50.f${hhh}
         if [ -s $cmce ]; then
           $WGRIB2 -match "APCP" $cmce|$WGRIB2 -i $cmce -grib cmce.ens${mb}.t${ihour}z.grid4.06h.f${hhh}.grib2
	   $WGRIB2 cmce.ens${mb}.t${ihour}z.grid4.06h.f${hhh}.grib2 -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003 cmce.ens${mb}.t${ihour}z.grid3.06h.f${hhh}.grib2 
           [[ $SENDCOM="YES" ]] && cpreq -v cmce.ens${mb}.t${ihour}z.grid3.06h.f${hhh}.grib2 $COMOUTcmce/cmce.ens${mb}.t${ihour}z.grid3.06h.f${hhh}.grib2
         else
           echo "WARNING: $cmce does not exist"
         fi
         fhr=$((fhr+6))
       done
    done
   done
fi

#################################################################
#Get CMCE members APCP 24 hour accumulation through PcpCombine
#################################################################
if [ $modnam = cmce_apcp24h ] ; then
    export output_base=${WORK}/precip/cmce_apcp24h
    export model=cmce
    export modelpath=$COMOUTcmce
    export lead 
    export ihour
    export mb
    for ihour in $gens_ihour ; do
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do
         typeset -a lead_arr
         for lead_chk in 024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384; do
           if [ -s $COMOUTcmce/cmce.ens${mb}.t${ihour}z.grid3.06h.f${lead_chk}.grib2 ] ; then
             lead_arr[${#lead_arr[*]}+1]=${lead_chk}
           else
             echo "WARNING: $COMOUTcmce/cmce.ens${mb}.t${ihour}z.grid3.06h.f${lead_chk}.grib2 does not exist"
	   fi
         done
         lead=$(echo $(echo ${lead_arr[@]}) | tr ' ' ',')
         ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstCMCE_APCP24h.conf  
         unset lead_arr
      done
    done
    [[ $SENDCOM="YES" ]] && cpreq -v ${output_base}/*.nc $COMOUTcmce/.
fi

##############################################################
#Get ECME members APCP 24 hour accumulation through PcpCombine
##############################################################
if [ $modnam = ecme_apcp24h ] ; then
  export lead
  export ihour
  export mb
  export modelpath=$COMOUTecme
  for ihour in 00 12 ; do
     export output_base=${WORK}/precip/ecme_apcp24h.${ihour}
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40  41 42 43 44 45 46 47 48 49 50  ; do
       typeset -a lead_arr
       for lead_chk in 024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360; do
         if [ -s $COMOUTecme/ecme.ens${mb}.t${ihour}z.grid4_apcp.f${lead_chk}.grib1 ] ; then 
           lead_arr[${#lead_arr[*]}+1]=${lead_chk} 
         else
           echo "WARNING: $COMOUTecme/ecme.ens${mb}.t${ihour}z.grid4_apcp.f${lead_chk}.grib1 does not exist"
         fi
       done
       lead=$(echo $(echo ${lead_arr[@]}) | tr ' ' ',')
       ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstECME_APCP24h.conf   
       unset lead_arr
     done
     [[ $SENDCOM="YES" ]] && cpreq -v ${output_base}/*.nc $COMOUTecme/.
  done
fi

#############################################################
# Get 24 hour NOHRSC snowfall data
#############################################################
if [ $modnam = nohrsc24h ] ; then
  for ihour in 00 12 ; do
    snowfall=$DCOMINnohrsc/${vday}/wgrbbul/nohrsc_snowfall/sfav2_CONUS_24h_${vday}${ihour}_grid184.grb2
    if [ -s $snowfall ] ; then
      cpreq -v $snowfall $WORK/nohrsc.t${ihour}z.grid184.grb2
      [[ $SENDCOM="YES" ]] && cpreq -v $WORK/nohrsc.t${ihour}z.grid184.grb2 $COMOUTgefs/nohrsc.t${ihour}z.grid184.grb2
    else
        if [ $SENDMAIL = YES ]; then
          export subject="NOHRSC Data Missing for EVS ${COMPONENT}"
          echo "Warning:  No NOHRSC analysis available for ${vday}${ihour}" > mailmsg
          echo "Missing file is $snowfall"  >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
	fi
    fi
  done
fi

###############################################################################
#Get GFS members WEASD & SNOD 24 hour snowfall accumulation through PcpCombine
###############################################################################
if [ $modnam = gefs_snow24h ] ; then
   export output_base=${WORK}/snow/gefs_snow24h.${gens_ihour}
   export lead
   export ihour
   export mb
   export model=gefs
   export modelpath=$COMOUTgefs
   export snow
   for ihour in $gens_ihour ; do
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
       typeset -a lead_arr
       for lead_chk in 024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384; do
         if [  -s $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.f${lead_chk}.grib2 ] ; then
             lead_arr[${#lead_arr[*]}+1]=${lead_chk}
         else
             echo "WARNING: $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.f${lead_chk}.grib2 does not exist"
         fi
       done
       lead=$(echo $(echo ${lead_arr[@]}) | tr ' ' ',')
       for snow in WEASD SNOD ; do
           ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_SNOW24h.conf  
       done
       unset lead_arr
     done
     [[ $SENDCOM="YES" ]] && cpreq -v $output_base/*.nc $COMOUTgefs/.
   done
fi

###############################################################################
#Get CMC members WEASD & SNOD 24 hour snowfall accumulation through PcpCombine
##############################################################################
if [ $modnam = cmce_snow24h ] ; then
  export output_base=${WORK}/snow/cmce_snow24h.${gens_ihour}
  export ihour
  export mb
  export model=cmce
  export modelpath=$COMOUTcmce
  export snow
  export lead
  for ihour in $gens_ihour ; do
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do
       typeset -a lead_arr
       for lead_chk in 024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384; do
         if [  -s $COMOUTcmce/cmce.ens${mb}.t${ihour}z.grid3.f${lead_chk}.grib2 ] ; then
           lead_arr[${#lead_arr[*]}+1]=${lead_chk}
         else
           echo "WARNING: $COMOUTcmce/cmce.ens${mb}.t${ihour}z.grid3.f${lead_chk}.grib2 does not exist"
         fi
       done
       lead=$(echo $(echo ${lead_arr[@]}) | tr ' ' ',')
       for snow in WEASD SNOD ; do
           ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_SNOW24h.conf  
       done
       unset lead_arr
     done
     [[ $SENDCOM="YES" ]] && cp $output_base/*.nc $COMOUTcmce/.
  done
fi

#####################################################################
#Get ECM members  24 hour snowfall accumulation through PcpCombine
####################################################################
if [ $modnam = ecme_snow24h ] ; then
    export ihour
    export mb
    export model=ecme
    export modelpath=$COMOUTecme
    export lead
  for ihour in 00 12 ; do
     export output_base=${WORK}/snow/ecme_snow24h.${ihour}
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 ; do
       typeset -a lead_arr
       for lead_chk in 024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360; do
         if [  -s $COMOUTecme/ecme.ens${mb}.t${ihour}z.grid4_apcp.f${lead_chk}.grib1 ] ; then
           lead_arr[${#lead_arr[*]}+1]=${lead_chk}
         else
           echo "WARNING: $COMOUTecme/ecme.ens${mb}.t${ihour}z.grid4_apcp.f${lead_chk}.grib1 does not exist"
         fi
       done
       lead=$(echo $(echo ${lead_arr[@]}) | tr ' ' ',')
       ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstECME_SNOW24h.conf  
       unset lead_arr
     done
     [[ $SENDCOM="YES" ]] && cp $output_base/ecme*.nc $COMOUTecme
  done
fi

#################################################################################
# Get gfs 00Z forecasts 500mb Geopotential Heights for headline score comparison
#################################################################################
if [ $modnam = gfs ] ; then
  for ihour in 00  ; do
    for  hhh in 024 048 072 096  120 144 168 192 216 240 264 288 312 336 360 384 ; do     
     gfs=$COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.f${hhh}
     if [ ! -s $gfs ]; then
      if [ $SENDMAIL = YES ]; then
        export subject="GFS F${hhh} Data Missing for EVS ${COMPONENT}"
        echo "Warning: No GFS F${hhh} available for ${vday}${ihour}" > mailmsg
        echo "Missing file is $gfs" >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $MAILTO
      fi
     else
       $WGRIB2  $gfs|grep "HGT:500 mb"|$WGRIB2 -i $gfs -grib $WORK/gfs.t${ihour}z.grid3.f${hhh}.grib2
       [[ $SENDCOM="YES" ]] && cpreq -v $WORK/gfs.t${ihour}z.grid3.f${hhh}.grib2 $COMOUTgefs/gfs.t${ihour}z.grid3.f${hhh}.grib2
     fi
    done
  done
fi

#############################################################
# Process OSI-SAF ice data (using Mallory's python scripts)
############################################################
if [ $modnam = osi_saf ] ; then
  INITDATEm1=$($NDATE -24 ${INITDATE}00 | cut -c1-8)
  osisaf_comout_file=${COMOUTosi_saf}/osi_saf.multi.${INITDATEm1}00to${INITDATE}00_G004.nc
  if [ -s $osisaf_comout_file ]; then
    echo "${osisaf_comout_file} exists"
  else
    osi_nh=$DCOMINosi_saf/$INITDATEm1/seaice/osisaf/ice_conc_nh_polstere-100_multi_${INITDATEm1}1200.nc
    osi_sh=$DCOMINosi_saf/$INITDATEm1/seaice/osisaf/ice_conc_sh_polstere-100_multi_${INITDATEm1}1200.nc
    if [ ! -s $osi_nh ]; then
        if [ $SENDMAIL = YES ]; then
          export subject="OSI_SAF NH Data Missing for EVS ${COMPONENT}"
          echo "Warning:  No OSI_SAF NH data  available for ${INITDATE}" > mailmsg
          echo "Missing file is $osi_nh"  >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
        fi 
    elif [ ! -s $osi_sh ]; then
          export subject="OSI_SAF SH Data Missing for EVS ${COMPONENT}"
          echo "Warning:  No OSI_SAF SH data  available for ${INITDATE}" > mailmsg
          echo "Missing file is $osi_sh"  >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
    else
	  echo "NH OSI_SAF and SH OSI_SAF datasets exist" 
          python ${USHevs}/global_ens/global_ens_sea_ice_prep.py
         [[ $SENDCOM="YES" ]] &&  cpreq -v $WORK/atmos.${INITDATE}/osi_saf/*.nc $COMOUTosi_saf/.
    fi
  fi
fi

#############################################################################
#Get GEFS members sea-ice concentration daily average through PcpCombine
# Ice concentration starts from f000. There is amount of ice at beginning.
# So, for f024 ice concentation, it shoule be  averaged of f000, f006, f012
# f018 and f024 
############################################################################
if [ $modnam = gefs_icec24h ] ; then
    export output_base=${WORK}/gefs_icec24h
    export model=gefs
    export modelpath=$COMOUTgefs
    export ihour
    export mb
    export accum=24
    export lead
    for ihour in 00 ; do
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
       typeset -a lead_arr
       for lead_chk in 024 048 072 096 120 144 168 192 216 240 264 288 312 336 360 384; do
         if [  -s $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.f${lead_chk}.grib2 ] ; then
           lead_arr[${#lead_arr[*]}+1]=${lead_chk}
         else
           echo "WARNING: $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.f${lead_chk}.grib2 does not exist"
         fi
       done
       lead=$(echo $(echo ${lead_arr[@]}) | tr ' ' ',')
       ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_ICEC.conf  
       unset lead_arr
     done
    done
    [[ $SENDCOM="YES" ]] && cpreq -v $output_base/gefs*icec*.nc $COMOUTgefs/.
fi

###########################################################################
#Get GEFS members sea-ice concentration weekly average through PcpCombine
###########################################################################
if [ $modnam = gefs_icec7day ] ; then
    export output_base=${WORK}/gefs_icec7day
    export model=gefs
    export modelpath=$COMOUTgefs
    export lead
    export ihour
    export mb
    export accum=168	
    for ihour in 00  ; do
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
        if [ $ihour = 00 ] ; then
            export leads='168 192 216 240 264 288 312 336 360 384'
        elif [ $ihour = 12 ] ; then 
            export leads='180 204 228 252 276 300 324 348 372'
        fi
        for lead in $leads; do
          ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_ICEC.conf  
        done
     done
   done						     
   [[ $SENDCOM="YES" ]] && cpreq -v $output_base/gefs*icec*.nc $COMOUTgefs/.
fi

######################################################
#Get GEFS members sst daily average through PcpCombine
######################################################
if [ $modnam = gefs_sst24h ] ; then
    export output_base=${WORK}/gefs_sst24h
    export model=gefs
    export modelpath=$COMOUTgefs
    export lead
    export ihour
    export mb
    export accum=24
    for ihour in 00  12  ; do
       for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
         if [ $ihour = 00 ] ; then
           export leads='024 048 072 096 120 144 168 192 216 240 264 288 312 336 360 384'
         elif [ $ihour = 12 ] ; then
           export leads='036 060 084 108 132 156 180 204 228 252 276 300 324 348 372'
         fi
         typeset -a lead_arr
         for lead_chk in $leads; do
           if [  -s $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.f${lead_chk}.grib2 ] ; then
             lead_arr[${#lead_arr[*]}+1]=${lead_chk}
           else
             echo "WARNING: $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.f${lead_chk}.grib2 does not exist"
	   fi
         done
         lead=$(echo $(echo ${lead_arr[@]}) | tr ' ' ',')
         ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_SST24h.conf  
         unset lead_arr
       done
   done
   [[ $SENDCOM="YES" ]] && cpreq -v $output_base/gefs*sst*.nc $COMOUTgefs
fi
