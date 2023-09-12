#!/bin/ksh
set -x

modnam=$1
gens_cyc=$2
fhr_beg=$3
fhr_end=$4


export vday=${INITDATE:-$PDYm2}    #for ensemble, use past-2 day as validation day
export vdate=${vdate:-$vday$cyc}

export cnvgrib=$CNVGRIB
export wgrib2=$WGRIB2
export ndate=$NDATE


#############################################################
#1:Get gfs analysis grib2 data in GRID#3 (1-degree global)
############################################################
if [ $modnam = gfsanl ]; then

  echo $modnam is print here ...............

  for cyc in 00 06 12 18 ; do
    ###cp $COMINgfsanl/gfs.$vday/${cyc}/atmos/gfs.t${cyc}z.pgrb2.1p00.f000 $COMOUT_gefs/gfsanl.t${cyc}z.grid3.f000.grib2

    #check if gfsanl is missing:
    missing=no
    if [ ! -s $COMINgfsanl/gfs.$vday/${cyc}/atmos/gfs.t${cyc}z.pgrb2.1p00.anl ] ; then
       export subject="GFS Analysis Data Missing for EVS ${COMPONENT}"
       echo "Warning: No GFS analysis available for ${INITDATE}${cyc}" > mailmsg
       echo Missing file is $COMINgfsanl/gfs.$vday/${cyc}/atmos/gfs.t${cyc}z.pgrb2.1p00.anl >> mailmsg
     echo "Job ID: $jobid" >> mailmsg
     cat mailmsg | mail -s "$subject" $maillist
     missing=yes
    fi

   if [ $missing = no ] ; then 
    cp $COMINgfsanl/gfs.$vday/${cyc}/atmos/gfs.t${cyc}z.pgrb2.1p00.anl $COMOUT_gefs/gfsanl.t${cyc}z.grid3.f000.grib2
    #There are no U10, V10 in GFS analysis, so use GFS*f000 as alternative
    GFSf000=$COMINgfsanl/gfs.$vday/${cyc}/atmos/gfs.t${cyc}z.pgrb2.1p00.f000 
    $WGRIB2  $GFSf000|grep "UGRD:10 m above ground"|$WGRIB2 -i $GFSf000 -grib $WORK/U10_f000.${cyc}
    cat $WORK/U10_f000.${cyc} >> $COMOUT_gefs/gfsanl.t${cyc}z.grid3.f000.grib2
    $WGRIB2  $GFSf000|grep "VGRD:10 m above ground"|$WGRIB2 -i $GFSf000 -grib $WORK/V10_f000.${cyc}
    cat $WORK/V10_f000.${cyc} >> $COMOUT_gefs/gfsanl.t${cyc}z.grid3.f000.grib2
   fi 
 done

   if [ $missing = no ] ; then
    #For WMO 1.5 deg verification 
    $wgrib2 $COMOUT_gefs/gfsanl.t00z.grid3.f000.grib2 -set_grib_type same -new_grid_winds earth -new_grid latlon 0:240:1.5 -90:121:1.5 $COMOUT_gefs/gfsanl.t00z.deg1.5.f000.grib2 
   fi
fi

#Note CMCE has no DPT 
if [ $modnam = cmcanl ] ; then

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

  cd $WORK

    export outdata=$COMOUT_cmce

    for cyc in 00 12; do
      origin=$COMINcmce/cmce.$vday/$cyc/pgrb2ap5

      if [ ! -s $COMINcmce/cmce.$vday/$cyc/pgrb2ap5/cmc_gec00.t${cyc}z.pgrb2a.0p50.anl ] ; then 
        cmcanl=$origin/cmc_gec00.t${cyc}z.pgrb2a.0p50.f000
      else
        cmcanl=$origin/cmc_gec00.t${cyc}z.pgrb2a.0p50.anl
      fi

      missing=no
      if [ ! -s $cmcanl ] ; then
          export subject="CMC Analysis Data Missing for EVS ${COMPONENT}"
          echo "Warning: No CMC analysis available for ${INITDATE}${cyc}" > mailmsg
          echo Missing file is $cmcanl >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $maillist
          missing=yes
      fi

      if [ $missing = no ] ; then
        $WGRIB2 $cmcanl | grep --file=${pat} | grep "anl:ENS=low-res" | $WGRIB2 -i $cmcanl -grib ${WORK}/grabcmcanl.${cyc}
        $wgrib2 ${WORK}/grabcmcanl.${cyc} -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003 $outdata/cmcanl.t${cyc}z.grid3.f000.grib2 &
      fi

    done
    wait

    for cyc in 00 12; do
      rm ${WORK}/grabcmcanl.${cyc}
    done
    rm ${pat}

  if [ $missing = no ] ; then
    $wgrib2 $COMOUT_cmce/cmcanl.t00z.grid3.f000.grib2 -set_grib_type same -new_grid_winds earth -new_grid latlon 0:240:1.5 -90:121:1.5 $COMOUT_cmce/cmcanl.t00z.deg1.5.f000.grib2
  fi
fi 




###########################################
#5:Get GFS 20 member grib2 file in grid3 
###########################################
if [ $modnam = gefs ] ; then

  cd $WORK
  total=30

   export outdata=$COMOUT_gefs

   if [ ! -s $outdata/gefs.ens30.t12z.grid3.f384.grib2 ] ; then
    tmpDir=/tmp/${modnam}.$fhr_beg
    mkdir -p ${tmpDir}

    # Create a file of patterns to use with grep.  This way we only need one grep
    pat0=${tmpDir}/pattern0.${modnam}.${gens_cyc}.${fhr_beg}
    pat1=${tmpDir}/pattern1.${modnam}.${gens_cyc}.${fhr_beg}

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

    #for cyc in 00 06 12 18 ; do
    for cyc in $gens_cyc  ; do
  
      origin=$COMINgefs/gefs.$vday/$cyc/atmos/pgrb2ap5  
      origin_cvc=$COMINgefs/gefs.$vday/$cyc/atmos/pgrb2bp5

      mbr=1
       while [ $mbr -le $total ] ; do
         mb=$mbr
         typeset -Z2 mb

         nfhrs=$fhr_beg

         while [ $nfhrs -le $fhr_end ] ; do

           hhh=$nfhrs
           typeset -Z3 hhh

           gefs=$origin/gep${mb}.t${cyc}z.pgrb2a.0p50.f${hhh}
           gefs_cvc=$origin_cvc/gep${mb}.t${cyc}z.pgrb2b.0p50.f${hhh}

           grabgefs=${tmpDir}/grabgefs.${cyc}.${mb}.${hhh}
           x=${tmpDir}/x.${cyc}.${mb}.${hhh}

           $WGRIB2 $gefs     | grep --file=${pat0} | $WGRIB2 -i $gefs     -grib ${grabgefs}
           $WGRIB2 $gefs_cvc | grep --file=${pat1} | $WGRIB2 -i $gefs_cvc -grib ${x}
           cat ${x} >> ${grabgefs}
           $wgrib2 ${grabgefs} -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003 $outdata/gefs.ens${mb}.t${cyc}z.grid3.f${hhh}.grib2 &
           rm ${x}

           #nfhrs=`expr $nfhrs + 12`
           nfhrs=`expr $nfhrs + 6`
         done
         wait

         for hhh in $(seq --format=%03g $fhr_beg 6 $fhr_end ); do
           rm ${tmpDir}/grabgefs.${cyc}.${mb}.${hhh}
         done

         mbr=`expr $mbr + 1`
      done

     done   #for cyc
     rm ${pat0} ${pat1}
   fi # check if file not existing 

fi





###########################################
#8:Get CMCE 20 member grib2 file in grid3 
###########################################
if [ $modnam = cmce ] ; then

  cd $WORK

  total=20

  export outdata=$COMOUT_cmce

  tmpDir=/tmp/${modnam}
  mkdir -p ${tmpDir}

  # Create a file of patterns to use with grep.  This way we only need one grep
  pat=${tmpDir}/pattern.$gens_cyc.$fhr_beg
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

     for cyc in $gens_cyc ; do

       origin=$COMINcmce/cmce.$vday/$cyc/pgrb2ap5

       mbr=1
       while [ $mbr -le $total ] ; do
         mb=$mbr
         typeset -Z2 mb

         nfhrs=$fhr_beg
         while [ $nfhrs -le $fhr_end ] ; do

           #hh=$nfhrs
           h3=$nfhrs           

           typeset -Z3 h3
           cmce=$origin/cmc_gep${mb}.t${cyc}z.pgrb2a.0p50.f${h3}
           grabcmce=${tmpDir}/grabcmce.${cyc}.${mb}.${h3}

           $WGRIB2  $cmce|grep --file=${pat}|$WGRIB2 -i $cmce -grib ${grabcmce}
           $wgrib2 ${grabcmce} -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003  $outdata/cmce.ens${mb}.t${cyc}z.grid3.f${h3}.grib2 &
           nfhrs=`expr $nfhrs + 12`

         done
         wait

         for h3 in $(seq --format=%03g $fhr_beg 12 $fhr_end ); do
           rm ${tmpDir}/grabcmce.${cyc}.${mb}.${h3}
         done

         mbr=`expr $mbr + 1` 

       done

    done # for cyc
  rm ${pat}
fi



if [ $modnam = ecme ] ; then

  echo "getting ECMWF ensemble member files ...."
  #Note all files are in non-NCEP but in ECMWF GRIB1 format 

  export outdata=$COMOUT_ecme

  for cyc in 00 12 ; do
    $USHevs/global_ens/evs_process_atmos_ecme.sh.dk ${vday}${cyc} ${cyc} &
  done
  wait

fi


if [ $modnam = prepbufr ] ; then
   
   > run_pb2nc.sh

   for cyc in 00 06 12 18 ; do

    	   

      > run_pb2nc.${cyc}.sh
      
      echo  "export output_base=${WORK}/pb2nc" >> run_pb2nc.${cyc}.sh

      echo  "export vbeg=${cyc}" >> run_pb2nc.${cyc}.sh
      echo  "export vend=${cyc}" >> run_pb2nc.${cyc}.sh

      if [ -s $COMINprepbufr/gdas.${vday}/${cyc}/atmos/gdas.t${cyc}z.prepbufr ] ; then
        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsGFS_Prepbufr.conf" >> run_pb2nc.${cyc}.sh &
        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsGFS_Prepbufr_Profile.conf" >> run_pb2nc.${cyc}.sh &
        echo "wait" >> run_pb2nc.${cyc}.sh
      else
        export subject="Prepbufr  Data Missing for EVS ${COMPONENT}"
        echo "Warning:  No prepbufr analysis available for ${INITDATE}${cyc}" > mailmsg
        echo Missing file is $COMINprepbufr/gdas.${vday}/${cyc}/atmos/gdas.t${cyc}z.prepbufr  >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $maillist
      fi 

      chmod +x run_pb2nc.${cyc}.sh
      echo "${DATA}/run_pb2nc.${cyc}.sh &" >> run_pb2nc.sh
           
  done

      echo "wait" >> run_pb2nc.sh
      echo "mv ${WORK}/pb2nc/prepbufr_nc/*.nc $COMOUT_gefs" >> run_pb2nc.sh

  chmod +x run_pb2nc.sh
  ${DATA}/run_pb2nc.sh


fi  


if [ $modnam = ccpa ] ; then

  day1=`$ndate -24 ${vday}12`
  export vday_1=${day1:0:8}

  for cyc in 00 06 12 18 ; do
    if [ -s $COMINccpa/ccpa.${vday}/$cyc/ccpa.t${cyc}z.06h.1p0.conus.gb2 ] ; then
      $wgrib2 $COMINccpa/ccpa.${vday}/$cyc/ccpa.t${cyc}z.06h.1p0.conus.gb2 -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003  ${COMOUT_gefs}/ccpa.t${cyc}z.grid3.06h.f00.grib2
    else
        export subject="CCPA  Data Missing for EVS ${COMPONENT}"
        echo "Warning:  No CCPA analysis available for ${INITDATE}${cyc}" > mailmsg
        echo Missing file is $COMINccpa/ccpa.${vday}/$cyc/ccpa.t${cyc}z.06h.1p0.conus.gb2  >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $maillist
    fi 
  done

  export output_base=${WORK}/precip

  export ccpa24=${WORK}/ccpa24
  mkdir $ccpa24
  rm -f ${WORK}/ccpa24/*.grib2


  for cyc in 12 ; do
    cp ${COMOUT_gefs}/ccpa.t12z.grid3.06h.f00.grib2 ${WORK}/ccpa24/ccpa1
    cp ${COMOUT_gefs}/ccpa.t06z.grid3.06h.f00.grib2 ${WORK}/ccpa24/ccpa2
    cp ${COMOUT_gefs}/ccpa.t00z.grid3.06h.f00.grib2 ${WORK}/ccpa24/ccpa3
    cp ${COMOUT}.${vday_1}/gefs/ccpa.t18z.grid3.06h.f00.grib2 ${WORK}/ccpa24/ccpa4

    if [ -s ${WORK}/ccpa24/ccpa1 ] && [ -s ${WORK}/ccpa24/ccpa2 ] && [ -s ${WORK}/ccpa24/ccpa3 ] && [ -s ${WORK}/ccpa24/ccpa4 ] ; then
       ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_obsCCPA24h.conf
       mv $output_base/ccpa.t12z.grid3.24h.f00.nc $COMOUT_gefs/.
    else
       export subject="06h CCPA Data Missing for 24h CCPA generation"
       echo "Warning: At least one of ccpa06h files is missing  for ${INITDATE}${cyc}" > mailmsg
       echo Missing file is ${COMOUT_gefs}/ccpa.t12z.grid3.06h.f00.grib2 or ${COMOUT}.${vday_1}/gefs/ccpa.t18z.grid3.06h.f00.grib2  >> mailmsg
       echo "Job ID: $jobid" >> mailmsg
       cat mailmsg | mail -s "$subject" $maillist
       exit 
    fi  
  done
fi



if [ $modnam = gefs_apcp06h ] ; then

   for cyc in $gens_cyc ; do

     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do

       typeset -Z3 hhh
       fhr=06
       while [ $fhr -le 384 ] ; do
         hhh=$fhr

        if [ -s $COMINgefs/gefs.$vday/$cyc/atmos/pgrb2ap5/gep${mb}.t${cyc}z.pgrb2a.0p50.f${hhh} ] ; then

         gefs=$COMINgefs/gefs.$vday/$cyc/atmos/pgrb2ap5/gep${mb}.t${cyc}z.pgrb2a.0p50.f${hhh}
         $wgrib2 -match "APCP" $gefs|$wgrib2 -i $gefs -grib gefs.ens${mb}.t${cyc}z.grid4.06h.f${hhh}.grib2
         $wgrib2 gefs.ens${mb}.t${cyc}z.grid4.06h.f${hhh}.grib2 -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003 $COMOUT_gefs/gefs.ens${mb}.t${cyc}z.grid3.06h.f${hhh}.grib2 &

        else
         
         #make up 20210923~20210930 
         gefs=$COMOUT_gefs/gefs.ens${mb}.t${cyc}z.grid3.f${hhh}.grib2
         $wgrib2 -match "APCP" $gefs|$wgrib2 -i $gefs -grib $COMOUT_gefs/gefs.ens${mb}.t${cyc}z.grid3.06h.f${hhh}.grib2 &

        fi

        fhr=$((fhr+6))

       done
       wait
    done
   done

fi 

if [ $modnam = gefs_apcp24h ] ; then

    export output_base=${WORK}/precip/gefs_apcp24h
    export model=gefs
    export modelpath=$COMOUT_gefs
    
    export cyc
    export mb

    for cyc in $gens_cyc ; do

     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
         if [ -s $COMOUT_gefs/gefs.ens${mb}.t${cyc}z.grid3.f024.grib2 ] ; then 	
            export lead='24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384'
            ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_APCP24h.conf &
	 fi
     done
     wait
    done

    mv ${output_base}/*.nc $COMOUT_gefs/.
fi


if [ $modnam = cmce_apcp06h ] ; then

    for cyc in $gens_cyc ; do
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do

       typeset -Z3 hhh
       fhr=06
       while [ $fhr -le 384 ] ; do
         hhh=$fhr
         cmce=$COMINcmce/cmce.$vday/$cyc/pgrb2ap5/cmc_gep${mb}.t${cyc}z.pgrb2a.0p50.f${hhh}
         $wgrib2 -match "APCP" $cmce|$wgrib2 -i $cmce -grib cmce.ens${mb}.t${cyc}z.grid4.06h.f${hhh}.grib2
	 $wgrib2 cmce.ens${mb}.t${cyc}z.grid4.06h.f${hhh}.grib2 -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003 $COMOUT_cmce/cmce.ens${mb}.t${cyc}z.grid3.06h.f${hhh}.grib2 &
         fhr=$((fhr+6))
       done
       wait

    done
   done
fi



if [ $modnam = cmce_apcp24h ] ; then

    export output_base=${WORK}/precip/cmce_apcp24h
    export model=cmce
    export modelpath=$COMOUT_cmce
    
    export cyc
    export mb

    for cyc in $gens_cyc ; do
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do
	 if [ -s $COMOUT_cmce/cmce.ens${mb}.t${cyc}z.grid3.06h.f024.grib2 ] ; then
	  export lead='24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384'
          ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstCMCE_APCP24h.conf &
	 fi 
     done
     wait
    done

    mv ${output_base}/*.nc $COMOUT_cmce/.
fi



if [ $modnam = ecme_apcp24h ] ; then

  export cyc
  export mb
  export modelpath=$COMOUT_ecme

  for cyc in 00 12 ; do
     export output_base=${WORK}/precip/ecme_apcp24h.${cyc}
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40  41 42 43 44 45 46 47 48 49 50  ; do
       if [ -s $COMOUT_ecme/ecme.ens${mb}.t${cyc}z.grid4_apcp.f024.grib1 ] ; then  
         export lead='24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360'
	 ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstECME_APCP24h.conf &
       fi
     done
     wait
  done

     mv ${output_base}/*.nc $COMOUT_ecme/.
fi


if [ $modnam = nohrsc24h ] ; then
 
  for cyc in 00 12 ; do
    snowfall=$COMINsnow/${vday}/wgrbbul/nohrsc_snowfall/sfav2_CONUS_24h_${vday}${cyc}_grid184.grb2
    if [ -s $snowfall ] ; then
      mv $snowfall $COMOUT_gefs/nohrsc.t${cyc}z.grid184.grb2
    else
        export subject="NOHRSC Data Missing for EVS ${COMPONENT}"
        echo "Warning:  No NOHRSC analysis available for ${INITDATE}${cyc}" > mailmsg
        echo Missing file is $snowfall  >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $maillist
    fi
  done

fi

if [ $modnam = gefs_snow24h ] ; then

  export output_base=${WORK}/snow/gefs_snow24h.${gens_cyc}

   export cyc
   export mb
   export model=gefs
   export modelpath=$COMOUT_gefs
   export snow

  for cyc in $gens_cyc ; do

    for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
       for snow in WEASD SNOD ; do 
	 if [  -s $COMOUT_gefs/gefs.ens${mb}.t${cyc}z.grid3.f024.grib2 ] ; then
	   export lead='24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384'
	   ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_SNOW24h.conf &
	 fi
       done
    done
    wait
    
  done

  mv $output_base/*.nc $COMOUT_gefs/.
fi



if [ $modnam = cmce_snow24h ] ; then

  export output_base=${WORK}/snow/cmce_snow24h.${gens_cyc}
  export cyc
  export mb
  export model=cmce
  export modelpath=$COMOUT_cmce
  export snow 
  for cyc in $gens_cyc ; do
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do

       for snow in WEASD SNOD ; do
        if [  -s $COMOUT_cmce/cmce.ens${mb}.t${cyc}z.grid3.f024.grib2 ] ; then  
         export lead='24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384'
         ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_SNOW24h.conf &
        fi
       done
       
     done
     wait
  done

  mv $output_base/*.nc $COMOUT_cmce/.
fi

if [ $modnam = ecme_snow24h ] ; then

    export cyc
    export mb
    export model=ecme
    export modelpath=$COMOUT_ecme

  for cyc in 00 12 ; do

     export output_base=${WORK}/snow/ecme_snow24h.${cyc}

     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 ; do
       if [  -s $COMOUT_ecme/ecme.ens${mb}.t${cyc}z.grid4_apcp.f024.grib1 ] ; then
    	  export lead='24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360 '
          ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstECME_SNOW24h.conf &
       fi
     done
     wait
  done

  #cp $output_base/ecme*.nc $COMOUT_ecme
fi


if [ $modnam = gfs ] ; then

  for cyc in 00  ; do

    for  hhh in 024 048 072 096  120 144 168 192 216 240 264 288 312 336 360 384 ; do     
     gfs=$COMINgfsanl/gfs.$vday/${cyc}/atmos/gfs.t${cyc}z.pgrb2.1p00.f${hhh}
     $WGRIB2  $gfs|grep "HGT:500 mb"|$WGRIB2 -i $gfs -grib $COMOUT_gefs/gfs.t${cyc}z.grid3.f${hhh}.grib2 &
    done
    wait

  done

fi


if [ $modnam = osi_saf ] ; then
   
   osi=$COMINosi_saf/$INITDATE/seaice/osisaf/ice_conc_nh_polstere-100_multi_${INITDATE}1200.nc	
   if [ -s $osi ] ; then
     python ${USHevs}/global_ens/global_det_sea_ice_prep.py
     cp $WORK/atmos.${INITDATE}/osi_saf/*.nc $COMOUT_osi_saf/.
   else

        export subject="OSI_SAF Data Missing for EVS ${COMPONENT}"
        echo "Warning:  No OSI_SAF data  available for ${INITDATE}" > mailmsg
        echo Missing file is $osi  >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $maillist
    fi 
fi

# Ice concentration starts from f000. There is amount of ice at beginning.
# So, for f024 ice concentation, it shoule be  averaged of f000, f006, f012
# f018 and f024 
if [ $modnam = gefs_icec24h ] ; then

    export output_base=${WORK}/gefs_icec24h
    export model=gefs
    export modelpath=$COMOUT_gefs

    export cyc
    export mb
    export accum=24

    for cyc in 00 ; do

      for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
    	 export lead='24, 48, 72, 96, 120, 144, 168, 192, 216,  240,  264,  288,  312,  336,  360,  384' 

	 if [  -s $COMOUT_gefs/gefs.ens${mb}.t${cyc}z.grid3.f024.grib2 ] ; then
            ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_ICEC.conf &
	 fi 

      done
      wait
    done

    mv $output_base/gefs*icec*.nc $COMOUT_gefs
fi

if [ $modnam = gefs_icec7day ] ; then

    export output_base=${WORK}/gefs_icec7day
    export model=gefs
    export modelpath=$COMOUT_gefs 
		              
    export cyc
    export mb
    export accum=168	

    #for cyc in 00  12  ; do
    for cyc in 00  ; do

     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
        if [ $cyc = 00 ] ; then
            export lead='168, 192, 216,  240,  264,  288,  312,  336,  360,  384'
        elif [ $cyc = 12 ] ; then 
            export lead='180, 204, 228, 252, 276, 300, 324, 348, 372 '
        fi
        ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_ICEC.conf &
     done
     wait
   done
							     
   mv $output_base/gefs*icec*.nc $COMOUT_gefs
fi

if [ $modnam = gefs_sst24h ] ; then

    export output_base=${WORK}/gefs_sst24h
    export model=gefs
    export modelpath=$COMOUT_gefs

    export cyc
    export mb
    export accum=24

    for cyc in 00  12  ; do

       if [ $cyc = 00 ] ; then
         export lead='24, 48, 72, 96, 120, 144, 168, 192, 216,  240,  264,  288,  312,  336,  360,  384'
       elif [ $cyc = 12 ] ; then
         export lead='36, 60, 84, 108, 132, 156, 180, 204, 228, 252, 276, 300, 324, 348, 372 '
       fi

       for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
	 if [  -s $COMOUT_gefs/gefs.ens${mb}.t${cyc}z.grid3.f024.grib2 ] ; then
           ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_SST24h.conf &
	 fi 
       done
       wait

    done

    mv $output_base/gefs*sst*.nc $COMOUT_gefs

fi

