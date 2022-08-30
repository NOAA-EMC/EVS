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
           ${COMINsref}/sref.${fday}/$fcyc/pgrb/sref_${base}.t${fcyc}z.pgrb212.${mb}.f${fhr_3}.grib2 \
           'name="APCP"; level="A03";' \
           ${COMINsref}/sref.${fday}/$fcyc/pgrb/sref_${base}.t${fcyc}z.pgrb212.${mb}.f${fhr}.grib2 \
           'name="APCP"; level="A03";' \
           sref_${base}.t${fcyc}z.${mb}.pgrb212.6hr.f${fhr}.nc
           mv sref_${base}.t${fcyc}z.${mb}.pgrb212.6hr.f${fhr}.nc $WORK/sref.${fday}/. 
       done
     done 
   done
  done

fi


if [ $modnam = ccpa ] ; then

  #ccpa hrap is in G240	
  ccpa06=${WORK}/ccpa.${vday}/ccpa06
  ccpa06_G240=${WORK}/ccpa.${vday}/ccpa06_G240
  mkdir -p $ccpa06
  mkdir -p $ccpa06_G240
  cd ${WORK}/ccpa.${vday}

  for cyc in 00 06 12 18 ; do
    $copygb2 -g"30 6 0 0 0 0 0 0 185 129 12190000 226541000 8 25000000 265000000 40635000 40635000 0 64 25000000 25000000 0 0" -i3 -x $COMINccpa/ccpa.${vday}/$cyc/ccpa.t${cyc}z.03h.hrap.conus.gb2 ${WORK}/ccpa.${vday}/ccpa.t${cyc}z.grid212.f00.grib2
    cp $COMINccpa/ccpa.${vday}/$cyc/ccpa.t${cyc}z.03h.hrap.conus.gb2 ${WORK}/ccpa.${vday}/ccpa.t${cyc}z.grid240.f00.grib2
  done
   
   
  typeset -Z2 cyc3
  for cyc in 03 09 15 ; do
    cyc3=$((cyc+3))
    $copygb2 -g"30 6 0 0 0 0 0 0 185 129 12190000 226541000 8 25000000 265000000 40635000 40635000 0 64 25000000 25000000 0 0" -i3 -x $COMINccpa/ccpa.${vday}/$cyc3/ccpa.t${cyc}z.03h.hrap.conus.gb2 ${WORK}/ccpa.${vday}/ccpa.t${cyc}z.grid212.f00.grib2
    cp $COMINccpa/ccpa.${vday}/$cyc3/ccpa.t${cyc}z.03h.hrap.conus.gb2 ${WORK}/ccpa.${vday}/ccpa.t${cyc}z.grid240.f00.grib2
  done

     DAY1=`$NDATE +24 ${vday}12`
     next=`echo ${DAY1} | cut -c 1-8`
   for cyc in 21 ; do
     $copygb2 -g"30 6 0 0 0 0 0 0 185 129 12190000 226541000 8 25000000 265000000 40635000 40635000 0 64 25000000 25000000 0 0" -i3 -x  $COMINccpa/ccpa.${next}/00/ccpa.t${cyc}z.03h.hrap.conus.gb2 ${WORK}/ccpa.${vday}/ccpa.t${cyc}z.grid212.f00.grib2
     cp $COMINccpa/ccpa.${next}/00/ccpa.t${cyc}z.03h.hrap.conus.gb2 ${WORK}/ccpa.${vday}/ccpa.t${cyc}z.grid240.f00.grib2
   done

   typeset -Z2 cyc_3
   for cyc in 03 09 15 21 ; do
    cyc_3=$((cyc-3))
    ln -sf  ${WORK}/ccpa.${vday}/ccpa.t${cyc_3}z.grid212.f00.grib2 $ccpa06/ccpa1
    ln -sf  ${WORK}/ccpa.${vday}/ccpa.t${cyc}z.grid212.f00.grib2 $ccpa06/ccpa2
    pcp_combine -sum 00000000_000000 3 ${vday}_${cyc} 6 ccpa.t${cyc}z.grid212.6hr.nc  -pcpdir  $ccpa06 -v 3

    ln -sf  ${WORK}/ccpa.${vday}/ccpa.t${cyc_3}z.grid240.f00.grib2 $ccpa06/ccpa1
    ln -sf  ${WORK}/ccpa.${vday}/ccpa.t${cyc}z.grid240.f00.grib2 $ccpa06/ccpa2
    pcp_combine -sum 00000000_000000 3 ${vday}_${cyc} 6 ccpa.t${cyc}z.grid240.6hr.nc  -pcpdir  $ccpa06 -v 3

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
