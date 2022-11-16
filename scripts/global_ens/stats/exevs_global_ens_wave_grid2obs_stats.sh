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

##########################
# get the model fcst files
##########################
set +x
echo ' '
echo 'Copying fcst files :'
echo '-----------------------------'
[[ "$LOUD" = YES ]] && set -x

mkdir -p ${DATA}/gribs

date_list="${PDYm1} ${PDYm2} ${PDYm3} ${PDYm4} ${PDYm5} ${PDYm6} ${PDYm7}
           ${PDYm8} ${PDYm9} ${PDYm10} ${PDYm11} ${PDYm12} ${PDYm13} ${PDYm14}
           ${PDYm15} ${PDYm16} ${PDYm17}"

for theDate in ${date_list}; do
  cp ${ARCgefs}/${RUN}.${theDate}/${MODELNAME}/${VERIF_CASE}/*global.0p25*grib2 ${DATA}/gribs/.
done

####################
# quick error check 
####################
nc=`ls ${DATA}/gribs/${MODELNAME}*grib2 | wc -l | awk '{print $1}'`
echo " Found ${nc} ${DATA}/gribs/${MODELNAME}*grib2 files for ${VDATE} "
if [ "${nc}" != '0' ]
then
  set +x
  echo "Successfully copied the GEFS-Wave grib2 files for ${VDATE}"
  [[ "$LOUD" = YES ]] && set -x
else
  set +x
  echo ' '
  echo '**************************************** '
  echo '*** ERROR : NO GEFS-Wave grib2 FILES *** '
  echo "      for ${VDATE} "
  echo '**************************************** '
  echo ' '
  echo "${MODELNAME}_${RUN} $VDATE $cycle : GEFS-Wave grib2 files missing."
  [[ "$LOUD" = YES ]] && set -x
  ./postmsg "$jlogfile" "FATAL ERROR : NO GEFS-Wave GRIB2 FILES for ${VDATE}"
  err_exit "FATAL ERROR: Did not copy the GEFS-Wave grib2 files for ${VDATE}"
fi

##############################################################
# check to see if the nc files have been made by the prep step
##############################################################
set +x
nc=`ls ${COMINgdasnc}/${RUN}.${VDATE}/${MODELNAME}/${VERIF_CASE}/gdas.*.nc | wc -l | awk '{print $1}'`
echo " Found ${nc} ${COMINgdasnc}/${RUN}.${VDATE}/${MODELNAME}/${VERIF_CASE}/gdas.*.nc files for ${VDATE} "
[[ "$LOUD" = YES ]] && set -x

if [ "${nc}" = '0' ]
then
  set +x
  echo ' '
  echo '**************************************** '
  echo '*** FATAL ERROR : NO GDAS.*.nc FILES *** '
  echo " in ${COMINgdasnc}/${RUN}.${VDATE}/${MODELNAME}/${VERIF_CASE}"
  echo '**************************************** '
  echo ' '
  echo "${MODELNAME}_${RUN} PointStat $VDATE : gdas.*.nc missing."
  [[ "$LOUD" = YES ]] && set -x
  ./postmsg "$jlogfile" "FATAL ERROR : NO gdas.*.nc OUTPUT FILES"
  err_exit "FATAL ERROR: PB2NC did not make the gdas.${VDATE}.nc files"  
fi

#########################
# copy the gdas nc files 
#########################
set +x
echo ' '
echo 'Copying GDAS netcdf files :'
echo '-----------------------------'
[[ "$LOUD" = YES ]] && set -x

mkdir -p ${DATA}/ncfiles
cp ${COMINgdasnc}/${RUN}.${VDATE}/${MODELNAME}/${VERIF_CASE}/gdas.*.nc ${DATA}/ncfiles/.

####################
# quick error check 
####################
nc=`ls ${DATA}/ncfiles/*nc | wc -l | awk '{print $1}'`
echo " Found ${nc} ${DATA}/ncfiles/*nc files for ${VDATE} "
if [ "${nc}" != '0' ]
then
  set +x
  echo "Successfully copied the GDAS netcdf files for ${VDATE}"
  [[ "$LOUD" = YES ]] && set -x
else
  set +x
  echo ' '
  echo '**************************************** '
  echo '*** ERROR : NO GDAS netcdf FILES *** '
  echo "      for ${VDATE} "
  echo '**************************************** '
  echo ' '
  echo "${MODELNAME}_${RUN} $VDATE $cycle : GDAS netcdf files missing."
  [[ "$LOUD" = YES ]] && set -x
  ./postmsg "$jlogfile" "FATAL ERROR : NO GDAS NETCDF FILES for ${VDATE}"
  err_exit "FATAL ERROR: Did not copy the GDAS netcdf files for ${VDATE}"
fi

#################################
# Make the command files for cfp 
#################################

cycles='00 06 12 18'
fhrs='fhr1 fhr2 fhr3 fhr4 fhr5 fhr6 fhr7 fhr8 fhr9'

export GRID2OBS_CONF="${PARMevs}/metplus_config/${COMPONENT}/${RUN}_${VERIF_CASE}/${STEP}"

cd ${DATA}
mkdir ${DATA}/all_stats
touch run_all_${MODELNAME}_${RUN}_g2o_poe.sh

for cyc in ${cycles}  ; do
  for fhr in ${fhrs} ; do
  # write the commands
    echo "export CYC=${cyc}" >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
    echo "export fhr=${fhr}" >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
    case ${fhr} in
    'fhr1')
      echo "export lead_hrs=0,6,12,18,24,30,36"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      ;;
    'fhr2')
      echo "export lead_hrs=42,48,54,60,66,72,78"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      ;;
    'fhr3')
      echo "export lead_hrs=84,90,96,102,108,114,120"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      ;;
    'fhr4')
      echo "export lead_hrs=126,132,138,144,150,156,162"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      ;;
    'fhr5')
      echo "export lead_hrs=168,174,180,186,192,198,204"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      ;;
    'fhr6')
      echo "export lead_hrs=210,216,222,228,234,240,246"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      ;;
    'fhr7')
      echo "export lead_hrs=252,258,264,270,276,282,288"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      ;;
    'fhr8')
      echo "export lead_hrs=294,300,306,312,318,324,330,336"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      ;;
    'fhr9')
      echo "export lead_hrs=342,348,354,360,366,372,378,384"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
      ;;
    esac
    echo "${METPLUS_PATH}/ush/run_metplus.py ${PARMevs}/metplus_config/machine.conf ${GRID2OBS_CONF}/PointStat_fcstGEFS_obsGDAS_climoERA5_Wave_Multifield.conf"  >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
    echo "export err=$?; err_chk" >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
    echo "cpreq ${DATA}/stats_${cyc}_${fhr}/*.stat ${COMOUTsmall}/." >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
    echo "mv ${DATA}/stats_${cyc}_${fhr}/*.stat ${DATA}/all_stats/." >> run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
    
    chmod +x run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh
    
    echo "run_${MODELNAME}_${RUN}_${cyc}_${fhr}_g2o.sh" >> run_all_${MODELNAME}_${RUN}_g2o_poe.sh
  done  # end of fhr
done  # end of cycles

chmod 775 run_all_${MODELNAME}_${RUN}_g2o_poe.sh

#######################
# Run the command file 
#######################
if [ ${run_mpi} = 'yes' ] ; then
  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
    mpiexec -np 36 --cpu-bind verbose,core --depth 3 cfp run_all_${MODELNAME}_${RUN}_g2o_poe.sh
else
  echo "not running mpiexec"
  sh run_all_${MODELNAME}_${RUN}_g2o_poe.sh
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
