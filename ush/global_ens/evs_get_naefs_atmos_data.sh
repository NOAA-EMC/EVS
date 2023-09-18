#!/bin/ksh
set -x

modnam=$1
naefs_cyc=$2
fhr_beg=$3
fhr_end=$4


export vday=${INITDATE:-$PDYm2}    #for ensemble, use past-2 day as validation day
export vdate=${vdate:-$vday$cyc}

export cnvgrib=$CNVGRIB
export wgrib2=$WGRIB2
export ndate=$NDATE




if [ $modnam = gefs_bc ] ; then

  cd $WORK
  total=30

   export outdata=$COMOUT_gefs_bc

   if [ ! -s $outdata/gefs.ens30.t12z.grid3.f384.grib2 ] ; then

    #for cyc in 00 06 12 18 ; do
    for cyc in $naefs_cyc  ; do
  
      origin=$COMINgefs_bc/gefs.$vday/$cyc/pgrb2ap5_bc

      mbr=1
       while [ $mbr -le $total ] ; do
         mb=$mbr
         typeset -Z2 mb

         nfhrs=$fhr_beg

         while [ $nfhrs -le $fhr_end ] ; do

           hhh=$nfhrs
           typeset -Z3 hhh

             gefs_bc=$origin/gep${mb}.t${cyc}z.pgrb2a.0p50_bcf${hhh}

             >$WORK/gefs.upper.${cyc}.${mb}.${hhh}

	     for level in 250 850 ; do
                  $WGRIB2  $gefs_bc|grep "UGRD:$level mb"|$WGRIB2 -i $gefs_bc -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
	          cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.upper.${cyc}.${mb}.${hhh}

	          $WGRIB2  $gefs_bc|grep "VGRD:$level mb"|$WGRIB2 -i $gefs_bc -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
	          cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.upper.${cyc}.${mb}.${hhh}
             done	

             $WGRIB2  $gefs_bc|grep "HGT:500 mb"|$WGRIB2 -i $gefs_bc -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
             cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.upper.${cyc}.${mb}.${hhh}
	     $WGRIB2  $gefs_bc|grep "HGT:1000 mb"|$WGRIB2 -i $gefs_bc -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
	     cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.upper.${cyc}.${mb}.${hhh}

             $WGRIB2  $gefs_bc|grep "TMP:850 mb"|$WGRIB2 -i $gefs_bc -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
             cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.upper.${cyc}.${mb}.${hhh}

	     $WGRIB2  $gefs_bc|grep "TMP:2 m "|$WGRIB2 -i $gefs_bc -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
	     cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.upper.${cyc}.${mb}.${hhh}

             $WGRIB2  $gefs_bc|grep "UGRD:10 m "|$WGRIB2 -i $gefs_bc -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
             cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.upper.${cyc}.${mb}.${hhh}

             $WGRIB2  $gefs_bc|grep "VGRD:10 m "|$WGRIB2 -i $gefs_bc -grib $WORK/grabgefs.${cyc}.${mb}.${hhh}
             cat $WORK/grabgefs.${cyc}.${mb}.${hhh} >> $WORK/gefs.upper.${cyc}.${mb}.${hhh}

            $wgrib2 $WORK/gefs.upper.${cyc}.${mb}.${hhh} -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003  $outdata/gefs_bc.ens${mb}.t${cyc}z.grid3.f${hhh}.grib2

            nfhrs=`expr $nfhrs + 12`
         done

         mbr=`expr $mbr + 1`
      done

     done   #for cyc

   fi # check if file not existing 

fi





###########################################
#8:Get CMCE 20 member grib2 file in grid3 
###########################################
if [ $modnam = cmce_bc ] ; then

  cd $WORK

  total=20

   export outdata=$COMOUT_cmce_bc

     for cyc in $naefs_cyc ; do

       origin=$COMINcmce_bc/${vday}/wgrbbul/cmcensbc_gb2

       mbr=1
       while [ $mbr -le $total ] ; do
         mb=$mbr
         typeset -Z2 mb

         nfhrs=$fhr_beg
         while [ $nfhrs -le $fhr_end ] ; do

           #hh=$nfhrs
           h3=$nfhrs           

           typeset -Z3 h3

             cmce_bc=$origin/${vday}${cyc}_CMC_naefsbc_hr_latlon0p5x0p5_P${h3}_0${mb}.grib2

             >$WORK/cmce.upper.${cyc}.${mb}.${h3}
             
	     for level in 250 850 ; do
		$WGRIB2  $cmce_bc|grep "UGRD:$level mb"|$WGRIB2 -i $cmce_bc -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
		cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.upper.${cyc}.${mb}.${h3}

                $WGRIB2  $cmce_bc|grep "VGRD:$level mb"|$WGRIB2 -i $cmce_bc -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
              cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.upper.${cyc}.${mb}.${h3}
	     done

             $WGRIB2  $cmce_bc|grep "HGT:500 mb"|$WGRIB2 -i $cmce_bc -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
             cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.upper.${cyc}.${mb}.${h3}
             $WGRIB2  $cmce_bc|grep "HGT:1000 mb"|$WGRIB2 -i $cmce_bc -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
	     cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.upper.${cyc}.${mb}.${h3}

             $WGRIB2  $cmce_bc|grep "TMP:850 mb"|$WGRIB2 -i $cmce_bc -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
             cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.upper.${cyc}.${mb}.${h3}

	     $WGRIB2  $cmce_bc|grep "TMP:2 m "|$WGRIB2 -i $cmce_bc -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
	     cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.upper.${cyc}.${mb}.${h3}

             $WGRIB2  $cmce_bc|grep "UGRD:10 m "|$WGRIB2 -i $cmce_bc -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
             cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.upper.${cyc}.${mb}.${h3}

             $WGRIB2  $cmce_bc|grep "VGRD:10 m "|$WGRIB2 -i $cmce_bc -grib $WORK/grabcmce.${cyc}.${mb}.${h3}
             cat $WORK/grabcmce.${cyc}.${mb}.${h3} >> $WORK/cmce.upper.${cyc}.${mb}.${h3}

             #use wgrib2 to reverse N-S grid direction and convert 0.5x0.5 deg to 1x1 deg

	     $wgrib2 $WORK/cmce.upper.${cyc}.${mb}.${h3} -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003  $outdata/cmce_bc.ens${mb}.t${cyc}z.grid3.f${h3}.grib2

             rm -f  $WORK/cmce.upper.${cyc}.${mb}.${h3}  

           nfhrs=`expr $nfhrs + 12`

         done

         mbr=`expr $mbr + 1` 

       done

    done # for cyc

fi



if [ $modnam = gefs_bc_apcp24h ] ; then

    cd $WORK

    export outdata=$COMOUT_gefs_bc

    for cyc in $naefs_cyc ; do

       origin=$COMINgefs_bc/gefs.$vday/$cyc/prcp_bc_gb2


       for  hhh in  024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384 ; do

        #apcp24_bc=$origin/geprcp.t${cyc}z.pgrb2a.0p50.bc_24hf${hhh}

	>$WORK/grabmbr.${cyc}.${hhh}
        for mbr in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30; do

          mb=$mbr
          typeset -Z2 mb

	     apcp24_bc=$origin/geprcp.t${cyc}z.pgrb2a.0p50.bc_24hf${hhh}

          $wgrib2 $apcp24_bc|grep "ENS=+${mbr}"|$WGRIB2 -i $apcp24_bc -grib $WORK/grabmbr.${cyc}.${hhh}
                   
          $wgrib2 $WORK/grabmbr.${cyc}.${hhh} -set_grib_type same -new_grid_winds earth -new_grid ncep grid 003  $outdata/gefs_bc.ens${mb}.t${cyc}z.grid3.24h.f${hhh}.grib2

        done

      done

    done

fi



