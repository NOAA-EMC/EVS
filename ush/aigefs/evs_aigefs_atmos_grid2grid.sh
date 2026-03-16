#!/bin/ksh
#************************************************************************************
# Script: evs_aigefs_atmos_grid2grid.sh
# Purpose: run AIGEFS/HGEFS grid2grid verification for upper fields and 24hr APCP
#          by setting several METplus environment variables and running METplus
#          config files
# Input parameters:
#   (1) modnam: either gefs or aigefs or hgefs
#   (2) verify: either upper or precip or all
# Execution steps:
#   Both upper and precip have similar steps:
#   (1) Set/export environment parameters for METplus config files and put them
#       into procedure files
#   (2) Set running config files and put them into sub-task scripts
#   (3) Put all sub-task scripts into one poe script file    
#   (4) If $run_mpi is yes, run the poe script in parallel; otherwise run the poe
#       script in sequence
# Notes on METplus verification:
#   (1) For EnsembleStat, the input forecast files are ensemble member files from
#       EVS prep directory
#   (2) For GridStat, the input forecast files are ensemble products. In this 
#       script, the ensemble products (mean or probability) are first generated
#       by the MET GenEnsProd tool dynamically in the netCDF files. Then the netCDF 
#       files are used as input for GridStat to verify SL1L2, SAL1L2, CTC, PSTD etc
#       line types
#
# Update: 10/14/2025 by Gwen Chen (lichuan.chen@noaa.gov)
#************************************************************************************
set -x 

modnam=$1
verify=$2

###########################################################
# export global parameters unified for all mpi sub-tasks
###########################################################
export regrid='NONE'

#********************************************************
# Check input if obs and fcst input data files available
#********************************************************
$USHevs/${COMPONENT}/evs_gens_atmos_check_input_files.sh $modnam
export err=$?; err_chk
$USHevs/${COMPONENT}/evs_gens_atmos_check_input_files.sh gfsanl
export err=$?; err_chk

#*************************
# Get sub-string of $EVSIN
#*************************
tail='/atmos'
prefix=${EVSIN%%$tail*}
index=${#prefix}
echo $index
COM_IN=${EVSIN:0:$index}
echo $COM_IN

MODL=`echo $modnam | tr '[a-z]' '[A-Z]'`

#********************************
# Begin to build sub-task scripts
#********************************
##############################
# verify = upper
##############################
if [ $verify = upper ] ; then
  if [ $modnam = gefs ] ; then
    anl=gfsanl
    mbrs=30
  elif [ $modnam = aigefs ] ; then
    anl=gfsanl
    mbrs=31
  elif [ $modnam = hgefs ] ; then
    anl=gfsanl
    mbrs=62
  else
    err_exit "wrong model: $modnam"
  fi

  vhours="00 06 12 18"

  #*****************************************************************
  # Check if all stats sub-tasks are completed in the previous runs
  if [ ! -s $COMOUTsmall/completed/stats_completed ] ; then
  mkdir -p $COMOUTsmall/completed
  mkdir -p $WORK/completed

  # Check if restart directory exists
  if [ -d $COMOUTsmall/restart/grid2grid ] ; then
    cp -rfu $COMOUTsmall/restart/grid2grid $WORK
  fi
  #*****************************************************************

  for metplus_job in GenEnsProd EnsembleStat GridStat ; do
    #*******************************************
    # Build a poe script to collect sub-tasks
    #*******************************************
    >run_all_gens_g2g_${metplus_job}_poe.sh

    for vhour in ${vhours} ; do
      for fhr in fhr1 ; do
	#****************************
	# Build sub-task scripts
	#****************************
        >run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
	echo  "export output_base=${WORK}/grid2grid/run_${modnam}_valid_at_t${vhour}z_${fhr}" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export modelpath=$COM_IN" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export OBTYPE=GDAS" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export maskpath=$maskpath" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export gdashead=$anl" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export gdasgrid=grid3" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export gdaspath=$COM_IN" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export modelgrid=grid3.f" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export model=$modnam"  >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export MODEL=$MODL" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export modelhead=$modnam" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export vbeg=$vhour" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export vend=$vhour" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export valid_increment=21600" >>  run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export modeltail='.grib2'" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export extradir='atmos/'" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export climpath=$CLIMO/era5" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export members=$mbrs" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh

        if [ $modnam = hgefs ] ; then
          leads_chk="000 006 012 018 024 030 036 042 048 054 060 066 072 078 084 090 096 102 108 114 120 126 132 138 144 150 156 162 168 174 180 186 192 198 204 210 216 222 228 234 240"
        else
          leads_chk="000 006 012 018 024 030 036 042 048 054 060 066 072 078 084 090 096 102 108 114 120 126 132 138 144 150 156 162 168 174 180 186 192 198 204 210 216 222 228 234 240 246 252 258 264 270 276 282 288 294 300 306 312 318 324 330 336 342 348 354 360 366 372 378 384"
        fi

        typeset -a lead_arr
        for lead_chk in $leads_chk; do
          fcst_time=$($NDATE -$lead_chk ${vday}${vhour})
          fyyyymmdd=${fcst_time:0:8}
          ihour=${fcst_time:8:2}
          if [ $metplus_job = GenEnsProd ] || [ $metplus_job = EnsembleStat ] ; then
              chk_path=$COM_IN/atmos.${fyyyymmdd}/$modnam/$modnam.ens*.t${ihour}z.grid3.f${lead_chk}.grib2
              nmbrs_lead_check=$(find $chk_path -size +0c 2>/dev/null | wc -l)
              if [ $nmbrs_lead_check -eq $mbrs ]; then
                 lead_arr[${#lead_arr[*]}+1]=${lead_chk}
              fi
          elif [ $metplus_job = GridStat ]; then
              chk_file=${WORK}/grid2grid/run_${modnam}_valid_at_t${vhour}z_${fhr}/stat/${modnam}/GenEnsProd_${MODL}_g2g_BIN1_FHR${lead_chk}_${vday}_${vhour}0000V_ens.nc
              if [ -s $chk_file ]; then
                lead_arr[${#lead_arr[*]}+1]=${lead_chk}
              fi
          fi
        done

        conf_MODL=GEFS

        for lead_hr in ${lead_arr[@]}; do
          # Check for restart: check if the single sub-task is completed in the previous run
	  # If this task has been completed in the previous run, then skip it
	  if [ ! -e $COMOUTsmall/completed/run_${modnam}_valid_at_t${vhour}z_${fhr}_${lead_hr}_${metplus_job}_g2g.completed ] ; then
	    echo "export lead=${lead_hr}" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh

            if [ $metplus_job = GenEnsProd ] || [ $metplus_job = EnsembleStat ]; then
       	      echo "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${conf_MODL}_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
              echo "export err=\$?; err_chk" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
            elif [ $metplus_job = GridStat ]; then
              echo "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${conf_MODL}_obsModelAnalysis_climoERA5_mean.conf " >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
              echo "export err=\$?; err_chk" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
            fi

	    # Indicate sub-task is completed for restart 
	    echo ">$WORK/completed/run_${modnam}_valid_at_t${vhour}z_${fhr}_${lead_hr}_${metplus_job}_g2g.completed" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
            echo "echo "${modnam}_valid_at_t${vhour}z_${fhr}_${lead_hr}_${metplus_job}_g2g task is completed" >> $WORK/completed/run_${modnam}_valid_at_t${vhour}z_${fhr}_${lead_hr}_${metplus_job}_g2g.completed" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh

            # Save files for restart
	    echo "if [ $SENDCOM = YES ] ; then" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
	    echo "  if [ -d $WORK/grid2grid/run_${modnam}_valid_at_t${vhour}z_${fhr}/stat/${modnam} ] ; then" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
            echo "    mkdir -p $COMOUTsmall/restart/grid2grid/run_${modnam}_valid_at_t${vhour}z_${fhr}/stat" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
            echo "    cp -f $WORK/completed/run_${modnam}_valid_at_t${vhour}z_${fhr}_${lead_hr}_${metplus_job}_g2g.completed $COMOUTsmall/completed" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
	    echo "    cp -rfu $WORK/grid2grid/run_${modnam}_valid_at_t${vhour}z_${fhr}/stat/${modnam} $COMOUTsmall/restart/grid2grid/run_${modnam}_valid_at_t${vhour}z_${fhr}/stat" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
	    echo "  fi" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
	    echo "fi" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
	  fi # end of check restart for sub-task
	done # end of lead_arr loop
	unset lead_arr

        if [ $metplus_job = EnsembleStat ] ; then
            if [ $SENDCOM="YES" ] ; then
                echo "for FILE in \$output_base/stat/${modnam}/ensemble_stat_*.stat ; do" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
                echo "  if [ -s \$FILE ]; then" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
                echo "    cp -v \$FILE $COMOUTsmall" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
                echo "  fi" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
                echo "done" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
             fi
        elif [ $metplus_job = GridStat ] ; then
            if [ $SENDCOM="YES" ] ; then
                echo "for FILE in \$output_base/stat/${modnam}/grid_stat_*.stat ; do" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
                echo "  if [ -s \$FILE ]; then" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
                echo "    cp -v \$FILE $COMOUTsmall" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
                echo "  fi" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
                echo "done" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
            fi
        fi

	chmod +x run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo "${DATA}/run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh" >> run_all_gens_g2g_${metplus_job}_poe.sh

      done # end of fhr1 loop
    done # end of vhours loop

    chmod 755 run_all_gens_g2g_${metplus_job}_poe.sh

    #************************************************
    # Run poe script in mpi parallel or in sequence
    #************************************************
    if [ -s run_all_gens_g2g_${metplus_job}_poe.sh ] ; then
      if [ $run_mpi = yes ] ; then
        mpiexec -n 4 -ppn 4 --cpu-bind verbose,core cfp ${DATA}/run_all_gens_g2g_${metplus_job}_poe.sh
        export err=$?; err_chk
      else
        ${DATA}/run_all_gens_g2g_${metplus_job}_poe.sh
        export err=$?; err_chk
      fi
    fi
  done # end of metplus_jobs loop

  # Indicate all tasks are completed
  >$WORK/completed/stats_completed
  echo "All stats are completed" >> $WORK/completed/stats_completed
  if [ $SENDCOM = YES ] ; then
    cp -f $WORK/completed/stats_completed $COMOUTsmall/completed
  fi

  fi # end of check restart for all tasks

  #********************************************************
  # Combine small stat files to form a final big stat file
  #********************************************************
  if [ $gather = yes ] ; then
    $USHevs/${COMPONENT}/evs_${COMPONENT}_atmos_gather.sh $MODELNAME grid2grid 00 18
    export err=$?; err_chk
  fi
fi # end of if verify = upper

##############################
# verify = precip
##############################
if [ $verify = precip ] ; then
  export COMOUTsmall_precip=$COMOUT/$RUN.$VDATE/$MODELNAME/precip
  mkdir -p $COMOUTsmall_precip

  if [ $modnam = gefs ] ; then
    mbrs=30
  elif [ $modnam = aigefs ] ; then
    mbrs=31
  elif [ $modnam = hgefs ] ; then
    mbrs=62
  else
    err_exit "wrong model: $modnam"
  fi

  apcps="24h 06h"

  #*****************************************************************
  # Check if all stats sub-tasks are completed in the previous runs
  if [ ! -s $COMOUTsmall_precip/completed/stats_completed ] ; then
  mkdir -p $COMOUTsmall_precip/completed
  mkdir -p $WORK/completed

  # Check if restart directory exists
  if [ -d $COMOUTsmall_precip/restart/grid2grid ] ; then
    cp -rfu $COMOUTsmall_precip/restart/grid2grid $WORK
  fi
  #*****************************************************************

  for metplus_job in GenEnsProd EnsembleStat GridStat ; do
    #*********************************************
    # Build a poe script to collect sub-tasks
    #*********************************************
    >run_all_gens_precip_${metplus_job}_poe.sh
    for apcp in $apcps ; do
      if [ $apcp = 24h ] ; then
        validhours='12'
      else
        validhours='00 06 12 18'
      fi
      for vhour in $validhours; do
	#**********************************
	# Build sub-task scripts
	#**********************************
        >run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
	echo  "export output_base=$WORK/grid2grid/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        export modelpath=$COM_IN
        echo  "export modelpath=$COM_IN" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        if [ $apcp = 24h ] ; then
          if [ $modnam = hgefs ] ; then
            leads_chk="024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240"
          else
            leads_chk="024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384"
          fi
          echo  "export ccpagrid=grid3.24h.f00.nc" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          echo  "export modelgrid=grid3.24h.f" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          echo  "export modeltail='.nc'" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          echo  "export valid_increment=21600" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          echo  "export climpath_apcp24_prob=$CLIMO/ccpa" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        elif [ $apcp = 06h ] ; then
          if [ $modnam = hgefs ] ; then
            leads_chk="024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240"
          else
            leads_chk="024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384"
          fi
          echo  "export vbeg=$vhour" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          echo  "export vend=$vhour" >>  run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          echo  "export valid_increment=21600" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          echo  "export ccpagrid=grid3.06h.f00.grib2" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          echo  "export modelgrid=grid3.f" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          echo  "export modeltail='.grib2'" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        fi
        echo  "export ccpahead=ccpa" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        echo  "export ccpapath=$COM_IN" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        echo  "export model=$modnam"  >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        echo  "export MODEL=$MODL" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        echo  "export modelhead=$modnam" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        echo  "export extradir='atmos/'" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        echo  "export members=$mbrs" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        typeset -a lead_arr
        for lead_chk in $leads_chk; do
          fcst_time=$($NDATE -$lead_chk ${vday}${vhour})
          fyyyymmdd=${fcst_time:0:8}
          ihour=${fcst_time:8:2}
          if [ $metplus_job = GenEnsProd ] || [ $metplus_job = EnsembleStat ] ; then
            if [ $apcp = 24h ]; then
              chk_path=$COM_IN/atmos.${fyyyymmdd}/$modnam/$modnam.ens*.t${ihour}z.grid3.24h.f${lead_chk}.nc
            elif [ $apcp = 06h ] ; then
              chk_path=$COM_IN/atmos.${fyyyymmdd}/$modnam/$modnam.ens*.t${ihour}z.grid3.f${lead_chk}.grib2
            fi
            nmbrs_lead_check=$(find $chk_path -size +0c 2>/dev/null | wc -l)
            if [ $nmbrs_lead_check -eq $mbrs ]; then
              lead_arr[${#lead_arr[*]}+1]=${lead_chk}
            fi
          elif [ $metplus_job = GridStat ]; then
            if [ $apcp = 24h ]; then
                chk_file=$WORK/grid2grid/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z/stat/${modnam}/GenEnsProd_${MODL}_APCP24_FHR${lead_chk}_${vday}_${vhour}0000V_ens.nc
            elif [ $apcp = 06h ] ; then
                chk_file=$WORK/grid2grid/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z/stat/${modnam}/GenEnsProd_${MODL}_APCP06_FHR${lead_chk}_${vday}_${vhour}0000V_ens.nc
            fi
            if [ -s $chk_file ]; then
              lead_arr[${#lead_arr[*]}+1]=${lead_chk}
            fi
          fi
        done

        conf_MODL=GEFS

        for lead_hr in ${lead_arr[@]}; do
        # Check for restart: check if the single sub-task is completed in the previous run
	# If this task has been completed in the previous run, then skip it
	if [ ! -e $COMOUTsmall_precip/completed/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_fhr${lead_hr}_${metplus_job}.completed ] ; then
        echo "export lead=${lead_hr}" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh

	if [ $metplus_job = GenEnsProd ] || [ $metplus_job = EnsembleStat ]; then
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${conf_MODL}_obsCCPA${apcp}.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          echo "export err=\$?; err_chk" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        elif [ $metplus_job = GridStat ]; then
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${conf_MODL}_obsCCPA${apcp}_mean.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          echo "export err=\$?; err_chk" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          if [ $apcp = 24h ] ; then
            echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${conf_MODL}_obsCCPA${apcp}_climoEMC_prob.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
            echo "export err=\$?; err_chk" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          elif [ $apcp = 06h ] ; then
            echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${conf_MODL}_obsCCPA${apcp}_prob.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
            echo "export err=\$?; err_chk" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          fi
        fi

        # Indicate sub-task is completed for restart
	echo ">$WORK/completed/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_fhr${lead_hr}_${metplus_job}.completed" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        echo "echo "${modnam}_ccpa${apcp}_valid_at_t${vhour}z_fhr${lead_hr}_${metplus_job} task is completed" >> $WORK/completed/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_fhr${lead_hr}_${metplus_job}.completed" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh

	# Save files for restart
	echo "if [ $SENDCOM = YES ] ; then" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        echo "  if [ -d $WORK/grid2grid/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z/stat/${modnam} ] ; then" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        echo "    mkdir -p $COMOUTsmall_precip/restart/grid2grid/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z/stat" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        echo "    cp -f $WORK/completed/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_fhr${lead_hr}_${metplus_job}.completed $COMOUTsmall_precip/completed" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
	echo "    cp -rfu $WORK/grid2grid/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z/stat/${modnam} $COMOUTsmall_precip/restart/grid2grid/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z/stat" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        echo "  fi" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
	echo "fi" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        fi # end of check restart for sub-task
	done # end of lead_arr loop
	unset lead_arr

	if [ $metplus_job = EnsembleStat ]; then
            if [ $SENDCOM="YES" ] ; then
                echo "for FILE in \$output_base/stat/${modnam}/ensemble_stat_*.stat ; do" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
                echo "  if [ -s \$FILE ]; then" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
                echo "    cp -v \$FILE $COMOUTsmall_precip" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
                echo "  fi" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
                echo "done" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
            fi
        elif [ $metplus_job = GridStat ]; then
            if [ $SENDCOM="YES" ] ; then
                echo "for FILE in \$output_base/stat/${modnam}/grid_stat_*.stat ; do" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
                echo "  if [ -s \$FILE ]; then" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
                echo "    cp -v \$FILE $COMOUTsmall_precip" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
                echo "  fi" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
                echo "done" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
            fi
        elif [ $metplus_job = GenEnsProd ]; then
          if [ $apcp = 24h ] ; then
	    #*******************************************************
	    # Save the 24h APCP ensemble mean files for spatial map 
	    #*******************************************************
            mkdir -p $COMOUT/$RUN.$VDATE/apcp24_mean/$MODELNAME
            if [ $SENDCOM="YES" ] ; then
                echo "for FILE in \$output_base/stat/${modnam}/GenEnsProd*APCP24*.nc ; do" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
                echo "  if [ -s \$FILE ]; then" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
                echo "    cp -v \$FILE $COMOUT/$RUN.$VDATE/apcp24_mean/$MODELNAME" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
                echo "  fi" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
                echo "done" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
            fi      
          fi
        fi

	chmod +x run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        echo "${DATA}/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh" >> run_all_gens_precip_${metplus_job}_poe.sh

      done # end of validhours loop
    done # end of apcps loop

    chmod 755 run_all_gens_precip_${metplus_job}_poe.sh

    #**********************************************
    # Run poe script in mpi parallel or in sequnce
    #**********************************************
    if [ -s run_all_gens_precip_${metplus_job}_poe.sh ]; then
      if [ $run_mpi = yes ] ; then
        mpiexec  -n 5 -ppn 5 --cpu-bind verbose,core cfp ${DATA}/run_all_gens_precip_${metplus_job}_poe.sh
        export err=$?; err_chk
      else
        ${DATA}/run_all_gens_precip_${metplus_job}_poe.sh
        export err=$?; err_chk
      fi
    fi
  done # end of metplus_jobs loop

  # Indicate all tasks are completed
  >$WORK/completed/stats_completed
  echo "All stats are completed" >> $WORK/completed/stats_completed
  if [ $SENDCOM = YES ] ; then
    cp -f $WORK/completed/stats_completed $COMOUTsmall_precip/completed
  fi

  fi # end of check restart for all tasks

  #********************************************************
  # Combine small stat files to form a final big stat file
  #********************************************************
  if [ $gather = yes ] ; then
    $USHevs/${COMPONENT}/evs_${COMPONENT}_atmos_gather.sh $MODELNAME precip 00 18
    export err=$?; err_chk
  fi
fi # end of if verify = precip
