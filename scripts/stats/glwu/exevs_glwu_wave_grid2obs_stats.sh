#!/bin/bash
###############################################################################
# Name of Script: exevs_glwu_stats.sh
# Purpose of Script: To create stat files for GLWU forecasts verified with
#    NDBC buoy data using MET/METplus.
# Developer: Samira Ardani (samira.ardani@noaa.gov)
# Citation:  Deanna Spindler / Deanna.Spindler@noaa.gov (global_det, global_ens)
#            Mallory Row / Mallory.Row@noaa.gov (global_det, global_ens)
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

vhours='1 7 13 19'

lead_hours='0 6 12 18 24 30 36 42 48 54 60 66 72 78
            84 90 96 102 108 114 120 126 132 138 144'

export GRID2OBS_CONF="${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}"

cd ${DATA}

############################################
# create point_stat files
############################################
echo ' '
echo 'Creating point_stat files'
for vhr in ${vhours} ; do
    vhr2=$(printf "%02d" "${vhr}")
    if [ ${vhr2} = '01' ] ; then
       wind_level_str="'{ name=\"WIND\"; level=\"(0,*,*)\"; }'"
       htsgw_level_str="'{ name=\"HTSGW\"; level=\"(0,*,*)\"; }'"
       perpw_level_str="'{ name=\"PERPW\"; level=\"(0,*,*)\"; }'"
    elif [ ${vhr2} = '07' ] ; then
       wind_level_str="'{ name=\"WIND\"; level=\"(2,*,*)\"; }'"
       htsgw_level_str="'{ name=\"HTSGW\"; level=\"(2,*,*)\"; }'"
       perpw_level_str="'{ name=\"PERPW\"; level=\"(2,*,*)\"; }'"
    elif [ ${vhr2} = '13' ] ; then
       wind_level_str="'{ name=\"WIND\"; level=\"(4,*,*)\"; }'"
       htsgw_level_str="'{ name=\"HTSGW\"; level=\"(4,*,*)\"; }'"
       perpw_level_str="'{ name=\"PERPW\"; level=\"(4,*,*)\"; }'"

    elif [ ${vhr2} = '19' ] ; then
       wind_level_str="'{ name=\"WIND\"; level=\"(6,*,*)\"; }'"
       htsgw_level_str="'{ name=\"HTSGW\"; level=\"(6,*,*)\"; }'"
       perpw_level_str="'{ name=\"PERPW\"; level=\"(6,*,*)\"; }'"
    fi
    for lead in ${lead_hours} ; do
       matchtime=$(date --date="${VDATE} ${vhr2} ${lead} hours ago" +"%Y%m%d %H")
       match_date=$(echo ${matchtime} | awk '{print $1}')
       match_hr=$(echo ${matchtime} | awk '{print $2}')
       match_fhr=$(printf "%02d" "${match_hr}")
       flead=$(printf "%03d" "${lead}")
       flead2=$(printf "%02d" "${lead}")
       EVSINndbcncfilename=${EVSINndbcnc}/${RUN}.${VDATE}/${MODELNAME}/${VERIF_CASE}/ndbc.${VDATE}.nc 
       DATAndbcncfilename=${DATA}/ncfiles/ndbc.${VDATE}.nc
       EVSINmodelfilename=$COMIN/prep/$COMPONENT/${RUN}.${match_date}/${MODELNAME}/${VERIF_CASE}/${MODELNAME}.grlc_2p5km.${match_date}.t${match_fhr}z.f${flead}.grib2                  
       DATAmodelfilename=$DATA/gribs/${MODELNAME}.grlc_2p5km.${match_date}.t${match_fhr}z.f${flead}.grib2
       DATAstatfilename=$DATA/all_stats/point_stat_fcst${MODNAM}_obsNDBC_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
       COMOUTstatfilename=$COMOUTsmall/point_stat_fcst${MODNAM}_obsNDBC_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
       if [[ -s $COMOUTstatfilename ]]; then
	       cp -v $COMOUTstatfilename $DATAstatfilename
       else
	       if [[ ! -s $DATAndbcncfilename ]]; then
		       if [[ -s $EVSINndbcncfilename ]]; then
			       cp -v $EVSINndbcncfilename $DATAndbcncfilename
		       else
			       echo "DOES NOT EXIST $EVSINndbcncfilename"
		       fi
	       fi
	       if [[ -s $DATAndbcncfilename ]]; then
		       if [[ ! -s $DATAmodelfilename ]]; then
			       if [[ -s $EVSINmodelfilename ]]; then
				       cp -v $EVSINmodelfilename $DATAmodelfilename
			       else
				       echo "DOES NOT EXIST $EVSINmodelfilename"
			       fi
		       fi
		       if [[ -s $DATAmodelfilename ]]; then
			       echo "export wind_level_str=${wind_level_str}" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
			       echo "export htsgw_level_str=${htsgw_level_str}" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
			       echo "export perpw_level_str=${perpw_level_str}" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
			       echo "export VHR=${vhr2}" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
			       echo "export lead=${flead}" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
			       echo "${METPLUS_PATH}/ush/run_metplus.py ${PARMevs}/metplus_config/machine.conf ${GRID2OBS_CONF}/PointStat_fcstGLWU_obsNDBC_climoERA5_Wave_Multifield.conf" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
			       echo "export err=\$?; err_chk" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
			       if [ $SENDCOM = YES ]; then
				       echo "cp -v $DATAstatfilename $COMOUTstatfilename" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
			       fi
			       chmod +x ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh
			       echo "${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${vhr2}_f${flead}_g2o.sh" >> ${DATA}/jobs/run_all_${MODELNAME}_${RUN}_g2o_poe.sh
		       fi
	       fi
       fi
done
done
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
#####################																					
# Run the command file
#####################                                                                                                                                                                        
if [[ -s ${DATA}/jobs/run_all_${MODELNAME}_${RUN}_g2o_poe.sh ]]; then
    if [ ${run_mpi} = 'yes' ] ; then
       export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
       mpiexec -np 36 -ppn 36 --cpu-bind verbose,core cfp ${DATA}/jobs/run_all_${MODELNAME}_${RUN}_g2o_poe.sh
    else
	echo "not running mpiexec"
	sh ${DATA}/jobs/run_all_${MODELNAME}_${RUN}_g2o_poe.sh
    fi
fi

##########################
# Gather all the files
#########################
if [ $gather = yes ] ; then
# check to see if the small stat files are there
   nc=$(ls ${DATA}/all_stats/*stat | wc -l | awk '{print $1}')
   if [ "${nc}" != '0' ]; then
           echo " Found ${nc} ${DATA}/all_stats/*stat files for ${VDATE}"
	   mkdir -p ${DATA}/stats
           # Use StatAnalysis to gather the small stat files into one file
           run_metplus.py ${PARMevs}/metplus_config/machine.conf ${GRID2OBS_CONF}/StatAnalysis_fcstGLWU_obsNDBC.conf
	   if [ $SENDCOM = YES ]; then
		   if [ -s ${DATA}/stats/evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat ]; then
			   cp -v ${DATA}/stats/evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat ${COMOUTfinal}/.
		   else
			   echo "DOES NOT EXIST ${DATA}/stats/evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat"
		   fi
	   fi
   else
	   echo "NO SMALL STAT FILES FOUND IN ${DATA}/all_stats"
   fi
fi

##############################################################################
echo ' '
echo "Ending at : `date`"
echo ' '
echo " *** End of ${MODELNAME}-${RUN} grid2obs stat *** "
echo ' '
################################ END OF SCRIPT ################################
