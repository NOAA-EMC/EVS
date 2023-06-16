#!/bin/bash
################################################################################
# Name of Script: exevs_global_ens_wave_grid2obs_stats.sh                       
# Deanna Spindler / Deanna.Spindler@noaa.gov                                    
# Purpose of Script: Run the grid2obs stats for any global wave model           
#                    (deterministic and ensemble: GEFS-Wave, GFS-Wave, NWPS)    
#                                                                               
# Usage:                                                                        
#  Parameters: None                                                             
#  Input files:                                                                 
#     gdas.${validdate}.nc                                                      
#  Output files:                                                                
#     point_stat_fcstGEFS_obsGDAS_climoERA5_${lead}L_$VDATE_${valid}V.stat      
#  User controllable options: None                                              
################################################################################

set -x 
# Use LOUD variable to turn on/off trace.  Defaults to YES (on).
export LOUD=${LOUD:-YES}; [[ $LOUD = yes ]] && export LOUD=YES
[[ "$LOUD" != YES ]] && set +x

#############################
## grid2obs wave model stats 
#############################

cd $DATA
echo "in $0 JLOGFILE is $jlogfile"
echo "Starting grid2obs_stats for ${MODELNAME}_${RUN}"

set +x
echo ' '
echo ' ******************************************'
echo " *** ${MODELNAME}-${RUN} grid2obs stats ***"
echo ' ******************************************'
echo ' '
echo "Starting at : `date`"
echo '-------------'
echo ' '
[[ "$LOUD" = YES ]] && set -x

mkdir -p ${DATA}/gribs
mkdir -p ${DATA}/ncfiles
mkdir ${DATA}/all_stats

cycles='0 6 12 18'

lead_hours='0 6 12 18 24 30 36 42 48 54 60 66 72 78
            84 90 96 102 108 114 120 126 132 138 144 150 156 162
            168 174 180 186 192 198 204 210 216 222 228 234 240 246
            252 258 264 270 276 282 288 294 300 306 312 318 324 330 
            336 342 348 354 360 366 372 378 384'

fhrs='fhr1 fhr2 fhr3 fhr4 fhr5 fhr6 fhr7 fhr8 fhr9'

export GRID2OBS_CONF="${PARMevs}/metplus_config/${COMPONENT}/${RUN}_${VERIF_CASE}/${STEP}"

cd ${DATA}

for cyc in ${cycles} ; do

  ##########################
  # get the model fcst files
  ##########################
  set +x
  echo ' '
  echo 'Copying model fcst files :'
  echo '-----------------------------'
  [[ "$LOUD" = YES ]] && set -x

  # clear lead_hrs# from previous cycle
  lead_hrs1=''
  lead_hrs2=''
  lead_hrs3=''
  lead_hrs4=''
  lead_hrs5=''
  lead_hrs6=''
  lead_hrs7=''
  lead_hrs8=''
  lead_hrs9=''
  for fhr in ${lead_hours} ; do
    matchtime=$(date --date="${VDATE} ${cyc} ${fhr} hours ago" +"%Y%m%d %H")
    match_date=$(echo ${matchtime} | awk '{print $1}')
    match_hr=$(echo ${matchtime} | awk '{print $2}')
    match_fhr=$(printf "%02d" "${match_hr}")
    flead=$(printf "%03d" "${fhr}")
    filename=${MODELNAME}.${RUN}.${match_date}.t${match_fhr}z.mean.global.0p25.f${flead}.grib2
    # check to see if the file is in the archive
    if [[ -s ${ARCgefs}/${RUN}.${match_date}/${MODELNAME}/${VERIF_CASE}/${filename} ]]; then
      cp ${ARCgefs}/${RUN}.${match_date}/${MODELNAME}/${VERIF_CASE}/${filename} ${DATA}/gribs/.
    fi
    # check to see if the file was copied successfully
    if [[ -s ${DATA}/gribs/${filename} ]] ; then
      if (( ${fhr} <= 36 )) ; then
        lead_hrs1="${lead_hrs1}${lead_hrs1:+,}${fhr}"
      elif (( ${fhr} > 36 & ${fhr} <= 78 )) ; then
        lead_hrs2="${lead_hrs2}${lead_hrs2:+,}${fhr}"
      elif (( ${fhr} > 78 & ${fhr} <= 120 )) ; then
        lead_hrs3="${lead_hrs3}${lead_hrs3:+,}${fhr}"
      elif (( ${fhr} > 120 & ${fhr} <= 162 )) ; then
        lead_hrs4="${lead_hrs4}${lead_hrs4:+,}${fhr}"
      elif (( ${fhr} > 162 & ${fhr} <= 204 )) ; then
        lead_hrs5="${lead_hrs5}${lead_hrs5:+,}${fhr}"
      elif (( ${fhr} > 204 & ${fhr} <= 246 )) ; then
        lead_hrs6="${lead_hrs6}${lead_hrs6:+,}${fhr}"
      elif (( ${fhr} > 246 & ${fhr} <= 288 )) ; then
        lead_hrs7="${lead_hrs7}${lead_hrs7:+,}${fhr}"
      elif (( ${fhr} > 288 & ${fhr} <= 336 )) ; then
        lead_hrs8="${lead_hrs8}${lead_hrs8:+,}${fhr}"
      elif (( ${fhr} > 336 & ${fhr} <= 384 )) ; then
        lead_hrs9="${lead_hrs9}${lead_hrs9:+,}${fhr}"
      fi
    fi
  done

  ####################
  # quick error check 
  ####################
  nc=$(ls ${DATA}/gribs/${MODELNAME}*${cyc}*.grib2 | wc -l | awk '{print $1}')
  if [ "${nc}" != '0' ]
  then
    set +x
    echo "Successfully copied ${nc} GEFS-Wave grib2 files for ${VDATE} ${cyc}"
    [[ "$LOUD" = YES ]] && set -x
  else
    set +x
    echo ' '
    echo '**************************************** '
    echo '*** ERROR : NO GEFS-Wave grib2 FILES *** '
    echo "      for ${VDATE} ${cyc}"
    echo '**************************************** '
    echo ' '
    echo "${MODELNAME}_${RUN} $VDATE $cyc : GEFS-Wave grib2 files missing."
    [[ "$LOUD" = YES ]] && set -x
    ./postmsg "$jlogfile" "FATAL ERROR : NO GEFS-Wave GRIB2 FILES for ${VDATE} ${cyc}"
    err_exit "FATAL ERROR: Did not copy the GEFS-Wave grib2 files for ${VDATE} ${cyc}"
  fi 
  
  #########################
  # copy the gdas nc files 
  #########################
  set +x
  echo ' '
  echo 'Copying GDAS netcdf files :'
  echo '-----------------------------'
  [[ "$LOUD" = YES ]] && set -x
  
  # check to see if the file is in the archive
  cyc=$(printf "%02d" "${cyc}")
  if [[ -s ${COMINgdasnc}/${RUN}.${VDATE}/${MODELNAME}/${VERIF_CASE}/gdas.${VDATE}${cyc}.nc ]] ; then
    cp ${COMINgdasnc}/${RUN}.${VDATE}/${MODELNAME}/${VERIF_CASE}/gdas.${VDATE}${cyc}.nc ${DATA}/ncfiles/.
    # check to see if the file was copied successfully
    if [[ -s ${DATA}/ncfiles/gdas.${VDATE}${cyc}.nc ]] ; then
      found_cycles="${found_cycles}${found_cycles:+ }${cyc}"
    fi
  fi

  ####################
  # quick error check 
  ####################
  nc=`ls ${DATA}/ncfiles/gdas.${VDATE}${cyc}.nc | wc -l | awk '{print $1}'`
  echo " Found ${DATA}/ncfiles/gdas.${VDATE}${cyc}.nc for ${VDATE} "
  if [ "${nc}" != '0' ]
  then
    found_cycle='yes'
    set +x
    echo "Successfully copied ${nc} GDAS netcdf files for ${VDATE}"
    [[ "$LOUD" = YES ]] && set -x
  else
    found_cycle='no'
    set +x
    echo ' '
    echo '**************************************** '
    echo '*** ERROR : NO GDAS netcdf FILES *** '
    echo "      for ${VDATE} ${cyc} "
    echo '**************************************** '
    echo ' '
    echo "${MODELNAME}_${RUN} $VDATE $cyc : GDAS netcdf files missing."
    [[ "$LOUD" = YES ]] && set -x
    ./postmsg "$jlogfile" "FATAL ERROR : NO GDAS NETCDF FILES for ${VDATE} ${cyc}"
    err_exit "FATAL ERROR: Did not copy the GDAS netcdf files for ${VDATE} ${cyc}"
  fi

  #################################
  # Make the command files for cfp 
  #################################
  
  # only run for those cycles with GDAS data
  if [ ${found_cycle} = 'yes' ] ; then
  
    if [ ${cyc} = '00' ] ; then
      wind_level_str="'{ name=\"WIND\"; level=\"(0,*,*)\"; }'"
      htsgw_level_str="'{ name=\"HTSGW\"; level=\"(0,*,*)\"; }'"
      perpw_level_str="'{ name=\"PERPW\"; level=\"(0,*,*)\"; }'"
    elif [ ${cyc} = '06' ] ; then
      wind_level_str="'{ name=\"WIND\"; level=\"(2,*,*)\"; }'"
      htsgw_level_str="'{ name=\"HTSGW\"; level=\"(2,*,*)\"; }'"
      perpw_level_str="'{ name=\"PERPW\"; level=\"(2,*,*)\"; }'"
    elif [ ${cyc} = '12' ] ; then
      wind_level_str="'{ name=\"WIND\"; level=\"(4,*,*)\"; }'"
      htsgw_level_str="'{ name=\"HTSGW\"; level=\"(4,*,*)\"; }'"
      perpw_level_str="'{ name=\"PERPW\"; level=\"(4,*,*)\"; }'"
    elif [ ${cyc} = '18' ] ; then
      wind_level_str="'{ name=\"WIND\"; level=\"(6,*,*)\"; }'"
      htsgw_level_str="'{ name=\"HTSGW\"; level=\"(6,*,*)\"; }'"
      perpw_level_str="'{ name=\"PERPW\"; level=\"(6,*,*)\"; }'"
    fi
    
    for fhr in ${fhrs} ; do
    # write the commands
      echo "export wind_level_str=${wind_level_str}" >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      echo "export htsgw_level_str=${htsgw_level_str}" >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      echo "export perpw_level_str=${perpw_level_str}" >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      echo "export CYC=${cyc}" >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      echo "export fhr=${fhr}" >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      case ${fhr} in
        'fhr1')
          echo "export lead_hrs=${lead_hrs1}"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
          ;;
        'fhr2')
          echo "export lead_hrs=${lead_hrs2}"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
          ;;
        'fhr3')
          echo "export lead_hrs=${lead_hrs3}"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
          ;;
        'fhr4')
          echo "export lead_hrs=${lead_hrs4}"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
          ;;
        'fhr5')
          echo "export lead_hrs=${lead_hrs5}"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
          ;;
        'fhr6')
          echo "export lead_hrs=${lead_hrs6}"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
          ;;
        'fhr7')
          echo "export lead_hrs=${lead_hrs7}"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
          ;;
        'fhr8')
          echo "export lead_hrs=${lead_hrs8}"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
          ;;
        'fhr9')
          echo "export lead_hrs=${lead_hrs9}"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
          ;;
      esac
      echo "${METPLUS_PATH}/ush/run_metplus.py ${PARMevs}/metplus_config/machine.conf ${GRID2OBS_CONF}/PointStat_fcstGEFS_obsGDAS_climoERA5_Wave_Multifield.conf"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      echo "export err=$?; err_chk" >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      echo "cpreq ${DATA}/stats_${cyc}_${fhr}/*.stat ${COMOUTsmall}/." >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      echo "mv ${DATA}/stats_${cyc}_${fhr}/*.stat ${DATA}/all_stats/." >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      
      chmod +x run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      
      echo "${DATA}/run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh" >> ${DATA}/run_all_${MODELNAME}_${RUN}_g2o_poe.sh
    done  # end of fhr
  fi # found cycle    
done  # end of cycles 

chmod 775 ${DATA}/run_all_${MODELNAME}_${RUN}_g2o_poe.sh

#######################
# Run the command file 
#######################
if [ ${run_mpi} = 'yes' ] ; then
  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
    mpiexec -np 36 --cpu-bind verbose,core --depth 3 cfp ${DATA}/run_all_${MODELNAME}_${RUN}_g2o_poe.sh
else
  echo "not running mpiexec"
  sh ${DATA}/run_all_${MODELNAME}_${RUN}_g2o_poe.sh
fi

#######################
# Gather all the files 
#######################
if [ $gather = yes ] ; then

  # check to see if the small stat files are there
  nc=$(ls ${DATA}/all_stats/*stat | wc -l | awk '{print $1}')
  echo " Found ${nc} ${DATA}/all_stats/*stat files for ${VDATE} "
  if [ "${nc}" != '0' ]
  then
    set +x
    echo "Small stat files found for ${VDATE}"
    [[ "$LOUD" = YES ]] && set -x
  else
    set +x
    echo ' '
    echo '**************************************** '
    echo '*** ERROR : NO SMALL STAT FILES *** '
    echo "      found for ${VDATE} "
    echo '**************************************** '
    echo ' '
    echo "${MODELNAME}_${RUN} $VDATE $cycle : small STAT files missing."
    [[ "$LOUD" = YES ]] && set -x
    ./postmsg "$jlogfile" "FATAL ERROR : NO SMALL STAT FILES FOR ${VDATE}"
    err_exit "FATAL ERROR: Did not find any small stat files for ${VDATE}"
  fi
  
  mkdir -p ${DATA}/stats
  # Use StatAnalysis to gather the small stat files into one file
  run_metplus.py ${PARMevs}/metplus_config/machine.conf \
           ${GRID2OBS_CONF}/StatAnalysis_fcstGEFS_obsGDAS.conf

  # check to see if the large stat file was made, copy it to $COMOUTfinal
  nc=$(ls ${DATA}/stats/*stat | wc -l | awk '{print $1}')
  echo " Found ${nc} ${DATA}/stats/*stat files for ${VDATE} "
  if [ "${nc}" != '0' ]
  then
    set +x
    echo "Large stat file found for ${VDATE}"
    [[ "$LOUD" = YES ]] && set -x
    cpreq ${DATA}/stats/*stat ${COMOUTfinal}/.
  else
    set +x
    echo ' '
    echo '**************************************** '
    echo '*** ERROR : NO LARGE STAT FILE *** '
    echo "      found for ${VDATE} "
    echo '**************************************** '
    echo ' '
    echo "${MODELNAME}_${RUN} $VDATE $cycle : large STAT file missing."
    [[ "$LOUD" = YES ]] && set -x
    ./postmsg "$jlogfile" "FATAL ERROR : NO LARGE STAT FILE FOR ${VDATE}"
    err_exit "FATAL ERROR: Did not find the large stat file for ${VDATE}"
  fi
else  
  echo "not gathering small metplus stat files right now"
fi

msg="JOB $job HAS COMPLETED NORMALLY."
postmsg "$jlogfile" "$msg"

# --------------------------------------------------------------------------- #
# Ending output                                                                

set +x
echo ' '
echo "Ending at : `date`"
echo ' '
echo " *** End of ${MODELNAME}-${RUN} grid2obs stat *** "
echo ' '
[[ "$LOUD" = YES ]] && set -x

# End of GEFS-Wave grid2obs stat script -------------------------------------- #
