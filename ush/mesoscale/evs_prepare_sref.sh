#!/bin/ksh

set -x

modnam=$1

export cnvgrib=${cnvgrib:-$CNVGRIB}
export wgrib2=${wgrib2:-$WGRIB2}
export ndate=${ndate:-$NDATE}

export vday=$VDATE

if [ $modnam = sref_apcp06 ] ; then

  export output_base=${WORK}/sref.${vday}
  export fhr
  export mb
  export base
  export vcyc
  for vcyc in 03 09 15 21  ; do
    for fhr in  06 12 18 24 30 36 42 48 54 60 66 72 78 84 ; do
      obsv_cyc=${vday}${vcyc}     #validation time: xxxx.tvcycz.f00
      fcst_time=`$ndate -$fhr $obsv_cyc`   #fcst running time in yyyyymmddhh
      export fday=${fcst_time:0:8}
      export fcyc=${fcst_time:8:2}
      export modelpath=${COMINsref}/sref.${fday}/$fcyc/pgrb
      mkdir $WORK/sref.${fday}

      for base in arw nmb ; do
        for mb in ctl n1 n2 n3 n4 n5 n6 p1 p2 p3 p4 p5 p6 ; do
         ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_fcstSREF_APCP06h.conf
         mv $output_base/sref_${base}.t${fcyc}z.${mb}.pgrb212.6hr.f${fhr}.nc $WORK/sref.${fday}/.
	  
       done
     done 
   done
  done

fi


if [ $modnam = sref_apcp24_mean ] ; then
  export output_base=${WORK}/sref.${vday}
  mkdir -p $output_base
  cd $output_base

  for cyc in 09 15 ; do
    large=$COMINsref/sref.${vday}/${cyc}/ensprod/sref.t${cyc}z.pgrb212.mean_3hrly.grib2
    fhr=3
    while [ $fhr -le 87 ] ; do
     fhr_3=$((fhr-3))
     string="APCP:surface:${fhr_3}-${fhr} hour"
     hh=$fhr
     typeset -Z2 hh
     $WGRIB2 $large|grep "$string"|$WGRIB2 -i $large -grib $output_base/sref.t${cyc}z.pgrb212.mean.fhr${hh}.grib2
     fhr=$((fhr+3))
    done
  done
  for nfhr in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 ; do
   echo $nfhr |$HOMEevs/exec/sref_precip.x
  done

  export lead='24, 48, 72'
  export cyc='12'
  export modelpath=$output_base

  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_fcstSREF_APCP24h.conf
  #mkdir -p $COMOUT/${RUN}.${VDATE}/${MODELNAME}/apcp24mean
  #cp $output_base/*24mean*.nc $COMOUT/${RUN}.${VDATE}/${MODELNAME}/apcp24mean
  mkdir -p ${COMOUTfinal}/apcp24mean
  cp $output_base/*24mean*.nc ${COMOUTfinal}/apcp24mean

fi  


if [ $modnam = ccpa ] ; then

  export output_base=${WORK}/ccpa.${vday}

 if [ -s $COMINccpa/ccpa.${vday}/18/ccpa.t18z.03h.hrap.conus.gb2 ] ; then

  #ccpa hrap is in G240	
  #cd ${WORK}/ccpa.${vday}

  export cyc
  for cyc in 00 06 12 18 ; do
    export ccpapath=$COMINccpa/ccpa.${vday}/$cyc
    export vbeg=$vday$cyc
    export vend=$vday$cyc

    ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/RegridDataPlane_obsCCPA_toG212.conf

    cp $COMINccpa/ccpa.${vday}/$cyc/ccpa.t${cyc}z.03h.hrap.conus.gb2 ${WORK}/ccpa.${vday}/ccpa.t${cyc}z.grid240.f00.grib2
  done
   
   
  typeset -Z2 cyc3
  for cyc in 03 09 15 ; do
    cyc3=$((cyc+3))
    export ccpapath=$COMINccpa/ccpa.${vday}/$cyc3
    export vbeg=$vday$cyc3
    export vend=$vday$cyc3

    ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/RegridDataPlane_obsCCPA_toG212.conf

    cp $COMINccpa/ccpa.${vday}/$cyc3/ccpa.t${cyc}z.03h.hrap.conus.gb2 ${WORK}/ccpa.${vday}/ccpa.t${cyc}z.grid240.f00.grib2

  done

     DAY1=`$NDATE +24 ${vday}12`
     next=`echo ${DAY1} | cut -c 1-8`

   for cyc in 21 ; do
      export ccpapath=$COMINccpa/ccpa.${next}/00
      export vbeg=$next$cyc
      export vend=$next$cyc

     ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/RegridDataPlane_obsCCPA_toG212.conf

     cp $COMINccpa/ccpa.${next}/00/ccpa.t${cyc}z.03h.hrap.conus.gb2 ${WORK}/ccpa.${vday}/ccpa.t${cyc}z.grid240.f00.grib2
   done

#############################################################################
#Get CCPA06h
#############################################################################

  ccpa06_G212=${WORK}/ccpa.${vday}/ccpa06_G212
  ccpa06_G240=${WORK}/ccpa.${vday}/ccpa06_G240
  mkdir -p $ccpa06_G212
  mkdir -p $ccpa06_G240

   export cyc 
    export vbeg=${vday}03
    export vend=${vday}21
    export valid_increment=6H
    export ccpatype=NETCDF
    export grid=grid212
    export ccpa06h=$ccpa06_G212
    export tail=nc

    ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_obsCCPA06h.conf

    export ccpatype=GFRIB
    export grid=grid240
    export ccpa06h=$ccpa06_G240
    export tail=grib2

    ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_obsCCPA06h.conf

 else
    export subject="CCPA Data Missing for EVS ${COMPONENT}"
    echo "Warning:  No CCPA data available for ${VDATE}" > mailmsg
    echo Missing file is $COMINccpa/ccpa.${vday}/??/ccpa.t??z.03h.hrap.conus.gb2  >> mailmsg
    echo "Job ID: $jobid" >> mailmsg
    cat mailmsg | mail -s "$subject" $maillist
    exit
 fi
fi


if [ $modnam = prepbufr ] ; then

 mkdir -p $WORK/prepbufr.$vday

export output_base=${WORK}/pb2nc

 if [ -s $COMINprepbufr/gfs.${vday}/18/atmos/gfs.t18z.prepbufr ] ; then 

   for cyc in 00  06  12  18  ; do

     export vbeg=${cyc}
     export vend=${cyc}

     ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsGFS_Prepbufr.conf
     cp ${WORK}/pb2nc/prepbufr_nc/*.nc $WORK/prepbufr.${vday} 

   done

 else

   export subject="Prepbufr Data Missing for EVS ${COMPONENT}"
   echo "Warning:  No Prepbufr data available for ${VDATE}" > mailmsg
   echo Missing file is $COMINprepbufr/gfs.${vday}/??/atmos/gfs.t??z.prepbufr  >> mailmsg
   echo "Job ID: $jobid" >> mailmsg
   cat mailmsg | mail -s "$subject" $maillist
   exit

 fi


fi 

exit
