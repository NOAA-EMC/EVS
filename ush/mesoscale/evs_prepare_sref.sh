set -x

modnam=$1

export copygb2=${copygb2:-$COPYGB2}
export cnvgrib=${cnvgrib:-$CNVGRIB}
export wgrib2=${wgrib2:-$WGRIB2}
export ndate=${ndate:-$NDATE}

export vday=$VDATE

if [ $modnam = sref_apcp06 ] ; then

  for vcyc in 03 09 15 21  ; do
    for fhr in  06 12 18 24 30 36 42 48 54 60 66 72 78 84 ; do

      obsv_cyc=${vday}${vcyc}     #validation time: xxxx.tvcycz.f00
      fcst_time=`$ndate -$fhr $obsv_cyc`
      fday=${fcst_time:0:8}
      fcyc=${fcst_time:8:2}
      apcp06=$WORK/sref.${fday}
      mkdir -p $apcp06
      typeset -Z2 fhr_3
      fhr_3=$((fhr-3)) 

      for base in arw nmb ; do
        for mb in ctl n1 n2 n3 n4 n5 n6 p1 p2 p3 p4 p5 p6 ; do
         pcp_combine -add \
           ${COMSREF}/sref.${fday}/$fcyc/pgrb/sref_${base}.t${fcyc}z.pgrb212.${mb}.f${fhr_3}.grib2 \
           'name="APCP"; level="A03";' \
           ${COMSREF}/sref.${fday}/$fcyc/pgrb/sref_${base}.t${fcyc}z.pgrb212.${mb}.f${fhr}.grib2 \
           'name="APCP"; level="A03";' \
           sref_${base}.t${fcyc}z.${mb}.pgrb212.6hr.f${fhr}.nc
           mv sref_${base}.t${fcyc}z.${mb}.pgrb212.6hr.f${fhr}.nc $WORK/sref.${fday}/. 
       done
     done 
   done
  done

fi


if [ $modnam = ccpa ] ; then

  ccpa06=${WORK}/ccpa.${vday}/ccpa06
  mkdir -p $ccpa06
  cd ${WORK}/ccpa.${vday}

  for cyc in 00 06 12 18 ; do
    $copygb2 -g"30 6 0 0 0 0 0 0 185 129 12190000 226541000 8 25000000 265000000 40635000 40635000 0 64 25000000 25000000 0 0" -i3 -x $COMCCPA/ccpa.${vday}/$cyc/ccpa.t${cyc}z.03h.hrap.conus.gb2 ${WORK}/ccpa.${vday}/ccpa.t${cyc}z.grid212.f00.grib2
  done

  typeset -Z2 cyc3
  for cyc in 03 09 15 ; do
    cyc3=$((cyc+3))
    $copygb2 -g"30 6 0 0 0 0 0 0 185 129 12190000 226541000 8 25000000 265000000 40635000 40635000 0 64 25000000 25000000 0 0" -i3 -x $COMCCPA/ccpa.${vday}/$cyc3/ccpa.t${cyc}z.03h.hrap.conus.gb2 ${WORK}/ccpa.${vday}/ccpa.t${cyc}z.grid212.f00.grib2
  done

     DAY1=`$NDATE +24 ${vday}12`
     next=`echo ${DAY1} | cut -c 1-8`
   for cyc in 21 ; do
     $copygb2 -g"30 6 0 0 0 0 0 0 185 129 12190000 226541000 8 25000000 265000000 40635000 40635000 0 64 25000000 25000000 0 0" -i3 -x  $COMCCPA/ccpa.${next}/00/ccpa.t${cyc}z.03h.hrap.conus.gb2 ${WORK}/ccpa.${vday}/ccpa.t${cyc}z.grid212.f00.grib2
   done

   typeset -Z2 cyc_3
   typeset -Z2 cyc_6
   for cyc in 03 09 15 21 ; do
    cyc_3=$((cyc-3))
    cyc_6=$((cyc-6))
    ln -sf  ${WORK}/ccpa.${vday}/ccpa.t${cyc_3}z.grid212.f00.grib2 $ccpa06/ccpa1
    ln -sf  ${WORK}/ccpa.${vday}/ccpa.t${cyc}z.grid212.f00.grib2 $ccpa06/ccpa2
    pcp_combine -sum 00000000_000000 3 ${vday}_${cyc} 6 ccpa.t${cyc}z.grid212.6hr.nc  -pcpdir  $ccpa06 -v 3
    #mv ccpa.t${cyc}z.grid212.f00.nc ${WORK}/ccpa.${vday} 
   done

fi



if  [ $modnam = ndas ] ; then

 mkdir -p $WORK/ndas.$vday

 DAY1=`$ndate +24 ${vday}09`
 tom=`echo ${DAY1} | cut -c 1-8`

   ln -sf $COMNDAS/nam.$vday/nam.t06z.awip3d00.tm03.grib2 $WORK/ndas.$vday/ndas.t03z.awip3d00.f00.grib2
   ln -sf $COMNDAS/nam.$vday/nam.t12z.awip3d00.tm03.grib2 $WORK/ndas.$vday/ndas.t09z.awip3d00.f00.grib2
   ln -sf $COMNDAS/nam.$vday/nam.t18z.awip3d00.tm03.grib2 $WORK/ndas.$vday/ndas.t15z.awip3d00.f00.grib2
   ln -sf  $COMNDAS/nam.$tom/nam.t00z.awip3d00.tm03.grib2 $WORK/ndas.$vday/ndas.t21z.awip3d00.f00.grib2

    for cyc in 03 09 15 21 ; do

      >$WORK/ndas.$vday/ndas.${cyc}
      ndas=$WORK/ndas.$vday/ndas.t${cyc}z.awip3d00.f00.grib2
      $wgrib2 $ndas|grep  "HGT:500 mb"|$wgrib2 -i $ndas -grib $WORK/ndas.$vday/z500.${cyc}
      cat $WORK/ndas.$vday/z500.${cyc} >> $WORK/ndas.$vday/ndas.${cyc}
      $wgrib2 $ndas|grep  "HGT:700 mb"|$wgrib2 -i $ndas -grib $WORK/ndas.$vday/z700.${cyc}
      cat $WORK/ndas.$vday/z700.${cyc} >> $WORK/ndas.$vday/ndas.${cyc}


      $wgrib2 $ndas|grep  "TMP:850 mb"|$wgrib2 -i $ndas -grib $WORK/ndas.$vday/t850.${cyc}
      cat $WORK/ndas.$vday/t850.${cyc} >> $WORK/ndas.$vday/ndas.${cyc}
      $wgrib2 $ndas|grep  "TMP:500 mb"|$wgrib2 -i $ndas -grib $WORK/ndas.$vday/t500.${cyc}
      cat $WORK/ndas.$vday/t500.${cyc} >> $WORK/ndas.$vday/ndas.${cyc}


      $wgrib2 $ndas|grep  "UGRD:850 mb"|$wgrib2 -i $ndas -grib $WORK/ndas.$vday/u850.${cyc}
      cat $WORK/ndas.$vday/u850.${cyc} >> $WORK/ndas.$vday/ndas.${cyc}
      $wgrib2 $ndas|grep  "VGRD:850 mb"|$wgrib2 -i $ndas -grib $WORK/ndas.$vday/v850.${cyc}
      cat $WORK/ndas.$vday/v850.${cyc} >> $WORK/ndas.$vday/ndas.${cyc}
      $wgrib2 $ndas|grep  "UGRD:500 mb"|$wgrib2 -i $ndas -grib $WORK/ndas.$vday/u500.${cyc}
      cat $WORK/ndas.$vday/u500.${cyc} >> $WORK/ndas.$vday/ndas.${cyc}
      $wgrib2 $ndas|grep  "VGRD:500 mb"|$wgrib2 -i $ndas -grib $WORK/ndas.$vday/v500.${cyc}
      cat $WORK/ndas.$vday/v500.${cyc} >> $WORK/ndas.$vday/ndas.${cyc}
      $wgrib2 $ndas|grep  "UGRD:500 mb"|$wgrib2 -i $ndas -grib $WORK/ndas.$vday/u250.${cyc}
      cat $WORK/ndas.$vday/u250.${cyc} >> $WORK/ndas.$vday/ndas.${cyc}
      $wgrib2 $ndas|grep  "VGRD:250 mb"|$wgrib2 -i $ndas -grib $WORK/ndas.$vday/v250.${cyc}
      cat $WORK/ndas.$vday/v250.${cyc} >> $WORK/ndas.$vday/ndas.${cyc}



      $copygb2 -g"30 6 0 0 0 0 0 0 185 129 12190000 226541000 8 25000000 265000000 40635000 40635000 0 64 25000000 25000000 0 0" -i2,1 -x $WORK/ndas.$vday/ndas.${cyc}  $WORK/ndas.${vday}/ndas.t${cyc}z.grid212.f00.grib2
    done

fi


if [ $modnam = prepbufr ] ; then

 mkdir -p $WORK/prepbufr.$vday

export output_base=${WORK}/pb2nc

 for cyc in 00  06  12  18  ; do

     export vbeg=${cyc}
     export vend=${cyc}

     ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsGFS_Prepbufr.cong
     cp ${WORK}/pb2nc/prepbufr_nc/*.nc $WORK/prepbufr.${vday} 

  done

fi 

exit
