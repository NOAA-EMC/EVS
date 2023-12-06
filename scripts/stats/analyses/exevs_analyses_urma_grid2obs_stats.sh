#/bin/bash

##################################################################################
# Name of Script: exevs_analyses_urma_grid2obs_stats.sh
# Contact(s):     Perry C. Shafran (perry.shafran@noaa.gov)
# Purpose of Script: This script runs METplus to generate 
#                    verification statistics for urma analyses and first guess
##################################################################################

set -x

# Set up initial directories and initialize variables

mkdir -p $DATA/logs
mkdir -p $DATA/stat
export finalstat=$DATA/final
mkdir -p $DATA/final

export regionnest=urma
export fcstmax=$g2os_sfc_fhr_max

export dirin=$COMINurma

export maskdir=$MASKS

# Search for obs Prepbufr file

obfound=0
fhr="00"

datehr=${VDATE}${vhr}
obday=`echo $datehr |cut -c1-8`
obhr=`echo $datehr |cut -c9-10`

if [ -e $COMINobsproc/${MODELNAME}.${obday}/${MODELNAME}.t${obhr}z.prepbufr.tm00 ]
then
 obfound=1
else
 echo "WARNING: $COMINobsproc/${MODELNAME}.${obday}/${MODELNAME}.t${obhr}z.prepbufr.tm00 is missing, METplus will not run"
 if [ $SENDMAIL = "YES" ]; then
  export subject="Prepbufr Data Missing for EVS ${COMPONENT}"
  echo "Warning: The ${obday} prepbufr file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
  echo "Missing file is $COMINobsproc/${MODELNAME}.${obday}/${MODELNAME}.t${obhr}z.prepbufr.tm00" >> mailmsg
  echo "Job ID: $jobid" >> mailmsg
  cat mailmsg | mail -s "$subject" $MAILTO
 fi
fi

echo $obfound

# Search for analysis (2dvaranl) or first guess (2dvarges) file

for type in 2dvaranl 2dvarges
do
if [ $type = "2dvaranl" ]
then
	export typtag="_anl"
elif [ $type = "2dvarges" ]
then
	export typtag="_ges"
fi
for modnam in urma2p5 akurma prurma hiurma 
do
export modnam
export outtyp=$type
export OBSDIR=OBS_$modnam

model1=`echo $MODELNAME | tr a-z A-Z`
export model1

if [ $modnam = "urma2p5" ]
then
	urmafound=0
	export grid=
        export masks=$maskdir/Bukovsky_RTMA_CONUS.nc,$maskdir/Bukovsky_RTMA_CONUS_East.nc,$maskdir/Bukovsky_RTMA_CONUS_West.nc,$maskdir/Bukovsky_RTMA_CONUS_Central.nc,$maskdir/Bukovsky_RTMA_CONUS_South.nc
	export wexptag="_wexp"
	export restag=""

	if [ $type = "2dvarges" ]
	then
	 fhr="01"
	fi

# Check for CONUS urma file

	if [ -e $COMINurma/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2_wexp ]
        then
          urmafound=1
        else
	 echo "WARNING: $COMINurma/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2_wexp is missing, METplus will not run"
	 if [ $SENDMAIL = "YES" ]; then
          export subject="CONUS Analysis Missing for EVS ${COMPONENT}"
          echo "Warning: The CONUS Analysis file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
          echo "Missing file is $COMINurma/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2_wexp" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
	 fi
       fi

fi
if [ $modnam = "akurma" ] 
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

# check for Alaska urma file

        urmafound=0

        if [ -e $COMINurma/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2 ]
        then
          urmafound=1
        else
	 echo "WARNING: $COMINurma/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2 is missing; METplus will not run"
         if [ $SENDMAIL = "YES" ]; then		
          export subject="Alaska Analysis Missing for EVS ${COMPONENT}"
          echo "Warning: The Alaska Analysis file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
          echo "Missing file is $COMINurma/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
	 fi
        fi

fi
if [ $modnam = "hiurma" ]
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
	  fhr="01"
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

	# check for Hawaii urma file

        urmafound=0

        if [ -e $COMINurma/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2 ]
        then    
          urmafound=1
        else 
	 echo "WARNING: $COMINurma/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2 is missing; METplus will not run"
	 if [ $SENDMAIL = "YES" ]; then
          export subject="Hawaii Analysis Missing for EVS ${COMPONENT}"
          echo "Warning: The Hawaii Analysis file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
          echo "Missing file is $COMINurma/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO	    
	 fi
        fi

fi
if [ $modnam = "prurma" ]
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
                  fhr="01"
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

	urmafound=0

# Check for Puerto Rico urma file

        if [ -e $COMINurma/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2 ]
        then
          urmafound=1
        else
	 echo "WARNING: $COMINurma/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2 is missing; METplus will not run"
	 if [ $SENDMAIL = "YES" ]; then
          export subject="Puerto Rico Analysis Missing for EVS ${COMPONENT}"
          echo "Warning: The Puerto Rico Analysis file is missing for valid date ${VDATE}. METplus will not run." > mailmsg
          echo "Missing file is $COMINurma/${modnam}.${VDATE}/${modnam}.t${vhr}z.${outtyp}_ndfd.grb2" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
	 fi
        fi

fi

# Run METplus for urma vs obs

if [ ! -e $COMOUTsmall/point_stat_${modnam}${typtag}_${fhr}0000L_${VDATE}_${vhr}0000V.stat ]
then
if [ $urmafound -eq 1 -a $obfound -eq 1 ]
then
run_metplus.py $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/PointStat_fcstANALYSES_obsNDAS_PrepBufr.conf $PARMevs/metplus_config/machine.conf
export err=$?; err_chk

mkdir -p $COMOUTsmall
if [ $SENDCOM = "YES" ]; then
 cp $DATA/point_stat/${modnam}${typtag}/* $COMOUTsmall
fi
else
echo "WARNING: NO URMA OR OBS DATA, METplus will not run"
echo "WARNING: URMAFOUND, OBFOUND", $urmafound, $obfound
fi
else
  echo "RESTART - $COMOUTsmall/point_stat_${modnam}${typtag}_${fhr}_${VDATE}_${vhr}0000V.stat exists"
fi

done

# Run StatAnalysis to generate final stat file

if [ $vhr = 23 -a $urmafound -eq 1 -a $obfound -eq 1 ]
then
       mkdir -p $COMOUTfinal
       cp $COMOUTsmall/*${regionnest}*${typtag}* $finalstat
       cd $finalstat
       run_metplus.py $PARMevs/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/StatAnalysis_fcstANALYSES_obsNDAS_GatherByDay.conf $PARMevs/metplus_config/machine.conf
       export err=$?; err_chk
       if [ $SENDCOM = "YES" ]; then
	 cpreq -v $finalstat/evs.stats.${regionnest}${typtag}.${RUN}.${VERIF_CASE}.v${VDATE}.stat $COMOUTfinal
       fi
else    
       echo "WARNING: NO URMA OR OBS DATA, or not gather time yet, METplus gather job will not run"
fi

log_dir="$DATA/logs/${MODELNAME}${typtag}"
if [ -d $log_dir ]; then
  log_file_count=$(find $log_dir -type f | wc -l)
  if [[ $log_file_count -ne 0 ]]; then
      log_files=("$log_dir"/*)
      for log_file in "${log_files[@]}"; do
        if [ -f "$log_file" ]; then
           echo "Start: $log_file"
           cat "$log_file"
           echo "End: $log_file"
        fi
     done
   fi
fi

done

exit

