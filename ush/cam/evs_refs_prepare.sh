#!/bin/ksh
#**************************************************************************
#  Purpose: Prepare required input forecast and validation data files
#           for refs stat jobs
#  Last update: 
#              05/10/2025, Update retart/MPMD, by Binbin Zhou Lynker@EMC/NCEP
#              06/25/2024, add restart by Binbin Zhou Lynker@EMC/NCEP 
#              10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
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
# First check if this task has been completed in the previous run
#    if no, continue this task
#    otherwise, copy all prepbufr nc files from restart directory
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
   if [ -s $ccpadir/*.grib2 ] ; then
    echo completed >$ccpadir/ccpa01h03h.completed
    if [ $SENDCOM = YES ] ; then
     cp $ccpadir/*01h*.grib2 $COMOUTrestart/prepare
     cp $ccpadir/*03h*.grib2 $COMOUTrestart/prepare
     cp $ccpadir/ccpa01h03h.completed $COMOUTrestart/prepare 
    fi 
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
   if [ -s $COMOUTrestart/prepare/ccpa*.*.grib2 ] ; then
    cp  $COMOUTrestart/prepare/ccpa*.*.grib2 $WORK/ccpa.${vday}
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
         ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_obsCCPA24h.conf
         export err=$?; err_chk
         [[ ! -d ${COMOUTsmall}/precip_mean24 ]] && mkdir -p ${COMOUTsmall}/precip_mean24
	 if [ -s ${WORK}/ccpa.${vday}/ccpa24h.t12z.G240.nc ] && [ $SENDCOM = YES ] ; then
           cp ${WORK}/ccpa.${vday}/ccpa24h.t12z.G240.nc ${COMOUTsmall}/precip_mean24
         fi 
	 #For restart:
	 if [ -s $WORK/ccpa.${vday}/*24h*.nc ] ; then
	   echo completed >$WORK/ccpa.${vday}/ccpa24h.completed
	   if [ $SENDCOM = YES ] ; then 
	    cp $WORK/ccpa.${vday}/*24h*.nc  $COMOUTrestart/prepare
            cp $WORK/ccpa.${vday}/ccpa24h.completed $COMOUTrestart/prepare
	   fi
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
    if [ -s $COMOUTrestart/prepare/ccpa24h*.nc ] ; then
      cp  $COMOUTrestart/prepare/ccpa24h*.nc $WORK/ccpa.${vday}
    fi

    #Copy precip_mean24 files from restart directory
    [[ ! -d $COMOUTsmall/precip_mean24 ]] && mkdir $COMOUTsmall/precip_mean24
    if [ -s $COMOUTrestart/prepare/ccpa24h.t12z.G240.nc ] ; then
     cp $COMOUTrestart/prepare/ccpa24h.t12z.G240.nc $COMOUTsmall/precip_mean24
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
   for fhr in 24 30 36 42 48 54 60 ; do
      fcst_time=`$NDATE -$fhr $obsv_vcyc`
      fyyyymmdd=${fcst_time:0:8}
      fcyc=${fcst_time:8:2}
      mkdir -p $WORK/refs.${fyyyymmdd}/${fcyc}
      export modelpath=${COMREFS}/refs.${fyyyymmdd}/${fcyc}/ensprod
      export prod 

      fhr_3=$((fhr-3))
      fhr_3=$((fhr-3))
      fhr_6=$((fhr-6))
      fhr_9=$((fhr-9))
      fhr_12=$((fhr-12))
      fhr_15=$((fhr-15))
      fhr_18=$((fhr-18))
      fhr_21=$((fhr-21))

     for prod in mean avrg pmmn lpmm ; do


      #if [ -s $modelpath/refs.t${fcyc}z.conus.${prod}.f${fhr}.grib2 ] && [ -s $modelpath/refs.t${fcyc}z.conus.${prod}.f${fhr_3}.grib2 ] && [ -s $modelpath/refs.t${fcyc}z.conus.${prod}.f${fhr_6}.grib2 ] && [ -s $modelpath/refs.t${fcyc}z.conus.${prod}.f${fhr_9}.grib2 ] && [ -s $modelpath/refs.t${fcyc}z.conus.${prod}.f${fhr_12}.grib2 ] && [ -s $modelpath/refs.t${fcyc}z.conus.${prod}.f${fhr_15}.grib2 ] && [ -s $modelpath/refs.t${fcyc}z.conus.${prod}.f${fhr_18}.grib2 ] && [ -s $modelpath/refs.t${fcyc}z.conus.${prod}.f${fhr_21}.grib2 ] ; then

      #####################################################################################################################
      # Restart: first check if refs.${fyyyymmdd}/${fcyc}/refs${prod}.t${fcyc}z.G227.24h.f${fhr}.nc exists 
      #    in the $COMOUTrestart directory, if not, run METplus to create it
      #    otherwise, copy it from the $COMOUTrestart directory
      ###################################################################################################################
       if [ ! -s  $COMOUTrestart/prepare/refs${prod}.${fyyyymmdd}.t${fcyc}z.G227.24h.f${fhr}.nc ] ; then
         ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_fcstREFS_APCP24h.conf
         export err=$?; err_chk
	     if [ -s $output_base/refs${prod}.t${fcyc}z.G227.24h.f${fhr}.nc ] ; then
             cp $output_base/refs${prod}.t${fcyc}z.G227.24h.f${fhr}.nc $WORK/refs.${fyyyymmdd}/${fcyc}/.
         if [ $SENDCOM = YES ] ; then
	         [[ ! -d ${COMOUTsmall}/precip_mean24 ]] && mkdir -p ${COMOUTsmall}/precip_mean24
             cp $WORK/refs.${fyyyymmdd}/${fcyc}/refs${prod}.t${fcyc}z.G227.24h.f${fhr}.nc ${COMOUTsmall}/precip_mean24/refs${prod}.${fyyyymmdd}.t${fcyc}z.G227.24h.f${fhr}.nc
	         #Save restart files
	         cp $WORK/refs.${fyyyymmdd}/${fcyc}/refs${prod}.t${fcyc}z.G227.24h.f${fhr}.nc $COMOUTrestart/prepare/refs${prod}.${fyyyymmdd}.t${fcyc}z.G227.24h.f${fhr}.nc
	     fi
         fi
       else
         #Restart: copy restart files to the working directory
	     [[ ! -d $WORK/refs.${fyyyymmdd}/${fcyc} ]] && mkdir -p $WORK/refs.${fyyyymmdd}/${fcyc}
         cp  $COMOUTrestart/prepare/refs${prod}.${fyyyymmdd}.t${fcyc}z.G227.24h.f${fhr}.nc $WORK/refs.${fyyyymmdd}/${fcyc}/refs${prod}.t${fcyc}z.G227.24h.f${fhr}.nc
	     [[ ! -d $COMOUTsmall/precip_mean24 ]] && mkdir $COMOUTsmall/precip_mean24
         if [ -s $COMOUTrestart/prepare/refs${prod}.${fyyyymmdd}.t${fcyc}z.G227.24h.f${fhr}.nc ] ; then
           cp $COMOUTrestart/prepare/refs${prod}.${fyyyymmdd}.t${fcyc}z.G227.24h.f${fhr}.nc $COMOUTsmall/precip_mean24
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
   for fhr in 24 30 36 42 48 54 60 ; do  
      fcst_time=`$NDATE -$fhr $obsv_vcyc`
      fyyyymmdd=${fcst_time:0:8}
      export fcyc=${fcst_time:8:2} #Alaska only has 06 cycle run 
      mkdir -p refs.${fyyyymmdd}/${fcyc}
      export modelpath=${COMREFS}/refs.${fyyyymmdd}/${fcyc}/ensprod
      export prod

      fhr_3=$((fhr-3))
      fhr_3=$((fhr-3))
      fhr_6=$((fhr-6))
      fhr_9=$((fhr-9))
      fhr_12=$((fhr-12))
      fhr_15=$((fhr-15))
      fhr_18=$((fhr-18))
      fhr_21=$((fhr-21))

     for prod in mean avrg pmmn lpmm ; do


      if [ -s $modelpath/refs.t${fcyc}z.${prod}.f${fhr}.ak.grib2 ] && [ -s $modelpath/refs.t${fcyc}z.${prod}.f${fhr_3}.ak.grib2 ] && [ -s $modelpath/refs.t${fcyc}z.${prod}.f${fhr_6}.ak.grib2 ] && [ -s $modelpath/refs.t${fcyc}z.${prod}.f${fhr_9}.ak.grib2 ] && [ -s $modelpath/refs.t${fcyc}z.${prod}.f${fhr_12}.ak.grib2 ] && [ -s $modelpath/refs.t${fcyc}z.${prod}.f${fhr_15}.ak.grib2 ] && [ -s $modelpath/refs.t${fcyc}z.${prod}.f${fhr_18}.ak.grib2 ] && [ -s $modelpath/refs.t${fcyc}z.${prod}.f${fhr_21}.ak.grib2 ] ; then

      #################################################################################################
      # Restart: first check if refs.${fyyyymmdd}/${fcyc}/refs${prod}.t${fcyc}z.G227.24h.f${fhr}.nc exists
      #    in the $COMOUTrestart directory, if not, run METplus to create it
      #    otherwise, copy it from the $COMOUTrestart directory
      ##################################################################################################
      if [ ! -s  $COMOUTrestart/prepare/refs${prod}.${fyyyymmdd}.t${fcyc}z.G255.24h.f${fhr}.nc ] ; then
         ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PRECIP_CONF}/PcpCombine_fcstREFS_APCP24h.conf
         export err=$?; err_chk
         if [ -s $output_base/refs${prod}.t${fcyc}z.G255.24h.f${fhr}.nc ] ; then
            mv $output_base/refs${prod}.t${fcyc}z.G255.24h.f${fhr}.nc $WORK/refs.${fyyyymmdd}/${fcyc}/.
            #Save restart files
	        if [ $SENDCOM = YES ] ; then
              cp $WORK/refs.${fyyyymmdd}/${fcyc}/refs${prod}.t${fcyc}z.G255.24h.f${fhr}.nc $COMOUTrestart/prepare/refs${prod}.${fyyyymmdd}.t${fcyc}z.G255.24h.f${fhr}.nc
	        fi
         fi
      else
         #Restart: copy restart files to the working directory
	     [[ ! -d $WORK/refs.${fyyyymmdd}/${fcyc} ]] && mkdir -p $WORK/refs.${fyyyymmdd}/${fcyc}
         cp  $COMOUTrestart/prepare/refs${prod}.${fyyyymmdd}.t${fcyc}z.G255.24h.f${fhr}.nc $WORK/refs.${fyyyymmdd}/${fcyc}/refs${prod}.t${fcyc}z.G255.24h.f${fhr}.nc
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
   
   if [ "$lvl" = "profile" ] || [ "$VERIF_CASE" = "severe" ] ; then
      cycs="00 12"
   else
      cycs="00 03 06 09 12 15 18 21"
   fi
  
   for vhr in $cycs  ; do
     if [ -s $COMINobsproc/rap.${VDATE}/rap.t${vhr}z.prepbufr.tm00 ] ; then
         for grid in $grids ; do
            export vbeg=${vhr}
            export vend=${vhr}
            export verif_grid=$grid

	    >$WORK/prepbufr.$vday/rap.t${vhr}z.${grid}.prepbufr
	    split_by_subset $COMINobsproc/rap.${VDATE}/rap.t${vhr}z.prepbufr.tm00
            for subset in ADPUPA ADPSFC SFCSHP MSONET ; do
	     if [ -s ${WORK}/${subset} ] ; then
	       cat ${WORK}/${subset} >> $WORK/prepbufr.$vday/rap.t${vhr}z.${grid}.prepbufr
	       rm -f ${WORK}/${subset}
	     fi
	    done

            export bufrpath=$WORK

	    if [ -s $WORK/prepbufr.$vday/rap.t${vhr}z.${grid}.prepbufr ] ; then
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
	    fi 
         done

      if [ -s ${WORK}/pb2nc/prepbufr_nc/*.nc ] ; then
         cp ${WORK}/pb2nc/prepbufr_nc/*.nc $WORK/prepbufr.${vday}
	 #Save restart files 
	 echo completed >${WORK}/pb2nc/prepbufr_nc/rap_prepbufr.completed
	 if [ $SENDCOM = YES ] ; then
           cp ${WORK}/pb2nc/prepbufr_nc/*.nc $COMOUTrestart/prepare
	   cp ${WORK}/pb2nc/prepbufr_nc/rap_prepbufr.completed $COMOUTrestart/prepare
	 fi
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
  done

 else
    #restart: copy restart files to the working directory
    [[ ! -d $WORK/prepbufr.${vday} ]] && mkdir -p $WORK/prepbufr.${vday}
    if [ -s $COMOUTrestart/prepare/*G227*.nc ] ; then
     cp $COMOUTrestart/prepare/*G227*.nc $WORK/prepbufr.${vday}
    fi
    if [ -s $COMOUTrestart/prepare/*G198*.nc ] ; then
     cp $COMOUTrestart/prepare/*G198*.nc $WORK/prepbufr.${vday}
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
if [ "$data" = "gfs_prepbufr" ] ; then

 if [ ! -e $COMOUTrestart/prepare/gfs_prepbufr.completed ] ; then

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

	    >$WORK/prepbufr.$vday/gdas.t${vhr}z.${grid}.prepbufr
	    split_by_subset $COMINobsproc/gdas.${vday}/${vhr}/atmos/gdas.t${vhr}z.prepbufr
	    for subset in ADPUPA ADPSFC SFCSHP MSONET ; do
	     if [ -s ${WORK}/${subset} ] ; then 
	      cat ${WORK}/${subset} >> $WORK/prepbufr.$vday/gdas.t${vhr}z.${grid}.prepbufr
	      rm -f ${WORK}/${subset}
	     fi
	    done
	    export bufrpath=$WORK

	    if [ -s $WORK/prepbufr.$vday/gdas.t${vhr}z.${grid}.prepbufr ] ; then
              ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsGDAS_Prepbufr_refs_profile.conf
              export err=$?; err_chk
	    fi
         done
         if [ -s ${WORK}/pb2nc/prepbufr_nc/*${grid}.nc ] ; then
            cp ${WORK}/pb2nc/prepbufr_nc/*${grid}.nc $WORK/prepbufr.$vday 
         fi
      done

      #For restart
      if [ -s ${WORK}/pb2nc/prepbufr_nc/*.nc ] ; then
	echo completed >${WORK}/pb2nc/prepbufr_nc/gfs_prepbufr.completed
	if [ $SENDCOM = YES ] ; then
         cp ${WORK}/pb2nc/prepbufr_nc/*.nc $COMOUTrestart/prepare
         cp ${WORK}/pb2nc/prepbufr_nc/gfs_prepbufr.completed $COMOUTrestart/prepare
	fi
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
    if [ -s $COMOUTrestart/prepare/*G200*.nc ] ; then
     cp $COMOUTrestart/prepare/*G200*.nc $WORK/prepbufr.${vday}
    fi
    if [ -s $COMOUTrestart/prepare/*G139*.nc ] ; then
     cp $COMOUTrestart/prepare/*G139*.nc $WORK/prepbufr.${vday}
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
 export accum
 if [ -s $DCOMINmrms/MultiSensor_QPE_??H_Pass2_00.00_${vday}-??0000.grib2.gz ] ; then 
    [[ ! -d $COMOUTrestart/prepare ]] && mkdir -p $COMOUTrestart/prepare

    for accum in 01 03 24 ; do

         if [ "$accum" = "03" ] ; then
            cycs="00 03 06 09 12 15 18 21"
         elif [ "$accum" = "24" ] ; then
            cycs="12"
         elif [ "$accum" = "01" ] ; then
            cycs="00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23"
         fi
         export vhr
         export output_base=$WORK/mrms${accum}h
         export mrmsdir=$WORK/mrms.$vday
         mkdir -p $mrmsdir
         cd $mrmsdir

         for vhr in $cycs ; do

	  if [ ! -s $COMOUTrestart/prepare/mrms${accum}h.t${vhr}z.G*.nc ] ; then 
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

	    if [ -s ${output_base}/mrms${accum}h.t${vhr}z.G*.nc ] ; then
	     cp ${output_base}/mrms${accum}h.t${vhr}z.G*.nc $mrmsdir
             #Save for restart
	     if [ $SENDCOM = YES ] ; then
	       cp ${output_base}/mrms${accum}h.t${vhr}z.G*.nc $COMOUTrestart/prepare
	     fi
	    fi

          else
	      #Copy mrms files to working directory
	      cp $COMOUTrestart/prepare/mrms${accum}h.t${vhr}z.G*.nc $WORK/mrms.$vday
          fi	      
       
         done 

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



#*************************************************************************
# Prepare the REFS member files for SFC fields since there 2 TCDC fields
#   but only one is required and METplus is hard to read the specific one.
#   So to retrieve this one TCDC, retrieve all required sfc fields
#************************************************************************
if [ "$data" = "sfc" ] ; then

  [[ ! -d $COMOUTrestart/prepare ]] && mkdir -p $COMOUTrestart/prepare

  cd $DATA/scripts
  echo ">$DATA/pat" 
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

  D2=`$NDATE -48 ${VDATE}00`
  VDATE_2=`echo ${D2} | cut -c 1-8`
  D1=`$NDATE -24 ${VDATE}00`
  VDATE_1=`echo ${D1} | cut -c 1-8`

  >prepare_poe.sh 
  #for day in $PDYm1 $PDYm2 $PDYm3 ; do
  for day in $VDATE $VDATE_1 $VDATE_2 ; do
   work=$DATA/refs.$day/verf_g2g
   mkdir -p $work

   [[ ! -d $COMOUTrestart/prepare/refs.$day/verf_g2g ]] && mkdir -p $COMOUTrestart/prepare/refs.$day/verf_g2g

   for cyc in 00 06 12 18 ; do 
    for domain in conus ak ; do

     >run_prepare.${day}.${cyc}.${domain}.sh

     if [ ! -e $COMOUTrestart/prepare/refs.$day/verf_g2g/run_prepare.${day}.${cyc}.${domain}.completed ] ; then

      echo "#!/bin/ksh" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "set -x" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "work=$work" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "cd \$work">> run_prepare.${day}.${cyc}.${domain}.sh
      echo "for fhr in 3 6 9 12 15 18 21 24 27 30 33 36 39 42 45 48 54 60 ; do" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "    typeset -Z2 hh" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "    hh=\$fhr      " >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "      for mbr in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 ; do" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "        refs=$COMREFS/refs.${day}/${cyc}/verf_g2g/refs.m\${mbr}.t${cyc}z.${domain}.f\${hh}" >> run_prepare.${day}.${cyc}.${domain}.sh
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
      #Save for restart  
      echo "if [ -s \$work/refs.m*.t${cyc}z.${domain}.f* ] ; then" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "  echo completed >\$work/run_prepare.${day}.${cyc}.${domain}.completed" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo " if [ $SENDCOM = YES ] ; then" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "  cp -r \$work/refs.m*.t${cyc}z.${domain}.f* $COMOUTrestart/prepare/refs.$day/verf_g2g" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "  cp $work/run_prepare.${day}.${cyc}.${domain}.completed $COMOUTrestart/prepare/refs.$day/verf_g2g" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo " fi" >> run_prepare.${day}.${cyc}.${domain}.sh
      echo "fi" >> run_prepare.${day}.${cyc}.${domain}.sh 

      chmod +x run_prepare.${day}.${cyc}.${domain}.sh
      echo "${DATA}/scripts/run_prepare.${day}.${cyc}.${domain}.sh" >> run_prepare_poe.sh
 
     else
      #Copy from restart:
       if [ -s $COMOUTrestart/prepare/refs.$day/verf_g2g/refs.m*.t${cyc}z.${domain}.f* ] ; then
         cp $COMOUTrestart/prepare/refs.$day/verf_g2g/refs.m*.t${cyc}z.${domain}.f* $work
       fi
     fi

    done
   done
  done

   if [ -s ${DATA}/scripts/run_prepare_poe.sh ] ; then
     chmod +x ${DATA}/scripts/run_prepare_poe.sh
     mpiexec  -n 24 -ppn 24 --cpu-bind core --depth=2 cfp ${DATA}/scripts/run_prepare_poe.sh
   fi

fi

