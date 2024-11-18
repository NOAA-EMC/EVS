#!/bin/ksh

#*********************************************************************************************************
# Script: evs_global_ens_atmos_grid2grid.sh
# Purpose: run Global ensembles (GEFS, CMCE, ECME, and NAEFS) grid2grid verification for upper fields 
#          and 24hr APCP by setting several METplus environment variables and running METplus conf files 
# Input parameters:
#   (1) modnam: either gefs or cmce or ecme or naefs or all
#   (2) verify: either upper or precip or all
# Execution steps:
#   Both upper and precip have similar steps:
#   (1) Set/export environment parameters for METplus conf files and put them into procedure files
#   (2) Set running conf files and put them into sub-task scripts
#   (3) Put all sub-task scripts into one poe script file    
#   (4) If $run_mpi is yes, run the poe script in parallel; otherwise run the poe script in sequence
# Notes on METplus verification:
#   (1) For EnsembleStat, the input forecast files are ensemble member files from EVS prep directory
#   (2) For GridStat, the input forecast files are ensemble products. Since global ensemble forecast
#       (GEFS, CMCE, ECME, NAEFS) have no ensemble product output (GEFS only has some a few), the
#       ensemble products should be generated. In this script, the ensemble products (mean or probability) 
#       are first generated by the MET GenEnsProd tool dynamically in the netCDF files. Then the netCDF 
#       files are used as input for GridStat to verify SL1L2, SAL1L2, CTC, PSTD etc line types
#
# Last update: 11/06/2024 by Gwen Chen (lichuan.chen@noaa.gov)
#              11/16/2023 by Binbin Zhou (Lynker@NCPE/EMC) 
#              11/12/2023 by Mallory Row (SAIC@NCEP/EMC) 
#
#********************************************************************************************************

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
if [ $modnam = gefs ] ; then
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh gfsanl
   export err=$?; err_chk
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh gefs
   export err=$?; err_chk
elif  [ $modnam = cmce ] ; then
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh cmcanl
   export err=$?; err_chk
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh cmce
   export err=$?; err_chk
elif  [ $modnam = ecme ] ; then
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh ecmanl
   export err=$?; err_chk
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh ecme
   export err=$?; err_chk
elif  [ $modnam = naefs ] ; then
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh gfsanl
   export err=$?; err_chk
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh cmcanl
   export err=$?; err_chk
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh gefs_bc
   export err=$?; err_chk
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh cmce_bc
   export err=$?; err_chk
fi

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
  elif [ $modnam = cmce ] ; then
    anl=cmcanl
    mbrs=20
  elif [ $modnam = ecme ] ; then
    anl=ecmanl
    mbrs=50
  elif [ $modnam = naefs ] ; then
    #*********************************
    # Dynamically create NAEFS members
    #*********************************
    $USHevs/global_ens/evs_gens_atmos_g2g_reset_naefs.sh
    export err=$?; err_chk
    anl=gfsanl
    if [ $gefs_number = 20 ] ; then
      mbrs=40
    elif [ $gefs_number = 30 ] ; then
      mbrs=50
    fi
  else
    err_exit "wrong model: $modnam"
  fi
  if [ $modnam = gefs ] ; then
    vhours="00 06 12 18"
  else
    vhours="00 12"
  fi

  #*****************************************************************
  # Check if all stats sub-tasks are completed in the previous runs
  if [ ! -s $COMOUTsmall/stats_completed ] ; then

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

    for vhour in ${vhours}  ; do
      for fhr in fhr1 ; do
	#****************************
	# Build sub-task scripts
	#****************************
        >run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh

        # Check for restart: check if the single sub-task is completed in the previous run
        # If this task has been completed in the previous run, then skip it
        if [ ! -e $COMOUTsmall/run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.completed ] ; then

	echo  "export output_base=${WORK}/grid2grid/run_${modnam}_valid_at_t${vhour}z_${fhr}" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        if [ $modnam = naefs ] ; then
          echo  "export modelpath=${WORK}/naefs" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        else
          echo  "export modelpath=$COM_IN" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        fi
        echo  "export OBTYPE=GDAS" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export maskpath=$maskpath" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export gdashead=$anl" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export gdasgrid=grid3" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export gdaspath=$COM_IN" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        if [ ${modnam} = ecme ] ; then
                echo  "export modelgrid=grid4.f" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        else
                echo  "export modelgrid=grid3.f" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        fi
        echo  "export model=$modnam"  >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export MODEL=$MODL" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export modelhead=$modnam" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export vbeg=$vhour" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export vend=$vhour" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export valid_increment=21600" >>  run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        if [ $modnam = ecme ] ; then
           echo  "export modeltail='.grib1'" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        else
           echo  "export modeltail='.grib2'" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        fi
        echo  "export extradir='atmos/'" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export climpath=$CLIMO/era5" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo  "export members=$mbrs" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        if [ $modnam = gefs ] ; then
          leads_chk="000 006 012 018 024 030 036 042 048 054 060 066 072 078 084 090 096 102 108 114 120 126 132 138 144 150 156 162 168 174 180 186 192 198 204 210 216 222 228 234 240 246 252 258 264 270 276 282 288 294 300 306 312 318 324 330 336 342 348 354 360 366 372 378 384"
        elif [ $modnam = cmce ] || [ $modnam = naefs ] ; then
          leads_chk="000 012 024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384"
        elif [  $modnam = ecme ] ; then
           leads_chk="000 012 024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360"
        fi
        typeset -a lead_arr
        for lead_chk in $leads_chk; do
          fcst_time=$($NDATE -$lead_chk ${vday}${vhour})
          fyyyymmdd=${fcst_time:0:8}
          ihour=${fcst_time:8:2}
          if [ $metplus_job = GenEnsProd ]|| [ $metplus_job = EnsembleStat ] ; then
              if [ $modnam = naefs ] ; then
                chk_path=${WORK}/naefs/$modnam.ens*.${fyyyymmdd}.t${ihour}z.grid3.f${lead_chk}.grib2
              elif [ $modnam = ecme ] ; then
                chk_path=$COM_IN/atmos.${fyyyymmdd}/$modnam/$modnam.ens*.t${ihour}z.grid4.f${lead_chk}.grib1
              else
                chk_path=$COM_IN/atmos.${fyyyymmdd}/$modnam/$modnam.ens*.t${ihour}z.grid3.f${lead_chk}.grib2
              fi
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
        lead=$(echo $(echo ${lead_arr[@]}) | tr ' ' ',')
        unset lead_arr
        if [ $metplus_job = GridStat ] && [ $modnam = ecme ]; then
          typeset -a lead_SFC_arr
          for lead_chk in $leads_chk; do
            fcst_time=$($NDATE -$lead_chk ${vday}${vhour})
            fyyyymmdd=${fcst_time:0:8}
            ihour=${fcst_time:8:2}
            chk_file_SFC=${WORK}/grid2grid/run_${modnam}_valid_at_t${vhour}z_${fhr}/stat/${modnam}/GenEnsProd_${MODL}_g2g_BIN1_SFC_FHR${lead_chk}_${vday}_${vhour}0000V_ens.nc
            if [ -s $chk_file_SFC ]; then
              lead_SFC_arr[${#lead_SFC_arr[*]}+1]=${lead_chk}
            fi
          done
          lead_SFC=$(echo $(echo ${lead_SFC_arr[@]}) | tr ' ' ',')
          unset lead_SFC_arr
        fi
        echo  "export lead=$lead" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        if [ $modnam = naefs ] ; then
          conf_MODL="NAEFSbc"
        elif [ $modnam = cmce ] ; then
          conf_MODL="GEFS"
        else
          conf_MODL=$MODL
        fi
        if [ $metplus_job = GenEnsProd ] || [ $metplus_job = EnsembleStat ]; then
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${conf_MODL}_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
          echo "export err=\$?; err_chk" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
          if [ $modnam = ecme ]; then
            echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${conf_MODL}_obsModelAnalysis_climoERA5_SFC.conf " >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
            echo "export err=\$?; err_chk" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
          fi
        elif [ $metplus_job = GridStat ]; then
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${conf_MODL}_obsModelAnalysis_climoERA5_mean.conf " >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
          echo "export err=\$?; err_chk" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
          if [ $modnam = ecme ]; then
            echo  "export lead=$lead_SFC" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
            echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${conf_MODL}_obsModelAnalysis_climoERA5_mean_SFC.conf " >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
            echo "export err=\$?; err_chk" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
          fi
        fi
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

	# Indicate sub-task is completed for restart 
	echo ">$COMOUTsmall/run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.completed" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh

	# Save files for restart
        echo "if [ $SENDCOM = YES ] ; then" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
	echo "  if [ -d $WORK/grid2grid/run_${modnam}_valid_at_t${vhour}z_${fhr}/stat/${modnam} ] ; then" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
	echo "    mkdir -p $COMOUTsmall/restart/grid2grid/run_${modnam}_valid_at_t${vhour}z_${fhr}/stat" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
	echo "    cp -rfu $WORK/grid2grid/run_${modnam}_valid_at_t${vhour}z_${fhr}/stat/${modnam} $COMOUTsmall/restart/grid2grid/run_${modnam}_valid_at_t${vhour}z_${fhr}/stat" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
	echo "  fi" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
	echo "fi" >> run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh

	chmod +x run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh
        echo "${DATA}/run_${modnam}_valid_at_t${vhour}z_${fhr}_${metplus_job}_g2g.sh" >> run_all_gens_g2g_${metplus_job}_poe.sh
        fi # end of check restart for sub-task

      done # end of fhr1 loop
    done # end of vhours loop

    chmod 755 run_all_gens_g2g_${metplus_job}_poe.sh

    #************************************************
    # Run poe script in mpi parallel or in sequence
    #************************************************
    if [ -s run_all_gens_g2g_${metplus_job}_poe.sh ] ; then
      if [ $run_mpi = yes ] ; then
        if [ ${modnam} = gefs ] ; then
          mpiexec  -n 4 -ppn 4 --cpu-bind verbose,core cfp ${DATA}/run_all_gens_g2g_${metplus_job}_poe.sh
          export err=$?; err_chk
        else
          mpiexec  -n 2 -ppn 2 --cpu-bind verbose,core cfp ${DATA}/run_all_gens_g2g_${metplus_job}_poe.sh
          export err=$?; err_chk
        fi
      else
        ${DATA}/run_all_gens_g2g_${metplus_job}_poe.sh
        export err=$?; err_chk
      fi
    fi
  done # end of metplus_jobs loop

  # Indicate all tasks are completed
  >$COMOUTsmall/stats_completed
  echo "stats are completed" >> $COMOUTsmall/stats_completed

  fi # end of check restart for all tasks

  #********************************************************
  # Combine small stat files to form a final big stat file
  #********************************************************
  if [ $gather = yes ] ; then
    if [ ${modnam} = gefs ] ; then
      $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME grid2grid 00 18
      export err=$?; err_chk
    else
      $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME grid2grid 00 12
      export err=$?; err_chk
    fi
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
  elif [ $modnam = cmce ] ; then
    mbrs=20
  elif [ $modnam = naefs ] ; then
    #*********************************
    # Dynamically create NAEFS members
    #*********************************
    $USHevs/global_ens/evs_gens_atmos_precip_create_naefs.sh
    export err=$?; err_chk
    if [ $gefs_number = 20 ] ; then
      mbrs=20
    elif [ $gefs_number = 30 ] ; then
      mbrs=30
    fi
  elif [ $modnam = ecme ] ; then
    mbrs=50
  else
    err_exit "wrong model: $modnam"
  fi
  if [ ${modnam} = gefs ] ; then
    apcps="24h 06h"
  else
    apcps="24h"
  fi

  #*****************************************************************
  # Check if all stats sub-tasks are completed in the previous runs
  if [ ! -s $COMOUTsmall_precip/stats_completed ] ; then

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

	# Check for restart: check if the single sub-task is completed in the previous run
	# If this task has been completed in the previous run, then skip it
	if [ ! -e $COMOUTsmall_precip/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.completed ] ; then

	echo  "export output_base=$WORK/grid2grid/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        if [ $modnam = naefs ] ; then
          export modelpath=${WORK}/naefs_precip
          echo  "export modelpath=${WORK}/naefs_precip" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        else
          export modelpath=$COM_IN
          echo  "export modelpath=$COM_IN" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        fi
        if [ $apcp = 24h ] ; then
          leads_chk="024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384"
          echo  "export ccpagrid=grid3.24h.f00.nc" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          if [ ${modnam} = ecme ] ; then
                  echo  "export modelgrid=grid4.24h.f" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          else
                  echo  "export modelgrid=grid3.24h.f" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          fi
          if [ $modnam = naefs ] ; then
             echo  "export modeltail='.grib2'" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          else
             echo  "export modeltail='.nc'" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          fi
          echo  "export valid_increment=21600" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          echo  "export climpath_apcp24_prob=$CLIMO/ccpa" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        elif [ $apcp = 06h ] ; then
          leads_chk="024 036 048 060 072 084 096 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384"
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
          if [ $metplus_job = GenEnsProd ]|| [ $metplus_job = EnsembleStat ] ; then
            if [ $apcp = 24h ]; then
              if [ $modnam = naefs ] ; then
                chk_path=${WORK}/naefs_precip/$modnam.ens*.${fyyyymmdd}.t${ihour}z.grid3.24h.f${lead_chk}.grib2
              elif [ ${modnam} = ecme ] ; then
                chk_path=$COM_IN/atmos.${fyyyymmdd}/$modnam/$modnam.ens*.t${ihour}z.grid4.24h.f${lead_chk}.nc
              else
                chk_path=$COM_IN/atmos.${fyyyymmdd}/$modnam/$modnam.ens*.t${ihour}z.grid3.24h.f${lead_chk}.nc
              fi
            elif [ $apcp = 06h ] ; then
              if [ $modnam = naefs ] ; then
                chk_path=${WORK}/naefs_precip/$modnam.ens*.${fyyyymmdd}.t${ihour}z.grid3.f${lead_chk}.grib2
              else
                chk_path=$COM_IN/atmos.${fyyyymmdd}/$modnam/$modnam.ens*.t${ihour}z.grid3.f${lead_chk}.grib2
              fi
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
        lead=$(echo $(echo ${lead_arr[@]}) | tr ' ' ',')
        unset lead_arr
        echo  "export lead=$lead" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        if [ $modnam = cmce ] ; then
          conf_MODL="GEFS"
        else
          conf_MODL=$MODL
        fi
        if [ $metplus_job = GenEnsProd ] || [ $metplus_job = EnsembleStat ]; then
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${conf_MODL}_obsCCPA${apcp}.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          echo "export err=\$?; err_chk" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        elif [ $metplus_job = GridStat ]; then
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${conf_MODL}_obsCCPA${apcp}_mean.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          echo "export err=\$?; err_chk" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          if [ $modnam = gefs ] || [ $modnam = cmce ] ; then
            if [ $apcp = 24h ] ; then
              echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${conf_MODL}_obsCCPA${apcp}_climoEMC_prob.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
              echo "export err=\$?; err_chk" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
            elif [ $apcp = 06h ] ; then
              echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${conf_MODL}_obsCCPA${apcp}_prob.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
              echo "export err=\$?; err_chk" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
            fi
          else
            echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/${metplus_job}_fcst${conf_MODL}_obsCCPA${apcp}_climoEMC_prob.conf " >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
            echo "export err=\$?; err_chk" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
          fi
        fi
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

        # Indicate sub-task is completed for restart 
	echo ">$COMOUTsmall_precip/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.completed" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh

	# Save files for restart
        echo "if [ $SENDCOM = YES ] ; then" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
	echo "  if [ -d $WORK/grid2grid/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z/stat/${modnam} ] ; then" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
	echo "    mkdir -p $COMOUTsmall_precip/restart/grid2grid/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z/stat" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh

	echo "    cp -rfu $WORK/grid2grid/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z/stat/${modnam} $COMOUTsmall_precip/restart/grid2grid/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z/stat" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        echo "  fi" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
	echo "fi" >> run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh

	chmod +x run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh
        echo "${DATA}/run_${modnam}_ccpa${apcp}_valid_at_t${vhour}z_${metplus_job}.sh" >> run_all_gens_precip_${metplus_job}_poe.sh

	fi # end of check restart for sub-task
      done # end of validhours loop
    done # end of apcps loop

    chmod 755 run_all_gens_precip_${metplus_job}_poe.sh

    #**********************************************
    # Run poe script in mpi parallel or in sequnce
    #**********************************************
    if [ -s run_all_gens_precip_${metplus_job}_poe.sh ]; then
      if [ $run_mpi = yes ] ; then
        if [ ${modnam} = gefs ] ; then
          mpiexec  -n 5 -ppn 5 --cpu-bind verbose,core cfp ${DATA}/run_all_gens_precip_${metplus_job}_poe.sh
          export err=$?; err_chk
        else
          mpiexec  -n 1 -ppn 1 --cpu-bind verbose,core cfp ${DATA}/run_all_gens_precip_${metplus_job}_poe.sh
          export err=$?; err_chk
        fi
      else
        ${DATA}/run_all_gens_precip_${metplus_job}_poe.sh
        export err=$?; err_chk
      fi
    fi
  done # end of metplus_jobs loop

  # Indicate all tasks are completed
  >$COMOUTsmall_precip/stats_completed
  echo "stats are completed" >> $COMOUTsmall_precip/stats_completed

  fi # end of check restart for all tasks

  #********************************************************
  # Combine small stat files to form a final big stat file
  #********************************************************
  if [ $gather = yes ] ; then
    if [ $modnam = gefs ] ; then
      $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME precip 00 18
    else
      $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME precip 00 12
    fi
  fi
fi # end of if verify = precip
