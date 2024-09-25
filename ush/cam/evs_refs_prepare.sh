#!/bin/ksh
#**************************************************************************
#  Purpose: Prepare required input forecast and validation data files
#           for refs stat jobs
#  Last update: 
#              05/30/2024, by Binbin Zhou Lynker@EMC/NCEP
#************************************************************************
set -x

#**************************
# data:    requested data 
#**************************
data=$1
domain=$2

#Note original ccpa hrap data are G240 grid
#     original refs mean/prob/member  data are G227 grid
#     original st4_ak data are G255 grid (not NCEP defined grid)

export vday=$VDATE

nextday=`$NDATE +24 ${vday}09 |cut -c1-8`
prevday=`$NDATE -24 ${vday}09 |cut -c1-8`

#********************************************************************
# For 1hr and 3hr CCPA data, directly copy from ccpa production files
# First check if this task has been completed in the previous run
#    if no, continue this task
#    otherwise, copy all ccpa nc files from restart directory
#
#
# *******************************************************************
if [ "$data" = "ccpa01h03h" ] ; then

  if [ ! -e $COMOUTrestart/prepare/ccpa01h03h.completed ] ; then

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

   #For restart
   [[ ! -e $COMOUTrestart/prepare/ccpa.${vday} ]] && mkdir -p $COMOUTrestart/prepare/ccpa.${vday}
   if [ -s $ccpadir/*.grib2 ] ; then
     cp $ccpadir/*01h*.grib2 $COMOUTrestart/prepare/ccpa.${vday}
     cp $ccpadir/*03h*.grib2 $COMOUTrestart/prepare/ccpa.${vday}
     >$COMOUTrestart/prepare/ccpa01h03h.completed 
   fi

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

  #copy from existing restart files: 
  else
   [[ ! -d $WORK/ccpa.${vday} ]] && mkdir -p $WORK/ccpa.${vday}
    if [ -s $COMOUTrestart/prepare/ccpa.${vday}/ccpa01h.*.grib2 ] ; then
     cp  $COMOUTrestart/prepare/ccpa.${vday}/ccpa01h.*.grib2 $WORK/ccpa.${vday}
    fi
    if [ -s $COMOUTrestart/prepare/ccpa.${vday}/ccpa03h.*.grib2 ] ; then
     cp  $COMOUTrestart/prepare/ccpa.${vday}/ccpa03h.*.grib2 $WORK/ccpa.${vday}
    fi
  fi
  

fi


#*******************************************************
# For 24hr ccpa data
# by using 6hr ccpa to derived from MET pcpcombine tool
# ******************************************************
if [ "$data" = "ccpa24h" ] ; then

  if [ ! -e $COMOUTrestart/prepare/ccpa24h.completed ] ; then	

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
	 if [ ! -d ${COMOUTfinal}/precip_mean24 ] ; then
           mkdir -p ${COMOUTfinal}/precip_mean24
	 fi
	 if [ -s ${WORK}/ccpa.${vday}/ccpa24h.t12z.G240.nc ] ; then
          cp ${WORK}/ccpa.${vday}/ccpa24h.t12z.G240.nc ${COMOUTfinal}/precip_mean24
         fi

	 #For restart:
	 [[ ! -e $COMOUTrestart/prepare/ccpa.${vday} ]] && mkdir -p $COMOUTrestart/prepare/ccpa.${vday}
	 if [ -s $WORK/ccpa.${vday}/*24h*.nc ] ; then
	    cp $WORK/ccpa.${vday}/*24h*.nc  $COMOUTrestart/prepare/ccpa.${vday}
            >$COMOUTrestart/prepare/ccpa24h.completed
	 fi


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

  else
    #Copy from the existing restart files 	  
    [[ ! -d $WORK/ccpa.${vday} ]] && mkdir -p $WORK/ccpa.${vday}
    if [ -s $COMOUTrestart/prepare/ccpa.${vday}/ccpa24h*.nc ] ; then 
      cp  $COMOUTrestart/prepare/ccpa.${vday}/ccpa24h*.nc $WORK/ccpa.${vday}
    fi
  fi


fi


#**********************************************************************************************************
# For REFS 24hr forecast APCP over CONUS, by using REFS's 3hr APCP data files from MET pcpcombine tool 
# Note: REFS product mean/pmmn, etc only have 1hr, 3hr APCP, but no 24APCP, so need derive their 24hr APCP
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

      mkdir -p $WORK/refs.${fyyyymmdd}
      export modelpath=${COMREFS}/refs.${fyyyymmdd}/ensprod

      #Create for restart
      [[ ! -e $COMOUTrestart/prepare/refs.${fyyyymmdd} ]] && mkdir -p $COMOUTrestart/prepare/refs.${fyyyymmdd}

      export prod
      for prod in mean avrg pmmn lpmm ; do

      #####################################################################################################################
      # Restart: first check if refs.${fyyyymmdd}/refs${prod}.t${fcyc}z.G227.24h.f${fhr}.nc exists 
      #    in the $COMOUTrestart directory, if not, run METplus to create it
      #    otherwise, copy it from the $COMOUTrestart directory
      ###################################################################################################################
      if [ ! -s  $COMOUTrestart/prepare/refs.${fyyyymmdd}/refs${prod}.t${fcyc}z.G227.24h.f${fhr}.nc ] ; then
	if [ -s ${modelpath}/refs.t${fcyc}z.${domain}.${prod}.f${fhr}.grib2 ] ; then
         ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_fcstREFS_APCP24h.conf
         export err=$?; err_chk
         mv $output_base/refs${prod}.t${fcyc}z.G227.24h.f${fhr}.nc $WORK/refs.${fyyyymmdd}/.
	 if [ ! -d ${COMOUT}/refs.${fyyyymmdd}/precip_mean24 ] ; then
	   mkdir -p  ${COMOUT}/refs.${fyyyymmdd}/precip_mean24
	 fi
         if [ -s $WORK/refs.${fyyyymmdd}/refs${prod}.t${fcyc}z.G227.24h.f${fhr}.nc ] ; then
            cp $WORK/refs.${fyyyymmdd}/refs${prod}.t${fcyc}z.G227.24h.f${fhr}.nc ${COMOUT}/refs.${fyyyymmdd}/precip_mean24
         fi

	 #Save restart files 
	 [[ $? = 0 ]] && cp $WORK/refs.${fyyyymmdd}/refs${prod}.t${fcyc}z.G227.24h.f${fhr}.nc $COMOUTrestart/prepare/refs.${fyyyymmdd}
        fi
       else
         #Restart: copy restart files to the working directory
         [[ ! -d $WORK/refs.${fyyyymmdd} ]] && mkdir -p $WORK/refs.${fyyyymmdd}
	 if [ -s $COMOUTrestart/prepare/refs.${fyyyymmdd}/refs${prod}.t${fcyc}z.G227.24h.f${fhr}.nc ] ; then
           cp  $COMOUTrestart/prepare/refs.${fyyyymmdd}/refs${prod}.t${fcyc}z.G227.24h.f${fhr}.nc $WORK/refs.${fyyyymmdd}
	 fi
       fi

      done
   done
fi


#**********************************************************************************************************
# For REFS 24hr forecast APCP over Alaska, by using REFS's 3hr APCP data files from MET pcpcombine tool
# Note: REFS product mean/pmmn, etc only have 1hr, 3hr APCP, but no 24APCP, so need derive their 24hr APCP
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
   for fhr in 24 30 36 42 48 ; do  
      fcst_time=`$NDATE -$fhr $obsv_vcyc`
      fyyyymmdd=${fcst_time:0:8}
      export fcyc=${fcst_time:8:2}  
      mkdir -p refs.${fyyyymmdd}
      export modelpath=${COMREFS}/refs.${fyyyymmdd}/ensprod
      export prod

      #Create for restart
      [[ ! -e $COMOUTrestart/prepare/refs.${fyyyymmdd} ]] && mkdir -p $COMOUTrestart/prepare/refs.${fyyyymmdd}

      for prod in mean avrg pmmn lpmm ; do
      #################################################################################################
      # Restart: first check if refs.${fyyyymmdd}/refs${prod}.t${fcyc}z.G255.24h.f${fhr}.nc exists
      #    in the $COMOUTrestart directory, if not, run METplus to create it
      #    otherwise, copy it from the $COMOUTrestart directory
      ##################################################################################################
      if [ ! -s  $COMOUTrestart/prepare/refs.${fyyyymmdd}/refs${prod}.t${fcyc}z.G255.24h.f${fhr}.nc ] ; then
	if [ -s ${modelpath}/refs.t${fcyc}z.${domain}.${prod}.f${fhr}.grib2 ] ; then
         ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_fcstREFS_APCP24h.conf
         export err=$?; err_chk
         if [ -s $output_base/refs${prod}.t${fcyc}z.G255.24h.f${fhr}.nc ] ; then
            mv $output_base/refs${prod}.t${fcyc}z.G255.24h.f${fhr}.nc $WORK/refs.${fyyyymmdd}/.
         fi

         #Save restart files
         [[ $? = 0 ]] && cp $WORK/refs.${fyyyymmdd}/refs${prod}.t${fcyc}z.G255.24h.f${fhr}.nc $COMOUTrestart/prepare/refs.${fyyyymmdd}
        fi
       else
         #Restart: copy restart files to the working directory
	 [[ ! -d $WORK/refs.${fyyyymmdd} ]] && mkdir -p $WORK/refs.${fyyyymmdd}
	 if [ -s $COMOUTrestart/prepare/refs.${fyyyymmdd}/refs${prod}.t${fcyc}z.G255.24h.f${fhr}.nc ] ; then
           cp  $COMOUTrestart/prepare/refs.${fyyyymmdd}/refs${prod}.t${fcyc}z.G255.24h.f${fhr}.nc $WORK/refs.${fyyyymmdd}
	 fi
       fi
      done
   done
fi


#*****************************************************************
# For RAP prepbufr data files: need to convert to netCDF format
#      by using MET pb2nc tool
#  First check if this task has been completed in the previous run
#    if no, continue this task
#    otherwise, copy all prepbufr nc files from restart directory
#*****************************************************************
if [ "$data" = "prepbufr" ] ; then

 if [ ! -e $COMOUTrestart/prepare/rap_prepbufr.completed ] ; then

   [[ ! -d $WORK/prepbufr.$vday ]] && mkdir -p $WORK/prepbufr.$vday
   export output_base=${WORK}/pb2nc
   if [ "$domain" = "CONUS" ] ; then
      grids=G227
   elif [ "$domain" = "Alaska" ] ; then
      grids=G198
   else
      grids="G227 G198"
   fi
   
   if [ "$lvl" = "profile" ] || [ "$VERIF_CASE" = "severe" ] || [ "$VERIF_CASE" = "spcoutlook" ] ; then
      cycs="00 12"
   else
      cycs="00 03 06 09 12 15 18  21"
   fi
   
   if [ -s $COMINobsproc/rap.${VDATE}/rap.t12z.prepbufr.tm00 ] ; then
      for grid in $grids ; do
         for vhr in $cycs  ; do
            export vbeg=${vhr}
            export vend=${vhr}
            export verif_grid=$grid

            if [ "$lvl" = "sfc" ] ; then
               ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr_refs.conf
               export err=$?; err_chk
            elif [ "$lvl" = "profile" ] ; then
               ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr_refs_profile.conf
               export err=$?; err_chk
            elif [ "$lvl" = "both" ] ; then
               ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr_refs.conf
               export err=$?; err_chk
               if [ "$vhr" = "00" ] || [ "$vhr" = "12" ] ; then
                  ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr_refs_profile.conf
	              export err=$?; err_chk
               fi
            fi

         done
      done

      if [ -s ${WORK}/pb2nc/prepbufr_nc/*.nc ] ; then
         cp ${WORK}/pb2nc/prepbufr_nc/*.nc $WORK/prepbufr.${vday}
	 #Save restart files 
	 cp ${WORK}/pb2nc/prepbufr_nc/*.nc $COMOUTrestart/prepare/prepbufr.${vday}
	 >$COMOUTrestart/prepare/rap_prepbufr.completed
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

 else
    #restart: copy restart files to the working directory
    [[ ! -d $WORK/prepbufr.${vday} ]] && mkdir -p $WORK/prepbufr.${vday}
    if [ -s $COMOUTrestart/prepare/prepbufr.${VDATE}/*G227*.nc ] ; then
      cp $COMOUTrestart/prepare/prepbufr.${VDATE}/*G227*.nc $WORK/prepbufr.${vday}
    fi
    if [ -s $COMOUTrestart/prepare/prepbufr.${VDATE}/*G198*.nc ] ; then
      cp $COMOUTrestart/prepare/prepbufr.${VDATE}/*G198*.nc $WORK/prepbufr.${vday}
    fi
 fi

fi


#******************************************************************
# For GFS prepbufr data files: need to convert to netCDF format
#      by using MET pb2nc tool
# Used for validation over Hawaii and Peurto Rico
#  First check if this task has been completed in the previous run
#    if no, continue this task
#    otherwise, copy all prepbufr nc files from restart directory
#*******************************************************************
if [ "$data" = "gdas_prepbufr" ] ; then

 if [ ! -e $COMOUTrestart/prepare/gdas_prepbufr.completed ] ; then

   [[ ! -d $WORK/prepbufr.$vday ]] && mkdir -p $WORK/prepbufr.$vday
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

	    >$WORK/prepbufr.$vday/gdas.t${vhr}z.${grid}.prepbufr
	    split_by_subset $COMINobsproc/gdas.${vday}/${vhr}/atmos/gdas.t${vhr}z.prepbufr
            cat $WORK/ADPUPA $WORK/ADPSFC >> $WORK/prepbufr.$vday/gdas.t${vhr}z.${grid}.prepbufr
	    export bufrpath=$WORK

            ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsGDAS_Prepbufr_refs_profile.conf
            export err=$?; err_chk
         done
         if [ -s ${WORK}/pb2nc/prepbufr_nc/*${grid}.nc ] ; then
            cp ${WORK}/pb2nc/prepbufr_nc/*${grid}.nc $WORK/prepbufr.$vday 
         fi
      done

      #For restart
      if [ $? = 0 ] ; then
        cp ${WORK}/pb2nc/prepbufr_nc/*.nc $COMOUTrestart/prepare/prepbufr.${vday}
        >$COMOUTrestart/prepare/gdas_prepbufr.completed
      fi

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

  else
    #Restart: copy files from restart files
    [[ ! -d $WORK/prepbufr.${vday} ]] && mkdir -p $WORK/prepbufr.${vday}
    if [ -s $COMOUTrestart/prepare/prepbufr.${VDATE}/*G200*.nc ] ; then
     cp $COMOUTrestart/prepare/prepbufr.${VDATE}/*G200*.nc $WORK/prepbufr.${vday}
    fi 
    if [ -s $COMOUTrestart/prepare/prepbufr.${VDATE}/*G139*.nc ] ; then
     cp $COMOUTrestart/prepare/prepbufr.${VDATE}/*G139*.nc $WORK/prepbufr.${vday}
    fi
  fi

fi

#********************************************************************
# For MRMS precip data over Alaska, need to convert to required grid
#     by using MET RegridDataPlane tool
#*********************************************************************
if [ "$data" = "mrms" ] ; then
  
 #############################################################
 # First check if this task has been completed, 
 # If no, do this task 
 # Otherwise, copy the mrms files from the restart directory
 ############################################################	
 if [ ! -e $COMOUTrestart/prepare/mrms.completed ] ; then      	

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

      #Save for restart
      if [ $? = 0 ] ; then
        [[ ! -d $COMOUTrestart/prepare/mrms.$vday ]] && mkdir -p $COMOUTrestart/prepare/mrms.$vday
        if [ -s $mrmsdir/*.nc ] ; then 
	  cp $mrmsdir/*.nc $COMOUTrestart/prepare/mrms.$vday
          >$COMOUTrestart/prepare/mrms.completed
	fi 
      fi

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

  else
    #Restart: copy from the restart files
    [[ ! -d $WORK/mrms.$vday ]] && mkdir -p $WORK/mrms.$vday
    if [ -s $COMOUTrestart/prepare/mrms.$vday/*.nc ] ; then
     cp $COMOUTrestart/prepare/mrms.$vday/*.nc $WORK/mrms.$vday  
    fi
  fi

fi 

#*************************************************************************
# Prepare the REFS member files for SFC fields since there 2 TCDC fields
#   but only one is required and METplus is hard to read the specific one.
#   So to retrieve this one TCDC, retrieve all required sfc fields
#************************************************************************
if [ "$data" = "sfc" ] ; then

  cd $DATA
  >$DATA/pat
  echo ">$/pat" 
  echo "VIS" >> $DATA/pat
  echo "DPT:2 m" >> $DATA/pat
  echo "TMP:2 m" >> $DATA/pat
  echo "UGRD:10 m" >> $DATA/pat
  echo "VGRD:10 m" >> $DATA/pat
  echo "HGT:cloud ceiling" >> $DATA/pat
  echo "RH:2 m" >> $DATA/pat
  echo "CAPE" >> $DATA/pat
  echo "GUST" >> $DATA/pat
  echo "HGT:planetary" >> $DATA/pat
  echo "MSLET" >> $DATA/pat

  >$DATA/prepare_poe.sh 
  for day in $PDYm1 $PDYm2 $PDYm3 ; do
   work=$DATA/refs.$day/verf_g2g
   mkdir -p $work

   for cyc in 00 06 12 18 ; do 
    for domain in conus ak ; do

      >run_prepare.${day}.${cyc}.${domain}.sh

      echo "#!/bin/ksh" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "set -x" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "work=$work" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "cd \$work">> run_prepare.${day}.${cyc}.${domain}.sh
      echo "for fhr in 3 6 9 12 15 18 21 24 27 30 33 36 39 42 45 48 ; do" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "    typeset -Z2 hh" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "    hh=\$fhr      " >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "      for mbr in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 ; do" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "        refs=$COMREFS/refs.${day}/verf_g2g/refs.m\${mbr}.t${cyc}z.${domain}.f\${hh}" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "        if [ -s \$refs ] ; then" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "          $WGRIB2 \$refs|grep --file=$DATA/pat|$WGRIB2 -i \$refs -grib  \$work/refs.m\${mbr}.t${cyc}z.${domain}.f\${hh}" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "          if [ \$mbr = 01 ] || [ \$mbr = 02 ] || [ \$mbr = 03 ] || [ \$mbr = 04 ] || [ \$mbr = 05 ] || [ \$mbr = 06 ] || [ \$mbr = 13 ] ; then " >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "             tm=\$fhr" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "          else" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "             tm=\$((fhr+6))" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "          fi" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "          string=\"TCDC:entire atmosphere (considered as a single layer):\${tm} hour fcst\" " >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "	      $WGRIB2 \$refs|grep \"\$string\"|$WGRIB2 -i \$refs -grib  \$work/tcdc.m\${mbr}.t${cyc}z.${domain}.f\${hh}" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "	      cat \$work/tcdc.m\${mbr}.t${cyc}z.${domain}.f\${hh} >> \$work/refs.m\${mbr}.t${cyc}z.${domain}.f\${hh}" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "        fi" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "    done" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo " done" >> run_prepare.${day}.${cyc}.${domain}.sh
   
      chmod +x run_prepare.${day}.${cyc}.${domain}.sh
      echo "${DATA}/run_prepare.${day}.${cyc}.${domain}.sh" >> run_prepare_poe.sh

    done
   done
  done

   chmod +x run_prepare_poe.sh

   if [ $run_mpi = yes ] ; then
     mpiexec  -n 24 -ppn 24 --cpu-bind core --depth=2 cfp ${DATA}/run_prepare_poe.sh
   else
    ${DATA}/run_prepare_poe.sh
   fi

fi

