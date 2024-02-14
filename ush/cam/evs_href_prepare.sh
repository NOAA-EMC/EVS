#!/bin/ksh
#**************************************************************************
#  Purpose: Prepare required input forecast and validation data files
#           for href stat jobs
#  Last update: 10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
#************************************************************************
set -x

#**************************
# data:    requested data 
#**************************
data=$1
domain=$2

export vday=$VDATE

nextday=`$NDATE +24 ${vday}09 |cut -c1-8`
prevday=`$NDATE -24 ${vday}09 |cut -c1-8`

#********************************************************************
# For 1hr and 3hr CCPA data, directly copy from ccpa production files
# *******************************************************************
if [ "$data" = "ccpa01h03h" ] ; then
   export  ccpadir=${WORK}/ccpa.${vday}
   mkdir -p $ccpadir
   cd $ccpadir

   has_ccpa=0
   missing_ccpa=0
   if [ -s $COMCCPA/ccpa.${vday}/00/ccpa.t00z.03h.hrap.conus.gb2 ] && [ -s $COMCCPA/ccpa.${vday}/00/ccpa.t00z.01h.hrap.conus.gb2 ] ; then 
      for vhr in 00 ; do
         cp $COMCCPA/ccpa.${vday}/00/ccpa.t${vhr}z.01h.hrap.conus.gb2  $ccpadir/ccpa01h.t${vhr}z.G240.grib2
         cp $COMCCPA/ccpa.${vday}/00/ccpa.t${vhr}z.03h.hrap.conus.gb2  $ccpadir/ccpa03h.t${vhr}z.G240.grib2
      done
      has_ccpa=$((has_ccpa + 1 ))
   else
      if [ ! -s $COMCCPA/ccpa.${vday}/00/ccpa.t00z.03h.hrap.conus.gb2 ] ; then
         echo "WARNING: $COMCCPA/ccpa.${vday}/00/ccpa.t${vhr}z.03h.hrap.conus.gb2 is missing\n" >> $DATA/job${data}${domain}_missing_ccpa_list
      else
         echo "WARNING: $COMCCPA/ccpa.${vday}/00/ccpa.t${vhr}z.01h.hrap.conus.gb2 is missing\n" >> $DATA/job${data}${domain}_missing_ccpa_list
      fi
      missing_ccpa=$((missing_ccpa + 1 ))
   fi
   for vhr in 01 02 03 04 05 06  ; do
      if [ -s $COMCCPA/ccpa.${vday}/06/ccpa.t${vhr}z.01h.hrap.conus.gb2 ] ; then
         cp $COMCCPA/ccpa.${vday}/06/ccpa.t${vhr}z.01h.hrap.conus.gb2  $ccpadir/ccpa01h.t${vhr}z.G240.grib2
         has_ccpa=$((has_ccpa + 1 ))
      else
	     echo "WARNING: $COMCCPA/ccpa.${vday}/06/ccpa.t${vhr}z.01h.hrap.conus.gb2 is missing\n" >> $DATA/job${data}${domain}_missing_ccpa_list
         missing_ccpa=$((missing_ccpa + 1 ))
      fi
   done
   for vhr in 07 08 09 10 11 12  ; do
      if [ -s $COMCCPA/ccpa.${vday}/12/ccpa.t${vhr}z.01h.hrap.conus.gb2 ] ; then
         cp $COMCCPA/ccpa.${vday}/12/ccpa.t${vhr}z.01h.hrap.conus.gb2  $ccpadir/ccpa01h.t${vhr}z.G240.grib2
	     has_ccpa=$((has_ccpa + 1 ))
      else
         echo "WARNING: $COMCCPA/ccpa.${vday}/12/ccpa.t${vhr}z.01h.hrap.conus.gb2 is missing\n" >> $DATA/job${data}${domain}_missing_ccpa_list
         missing_ccpa=$((missing_ccpa + 1 ))
      fi
   done
   for vhr in 13 14 15 16 17 18  ; do
      if [ -s $COMCCPA/ccpa.${vday}/18/ccpa.t${vhr}z.01h.hrap.conus.gb2 ] ; then 
         cp $COMCCPA/ccpa.${vday}/18/ccpa.t${vhr}z.01h.hrap.conus.gb2 $ccpadir/ccpa01h.t${vhr}z.G240.grib2
	     has_ccpa=$((has_ccpa + 1 ))
      else
	     echo "WARNING: $COMCCPA/ccpa.${vday}/18/ccpa.t${vhr}z.01h.hrap.conus.gb2 is missing\n" >> $DATA/job${data}${domain}_missing_ccpa_list
         missing_ccpa=$((missing_ccpa + 1 ))
      fi
   done
   for vhr in 19 20 21 22 23  ; do
      if [ -s $COMCCPA/ccpa.${nextday}/00/ccpa.t${vhr}z.01h.hrap.conus.gb2 ] ; then
         cp $COMCCPA/ccpa.${nextday}/00/ccpa.t${vhr}z.01h.hrap.conus.gb2 $ccpadir/ccpa01h.t${vhr}z.G240.grib2
	     has_ccpa=$((has_ccpa + 1 ))
      else
	     echo "WARNING: $COMCCPA/ccpa.${nextday}/00/ccpa.t${vhr}z.01h.hrap.conus.gb2 is missing\n" >> $DATA/job${data}${domain}_missing_ccpa_list
         missing_ccpa=$((missing_ccpa + 1 ))
      fi	  
   done
   for vhr in  03 06 ; do
      if [ -s $COMCCPA/ccpa.${vday}/06/ccpa.t${vhr}z.03h.hrap.conus.gb2 ] ; then 
         cp $COMCCPA/ccpa.${vday}/06/ccpa.t${vhr}z.03h.hrap.conus.gb2  $ccpadir/ccpa03h.t${vhr}z.G240.grib2
	     has_ccpa=$((has_ccpa + 1 ))
      else
	     echo "WARNING: $COMCCPA/ccpa.${vday}/06/ccpa.t${vhr}z.03h.hrap.conus.gb2 is missing\n" >> $DATA/job${data}${domain}_missing_ccpa_list
         missing_ccpa=$((missing_ccpa + 1 ))
      fi
   done
   for vhr in 09 12 ; do
      if [ -s $COMCCPA/ccpa.${vday}/12/ccpa.t${vhr}z.03h.hrap.conus.gb2 ] ; then
         cp $COMCCPA/ccpa.${vday}/12/ccpa.t${vhr}z.03h.hrap.conus.gb2 $ccpadir/ccpa03h.t${vhr}z.G240.grib2
	     has_ccpa=$((has_ccpa + 1 ))
      else
	     echo "WARNING: $COMCCPA/ccpa.${vday}/12/ccpa.t${vhr}z.03h.hrap.conus.gb2 is missing\n" >> $DATA/job${data}${domain}_missing_ccpa_list
         missing_ccpa=$((missing_ccpa + 1 ))
      fi
   done 
   for vhr in 15 18 ; do
      if [ -s $COMCCPA/ccpa.${vday}/18/ccpa.t${vhr}z.03h.hrap.conus.gb2 ] ; then
         cp $COMCCPA/ccpa.${vday}/18/ccpa.t${vhr}z.03h.hrap.conus.gb2 $ccpadir/ccpa03h.t${vhr}z.G240.grib2
	     has_ccpa=$((has_ccpa + 1 ))
      else
	     echo "WARNING: $COMCCPA/ccpa.${vday}/18/ccpa.t${vhr}z.03h.hrap.conus.gb2 is missing\n" >> $DATA/job${data}${domain}_missing_ccpa_list
         missing_ccpa=$((missing_ccpa + 1 ))
      fi
   done
   for vhr in 21 ; do
      if [ -s $COMCCPA/ccpa.${nextday}/00/ccpa.t${vhr}z.03h.hrap.conus.gb2 ] ; then
         cp $COMCCPA/ccpa.${nextday}/00/ccpa.t${vhr}z.03h.hrap.conus.gb2 $ccpadir/ccpa03h.t${vhr}z.G240.grib2
	     has_ccpa=$((has_ccpa + 1 ))
      else
	     echo "WARNING: $COMCCPA/ccpa.${nextday}/00/ccpa.t${vhr}z.03h.hrap.conus.gb2 is missing\n" >> $DATA/job${data}${domain}_missing_ccpa_list
         missing_ccpa=$((missing_ccpa + 1 ))
      fi
   done
   if [ "$missing_ccpa" -gt "0" ] ; then 
      echo "WARNING:  No CCPA data in $COMCCPA available for EVS ${COMPONENT}" 
    if [ "$SENDMAIL" = "YES" ] ; then
      export subject="CCPA Data Missing for EVS ${COMPONENT}"
      echo "WARNING:  No CCPA data available for ${VDATE}" > mailmsg
      echo -e "`cat $DATA/job${data}${domain}_missing_ccpa_list`" >> mailmsg
      echo "Job ID: $jobid" >> mailmsg
      cat mailmsg | mail -s "$subject" $MAILTO
    fi
   fi
fi


#*******************************************************
# For 24hr ccpa data
# by using 6hr ccpa to derived from MET pcpcombine tool
# ******************************************************
if [ "$data" = "ccpa24h" ] ; then

   export output_base=${WORK}/ccpa.${vday}
   export ccpadir=${WORK}/ccpa.${vday}
   export ccpa24=$ccpadir/ccpa24
   mkdir -p $ccpa24

   vhours="12"
   for vhr in $vhours ; do
      if [ -s ${COMCCPA}/ccpa.${vday}/12/ccpa.t12z.06h.hrap.conus.gb2 ]; then
         cp ${COMCCPA}/ccpa.${vday}/12/ccpa.t12z.06h.hrap.conus.gb2 $ccpa24/ccpa1
      else
	     echo "Missing file is ${COMCCPA}/ccpa.${vday}/12/ccpa.t12z.06h.hrap.conus.gb2\n" >> $DATA/job${data}${domain}_missing_24hrccpa_list
      fi
      if [ -s ${COMCCPA}/ccpa.${vday}/06/ccpa.t06z.06h.hrap.conus.gb2 ]; then
         cp ${COMCCPA}/ccpa.${vday}/06/ccpa.t06z.06h.hrap.conus.gb2 $ccpa24/ccpa2
      else
	     echo "Missing file is ${COMCCPA}/ccpa.${vday}/06/ccpa.t06z.06h.hrap.conus.gb2\n" >> $DATA/job${data}${domain}_missing_24hrccpa_list
      fi
      if [ -s ${COMCCPA}/ccpa.${vday}/00/ccpa.t00z.06h.hrap.conus.gb2 ]; then
         cp ${COMCCPA}/ccpa.${vday}/00/ccpa.t00z.06h.hrap.conus.gb2 $ccpa24/ccpa3
      else
	     echo "Missing file is ${COMCCPA}/ccpa.${vday}/00/ccpa.t00z.06h.hrap.conus.gb2\n" >> $DATA/job${data}${domain}_missing_24hrccpa_list
      fi
      if [ -s ${COMCCPA}/ccpa.${prevday}/18/ccpa.t18z.06h.hrap.conus.gb2 ]; then
         cp ${COMCCPA}/ccpa.${prevday}/18/ccpa.t18z.06h.hrap.conus.gb2 $ccpa24/ccpa4
      else
	     echo "Missing file is ${COMCCPA}/ccpa.${prevday}/18/ccpa.t18z.06h.hrap.conus.gb2\n" >> $DATA/job${data}${domain}_missing_24hrccpa_list
      fi
      if [ -s $ccpa24/ccpa1 ] && [ -s $ccpa24/ccpa2 ] && [ -s $ccpa24/ccpa3 ] && [ -s $ccpa24/ccpa4 ] ; then
         ${METPLUS_PATH}/ush/master_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_obsCCPA24h.conf
         export err=$?; err_chk
         mkdir -p ${COMOUTfinal}/precip_mean24
         cp ${WORK}/ccpa.${vday}/ccpa24h.t12z.G240.nc ${COMOUTfinal}/precip_mean24
      else
	 echo "WARNING: At least one of ccpa06h files $ccpa24/ccpa? is missing for EVS ${COMPONENT}"
         if [ "$SENDMAIL" = "YES" ] ; then
            export subject="06h CCPA Data Missing for 24h CCPA generation"
            echo "WARNING: At least one of ccpa06h files is missing  for ${VDATE}" > mailmsg
            echo -e "`cat $DATA/job${data}${domain}_missing_24hrccpa_list`" >> mailmsg
            echo "Job ID: $jobid" >> mailmsg
            cat mailmsg | mail -s "$subject" $MAILTO
         fi
      fi
   done
fi


#**********************************************************************************************************
# For HREF 24hr forecast APCP over CONUS, by using HREF's 3hr APCP data files from MET pcpcombine tool 
# Note: HREF product mean/pmmn, etc only have 1hr, 3hr APCP, but no 24APCP, so need derive their 24hr APCP
#  While product prob files have 1hr, 3hr and 24APCP probability fields, so no need to derive 
#  This is based on validation time is only at 12Z
#  *******************************************************************************************************
if [ "$data" = "apcp24h_conus" ] ; then

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
         export err=$?; err_chk
         mv $output_base/href${prod}.t${fcyc}z.G227.24h.f${fhr}.nc $WORK/href.${fyyyymmdd}/.
         mkdir -p ${COMOUT}/href.${fyyyymmdd}/precip_mean24
         if [ -s $WORK/href.${fyyyymmdd}/href${prod}.t${fcyc}z.G227.24h.f${fhr}.nc ] ; then
            cp $WORK/href.${fyyyymmdd}/href${prod}.t${fcyc}z.G227.24h.f${fhr}.nc ${COMOUT}/href.${fyyyymmdd}/precip_mean24
         fi
      done
   done
fi


#**********************************************************************************************************
# For HREF 24hr forecast APCP over Alaska, by using HREF's 3hr APCP data files from MET pcpcombine tool
# Note: HREF product mean/pmmn, etc only have 1hr, 3hr APCP, but no 24APCP, so need derive their 24hr APCP
#  While product prob files have 1hr, 3hr and 24APCP probability fields, so no need to derive 
#  This is obly based on validation time at 00Z, 06Z, 12Z and 18Z 
#**********************************************************************************************************
if [ "$data" = "apcp24h_alaska" ] ; then

   export domain=ak
   export grid=G255
   export output_base=$WORK/apcp24h_ak
   export fcyc
   export vcyc=12
   obsv_vcyc=${vday}${vcyc}

   export fhr
   for fhr in 30 ; do  #since Alaska run only at 06Z, only 30fhr fcst can be validated at 12Z 
      fcst_time=`$NDATE -$fhr $obsv_vcyc`
      fyyyymmdd=${fcst_time:0:8}
      export fcyc=${fcst_time:8:2} #Alaska only has 06 cycle run 
      mkdir -p href.${fyyyymmdd}
      export modelpath=${COMHREF}/href.${fyyyymmdd}/ensprod
      export prod
      for prod in mean avrg pmmn lpmm ; do
         ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_fcstHREF_APCP24h.conf
         export err=$?; err_chk
         if [ -s $output_base/href${prod}.t${fcyc}z.G255.24h.f${fhr}.nc ] ; then
            mv $output_base/href${prod}.t${fcyc}z.G255.24h.f${fhr}.nc $WORK/href.${fyyyymmdd}/.
         fi 	    
      done
   done
fi


#********************************************************
# For RAP prepbufr data files: need to convert to netCDF format
#      by using MET pb2nc tool
#********************************************************  
if [ "$data" = "prepbufr" ] ; then

   mkdir -p $WORK/prepbufr.$vday
   export output_base=${WORK}/pb2nc
   if [ "$domain" = "CONUS" ] ; then
      grids=G227
   elif [ "$domain" = "Alaska" ] ; then
      grids=G198
   else
      grids="G227 G198"
   fi
   
   if [ "$lvl" = "profile" ] || [ "$VERIF_CASE" = "severe" ] ; then
      cycs="00 12"
   else
      cycs="00 01 02 03 04 05 06 07 08  09 10 11 12 13 14 15 16 17 18 19 20  21 22 23"
   fi
   
   if [ -s $COMINobsproc/rap.${VDATE}/rap.t12z.prepbufr.tm00 ] ; then
      for grid in $grids ; do
         for vhr in $cycs  ; do
            export vbeg=${vhr}
            export vend=${vhr}
            export verif_grid=$grid
            if [ "$lvl" = "sfc" ] ; then
               ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr_href.conf
               export err=$?; err_chk
            elif [ "$lvl" = "profile" ] ; then
               ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr_href_profile.conf
               export err=$?; err_chk
            elif [ "$lvl" = "both" ] ; then
               ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr_href.conf
               export err=$?; err_chk
               if [ "$vhr" = "00" ] || [ "$vhr" = "12" ] ; then
                  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr_href_profile.conf
	              export err=$?; err_chk
               fi
            fi
         done
      done
      if [ -s ${WORK}/pb2nc/prepbufr_nc/*.nc ] ; then
         cp ${WORK}/pb2nc/prepbufr_nc/*.nc $WORK/prepbufr.${vday}
      fi
   else
      echo "WARNING:  No RAP Prepbufr data $COMINobsproc/rap.${VDATE}/rap.t12z.prepbufr.tm00 AVAILABLE FOR ${vdate}"
      if [ "$SENDMAIL" = "YES" ] ; then
         export subject="RAP Prepbufr Data Missing for EVS ${COMPONENT}"
         echo "WARNING:  No RAP Prepbufr data available for ${VDATE}" > mailmsg
         echo Missing file is $COMINobsproc/rap.${VDATE}/rap.t12z.prepbufr.tm00  >> mailmsg
         echo "Job ID: $jobid" >> mailmsg
         cat mailmsg | mail -s "$subject" $MAILTO
      fi
   fi
fi


#********************************************************
# For GFS prepbufr data files: need to convert to netCDF format
#      by using MET pb2nc tool
# Used for validation over Hawaii and Peurto Rico
#********************************************************
if [ "$data" = "gfs_prepbufr" ] ; then

   mkdir -p $WORK/prepbufr.$vday
   export output_base=${WORK}/pb2nc
   if [ -s $COMINobsproc/gdas.${vday}/18/atmos/gdas.t18z.prepbufr ] ; then 
      for domain in Hawaii PRico ; do
         if [ "$domain" = "Hawaii" ] ; then
            grid=G139
         elif [ "$domain" = "PRico" ] ; then
            grid=G200
         fi
         export verif_grid=$grid
         for vhr in 00 12 ; do
            export vbeg=${vhr}
            export vend=${vhr}
            ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsGFS_Prepbufr_Profile.conf
            export err=$?; err_chk
         done
         if [ -s ${WORK}/pb2nc/prepbufr_nc/*${grid}.nc ] ; then
            cp ${WORK}/pb2nc/prepbufr_nc/*${grid}.nc $WORK/prepbufr.$vday 
         fi
      done
   else
      echo "WARNING:  No GFS Prepbufr data $COMINobsproc/gdas.${vday}/18/atmos/gdas.t18z.prepbufr available for EVS ${COMPONENT}"
      if [ "$SENDMAIL" = "YES" ] ; then
         export subject="GFS Prepbufr Data Missing for EVS ${COMPONENT}"
         echo "WARNING:  No GFS Prepbufr data available for ${VDATE}" > mailmsg
         echo Missing file is $COMINobsproc/gdas.${vday}/18/atmos/gdas.t18z.prepbufr  >> mailmsg
         echo "Job ID: $jobid" >> mailmsg
         cat mailmsg | mail -s "$subject" $MAILTO
      fi
   fi
fi

#********************************************************************
# For MRMS precip data over Alaska, need to convert to required grid
#     by using MET RegridDataPlane tool
#*********************************************************************
if [ "$data" = "mrms" ] ; then
   
   export accum
   if [ -s $DCOMINmrms/MultiSensor_QPE_??H_Pass2_00.00_${vday}-??0000.grib2.gz ] ; then 
      for accum in 01 03 24 ; do 	
         if [ "$accum" = "03" ] ; then
            cycs="00 03 06 09 12 15 18 21"
         elif [ "$accum" = "24" ] ; then
            cycs="00 06 12  18"
         elif [ "$accum" = "01" ] ; then
            cycs="00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23"
         fi
         export vhr
         export output_base=$WORK/mrms${accum}h
         export mrmsdir=$WORK/mrms.$vday
         mkdir -p $mrmsdir
         cd $mrmsdir
         for vhr in $cycs ; do
            export vbeg=$vday$vhr
            export vend=$vday$vhr
            mrms03=$DCOMINmrms/MultiSensor_QPE_${accum}H_Pass2_00.00_${vday}-${vhr}0000.grib2.gz
            if [ -s $mrms03 ] ; then 
               cp $mrms03 $mrmsdir/.
               gunzip MultiSensor_QPE_${accum}H_Pass2_00.00_${vday}-${vhr}0000.grib2.gz
               export MET_GRIB_TABLES=$PARMevs/metplus_config/prep/$COMPONENT/precip/grib2_mrms_qpf.txt
               export togrid=G216
               export grid=G216
               ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/RegridDataPlane_obsMRMSqpf.conf
               export err=$?; err_chk
               export togrid=G091
               export grid=G91
               ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/RegridDataPlane_obsMRMSqpf.conf
               export err=$?; err_chk
               export togrid=
               export grid=G255
               ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/RegridDataPlane_obsMRMSqpf_toMRMSnc.conf
               export err=$?; err_chk
            else
               echo "WARNING: $mrms03 is missing"
            fi    
         done 
         if [ -s ${output_base}/*.nc ] ; then
            cp ${output_base}/*.nc $mrmsdir
         fi
      done
   else
      echo "WARNING:  No MRMS data $DCOMINmrms/MultiSensor_QPE_*.grib2.gz available for EVS ${COMPONENT}"
      if [ "$SENDMAIL" = "YES" ] ; then
         export subject="MRMS Data Missing for EVS ${COMPONENT}"
         echo "WARNING:  No MRMS data available for ${VDATE}" > mailmsg
         echo Missing file is $DCOMINmrms/MultiSensor_QPE_*.grib2.gz  >> mailmsg
         echo "Job ID: $jobid" >> mailmsg
         cat mailmsg | mail -s "$subject" $MAILTO
      fi
   fi
fi 
