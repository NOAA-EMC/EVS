#!/bin/bash
###############################################################################
# Name of Script: exevs_nwps_wave_grid2obs_stats.sh
# Purpose of Script: To create stat files for NWPS forecasts verified with
#    NDBC buoy data using MET/METplus.
# Author: Samira Ardani (samira.ardani@noaa.gov)
#         - Added MPMD directories and updated the $DATA structure (03/2025).
#         - Added all available WFOs for stats analysis (08/2025). 
# Input fils:
# indivudual fcst grib2 files from ARCmodel
# Output files:
# Point_stat_fcstNWPS_obs_${lead}L_$VDATE_${valid}V.stat
###############################################################################

set -x


############################
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
mkdir -p ${DATA}/logs
mkdir -p ${DATA}/confs
mkdir -p ${DATA}/tmp
mkdir -p ${DATA}/SFCSHP
mkdir -p ${DATA}/job_work_dir

vhours='00 06 12 18'
WFO='aer afg ajk alu akq box car chs gys olm lwx mhx okx phi gum hfo bro crp hgx jax key lch lix mfl mlb mob sju tae tbw eka lox mfr mtr pqr sew sgx'
CG='CG1'
lead_hours='0 24 48 72 96 120 144'


export GRID2OBS_CONF="${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}"

cd ${DATA}

############################################
# create point_stat files
############################################
echo ' '
echo 'Creating point_stat files'

for wfo in ${WFO}; do
	export wfo=$wfo
	mkdir -p ${DATA}/jobs/${wfo}
	mkdir -p $COMOUTsmall/${wfo}
	mkdir -p ${DATA}/all_stats/${wfo}
	mkdir -p ${DATA}/stats
	mkdir -p ${DATA}/stats/${wfo}
	for cg in ${CG}; do 
		for vhr in ${vhours} ; do
    			vhr2=$(printf "%02d" "${vhr}")
    			if [ ${vhr2} = '00' ] ; then
       				wind_level_str="'{ name=\"WIND\"; level=\"(0,*,*)\"; }'"
       				htsgw_level_str="'{ name=\"HTSGW\"; level=\"(0,*,*)\"; }'"
       				perpw_level_str="'{ name=\"PERPW\"; level=\"(0,*,*)\"; }'"
       				wdir_level_str="'{ name=\"WDIR\"; level=\"(0,*,*)\"; }'"
    			elif [ ${vhr2} = '06' ] ; then
       				wind_level_str="'{ name=\"WIND\"; level=\"(2,*,*)\"; }'"
       				htsgw_level_str="'{ name=\"HTSGW\"; level=\"(2,*,*)\"; }'"
       				perpw_level_str="'{ name=\"PERPW\"; level=\"(2,*,*)\"; }'"
       				wdir_level_str="'{ name=\"WDIR\"; level=\"(2,*,*)\"; }'"
    			elif [ ${vhr2} = '12' ] ; then
				wind_level_str="'{ name=\"WIND\"; level=\"(4,*,*)\"; }'"
				htsgw_level_str="'{ name=\"HTSGW\"; level=\"(4,*,*)\"; }'"
				perpw_level_str="'{ name=\"PERPW\"; level=\"(4,*,*)\"; }'"
				wdir_level_str="'{ name=\"WDIR\"; level=\"(4,*,*)\"; }'"
			elif [ ${vhr2} = '18' ] ; then
       				wind_level_str="'{ name=\"WIND\"; level=\"(6,*,*)\"; }'"
       				htsgw_level_str="'{ name=\"HTSGW\"; level=\"(6,*,*)\"; }'"
       				perpw_level_str="'{ name=\"PERPW\"; level=\"(6,*,*)\"; }'"
       				wdir_level_str="'{ name=\"WDIR\"; level=\"(6,*,*)\"; }'"
    			fi

    			for lead in ${lead_hours} ; do
	    			matchtime=$(date --date="${VDATE} ${vhr2} ${lead} hours ago" +"%Y%m%d %H")
	    			match_date=$(echo ${matchtime} | awk '{print $1}')
	    			match_hr=$(echo ${matchtime} | awk '{print $2}')
	    			match_fhr=$(printf "%02d" "${match_hr}")
	    			flead=$(printf "%03d" "${lead}")
	    			flead2=$(printf "%02d" "${lead}")
	    
	    			EVSINmodelfilename=$COMIN/prep/$COMPONENT/${RUN}.${match_date}/${MODELNAME}/${VERIF_CASE}/${wfo}_${MODELNAME}_${cg}.${match_date}.t${match_fhr}z.f${flead}.grib2
	    			DATAmodelfilename=$DATA/gribs/${wfo}_${MODELNAME}_${cg}.${match_date}.t${match_fhr}z.f${flead}.grib2
	    			for OBSNAME in NDBC; do
		    			export OBSNAME=${OBSNAME}
			    		EVSINobsfilename=${EVSINndbcnc}/${RUN}.${VDATE}/ndbc/${VERIF_CASE}/ndbc.${VDATE}.nc
			    		DATAobsfilename=${DATA}/ncfiles/ndbc.${VDATE}.nc
	    			done
			        job_work_dir=$DATA/job_work_dir/${wfo}/PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}
			        job_stat_file=$job_work_dir/point_stat_fcst${MODNAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat	
				DATAstatfilename=$DATA/all_stats/${wfo}/point_stat_fcst${MODNAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
				COMOUTstatfilename=$COMOUTsmall/${wfo}/point_stat_fcst${MODNAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
	    			
				if [[ -s $COMOUTstatfilename ]]; then
			    		echo "RESTART: Copy the files"
					cp -v $COMOUTstatfilename $DATAstatfilename
				else
					if [[ ! -s $DATAobsfilename ]]; then
						if [[ -s $EVSINobsfilename ]]; then
							cp -v $EVSINobsfilename $DATAobsfilename
						else
							echo "DOES NOT EXIST $EVSINobsfilename"
						fi
					fi
					if [[ -s $DATAobsfilename ]]; then
			    			if [[ ! -s $DATAmodelfilename ]]; then
				    			if [[ -s $EVSINmodelfilename ]]; then
				    				cp -v  $EVSINmodelfilename $DATAmodelfilename
			    				else
				    				echo "DOES NOT EXIST $EVSINmodelfilename"
			    				fi
		    				fi
			    			if [[ -s $DATAmodelfilename ]]; then
						    	echo "export wind_level_str=${wind_level_str}" >> ${DATA}/jobs/${wfo}/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
				       		    	echo "export htsgw_level_str=${htsgw_level_str}" >> ${DATA}/jobs/${wfo}/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
						    	echo "export perpw_level_str=${perpw_level_str}" >> ${DATA}/jobs/${wfo}/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
						    	echo "export wdir_level_str=${wdir_level_str}" >> ${DATA}/jobs/${wfo}/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
						    	echo "export VHR=${vhr2}" >> ${DATA}/jobs/${wfo}/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
						    	echo "export lead=${flead}" >> ${DATA}/jobs/${wfo}/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
							echo "export wfo=${wfo}" >> ${DATA}/jobs/${wfo}/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
						    	echo "export job_work_dir=${job_work_dir}" >> ${DATA}/jobs/${wfo}/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
							echo "${METPLUS_PATH}/ush/run_metplus.py ${PARMevs}/metplus_config/machine.conf ${GRID2OBS_CONF}/PointStat_fcstNWPS_obs${OBSNAME}_climoERA5_Wave_Multifield.conf" >> ${DATA}/jobs/${wfo}/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
						    	echo "export err=\$?; err_chk" >> ${DATA}/jobs/${wfo}/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
						    	if [ $SENDCOM = YES ]; then
							    	echo "if [ -s $job_stat_file ]; then cp -v $job_stat_file $COMOUTstatfilename; fi" >> ${DATA}/jobs/${wfo}/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
							fi
						    	chmod +x ${DATA}/jobs/${wfo}/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
						    	echo "${DATA}/jobs/${wfo}/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh" >> ${DATA}/jobs/${wfo}/run_all_${MODELNAME}_${RUN}_g2o_poe.sh
						else
							echo "DOES NOT EXIST $DATAmodelfilename"
				    		fi
			    		fi
				fi
			done
		done
	done

                                                                                                                                                                                             #########################																					
# Run the command file
#########################                                                                                                                                                                        
	if [[ -s ${DATA}/jobs/${wfo}/run_all_${MODELNAME}_${RUN}_g2o_poe.sh ]]; then
    		if [ ${run_mpi} = 'yes' ] ; then
       			mpiexec -np 36 -ppn 36 --cpu-bind verbose,core cfp ${DATA}/jobs/${wfo}/run_all_${MODELNAME}_${RUN}_g2o_poe.sh
       			export err=$?; err_chk

    		else
			echo "not running mpiexec"
			sh ${DATA}/jobs/${wfo}/run_all_${MODELNAME}_${RUN}_g2o_poe.sh
    		fi
	fi

###########################
## copy all the jobs files
###########################

	for vhr in ${vhours} ; do
		vhr2=$(printf "%02d" "${vhr}")
		for lead in ${lead_hours} ; do
			flead=$(printf "%03d" "${lead}")
			flead2=$(printf "%02d" "${lead}")
			job_stat_file=$DATA/job_work_dir/${wfo}/PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}/point_stat_fcst${MODNAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
			DATAstatfilename=$DATA/all_stats/${wfo}/point_stat_fcst${MODNAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
			if [ -s $job_stat_file ]; then
				cp -v $job_stat_file $DATAstatfilename
			fi
		done
	done	
##########################
# Gather all the files
#########################
	if [ $gather = yes ] ; then
	# check to see if the small stat files are there
	   nc=$(ls ${DATA}/all_stats/${wfo}/ | wc -l | awk '{print $1}')
	   if [ "${nc}" != '0' ]; then
		   echo " Found ${nc} ${DATA}/all_stats/${wfo}/*stat files for ${VDATE}"
		   export job_work_dir=$DATA/job_work_dir/StatAnalysis_${VDATE}
		   mkdir -p $job_work_dir/${wfo}
                   # Use StatAnalysis to gather the small stat files into one file
		   run_metplus.py ${PARMevs}/metplus_config/machine.conf ${GRID2OBS_CONF}/StatAnalysis_fcstNWPS_obs$OBSNAME.conf
		   export err=$?; err_chk

		   if [ $SENDCOM = YES ]; then
			   if [ -s ${job_work_dir}/${wfo}/evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat ]; then
				   cp -v ${job_work_dir}/${wfo}/evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat ${COMOUTfinal}/evs.stats.${MODELNAME}.${wfo}.${RUN}.${VERIF_CASE}.v${VDATE}.stat 
			   else
				   echo "DOES NOT EXIST ${job_work_dir}/${wfo}/evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat"
			   fi
		   fi
	   else
		   echo "NOTE:NO SMALL STAT FILES FOUND IN ${DATA}/all_stats/${wfo}"
	   fi
	fi
done
###############################################################################
echo ' '
echo "Ending at : `date`"
echo ' '
echo " *** End of ${MODELNAME}-${RUN} grid2obs stat *** "
echo ' '
################################ END OF SCRIPT ################################
