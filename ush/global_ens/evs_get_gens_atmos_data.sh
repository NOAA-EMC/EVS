#!/bin/ksh

set -x

modnam=$1
gens_cyc=$2
fhr_beg=$3
fhr_end=$4

export vday=${vday:-$PDYm2}    #for ensemble, use past-2 day as validation day
export vdate=${vdate:-$vday$cyc}

export copygb2=$COPYGB2
export cnvgrib=$CNVGRIB
export wgrib2=$WGRIB2
export ndate=$NDATE


#############################################################
#1:Get gfs analysis grib2 data in GRID#3 (1-degree global)
############################################################
if [ $modnam = gfsanl ]; then

  echo $modnam is print here ...............

  for cyc in 00 06 12 18 ; do

    cp $COMINgfsanl/gfs.$vday/${cyc}/atmos/gfs.t${cyc}z.pgrb2.1p00.f000 $COMOUT_gefs/gfsanl.t${cyc}z.grid3.f000.grib2

  done
fi


#Note CMCE has no DPT 
if [ $modnam = cmcanl ] ; then


  cd $WORK

    export outdata=$COMOUT_cmce

    for cyc in 00 12; do
      origin=$COMINcmce/cmce.$vday/$cyc/pgrb2ap5
      >$WORK/cmce.upper.${cyc}.${mb}.${h3}
      >$WORK/cmce.sfc.${cyc}.${mb}.${h3}
      >output.${cyc}

      if [ ! -s $COMINcmce/cmce.$vday/$cyc/pgrb2ap5/cmc_gec00.t${cyc}z.pgrb2a.0p50.anl ] ; then 
        cmcanl=$origin/cmc_gec00.t${cyc}z.pgrb2a.0p50.f000
      else
        cmcanl=$origin/cmc_gec00.t${cyc}z.pgrb2a.0p50.anl
      fi



      $WGRIB2  $cmcanl|grep "HGT:"|grep "anl:ENS=low-res"|$WGRIB2 -i $cmcanl -grib $WORK/output.${cyc}
      cat $WORK/output.${cyc} >> $WORK/cmce.upper.${cyc}.${mb}.${h3}


      $WGRIB2  $cmcanl|grep "TMP:"|grep "anl:ENS=low-res"|$WGRIB2 -i $cmcanl -grib $WORK/output.${cyc}
      cat $WORK/output.${cyc} >> $WORK/cmce.upper.${cyc}.${mb}.${h3}

      $WGRIB2  $cmcanl|grep "UGRD:"|grep "anl:ENS=low-res"|$WGRIB2 -i $cmcanl -grib $WORK/output.${cyc}
      cat $WORK/output.${cyc} >> $WORK/cmce.upper.${cyc}.${mb}.${h3}

      $WGRIB2  $cmcanl|grep "VGRD:"|grep "anl:ENS=low-res"|$WGRIB2 -i $cmcanl -grib $WORK/output.${cyc}
      cat $WORK/output.${cyc} >> $WORK/cmce.upper.${cyc}.${mb}.${h3}

      $WGRIB2 $cmcanl|grep "PRMSL:"|grep "anl:ENS=low-res"|$WGRIB2 -i $cmcanl -grib $WORK/output.${cyc}
      cat $WORK/output.${cyc} >> $WORK/cmce.sfc.${cyc}.${mb}.${h3}

       $WGRIB2 $cmcanl|grep "RH:"|grep "anl:ENS=low-res"|$WGRIB2 -i $cmcanl -grib $WORK/output.${cyc}
      cat $WORK/output.${cyc} >> $WORK/cmce.sfc.${cyc}.${mb}.${h3}

 
      #cat $WORK/cmce.sfc >> $WORK/cmce.upper.adjusted
      #use copygb2 to reverse north-south direction, and convert ftom 0.5x0.5 degree to 1x1 degree
      #$COPYGB2 -g"0 6 0 0 0 0 0 0 360 181 0 -1 90000000 0 48 -90000000 359000000 1000000 1000000 0" -x $WORK/cmce.upper.adjusted  $outdata/cmcanl.t${cyc}z.grid3.f00.grib2
      cat $WORK/cmce.sfc.${cyc}.${mb}.${h3} >> $WORK/cmce.upper.${cyc}.${mb}.${h3}
      $COPYGB2 -g"0 6 0 0 0 0 0 0 360 181 0 -1 90000000 0 48 -90000000 359000000 1000000 1000000 0" -x $WORK/cmce.upper.${cyc}.${mb}.${h3} $outdata/cmcanl.t${cyc}z.grid3.f000.grib2

      rm   $WORK/cmce.upper.${cyc}.${mb}.${h3} $WORK/cmce.sfc.${cyc}.${mb}.${h3}  $WORK/output.${cyc}
   done
 
fi 




###########################################
#5:Get GFS 20 member grib2 file in grid3 
###########################################
if [ $modnam = gefs ] ; then

  cd $WORK
  total=30

   export outdata=$COMOUT_gefs

   if [ ! -s $outdata/gefs.ens30.t12z.grid3.f384.grib2 ] ; then

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

             >$WORK/gefs.upper.${cyc}.${mb}.${hhh}
             >$WORK/gefs.sfc.${cyc}.${mb}.${hhh}
             $WGRIB2  $gefs|grep "HGT:"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
             cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.upper.${cyc}.${mb}.${hhh}

             $WGRIB2  $gefs|grep "TMP:"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
             cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.upper.${cyc}.${mb}.${hhh}

             $WGRIB2  $gefs|grep "UGRD:"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
             cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.upper.${cyc}.${mb}.${hhh}

             $WGRIB2  $gefs|grep "VGRD:"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
             cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.upper.${cyc}.${mb}.${hhh}

             $WGRIB2  $gefs|grep "RH:"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
             cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.upper.${cyc}.${mb}.${hhh}

             $WGRIB2 $gefs|grep "TCDC:"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
             cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.sfc.${cyc}.${mb}.${hhh}

             $WGRIB2 $gefs|grep "APCP:"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
             cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.sfc.${cyc}.${mb}.${hhh}

	     $WGRIB2 $gefs|grep "WEASD:"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
	     cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.sfc.${cyc}.${mb}.${hhh}

             $WGRIB2 $gefs|grep "PRMSL:"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
             cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.sfc.${cyc}.${mb}.${hhh}

             cat $WORK/gefs.sfc.${cyc}.${mb}.${hhh}  >> $WORK/gefs.upper.${cyc}.${mb}.${hhh}

          
             $WGRIB2 $gefs_cvc|grep "DPT:2 m"|$WGRIB2 -i $gefs_cvc -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
             cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.upper.${cyc}.${mb}.${hhh}

             $WGRIB2 $gefs_cvc|grep "VIS:surface"|$WGRIB2 -i $gefs_cvc -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
             cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.upper.${cyc}.${mb}.${hhh}
 
             $WGRIB2 $gefs_cvc|grep "CAPE:surface"|$WGRIB2 -i $gefs_cvc -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
             cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.upper.${cyc}.${mb}.${hhh}

             $WGRIB2 $gefs_cvc|grep "HGT:cloud ceiling"|$WGRIB2 -i $gefs_cvc -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
             cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.upper.${cyc}.${mb}.${hhh}

             #$WGRIB2 $gefs_cvc|grep "SPFH:"|$WGRIB2 -i $gefs_cvc -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
             #cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.upper.${cyc}.${mb}.${hhh} 

            $COPYGB2 -g"0 6 0 0 0 0 0 0 360 181 0 -1 90000000 0 48 -90000000 359000000 1000000 1000000 0" -x $WORK/gefs.upper.${cyc}.${mb}.${hhh} $outdata/gefs.ens${mb}.t${cyc}z.grid3.f${hhh}.grib2
            #mv $WORK/gefs.upper.${cyc}.${mb}.${hhh} $outdata/gefs.ens${mb}.t${cyc}z.grid4.f${hhh}.grib2

            rm -f  $WORK/gefs.upper.${cyc}.${mb}.${hhh} $WORK/gefs.sfc.${cyc}.${mb}.${hhh}         

            #nfhrs=`expr $nfhrs + 12`
            nfhrs=`expr $nfhrs + 6`
         done

         mbr=`expr $mbr + 1`
      done

     done   #for cyc

   fi # check if file not existing 

fi





###########################################
#8:Get CMCE 20 member grib2 file in grid3 
###########################################
if [ $modnam = cmce ] ; then

  cd $WORK

  total=20

   export outdata=$COMOUT_cmce

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

             >$WORK/cmce.upper.${cyc}.${mb}.${h3}
             >$WORK/cmce.sfc.${cyc}.${mb}.${h3}
             
             $WGRIB2  $cmce|grep "HGT:"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
             cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.upper.${cyc}.${mb}.${h3}

             $WGRIB2  $cmce|grep "TMP:"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
             cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.upper.${cyc}.${mb}.${h3}

             $WGRIB2  $cmce|grep "UGRD:"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
             cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.upper.${cyc}.${mb}.${h3}

             $WGRIB2  $cmce|grep "VGRD:"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
             cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.upper.${cyc}.${mb}.${h3}

             $WGRIB2  $cmce|grep "RH:"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
             cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.upper.${cyc}.${mb}.${h3}

             $WGRIB2 $cmce|grep "TCDC:local level"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
             cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.sfc.${cyc}.${mb}.${h3}

             $WGRIB2 $cmce|grep "APCP:"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
             cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.sfc.${cyc}.${mb}.${h3}

	     $WGRIB2 $cmce|grep "WEASD:"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
	     cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.sfc.${cyc}.${mb}.${h3}

             $WGRIB2 $cmce|grep "PRMSL:"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
             cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.sfc.${cyc}.${mb}.${h3}

             $WGRIB2 $cmce|grep "CAPE:atmos col"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
             cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.sfc.${cyc}.${mb}.${h3}

             #$WGRIB2 $cmce|grep "SPFH:"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
             #cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.sfc.${cyc}.${mb}.${h3}

             #echo "cmce.upper" | $EXECevs_g2g/evs_g2g_adjustCMC.x
             #cat $WORK/cmce.sfc >> $WORK/cmce.upper.adjusted
             #In MET, not necessary to adjust upper level fields for CMCE members since
             #MET  uses string of field name to read data

             #use copygb2 to reverse N-S grid direction and convert 0.5x0.5 deg to 1x1 deg
             #$COPYGB2 -g"0 6 0 0 0 0 0 0 360 181 0 -1 90000000 0 48 -90000000 359000000 1000000 1000000 0" -x $WORK/cmce.upper.adjusted $outdata/cmce.ens${mb}.t${cyc}z.grid3.f${hh}
           
             cat $WORK/cmce.sfc.${cyc}.${mb}.${h3} >> $WORK/cmce.upper.${cyc}.${mb}.${h3} 

             $COPYGB2 -g"0 6 0 0 0 0 0 0 360 181 0 -1 90000000 0 48 -90000000 359000000 1000000 1000000 0" -x $WORK/cmce.upper.${cyc}.${mb}.${h3} $outdata/cmce.ens${mb}.t${cyc}z.grid3.f${h3}.grib2

             rm -f  $WORK/cmce.upper.${cyc}.${mb}.${h3} $WORK/cmce.sfc.${cyc}.${mb}.${h3} 

           nfhrs=`expr $nfhrs + 12`

         done

         mbr=`expr $mbr + 1` 

       done

    done # for cyc

fi



if [ $modnam = ecme ] ; then

  echo "getting ECMWF ensemble member files ...."
  #Note all files are in non-NCEP but in ECMWF GRIB1 format 

  export outdata=$COMOUT_ecme

  for cyc in 00 12 ; do
    $USHevs/global_ens/evs_process_atmos_ecme.sh ${vday}${cyc} ${cyc}
  done 

fi


if [ $modnam = prepbufr ] ; then
   
   > run_pb2nc.sh

   for cyc in 00 06 12 18 ; do

      > run_pb2nc.${cyc}.sh
      
      echo  "export output_base=${WORK}/pb2nc" >> run_pb2nc.${cyc}.sh

      echo  "export vbeg=${cyc}" >> run_pb2nc.${cyc}.sh
      echo  "export vend=${cyc}" >> run_pb2nc.${cyc}.sh

      echo  "${METPLUS_PATH}/ush/master_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsGFS_Prepbufr.cong" >> run_pb2nc.${cyc}.sh

      echo  "${METPLUS_PATH}/ush/master_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsGFS_Prepbufr_Profile.cong" >> run_pb2nc.${cyc}.sh


      chmod +x run_pb2nc.${cyc}.sh
      echo "run_pb2nc.${cyc}.sh" >> run_pb2nc.sh
           
  done

      echo "cp ${WORK}/pb2nc/prepbufr_nc/*.nc $COMOUT_gefs" >> run_pb2nc.sh  

  chmod +x run_pb2nc.sh
  sh run_pb2nc.sh


fi  


if [ $modnam = ccpa ] ; then

  day1=`$ndate -24 ${vday}12`
  vday_1=${day1:0:8}

  for cyc in 00 06 12 18 ; do
    $COPYGB2 -g"0 6 0 0 0 0 0 0 360 181 0 -1 90000000 0 48 -90000000 359000000 1000000 1000000 0" -x  $COMINccpa/ccpa.${vday}/$cyc/ccpa.t${cyc}z.06h.1p0.conus.gb2 ${COMOUT_gefs}/ccpa.t${cyc}z.grid3.06h.f00.grib2 

  done

  ccpa24=${WORK}/ccpa24
  mkdir $ccpa24
  rm -f ${WORK}/ccpa24/*.grib2

  for cyc in 12 ; do
    cp ${COMOUT_gefs}/ccpa.t12z.grid3.06h.f00.grib2 ${WORK}/ccpa24/ccpa1
    cp ${COMOUT_gefs}/ccpa.t06z.grid3.06h.f00.grib2 ${WORK}/ccpa24/ccpa2
    cp ${COMOUT_gefs}/ccpa.t00z.grid3.06h.f00.grib2 ${WORK}/ccpa24/ccpa3
    cp ${COMOUT}.${vday_1}/gefs/ccpa.t18z.grid3.06h.f00.grib2 ${WORK}/ccpa24/ccpa4

    pcp_combine ${vday_1}_120000 06 ${vday}_120000 24 ccpa.t12z.grid3.24h.f00.nc -pcpdir ${WORK}/ccpa24
    cp ccpa.t12z.grid3.24h.f00.nc $COMOUT_gefs/.
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
         $copygb2  -g"0 6 0 0 0 0 0 0 360 181 0 -1 90000000 0 48 -90000000 359000000 1000000 1000000 0" -i3 -x gefs.ens${mb}.t${cyc}z.grid4.06h.f${hhh}.grib2 $COMOUT_gefs/gefs.ens${mb}.t${cyc}z.grid3.06h.f${hhh}.grib2

        else
         
         #make up 20210923~20210930 
         gefs=$COMOUT_gefs/gefs.ens${mb}.t${cyc}z.grid3.f${hhh}.grib2
         $wgrib2 -match "APCP" $gefs|$wgrib2 -i $gefs -grib $COMOUT_gefs/gefs.ens${mb}.t${cyc}z.grid3.06h.f${hhh}.grib2

        fi

        fhr=$((fhr+6))

       done
    done
   done

fi 

if [ $modnam = gefs_apcp24h ] ; then
 
    for cyc in $gens_cyc ; do

     apcp24=$WORK/apcp24.gefs.$cyc
     mkdir -p $apcp24
     rm -f $apcp24/*.grib2

     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do

       typeset -Z3 hhh
       typeset -Z3 hhh_6
       typeset -Z3 hhh_12
       typeset -Z3 hhh_18
       fhr=24
       while [ $fhr -le 384 ] ; do
         hhh=$fhr 
         apcp1=$COMOUT_gefs/gefs.ens${mb}.t${cyc}z.grid3.06h.f${hhh}.grib2
         cp $apcp1 $apcp24/.

         fhr_6=$((fhr-6))
         hhh_6=$fhr_6
         apcp2=$COMOUT_gefs/gefs.ens${mb}.t${cyc}z.grid3.06h.f${hhh_6}.grib2
         cp $apcp2 $apcp24/.

         fhr_12=$((fhr-12))
         hhh_12=$fhr_12
         apcp3=$COMOUT_gefs/gefs.ens${mb}.t${cyc}z.grid3.06h.f${hhh_12}.grib2
         cp $apcp3 $apcp24/.

         fhr_18=$((fhr-18))
         hhh_18=$fhr_18
         apcp4=$COMOUT_gefs/gefs.ens${mb}.t${cyc}z.grid3.06h.f${hhh_18}.grib2
         cp $apcp4 $apcp24/.

         fcst_cyc=${vday}${cyc}
	 #Note fcst_time is future, not backward. This is just reversed to the pcp_combine -sum in HREF 
         fcst_time=`$ndate +$fhr $fcst_cyc`  
         fvday=${fcst_time:0:8} #forecast hours --> day+hour format
         hour=${fcst_time:8:2}
         pcp_combine -sum ${vday}_${cyc}0000 06 ${fvday}_${hour} 24 gefs.ens${mb}.t${cyc}z.grid3.24h.f${hhh}.nc -pcpdir $apcp24 -field 'name="APCP"; level="A06";'
         cp gefs.ens${mb}.t${cyc}z.grid3.24h.f${hhh}.nc $COMOUT_gefs
         fhr=$((fhr+12))
         rm -f $apcp24/*.grib2
       done
      done
    done

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
         $copygb2  -g"0 6 0 0 0 0 0 0 360 181 0 -1 90000000 0 48 -90000000 359000000 1000000 1000000 0" -i3 -x cmce.ens${mb}.t${cyc}z.grid4.06h.f${hhh}.grib2 $COMOUT_cmce/cmce.ens${mb}.t${cyc}z.grid3.06h.f${hhh}.grib2
         fhr=$((fhr+6))
       done

    done
   done
fi

if [ $modnam = cmce_apcp24h ] ; then

   for cyc in $gens_cyc ; do

     apcp24=$WORK/apcp24.cmce.$cyc
     mkdir -p $apcp24
     rm -f $apcp24/*.grib2


     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do

       typeset -Z3 hhh
       typeset -Z3 hhh_6
       typeset -Z3 hhh_12
       typeset -Z3 hhh_18
       fhr=24
       while [ $fhr -le 384 ] ; do
         hhh=$fhr
         cmce1=$COMOUT_cmce/cmce.ens${mb}.t${cyc}z.grid3.06h.f${hhh}.grib2
         cp $cmce1 $apcp24/.

         fhr_6=$((fhr-6))
         hhh_6=$fhr_6
         cmce2=$COMOUT_cmce/cmce.ens${mb}.t${cyc}z.grid3.06h.f${hhh_6}.grib2
         cp $cmce2 $apcp24/.

         fhr_12=$((fhr-12))
         hhh_12=$fhr_12
         cmce3=$COMOUT_cmce/cmce.ens${mb}.t${cyc}z.grid3.06h.f${hhh_12}.grib2
         cp $cmce3 $apcp24/.

         fhr_18=$((fhr-18))
         hhh_18=$fhr_18
         cmce4=$COMOUT_cmce/cmce.ens${mb}.t${cyc}z.grid3.06h.f${hhh_18}.grib2
         cp $cmce4 $apcp24/.
        fcst_cyc=${vday}${cyc}
         fcst_time=`$ndate +$fhr $fcst_cyc`
         fvday=${fcst_time:0:8} #forecast hours --> day+hour format
         hour=${fcst_time:8:2}
         pcp_combine -sum ${vday}_${cyc}0000 06 ${fvday}_${hour} 24 cmce.ens${mb}.t${cyc}z.grid3.24h.f${hhh}.nc -pcpdir $apcp24 -field 'name="APCP"; level="A06";'
         cp cmce.ens${mb}.t${cyc}z.grid3.24h.f${hhh}.nc $COMOUT_cmce
         fhr=$((fhr+12))
         rm -f $apcp24/*.grib2
       done
     done
   done
fi

if [ $modnam = ecme_apcp24h ] ; then

  for cyc in 00 12 ; do
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40  41 42 43 44 45 46 47 48 49 50  ; do


       pcp_combine -subtract \
        $COMOUT_ecme/ecme.ens${mb}.t${cyc}z.grid3_apcp.f024.grib1 'name="TP"; level="L0";' \
        $COMOUT_ecme/ecme.ens${mb}.t${cyc}z.grid3_apcp.f000.grib1 'name="TP"; level="L0";' \
        ecme.ens${mb}.t${cyc}z.grid3.24h.f024.nc
        cp ecme.ens${mb}.t${cyc}z.grid3.24h.f024.nc $COMOUT_ecme 


       typeset -Z3 hhh
       typeset -Z3 hhh_24
       fhr=36
       while [ $fhr -le 360 ] ; do
         hhh=$fhr

         fhr_24=$((fhr-24))
         hhh_24=$fhr_24

         pcp_combine -subtract \
           $COMOUT_ecme/ecme.ens${mb}.t${cyc}z.grid3_apcp.f${hhh}.grib1  \
           'name="TP"; level="L0";' \
           $COMOUT_ecme/ecme.ens${mb}.t${cyc}z.grid3_apcp.f${hhh_24}.grib1 \
           'name="TP"; level="L0";' \
           ecme.ens${mb}.t${cyc}z.grid3.24h.f${hhh}.nc
           cp ecme.ens${mb}.t${cyc}z.grid3.24h.f${hhh}.nc $COMOUT_ecme 
         fhr=$((fhr+12))
       done

     done
  done

fi


if [ $modnam = nohrsc24h ] ; then
 
  for cyc in 00 12 ; do
    snowfall=$COMINsnow/${vday}/wgrbbul/nohrsc_snowfall/sfav2_CONUS_24h_${vday}${cyc}_grid184.grb2
    cp $snowfall $COMOUT_gefs/nohrsc.t${cyc}z.grid184.grb2
  done

fi

if [ $modnam = gefs_snow24h ] ; then

  #for cyc in 00 12 ; do
  for cyc in $gens_cyc ; do

     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do

       typeset -Z3 hhh
       typeset -Z3 hhh_24
       fhr=24
       while [ $fhr -le 384 ] ; do
            hhh=$fhr
            fhr_24=$((fhr-24))
            hhh_24=$fhr_24
            pcp_combine -subtract \
            $COMOUT_gefs/gefs.ens${mb}.t${cyc}z.grid3.f${hhh}.grib2  \
         	                    'name="WEASD"; level="Z0";' \
            $COMOUT_gefs/gefs.ens${mb}.t${cyc}z.grid3.f${hhh_24}.grib2 \
      	        	            'name="WEASD"; level="Z0";' \
             gefs.ens${mb}.t${cyc}z.grid3.weasd_24h.f${hhh}.nc
            cp gefs.ens${mb}.t${cyc}z.grid3.weasd_24h.f${hhh}.nc $COMOUT_gefs
           fhr=$((fhr+12))
       done
     done
  done

fi

if [ $modnam = cmce_snow24h ] ; then

  for cyc in 00 12 ; do
  #for cyc in $gens_cyc ; do

     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do

       typeset -Z3 hhh
       typeset -Z3 hhh_24
       fhr=24
       while [ $fhr -le 384 ] ; do
            hhh=$fhr
            fhr_24=$((fhr-24))
            hhh_24=$fhr_24
            pcp_combine -subtract \
            $COMOUT_cmce/cmce.ens${mb}.t${cyc}z.grid3.f${hhh}.grib2  \
                                    'name="WEASD"; level="Z0";' \
            $COMOUT_cmce/cmce.ens${mb}.t${cyc}z.grid3.f${hhh_24}.grib2 \
                                    'name="WEASD"; level="Z0";' \
             cmce.ens${mb}.t${cyc}z.grid3.weasd_24h.f${hhh}.nc
            cp cmce.ens${mb}.t${cyc}z.grid3.weasd_24h.f${hhh}.nc $COMOUT_cmce
           fhr=$((fhr+12))
       done
     done
  done

fi

if [ $modnam = ecme_snow24h ] ; then

  for cyc in 00 12 ; do
  #for cyc in $gens_cyc ; do

     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30; do

       typeset -Z3 hhh
       typeset -Z3 hhh_24
       fhr=24
       while [ $fhr -le 360 ] ; do
            hhh=$fhr
            fhr_24=$((fhr-24))
            hhh_24=$fhr_24
            pcp_combine -subtract \
            $COMOUT_ecme/ecme.ens${mb}.t${cyc}z.grid3_apcp.f${hhh}.grib1  \
                                    'name="SF"; level="L0";' \
            $COMOUT_ecme/ecme.ens${mb}.t${cyc}z.grid3_apcp.f${hhh_24}.grib1 \
                                    'name="SF"; level="L0";' \
             ecme.ens${mb}.t${cyc}z.grid3.weasd_24h.f${hhh}.nc
            cp ecme.ens${mb}.t${cyc}z.grid3.weasd_24h.f${hhh}.nc $COMOUT_ecme
           fhr=$((fhr+12))
       done
     done
  done

fi

