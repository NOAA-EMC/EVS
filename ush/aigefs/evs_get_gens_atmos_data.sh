#!/bin/ksh
#######################################################################################
# Purposes: 
#   1. Retrive/regrid analysis/observations (to 1 degree)
#   2. Retrive required fields from AIGEFS and large operational GEFS member
#      files to form smaller member files
#   3. Regrid the smaller files to required grid (1x1 degree).
#   4. Store the well-formed analysis/observations or smaller ensemble member files
#      in the evs prep sub-directory /prep/aigefs/atmos.YYYYMMDD
#
# Updated: 10/03/2025 by L. Gwen Chen (lichuan.chen@noaa.gov) 
#######################################################################################
set -x

modnam=$1
gens_ihour=$2
fhr_beg=$3
fhr_end=$4

export vday=${INITDATE:-$PDYm2}    #for ensemble, use past-2 day as validation day
export vdate=${vdate:-$vday$ihour}

if [ -z "$gens_ihour" ] ; then
  export WORKtask=$WORK/get_${modnam}
else
  export WORKtask=$WORK/get_${modnam}_${gens_ihour}z_f${fhr_beg}_to_f${fhr_end}
fi

mkdir -p $WORKtask
cd $WORKtask

#################################################################################
# Get GFS analysis grib2 data in GRID#3 (1-degree global) and WMO 1.5 deg for 00Z
# NOTE: There are no U10, V10 in GFS analysis, so use GFS*f000 as an alternative
#################################################################################
if [ $modnam = gfsanl ]; then
  for ihour in 00 06 12 18 ; do
    if [ ! -s $COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.anl ] ; then
      echo "WARNING: $COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.anl is not available" 
      if [ $SENDMAIL = YES ]; then
        export subject="GFS Analysis Data Missing for EVS ${COMPONENT}"
        echo "Warning: No GFS analysis available for ${vday}${ihour}" > mailmsg
        echo "Missing file is $COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.anl" >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $MAILTO
      fi
    else
      cp -v $COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.anl $WORKtask/gfsanl.t${ihour}z.grid3.f000.grib2
    fi
    if [ ! -s $COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.f000 ]; then
      echo "WARNING: $COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.f000 is not available"
      if [ $SENDMAIL = YES ]; then
        export subject="GFS F000 Data Missing for EVS ${COMPONENT}"
        echo "Warning: No GFS F000 available for ${vday}${ihour}" > mailmsg
        echo "Missing file is $COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.f000" >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $MAILTO
      fi
    else
      GFSf000=$COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.f000
      $WGRIB2 $GFSf000 | grep "UGRD:10 m above ground" | $WGRIB2 -i $GFSf000 -grib $WORKtask/U10_f000.${ihour}
      cat $WORKtask/U10_f000.${ihour} >> $WORKtask/gfsanl.t${ihour}z.grid3.f000.grib2
      $WGRIB2 $GFSf000 | grep "VGRD:10 m above ground" | $WGRIB2 -i $GFSf000 -grib $WORKtask/V10_f000.${ihour}
      cat $WORKtask/V10_f000.${ihour} >> $WORKtask/gfsanl.t${ihour}z.grid3.f000.grib2
    fi
    if [ $SENDCOM="YES" ] ; then
        if [ -s $WORKtask/gfsanl.t${ihour}z.grid3.f000.grib2 ]; then
            cp -v $WORKtask/gfsanl.t${ihour}z.grid3.f000.grib2 $COMOUTgefs/gfsanl.t${ihour}z.grid3.f000.grib2
        fi
    fi
  done

  if [ -s $COMOUTgefs/gfsanl.t00z.grid3.f000.grib2 ]; then
    $WGRIB2 $COMOUTgefs/gfsanl.t00z.grid3.f000.grib2 -set_grib_type same -new_grid_winds earth -new_grid latlon 0:240:1.5 -90:121:1.5 $WORKtask/gfsanl.t00z.deg1.5.f000.grib2
    if [ $SENDCOM="YES" ] ; then
      if [ -s $WORKtask/gfsanl.t00z.deg1.5.f000.grib2 ]; then
        cp -v $WORKtask/gfsanl.t00z.deg1.5.f000.grib2 $COMOUTgefs/gfsanl.t00z.deg1.5.f000.grib2
      fi
    fi
  fi
fi

############################################################
# Get GEFS member grib2 files in GRID#3 
# Note: for GEFS get data at 4 cycles 00, 06, 12 and 18Z
#       specified by $gens_ihour
############################################################
if [ $modnam = gefs ] ; then
  total=30

  if [ ! -s $WORKtask/gefs.ens30.t${gens_ihour}z.grid3.f${fhr_end}.grib2 ] ; then
    tmpDir=$WORKtask/${modnam}.${fhr_beg}
    mkdir -p $tmpDir

    # Create a file of patterns to use with grep. This way we only need one grep
    pat0=${tmpDir}/pattern0.${modnam}.${gens_ihour}.${fhr_beg}

    # Upper air
    if [ -e ${pat0} ]; then rm ${pat0}; fi
    >${pat0}

    for level in 10 50 100 200 250 300 400 500 700 850 925 1000 ; do
      echo "UGRD:$level mb" >> ${pat0}
      echo "VGRD:$level mb" >> ${pat0}
    done
    echo "HGT:" >> ${pat0}
    echo "TMP:" >> ${pat0} 
    # Surface
    echo "UGRD:10 m above ground" >> ${pat0}
    echo "VGRD:10 m above ground" >> ${pat0}
    echo "APCP:" >> ${pat0}
    echo "PRMSL:" >> ${pat0}

    for ihour in $gens_ihour ; do
    origin=$COMINgefs/gefs.$vday/$ihour/atmos/pgrb2ap5
    mbr=0

    while [ $mbr -le $total ] ; do
      mb=$mbr
      typeset -Z2 mb
      nfhrs=$fhr_beg

      while [ $nfhrs -le $fhr_end ] ; do
        hhh=$nfhrs
        typeset -Z3 hhh

        # Note: control member (gec00) is not used in GEFS verification,
        #       but used in HGEFS verification. Prep it together to generate
        #       24-hr precip file later
        if [ $mb = 00 ]; then
          gefs=$origin/gec${mb}.t${ihour}z.pgrb2a.0p50.f${hhh}
        else
          gefs=$origin/gep${mb}.t${ihour}z.pgrb2a.0p50.f${hhh}
        fi

        if [ -s $gefs ]; then
          grabgefs=${tmpDir}/grabgefs.${ihour}.${mb}.${hhh}
          x=${tmpDir}/x.${ihour}.${mb}.${hhh}
          $WGRIB2 $gefs | grep --file=${pat0} | $WGRIB2 -i $gefs -grib ${grabgefs}
        else
          echo "WARNING: $gefs is not available"
          if [ $SENDMAIL = YES ]; then
            export subject="GEFS Member ${mb} F${hhh} Data Missing for EVS ${COMPONENT}"
            echo "Warning: No GEFS Member ${mb} F${hhh} available for ${vday}${ihour}" > mailmsg
            echo "Missing file is $gefs" >> mailmsg
            echo "Job ID: $jobid" >> mailmsg
            cat mailmsg | mail -s "$subject" $MAILTO
          fi
        fi

        if [ ! -z $grabgefs ]; then
          if [ -s $grabgefs ]; then
            $WGRIB2 ${grabgefs} -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003 $WORKtask/gefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2
          fi

          if [ $SENDCOM="YES" ] ; then
            if [ -s $WORKtask/gefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2 ]; then 
              cp -v $WORKtask/gefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2 $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2
              cp -v $WORKtask/gefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2 $COMOUThgefs/hgefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2
            fi
          fi
        fi
        nfhrs=`expr $nfhrs + 6`
      done # forecast hour

      mbr=`expr $mbr + 1`
    done # member
    done # ihour

# Clean up temporary directory
    rm -r ${tmpDir}

  fi # check if file exists
fi

############################################################
# Get AIGEFS member grib2 files in GRID#3 
# Note: for AIGEFS get data at 4 cycles 00, 06, 12 and 18Z
#       specified by $gens_ihour
############################################################
if [ $modnam = aigefs ] ; then
  total=30

  if [ ! -s $WORKtask/aigefs.ens30.t${gens_ihour}z.grid3.f${fhr_end}.grib2 ] ; then
    tmpDir=$WORKtask/${modnam}.${fhr_beg}
    mkdir -p $tmpDir

    # Create a file of patterns to use with grep. This way we only need one grep
    pat0=${tmpDir}/pattern0.${modnam}.${gens_ihour}.${fhr_beg}
    pat1=${tmpDir}/pattern1.${modnam}.${gens_ihour}.${fhr_beg}

    # Upper air
    if [ -e ${pat0} ]; then rm ${pat0}; fi
    >${pat0}
    echo "HGT:" >> ${pat0}
    echo "TMP:" >> ${pat0}
    echo "UGRD:" >> ${pat0}
    echo "VGRD:" >> ${pat0}

    # Surface
    if [ -e ${pat1} ]; then rm ${pat1}; fi
    >${pat1}
    echo "PRMSL:" >> ${pat1}
    echo "TMP:2 m above ground" >> ${pat1}
    echo "UGRD:10 m above ground" >> ${pat1}
    echo "VGRD:10 m above ground" >> ${pat1}
    echo "APCP:" >> ${pat1}

    for ihour in $gens_ihour ; do
    mbr=0
    while [ $mbr -le $total ] ; do
      mb2=$mbr
      mb3=$mbr
      typeset -Z2 mb2
      typeset -Z3 mb3
      origin=$COMINaigefs/aigefs.$vday/$ihour/mem${mb3}/model/atmos/grib2
      nfhrs=$fhr_beg

      while [ $nfhrs -le $fhr_end ] ; do
        hhh=$nfhrs
        typeset -Z3 hhh
        aigefs_pres=$origin/aigefs.t${ihour}z.pres.f${hhh}.grib2
        aigefs_sfc=$origin/aigefs.t${ihour}z.sfc.f${hhh}.grib2

        if [ -s $aigefs_pres ]; then
          grabaigefs=${tmpDir}/grabaigefs.${ihour}.${mb2}.${hhh}
          x=${tmpDir}/x.${ihour}.${mb2}.${hhh}
          $WGRIB2 $aigefs_pres | grep --file=${pat0} | $WGRIB2 -i $aigefs_pres -grib ${grabaigefs}
        else
          echo "WARNING: $aigefs_pres is not available"
          if [ $SENDMAIL = YES ]; then
            export subject="AIGEFS Member ${mb3} F${hhh} Data Missing for EVS ${COMPONENT}"
            echo "Warning: No AIGEFS Member ${mb3} F${hhh} available for ${vday}${ihour}" > mailmsg
            echo "Missing file is $aigefs_pres" >> mailmsg
            echo "Job ID: $jobid" >> mailmsg
            cat mailmsg | mail -s "$subject" $MAILTO
          fi
        fi

        if [ -s $aigefs_sfc ]; then
          [[ -z $grabaigefs ]] && grabaigefs=${tmpDir}/grabaigefs.${ihour}.${mb2}.${hhh}
          [[ -z $x ]] && x=${tmpDir}/x.${ihour}.${mb2}.${hhh}
          $WGRIB2 $aigefs_sfc | grep --file=${pat1} | $WGRIB2 -i $aigefs_sfc -grib ${x}
          cat ${x} >> ${grabaigefs}
        else
          echo "WARNING: $aigefs_sfc is not available"
          if [ $SENDMAIL = YES ]; then
            export subject="AIGEFS Member ${mb3} F${hhh} Data Missing for EVS ${COMPONENT}"
            echo "Warning: No AIGEFS Member ${mb3} F${hhh} available for ${vday}${ihour}" > mailmsg
            echo "Missing file is $aigefs_sfc" >> mailmsg
            echo "Job ID: $jobid" >> mailmsg
            cat mailmsg | mail -s "$subject" $MAILTO
          fi
        fi

        if [ ! -z $grabaigefs ]; then
          if [ -s $grabaigefs ]; then
            $WGRIB2 ${grabaigefs} | sed -e 's/:UGRD:/:UGRDa:/' -e 's/:VGRD:/:UGRDb:/' | sort -t: -k3,3 -k5,8 -k4,4 | $WGRIB2 ${grabaigefs} -i -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003 $WORKtask/aigefs.ens${mb2}.t${ihour}z.grid3.f${hhh}.grib2
          fi
          if [ $SENDCOM="YES" ] ; then
            if [ -s $WORKtask/aigefs.ens${mb2}.t${ihour}z.grid3.f${hhh}.grib2 ]; then
              cp -v $WORKtask/aigefs.ens${mb2}.t${ihour}z.grid3.f${hhh}.grib2 $COMOUTaigefs/aigefs.ens${mb2}.t${ihour}z.grid3.f${hhh}.grib2

              # change member numbers from 00-30 to 31-61 for HGEFS
              hmbr=`expr $mbr + 31`
              cp -v $WORKtask/aigefs.ens${mb2}.t${ihour}z.grid3.f${hhh}.grib2 $COMOUThgefs/hgefs.ens${hmbr}.t${ihour}z.grid3.f${hhh}.grib2
            fi
          fi
        fi
        nfhrs=`expr $nfhrs + 6`
      done # forecast hour

      mbr=`expr $mbr + 1`
    done # member
    done # ihour

# Clean up temporary directory
    rm -r ${tmpDir}

  fi # check if file exists
fi

#############################################################
# Run GDAS prepbufr files through PB2NC
#############################################################
if [ $modnam = prepbufr ] ; then
   > run_pb2nc.sh
   for ihour in 00 06 12 18 ; do
      > run_pb2nc.${ihour}.sh
      echo "export bufrpath=$WORKtask" >> run_pb2nc.${ihour}.sh
      echo "export output_base=$WORKtask/pb2nc" >> run_pb2nc.${ihour}.sh
      echo "export vbeg=${ihour}" >> run_pb2nc.${ihour}.sh
      echo "export vend=${ihour}" >> run_pb2nc.${ihour}.sh
      if [ -s $COMINobsproc/gdas.${vday}/${ihour}/atmos/gdas.t${ihour}z.prepbufr ] ; then
        # Split the prepbufr data file by message types to reduce walltime
	echo "mkdir -p $WORKtask/prepbufr.${vday}" >> run_pb2nc.${ihour}.sh
        echo ">$WORKtask/prepbufr.${vday}/gdas.t${ihour}z.prepbufr" >> run_pb2nc.${ihour}.sh
	echo "split_by_subset $COMINobsproc/gdas.${vday}/${ihour}/atmos/gdas.t${ihour}z.prepbufr" >> run_pb2nc.${ihour}.sh
	echo "cat $WORKtask/ADPUPA $WORKtask/ADPSFC $WORKtask/SFCSHP >> $WORKtask/prepbufr.${vday}/gdas.t${ihour}z.prepbufr" >> run_pb2nc.${ihour}.sh
      	echo "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsGFS_Prepbufr.conf" >> run_pb2nc.${ihour}.sh  
        echo "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsGFS_Prepbufr_Profile.conf" >> run_pb2nc.${ihour}.sh  
      else
        echo "WARNING: $COMINobsproc/gdas.${vday}/${ihour}/atmos/gdas.t${ihour}z.prepbufr is not available"
	if [ $SENDMAIL = YES ]; then
          export subject="Prepbufr Data Missing for EVS ${COMPONENT}"
          echo "Warning: No prepbufr analysis available for ${vday}${ihour}" > mailmsg
          echo "Missing file is $COMINobsproc/gdas.${vday}/${ihour}/atmos/gdas.t${ihour}z.prepbufr"  >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
	fi
      fi 
      chmod +x run_pb2nc.${ihour}.sh
      echo "$WORKtask/run_pb2nc.${ihour}.sh" >> run_pb2nc.sh
   done
   echo "for FILE in $WORKtask/pb2nc/prepbufr_nc/*.nc ; do" >> run_pb2nc.sh
   echo "  if [ -s \$FILE ]; then" >> run_pb2nc.sh
   echo "      chmod 640 $WORKtask/pb2nc/prepbufr_nc/*prepbufr*.nc" >> run_pb2nc.sh
   echo "      chgrp rstprod $WORKtask/pb2nc/prepbufr_nc/*prepbufr*.nc" >> run_pb2nc.sh
   echo "      cp -v \$FILE $COMOUTgefs" >> run_pb2nc.sh
   echo "      chmod 640 $COMOUTgefs/*prepbufr*.nc" >> run_pb2nc.sh
   echo "      chgrp rstprod $COMOUTgefs/*prepbufr*.nc" >> run_pb2nc.sh
   echo "  fi" >> run_pb2nc.sh
   echo "done" >> run_pb2nc.sh
   chmod +x run_pb2nc.sh
   $WORKtask/run_pb2nc.sh
fi

############################################################
# Get CCPA 6 hour accumulation and run PCPCombine to get
#         24 hour accumulation
############################################################
if [ $modnam = ccpa ] ; then
  day1=$($NDATE -24 ${vday}12)
  export vday_1=${day1:0:8}
  for ihour in 00 06 12 18 ; do
    if [ -s $COMINccpa/ccpa.${vday}/$ihour/ccpa.t${ihour}z.06h.1p0.conus.gb2 ] ; then
      $WGRIB2 $COMINccpa/ccpa.${vday}/$ihour/ccpa.t${ihour}z.06h.1p0.conus.gb2 -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003 $WORKtask/ccpa.t${ihour}z.grid3.06h.f00.grib2
      if [ $SENDCOM="YES" ] ; then
        if [ -s $WORKtask/ccpa.t${ihour}z.grid3.06h.f00.grib2 ]; then
          cp -v $WORKtask/ccpa.t${ihour}z.grid3.06h.f00.grib2 ${COMOUTgefs}/ccpa.t${ihour}z.grid3.06h.f00.grib2
        fi
      fi
    else
      echo "WARNING: $COMINccpa/ccpa.${vday}/$ihour/ccpa.t${ihour}z.06h.1p0.conus.gb2 is not available" 
      if [ $SENDMAIL = YES ]; then
        export subject="CCPA Data Missing for EVS ${COMPONENT}"
        echo "Warning: No CCPA analysis available for ${vday}${ihour}" > mailmsg
        echo "Missing file is $COMINccpa/ccpa.${vday}/$ihour/ccpa.t${ihour}z.06h.1p0.conus.gb2"  >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $MAILTO
      fi
    fi 
  done
  export output_base=${WORKtask}/precip
  export ccpa24=${WORKtask}/ccpa24
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
        cp -v $source_ccpa_file ${WORKtask}/ccpa24/ccpa${nccpa_file}
      else
        echo "WARNING: $source_ccpa_file is not available"
        if [ $SENDMAIL = YES ]; then
          export subject="06h CCPA Data Missing for 24h CCPA generation"
          echo "Warning: A 06h CCPA file is missing for 24h CCPA generation at ${vday}${ihour}" > mailmsg
          echo "Missing file is $source_ccpa_file" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
        fi
      fi
      nccpa_file=`expr $nccpa_file + 1`
    done

    if [ -s ${WORKtask}/ccpa24/ccpa1 ] && [ -s ${WORKtask}/ccpa24/ccpa2 ] && [ -s ${WORKtask}/ccpa24/ccpa3 ] && [ -s ${WORKtask}/ccpa24/ccpa4 ] ; then
      ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_obsCCPA24h.conf
      if [ $SENDCOM="YES" ] ; then
        if [ -s $output_base/ccpa.t12z.grid3.24h.f00.nc ]; then
          cp -v $output_base/ccpa.t12z.grid3.24h.f00.nc $COMOUTgefs/.
        fi
      fi
    fi  
  done
fi

################################################################
# Get GEFS members APCP 24 hour accumulation through PcpCombine
################################################################
if [ $modnam = gefs_apcp24h ] ; then
    export output_base=${WORKtask}/precip/gefs_apcp24h
    export model=gefs
    export modelpath=$COMOUTgefs
    export ihour
    export mb
    export lead
    for ihour in $gens_ihour ; do
      for mb in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
        typeset -a lead_arr
        for lead_chk in 024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384; do
          file1=gefs.ens${mb}.t${ihour}z.grid3.f${lead_chk}.grib2
          if [ $lead_chk -ge 108 ]; then
             file2=gefs.ens${mb}.t${ihour}z.grid3.f$(printf '%03d' $((lead_chk-6))).grib2
             file3=gefs.ens${mb}.t${ihour}z.grid3.f$(printf '%03d' $((lead_chk-12))).grib2
             file4=gefs.ens${mb}.t${ihour}z.grid3.f$(printf '%03d' $((lead_chk-18))).grib2
          else
             strip_lead_chk=$(echo $lead_chk | sed 's/^0*//')
             file2=gefs.ens${mb}.t${ihour}z.grid3.f$(printf '%03d' $((strip_lead_chk-6))).grib2
             file3=gefs.ens${mb}.t${ihour}z.grid3.f$(printf '%03d' $((strip_lead_chk-12))).grib2
             file4=gefs.ens${mb}.t${ihour}z.grid3.f$(printf '%03d' $((strip_lead_chk-18))).grib2
          fi 
          if [ -s $COMOUTgefs/$file1 -a\
               -s $COMOUTgefs/$file2 -a\
               -s $COMOUTgefs/$file3 -a\
               -s $COMOUTgefs/$file4 ] ; then	
             lead_arr[${#lead_arr[*]}+1]=${lead_chk}
          else
             echo "WARNING: $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.f*.grib2 does not exist"
	  fi
        done
        lead=$(echo $(echo ${lead_arr[@]}) | tr ' ' ',')
        if [ ! -z $lead ]; then
          ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_APCP24h.conf
        fi  
        unset lead_arr
      done
    done

    if [ $SENDCOM="YES" ] ; then
      for FILE in ${output_base}/*.nc ; do
        if [ -s $FILE ]; then
          cp -v $FILE $COMOUTgefs/.
          cp -v $FILE $COMOUThgefs/.
        fi
      done
    fi

    # Rename files in hgefs
    for ihour in $gens_ihour ; do
      for fhr in 024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384; do
        for mb in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
          mv $COMOUThgefs/gefs.ens${mb}.t${ihour}z.grid3.24h.f${fhr}.nc $COMOUThgefs/hgefs.ens${mb}.t${ihour}z.grid3.24h.f${fhr}.nc
        done

        # Remove ens00 from gefs since it is not used for GEFS verification
        rm $COMOUTgefs/gefs.ens00.t${ihour}z.grid3.24h.f${fhr}.nc
      done

      # Also remove all ens00 grib2 files in gefs
      ihour6=`expr $ihour + 6`
      typeset -Z2 ihour6
      fhr=0
      while [ $fhr -le 384 ] ; do
        hhh=$fhr
        typeset -Z3 hhh
        rm $COMOUTgefs/gefs.ens00.t${ihour}z.grid3.f${hhh}.grib2
        rm $COMOUTgefs/gefs.ens00.t${ihour6}z.grid3.f${hhh}.grib2
        fhr=`expr $fhr + 6`
      done
    done

fi

##################################################################
# Get AIGEFS members APCP 24 hour accumulation through PcpCombine
##################################################################
if [ $modnam = aigefs_apcp24h ] ; then
    export output_base=${WORKtask}/precip/aigefs_apcp24h
    export model=aigefs
    export modelpath=$COMOUTaigefs
    export ihour
    export mb
    export lead
    for ihour in $gens_ihour ; do
      for mb in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
        typeset -a lead_arr
        for lead_chk in 024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384; do
          file1=aigefs.ens${mb}.t${ihour}z.grid3.f${lead_chk}.grib2
          if [ $lead_chk -ge 108 ]; then
             file2=aigefs.ens${mb}.t${ihour}z.grid3.f$(printf '%03d' $((lead_chk-6))).grib2
             file3=aigefs.ens${mb}.t${ihour}z.grid3.f$(printf '%03d' $((lead_chk-12))).grib2
             file4=aigefs.ens${mb}.t${ihour}z.grid3.f$(printf '%03d' $((lead_chk-18))).grib2
          else
             strip_lead_chk=$(echo $lead_chk | sed 's/^0*//')
             file2=aigefs.ens${mb}.t${ihour}z.grid3.f$(printf '%03d' $((strip_lead_chk-6))).grib2
             file3=aigefs.ens${mb}.t${ihour}z.grid3.f$(printf '%03d' $((strip_lead_chk-12))).grib2
             file4=aigefs.ens${mb}.t${ihour}z.grid3.f$(printf '%03d' $((strip_lead_chk-18))).grib2
          fi
          if [ -s $COMOUTaigefs/$file1 -a\
               -s $COMOUTaigefs/$file2 -a\
               -s $COMOUTaigefs/$file3 -a\
               -s $COMOUTaigefs/$file4 ] ; then
             lead_arr[${#lead_arr[*]}+1]=${lead_chk}
          else
             echo "WARNING: $COMOUTaigefs/aigefs.ens${mb}.t${ihour}z.grid3.f*.grib2 does not exist"
          fi
        done
        lead=$(echo $(echo ${lead_arr[@]}) | tr ' ' ',')
        if [ ! -z $lead ]; then
          ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstAIGEFS_APCP24h.conf
        fi
        unset lead_arr
      done
    done

    if [ $SENDCOM="YES" ] ; then
      for FILE in ${output_base}/*.nc ; do
        if [ -s $FILE ]; then
          cp -v $FILE $COMOUTaigefs/.
          cp -v $FILE $COMOUThgefs/.
        fi
      done
    fi

    # Rename and renumber files in hgefs
    for ihour in $gens_ihour ; do
      for fhr in 024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384; do
        for mb in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
          hmbr=`expr $mb + 31`
          mv $COMOUThgefs/aigefs.ens${mb}.t${ihour}z.grid3.24h.f${fhr}.nc $COMOUThgefs/hgefs.ens${hmbr}.t${ihour}z.grid3.24h.f${fhr}.nc
        done
      done
    done

fi

