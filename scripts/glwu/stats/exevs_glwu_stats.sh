#!/bin/bash
###############################################################################
# Name of Script: exevs_glwu_stats.sh
# Purpose of Script: To create stat files for GLWU forecasts verified with
#    NDBC buoy data using MET/METplus.
# Author: Samira Ardani (samira.ardani@noaa.gov)
###############################################################################

set -x

# check if ndbc nc file exists; exit if not
if [ ! -s $COMINobs/glwu.$VDATE/$RUN/ndbc.${VDATE}.nc ] ; then
   export subject="NDBC Data Missing for EVS GLWU"
   export maillist=${maillist:-'alicia.bentley@noaa.gov,samira.ardani@noaa.gov'}
   echo "Warning: No NDBC data was available for valid date $VDATE." > mailmsg
#   cat mailmsg | mail -s "$subject" $maillist
   exit 0
fi


############################
## grid2obs wave model stats 
#############################

cd $DATA
echo "in $0 JLOGFILE is $jlogfile"
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

cycles='00 06 12 18'

lead_hours='0 6 12 18 24 30 36 42 48 54 60 66 72 78
            84 90 96 102 108 114 120 126 132 138 144 150 156 162
            168 174 180 186 192 198 204 210 216 222 228 234 240 246
            252 258 264 270 276 282 288 294 300 306 312 318 324 330
	    336 342 348 354 360 366 372 378 384'
export GRID2OBS_CONF="${PARMevs}/metplus_config/${COMPONENT}/${RUN}_${VERIF_CASE}/${STEP}"
cd ${DATA}
############################################
# create point_stat files
############################################
echo ' '
echo 'Creating point_stat files'
for cyc in ${cycles} ; do
    #cyc2=$(printf "%02d" "${cyc}")
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
    for fhr in ${lead_hours} ; do
       matchtime=$(date --date="${VDATE} ${cyc} ${fhr} hours ago" +"%Y%m%d %H")
       match_date=$(echo ${matchtime} | awk '{print $1}')
       match_hr=$(echo ${matchtime} | awk '{print $2}')
       match_fhr=$(printf "%02d" "${match_hr}")
       flead=$(printf "%03d" "${fhr}")
       flead2=$(printf "%02d" "${fhr}")																				    COMINglwufilename=${COMINglwunc}/${RUN}.${VDATE}/${MODELNAME}/${VERIF_CASE}/glwu.${VDATE}${cyc2}.nc 
       DATAglwuncfilename=${DATA}/ncfiles/glwu.${VDATE}${cyc2}.nc
       COMINmodelfilename=$COMIN/prep/$COMPONENT/${RUN}.${match_date}/${MODELNAME}/${VERIF_CASE}/${MODELNAME}.${RUN}.${match_date}.t${match_fhr}z.nc                  
       DATAmodelfilename=$DATA/gribs/${MODELNAME}.${RUN}.${match_date}.t${match_fhr}z.nc
       DATAstatfilename=$DATA/all_stats/point_stat_fcst${MODNAM}_obsGLWU_NDBC_${flead2}0000L_${VDATE}_${cyc}0000V.stat
       COMOUTstatfilename=$COMOUTsmall/point_stat_fcst${MODNAM}_obsGLWU_NDBC_${flead2}0000L_${VDATE}_${cyc}0000V.stat
       if [[ -s $COMOUTstatfilename ]]; then
	       cp -v $COMOUTstatfilename $DATAstatfilename
       else
	       if [[ ! -s $DATAglwuncfilename ]]; then
		       if [[ -s $COMINglwuncfilename ]]; then
			       cp -v $COMINglwuncfilename $DATAglwuncfilename
		       else
			       echo "DOES NOT EXIST $COMINglwuncfilename"
		       fi
	       fi
	       if [[ -s $DATAglwuncfilename ]]; then
		       if [[ ! -s $DATAmodelfilename ]]; then
			       if [[ -s $COMINmodelfilename ]]; then
				       cp -v $COMINmodelfilename $DATAmodelfilename
			       else
				       echo "DOES NOT EXIST $COMINmodelfilename"
			       fi
		       fi
		       if [[ -s $DATAmodelfilename ]]; then
			       echo "export wind_level_str=${wind_level_str}" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${cyc}_f${flead}_g2o.sh
			       echo "export htsgw_level_str=${htsgw_level_str}" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${cyc}_f${flead}_g2o.sh
			       echo "export perpw_level_str=${perpw_level_str}" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${cyc}_f${flead}_g2o.sh
			       echo "export CYC=${cyc}" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${cyc}_f${flead}_g2o.sh
			       echo "export fhr=${flead}" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${cyc}_f${flead}_g2o.sh
			       echo "${METPLUS_PATH}/ush/run_metplus.py ${PARMevs}/metplus_config/machine.conf ${GRID2OBS_CONF}/PointStat_fcstGEFS_obsGDAS_climoERA5_Wave_Multifield.conf" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${cyc}_f${flead}_g2o.sh
			       echo "export err=$?; err_chk" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${cyc}_f${flead}_g2o.sh
			       if [ $SENDCOM = YES ]; then
				       echo "cp -v $DATAstatfilename $COMOUTstatfilename" >> ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${cyc}_f${flead}_g2o.sh
			       fi                                                                                                                                                                                           chmod +x ${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${cyc}_f${flead}_g2o.sh
			       echo "${DATA}/jobs/run_${MODELNAME}_${RUN}_${VDATE}${cyc}_f${flead}_g2o.sh" >> ${DATA}/jobs/run_all_${MODELNAME}_${RUN}_g2o_poe.sh
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
           run_metplus.py ${PARMevs}/metplus_config/machine.conf ${GRID2OBS_CONF}/StatAnalysis_fcstGLWU_obsGLWU.conf
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
echo ' '
echo "Ending at : `date`"
echo ' '
echo " *** End of ${MODELNAME}-${RUN} grid2obs stat *"              
echo ' '

##################################################################
# Revisit part below later and keep it in case you need to use it:

# run Point_Stat
run_metplus.py -c $CONFIGevs/metplus_glwu.conf \
-c $CONFIGevs/${VERIF_CASE}/$STEP/PointStat_fcstGLWU_obsNDBC_htsgw.conf

# check if stat files exist; exit if not
if [ ! -s $COMOUTsmall/point_stat_GLWU_NDBC_HTSGW_1440000L_${VDATE}_000000V.stat ] ; then
   echo "Missing GLWU_NDBC_HTSGW stat files for $VDATE" 
   exit
fi

# sum small stat files into one big file using Stat_Analysis
mkdir -p $COMOUTfinal

run_metplus.py -c $CONFIGevs/metplus_glwu.conf \
-c $CONFIGevs/${VERIF_CASE}/$STEP/StatAnalysis_fcstGLWU_obsNDBC.conf

# archive final stat file
rsync -av $COMOUTfinal $ARCHevs

exit

################################ END OF SCRIPT ################################
