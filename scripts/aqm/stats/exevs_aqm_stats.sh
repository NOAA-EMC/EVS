set -x

mkdir -p $DATA/logs
mkdir -p $DATA/stat

export OBSDIR=OBS
export modnam=cs
export fcstmax=72

export MASK_DIR=/lfs/h2/emc/vpppg/noscrub/logan.dawson/CAM_verif/masks/Bukovsky_CONUS/EVS_fix

export model1=`echo $MODELNAME | tr a-z A-Z`
echo $model1

# Begin verification of both the hourly data of ozone and PM

o3found=0
pmfound=0

for outtyp in awpozcon pm25
do

# Checks for observation files

 if [ $outtyp = "awpozcon" ]
 then
  if [ -e $COMINobs/hourly.${VDATE}/aqm.t12z.prepbufr.tm00 ]
  then
   o3found=1
  fi
 fi
 if [ $outtyp = "pm25" ]
 then
  if [ -e $COMINobs/hourly.${PDYm2}/aqm.t12z.anowpm.pb.tm024 ]
  then
   pmfound=1
  fi
 fi
 echo "o3found,pmfound=", $o3found, $pmfound

# Verification to be done both on raw output files and bias-corrected files

  for biastyp in raw bc
  do

    export outtyp
    export biastyp
    echo $biastyp

    if [ $biastyp = "raw" ]
    then
      export bctag=
      export bcout=_raw
    fi

    if [ $biastyp = "bc" ]
    then
      export bctag=_bc
      export bcout=_bc
    fi

# check to see that model files exist, and list which forecast hours are to be used

    fhr=0
    numo3fcst=0
    numpmfcst=0
    while [ $fhr -le $fcstmax ]
    do
      if [ $fhr -lt 10 ]
      then
        fhr=0$fhr
      fi
      export fhr

      export datehr=${VDATE}${cyc}
      adate=`$NDATE -$fhr $datehr`
      aday=`echo $adate |cut -c1-8`
      acyc=`echo $adate |cut -c9-10`
      if [ $acyc = 06 -o $acyc = 12 ]
      then
      if [ -e $COMINaqm/cs.${aday}/aqm.t${acyc}z.awpozcon${bctag}.f${fhr}.148.grib2 ]
      then
        echo "$fhr found"
        echo $fhr >> $DATA/fcstlist_o3
        let "numo3fcst=numo3fcst+1"
      fi 
      if [ -e $COMINaqm/cs.${aday}/aqm.t${acyc}z.pm25${bctag}.f${fhr}.148.grib2 ]
      then
        echo "$fhr found"
        echo $fhr >> $DATA/fcstlist_pm
        let "numpmfcst=numpmfcst+1"
      fi

      fi
      let "fhr=fhr+1"
    done
    export fcsthours_o3=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' $DATA/fcstlist_o3`
    export fcsthours_pm=`awk -v d=", " '{s=(NR==1?s:s d)$0}END{print s}' $DATA/fcstlist_pm`
    export numo3fcst
    export numpmfcst
    rm $DATA/fcstlist_o3 $DATA/fcstlist_pm
    echo "numo3fcst,numpmfcst", $numo3fcst, $numpmfcst

    case $outtyp in

        awpozcon) if [ $numo3fcst -gt 0 -a $o3found -eq 1 ]
                  then
                  export fcsthours=$fcsthours_o3
                  run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PointStat_fcstOZONE_obsAIRNOW.conf $PARMevs/metplus_config/machine.conf
                  export err=$?; err_chk
                  mkdir -p $COMOUTsmall
                  cp $DATA/point_stat/$MODELNAME/* $COMOUTsmall
                  if [ $cyc = 23 ]
                  then
                    mkdir -p $COMOUTfinal
                    run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/StatAnalysis_fcstOZONE_obsAIRNOW_GatherByDay.conf $PARMevs/metplus_config/machine.conf
                    export err=$?; err_chk
                  fi
                  else
                  echo "NO O3 FORECAST OR OBS TO VERIFY"
                  echo "NUM FCST, NUM OBS", $numo3fcst, $o3found
                  fi
                  ;;
      pm25) if [ $numpmfcst -gt 0 -a $pmfound -eq 1 ]
            then
            export fcsthours=$fcsthours_pm
            run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PointStat_fcstPM2p5_obsAIRNOW.conf $PARMevs/metplus_config/machine.conf
            export err=$?; err_chk
            mkdir -p $COMOUTsmall
            cp $DATA/point_stat/$MODELNAME/* $COMOUTsmall
            if [ $cyc = 23 ]
            then
               mkdir -p $COMOUTfinal
               run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/StatAnalysis_fcstPM_obsANOWPM_GatherByDay.conf $PARMevs/metplus_config/machine.conf
               export err=$?; err_chk
            fi
            else
            echo "NO PM FORECAST OR OBS TO VERIFY"
            echo "NUM FCST, NUM OBS", $numpmfcst, $pmfound
            fi
            ;;
    esac

  done

done

# Daily verification of the daily maximum of 8-hr ozone
# Verification being done on both raw and bias-corrected output data

if [ $cyc = 11 ]
then

  export OBSDIR=OBSMAX

  for biastyp in raw bc
  do

    export biastyp
    echo $biastyp

    if [ $biastyp = "raw" ]
    then
      export bctag=
      export bcout=_raw
    fi

    if [ $biastyp = "bc" ]
    then
      export bctag=_bc
      export bcout=_bc
    fi

    for hour in 06 12
    do

      export hour

#  search for model file and 2nd obs file for the daily 8-hr ozone max

      ozmax8=0
      ozobs2=0
      if [ -e $COMINaqmproc/atmos.${VDATE}/aqm/aqm.t${hour}z.max_8hr_o3${bctag}.148.grib2 ]
      then
        ozmax8=1
      fi
      if [ -e $COMINaqmproc/atmos.${PDYm4}/aqm/aqm.t${hour}z.max_8hr_o3${bctag}.148.grib2 ]
      then
       let "ozmax8=ozmax8+1"
      fi
      if [ -e $COMINaqmproc/atmos.${PDYm5}/aqm/aqm.t${hour}z.max_8hr_o3${bctag}.148.grib2 ]
      then
        let "ozmax8=ozmax8+1"
      fi
      if [ -e $COMINobs/hourly.${PDYm2}/aqm.t12z.prepbufr.tm00 ]
      then
       ozobs2=1
      fi
      echo "ozmax8, ozobs2=",$ozmax8,$ozobs2
      if [ $ozmax8 -gt 0 -a $ozobs2 -gt 0 ]
      then 
        run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PointStat_fcstOZONEMAX_obsAIRNOW.conf $PARMevs/metplus_config/machine.conf
	export err=$?; err_chk
        cp $DATA/point_stat/$MODELNAME/* $COMOUTsmall
        export outtyp=OZMAX8
        run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/StatAnalysis_fcstOZONEMAX_obsAIRNOW_GatherByDay.conf $PARMevs/metplus_config/machine.conf
	export err=$?; err_chk
       else
         echo "NO OZMAX8 OBS OR MODEL DATA"
         echo "OZMAX8, OZOBS2", $ozmax8, $ozobs2
       fi
    done

  done

fi

# Daily verification of the daily average of PM2.5
# Verification is being done on both raw and bias-corrected output data

if [ $cyc = 04 ]
then

  export OBSDIR=OBSMAX

  for biastyp in raw bc
  do

    export biastyp
    echo $biastyp

    if [ $biastyp = "raw" ]
    then
      export bctag=
      export bcout=_raw
    fi

    if [ $biastyp = "bc" ]
    then
      export bctag=_bc
      export bcout=_bc
    fi

    for hour in 06 12
    do

      export hour

#  search for model file and 2nd obs file for the daily average PM

      pmave1=0
      pmobs2=0
      if [ -e $COMINaqm/cs.${VDATE}/aqm.t${hour}z.ave_24hr_pm25${bctag}.148.grib2 ]
      then
        pmave1=1
      fi
      if [ -e $COMINaqm/cs.${PDYm4}/aqm.t${hour}z.ave_24hr_pm25${bctag}.148.grib2 ]
      then
       let "pmave1=pmave1+1" 
      fi
      if [ -e $COMINaqm/cs.${PDYm5}/aqm.t${hour}z.ave_24hr_pm25${bctag}.148.grib2 ]
      then
        let "pmave1=pmave1+1"
      fi
      if [ -e $COMINobs/hourly.${PDYm1}/aqm.t12z.anowpm.pb.tm024 ]
      then
       pmobs2=1
      fi
      echo "pmave1, pmobs2=",$pmave1,$pmobs2
      if [ $pmave1 -gt 0 -a $pmobs2 -gt 0 ]
      then
        run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/PointStat_fcstPMAVE_obsANOWPM.conf $PARMevs/metplus_config/machine.conf
	export err=$?; err_chk
        cp $DATA/point_stat/$MODELNAME/* $COMOUTsmall
        export outtyp=PMAVE
        run_metplus.py $PARMevs/metplus_config/${COMPONENT}/${VERIF_CASE}/stats/StatAnalysis_fcstPMAVE_obsANOWPM_GatherByDay.conf $PARMevs/metplus_config/machine.conf
	export err=$?; err_chk
       else
         echo "NO PMAVE OBS OR MODEL DATA"
         echo "PMAVE1, PMOBS2", $pmave1, $pmobs2
       fi
    done

  done

fi

exit

