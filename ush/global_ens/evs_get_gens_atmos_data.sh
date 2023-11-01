#!/bin/ksh
set -x

modnam=$1
gens_ihour=$2
fhr_beg=$3
fhr_end=$4


export vday=${INITDATE:-$PDYm2}    #for ensemble, use past-2 day as validation day
export vdate=${vdate:-$vday$ihour}

export cnvgrib=$CNVGRIB
export wgrib2=$WGRIB2
export ndate=$NDATE


#############################################################
#1:Get gfs analysis grib2 data in GRID#3 (1-degree global)
############################################################
if [ $modnam = gfsanl ]; then

  echo $modnam is print here ...............

  for ihour in 00 06 12 18 ; do
    ###[[ $SENDCOM="YES" ]] && cp $COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.f000 $COMOUTgefs/gfsanl.t${ihour}z.grid3.f000.grib2

    #check if gfsanl is missing:
    missing=no
    if [ ! -s $COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.anl ] ; then
      if [ $SENDMAIL = YES ]; then
        export subject="GFS Analysis Data Missing for EVS ${COMPONENT}"
        echo "Warning: No GFS analysis available for ${INITDATE}${ihour}" > mailmsg
        echo Missing file is $COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.anl >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $maillist
      fi
     missing=yes
    fi

   if [ $missing = no ] ; then 
    [[ $SENDCOM="YES" ]] && cp $COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.anl $COMOUTgefs/gfsanl.t${ihour}z.grid3.f000.grib2
    #There are no U10, V10 in GFS analysis, so use GFS*f000 as alternative
    GFSf000=$COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.f000 
    $WGRIB2  $GFSf000|grep "UGRD:10 m above ground"|$WGRIB2 -i $GFSf000 -grib $WORK/U10_f000.${ihour}
    cat $WORK/U10_f000.${ihour} >> $COMOUTgefs/gfsanl.t${ihour}z.grid3.f000.grib2
    $WGRIB2  $GFSf000|grep "VGRD:10 m above ground"|$WGRIB2 -i $GFSf000 -grib $WORK/V10_f000.${ihour}
    cat $WORK/V10_f000.${ihour} >> $COMOUTgefs/gfsanl.t${ihour}z.grid3.f000.grib2
   fi 
 done

   if [ $missing = no ] ; then
    #For WMO 1.5 deg verification 
    $wgrib2 $COMOUTgefs/gfsanl.t00z.grid3.f000.grib2 -set_grib_type same -new_grid_winds earth -new_grid latlon 0:240:1.5 -90:121:1.5 $COMOUTgefs/gfsanl.t00z.deg1.5.f000.grib2 
   fi
fi

#Note CMCE has no DPT 
if [ $modnam = cmcanl ] ; then


  cd $WORK

    export outdata=$COMOUTcmce

    for ihour in 00 12; do
      origin=$COMINcmce/cmce.$vday/$ihour/pgrb2ap5
      >$WORK/cmce.upper.${ihour}.${mb}.${h3}
      >$WORK/cmce.sfc.${ihour}.${mb}.${h3}
      >output.${ihour}

      if [ ! -s $COMINcmce/cmce.$vday/$ihour/pgrb2ap5/cmc_gec00.t${ihour}z.pgrb2a.0p50.anl ] ; then 
        cmcanl=$origin/cmc_gec00.t${ihour}z.pgrb2a.0p50.f000
      else
        cmcanl=$origin/cmc_gec00.t${ihour}z.pgrb2a.0p50.anl
      fi

     missing=no
     if [ ! -s $cmcanl ] ; then
       if [ $SENDMAIL = YES ]; then
         export subject="CMC Analysis Data Missing for EVS ${COMPONENT}"
         echo "Warning: No CMC analysis available for ${INITDATE}${ihour}" > mailmsg
         echo Missing file is $cmcanl >> mailmsg
         echo "Job ID: $jobid" >> mailmsg
         cat mailmsg | mail -s "$subject" $maillist
       fi
     missing=yes
    fi

   if [ $missing = no ] ; then
     for level in 10 50 100 200 250 300 400 500 700 850 925 1000 ; do
      $WGRIB2  $cmcanl|grep "UGRD:$level mb"|grep "anl:ENS=low-res"|$WGRIB2 -i $cmcanl -grib $WORK/output.${ihour}
      cat $WORK/output.${ihour} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}

      $WGRIB2  $cmcanl|grep "VGRD:$level mb"|grep "anl:ENS=low-res"|$WGRIB2 -i $cmcanl -grib $WORK/output.${ihour}
      cat $WORK/output.${ihour} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}
     done	     

      $WGRIB2  $cmcanl|grep "HGT:"|grep "anl:ENS=low-res"|$WGRIB2 -i $cmcanl -grib $WORK/output.${ihour}
      cat $WORK/output.${ihour} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}


      $WGRIB2  $cmcanl|grep "TMP:"|grep "anl:ENS=low-res"|$WGRIB2 -i $cmcanl -grib $WORK/output.${ihour}
      cat $WORK/output.${ihour} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}

      $WGRIB2  $cmcanl|grep "UGRD:10 m "|grep "anl:ENS=low-res"|$WGRIB2 -i $cmcanl -grib $WORK/output.${ihour}
      cat $WORK/output.${ihour} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}

      $WGRIB2  $cmcanl|grep "VGRD:10 m "|grep "anl:ENS=low-res"|$WGRIB2 -i $cmcanl -grib $WORK/output.${ihour}
      cat $WORK/output.${ihour} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}

      $WGRIB2 $cmcanl|grep "PRMSL:"|grep "anl:ENS=low-res"|$WGRIB2 -i $cmcanl -grib $WORK/output.${ihour}
      cat $WORK/output.${ihour} >> $WORK/cmce.sfc.${ihour}.${mb}.${h3}

       $WGRIB2 $cmcanl|grep "RH:"|grep "anl:ENS=low-res"|$WGRIB2 -i $cmcanl -grib $WORK/output.${ihour}
      cat $WORK/output.${ihour} >> $WORK/cmce.sfc.${ihour}.${mb}.${h3}

 
      #cat $WORK/cmce.sfc >> $WORK/cmce.upper.adjusted
      #use wgrib2 to reverse north-south direction, and convert ftom 0.5x0.5 degree to 1x1 degree
      cat $WORK/cmce.sfc.${ihour}.${mb}.${h3} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}

       $wgrib2 $WORK/cmce.upper.${ihour}.${mb}.${h3} -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003 $outdata/cmcanl.t${ihour}z.grid3.f000.grib2


    fi
   done

   if [ $missing = no ] ; then
    $wgrib2 $COMOUTcmce/cmcanl.t00z.grid3.f000.grib2 -set_grib_type same -new_grid_winds earth -new_grid latlon 0:240:1.5 -90:121:1.5 $COMOUTcmce/cmcanl.t00z.deg1.5.f000.grib2
   fi
fi 




###########################################
#5:Get GFS 20 member grib2 file in grid3 
###########################################
if [ $modnam = gefs ] ; then

  cd $WORK
  total=30

   export outdata=$COMOUTgefs

   if [ ! -s $outdata/gefs.ens30.t12z.grid3.f384.grib2 ] ; then

    #for ihour in 00 06 12 18 ; do
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

	     for level in 10 50 100 200 250 300 400 500 700 850 925 1000 ; do
                  $WGRIB2  $gefs|grep "UGRD:$level mb"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
	          cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}

	          $WGRIB2  $gefs|grep "VGRD:$level mb"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
	          cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}
             done	

             $WGRIB2  $gefs|grep "HGT:"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
             cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}

             $WGRIB2  $gefs|grep "TMP:"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
             cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}

             $WGRIB2  $gefs|grep "UGRD:10 m "|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
             cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}

             $WGRIB2  $gefs|grep "VGRD:10 m "|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
             cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}

             $WGRIB2  $gefs|grep "RH:"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
             cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}

             $WGRIB2 $gefs|grep "TCDC:"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
             cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.sfc.${ihour}.${mb}.${hhh}

             $WGRIB2 $gefs|grep "APCP:"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
             cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.sfc.${ihour}.${mb}.${hhh}

	     $WGRIB2 $gefs|grep "WEASD:"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
	     cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.sfc.${ihour}.${mb}.${hhh}

	     $WGRIB2 $gefs|grep "SNOD:"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
	     cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.sfc.${ihour}.${mb}.${hhh}

             $WGRIB2 $gefs|grep "PRMSL:"|$WGRIB2 -i $gefs -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
             cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.sfc.${ihour}.${mb}.${hhh}

             cat $WORK/gefs.sfc.${ihour}.${mb}.${hhh}  >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}

          
             $WGRIB2 $gefs_cvc|grep "DPT:2 m"|$WGRIB2 -i $gefs_cvc -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
             cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}

             $WGRIB2 $gefs_cvc|grep "VIS:surface"|$WGRIB2 -i $gefs_cvc -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
             cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}
 
             $WGRIB2 $gefs_cvc|grep "CAPE:surface"|$WGRIB2 -i $gefs_cvc -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
             cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}

             $WGRIB2 $gefs_cvc|grep "HGT:cloud ceiling"|$WGRIB2 -i $gefs_cvc -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
             cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}

	     $WGRIB2 $gefs_cvc|grep "ICEC:surface"|$WGRIB2 -i $gefs_cvc -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
	     cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}

	     $WGRIB2 $gefs_cvc|grep "TMP:surface"|$WGRIB2 -i $gefs_cvc -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
	     cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}

             #$WGRIB2 $gefs_cvc|grep "SPFH:"|$WGRIB2 -i $gefs_cvc -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
             #cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh} 

            $wgrib2 $WORK/gefs.upper.${ihour}.${mb}.${hhh} -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003  $outdata/gefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2


            #nfhrs=`expr $nfhrs + 12`
            nfhrs=`expr $nfhrs + 6`
         done

         mbr=`expr $mbr + 1`
      done

     done   #for ihour

   fi # check if file not existing 

fi





###########################################
#8:Get CMCE 20 member grib2 file in grid3 
###########################################
if [ $modnam = cmce ] ; then

  cd $WORK

  total=20

   export outdata=$COMOUTcmce

     for ihour in $gens_ihour ; do

       origin=$COMINcmce/cmce.$vday/$ihour/pgrb2ap5

       mbr=1
       while [ $mbr -le $total ] ; do
         mb=$mbr
         typeset -Z2 mb

         nfhrs=$fhr_beg
         while [ $nfhrs -le $fhr_end ] ; do

           #hh=$nfhrs
           h3=$nfhrs           

           typeset -Z3 h3

             cmce=$origin/cmc_gep${mb}.t${ihour}z.pgrb2a.0p50.f${h3}

             >$WORK/cmce.upper.${ihour}.${mb}.${h3}
             >$WORK/cmce.sfc.${ihour}.${mb}.${h3}
             
	     for level in 10 50 100 200 250 300 400 500 700 850 925 1000 ; do
		$WGRIB2  $cmce|grep "UGRD:$level mb"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
		cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}

                $WGRIB2  $cmce|grep "VGRD:$level mb"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
              cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}
	     done

             $WGRIB2  $cmce|grep "HGT:"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
             cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}

             $WGRIB2  $cmce|grep "TMP:"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
             cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}

             $WGRIB2  $cmce|grep "UGRD:10 m "|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
             cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}

             $WGRIB2  $cmce|grep "VGRD:10 m "|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
             cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}

             $WGRIB2  $cmce|grep "RH:"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
             cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}

             $WGRIB2 $cmce|grep "TCDC:local level"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
             cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.sfc.${ihour}.${mb}.${h3}

             $WGRIB2 $cmce|grep "APCP:"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
             cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.sfc.${ihour}.${mb}.${h3}

	     $WGRIB2 $cmce|grep "WEASD:"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
	     cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.sfc.${ihour}.${mb}.${h3}

	     $WGRIB2 $cmce|grep "SNOD:"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
	     cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.sfc.${ihour}.${mb}.${h3}

             $WGRIB2 $cmce|grep "PRMSL:"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
             cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.sfc.${ihour}.${mb}.${h3}

             $WGRIB2 $cmce|grep "CAPE:atmos col"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
             cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.sfc.${ihour}.${mb}.${h3}

             #$WGRIB2 $cmce|grep "SPFH:"|$WGRIB2 -i $cmce -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
             #cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.sfc.${ihour}.${mb}.${h3}

             #echo "cmce.upper" | $EXECevs_g2g/evs_g2g_adjustCMC.x
             #cat $WORK/cmce.sfc >> $WORK/cmce.upper.adjusted
             #In MET, not necessary to adjust upper level fields for CMCE members since
             #MET  uses string of field name to read data

             #use wgrib2 to reverse N-S grid direction and convert 0.5x0.5 deg to 1x1 deg
           
             cat $WORK/cmce.sfc.${ihour}.${mb}.${h3} >> $WORK/cmce.upper.${ihour}.${mb}.${h3} 


	     $wgrib2 $WORK/cmce.upper.${ihour}.${mb}.${h3} -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003  $outdata/cmce.ens${mb}.t${ihour}z.grid3.f${h3}.grib2


           nfhrs=`expr $nfhrs + 12`

         done

         mbr=`expr $mbr + 1` 

       done

    done # for ihour

fi



if [ $modnam = ecme ] ; then

  echo "getting ECMWF ensemble member files ...."
  #Note all files are in non-NCEP but in ECMWF GRIB1 format 

  export outdata=$COMOUTecme

  for ihour in 00 12 ; do
    $USHevs/global_ens/evs_process_atmos_ecme.sh ${vday}${ihour} ${ihour}
  done 

fi


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
          echo "Warning:  No prepbufr analysis available for ${INITDATE}${ihour}" > mailmsg
          echo Missing file is $COMINobsproc/gdas.${vday}/${ihour}/atmos/gdas.t${ihour}z.prepbufr  >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $maillist
	fi
      fi 

      chmod +x run_pb2nc.${ihour}.sh
      echo "${DATA}/run_pb2nc.${ihour}.sh" >> run_pb2nc.sh
           
  done
      echo "chmod 640 ${WORK}/pb2nc/prepbufr_nc/*prepbufr*.nc" >> run_pb2nc.sh
      echo "chgrp rstprod ${WORK}/pb2nc/prepbufr_nc/*prepbufr*.nc" >> run_pb2nc.sh
      echo "cp ${WORK}/pb2nc/prepbufr_nc/*.nc $COMOUTgefs" >> run_pb2nc.sh
      echo "chmod 640 $COMOUTgefs/*prepbufr*.nc" >> run_pb2nc.sh
      echo "chgrp rstprod $COMOUTgefs/*prepbufr*.nc" >> run_pb2nc.sh

  chmod +x run_pb2nc.sh
  ${DATA}/run_pb2nc.sh


fi  


if [ $modnam = ccpa ] ; then

  day1=`$ndate -24 ${vday}12`
  export vday_1=${day1:0:8}

  for ihour in 00 06 12 18 ; do
    if [ -s $COMINccpa/ccpa.${vday}/$ihour/ccpa.t${ihour}z.06h.1p0.conus.gb2 ] ; then
      $wgrib2 $COMINccpa/ccpa.${vday}/$ihour/ccpa.t${ihour}z.06h.1p0.conus.gb2 -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003  ${COMOUTgefs}/ccpa.t${ihour}z.grid3.06h.f00.grib2
    else
        if [ $SENDMAIL = YES ]; then
          export subject="CCPA  Data Missing for EVS ${COMPONENT}"
          echo "Warning:  No CCPA analysis available for ${INITDATE}${ihour}" > mailmsg
          echo Missing file is $COMINccpa/ccpa.${vday}/$ihour/ccpa.t${ihour}z.06h.1p0.conus.gb2  >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $maillist
	fi
    fi 
  done

  export output_base=${WORK}/precip

  export ccpa24=${WORK}/ccpa24
  mkdir $ccpa24


  for ihour in 12 ; do
    cp ${COMOUTgefs}/ccpa.t12z.grid3.06h.f00.grib2 ${WORK}/ccpa24/ccpa1
    cp ${COMOUTgefs}/ccpa.t06z.grid3.06h.f00.grib2 ${WORK}/ccpa24/ccpa2
    cp ${COMOUTgefs}/ccpa.t00z.grid3.06h.f00.grib2 ${WORK}/ccpa24/ccpa3
    cp ${COMOUT}/atmos.${vday_1}/gefs/ccpa.t18z.grid3.06h.f00.grib2 ${WORK}/ccpa24/ccpa4

    if [ -s ${WORK}/ccpa24/ccpa1 ] && [ -s ${WORK}/ccpa24/ccpa2 ] && [ -s ${WORK}/ccpa24/ccpa3 ] && [ -s ${WORK}/ccpa24/ccpa4 ] ; then
       ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_obsCCPA24h.conf
       [[ $SENDCOM="YES" ]] && cp $output_base/ccpa.t12z.grid3.24h.f00.nc $COMOUTgefs/.
    else
       if [ $SENDMAIL = YES ]; then
         export subject="06h CCPA Data Missing for 24h CCPA generation"
         echo "Warning: At least one of ccpa06h files is missing  for ${INITDATE}${ihour}" > mailmsg
         echo Missing file is {COMOUTgefs}/ccpa.t00z.grid3.06h.f00.grib2, ${COMOUTgefs}/ccpa.t06z.grid3.06h.f00.grib2, ${COMOUTgefs}/ccpa.t12z.grid3.06h.f00.grib2, or ${COMOUT}.${vday_1}/gefs/ccpa.t18z.grid3.06h.f00.grib2  >> mailmsg
         echo "Job ID: $jobid" >> mailmsg
         cat mailmsg | mail -s "$subject" $maillist
       fi
      exit 
    fi  
  done
fi



if [ $modnam = gefs_apcp06h ] ; then

   for ihour in $gens_ihour ; do

     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do

       typeset -Z3 hhh
       fhr=06
       while [ $fhr -le 384 ] ; do
         hhh=$fhr

        if [ -s $COMINgefs/gefs.$vday/$ihour/atmos/pgrb2ap5/gep${mb}.t${ihour}z.pgrb2a.0p50.f${hhh} ] ; then

         gefs=$COMINgefs/gefs.$vday/$ihour/atmos/pgrb2ap5/gep${mb}.t${ihour}z.pgrb2a.0p50.f${hhh}
         $wgrib2 -match "APCP" $gefs|$wgrib2 -i $gefs -grib gefs.ens${mb}.t${ihour}z.grid4.06h.f${hhh}.grib2
         $wgrib2 gefs.ens${mb}.t${ihour}z.grid4.06h.f${hhh}.grib2 -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003 $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.06h.f${hhh}.grib2

        else
         
         #make up 20210923~20210930 
         gefs=$COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2
         $wgrib2 -match "APCP" $gefs|$wgrib2 -i $gefs -grib $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.06h.f${hhh}.grib2

        fi

        fhr=$((fhr+6))

       done
    done
   done

fi 

if [ $modnam = gefs_apcp24h ] ; then

    export output_base=${WORK}/precip/gefs_apcp24h
    export model=gefs
    export modelpath=$COMOUTgefs
    
    export ihour
    export mb

    for ihour in $gens_ihour ; do

     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
         if [ -s $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.f024.grib2 ] ; then 	
            export lead='24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384'
            ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_APCP24h.conf
	 fi
      done
    done

    [[ $SENDCOM="YES" ]] && cp ${output_base}/*.nc $COMOUTgefs/.
fi


if [ $modnam = cmce_apcp06h ] ; then

    for ihour in $gens_ihour ; do
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do

       typeset -Z3 hhh
       fhr=06
       while [ $fhr -le 384 ] ; do
         hhh=$fhr
         cmce=$COMINcmce/cmce.$vday/$ihour/pgrb2ap5/cmc_gep${mb}.t${ihour}z.pgrb2a.0p50.f${hhh}
         $wgrib2 -match "APCP" $cmce|$wgrib2 -i $cmce -grib cmce.ens${mb}.t${ihour}z.grid4.06h.f${hhh}.grib2
	 $wgrib2 cmce.ens${mb}.t${ihour}z.grid4.06h.f${hhh}.grib2 -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003 $COMOUTcmce/cmce.ens${mb}.t${ihour}z.grid3.06h.f${hhh}.grib2
         fhr=$((fhr+6))
       done

    done
   done
fi



if [ $modnam = cmce_apcp24h ] ; then

    export output_base=${WORK}/precip/cmce_apcp24h
    export model=cmce
    export modelpath=$COMOUTcmce
    
    export ihour
    export mb

    for ihour in $gens_ihour ; do
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do
	 if [ -s $COMOUTcmce/cmce.ens${mb}.t${ihour}z.grid3.06h.f024.grib2 ] ; then
	  export lead='24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384'
          ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstCMCE_APCP24h.conf
	 fi 
      done
    done

    [[ $SENDCOM="YES" ]] && cp ${output_base}/*.nc $COMOUTcmce/.
fi



if [ $modnam = ecme_apcp24h ] ; then

  export ihour
  export mb
  export modelpath=$COMOUTecme

  for ihour in 00 12 ; do
     export output_base=${WORK}/precip/ecme_apcp24h.${ihour}
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40  41 42 43 44 45 46 47 48 49 50  ; do
       if [ -s $COMOUTecme/ecme.ens${mb}.t${ihour}z.grid4_apcp.f024.grib1 ] ; then  
         export lead='24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360'
	 ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstECME_APCP24h.conf
       fi
     done
  done

     [[ $SENDCOM="YES" ]] && cp ${output_base}/*.nc $COMOUTecme/.
fi


if [ $modnam = nohrsc24h ] ; then
 
  for ihour in 00 12 ; do
    snowfall=$DCOMINnohrsc/${vday}/wgrbbul/nohrsc_snowfall/sfav2_CONUS_24h_${vday}${ihour}_grid184.grb2
    if [ -s $snowfall ] ; then
      [[ $SENDCOM="YES" ]] && cp $snowfall $COMOUTgefs/nohrsc.t${ihour}z.grid184.grb2
    else
        if [ $SENDMAIL = YES ]; then
          export subject="NOHRSC Data Missing for EVS ${COMPONENT}"
          echo "Warning:  No NOHRSC analysis available for ${INITDATE}${ihour}" > mailmsg
          echo Missing file is $snowfall  >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $maillist
	fi
    fi
  done

fi

if [ $modnam = gefs_snow24h ] ; then

  export output_base=${WORK}/snow/gefs_snow24h.${gens_ihour}

   export ihour
   export mb
   export model=gefs
   export modelpath=$COMOUTgefs
   export snow

  for ihour in $gens_ihour ; do

     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
       for snow in WEASD SNOD ; do 
	 if [  -s $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.f024.grib2 ] ; then
	   export lead='24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384'
	   ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_SNOW24h.conf
	 fi 
       done
    done  
    
  done

  [[ $SENDCOM="YES" ]] && cp $output_base/*.nc $COMOUTgefs/.
fi



if [ $modnam = cmce_snow24h ] ; then

  export output_base=${WORK}/snow/cmce_snow24h.${gens_ihour}
  export ihour
  export mb
  export model=cmce
  export modelpath=$COMOUTcmce
  export snow 
  for ihour in $gens_ihour ; do
     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do

       for snow in WEASD SNOD ; do
        if [  -s $COMOUTcmce/cmce.ens${mb}.t${ihour}z.grid3.f024.grib2 ] ; then  
         export lead='24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384'
         ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_SNOW24h.conf
        fi
       done
       
     done
  done

  [[ $SENDCOM="YES" ]] && cp $output_base/*.nc $COMOUTcmce/.
fi

if [ $modnam = ecme_snow24h ] ; then

    export ihour
    export mb
    export model=ecme
    export modelpath=$COMOUTecme

  for ihour in 00 12 ; do

     export output_base=${WORK}/snow/ecme_snow24h.${ihour}

     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 ; do
       if [  -s $COMOUTecme/ecme.ens${mb}.t${ihour}z.grid4_apcp.f024.grib1 ] ; then
    	  export lead='24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360 '
          ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstECME_SNOW24h.conf
       fi
     done
  done

  #[[ $SENDCOM="YES" ]] && cp $output_base/ecme*.nc $COMOUTecme
fi


if [ $modnam = gfs ] ; then

  for ihour in 00  ; do

    for  hhh in 024 048 072 096  120 144 168 192 216 240 264 288 312 336 360 384 ; do     
     gfs=$COMINgfs/gfs.$vday/${ihour}/atmos/gfs.t${ihour}z.pgrb2.1p00.f${hhh}
     $WGRIB2  $gfs|grep "HGT:500 mb"|$WGRIB2 -i $gfs -grib $COMOUTgefs/gfs.t${ihour}z.grid3.f${hhh}.grib2     
    done

  done

fi


if [ $modnam = osi_saf ] ; then
   
   osi=$DCOMINosi_saf/$INITDATE/seaice/osisaf/ice_conc_nh_polstere-100_multi_${INITDATE}1200.nc	
   if [ -s $osi ] ; then
     python ${USHevs}/global_ens/global_ens_sea_ice_prep.py
     [[ $SENDCOM="YES" ]] &&  cp $WORK/atmos.${INITDATE}/osi_saf/*.nc $COMOUTosi_saf/.
   else
	if [ $SENDMAIL = YES ]; then
          export subject="OSI_SAF Data Missing for EVS ${COMPONENT}"
          echo "Warning:  No OSI_SAF data  available for ${INITDATE}" > mailmsg
          echo Missing file is $osi  >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $maillist
	fi
    fi 
fi

# Ice concentration starts from f000. There is amount of ice at beginning.
# So, for f024 ice concentation, it shoule be  averaged of f000, f006, f012
# f018 and f024 
if [ $modnam = gefs_icec24h ] ; then

    export output_base=${WORK}/gefs_icec24h
    export model=gefs
    export modelpath=$COMOUTgefs

    export ihour
    export mb
    export accum=24

    for ihour in 00 ; do

     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
    	 export lead='24, 48, 72, 96, 120, 144, 168, 192, 216,  240,  264,  288,  312,  336,  360,  384' 

	 if [  -s $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.f024.grib2 ] ; then
    	     ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_ICEC.conf
	 fi 

      done
    done

    [[ $SENDCOM="YES" ]] && cp $output_base/gefs*icec*.nc $COMOUTgefs
fi

if [ $modnam = gefs_icec7day ] ; then

    export output_base=${WORK}/gefs_icec7day
    export model=gefs
    export modelpath=$COMOUTgefs 
		              
    export ihour
    export mb
    export accum=168	

    #for ihour in 00  12  ; do
    for ihour in 00  ; do

     for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
        if [ $ihour = 00 ] ; then
            export lead='168, 192, 216,  240,  264,  288,  312,  336,  360,  384'
        elif [ $ihour = 12 ] ; then 
            export lead='180, 204, 228, 252, 276, 300, 324, 348, 372 '
        fi
        ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_ICEC.conf
     done
   done
							     
   [[ $SENDCOM="YES" ]] && cp $output_base/gefs*icec*.nc $COMOUTgefs
fi

if [ $modnam = gefs_sst24h ] ; then

    export output_base=${WORK}/gefs_sst24h
    export model=gefs
    export modelpath=$COMOUTgefs

    export ihour
    export mb
    export accum=24

    for ihour in 00  12  ; do

       for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
         if [ $ihour = 00 ] ; then
           export lead='24, 48, 72, 96, 120, 144, 168, 192, 216,  240,  264,  288,  312,  336,  360,  384'
         elif [ $ihour = 12 ] ; then
           export lead='36, 60, 84, 108, 132, 156, 180, 204, 228, 252, 276, 300, 324, 348, 372 '
         fi
	 if [  -s $COMOUTgefs/gefs.ens${mb}.t${ihour}z.grid3.f024.grib2 ] ; then
           ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${CONF_PREP}/PcpCombine_fcstGEFS_SST24h.conf
	 fi 
       done

   done

     [[ $SENDCOM="YES" ]] && cp $output_base/gefs*sst*.nc $COMOUTgefs

fi

