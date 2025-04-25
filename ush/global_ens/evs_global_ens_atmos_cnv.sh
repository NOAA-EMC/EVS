#!/bin/ksh
#*****************************************************************************************
#  Purpose: Run cnv verification job
#      
#     Note: This script is specific for ceiling and visibility (cnv).
#           For ceiling and visibility, in case of clear sky in one member, its forecast 
#           will be given a very large value. This very large value may be arbitrary,
#           so it can not be used in the ensemble mean computation of CTC scores 
#           (so-called conditional-mean). The better solution to deal with such case is: 
#              Step 1. First verify cnv to get CTC stat files for each ensemble member.
#              Step 2. Calculate the ensemble mean of CTC among the stat files of all
#                      ensemble members. In other words, get the average of each column  
#                      (hit rate, false alarm, etc.) of CTC line type.
#              Step 3. Form final CTC stat file for cnv using the averaged CTC columns. 
#
#  Last update: 04/11/2025 by L. Gwen Chen (lichuan.chen@noaa.gov)
#               11/16/2023 by Binbin Zhou Lynker@EMC/NCEP
#
#*****************************************************************************************

set -x 

modnam=$1

########################################################
# export global parameters unified for all mpi sub-tasks
########################################################
export regrid='NONE'

#*******************************************************
# Check input if obs and fcst input data files available 
#*******************************************************
$USHevs/global_ens/evs_gens_atmos_check_input_files.sh prepbufr
export err=$?; err_chk
$USHevs/global_ens/evs_gens_atmos_check_input_files.sh $modnam
export err=$?; err_chk

MODNAM=`echo $modnam | tr '[a-z]' '[A-Z]'`
#********************************************************************
# Set up members, validation files and forecast hours based on models
#********************************************************************
if [ $modnam = gefs ] ; then
     mbrs='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30'
     validhours="00 06 12 18"
     fhrs="0 6 12 18 24 30 36 42 48 54 60 66 72 78 84"
elif [ $modnam = cmce ] ; then
     mbrs='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20'
     validhours="00 12"
     fhrs="12 24 36 48 60 72 84"
elif [ $modnam = ecme ] ; then
     mbrs='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50'
     validhours="00 12"
     fhrs="12 24 36 48 60 72 84"
else
     err_exit "wrong model: $modnam"
fi

tail='/atmos'
prefix=${EVSIN%%$tail*}
index=${#prefix}
echo $index
COM_IN=${EVSIN:0:$index}
echo $COM_IN

#************************************
# Step 1. Run METplus for all members
#************************************

# Check if all stats sub-tasks are completed in the previous runs
if [ ! -s $COMOUTsmall/completed/stats_completed ] ; then
mkdir -p $COMOUTsmall/completed
mkdir -p $WORK/completed

# Check if restart directory exists
if [ -d $COMOUTsmall/restart/cnv ] ; then
  cp -rfu $COMOUTsmall/restart/cnv $WORK
fi

#***********************************************
# Build a poe script to collect sub-task scripts
#***********************************************
>run_all_gens_cnv_poe.sh
for vhour in $validhours ; do
  for fhr in $fhrs ; do
    fhr3=$fhr
    typeset -Z3 fhr3
    fcst_time=$($NDATE -$fhr3 ${vday}${vhour})
    fyyyymmdd=${fcst_time:0:8}
    ihour=${fcst_time:8:2}
    #***********************
    # Build sub-task scripts
    #***********************
    >run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    #****************************
    # Run METplus for all members
    #****************************
    echo  "export output_base=$WORK/cnv/run_${modnam}_t${vhour}z_${fhr}_cnv" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export modelpath=$COM_IN" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export prepbufrhead=gfs" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export prepbufrgrid=prepbufr.f00.nc" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export prepbufrpath=$COM_IN" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export model=$modnam" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export MODEL=$MODNAM" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export vbeg=$vhour" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export vend=$vhour" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export valid_increment=21600" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export lead=$fhr" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo  "export modelhead=$modnam" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    if [ $modnam = ecme ] ; then
      echo  "export modeltail='.grib1'" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
      echo  "export modelgrid=grid4.f" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    else
      echo  "export modeltail='.grib2'" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
      echo  "export modelgrid=grid3.f" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    fi
    echo  "export extradir='atmos/'" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh

    for mbr in $mbrs ; do
      if [ $modnam = ecme ] ; then
        chk_file=$COM_IN/atmos.${fyyyymmdd}/$modnam/$modnam.ens${mbr}.t${ihour}z.grid4.f${fhr3}.grib1
      else
        chk_file=$COM_IN/atmos.${fyyyymmdd}/$modnam/$modnam.ens${mbr}.t${ihour}z.grid3.f${fhr3}.grib2
      fi

      if [ -s $chk_file ] ; then
        # Check for restart: check if the single sub-task is completed in the previous run
	# If this task has been completed in the previous run, then skip it
	if [ ! -e $COMOUTsmall/completed/run_${modnam}_t${vhour}z_f${fhr}_m${mbr}_cnv.completed ] ; then
      	  echo "export mbr=$mbr" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
          echo "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcst${MODNAM}_obsPREPBUFR_CNV.conf" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
          echo "export err=\$?; err_chk" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh

	  # Indicate sub-task is completed for restart        
	  echo ">$WORK/completed/run_${modnam}_t${vhour}z_f${fhr}_m${mbr}_cnv.completed" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh        
	  echo "echo "${modnam}_t${vhour}z_f${fhr}_m${mbr}_cnv task is completed" >> $WORK/completed/run_${modnam}_t${vhour}z_f${fhr}_m${mbr}_cnv.completed" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh

          # Save files for restart
	  echo "if [ $SENDCOM = YES ] ; then" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
	  echo "  if [ -d $WORK/cnv/run_${modnam}_t${vhour}z_${fhr}_cnv/stat/${modnam} ] ; then" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
	  echo "    mkdir -p $COMOUTsmall/restart/cnv/run_${modnam}_t${vhour}z_${fhr}_cnv/stat" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
	  echo "    cp -f $WORK/completed/run_${modnam}_t${vhour}z_f${fhr}_m${mbr}_cnv.completed $COMOUTsmall/completed" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
	  echo "    cp -rfu $WORK/cnv/run_${modnam}_t${vhour}z_${fhr}_cnv/stat/${modnam} $COMOUTsmall/restart/cnv/run_${modnam}_t${vhour}z_${fhr}_cnv/stat" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
	  echo "  fi" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
	  echo "fi" >> run_${modnam}_t${vhour}z_${fhr}_cnv.sh
	fi # end of check restart for sub-task
      fi
    done # end of mbrs loop

    chmod +x run_${modnam}_t${vhour}z_${fhr}_cnv.sh
    echo "${DATA}/run_${modnam}_t${vhour}z_${fhr}_cnv.sh" >> run_all_gens_cnv_poe.sh
 done # end of fhrs loop
done # end of validhours loop

#**********************
# Run step 1 poe script
#**********************
chmod 775 run_all_gens_cnv_poe.sh
if [ $run_mpi = yes ] ; then
  mpiexec -n 28 -ppn 28 --cpu-bind verbose,core cfp ${DATA}/run_all_gens_cnv_poe.sh
  export err=$?; err_chk
else
  ${DATA}/run_all_gens_cnv_poe.sh
  export err=$?; err_chk
fi

#***********************************************************
# Step 2. Average CTC columns over stat files of all members
#***********************************************************

#***********************************************
# Build a poe script to collect sub-task scripts 
#***********************************************
>run_all_gens_cnv_poe2.sh
for fhr in $fhrs ; do
  # Check for restart: check if the single sub-task is completed in the previous run
  # If this task has been completed in the previous run, then skip it
  if [ ! -e $COMOUTsmall/completed/run_${modnam}_${fhr}_cnv.completed ] ; then

    #***************************************************************************
    # Build sub-tasks which use $USHevs/global_ens/evs_global_ens_average_cnv.sh
    #   to get averaged CTC final stat files
    #***************************************************************************
    mkdir -p $WORK/cnv/run_${modnam}_${fhr}_cnv/stat/${modnam}
    for FILE in $COMOUTsmall/restart/cnv/run_${modnam}_t*z_${fhr}_cnv/stat/${modnam}/* ; do
        if [ -s $FILE ]; then
            cp -v $FILE $WORK/cnv/run_${modnam}_${fhr}_cnv/stat/${modnam}/.
        fi
    done

    echo "export output_base=$WORK/cnv/run_${modnam}_${fhr}_cnv" >> run_${modnam}_${fhr}_cnv.sh
    echo "cd \$output_base/stat/${modnam}" >> run_${modnam}_${fhr}_cnv.sh
    echo "$USHevs/global_ens/evs_global_ens_average_cnv.sh $modnam $fhr" >> run_${modnam}_${fhr}_cnv.sh
    echo "export err=\$?; err_chk" >> run_${modnam}_${fhr}_cnv.sh

    # Indicate sub-task is completed for restart
    echo ">$WORK/completed/run_${modnam}_${fhr}_cnv.completed" >> run_${modnam}_${fhr}_cnv.sh
    echo "echo "${modnam}_${fhr}_cnv task is completed" >> $WORK/completed/run_${modnam}_${fhr}_cnv.completed" >> run_${modnam}_${fhr}_cnv.sh

    echo "if [ $SENDCOM="YES" ] ; then" >> run_${modnam}_${fhr}_cnv.sh
    echo "  cp -f $WORK/completed/run_${modnam}_${fhr}_cnv.completed $COMOUTsmall/completed" >> run_${modnam}_${fhr}_cnv.sh
    echo "  for FILE in \$output_base/stat/${modnam}/*PREPBUFR_CONUS*.stat ; do" >> run_${modnam}_${fhr}_cnv.sh
    echo "    if [ -s \$FILE ]; then" >> run_${modnam}_${fhr}_cnv.sh
    echo "      cp -v \$FILE $COMOUTsmall" >> run_${modnam}_${fhr}_cnv.sh
    echo "    fi" >> run_${modnam}_${fhr}_cnv.sh
    echo "  done" >> run_${modnam}_${fhr}_cnv.sh
    echo "fi" >> run_${modnam}_${fhr}_cnv.sh
  fi # end of check restart for sub-task

  chmod +x run_${modnam}_${fhr}_cnv.sh
  echo "${DATA}/run_${modnam}_${fhr}_cnv.sh" >> run_all_gens_cnv_poe2.sh
done # end of fhrs loop

#************************
# Run step 2/3 poe script
#************************
chmod 775 run_all_gens_cnv_poe2.sh
if [ $run_mpi = yes ] ; then
  mpiexec -n 14 -ppn 14 --cpu-bind verbose,core cfp ${DATA}/run_all_gens_cnv_poe2.sh
  export err=$?; err_chk
else
  ${DATA}/run_all_gens_cnv_poe2.sh
  export err=$?; err_chk
fi

# Indicate all tasks are completed
>$WORK/completed/stats_completed
echo "All stats are completed" >> $WORK/completed/stats_completed

if [ $SENDCOM = YES ] ; then
  cp -f $WORK/completed/stats_completed $COMOUTsmall/completed
fi

fi # end of check restart for all tasks

#*******************************************************
# Combine small stat files to form a final big stat file
#*******************************************************
if [ $gather = yes ] ; then
  $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME cnv 00 18
  export err=$?; err_chk
fi
