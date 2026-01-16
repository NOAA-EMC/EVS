#!/bin/ksh
#**************************************************************************
#  Purpose: check the required input forecast and validation data files
#           for refs stat jobs
#  Last update: 10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
#************************************************************************
set -x

vday=$VDATE

typeset -Z2 vhr

if [ $VERIF_CASE = grid2obs ] || [ $VERIF_CASE = spcoutlook ] ; then
   echo "Checking prepbufr files...." 
   
   missing=0 
   for vhr in 00 01 02 03 04 05 06 07 08  09 10 11 12 13 14 15 16 17 18 19 20  21 22 23 ; do
      if [ ! -s $COMINobsproc/rap.${vday}/rap.t${vhr}z.prepbufr.tm00 ] ; then
         missing=$((missing + 1 ))
         echo  "WARNING: $COMINobsproc/rap.${vday}/rap.t${vhr}z.prepbufr.tm00 is missing"
      fi
   done
   echo "Missing prepbufr files = " $missing
   if [ $missing -eq 24  ] ; then
      echo "WARNING: All of the RAP prepbufr files are missing for EVS ${COMPONENT}"
      export verif_all=no
      >$DATA/verif_all.no
      if [ "$SENDMAIL" = "YES" ] ; then
	 export subject="RAP Prepbufr Data Missing for EVS ${COMPONENT}"
	 echo "WARNING:  No RAP Prepbufr data available for ${vday}" > mailmsg
	 echo "All of  $COMINobsproc/rap.${vday}/rap.txxz.prepbufr.tm00" files are missing >> mailmsg
	 echo "Job ID: $jobid" >> mailmsg
	 cat mailmsg | mail -s "$subject" $MAILTO
       fi
   fi

fi


if [ $VERIF_CASE = precip ] ; then
   echo "Checking precip files...." 

   next=`$NDATE +24 ${vday}12 |cut -c 1-8`
   prev=`$NDATE -24 ${vday}12 |cut -c 1-8`
   missing=0
   for vhr in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 ; do
      if [ $vhr = 00 ] ; then
         cyc_dir=00
         init=$vday
      elif [ $vhr = 01 02 03 04 05 06  ] || [ $vhr = 06 ] ; then
         cyc_dir=06
         init=$vday
      elif [ $vhr = 07 08 09 10 11 12  ] || [ $vhr = 12 ] ; then
         cyc_dir=12
         init=$vday
      elif [ $vhr = 13 14 15 16 17 18 ] || [ $vhr = 18 ] ; then
         cyc_dir=18
         init=$vday
      elif [ $vhr = 19 20 21 22 23 ] ; then
         cyc_dir=00
         init=$next
      fi	      
      ccpa=$COMINccpa/ccpa.${init}/${cyc_dir}/ccpa.t${vhr}z.01h.hrap.conus.gb2
      if [ ! -s $ccpa ] ; then
         missing=$((missing + 1 ))
         echo "WARNING: $ccpa is missing"
      fi
   done
   echo "Missing ccpa01h files = " $missing
   if [ $missing -eq 24  ] ; then
      echo "WARNING: All of the ccpa01h files are missing for EVS ${COMPONENT}"
      export verif_precip=no
      >$DATA/verif_precip.no
      if [ "$SENDMAIL" = "YES" ] ; then
	  export subject="CCPA_01h Data Missing for EVS ${COMPONENT}"
	  echo "WARNING:  No CCPA_01h data available for ${vday}" > mailmsg
	  echo "All of $COMINccpa/ccpa.${vday}/cycle/ccpa.txxz.01h.hrap.conus.gb2 are missing" >> mailmsg
	  echo "Job ID: $jobid" >> mailmsg
	  cat mailmsg | mail -s "$subject" $MAILTO
      fi

   fi                 

   missing=0
   for vhr in 00 03 06 09 12 15 18 21 ; do
      if [ $vhr = 00 ] ; then
         cyc_dir=00
         init=$vday
      elif [ $vhr = 03 06  ] || [ $vhr = 06 ] ; then
         cyc_dir=06
         init=$vday
      elif [ $vhr = 09 12  ] || [ $vhr = 12 ] ; then
         cyc_dir=12
         init=$vday
      elif [ $vhr = 15 18 ] || [ $vhr = 18 ] ; then
         cyc_dir=18
         init=$vday
      elif [ $vhr = 21 ] ; then
         cyc_dir=00
         init=$next
      fi
      ccpa=$COMINccpa/ccpa.${init}/${cyc_dir}/ccpa.t${vhr}z.03h.hrap.conus.gb2
      if [ ! -s $ccpa ] ; then
         missing=$((missing + 1 ))
	     echo "WARNING: $ccpa is missing"
      fi
   done
   echo "Missing ccpa03h files = " $missing
   if [ $missing -eq 8  ] ; then
      echo "WARNING: All of the ccpa03h files are missing for EVS ${COMPONENT}"
      export verif_precip=no
      >$DATA/verif_precip.no
      if [ "$SENDMAIL" = "YES" ] ; then
          export subject="CCPA_03h Data Missing for EVS ${COMPONENT}"
          echo "WARNING:  No CCPA_03h data available for ${VDATE}" > mailmsg
          echo "All of $COMINccpa/ccpa.${vday}/cycle/ccpa.txxz.03h.hrap.conus.gb2 are missing" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
      fi

   fi

   missing=0
   for vhr in 12 ; do
      if [ ! -s $COMINccpa/ccpa.${vday}/12/ccpa.t12z.06h.hrap.conus.gb2 ] ; then
         missing=$((missing+1))
         echo "WARNING: $COMINccpa/ccpa.${vday}/12/ccpa.t12z.06h.hrap.conus.gb2 is missing"
      elif [ ! -s $COMINccpa/ccpa.${vday}/06/ccpa.t06z.06h.hrap.conus.gb2 ] ; then
         missing=$((missing+1))
         echo "WARNING: $COMINccpa/ccpa.${vday}/06/ccpa.t06z.06h.hrap.conus.gb2 is missing"
      elif [ ! -s $COMINccpa/ccpa.${vday}/00/ccpa.t00z.06h.hrap.conus.gb2 ] ; then
         missing=$((missing+1))
         echo "WARNING: $COMINccpa/ccpa.${vday}/00/ccpa.t00z.06h.hrap.conus.gb2 is missing"
      elif [ ! -s $COMINccpa/ccpa.${prev}/18/ccpa.t18z.06h.hrap.conus.gb2 ] ; then
         missing=$((missing+1))
         echo "WARNING: $COMINccpa/ccpa.${prev}/18/ccpa.t18z.06h.hrap.conus.gb2 is missing"
      fi
   done
   echo "Missing ccpa06h files = " $missing
   if [ $missing -ge 1  ] ; then
      echo "WARNING: At least one of the ccpa06h files are missing for EVS ${COMPONENT}"
      export verif_precip=no
      >$DATA/verif_precip.no

      if [ "$SENDMAIL" = "YES" ] ; then
          export subject="CCPA_06h Data Missing for EVS ${COMPONENT}"
          echo "WARNING:  No CCPA_06h data available for ${vday}" > mailmsg
          echo "All of $COMINccpa/ccpa.${vday}/cycle/ccpa.txxz.06h.hrap.conus.gb2 are missing" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
      fi

   fi

   accum=01
   missing=0
   for vhr in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 ; do
      mrms=$DCOMINmrms/MultiSensor_QPE_${accum}H_Pass2_00.00_${vday}-${vhr}0000.grib2.gz
      if [ ! -s $mrms ] ; then
         missing=$((missing+1))
         echo "WARNING: $mrms is missing"
      fi
   done
   echo "Missing mrms01h files = " $missing
   if [ $missing -eq 24  ] ; then
      echo "WARNING: All of mrms01h files are missing for EVS ${COMPONENT}"
      export verif_precip=no
      >$DATA/verif_precip.no

      if [ "$SENDMAIL" = "YES" ] ; then
          export subject="MRMS_01h Data Missing for EVS ${COMPONENT}"
          echo "WARNING:  No MRMS_01h data available for ${vday}" > mailmsg
          echo "All of $DCOMINmrms/MultiSensor_QPE_${accum}H_Pass2_00.00_${vday}-vhr0000.grib2.gz are missing" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
      fi

   fi

   accum=03
   missing=0
   for vhr in 00 03 06 09 12 15 18 21 ; do
      mrms=$DCOMINmrms/MultiSensor_QPE_${accum}H_Pass2_00.00_${vday}-${vhr}0000.grib2.gz
      if [ ! -s $mrms ] ; then
         missing=$((missing+1))
         echo "WARNING: $mrms is missing"
      fi
   done
   echo "Missing mrms03h files = " $missing
   if [ $missing -eq 8  ] ; then
      echo "WARNING: All of mrms03h files are missing for EVS ${COMPONENT}"
      export verif_precip=no
      >$DATA/verif_precip.no

      if [ "$SENDMAIL" = "YES" ] ; then
          export subject="MRMS_03h Data Missing for EVS ${COMPONENT}"
          echo "WARNING:  No MRMS_03h data available for ${vday}" > mailmsg
          echo "All of $DCOMINmrms/MultiSensor_QPE_${accum}H_Pass2_00.00_${vday}-vhr0000.grib2.gz are missing" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
      fi

   fi

   accum=24
   missing=0
   for vhr in 00 06 12 18 ; do
      mrms=$DCOMINmrms/MultiSensor_QPE_${accum}H_Pass2_00.00_${vday}-${vhr}0000.grib2.gz
      if [ ! -s $mrms ] ; then
         missing=$((missing+1))
         echo "WARNING: $mrms is missing"
      fi
   done
   echo "Missing mrms24h files = " $missing
   if [ $missing -eq 4  ] ; then
      echo "WARNING: All of the mrms24h files are missing for EVS ${COMPONENT}"   
      export verif_precip=no
      >$DATA/verif_precip.no

      if [ "$SENDMAIL" = "YES" ] ; then
          export subject="MRMS_24h Data Missing for EVS ${COMPONENT}"
          echo "WARNING:  No MRMS_24h data available for ${vday}" > mailmsg
          echo "All of $DCOMINmrms/MultiSensor_QPE_${accum}H_Pass2_00.00_${vday}-vhr0000.grib2.gz are missing" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
      fi

   fi
fi

