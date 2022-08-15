#!/bin/ksh
#############################################################################
# Author: Binbin Zhou /IMSG
#         Dec 15, 2021
#############################################################################
set -x

data=$1

export vday=$VDATE

nextday=`$NDATE +24 ${vday}09 |cut -c1-8`
prevday=`$NDATE -24 ${vday}09 |cut -c1-8`

#NOTE: COPYGB2 is using option -i3 (budget)   
 
if [ $data = ccpa01h03h ] ; then

ccpadir=$WORK/ccpa.$vday

mkdir -p $ccpadir

     for cyc in 00 ; do
       ccpa01h=$COMCCPA/ccpa.${vday}/00/ccpa.t${cyc}z.01h.hrap.conus.gb2
       $COPYGB2 -g"30 6 0 0 0 0 0 0 1473 1025 12190000 226541000 8 25000000 265000000 5079000 5079000 0 64 25000000 25000000 0 0" -i3,1 -x $ccpa01h  $ccpadir/ccpa01h.t${cyc}z.G227.grib2
       ccpa03h=$COMCCPA/ccpa.${vday}/00/ccpa.t${cyc}z.03h.hrap.conus.gb2
       $COPYGB2 -g"30 6 0 0 0 0 0 0 1473 1025 12190000 226541000 8 25000000 265000000 5079000 5079000 0 64 25000000 25000000 0 0" -i3,1 -x $ccpa03h  $ccpadir/ccpa03h.t${cyc}z.G227.grib2
     done

     for cyc in 01 02 03 04 05 06  ; do
       ccpa01h=$COMCCPA/ccpa.${vday}/06/ccpa.t${cyc}z.01h.hrap.conus.gb2
       $COPYGB2 -g"30 6 0 0 0 0 0 0 1473 1025 12190000 226541000 8 25000000 265000000 5079000 5079000 0 64 25000000 25000000 0 0" -i3,1 -x $ccpa01h  $ccpadir/ccpa01h.t${cyc}z.G227.grib2
     done

     for cyc in 07 08 09 10 11 12  ; do
       ccpa01h=$COMCCPA/ccpa.${vday}/12/ccpa.t${cyc}z.01h.hrap.conus.gb2
       $COPYGB2 -g"30 6 0 0 0 0 0 0 1473 1025 12190000 226541000 8 25000000 265000000 5079000 5079000 0 64 25000000 25000000 0 0" -i3,1 -x $ccpa01h  $ccpadir/ccpa01h.t${cyc}z.G227.grib2
     done

     for cyc in 13 14 15 16 17 18  ; do
       ccpa01h=$COMCCPA/ccpa.${vday}/18/ccpa.t${cyc}z.01h.hrap.conus.gb2
       $COPYGB2 -g"30 6 0 0 0 0 0 0 1473 1025 12190000 226541000 8 25000000 265000000 5079000 5079000 0 64 25000000 25000000 0 0" -i3,1 -x $ccpa01h  $ccpadir/ccpa01h.t${cyc}z.G227.grib2
     done

     for cyc in 19 20 21 22 23  ; do
       ccpa01h=$COMCCPA/ccpa.${nextday}/00/ccpa.t${cyc}z.01h.hrap.conus.gb2
       $COPYGB2 -g"30 6 0 0 0 0 0 0 1473 1025 12190000 226541000 8 25000000 265000000 5079000 5079000 0 64 25000000 25000000 0 0" -i3,1 -x $ccpa01h  $ccpadir/ccpa01h.t${cyc}z.G227.grib2
     done

 
     for cyc in  03 06 ; do 
       ccpa03h=$COMCCPA/ccpa.${vday}/06/ccpa.t${cyc}z.03h.hrap.conus.gb2
       $COPYGB2 -g"30 6 0 0 0 0 0 0 1473 1025 12190000 226541000 8 25000000 265000000 5079000 5079000 0 64 25000000 25000000 0 0" -i3,1 -x $ccpa03h  $ccpadir/ccpa03h.t${cyc}z.G227.grib2
     done
 
     for cyc in 09 12 ; do
       ccpa03h=$COMCCPA/ccpa.${vday}/12/ccpa.t${cyc}z.03h.hrap.conus.gb2
       $COPYGB2 -g"30 6 0 0 0 0 0 0 1473 1025 12190000 226541000 8 25000000 265000000 5079000 5079000 0 64 25000000 25000000 0 0" -i3,1 -x $ccpa03h  $ccpadir/ccpa03h.t${cyc}z.G227.grib2
     done 

     for cyc in 15 18 ; do
       ccpa03h=$COMCCPA/ccpa.${vday}/18/ccpa.t${cyc}z.03h.hrap.conus.gb2
       $COPYGB2 -g"30 6 0 0 0 0 0 0 1473 1025 12190000 226541000 8 25000000 265000000 5079000 5079000 0 64 25000000 25000000 0 0" -i3,1 -x $ccpa03h  $ccpadir/ccpa03h.t${cyc}z.G227.grib2
     done

     for cyc in 21 ; do
       ccpa03h=$COMCCPA/ccpa.${nextday}/00/ccpa.t${cyc}z.03h.hrap.conus.gb2
       $COPYGB2 -g"30 6 0 0 0 0 0 0 1473 1025 12190000 226541000 8 25000000 265000000 5079000 5079000 0 64 25000000 25000000 0 0" -i3,1 -x $ccpa03h  $ccpadir/ccpa03h.t${cyc}z.G227.grib2
     done

fi

if [ $data = ccpa24h ] ; then

ccpadir=$WORK/ccpa.$vday
mkdir -p $ccpadir

 cycles="12"
 for cyc in $cycles ; do
  ccpa1=${COMCCPA}/ccpa.${vday}/12/ccpa.t12z.06h.hrap.conus.gb2
  ccpa2=${COMCCPA}/ccpa.${vday}/06/ccpa.t06z.06h.hrap.conus.gb2
  ccpa3=${COMCCPA}/ccpa.${vday}/00/ccpa.t00z.06h.hrap.conus.gb2
  ccpa4=${COMCCPA}/ccpa.${prevday}/18/ccpa.t18z.06h.hrap.conus.gb2

  mkdir -p $ccpadir/ccpa24
  cp $ccpa1 $ccpadir/ccpa24/.
  cp $ccpa2 $ccpadir/ccpa24/.
  cp $ccpa3 $ccpadir/ccpa24/.
  cp $ccpa4 $ccpadir/ccpa24/.

  pcp_combine ${prevday}_120000 06 ${vday}_120000 24  ccpa24.t12z.hrap.conus.nc -pcpdir $ccpadir/ccpa24

  regrid_data_plane ccpa24.t12z.hrap.conus.nc G227 ccpa24h.t12z.G227.nc -field 'name="APCP_24"; level="(*,*)";'

  mv ccpa24h.t12z.G227.nc  $ccpadir

 done

fi



# Note: HREF product mean/pmmn, etc only have 1hr, 3hr APCP, but no 24APCP, so need derive their 24hr APCP
#  While product prob files have 1hr, 3hr and 24APCP probability fields, so no need to derive 
#
if [ $data = apcp24h ] ; then

typeset -Z2 fcyc
cyc=12
obsv_cyc=${vday}${cyc}

for fhr in 24 30 36 42 48 ; do
 fcst_time=`$NDATE -$fhr $obsv_cyc`
 fyyyymmdd=${fcst_time:0:8}
 fcyc=${fcst_time:8:2}
 if [ $fhr = 24 ] ; then
  hhs=" 03 06 09 12 15 18 21 24"
  init="12"
 elif [ $fhr = 30 ] ; then
  hhs=" 09 12 15 18 21 24 27 30"
  init="06"
 elif [ $fhr = 36 ] ; then
  hhs=" 15 18 21 24 27 30 33 36"
  init="00"
 elif [ $fhr = 42 ] ; then
  hhs=" 21 24 27 30 33 36 39 42"
  init="18"
 elif [ $fhr = 48 ] ; then
  hhs=" 27 30 33 36 39 42 45 48"
  init="12"
 else
  exit
 fi

  href=$WORK/href.${fyyyymmdd}/apcp24_mean
  mkdir -p $href
  for hh in $hhs ; do
    hrefmean=${COMHREF}/href.${fyyyymmdd}/ensprod/href.t${fcyc}z.conus.mean.f${hh}.grib2
    cp $hrefmean $href
  done
  pcp_combine ${fyyyymmdd}_${init}0000 03 ${vday}_12 24 href.t${init}z.conus.mean24.f${fhr}.nc -pcpdir $href
  mv href.t${init}z.conus.mean24.f${fhr}.nc $WORK/href.${fyyyymmdd}/hrefmean.t${init}z.conus.24h.f${fhr}.nc

  href=$WORK/href.${fyyyymmdd}/apcp24_avrg
  mkdir -p $href
  for hh in $hhs ; do
    hrefavrg=${COMHREF}/href.${fyyyymmdd}/ensprod/href.t${fcyc}z.conus.avrg.f${hh}.grib2
    cp $hrefavrg $href
  done
  pcp_combine ${fyyyymmdd}_${init}0000 03 ${vday}_12 24 href.t${init}z.conus.avrg24.f${fhr}.nc -pcpdir $href
  mv href.t${init}z.conus.avrg24.f${fhr}.nc $WORK/href.${fyyyymmdd}/hrefavrg.t${init}z.conus.24h.f${fhr}.nc

  href=$WORK/href.${fyyyymmdd}/apcp24_pmmn
  mkdir -p $href
  for hh in $hhs ; do
    hrefpmmn=${COMHREF}/href.${fyyyymmdd}/ensprod/href.t${fcyc}z.conus.pmmn.f${hh}.grib2
    cp $hrefpmmn $href
  done
  pcp_combine ${fyyyymmdd}_${init}0000 03 ${vday}_12 24 href.t${init}z.conus.pmmn24.f${fhr}.nc -pcpdir $href
  mv href.t${init}z.conus.pmmn24.f${fhr}.nc $WORK/href.${fyyyymmdd}/hrefpmmn.t${init}z.conus.24h.f${fhr}.nc

  href_lpmm=$WORK/href.${fyyyymmdd}/apcp24_lpmm
  mkdir -p $href_lpmm

  for hh in $hhs ; do
    hreflpmm=${COMHREF}/href.${fyyyymmdd}/ensprod/href.t${fcyc}z.conus.lpmm.f${hh}.grib2
    cp $hreflpmm $href_lpmm
  done
  pcp_combine ${fyyyymmdd}_${init}0000 03 ${vday}_12 24 href.t${init}z.conus.lpmm24.f${fhr}.nc -pcpdir $href_lpmm
  mv href.t${init}z.conus.lpmm24.f${fhr}.nc $WORK/href.${fyyyymmdd}/hreflpmm.t${init}z.conus.24h.f${fhr}.nc

done

fi



if [ $data = prepbufr ] ; then

 mkdir -p $WORK/prepbufr.$vday
 #export PREPBUFR=$WORK/prepbufr.$vday
 export output_base=${WORK}/pb2nc

 if [ $domain = CONUS ] ; then
   grids=G227
 elif [ $domain = Alaska ] ; then
   grids=G198
 else
   grids="G227 G198"
 fi

 if [ $lvl = profile ] ; then
    cycs="00 12"
 else
    cycs="00 01 02 03 04 05 06 07 08  09 10 11 12 13 14 15 16 17 18 19 20  21 22 23"
 fi

 for grid in $grids ; do
  for cyc in $cycs  ; do

     export vbeg=${cyc}
     export vend=${cyc}
     export verif_grid=$grid

     if [ $lvl = sfc ] ; then
       ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr_href.cong
     elif [ $lvl = profile ] ; then
       ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr_href_profile.cong
     elif [ $lvl = both ] ; then
       ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr_href.cong
       if [ $cyc = 00 ] || [ $cyc = 12 ] ; then
          ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr_href_profile.cong
       fi
     fi

  done
 done

  cp ${WORK}/pb2nc/prepbufr_nc/*.nc $WORK/prepbufr.${vday}

fi


