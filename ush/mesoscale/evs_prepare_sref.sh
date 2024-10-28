#!/bin/ksh
#**************************************************************************
#  Purpose: Get required input forecast and validation data files
#           for sref stat jobs
#  Last update: 
#               10/18/2024, resolved the duplicated APCP03 in arw/f03 and 06 members
#               06/05/2024, add restart capability, Binbin Zhou Lynker@EMC/NCEP
#               05/04/2024, (1) change gfs to gdas for prepbufr files
#                           (2) split the prepbufr files before running METplus PB2NC
#                               to reduce the walltime
#                               by Binbin Zhou Lynker@EMC/NCEP
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

  export output_base=${WORK}/sref
  export fhr
  export mb
  export base
  export vvhr
  #vvhr -> validation cycle hour
  #fday -> forecst running day 
  #fvhr -> forecast cycle hour
  for vvhr in 03 09 15 21  ; do
    for fhr in 06 12 18 24 30 36 42 48 54 60 66 72 78 84 ; do
      obsv_vhr=${vday}${vvhr}     #validation time: xxxx.tvvhrz.f00
      fcst_time=`$ndate -$fhr $obsv_vhr`   #fcst running time in yyyyymmddhh
      export fday=${fcst_time:0:8}
      export fvhr=${fcst_time:8:2}
      if [ ! -d $WORK/sref.${fday} ] ; then
       mkdir $WORK/sref.${fday}
      fi

      #Create for  restart
      if [ ! -d $COMOUTrestart/sref.${fday} ] ; then
        mkdir -p $COMOUTrestart/sref.${fday}
      fi

      export modelpath=$WORK/sref.${fday}

      for base in arw nmb ; do
        for mb in ctl n1 n2 n3 n4 n5 n6 p1 p2 p3 p4 p5 p6 ; do

	 #################################################################################################
	 #Check if $COMOUTrestart/sref.${fday}/sref_${base}.t${fvhr}z.${mb}.pgrb212.6hr.f${fhr}.nc exists
	 #         if not existing, run metplus to get it
	 #         if yes, copy it to the working directory (restart case)  
	 ##################################################################################################
	 if [ ! -s $COMOUTrestart/sref.${fday}/sref_${base}.t${fvhr}z.${mb}.pgrb212.6hr.f${fhr}.nc ] ; then

           ############################################################################################
	   # Note: for arw/f03 and f06 members, the APCP03 is duplicated. So grab the second one (#479:)
	   #       and save the files in the working directory 
	   # ########################################################################################## 		 
	   if [ $base = arw ] && [ $fhr = 06 ] ; then
	      sref03=${COMINsref}/sref.${fday}/$fvhr/pgrb/sref_${base}.t${fvhr}z.pgrb212.${mb}.f03.grib2
	      if [ -s $sref03 ] ; then
	        $WGRIB2 $sref03|grep "^479:"|$WGRIB2 -i $sref03 -grib $WORK/sref.${fday}/sref_${base}.t${fvhr}z.pgrb212.${mb}.f03.grib2
	      fi
	      sref06=${COMINsref}/sref.${fday}/$fvhr/pgrb/sref_${base}.t${fvhr}z.pgrb212.${mb}.f06.grib2
	      if  [ -s $sref06 ] ; then
	        $WGRIB2 $sref06|grep "^479:"|$WGRIB2 -i $sref06 -grib $WORK/sref.${fday}/sref_${base}.t${fvhr}z.pgrb212.${mb}.f06.grib2
	      fi
	      export modelpath=$WORK/sref.${fday}
            else
              export modelpath=${COMINsref}/sref.${fday}/$fvhr/pgrb  
           fi

           if [ -s $modelpath/sref_${base}.t${fvhr}z.pgrb212.${mb}.f${fhr}.grib2 ] ; then
              ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_fcstSREF_APCP06h.conf
              export err=$?; err_chk
              if [ -s $output_base/sref_${base}.t${fvhr}z.${mb}.pgrb212.6hr.f${fhr}.nc ] ; then
	        cp $output_base/sref_${base}.t${fvhr}z.${mb}.pgrb212.6hr.f${fhr}.nc $WORK/sref.${fday}/.
	        #save for restart:
	        mv $output_base/sref_${base}.t${fvhr}z.${mb}.pgrb212.6hr.f${fhr}.nc $COMOUTrestart/sref.${fday}/.
	      fi
	   fi
	 else
	   #Restart:
	   if [ -s $COMOUTrestart/sref.${fday}/sref_${base}.t${fvhr}z.${mb}.pgrb212.6hr.f${fhr}.nc ] ; then
	     cp $COMOUTrestart/sref.${fday}/sref_${base}.t${fvhr}z.${mb}.pgrb212.6hr.f${fhr}.nc $WORK/sref.${fday}
	   fi
	 fi

       done
     done 
   done
  done

fi

#********************************************************************************
# Get sref's 24hr APCP forecast files
#    First get operational sref's 3hr APCP mean grib2 files 
#    Then use Pcpcombine to get 24hr APCP netCDF files
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
  
  #Save for restart:
  if [ -s $output_base/*24mean*.nc ] ; then
    if [ ! -d ${COMOUTfinal}/apcp24mean ] ; then
        mkdir -p ${COMOUTfinal}/apcp24mean
    fi
    if [ -s $output_base/*24mean*.nc ] ; then
      cp $output_base/*24mean*.nc ${COMOUTfinal}/apcp24mean
    fi
  fi
fi  


#********************************************************************
# Get 3hr CCPA observation data over grid212 and grid240 by using MET
#  RegridDataPlane tool
# Note: checking the restart files is set in evs_sref_precip.sh   
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
  # Get 06hr CCPA data from previously obtained 3hr CCPA data files by using
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

 #Save for restart
 if [ -d ${WORK}/ccpa.${vday} ] ; then
   cp -r ${WORK}/ccpa.${vday} $COMOUTrestart
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

     #*******************************************************************************
     # Using the bufr module tool: split_by_subset to split the prepbufr data files
     #  into specifically required data types to reduce the walltime
     #*******************************************************************************
     >$WORK/prepbufr.$vday/gdas.t${vhr}z.prepbufr
     split_by_subset ${COMINobsproc}/gdas.${vday}/$vhr/atmos/gdas.t${vhr}z.prepbufr
     for subset in ADPSFC SFCSHP ADPUPA ; do
       if [ -s ${WORK}/${subset} ]; then
          cat ${WORK}/${subset} >> $WORK/prepbufr.$vday/gdas.t${vhr}z.prepbufr
       fi
     done
     export bufrpath=$WORK
     if [ -s $WORK/prepbufr.$vday/gdas.t${vhr}z.prepbufr ] ; then
       ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsGFS_Prepbufr.conf
       export err=$?; err_chk
       if [ -s ${WORK}/pb2nc/prepbufr_nc/*.nc ] ; then
         cp ${WORK}/pb2nc/prepbufr_nc/*.nc $WORK/prepbufr.${vday} 
       fi
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

  #Save for restart
  if [ -d $WORK/prepbufr.${vday} ] ; then
    cp -r $WORK/prepbufr.${vday} $COMOUTrestart
  fi

fi 

