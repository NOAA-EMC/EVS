#!/bin/bash
################################################################################
# Name of Script: exevs_global_ens_wave_grid2obs_stats.sh                       
# Deanna Spindler / Deanna.Spindler@noaa.gov                                    
# Mallory Row / Mallory.Row@noaa.gov
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

#############################
## grid2obs wave model stats 
#############################

cd $DATA
echo "Starting grid2obs_stats for ${MODELNAME}_${RUN}"

echo ' '
echo ' ******************************************'
echo " *** ${MODELNAME}-${RUN} grid2obs stats ***"
echo ' ******************************************'
echo ' '
echo "Starting at : `date`"
echo '-------------'
echo ' '

mkdir -p ${DATA}/gribs
mkdir -p ${DATA}/ncfiles
mkdir -p ${DATA}/all_stats
mkdir -p ${DATA}/jobs
#mkdir -p ${DATA}/logs
mkdir -p ${DATA}/confs
mkdir -p ${DATA}/tmp

validhours='0 6 12 18'

lead_hours='0 6 12 18 24 30 36 42 48 54 60 66 72 78
            84 90 96 102 108 114 120 126 132 138 144 150 156 162
            168 174 180 186 192 198 204 210 216 222 228 234 240 246
            252 258 264 270 276 282 288 294 300 306 312 318 324 330 
            336 342 348 354 360 366 372 378 384'

export GRID2OBS_CONF="${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}"

cd ${DATA}

############################################
# create point_stat files
############################################
echo ' '
echo 'Creating point_stat files'
for vhour in ${validhours} ; do
    vhour2=$(printf "%02d" "${vhour}")
    if [ ${vhour2} = '00' ] ; then
      wind_level_str="'{ name=\"WIND\"; level=\"(0,*,*)\"; }'"
      htsgw_level_str="'{ name=\"HTSGW\"; level=\"(0,*,*)\"; }'"
      perpw_level_str="'{ name=\"PERPW\"; level=\"(0,*,*)\"; }'"
    elif [ ${vhour2} = '06' ] ; then
      wind_level_str="'{ name=\"WIND\"; level=\"(2,*,*)\"; }'"
      htsgw_level_str="'{ name=\"HTSGW\"; level=\"(2,*,*)\"; }'"
      perpw_level_str="'{ name=\"PERPW\"; level=\"(2,*,*)\"; }'"
    elif [ ${vhour2} = '12' ] ; then
      wind_level_str="'{ name=\"WIND\"; level=\"(4,*,*)\"; }'"
      htsgw_level_str="'{ name=\"HTSGW\"; level=\"(4,*,*)\"; }'"
      perpw_level_str="'{ name=\"PERPW\"; level=\"(4,*,*)\"; }'"
    elif [ ${vhour2} = '18' ] ; then
      wind_level_str="'{ name=\"WIND\"; level=\"(6,*,*)\"; }'"
      htsgw_level_str="'{ name=\"HTSGW\"; level=\"(6,*,*)\"; }'"
      perpw_level_str="'{ name=\"PERPW\"; level=\"(6,*,*)\"; }'"
    fi
    for fhr in ${lead_hours} ; do
        matchtime=$($NDATE -${fhr} ${VDATE}${vhour2})
        match_date=$(echo ${matchtime} | cut -c 1-8)
        match_hr=$(echo ${matchtime}  | cut -c 9-10)
        match_fhr=$(printf "%02d" "${match_hr}")
        flead=$(printf "%03d" "${fhr}")
        flead2=$(printf "%02d" "${fhr}")
        EVSgdasncfilename=${EVSINgdasnc}/${RUN}.${VDATE}/${MODELNAME}/${VERIF_CASE}/gdas.${VDATE}${vhour2}.nc 
        DATAgdasncfilename=${DATA}/ncfiles/gdas.${VDATE}${vhour2}.nc
        EVSmodelfilename=$COMIN/prep/$COMPONENT/${RUN}.${match_date}/${MODELNAME}/${VERIF_CASE}/${MODELNAME}.${RUN}.${match_date}.t${match_fhr}z.mean.global.0p25.f${flead}.grib2
        DATAmodelfilename=$DATA/gribs/${MODELNAME}.${RUN}.${match_date}.t${match_fhr}z.mean.global.0p25.f${flead}.grib2
        DATAstatfilename=$DATA/all_stats/point_stat_fcst${MODNAM}_obsGDAS_climoERA5_${flead2}0000L_${VDATE}_${vhour2}0000V.stat
        COMOUTstatfilename=$COMOUTsmall/point_stat_fcst${MODNAM}_obsGDAS_climoERA5_${flead2}0000L_${VDATE}_${vhour2}0000V.stat
        if [[ -s $COMOUTstatfilename ]]; then
            cpreq -v $COMOUTstatfilename $DATAstatfilename
        else
            if [[ ! -s $DATAgdasncfilename ]]; then
                if [[ -s $EVSgdasncfilename ]]; then
                    cpreq -v $EVSgdasncfilename $DATAgdasncfilename
                else
                    echo "WARNING: DOES NOT EXIST $EVSgdasncfilename"
                fi
            fi
            if [[ -s $DATAgdasncfilename ]]; then
                if [[ ! -s $DATAmodelfilename ]]; then
                    if [[ -s $EVSmodelfilename ]]; then
                        cpreq -v $EVSmodelfilename $DATAmodelfilename
                    else
                        echo "WARNING: DOES NOT EXIST $EVSmodelfilename"
                    fi
                fi
                if [[ -s $DATAmodelfilename ]]; then
                    echo "export wind_level_str=${wind_level_str}" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhour2}_f${flead}_g2o.sh
                    echo "export htsgw_level_str=${htsgw_level_str}" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhour2}_f${flead}_g2o.sh
                    echo "export perpw_level_str=${perpw_level_str}" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhour2}_f${flead}_g2o.sh
                    echo "export VHOUR=${vhour2}" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhour2}_f${flead}_g2o.sh
                    echo "export fhr=${flead}" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhour2}_f${flead}_g2o.sh
                    echo "${METPLUS_PATH}/ush/run_metplus.py ${PARMevs}/metplus_config/machine.conf ${GRID2OBS_CONF}/PointStat_fcstGEFS_obsGDAS_climoERA5_Wave_Multifield.conf" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhour2}_f${flead}_g2o.sh
                    echo "export err=\$?; err_chk" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhour2}_f${flead}_g2o.sh
                    if [ $SENDCOM = YES ]; then
                        echo "cp -v $DATAstatfilename $COMOUTstatfilename" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhour2}_f${flead}_g2o.sh
                    fi

                    chmod +x ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhour2}_f${flead}_g2o.sh
      
                    echo "${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhour2}_f${flead}_g2o.sh" >> ${DATA}/jobs/run_all_${MODELNAME}_${RUN}_g2o_poe.sh
                fi
            fi
        fi
    done
done

#######################
# Run the command file 
#######################
if [[ -s ${DATA}/jobs/run_all_${MODELNAME}_${RUN}_g2o_poe.sh ]]; then
    if [ ${run_mpi} = 'yes' ] ; then
        mpiexec -np 36 -ppn 36 --cpu-bind verbose,core cfp ${DATA}/jobs/run_all_${MODELNAME}_${RUN}_g2o_poe.sh
        export err=$?; err_chk
    else
        echo "not running mpiexec"
        ${DATA}/jobs/run_all_${MODELNAME}_${RUN}_g2o_poe.sh
        export err=$?; err_chk
    fi
fi

#######################
# Gather all the files 
#######################
if [ $gather = yes ] ; then
  # check to see if the small stat files are there
  nc=$(ls ${DATA}/all_stats/*stat | wc -l | awk '{print $1}')
  if [ "${nc}" != '0' ]; then
      echo " Found ${nc} ${DATA}/all_stats/*stat files for ${VDATE}"
      mkdir -p ${DATA}/stats
      # Use StatAnalysis to gather the small stat files into one file
      run_metplus.py ${PARMevs}/metplus_config/machine.conf ${GRID2OBS_CONF}/StatAnalysis_fcstGEFS_obsGDAS.conf
      export err=$?; err_chk
      if [ $SENDCOM = YES ]; then
          if [ -s ${DATA}/stats/evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat ]; then
              cp -v ${DATA}/stats/evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat ${COMOUTfinal}/.
          else
              echo "WARNING: DOES NOT EXIST ${DATA}/stats/evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat"
          fi
      fi
  else
      echo "WARNING: NO SMALL STAT FILES FOUND IN ${DATA}/all_stats, not running StatAnalysis"
  fi
fi
echo ' '
echo "Ending at : `date`"
echo ' '
echo " *** End of ${MODELNAME}-${RUN} grid2obs stat *** "
echo ' '
