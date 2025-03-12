#!/bin/bash
################################################################################
# Name of Script: exevs_nfcens_wave_grid2obs_stats.sh                           
# Cited to former developers: Deanna Spindler / Deanna.Spindler@noaa.gov                                    
#                             Mallory Row / Mallory.Row@noaa.gov
# 
# Developer: Samira Ardani / samira.ardani@noaa.gov
#
# Purpose of Script: Run the grid2obs stats for any global wave model           
#                    (deterministic and ensemble: GEFS-Wave, GFS-Wave, NWPS)    
# 		    EVSv2 added features: 
# 		    1- FNMOC anf GEFS were added to plot against NFCENS (07/2024).	           
# 		    2- Added MPMD directories and updated the $DATA structure (03/2025).                                                                   
# Usage:                                                                        
#  Parameters: None                                                             
#  Input files:                                                                 
#     gdas.SFCSHP.${validdate}.nc                                                      
#     individual fcst grib2 files from ARCmodel                                 
#  Output files:                                                                
#     point_stat_fcstNFCENS_obsGDAS_climoERA5_${lead}L_$VDATE_${valid}V.stat    
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
mkdir -p ${DATA}/SFCSHP
mkdir -p ${DATA}/all_stats
mkdir -p ${DATA}/jobs
mkdir -p ${DATA}/logs
mkdir -p ${DATA}/confs
mkdir -p ${DATA}/tmp
mkdir -p ${DATA}/job_work_dir

vhours='0 12'

lead_hours='0 12 24 36 48 60 72
            84 96 108 120 132 144 156
            168 180 192 204 216 228 240'

export GRID2OBS_CONF="${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}"
export OBSNAME="GDAS"
cd ${DATA}

############################################
# create point_stat files
############################################
echo ' '
echo 'Creating point_stat files'
for vhr in ${vhours} ; do
    vhr2=$(printf "%02d" "${vhr}")
    if [ ${vhr2} = '00' ] ; then
      climo_level_str="'{ name=\"HTSGW\"; level=\"(0,*,*)\"; }'"
    elif [ ${vhr2} = '12' ] ; then
      climo_level_str="'{ name=\"HTSGW\"; level=\"(4,*,*)\"; }'"
    fi
    for fhr in ${lead_hours} ; do
        matchtime=$(date --date="${VDATE} ${vhr2} ${fhr} hours ago" +"%Y%m%d %H")
        match_date=$(echo ${matchtime} | awk '{print $1}')
        match_hr=$(echo ${matchtime} | awk '{print $2}')
        match_fhr=$(printf "%02d" "${match_hr}")
        flead=$(printf "%03d" "${fhr}")
        flead2=$(printf "%02d" "${fhr}")
        EVSINgdasncfilename=${EVSINgdasnc}/${RUN}.${VDATE}/${MODELNAME}/${VERIF_CASE}/gdas.SFCSHP.${VDATE}${vhr2}.nc 
        DATAgdasncfilename=${DATA}/SFCSHP/gdas.SFCSHP.${VDATE}${vhr2}.nc
        EVSINmodelfilename=$COMIN/prep/$COMPONENT/${RUN}.${match_date}/${MODELNAME}/${VERIF_CASE}/HTSGW_mean.${match_date}.t${match_fhr}z.f${flead}.grib2
        DATAmodelfilename=$DATA/gribs/HTSGW_mean.${match_date}.t${match_fhr}z.f${flead}.grib2
        DATAstatfilename=$DATA/all_stats/point_stat_fcst${MODNAM}_obsGDAS_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
	job_work_dir_nfcens=$DATA/job_work_dir/PointStat_${MODNAM}_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}
	job_stat_file_nfcens=$job_work_dir_nfcens/point_stat_fcst${MODNAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
        COMOUTstatfilename=$COMOUTsmall/point_stat_fcst${MODNAM}_obsGDAS_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
	EVSINgefsfilename=$COMIN/prep/$COMPONENT/${RUN}.${match_date}/${MODELNAME}/${VERIF_CASE}/${MODEL1NAME}.${RUN}.${match_date}.t${match_fhr}z.mean.global.0p25.f${flead}.grib2
	DATAgefsfilename=$DATA/gribs/${MODEL1NAME}.${RUN}.${match_date}.t${match_fhr}z.mean.global.0p25.f${flead}.grib2
	DATAgefsstatfilename=$DATA/all_stats/point_stat_fcst${MOD1NAM}_obsGDAS_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
	job_work_dir_gefs=$DATA/job_work_dir/PointStat_${MOD1NAM}_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}
	job_stat_file_gefs=$job_work_dir_gefs/point_stat_fcst${MOD1NAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
	COMOUTgefsstatfilename=$COMOUTsmall/point_stat_fcst${MOD1NAM}_obsGDAS_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
	EVSINfnmocfilename=$COMIN/prep/$COMPONENT/${RUN}.${match_date}/${MODELNAME}/${VERIF_CASE}/wave_${match_date}${match_fhr}.f${flead}.grib2
	DATAfnmocfilename=$DATA/gribs/wave_${match_date}${match_fhr}.f${flead}.grib2
	DATAfnmocstatfilename=$DATA/all_stats/point_stat_fcst${MOD2NAM}_obsGDAS_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
	job_work_dir_fnmoc=$DATA/job_work_dir/PointStat_${MOD2NAM}_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}
	job_stat_file_fnmoc=$job_work_dir_fnmoc/point_stat_fcst${MOD2NAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
	COMOUTfnmocstatfilename=$COMOUTsmall/point_stat_fcst${MOD2NAM}_obsGDAS_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat

        ############################################################################################
	#Point-stat for nfcens:
	############################################################################################
	
        if [[ -s $COMOUTstatfilename ]]; then
            cp -v $COMOUTstatfilename $DATAstatfilename
        else
            if [[ ! -s $DATAgdasncfilename ]]; then
                if [[ -s $EVSINgdasncfilename ]]; then
                    cp -v $EVSINgdasncfilename $DATAgdasncfilename
                else
                    echo "WARNING: DOES NOT EXIST $EVSINgdasncfilename"
                fi
            fi
            if [[ -s $DATAgdasncfilename ]]; then
                if [[ ! -s $DATAmodelfilename ]]; then
                    if [[ -s $EVSINmodelfilename ]]; then
                        cp -v $EVSINmodelfilename $DATAmodelfilename
                    else
                        echo "WARNING: DOES NOT EXIST $EVSINmodelfilename"
                    fi
                fi
                if [[ -s $DATAmodelfilename ]]; then
                    echo "export climo_level_str=${climo_level_str}" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
                    echo "export VHR=${vhr2}" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
                    echo "export fhr=${flead}" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
		    echo "export job_work_dir_nfcens=${job_work_dir_nfcens}"  >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
                    echo "${METPLUS_PATH}/ush/run_metplus.py ${PARMevs}/metplus_config/machine.conf ${GRID2OBS_CONF}/PointStat_fcstNFCENS_obsGDAS_climoERA5_Wave_Multifield.conf" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
		    export err=$?; err_chk
                    echo "export err=\$?; err_chk" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
                    if [ $SENDCOM = YES ]; then
                        echo "if [ -f $job_stat_file_nfcens ]; then cp -v $job_stat_file_nfcens $COMOUTstatfilename; fi" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
                    fi

                    chmod +x ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
      
                    echo "${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh" >> ${DATA}/jobs/run_all_${MODELNAME}_${RUN}_g2o_poe.sh
                fi
            fi
        fi

        ###############################################################################
        # Point-stat for gefs model:
        ##############################################################################

        if [[ -s $COMOUTgefsstatfilename ]]; then
            cp -v $COMOUTgefsstatfilename $DATAgefsstatfilename
        else
            if [[ ! -s $DATAgdasncfilename ]]; then
                if [[ -s $EVSINgdasncfilename ]]; then
                    cp -v $EVSINgdasncfilename $DATAgdasncfilename
                else
                    echo "WARNING: DOES NOT EXIST $EVSINgdasncfilename"
                fi
            fi
            if [[ -s $DATAgdasncfilename ]]; then
                if [[ ! -s $DATAgefsfilename ]]; then
                    if [[ -s $EVSINgefsfilename ]]; then
                        cp -v $EVSINgefsfilename $DATAgefsfilename
                    else
                        echo "WARNING: DOES NOT EXIST $EVSINgefsfilename"
                    fi
                fi
                if [[ -s $DATAgefsfilename ]]; then
                    echo "export climo_level_str=${climo_level_str}" >> ${DATA}/jobs/run_${MODEL1NAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh

                    echo "export VHR=${vhr2}" >> ${DATA}/jobs/run_${MODEL1NAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
                    echo "export fhr=${flead}" >> ${DATA}/jobs/run_${MODEL1NAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
		    echo "export job_work_dir_gefs=${job_work_dir_gefs}" >> ${DATA}/jobs/run_${MODEL1NAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
                    echo "${METPLUS_PATH}/ush/run_metplus.py ${PARMevs}/metplus_config/machine.conf ${GRID2OBS_CONF}/PointStat_fcst${MOD1NAM}_obsGDAS_climoERA5_Wave_Multifield.conf" >> ${DATA}/jobs/run_${MODEL1NAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
		    export err=$?; err_chk
                    echo "export err=\$?; err_chk" >> ${DATA}/jobs/run_${MODEL1NAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
                    if [ $SENDCOM = YES ]; then
                        echo "if [ -f $job_stat_file_gefs ]; then cp -v $job_stat_file_gefs $COMOUTgefsstatfilename; fi" >> ${DATA}/jobs/run_${MODEL1NAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
                    fi

                    chmod +x ${DATA}/jobs/run_${MODEL1NAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
      
                    echo "${DATA}/jobs/run_${MODEL1NAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh" >> ${DATA}/jobs/run_all_${MODEL1NAME}_${RUN}_g2o_poe.sh
                fi
            fi
        fi


        ###############################################################################
        # Point-stat for fnmoc model:
        ##############################################################################

        if [[ -s $COMOUTfnmocstatfilename ]]; then
            cp -v $COMOUTfnmocstatfilename $DATAfnmocstatfilename
        else
            if [[ ! -s $DATAgdasncfilename ]]; then
                if [[ -s $EVSINgdasncfilename ]]; then
                    cp -v $EVSINgdasncfilename $DATAgdasncfilename
                else
                    echo "WARNING: DOES NOT EXIST $EVSINgdasncfilename"
                fi
            fi
            if [[ -s $DATAgdasncfilename ]]; then
                if [[ ! -s $DATAfnmocfilename ]]; then
                    if [[ -s $EVSINfnmocfilename ]]; then
                        cp -v $EVSINfnmocfilename $DATAfnmocfilename
                    else
                        echo "WARNING: DOES NOT EXIST $EVSINfnmocfilename"
                    fi
                fi
                if [[ -s $DATAfnmocfilename ]]; then
                    echo "export climo_level_str=${climo_level_str}" >> ${DATA}/jobs/run_${MODEL2NAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh

                    echo "export VHR=${vhr2}" >> ${DATA}/jobs/run_${MODEL2NAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
                    echo "export fhr=${flead}" >> ${DATA}/jobs/run_${MODEL2NAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
		    echo "export job_work_dir_fnmoc=${job_work_dir_fnmoc}" >> ${DATA}/jobs/run_${MODEL2NAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
                    echo "${METPLUS_PATH}/ush/run_metplus.py ${PARMevs}/metplus_config/machine.conf ${GRID2OBS_CONF}/PointStat_fcst${MOD2NAM}_obsGDAS_climoERA5_Wave_Multifield.conf" >> ${DATA}/jobs/run_${MODEL2NAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
		    export err=$?; err_chk
                    echo "export err=\$?; err_chk" >> ${DATA}/jobs/run_${MODEL2NAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
                    if [ $SENDCOM = YES ]; then
                        echo "if [ -f $job_stat_file_fnmoc ]; then cp -v $job_stat_file_fnmoc $COMOUTfnmocstatfilename; fi" >> ${DATA}/jobs/run_${MODEL2NAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
                    fi

                    chmod +x ${DATA}/jobs/run_${MODEL2NAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
      
                    echo "${DATA}/jobs/run_${MODEL2NAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh" >> ${DATA}/jobs/run_all_${MODEL2NAME}_${RUN}_g2o_poe.sh

                fi
            fi
        fi

    done
done

#######################
# Run the command file 
#######################
models='nfcens gefs fnmoc'
for model in ${models}; do
	if [[ -s ${DATA}/jobs/run_all_${model}_${RUN}_g2o_poe.sh ]]; then
    		if [ ${run_mpi} = 'yes' ] ; then
        	mpiexec -np 36 -ppn 36 --cpu-bind verbose,core cfp ${DATA}/jobs/run_all_${model}_${RUN}_g2o_poe.sh
    	else
        	echo "not running mpiexec"
        	sh ${DATA}/jobs/run_all_${model}_${RUN}_g2o_poe.sh
    	fi
	fi
done


############################################
## Copy all the jobs file into one directory
#############################################
for vhr in ${vhours} ; do
	vhr2=$(printf "%02d" "${vhr}")
	for fhr in ${lead_hours} ; do
		flead=$(printf "%03d" "${fhr}")
		flead2=$(printf "%02d" "${fhr}")
		for model in ${models}; do
			if [ ${model} = nfcens ]; then
			       job_stat_file=$DATA/job_work_dir/PointStat_${MODNAM}_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}/point_stat_fcst${MODNAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
			       all_stats_stat_file=$DATA/all_stats/point_stat_fcst${MODNAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
			       if [ -s $job_stat_file ]; then
				       cp -v $job_stat_file $all_stats_stat_file
			       fi

			elif [ ${model} = gefs ]; then
				job_stat_file=$DATA/job_work_dir/PointStat_${MOD1NAM}_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}/point_stat_fcst${MOD1NAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
				all_stats_stat_file=$DATA/all_stats/point_stat_fcst${MOD1NAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
			       if [ -s $job_stat_file ]; then
				       cp -v $job_stat_file $all_stats_stat_file
			       fi

			elif [ ${model} = fnmoc ]; then
				job_stat_file=$DATA/job_work_dir/PointStat_${MOD2NAM}_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}/point_stat_fcst${MOD2NAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
				all_stats_stat_file=$DATA/all_stats/point_stat_fcst${MOD2NAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
			       if [ -s $job_stat_file ]; then
				       cp -v $job_stat_file $all_stats_stat_file
			       fi
			fi
			
		done
	done
done

#######################
# Gather all the files 
#######################
if [ $gather = yes ] ; then

  # check to see if the small stat files are there
  nc=$(ls ${DATA}/all_stats/*stat | wc -l | awk '{print $1}')
  if [ "${nc}" != '0' ]; then
      echo " Found ${nc} ${DATA}/all_stats/*stat files for ${VDATE}"
      mkdir -p ${DATA}/stats
      export job_work_dir=$DATA/job_work_dir/StatAnalysis_${VDATE}
      
      # Use StatAnalysis to gather the small stat files into one file
      run_metplus.py ${PARMevs}/metplus_config/machine.conf ${GRID2OBS_CONF}/StatAnalysis_fcstNFCENS_obsGDAS.conf
      export err=$?; err_chk

      run_metplus.py ${PARMevs}/metplus_config/machine.conf ${GRID2OBS_CONF}/StatAnalysis_fcstGEFS_obsGDAS.conf
      export err=$?; err_chk
      
      run_metplus.py ${PARMevs}/metplus_config/machine.conf ${GRID2OBS_CONF}/StatAnalysis_fcstFNMOC_obsGDAS.conf
      export err=$?; err_chk

      for model in ${models}; do
	      if [ $SENDCOM = YES ]; then
		      if [ -s ${job_work_dir}/evs.stats.${model}.${RUN}.${VERIF_CASE}.v${VDATE}.stat ]; then
			      cp -v ${job_work_dir}/evs.stats.${model}.${RUN}.${VERIF_CASE}.v${VDATE}.stat ${COMOUTfinal}/.
		      else
			      echo "WARNING: DOES NOT EXIST ${job_work_dir}/evs.stats.${model}.${RUN}.${VERIF_CASE}.v${VDATE}.stat"
		      fi
	      fi
      done
  else
      echo "NOTE: NO SMALL STAT FILES FOUND IN ${DATA}/all_stats"
  fi
fi

#####################################################################
echo ' '
echo "Ending at : `date`"
echo ' '
echo " *** End of ${MODELNAME}-${RUN} grid2obs stat *** "
echo ' '

# End of NFCENS grid2obs stat script -------------------------------------- #
