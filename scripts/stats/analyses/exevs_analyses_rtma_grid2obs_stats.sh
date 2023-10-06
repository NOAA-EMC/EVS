#/bin/bash

set -x

mkdir -p $DATA/logs
mkdir -p $DATA/stat
export finalstat=$DATA/final
mkdir -p $DATA/final

export regionnest=rtma
export fcstmax=$g2os_sfc_fhr_max

export maskdir=$MASKS

# search to see if obs file exists

obfound=0
fhr="00"

datehr=${VDATE}${cyc}
obday=`echo $datehr |cut -c1-8`
obhr=`echo $datehr |cut -c9-10`

if [ -e $COMINobs/${MODELNAME}.${obday}/${MODELNAME}.t${obhr}z.prepbufr.tm00 ]
then
 obfound=1
else
 export subject="Prepbufr Data Missing for EVS ${COMPONENT}"
 echo "Warning: The ${obday} prepbufr file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
 echo "Missing file is $COMINobs/${MODELNAME}.${obday}/${MODELNAME}.t${obhr}z.prepbufr.tm00" >> mailmsg
 echo "Job ID: $jobid" >> mailmsg
 cat mailmsg | mail -s "$subject" $maillist
fi

echo $obfound


for type in 2dvaranl 2dvarges
do
if [ $type = "2dvaranl" ]
then
	export typtag="_anl"
elif [ $type = "2dvarges" ]
then
	export typtag="_ges"
fi
for modnam in rtma2p5 akrtma prrtma hirtma gurtma
do
export modnam
export outtyp=$type
export OBSDIR=OBS_$modnam

model1=`echo $MODELNAME | tr a-z A-Z`
export model1

if [ $modnam = "rtma2p5" ]
then
	rtmafound=0
	export grid=
        export masks=$maskdir/Bukovsky_RTMA_CONUS.nc,$maskdir/Bukovsky_RTMA_CONUS_East.nc,$maskdir/Bukovsky_RTMA_CONUS_West.nc,$maskdir/Bukovsky_RTMA_CONUS_Central.nc,$maskdir/Bukovsky_RTMA_CONUS_South.nc
	export wexptag="_wexp"
	export restag=""

	if [ $type = "2dvarges" ]
	then
	 fhr="01"
	fi

	if [ -e $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}z.${outtyp}_ndfd.grb2_wexp ]
        then
          rtmafound=1
        else
	 if [ $SENDMAIL = "YES" ]; then
          export subject="CONUS Analysis Missing for EVS ${COMPONENT}"
          echo "Warning: The CONUS Analysis file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
          echo "Missing file is $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}z.${outtyp}_ndfd.grb2_wexp" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $maillist
	 fi
       fi

fi
if [ $modnam = "akrtma" ] 
then
	export grid=
        export masks=$maskdir/Alaska_RTMA.nc
	export wexptag=""
	export restag="_3p0"

	if [ $type = "2dvarges" ]
        then
	 if [ $cyc = 00 -o $cyc = 06 -o $cyc = 09 -o $cyc = 12 -o $cyc = 15 -o $cyc = 18 -o $cyc = 21 ]
         then
	  fhr="03"
	 elif [ $cyc = 01 -o $cyc = 07 -o $cyc = 10 -o $cyc = 13 -o $cyc = 16 -o $cyc = 19 -o $cyc = 22 ]
         then
	  fhr="01"
         elif [ $cyc = 02 -o $cyc = 08 -o $cyc = 11 -o $cyc = 14 -o $cyc = 17 -o $cyc = 20 -o $cyc = 23 ]
	 then
	  fhr="02"
	 fi
	fi

# check for CONUS rtma2p5 file

        rtmafound=0

        if [ -e $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}z.${outtyp}_ndfd.grb2 ]
        then
          rtmafound=1
        else
	 if [ $SENDMAIL = "YES" ]; then
          export subject="Alaska Analysis Missing for EVS ${COMPONENT}"
          echo "Warning: The Alaska Analysis file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
          echo "Missing file is $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}z.${outtyp}_ndfd.grb2" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $maillist
	 fi
        fi

fi
if [ $modnam = "hirtma" ]
then
        export grid=
        export masks=$maskdir/Hawaii_RTMA.nc
	export wexptag=""
	export restag=""

	if [ $type = "2dvarges" ]
	then
	 if [ $cyc = 00 -o $cyc = 06 -o $cyc = 12 -o $cyc = 18 ]
         then
          fhr="06"
	 elif [ $cyc = 01 -o $cyc = 07 -o $cyc = 13 -o $cyc = 19 ]
	 then
	  fhr="07"
	 elif [ $cyc = 02 -o $cyc = 08 -o $cyc = 14 -o $cyc = 20 ]
	 then
	  fhr="02"
	 elif [ $cyc = 03 -o $cyc = 09 -o $cyc = 15 -o $cyc = 21 ]
         then
	  fhr="03"
	 elif [ $cyc = 04 -o $cyc = 10 -o $cyc = 16 -o $cyc = 22 ]
	 then
	  fhr="04"
	 elif [ $cyc = 05 -o $cyc = 11 -o $cyc = 17 -o $cyc = 23 ]
	 then
	  fhr="05"
	 fi
	fi

	# check for CONUS rtma2p5 file

        rtmafound=0

        if [ -e $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}z.${outtyp}_ndfd.grb2 ]
        then    
          rtmafound=1
        else 
	 if [ $SENDMAIL = "YES" ]; then
          export subject="Hawaii Analysis Missing for EVS ${COMPONENT}"
          echo "Warning: The Hawaii Analysis file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
          echo "Missing file is $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}z.${outtyp}_ndfd.grb2" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $maillist	    
	 fi
        fi

fi
if [ $modnam = "prrtma" ]
then
        export grid=
        export masks=$maskdir/Puerto_Rico_RTMA.nc
        export wexptag=""
	export restag=""

	        if [ $type = "2dvarges" ]
	        then
	         if [ $cyc = 00 -o $cyc = 06 -o $cyc = 12 -o $cyc = 18 ]
                 then
                  fhr="06"
                 elif [ $cyc = 01 -o $cyc = 07 -o $cyc = 13 -o $cyc = 19 ]
		 then
                  fhr="07"
                 elif [ $cyc = 02 -o $cyc = 08 -o $cyc = 14 -o $cyc = 20 ]
		 then
                  fhr="02"
                 elif [ $cyc = 03 -o $cyc = 09 -o $cyc = 15 -o $cyc = 21 ]
	         then
                  fhr="03"
                 elif [ $cyc = 04 -o $cyc = 10 -o $cyc = 16 -o $cyc = 22 ]
		 then
                  fhr="04"
                 elif [ $cyc = 05 -o $cyc = 11 -o $cyc = 17 -o $cyc = 23 ]
	         then
                  fhr="05"
                 fi
                fi

	rtmafound=0

        if [ -e $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}z.${outtyp}_ndfd.grb2 ]
        then
          rtmafound=1
        else
	 if [ $SENDMAIL = "YES" ]; then
          export subject="Puerto Rico Analysis Missing for EVS ${COMPONENT}"
          echo "Warning: The Puerto Rico Analysis file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
          echo "Missing file is $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}z.${outtyp}_ndfd.grb2" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $maillist
	 fi
        fi

fi

if [ $modnam = "gurtma" ]
then 
   export grid=
   export masks=$maskdir/Guam_RTMA.nc
   export wexptag=""
   export restag=""
   rtmafound=0 

   if [ $type = "2dvarges" ]
   then
    if [ $cyc = 00 -o $cyc = 12 ]
    then
     fhr="12"
    elif [ $cyc = 01 -o $cyc = 13 ]
    then
     fhr="13"
    elif [ $cyc = 02 -o $cyc = 14 ]
    then
     fhr="14"
    elif [ $cyc = 03 -o $cyc = 15 ]
    then
     fhr="15"
    elif [ $cyc = 04 -o $cyc = 16 ]
    then
     fhr="16"
    elif [ $cyc = 05 -o $cyc = 17 ]
    then
     fhr="17"
    elif [ $cyc = 06 -o $cyc = 18 ]
    then
     fhr="06"
    elif [ $cyc = 07 -o $cyc = 19 ]
    then
     fhr="07"
    elif [ $cyc = 08 -o $cyc = 20 ]
    then
     fhr="08"
    elif [ $cyc = 09 -o $cyc = 21 ]
    then
     fhr="09"
    elif [ $cyc = 10 -o $cyc = 22 ]
    then
     fhr="10"
    elif [ $cyc = 11 -o $cyc = 23 ]
    then
     fhr="11"
    fi
   fi
					 
   if [ -s $COMINobs/urma.${obday}/urma.t${obhr}z.prepbufr.tm00 ]
   then 
      obfound=1
   else
    if [ $SENDMAIL = "YES" ]; then
      export subject="Guam Prepbufr Data Missing for EVS ${COMPONENT}"
      echo "Warning: The ${obday} prepbufr file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
      echo "Missing file is $COMINobs/urma.${obday}/urma.t${obhr}z.prepbufr.tm00" >> mailmsg
      echo "Job ID: $jobid" >> mailmsg
      cat mailmsg | mail -s "$subject" $maillist
    fi
   fi
   
   if [ -s $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}z.${outtyp}_ndfd.grb2 ]
   then
     rtmafound=1
   else
    if [ $SENDMAIL = "YES" ]; then
     export subject="Guam Analysis Missing for EVS ${COMPONENT}"
     echo "Warning: The Guam Analysis file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
     echo "Missing file is $COMINfcst/${modnam}.${VDATE}/${modnam}.t${cyc}z.${outtyp}_ndfd.grb2" >> mailmsg
     echo "Job ID: $jobid" >> mailmsg
     cat mailmsg | mail -s "$subject" $maillist
    fi
   fi
fi

if [ ! -e $COMOUTsmall/point_stat_${modnam}${typtag}_${fhr}0000L_${VDATE}_${cyc}0000V.stat ]
then
if [ $rtmafound -eq 1 -a $obfound -eq 1 ]
then
run_metplus.py $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/PointStat_fcstANALYSES_obsNDAS_PrepBufr.conf $PARMevs/metplus_config/machine.conf
export err=$?; err_chk

mkdir -p $COMOUTsmall
if [ $SENDCOM = "YES" ]; then
 cp $DATA/point_stat/${modnam}${typtag}/* $COMOUTsmall
fi
else
echo "NO RTMA OR OBS DATA, METplus will not run"
echo "RTMAFOUND, OBFOUND", $rtmafound, $obfound
fi
else
  echo "RESTART - $COMOUTsmall/point_stat_${modnam}${typtag}_${fhr}_${VDATE}_${cyc}0000V.stat exists"
fi


done

if [ $cyc = 23 -a $rtmafound -eq 1 -a $obfound -eq 1 ]
then
       mkdir -p $COMOUTfinal
       cp $COMOUTsmall/*${regionnest}*${typtag}* $finalstat
       cd $finalstat
       run_metplus.py $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/StatAnalysis_fcstANALYSES_obsNDAS_GatherByDay.conf $PARMevs/metplus_config/machine.conf
       export err=$?; err_chk
       if [ $SENDCOM = "YES" ]; then
         cp $finalstat/evs.stats.${regionnest}${typtag}.${RUN}.${VERIF_CASE}.v${VDATE}.stat $COMOUTfinal
       fi
else    
       echo "NO RTMA OR OBS DATA, or not gather time yet, METplus gather job will not run"
fi

done

exit

