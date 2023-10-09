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

datehr=${VDATE}${vhr}
obday=`echo $datehr |cut -c1-8`
obhr=`echo $datehr |cut -c9-10`

if [ -e $COMINobsproc/${MODELNAME}.${obday}/${MODELNAME}.t${obhr}z.prepbufr.tm00 ]
then
 obfound=1
else
 export subject="Prepbufr Data Missing for EVS ${COMPONENT}"
 echo "Warning: The ${obday} prepbufr file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
 echo "Missing file is $COMINobsproc/${MODELNAME}.${obday}/${MODELNAME}.t${obhr}z.prepbufr.tm00" >> mailmsg
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

	if [ -e $COMINanl/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2_wexp ]
        then
          rtmafound=1
        else
	 if [ $SENDMAIL = "YES" ]; then
          export subject="CONUS Analysis Missing for EVS ${COMPONENT}"
          echo "Warning: The CONUS Analysis file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
          echo "Missing file is $COMINanl/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2_wexp" >> mailmsg
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
	 if [ $vhr = 00 -o $vhr = 06 -o $vhr = 09 -o $vhr = 12 -o $vhr = 15 -o $vhr = 18 -o $vhr = 21 ]
         then
	  fhr="03"
	 elif [ $vhr = 01 -o $vhr = 07 -o $vhr = 10 -o $vhr = 13 -o $vhr = 16 -o $vhr = 19 -o $vhr = 22 ]
         then
	  fhr="01"
         elif [ $vhr = 02 -o $vhr = 08 -o $vhr = 11 -o $vhr = 14 -o $vhr = 17 -o $vhr = 20 -o $vhr = 23 ]
	 then
	  fhr="02"
	 fi
	fi

# check for CONUS rtma2p5 file

        rtmafound=0

        if [ -e $COMINanl/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2 ]
        then
          rtmafound=1
        else
	 if [ $SENDMAIL = "YES" ]; then
          export subject="Alaska Analysis Missing for EVS ${COMPONENT}"
          echo "Warning: The Alaska Analysis file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
          echo "Missing file is $COMINanl/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2" >> mailmsg
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
	 if [ $vhr = 00 -o $vhr = 06 -o $vhr = 12 -o $vhr = 18 ]
         then
          fhr="06"
	 elif [ $vhr = 01 -o $vhr = 07 -o $vhr = 13 -o $vhr = 19 ]
	 then
	  fhr="07"
	 elif [ $vhr = 02 -o $vhr = 08 -o $vhr = 14 -o $vhr = 20 ]
	 then
	  fhr="02"
	 elif [ $vhr = 03 -o $vhr = 09 -o $vhr = 15 -o $vhr = 21 ]
         then
	  fhr="03"
	 elif [ $vhr = 04 -o $vhr = 10 -o $vhr = 16 -o $vhr = 22 ]
	 then
	  fhr="04"
	 elif [ $vhr = 05 -o $vhr = 11 -o $vhr = 17 -o $vhr = 23 ]
	 then
	  fhr="05"
	 fi
	fi

	# check for CONUS rtma2p5 file

        rtmafound=0

        if [ -e $COMINanl/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2 ]
        then    
          rtmafound=1
        else 
	 if [ $SENDMAIL = "YES" ]; then
          export subject="Hawaii Analysis Missing for EVS ${COMPONENT}"
          echo "Warning: The Hawaii Analysis file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
          echo "Missing file is $COMINanl/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2" >> mailmsg
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
	         if [ $vhr = 00 -o $vhr = 06 -o $vhr = 12 -o $vhr = 18 ]
                 then
                  fhr="06"
                 elif [ $vhr = 01 -o $vhr = 07 -o $vhr = 13 -o $vhr = 19 ]
		 then
                  fhr="07"
                 elif [ $vhr = 02 -o $vhr = 08 -o $vhr = 14 -o $vhr = 20 ]
		 then
                  fhr="02"
                 elif [ $vhr = 03 -o $vhr = 09 -o $vhr = 15 -o $vhr = 21 ]
	         then
                  fhr="03"
                 elif [ $vhr = 04 -o $vhr = 10 -o $vhr = 16 -o $vhr = 22 ]
		 then
                  fhr="04"
                 elif [ $vhr = 05 -o $vhr = 11 -o $vhr = 17 -o $vhr = 23 ]
	         then
                  fhr="05"
                 fi
                fi

	rtmafound=0

        if [ -e $COMINanl/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2 ]
        then
          rtmafound=1
        else
	 if [ $SENDMAIL = "YES" ]; then
          export subject="Puerto Rico Analysis Missing for EVS ${COMPONENT}"
          echo "Warning: The Puerto Rico Analysis file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
          echo "Missing file is $COMINanl/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2" >> mailmsg
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
    if [ $vhr = 00 -o $vhr = 12 ]
    then
     fhr="12"
    elif [ $vhr = 01 -o $vhr = 13 ]
    then
     fhr="13"
    elif [ $vhr = 02 -o $vhr = 14 ]
    then
     fhr="14"
    elif [ $vhr = 03 -o $vhr = 15 ]
    then
     fhr="15"
    elif [ $vhr = 04 -o $vhr = 16 ]
    then
     fhr="16"
    elif [ $vhr = 05 -o $vhr = 17 ]
    then
     fhr="17"
    elif [ $vhr = 06 -o $vhr = 18 ]
    then
     fhr="06"
    elif [ $vhr = 07 -o $vhr = 19 ]
    then
     fhr="07"
    elif [ $vhr = 08 -o $vhr = 20 ]
    then
     fhr="08"
    elif [ $vhr = 09 -o $vhr = 21 ]
    then
     fhr="09"
    elif [ $vhr = 10 -o $vhr = 22 ]
    then
     fhr="10"
    elif [ $vhr = 11 -o $vhr = 23 ]
    then
     fhr="11"
    fi
   fi
					 
   if [ -s $COMINobsproc/urma.${obday}/urma.t${obhr}z.prepbufr.tm00 ]
   then 
      obfound=1
   else
    if [ $SENDMAIL = "YES" ]; then
      export subject="Guam Prepbufr Data Missing for EVS ${COMPONENT}"
      echo "Warning: The ${obday} prepbufr file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
      echo "Missing file is $COMINobsproc/urma.${obday}/urma.t${obhr}z.prepbufr.tm00" >> mailmsg
      echo "Job ID: $jobid" >> mailmsg
      cat mailmsg | mail -s "$subject" $maillist
    fi
   fi
   
   if [ -s $COMINanl/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2 ]
   then
     rtmafound=1
   else
    if [ $SENDMAIL = "YES" ]; then
     export subject="Guam Analysis Missing for EVS ${COMPONENT}"
     echo "Warning: The Guam Analysis file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
     echo "Missing file is $COMINanl/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2" >> mailmsg
     echo "Job ID: $jobid" >> mailmsg
     cat mailmsg | mail -s "$subject" $maillist
    fi
   fi
fi

if [ ! -e $COMOUTsmall/point_stat_${modnam}${typtag}_${fhr}0000L_${VDATE}_${vhr}0000V.stat ]
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
  echo "RESTART - $COMOUTsmall/point_stat_${modnam}${typtag}_${fhr}_${VDATE}_${vhr}0000V.stat exists"
fi


done

if [ $vhr = 23 -a $rtmafound -eq 1 -a $obfound -eq 1 ]
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

