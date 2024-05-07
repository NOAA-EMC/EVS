#!/bin/ksh
#*************************************************************************************************
# Purpose:  Run NAEFS  prep job
#             1. Retrieve bias-corrected GEFS and CMCE member files to form smaller grib2 files
#             2. For APCP24h, only retrive bias-corrected GEFS files 
#             3. Stored the smaller grib files in prep/global_ens/atmos.YYYYMMDD/gefs_bc, 
#                and prep/global_ens/atmos.YYYYMMDD/cmce_bc
#
# Last updated 11/15/2023: by  Binbin Zhou, Lynker@EMC/NCEP
#************************************************************************************************
set -x

modnam=$1
naefs_ihour=$2
fhr_beg=$3
fhr_end=$4

export vday=${INITDATE:-$PDYm2}    #for ensemble, use past-2 day as validation day
export vdate=${vdate:-$vday$ihour}

cd $WORK

###########################################
#Get GEFS 30 member grib2 file in grid3 
###########################################
if [ $modnam = gefs_bc ] ; then
  total=$gefs_mbrs
  for ihour in $naefs_ihour  ; do
      origin=$COMINgefs_bc/gefs.$vday/$ihour/pgrb2ap5_bc
      mbr=1
       while [ $mbr -le $total ] ; do
         mb=$mbr
         typeset -Z2 mb
         nfhrs=$fhr_beg
         while [ $nfhrs -le $fhr_end ] ; do
           hhh=$nfhrs
           typeset -Z3 hhh
           gefs_bc=$origin/gep${mb}.t${ihour}z.pgrb2a.0p50_bcf${hhh}
           if [ -s $gefs_bc ]; then
             >$WORK/gefs.upper.${ihour}.${mb}.${hhh}
	     for level in 250 850 ; do
                  $WGRIB2  $gefs_bc|grep "UGRD:$level mb"|$WGRIB2 -i $gefs_bc -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
	          cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}
	          $WGRIB2  $gefs_bc|grep "VGRD:$level mb"|$WGRIB2 -i $gefs_bc -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
	          cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}
             done	
             $WGRIB2  $gefs_bc|grep "HGT:500 mb"|$WGRIB2 -i $gefs_bc -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
             cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}
	     $WGRIB2  $gefs_bc|grep "HGT:1000 mb"|$WGRIB2 -i $gefs_bc -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
	     cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}
             $WGRIB2  $gefs_bc|grep "TMP:850 mb"|$WGRIB2 -i $gefs_bc -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
             cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}
	     $WGRIB2  $gefs_bc|grep "TMP:2 m "|$WGRIB2 -i $gefs_bc -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
	     cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}
             $WGRIB2  $gefs_bc|grep "UGRD:10 m "|$WGRIB2 -i $gefs_bc -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
             cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}
             $WGRIB2  $gefs_bc|grep "VGRD:10 m "|$WGRIB2 -i $gefs_bc -grib $WORK/grabgefs.${ihour}.${mb}.${hhh}
             cat $WORK/grabgefs.${ihour}.${mb}.${hhh} >> $WORK/gefs.upper.${ihour}.${mb}.${hhh}
             $WGRIB2 $WORK/gefs.upper.${ihour}.${mb}.${hhh} -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003  $WORK/gefs_bc.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2
             if [ $SENDCOM="YES" ] ; then
                 if [ -s $WORK/gefs_bc.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2 ]; then 
                     cp -v $WORK/gefs_bc.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2 $COMOUTgefs_bc/gefs_bc.ens${mb}.t${ihour}z.grid3.f${hhh}.grib2
                 fi
             fi
          else
            echo "WARNING: $gefs_bc is not available"
            if [ $SENDMAIL = YES ]; then
              export subject="GEFS BC member ${mb} F${hhh} Data Missing for EVS ${COMPONENT}"
              echo "Warning: No GEFS BC member ${mb} F${hhh} available for ${vday}${ihour}" > mailmsg
              echo "Missing file is $gefs_bc" >> mailmsg
              echo "Job ID: $jobid" >> mailmsg
              cat mailmsg | mail -s "$subject" $MAILTO
            fi
          fi  
          nfhrs=`expr $nfhrs + 12`
         done
         mbr=`expr $mbr + 1`
      done
     done   #for ihour
fi

###########################################
#Get CMCE 20 member grib2 file in grid3 
###########################################
if [ $modnam = cmce_bc ] ; then
  total=20
  for ihour in $naefs_ihour ; do
     origin=$DCOMINcmce_bc/${vday}/wgrbbul/cmcensbc_gb2
     mbr=1
     while [ $mbr -le $total ] ; do
       mb=$mbr
       typeset -Z2 mb
       nfhrs=$fhr_beg
       while [ $nfhrs -le $fhr_end ] ; do
           h3=$nfhrs           
           typeset -Z3 h3
             cmce_bc=$origin/${vday}${ihour}_CMC_naefsbc_hr_latlon0p5x0p5_P${h3}_0${mb}.grib2
             if [ -s $cmce_bc ]; then
               >$WORK/cmce.upper.${ihour}.${mb}.${h3}
               for level in 250 850 ; do
  		$WGRIB2  $cmce_bc|grep "UGRD:$level mb"|$WGRIB2 -i $cmce_bc -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
		cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}
                $WGRIB2  $cmce_bc|grep "VGRD:$level mb"|$WGRIB2 -i $cmce_bc -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
                cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}
	       done
               $WGRIB2  $cmce_bc|grep "HGT:500 mb"|$WGRIB2 -i $cmce_bc -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
               cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}
               $WGRIB2  $cmce_bc|grep "HGT:1000 mb"|$WGRIB2 -i $cmce_bc -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
	       cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}
               $WGRIB2  $cmce_bc|grep "TMP:850 mb"|$WGRIB2 -i $cmce_bc -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
               cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}
	       $WGRIB2  $cmce_bc|grep "TMP:2 m "|$WGRIB2 -i $cmce_bc -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
	       cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}
               $WGRIB2  $cmce_bc|grep "UGRD:10 m "|$WGRIB2 -i $cmce_bc -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
               cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}
               $WGRIB2  $cmce_bc|grep "VGRD:10 m "|$WGRIB2 -i $cmce_bc -grib $WORK/grabcmce.${ihour}.${mb}.${h3}
               cat $WORK/grabcmce.${ihour}.${mb}.${h3} >> $WORK/cmce.upper.${ihour}.${mb}.${h3}
	       #*****************************************************************************
               #use WGRIB2 to reverse N-S grid direction and convert 0.5x0.5 deg to 1x1 deg
	       #*****************************************************************************
	       $WGRIB2 $WORK/cmce.upper.${ihour}.${mb}.${h3} -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003  $WORK/cmce_bc.ens${mb}.t${ihour}z.grid3.f${h3}.grib2
               if [ $SENDCOM="YES" ] ; then
                   if [ -s $WORK/cmce_bc.ens${mb}.t${ihour}z.grid3.f${h3}.grib2 ]; then
                       cp -v $WORK/cmce_bc.ens${mb}.t${ihour}z.grid3.f${h3}.grib2 $COMOUTcmce_bc/cmce_bc.ens${mb}.t${ihour}z.grid3.f${h3}.grib2
                   fi
               fi
               rm -f  $WORK/cmce.upper.${ihour}.${mb}.${h3}
             else
               echo "WARNING: $cmce_bc is not available"
               if [ $SENDMAIL = YES ]; then
                 export subject="CMCE BC member ${mb} F${h3} Data Missing for EVS ${COMPONENT}"
                 echo "Warning: No CMCE BC member ${mb} F${h3} available for ${vday}${ihour}" > mailmsg
                 echo "Missing file is $cmce_bc" >> mailmsg
                 echo "Job ID: $jobid" >> mailmsg
                cat mailmsg | mail -s "$subject" $MAILTO
               fi
               echo "WARNING: $cmce_bc does not exist"
             fi
           nfhrs=`expr $nfhrs + 12`
       done
       mbr=`expr $mbr + 1` 
     done
  done # for ihour
fi

###########################################
#Get GEFS 30 member for APCP 24 hour accumulation
###########################################
if [ $modnam = gefs_bc_apcp24h ] ; then
    if [ $gefs_mbrs = 20 ] ; then
      mbrs='1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20'
    elif [ $gefs_mbrs = 30 ] ; then
      mbrs='1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30'
    else
      err_exit "mbrs is not defined"
    fi
    for ihour in $naefs_ihour ; do
       origin=$COMINgefs_bc/gefs.$vday/$ihour/prcp_bc_gb2
       for  hhh in  024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384 ; do
	>$WORK/grabmbr.${ihour}.${hhh}
        for mbr in $mbrs ; do
          mb=$mbr
          typeset -Z2 mb
	  apcp24_bc=$origin/geprcp.t${ihour}z.pgrb2a.0p50.bc_24hf${hhh}
          if [ -s $apcp24_bc ]; then
            $WGRIB2 $apcp24_bc|grep -w "ENS=+${mbr}"|$WGRIB2 -i $apcp24_bc -grib $WORK/grabmbr.${ihour}.${hhh}
            $WGRIB2 $WORK/grabmbr.${ihour}.${hhh} -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003  $WORK/gefs_bc.ens${mb}.t${ihour}z.grid3.24h.f${hhh}.grib2
            if [ $SENDCOM="YES" ] ; then
                if [ -s $WORK/gefs_bc.ens${mb}.t${ihour}z.grid3.24h.f${hhh}.grib2 ]; then
                    cp -v $WORK/gefs_bc.ens${mb}.t${ihour}z.grid3.24h.f${hhh}.grib2 $COMOUTgefs_bc/gefs_bc.ens${mb}.t${ihour}z.grid3.24h.f${hhh}.grib2
                fi
            fi
          else
            echo "WARNING: $apcp24_bc is not available" 
            if [ $SENDMAIL = YES ]; then
              export subject="GEFS BC member ${mb} F${hhh} Data Missing for EVS ${COMPONENT}"
              echo "Warning: No GEFS BC member ${mb} F${hhh} available for ${vday}${ihour}" > mailmsg
              echo "Missing file is $apcp24_bc" >> mailmsg
              echo "Job ID: $jobid" >> mailmsg
              cat mailmsg | mail -s "$subject" $MAILTO
            fi
          fi
        done
      done
    done
fi
