#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_wave_grid2obs_stats.sh
# Developers: Deanna Spindler / Deanna.Spindler@noaa.gov
#             Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: This script is run for the global_det wave stats step
#                    for the grid-to-obs verification. It uses METplus to
#                    generate the statistics.
###############################################################################

set -x

#############################
## grid2obs wave model stats
#############################

cd $DATA
echo "in $0 JLOGFILE"
echo "Starting grid2obs_stats for ${MODELNAME} ${RUN}"
echo "Starting at : `date`"
echo ' '
echo " *** ${MODELNAME}-${RUN} grid2obs stats ***"
echo ' '

export MODNAM=`echo $MODELNAME | tr '[a-z]' '[A-Z]'`
mkdir -p ${DATA}/gribs
mkdir -p ${DATA}/ncfiles
mkdir -p ${DATA}/all_stats
mkdir -p ${DATA}/jobs
mkdir -p ${DATA}/logs
mkdir -p ${DATA}/confs
mkdir -p ${DATA}/tmp

valid_hours='0 6 12 18'
##########################
# get the model fcst files
##########################
if [ $MODELNAME == "gfs" ]; then
    cycles='0 6 12 18'
    lead_hours='0 6 12 18 24 30 36 42 48 54 60 66 72 78
                84 90 96 102 108 114 120 126 132 138 144 150 156 162
                168 174 180 186 192 198 204 210 216 222 228 234 240 246
                252 258 264 270 276 282 288 294 300 306 312 318 324 330
                336 342 348 354 360 366 372 378 384'
else
    echo ' '
    echo '**************************************** '
    echo "*** ERROR : ${MODELNAME} NOT VALID ***"
    echo '**************************************** '
    echo ' '
    echo "${MODELNAME}_${RUN} $VDATE : ${MODELNAME} not valid."
    ./postmsg "$jlogfile" "FATAL ERROR : ${MODELNAME} NOT VALID"
    err_exit "FATAL ERROR: ${MODELNAME} NOT VALID"
fi

############################################
# create ASCII2NC NBDC files and PB2NC GDAS files
############################################
poe_script=${DATA}/jobs/run_all_2NC_poe.sh
echo ' '
echo 'Creating NDBC ascii2nc files'
COMINasciiNDBC=$COMINndbc/prep/${COMPONENT}/wave.${VDATE}/ndbc
DATAascii2ncNDBC=${DATA}/ncfiles/ndbc.${VDATE}.nc
COMOUTascii2ncNDBC=$COMOUTndbc/ndbc.${VDATE}.nc
if [[ -s $COMOUTascii2ncNDBC ]]; then
    cp -v $COMOUTascii2ncNDBC $DATAascii2ncNDBC
else
    nbdc_txt_ncount=$(ls -l ${COMINasciiNDBC}/*.txt |wc -l)
    if [[ $nbdc_txt_ncount -ne 0 ]]; then
        echo "#!/bin/bash" >> ${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh
        echo "" >> ${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh
        echo "export COMINndbc=${COMINndbc}" >> ${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh
        echo "export DATA=$DATA" >> ${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh
        echo "export VDATE=$VDATE" >> ${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh
        echo "export MET_NDBC_STATIONS=${FIXevs}/ndbc_stations/ndbc_stations.xml" >> ${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh
        echo "run_metplus.py ${PARMevs}/metplus_config/machine.conf ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}/ASCII2NC_obsNDBC.conf" >> ${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh
        echo "export err=\$?; err_chk" >> ${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh
        if [ $SENDCOM = YES ]; then
            echo "cp -v $DATAascii2ncNDBC $COMOUTascii2ncNDBC" >> ${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh
            echo "export err=\$?; err_chk" >> ${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh
        fi
        chmod +x ${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh
        echo "${DATA}/jobs/run_ASCII2NC_NDBC_valid${VDATE}.sh" >> $poe_script
    fi
fi
echo ' '
echo 'Creating GDAS pb2nc files'
for vhr in ${valid_hours} ; do
    vhr2=$(printf "%02d" "${vhr}")
    COMINprepbufrGDAS=$COMINobsproc/gdas.${VDATE}/${vhr2}/atmos/gdas.t${vhr2}z.prepbufr
    DATApb2ncGDAS=${DATA}/ncfiles/gdas.${VDATE}${vhr2}.nc
    COMOUTpb2ncGDAS=$COMOUTprepbufr/gdas.${VDATE}${vhr2}.nc
    if [[ -s $COMOUTpb2ncGDAS ]]; then
        cp -v $COMOUTpb2ncGDAS $DATApb2ncGDAS
    else
        if [ ! -s $COMINprepbufrGDAS ] ; then
            if [ $SENDMAIL = YES ] ; then
                export subject="GDAS Prepbufr Data Missing for EVS ${COMPONENT}"
                echo "Warning: No GDAS Prepbufr was available for valid date ${VDATE}${vhr}" > mailmsg
                echo "Missing file is $COMINprepbufrGDAS" >> mailmsg
                echo "Job ID: $jobid" >> mailmsg
                cat mailmsg | mail -s "$subject" $maillist
            fi
        else
            echo "#!/bin/bash" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${vhr2}.sh
            echo "" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${vhr2}.sh
            echo "export COMINobsproc=${COMINobsproc}" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${vhr2}.sh
            echo "export DATA=$DATA" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${vhr2}.sh
            echo "export VDATE=$VDATE" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${vhr2}.sh
            echo "export vhr2=$vhr2" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${vhr2}.sh
            echo "run_metplus.py ${PARMevs}/metplus_config/machine.conf ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}/PB2NC_obsPrepbufrGDAS.conf" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${vhr2}.sh
            echo "export err=\$?; err_chk" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${vhr2}.sh
            if [ $SENDCOM = YES ]; then
                echo "cp -v $DATApb2ncGDAS $COMOUTpb2ncGDAS" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${vhr2}.sh
                echo "export err=\$?; err_chk" >> ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${vhr2}.sh
            fi
            chmod +x ${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${vhr2}.sh
            echo "${DATA}/jobs/run_PB2NC_GDAS_valid${VDATE}${vhr2}.sh" >> $poe_script
        fi
    fi
done
ncount_job=$(ls -l ${DATA}/jobs/run*2NC_*.sh |wc -l)
if [[ $ncount_job -gt 0 ]]; then
    if [ $USE_CFP = YES ]; then
        chmod 775 $poe_script
        export MP_PGMMODEL=mpmd
        export MP_CMDFILE=${poe_script}
        nselect=$(cat $PBS_NODEFILE | wc -l)
        nnp=$(($nselect * $nproc))
        launcher="mpiexec -np ${nnp} -ppn ${nproc} --cpu-bind verbose,depth cfp"
        $launcher $MP_CMDFILE
    else
        /bin/bash ${poe_script}
    fi
fi
####################
# quick error check
####################
nc=`ls ${DATA}/ncfiles/gdas.${VDATE}*.nc | wc -l | awk '{print $1}'`
echo " Found ${DATA}/ncfiles/gdas.${VDATE}*.nc for ${VDATE}"
if [ "${nc}" != '0' ]; then
    echo "Successfully found ${nc} GDAS pb2nc files for valid date ${VDATE}"
else
    echo ' '
    echo '**************************************** '
    echo '*** WARNING : NO GDAS netcdf FILES *** '
    echo "      for valid date ${VDATE} "
    echo '**************************************** '
    echo ' '
    echo "${MODELNAME}_${RUN} $VDATE : GDAS pb2nc files missing."
    ./postmsg "$jlogfile" "WARNING : NO GDAS PB2NC FILES for valid date ${VDATE}"
fi
nc=`ls ${DATA}/ncfiles/ndbc.${VDATE}*.nc | wc -l | awk '{print $1}'`
echo " Found ${DATA}/ncfiles/ndbc.${VDATE}*.nc for ${VDATE}"
if [ "${nc}" != '0' ]; then
    echo "Successfully found ${nc} NDBC ascii2nc files for valid date ${VDATE}"
else
    echo ' '
    echo '**************************************** '
    echo '*** WARNING : NO NDBC netcdf FILES *** '
    echo "      for valid date ${VDATE} "
    echo '**************************************** '
    echo ' '
    echo "${MODELNAME}_${RUN} $VDATE : NDBC ascii2nc files missing."
    ./postmsg "$jlogfile" "WARNING : NO NDBC ASCII2NC FILES for valid date ${VDATE}"
fi

############################################
# create point_stat files
############################################
echo ' '
echo 'Creating point_stat files'
poe_script=${DATA}/jobs/run_all_PointStat_poe.sh
for vhr in ${valid_hours} ; do
    vhr2=$(printf "%02d" "${vhr}")
    if [ ${vhr2} = '00' ] ; then
        wind_level_str="'{ name=\"WIND\"; level=\"(0,*,*)\"; }'"
        htsgw_level_str="'{ name=\"HTSGW\"; level=\"(0,*,*)\"; }'"
        perpw_level_str="'{ name=\"PERPW\"; level=\"(0,*,*)\"; }'"
    elif [ ${vhr2} = '06' ] ; then
        wind_level_str="'{ name=\"WIND\"; level=\"(2,*,*)\"; }'"
        htsgw_level_str="'{ name=\"HTSGW\"; level=\"(2,*,*)\"; }'"
        perpw_level_str="'{ name=\"PERPW\"; level=\"(2,*,*)\"; }'"
    elif [ ${vhr2} = '12' ] ; then
        wind_level_str="'{ name=\"WIND\"; level=\"(4,*,*)\"; }'"
        htsgw_level_str="'{ name=\"HTSGW\"; level=\"(4,*,*)\"; }'"
        perpw_level_str="'{ name=\"PERPW\"; level=\"(4,*,*)\"; }'"
    elif [ ${vhr2} = '18' ] ; then
        wind_level_str="'{ name=\"WIND\"; level=\"(6,*,*)\"; }'"
        htsgw_level_str="'{ name=\"HTSGW\"; level=\"(6,*,*)\"; }'"
        perpw_level_str="'{ name=\"PERPW\"; level=\"(6,*,*)\"; }'"
    fi
    for fhr in ${lead_hours} ; do
        matchtime=$(date --date="${VDATE} ${vhr} ${fhr} hours ago" +"%Y%m%d %H")
        match_date=$(echo ${matchtime} | awk '{print $1}')
        match_hr=$(echo ${matchtime} | awk '{print $2}')
        match_fhr=$(printf "%02d" "${match_hr}")
        flead=$(printf "%03d" "${fhr}")
        flead2=$(printf "%02d" "${fhr}")
        if [ $MODELNAME == "gfs" ]; then
            COMINmodelfilename=$COMIN/prep/$COMPONENT/${RUN}.${match_date}/${MODELNAME}/${MODELNAME}${RUN}.${match_date}.t${match_fhr}z.global.0p25.f${flead}.grib2
        fi
        DATAmodelfilename=$DATA/gribs/${MODELNAME}${RUN}.${match_date}.t${match_fhr}z.global.0p25.f${flead}.grib2
        if [[ -s $COMINmodelfilename ]]; then
            if [[ ! -s $DATAmodelfilename ]]; then
                cp -v $COMINmodelfilename $DATAmodelfilename
            fi
        else
            echo "DOES NOT EXIST $COMINmodelfilename"
        fi
        if [[ -s $DATAmodelfilename ]]; then
            for OBSNAME in GDAS NDBC; do
                if [ $OBSNAME = GDAS ]; then
                    DATAOBSNAME=${DATA}/ncfiles/gdas.${VDATE}${vhr2}.nc
                elif [ $OBSNAME = NDBC ]; then
                    DATAOBSNAME=${DATA}/ncfiles/ndbc.${VDATE}.nc
                fi
                DATAstatfilename=$DATA/all_stats/point_stat_fcst${MODNAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
                COMOUTstatfilename=$COMOUTsmall/point_stat_fcst${MODNAM}_obs${OBSNAME}_climoERA5_${flead2}0000L_${VDATE}_${vhr2}0000V.stat
                if [[ -s $COMOUTstatfilename ]]; then
                    cp -v $COMOUTstatfilename $DATAstatfilename
                else
                    if [[ -s $DATAOBSNAME ]]; then
                        echo "#!/bin/bash" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}.sh
                        echo "" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}.sh
                        echo "export FIXevs=$FIXevs" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}.sh
                        echo "export DATA=$DATA" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}.sh
                        echo "export VDATE=$VDATE" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}.sh
                        echo "export vhr2=$vhr2" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}.sh
                        echo "export wind_level_str=${wind_level_str}" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}.sh
                        echo "export htsgw_level_str=${htsgw_level_str}" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}.sh
                        echo "export perpw_level_str=${perpw_level_str}" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}.sh
                        echo "export flead=${flead}" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}.sh
                        echo "export MODNAM=${MODNAM}" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}.sh
                        echo "run_metplus.py ${PARMevs}/metplus_config/machine.conf ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}/PointStat_fcstGLOBAL_DET_obs${OBSNAME}_climoERA5_Wave_Multifield.conf" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}.sh
                        echo "export err=\$?; err_chk" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}.sh
                        if [ $SENDCOM = YES ]; then
                            echo "cp -v $DATAstatfilename $COMOUTstatfilename" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}.sh
                            echo "export err=\$?; err_chk" >> ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}.sh
                        fi
                        chmod +x ${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}.sh
                        echo "${DATA}/jobs/run_PointStat_obs${OBSNAME}_valid${VDATE}${vhr2}_f${flead}.sh" >> $poe_script
                    fi
                fi
            done
        fi
    done
done
ncount_job=$(ls -l ${DATA}/jobs/run_PointStat*.sh |wc -l)
if [[ $ncount_job -gt 0 ]]; then
    if [ $USE_CFP = YES ]; then
        chmod 775 $poe_script
        export MP_PGMMODEL=mpmd
        export MP_CMDFILE=${poe_script}
        nselect=$(cat $PBS_NODEFILE | wc -l)
        nnp=$(($nselect * $nproc))
        launcher="mpiexec -np ${nnp} -ppn ${nproc} --cpu-bind verbose,depth cfp"
        $launcher $MP_CMDFILE
    else
        /bin/bash ${poe_script}
    fi
fi

####################
# gather all the files
####################
nc=$(ls ${DATA}/all_stats/*stat | wc -l | awk '{print $1}')
echo " Found ${nc} ${DATA}/all_stats/*stat files for valid date ${VDATE} "
if [ "${nc}" != '0' ]; then
    echo "Small stat files found for valid date ${VDATE}"
    # Use StatAnalysis to gather the small stat files into one file
    run_metplus.py ${PARMevs}/metplus_config/machine.conf ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}/StatAnalysis_fcstGLOBAL_DET.conf
else
    echo ' '
    echo '**************************************** '
    echo '*** ERROR : NO SMALL STAT FILES *** '
    echo "      found for valid date ${VDATE} "
    echo '**************************************** '
    echo ' '
    echo "${MODELNAME}_${RUN} $VDATE : small STAT files missing."
    ./postmsg "$jlogfile" "FATAL ERROR : NO SMALL STAT FILES FOR valid date ${VDATE}"
    err_exit "FATAL ERROR: Did not find any small stat files for valid date ${VDATE}"
fi
# check to see if the large stat file was made, copy it to $COMOUTfinal
nc=$(ls ${DATA}/evs.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat | wc -l | awk '{print $1}')
echo " Found ${nc} large stat file for valid date ${VDATE} "
if [ "${nc}" != '0' ]; then
    echo "Large stat file found for ${VDATE}"
    if [ $SENDCOM = YES ]; then
        cp -v ${DATA}/evs.${STEP}.${MODELNAME}.${RUN}.${VERIF_CASE}.v${VDATE}.stat ${COMOUTfinal}/.
    fi
else
    echo ' '
    echo '**************************************** '
    echo '*** WARNING : NO LARGE STAT FILE *** '
    echo "      found for valid date ${VDATE} "
    echo '**************************************** '
    echo ' '
    echo "${MODELNAME}_${RUN} $VDATE : large STAT file missing."
    ./postmsg "$jlogfile" "WARNING : NO LARGE STAT FILE FOR valid date ${VDATE}"
fi

msg="JOB $job HAS COMPLETED NORMALLY."
postmsg "$jlogfile" "$msg"

echo ' '
echo "Ending grid2obs_stats for ${MODELNAME} ${RUN}"
echo "Ending at : `date`"
echo ' '
