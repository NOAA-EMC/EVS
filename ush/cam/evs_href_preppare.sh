#!/bin/ksh
#############################################################################
# Author: Binbin Zhou /IMSG
#         Dec 15, 2021
#############################################################################
set -x

data=$1
domain=$2

#Note original ccpa hrap data are G240 grid
#     original hrefmean/prob/member  data are G227 grid
#     original st4_ak data are G255 grid (not NCEP defined grid) 

export vday=$VDATE

nextday=`$NDATE +24 ${vday}09 |cut -c1-8`
prevday=`$NDATE -24 ${vday}09 |cut -c1-8`

if [ $data = ccpa01h03h ] ; then

export  ccpadir=${WORK}/ccpa.${vday}

mkdir -p $ccpadir
cd $ccpadir

 if [ -s $COMCCPA/ccpa.${vday}/00/ccpa.t00z.03h.hrap.conus.gb2 ] && [ -s $COMCCPA/ccpa.${vday}/00/ccpa.t00z.01h.hrap.conus.gb2 ] ; then 

     for cyc in 00 ; do
       cp $COMCCPA/ccpa.${vday}/00/ccpa.t${cyc}z.01h.hrap.conus.gb2  $ccpadir/ccpa01h.t${cyc}z.G240.grib2
       cp $COMCCPA/ccpa.${vday}/00/ccpa.t${cyc}z.03h.hrap.conus.gb2  $ccpadir/ccpa03h.t${cyc}z.G240.grib2
     done

     for cyc in 01 02 03 04 05 06  ; do
       cp $COMCCPA/ccpa.${vday}/06/ccpa.t${cyc}z.01h.hrap.conus.gb2  $ccpadir/ccpa01h.t${cyc}z.G240.grib2
     done

     for cyc in 07 08 09 10 11 12  ; do
       cp $COMCCPA/ccpa.${vday}/12/ccpa.t${cyc}z.01h.hrap.conus.gb2  $ccpadir/ccpa01h.t${cyc}z.G240.grib2
     done

     for cyc in 13 14 15 16 17 18  ; do
       cp $COMCCPA/ccpa.${vday}/18/ccpa.t${cyc}z.01h.hrap.conus.gb2 $ccpadir/ccpa01h.t${cyc}z.G240.grib2
     done

     for cyc in 19 20 21 22 23  ; do
       cp $COMCCPA/ccpa.${nextday}/00/ccpa.t${cyc}z.01h.hrap.conus.gb2 $ccpadir/ccpa01h.t${cyc}z.G240.grib2
     done

 
     for cyc in  03 06 ; do 
       cp $COMCCPA/ccpa.${vday}/06/ccpa.t${cyc}z.03h.hrap.conus.gb2  $ccpadir/ccpa03h.t${cyc}z.G240.grib2
     done
 
     for cyc in 09 12 ; do 
       cp $COMCCPA/ccpa.${vday}/12/ccpa.t${cyc}z.03h.hrap.conus.gb2 $ccpadir/ccpa03h.t${cyc}z.G240.grib2
     done 

     for cyc in 15 18 ; do
       cp $COMCCPA/ccpa.${vday}/18/ccpa.t${cyc}z.03h.hrap.conus.gb2 $ccpadir/ccpa03h.t${cyc}z.G240.grib2
     done

     for cyc in 21 ; do
       cp $COMCCPA/ccpa.${nextday}/00/ccpa.t${cyc}z.03h.hrap.conus.gb2 $ccpadir/ccpa03h.t${cyc}z.G240.grib2
     done

  else
     export subject="CCPA Data Missing for EVS ${COMPONENT}"
     echo "Warning:  No CCPA data available for ${VDATE}" > mailmsg
     echo Missing file is $COMCCPA/ccpa.${vday}/00/ccpa.t00z.03h.hrap.conus.gb2 or $COMCCPA/ccpa.${vday}/00/ccpa.t00z.01h.hrap.conus.gb2 >> mailmsg
     echo "Job ID: $jobid" >> mailmsg
     cat mailmsg | mail -s "$subject" $maillist
     exit
  fi

fi

if [ $data = ccpa24h ] ; then

export output_base=${WORK}/ccpa.${vday}
export ccpadir=${WORK}/ccpa.${vday}
export ccpa24=$ccpadir/ccpa24
mkdir -p $ccpa24


 cycles="12"
 for cyc in $cycles ; do
  cp ${COMCCPA}/ccpa.${vday}/12/ccpa.t12z.06h.hrap.conus.gb2 $ccpa24/ccpa1
  cp ${COMCCPA}/ccpa.${vday}/06/ccpa.t06z.06h.hrap.conus.gb2 $ccpa24/ccpa2
  cp ${COMCCPA}/ccpa.${vday}/00/ccpa.t00z.06h.hrap.conus.gb2 $ccpa24/ccpa3
  cp ${COMCCPA}/ccpa.${prevday}/18/ccpa.t18z.06h.hrap.conus.gb2 $ccpa24/ccpa4

  if [ -s $ccpa24/ccpa1 ] && [ -s $ccpa24/ccpa2 ] && [ -s $ccpa24/ccpa3 ] && [ -s $ccpa24/ccpa4 ] ; then
    ${METPLUS_PATH}/ush/master_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_obsCCPA24h.conf
    mkdir -p ${COMOUTfinal}/precip_mean24
    cp ${WORK}/ccpa.${vday}/ccpa24h.t12z.G240.nc ${COMOUTfinal}/precip_mean24
  else
    export subject="06h CCPA Data Missing for 24h CCPA generation"
    echo "Warning: At least one of ccpa06h files is missing  for ${VDATE}" > mailmsg
    echo Missing file is ${COMCCPA}/ccpa.${vday}/12/ccpa.t12z.06h.hrap.conus.gb2 or ${COMCCPA}/ccpa.${prevday}/18/ccpa.t18z.06h.hrap.conus.gb2  >> mailmsg
    echo "Job ID: $jobid" >> mailmsg
    cat mailmsg | mail -s "$subject" $maillist
    exit
  fi

 done

fi



# Note: HREF product mean/pmmn, etc only have 1hr, 3hr APCP, but no 24APCP, so need derive their 24hr APCP
#  While product prob files have 1hr, 3hr and 24APCP probability fields, so no need to derive 
#  This is based on validation time is only at 12Z

if [ $data = apcp24h_conus ] ; then

export domain=conus
export grid=G227
export output_base=$WORK/apcp24h_conus
export fcyc	
export vcyc=12
obsv_vcyc=${vday}${vcyc}

export fhr
for fhr in 24 30 36 42 48 ; do
 fcst_time=`$NDATE -$fhr $obsv_vcyc`
 fyyyymmdd=${fcst_time:0:8}
 fcyc=${fcst_time:8:2}


  mkdir -p $WORK/href.${fyyyymmdd}

  export modelpath=${COMHREF}/href.${fyyyymmdd}/ensprod

  export prod 
  for prod in mean avrg pmmn lpmm ; do
 
     ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_fcstHREF_APCP24h.conf
     mv $output_base/href${prod}.t${fcyc}z.G227.24h.f${fhr}.nc $WORK/href.${fyyyymmdd}/.
     mkdir -p ${COMOUT}/href.${fyyyymmdd}/precip_mean24
     cp $WORK/href.${fyyyymmdd}/href${prod}.t${fcyc}z.G227.24h.f${fhr}.nc ${COMOUT}/href.${fyyyymmdd}/precip_mean24

  done

done

fi






# Note: HREF product mean/pmmn, etc only have 1hr, 3hr APCP, but no 24APCP, so need derive their 24hr APCP
#  While product prob files have 1hr, 3hr and 24APCP probability fields, so no need to derive 
#  This is obly based on validation time at 00Z, 06Z, 12Z and 18Z 

if [ $data = apcp24h_alaska ] ; then

 export domain=ak
 export grid=G255
 export output_base=$WORK/apcp24h_ak
 export fcyc
 export vcyc=12
 obsv_vcyc=${vday}${vcyc}

 export fhr

 #for fhr in 24 30 36 42 48 ; do
 for fhr in 30 ; do  #since Alaska run only at 06Z, only 30fhr fcst can be validated at 12Z 

   fcst_time=`$NDATE -$fhr $obsv_vcyc`
   fyyyymmdd=${fcst_time:0:8}
   export fcyc=${fcst_time:8:2} #Alaska only has 06 cycle run 
   #export fcyc=06  #Alaska only has 06 cycle run

   mkdir -p href.${fyyyymmdd}

   export modelpath=${COMHREF}/href.${fyyyymmdd}/ensprod
   export prod
   for prod in mean avrg pmmn lpmm ; do
	  
     ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_fcstHREF_APCP24h.conf
     mv $output_base/href${prod}.t${fcyc}z.G255.24h.f${fhr}.nc $WORK/href.${fyyyymmdd}/.
	    
   done
	      
 done

fi




if [ $data = prepbufr ] ; then

 mkdir -p $WORK/prepbufr.$vday
 export output_base=${WORK}/pb2nc

 if [ $domain = CONUS ] ; then
   grids=G227
 elif [ $domain = Alaska ] ; then
   grids=G198
 else
   grids="G227 G198"
 fi

 #lvl is set in /scripts/exevs_href_grid2obs_stats.sh (lvl=both)
 if [ $lvl = profile ] || [ $VERIF_CASE = severe ] ; then
    cycs="00 12"
 else
    cycs="00 01 02 03 04 05 06 07 08  09 10 11 12 13 14 15 16 17 18 19 20  21 22 23"
 fi

 if [ -s $COMINobsproc/rap.${VDATE}/rap.t12z.prepbufr.tm00 ] ; then
  for grid in $grids ; do
   for cyc in $cycs  ; do

     export vbeg=${cyc}
     export vend=${cyc}
     export verif_grid=$grid

     if [ $lvl = sfc ] ; then
       ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr_href.conf
     elif [ $lvl = profile ] ; then
       ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr_href_profile.conf
     elif [ $lvl = both ] ; then
       ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr_href.conf
       if [ $cyc = 00 ] || [ $cyc = 12 ] ; then
          ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr_href_profile.conf
       fi
     fi

   done
  done

  cp ${WORK}/pb2nc/prepbufr_nc/*.nc $WORK/prepbufr.${vday}

 else

   export subject="RAP Prepbufr Data Missing for EVS ${COMPONENT}"
   echo "Warning:  No RAP Prepbufr data available for ${VDATE}" > mailmsg
   echo Missing file is $COMINobsproc/rap.${VDATE}/rap.t??z.prepbufr.tm00  >> mailmsg
   echo "Job ID: $jobid" >> mailmsg
   cat mailmsg | mail -s "$subject" $maillist
   exit 
 fi



fi


if [ $data = gfs_prepbufr ] ; then

    mkdir -p $WORK/prepbufr.$vday
    export output_base=${WORK}/pb2nc

 if [ -s $COMINobsproc/gdas.${vday}/18/atmos/gdas.t18z.prepbufr ] ; then 

  for domain in Hawaii PRico ; do

   if [ $domain = Hawaii ] ; then
     grid=G139
   elif [ $domain = PRico ] ; then
     grid=G200
   fi

   export verif_grid=$grid

   for cyc in 00 12 ; do
      export vbeg=${cyc}
      export vend=${cyc}

      ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsGFS_Prepbufr_Profile.conf
   done
   cp ${WORK}/pb2nc/prepbufr_nc/*${grid}.nc $WORK/prepbufr.$vday 

  done

  else
     export subject="GFS Prepbufr Data Missing for EVS ${COMPONENT}"
     echo "Warning:  No GFS Prepbufr data available for ${VDATE}" > mailmsg
     echo Missing file is $COMINobsproc/gfs.${vday}/??/atmos/gfs.t??z.prepbufr  >> mailmsg
     echo "Job ID: $jobid" >> mailmsg
     cat mailmsg | mail -s "$subject" $maillist
     exit
  fi


fi


if [ $data = mrms ] ; then

export accum

 if [ -s $COMINmrms/MultiSensor_QPE_03H_Pass2_00.00_${vday}-120000.grib2.gz ] ; then 

  for accum in 01 03 24 ; do 	

   if [ $accum = 03 ] ; then
    cycs="00 03 06 09 12 15 18 21"
   elif [ $accum = 24 ] ; then
    cycs="00 06 12  18"
   elif [ $accum = 01 ] ; then
    cycs="00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23"
   fi

   export cyc
   export output_base=$WORK/mrms${accum}h
   export mrmsdir=$WORK/mrms.$vday
   mkdir -p $mrmsdir
   cd $mrmsdir

   for cyc in $cycs ; do

    export vbeg=$vday$cyc
    export vend=$vday$cyc
   

    mrms03=$COMINmrms/MultiSensor_QPE_${accum}H_Pass2_00.00_${vday}-${cyc}0000.grib2.gz
    cp $mrms03 $mrmsdir/.
    gunzip MultiSensor_QPE_${accum}H_Pass2_00.00_${vday}-${cyc}0000.grib2.gz
    export MET_GRIB_TABLES=$PARMevs/metplus_config/cam/precip/prep/grib2_mrms_qpf.txt

    export togrid=G216
    export grid=G216
    ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/RegridDataPlane_obsMRMSqpf.conf

    export togrid=G091
    export grid=G91
    ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/RegridDataPlane_obsMRMSqpf.conf

    export togrid=
    export grid=G255
    ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/RegridDataPlane_obsMRMSqpf_toMRMSnc.conf

   done 

    cp ${output_base}/*.nc $mrmsdir

  done

 else

   export subject="MRMS Data Missing for EVS ${COMPONENT}"
   echo "Warning:  No MRMS data available for ${VDATE}" > mailmsg
   echo Missing file is $COMINmrms/MultiSensor_QPE_??H_Pass2_00.00_${vday}-120000.grib2.gz  >> mailmsg
   echo "Job ID: $jobid" >> mailmsg
   cat mailmsg | mail -s "$subject" $maillist
   exit
 fi


fi 


