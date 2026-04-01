#!/bin/ksh
#************************************************************************************
# Script: evs_aigefs_atmos_grid2obs.sh
# Purpose: run AIGEFS/HGEFS grid2obs verification for upper and surface fields
#          by setting several METplus environment variables and running METplus
#          config files
# Input parameters:
#   (1) modnam: either gefs or aigefs or hgefs 
# Execution steps:
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

###########################################################
# export global parameters unified for all mpi sub-tasks
###########################################################
export regrid='NONE'

#**********************************
# Check availability of input files
#**********************************
$USHevs/${COMPONENT}/evs_gens_atmos_check_input_files.sh $modnam
export err=$?; err_chk
$USHevs/${COMPONENT}/evs_gens_atmos_check_input_files.sh prepbufr
export err=$?; err_chk
$USHevs/${COMPONENT}/evs_gens_atmos_check_input_files.sh prepbufr_profile
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

#********************************
# Begin to build sub-task scripts
#********************************
MODNAM=`echo $modnam | tr '[a-z]' '[A-Z]'`
if [ $modnam = gefs ] ; then
  mbrs=30
elif [ $modnam = aigefs ] ; then
  mbrs=31
elif [ $modnam = hgefs ] ; then
  mbrs=62
else
  err_exit "wrong model: $modnam"
fi

#***************************************
# fields: types of fields to be verified
#***************************************
fields="sfc profile upper"
validhours="00 06 12 18"

#*****************************************************************
# Check if all stats sub-tasks are completed in the previous runs
if [ ! -s $COMOUTsmall/completed/stats_completed ] ; then
mkdir -p $COMOUTsmall/completed
mkdir -p $WORK/completed

# Check if restart directory exists
if [ -d $COMOUTsmall/restart/grid2obs ] ; then
  cp -rfu $COMOUTsmall/restart/grid2obs $WORK
fi
#*****************************************************************

for field in $fields ; do
    fieldUPPER=`echo $field | tr '[a-z]' '[A-Z]'`
    if [ $field = profile ] || [ $field = upper ] ; then
      #******************************************************
      # fhrs: groups of forecast hours for building sub-tasks
      #******************************************************
      if [ $modnam = hgefs ] ; then
        fhrs='fhr1 fhr2 fhr3'
      else
        fhrs='fhr1 fhr2 fhr3 fhr4'
      fi
    elif [ $field = sfc ] ; then
      if [ $modnam = hgefs ] ; then
        fhrs='fhr21 fhr22 fhr23'
      else
        fhrs='fhr21 fhr22 fhr23 fhr24'
      fi
    fi

    if [ $field = sfc ] ; then
       metplus_jobs="GenEnsProd EnsembleStat PointStat"
    elif [ $field = profile ] ; then
       metplus_jobs="EnsembleStat"
    elif [ $field = upper ] ; then
       metplus_jobs="GenEnsProd PointStat"
    fi

    for metplus_job in $metplus_jobs ; do
      #****************************************
      # Build a poe script to collect sub-tasks
      #****************************************
      >run_all_gens_${field}_${metplus_job}_g2o_poe.sh
      for vhour in ${validhours} ; do
        for fhr in $fhrs ; do
          if [ $modnam = hgefs ] ; then
            # For profile and upper
            if [ $fhr = fhr1 ] ; then
              leads_chk="000 006 012 018 024 030 036 042 048 054 060 066 072 078 084 090 096"
            elif [ $fhr = fhr2 ] ; then
              leads_chk="102 108 114 120 126 132 138 144 150 156 162 168 174 180 186 192"
            elif [ $fhr = fhr3 ] ; then
              leads_chk="198 204 210 216 222 228 234 240"
            # For sfc
            elif [ $fhr = fhr21 ] ; then
              leads_chk="000 006 012 018 024 030 036 042 048 054 060 066 072 078 084 090 096" 
            elif [ $fhr = fhr22 ] ; then
              leads_chk="102 108 114 120 126 132 138 144 150 156 162 168 174 180 186 192"
            elif [ $fhr = fhr23 ] ; then
              leads_chk="198 204 210 216 222 228 234 240" 
            fi
          else
            # For profile and upper
            if [ $fhr = fhr1 ] ; then
              leads_chk="000 006 012 018 024 030 036 042 048 054 060 066 072 078 084 090 096"
            elif [ $fhr = fhr2 ] ; then
              leads_chk="102 108 114 120 126 132 138 144 150 156 162 168 174 180 186 192"
            elif [ $fhr = fhr3 ] ; then
              leads_chk="198 204 210 216 222 228 234 240 246 252 258 264 270 276 282 288"
            elif [ $fhr = fhr4 ] ; then
              leads_chk="294 300 306 312 318 324 330 336 342 348 354 360 366 372 378 384"
            # For sfc
            elif [ $fhr = fhr21 ] ; then
              leads_chk="000 006 012 018 024 030 036 042 048 054 060 066 072 078 084 090 096"
            elif [ $fhr = fhr22 ] ; then
              leads_chk="102 108 114 120 126 132 138 144 150 156 162 168 174 180 186 192"
            elif [ $fhr = fhr23 ] ; then
              leads_chk="198 204 210 216 222 228 234 240 246 252 258 264 270 276 282 288"
            elif [ $fhr = fhr24 ] ; then
              leads_chk="294 300 306 312 318 324 330 336 342 348 354 360 366 372 378 384"
            fi
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
            elif [ $metplus_job = PointStat ]; then
              chk_file=$WORK/grid2obs/run_${modnam}_${vhour}_${fhr}_${field}_g2o/stat/${modnam}/GenEnsProd_${MODNAM}_${fieldUPPER}_BIN1_FHR${lead_chk}_${vday}_${vhour}0000V_ens.nc
              if [ -s $chk_file ]; then
                lead_arr[${#lead_arr[*]}+1]=${lead_chk}
              fi
            fi
          done
          lead=$(echo $(echo ${lead_arr[@]}) | tr ' ' ',')
          unset lead_arr
	  #*****************************
	  # Build sub-task scripts
	  #*****************************
          >run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh

          # Check for restart: check if the single sub-task is completed in the previous run
	  # If this task has been completed in the previous run, then skip it
	  if [ ! -e $COMOUTsmall/completed/run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.completed ] ; then

	  echo  "export output_base=$WORK/grid2obs/run_${modnam}_${vhour}_${fhr}_${field}_g2o" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          echo  "export modelpath=$COM_IN" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          echo  "export prepbufrhead=gfs" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          if [ $field = profile ] ; then
             echo  "export prepbufrgrid=prepbufr_profile.f00.nc" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          else
             echo  "export prepbufrgrid=prepbufr.f00.nc" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          fi
          echo  "export prepbufrpath=$COM_IN" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          echo  "export model=$modnam" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          echo  "export MODEL=${MODNAM}" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          echo  "export vbeg=$vhour" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          echo  "export vend=$vhour" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          echo  "export valid_increment=100" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          echo  "export modelhead=$modnam" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          echo  "export modeltail='.grib2'" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          echo  "export modelgrid=grid3.f" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          echo  "export extradir='atmos/'" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          echo  "export climpath=$CLIMO/era5" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          echo  "export climgrid=grid3" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          echo  "export climtail='.grib1'" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          echo  "export members=$mbrs" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          echo  "export lead=$lead" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh

          if [ $field = sfc ] || [ $field = upper ]; then
              conf_MODNAM=${MODNAM}
              if [ $metplus_job = GenEnsProd ] || [ $metplus_job = EnsembleStat ] ; then
                echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/${metplus_job}_fcst${conf_MODNAM}_obsPREPBUFR_${fieldUPPER}_climoERA5.conf " >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
                echo "export err=\$?; err_chk" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
              elif [ $metplus_job = PointStat ]; then
                echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/${metplus_job}_fcst${conf_MODNAM}_obsPREPBUFR_${fieldUPPER}_mean_climoERA5.conf " >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
                echo "export err=\$?; err_chk" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
              fi
          elif [ $field = profile ] ; then
              echo "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/${metplus_job}_fcst${MODNAM}_obsPREPBUFR_${fieldUPPER}.conf" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
              echo "export err=\$?; err_chk" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          fi

          if [ $metplus_job = EnsembleStat ] ; then
              if [ $SENDCOM="YES" ] ; then
                  echo "for FILE in \$output_base/stat/${modnam}/ensemble_stat*.stat ; do" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
                  echo "  if [ -s \$FILE ]; then" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
                  echo "    cp -v \$FILE $COMOUTsmall" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
                  echo "  fi" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
                  echo "done" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
               fi
          elif [ $metplus_job = PointStat ]; then
              if [ $SENDCOM="YES" ] ; then
                  echo "for FILE in \$output_base/stat/${modnam}/point_stat*.stat ; do" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
                  echo "  if [ -s \$FILE ]; then" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
                  echo "    cp -v \$FILE $COMOUTsmall" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
                  echo "  fi" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
                  echo "done" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
              fi
          fi

          # Indicate sub-task is completed for restart 
	  echo ">$WORK/completed/run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.completed" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
	  echo "echo "${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o task is completed" >> $WORK/completed/run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.completed" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh

          # Save files for restart
	  echo "if [ $SENDCOM = YES ] ; then" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          echo "  cp -f $WORK/completed/run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.completed $COMOUTsmall/completed" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh 
	  echo "  if [ -d $WORK/grid2obs/run_${modnam}_${vhour}_${fhr}_${field}_g2o/stat/${modnam} ] ; then" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
	  echo "    mkdir -p $COMOUTsmall/restart/grid2obs/run_${modnam}_${vhour}_${fhr}_${field}_g2o/stat" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
	  echo "    cp -rfu $WORK/grid2obs/run_${modnam}_${vhour}_${fhr}_${field}_g2o/stat/${modnam} $COMOUTsmall/restart/grid2obs/run_${modnam}_${vhour}_${fhr}_${field}_g2o/stat" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
	  echo "  fi" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
	  echo "fi" >> run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh

	  chmod +x run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh
          echo "${DATA}/run_${modnam}_${vhour}_${fhr}_${field}_${metplus_job}_g2o.sh" >> run_all_gens_${field}_${metplus_job}_g2o_poe.sh
	  fi # end of check restart for sub-task

        done # end of fhrs loop
      done # end of validhours loop

    chmod 755 ${DATA}/run_all_gens_${field}_${metplus_job}_g2o_poe.sh

    #**********************************************
    # Run poe script in MPI parallel or in sequence
    #**********************************************
    if [ $run_mpi = yes ] ; then
      mpiexec -n 16 -ppn 16 --cpu-bind verbose,core cfp ${DATA}/run_all_gens_${field}_${metplus_job}_g2o_poe.sh
      export err=$?; err_chk
    else
      ${DATA}/run_all_gens_${field}_${metplus_job}_g2o_poe.sh
      export err=$?; err_chk
    fi
    done # end of metplus_jobs loop
done # end of fields loop

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
  $USHevs/${COMPONENT}/evs_${COMPONENT}_atmos_gather.sh $MODELNAME grid2obs 00 18
  export err=$?; err_chk
fi
