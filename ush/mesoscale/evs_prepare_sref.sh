#!/bin/ksh
#**************************************************************************
#  Purpose: Get required input forecast and validation data files
#           for sref stat jobs
#  Last update: 
#               05/04/2024, (1) change gfs to gdas for prepbufr files
#                           (2) split the prepbufr files before running METplus PB2NC
#                               to save walltime
#                             by Binbin Zhou Lynker@EMC/NCEP
#               10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
#************************************************************************
set -x

modnam=$1

export cnvgrib=${cnvgrib:-$CNVGRIB}
export wgrib2=${wgrib2:-$WGRIB2}
export ndate=${ndate:-$NDATE}

export vday=$VDATE

#**************************************************************
# Get sref's 6hr APCP forecst data
#   First get sref member files
#   Then use MET Pcpcombine to get sref's APCP 6h mean netCD files
#**************************************************************
if [ $modnam = sref_apcp06 ] && [ ! -e $DATA/sref_mbrs.missing ] ; then

  export output_base=${WORK}/sref.${vday}
  export fhr
  export mb
  export base
  export vvhr
  #vvhr -> validation cycle hour
  #fday -> forecst running day 
  #fvhr -> forecast cycle hour
  for vvhr in 03 09 15 21  ; do
    for fhr in  06 12 18 24 30 36 42 48 54 60 66 72 78 84 ; do
      obsv_vhr=${vday}${vvhr}     #validation time: xxxx.tvvhrz.f00
      fcst_time=`$ndate -$fhr $obsv_vhr`   #fcst running time in yyyyymmddhh
      export fday=${fcst_time:0:8}
      export fvhr=${fcst_time:8:2}
      export modelpath=${COMINsref}/sref.${fday}/$fvhr/pgrb
      if [ ! -d $WORK/sref.${fday} ] ; then
       mkdir $WORK/sref.${fday}
      fi
      for base in arw nmb ; do
        for mb in ctl n1 n2 n3 n4 n5 n6 p1 p2 p3 p4 p5 p6 ; do
         ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_fcstSREF_APCP06h.conf
         export err=$?; err_chk
	 if [ -s $output_base/sref_${base}.t${fvhr}z.${mb}.pgrb212.6hr.f${fhr}.nc ] ; then
	   mv $output_base/sref_${base}.t${fvhr}z.${mb}.pgrb212.6hr.f${fhr}.nc $WORK/sref.${fday}/.
	 fi
       done
     done 
   done
  done

fi

#********************************************************************************
# Get sref's 24hr APCP forecast files
#  First get operational sref's 3hr APCP mean grib2 files 
#  Then use Pcpcombine to get 24hr APCP netCDF files
#********************************************************************************
if [ $modnam = sref_apcp24_mean ] && [ ! -e $DATA/sref_mbrs.missing ] ; then
  export output_base=${WORK}/sref.${vday}
  mkdir -p $output_base
  cd $output_base

  for vhr in 09 15 ; do
    large=${COMINsref}/sref.${vday}/${vhr}/ensprod/sref.t${vhr}z.pgrb212.mean_3hrly.grib2
    fhr=3
    while [ $fhr -le 87 ] ; do
     fhr_3=$((fhr-3))
     string="APCP:surface:${fhr_3}-${fhr} hour"
     hh=$fhr
     typeset -Z2 hh
     if [ -s $large ] ; then
       $WGRIB2 $large|grep "$string"|$WGRIB2 -i $large -grib $output_base/sref.t${vhr}z.pgrb212.mean.fhr${hh}.grib2
     fi
     fhr=$((fhr+3))
    done
  done
  for nfhr in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 ; do
   echo $nfhr |$HOMEevs/exec/sref_precip.x
  done

  export lead='24, 48, 72'
  export vhr='12'
  export modelpath=$output_base

  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_fcstSREF_APCP24h.conf
  export err=$?; err_chk
  mkdir -p ${COMOUTfinal}/apcp24mean
  if [ -s $output_base/*24mean*.nc ] ; then
    cp $output_base/*24mean*.nc ${COMOUTfinal}/apcp24mean
  fi
fi  


#********************************************************************
# Get 3hr CCPA observation data over grid212 and grid240 by using MET
#  RegridDataPlane tool
#*******************************************************************
if [ $modnam = ccpa ] && [ ! -e $DATA/ccpa.missing ] ; then

  export output_base=${WORK}/ccpa.${vday}

 if [ -s $COMINccpa/ccpa.${vday}/??/ccpa.t??z.03h.hrap.conus.gb2 ] ; then

  #ccpa hrap is in G240	

  export vhr
  for vhr in 00 06 12 18 ; do
    export ccpapath=$COMINccpa/ccpa.${vday}/$vhr
    export vbeg=$vday$vhr
    export vend=$vday$vhr

    ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/RegridDataPlane_obsCCPA_toG212.conf
    export err=$?; err_chk
    if [ -s $COMINccpa/ccpa.${vday}/$vhr/ccpa.t${vhr}z.03h.hrap.conus.gb2 ] ; then
      cp $COMINccpa/ccpa.${vday}/$vhr/ccpa.t${vhr}z.03h.hrap.conus.gb2 ${WORK}/ccpa.${vday}/ccpa.t${vhr}z.grid240.f00.grib2
    fi
  done
   
   
  typeset -Z2 vhr3
  for vhr in 03 09 15 ; do
    vhr3=$((vhr+3))
    export ccpapath=$COMINccpa/ccpa.${vday}/$vhr3
    export vbeg=$vday$vhr3
    export vend=$vday$vhr3

    ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/RegridDataPlane_obsCCPA_toG212.conf
    export err=$?; err_chk
    if [ -s $COMINccpa/ccpa.${vday}/$vhr3/ccpa.t${vhr}z.03h.hrap.conus.gb2 ] ; then
      cp $COMINccpa/ccpa.${vday}/$vhr3/ccpa.t${vhr}z.03h.hrap.conus.gb2 ${WORK}/ccpa.${vday}/ccpa.t${vhr}z.grid240.f00.grib2
    fi
  done

     DAY1=`$NDATE +24 ${vday}12`
     next=`echo ${DAY1} | cut -c 1-8`

   for vhr in 21 ; do
      export ccpapath=$COMINccpa/ccpa.${next}/00
      export vbeg=$next$vhr
      export vend=$next$vhr

     ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/RegridDataPlane_obsCCPA_toG212.conf
     export err=$?; err_chk
     if [ -s $COMINccpa/ccpa.${next}/00/ccpa.t${vhr}z.03h.hrap.conus.gb2 ] ; then
       cp $COMINccpa/ccpa.${next}/00/ccpa.t${vhr}z.03h.hrap.conus.gb2 ${WORK}/ccpa.${vday}/ccpa.t${vhr}z.grid240.f00.grib2
     fi
   done


  #************************************************************************
  # Get 06hr CCPA data from previously obtained 3hr CCPA data files by usin
  #   MET PcpCombine tool
  #************************************************************************
  ccpa06_G212=${WORK}/ccpa.${vday}/ccpa06_G212
  ccpa06_G240=${WORK}/ccpa.${vday}/ccpa06_G240
  mkdir -p $ccpa06_G212
  mkdir -p $ccpa06_G240

   export vhr 
    export vbeg=${vday}03
    export vend=${vday}21
    export valid_increment=6H
    export ccpatype=NETCDF
    export grid=grid212
    export ccpa06h=$ccpa06_G212
    export tail=nc

    ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_obsCCPA06h.conf
    export err=$?; err_chk
    export ccpatype=GFRIB
    export grid=grid240
    export ccpa06h=$ccpa06_G240
    export tail=grib2

    ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_obsCCPA06h.conf
    export err=$?; err_chk

 else
  echo "WARNING: Missing file $COMINccpa/ccpa.${vday}/??/ccpa.t??z.03h.hrap.conus.gb2"
  if [ $SENDMAIL = YES ] ; then	 
    export subject="CCPA Data Missing for EVS ${COMPONENT}"
    echo "WARNING:  No CCPA data available for ${VDATE}" > mailmsg
    echo "Missing file is $COMINccpa/ccpa.${vday}/??/ccpa.t??z.03h.hrap.conus.gb2"  >> mailmsg
    echo "Job ID: $jobid" >> mailmsg
    cat mailmsg | mail -s "$subject" $MAILTO  
  fi
 fi
fi


#*****************************************************************
# Get prepbufr data and converted to NetCDF format files by using
#  MET pb2nc tool
#  **************************************************************
if [ $modnam = prepbufr ] && [ ! -e $DATA/prepbufr.missing ] ; then

 mkdir -p $WORK/prepbufr.$vday

export output_base=${WORK}/pb2nc

 if [ -s ${COMINobsproc}/gdas.${vday}/??/atmos/gdas.t??z.prepbufr ] ; then

   for vhr in 00  06  12  18  ; do

     export vbeg=${vhr}
     export vend=${vhr}

     #Split the prepbufr data files into specifiically required data types to reduce
     #the walltime
     >$WORK/prepbufr.$vday/gdas.t${vhr}z.prepbufr
     split_by_subset ${COMINobsproc}/gdas.${vday}/$vhr/atmos/gdas.t${vhr}z.prepbufr
     cat $WORK/ADPSFC $WORK/SFCSHP $WORK/ADPUPA >> $WORK/prepbufr.$vday/gdas.t${vhr}z.prepbufr

     export bufrpath=$WORK
     ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsGFS_Prepbufr.conf
     export err=$?; err_chk
     if [ -s ${WORK}/pb2nc/prepbufr_nc/*.nc ] ; then
       cp ${WORK}/pb2nc/prepbufr_nc/*.nc $WORK/prepbufr.${vday} 
     fi
   done

 else
  echo "WARNING: Missing file is ${COMINobsproc}/gdas.${vday}/??/atmos/gdas.t??z.prepbufr"
  if [ $SENDMAIL = YES ] ; then
   export subject="Prepbufr Data Missing for EVS ${COMPONENT}"
   echo "WARNING:  No Prepbufr data available for ${VDATE}" > mailmsg
   echo "Missing file is ${COMINobsproc}/gdas.${vday}/??/atmos/gdas.t??z.prepbufr"  >> mailmsg
   echo "Job ID: $jobid" >> mailmsg
   cat mailmsg | mail -s "$subject" $MAILTO 
  fi
 fi


fi 

