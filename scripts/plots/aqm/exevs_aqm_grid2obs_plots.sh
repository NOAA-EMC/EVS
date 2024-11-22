#!/bin/bash
###############################################################################
# Name of Script: exevs_aqm_grid2obs_plots.sh
# Developers: Ho-Chun Huang / Ho-Chun.Huang@noaa.gov
#
# Original Name of Script: exevs_global_det_atmos_grid2obs_plots.sh
# Original Author: Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: This script is run for the aqm plots step for
#                    the grid-to-obs verification. It uses EMC-developed
#                    python scripts to do the plotting.
#
#   Change Logs:
#   11/21/2024   Ho-Chun Huang  Use GLOBAL_DET CFP approach for regular plots
###############################################################################

set -x

export VERIF_CASE_STEP_abbrev="g2op"
echo "RUN MODE:${evs_run_mode}"

## export PLOTDIR=${DATA}/plots
## export OUTDIR=${DATA}/out
export PRUNEDIR=${DATA}/prune    ## for headline
mkdir -p ${PRUNEDIR}

export STATDIR=${DATA}/stats
export PLOTDIR_headline=${DATA}/plots_headline
mkdir -p ${STATDIR} ${PLOTDIR_headline}

# Source config
source ${config}
export err=$?; err_chk

model1=`echo ${MODELNAME} | tr a-z A-Z`
export model1

aqm_ver_id=$( echo ${aqm_ver} | awk -F"." '{print $1$2}' )
export modelid=${MODELNAME}${aqm_ver_id}

ObsType=`echo ${DATA_TYPE} | tr A-Z a-z`
export ObsType

# Bring in all stats files, and change into display name
# for different models or types of solution.

for biasc in raw bc; do
    NOW=${VDATE_START}
    while [ ${NOW} -le ${VDATE_END} ]; do
        cpfile=evs.stats.${MODELNAME}_${biasc}.${RUN}.${VERIF_CASE}_${ObsType}.v${NOW}.stat
        sedfile=evs.stats.${modelid}_${biasc}_${ObsType}.${RUN}.${VERIF_CASE}.v${NOW}.stat
        if [ -s ${EVSINaqm}/${MODELNAME}.${NOW}/${cpfile} ]; then
            cpreq ${EVSINaqm}/${MODELNAME}.${NOW}/${cpfile} ${STATDIR}
            sed "s/${model1}/${modelid}_${biasc}/g" ${STATDIR}/${cpfile} > ${STATDIR}/${sedfile}
        else
            echo "WARNING ${MODELNAME} ${STEP} :: Can not find ${EVSINaqm}.${NOW}/${cpfile}"
        fi
	cdate=${NOW}"00"
	DATE=$( ${NDATE} +24 ${cdate} )
    done
done

# Make directory
mkdir -p ${VERIF_CASE}_${STEP}

# Set number of days being plotted
start_date_seconds=$(date +%s -d ${start_date})
end_date_seconds=$(date +%s -d ${end_date})
diff_seconds=$(expr ${end_date_seconds} - ${start_date_seconds})
diff_days=$(expr ${diff_seconds} \/ 86400)
total_days=$(expr ${diff_days} + 1)
NDAYS=${NDAYS:-${total_days}}

# Check user's config settings
python ${USHevs}/${COMPONENT}/${COMPONENT}_check_settings.py
export err=$?; err_chk

# Create output directories
python ${USHevs}/${COMPONENT}/${COMPONENT}_create_output_dirs.py
export err=$?; err_chk

# Link needed data files and set up model information
python ${USHevs}/${COMPONENT}/${COMPONENT}_get_data_files.py
export err=$?; err_chk

# Create and run job scripts for condense_stats, filter_stats, make_plots, and tar_images
## for group in condense_stats filter_stats make_plots tar_images; do
declare -a proc_list=( condense_stats filter_stats make_plots tar_images )
for group in "${proc_list[@]}"; do
    export JOB_GROUP=${group}
    echo "Creating and running jobs for grid-to-obs plots: ${JOB_GROUP}"
    python ${USHevs}/${COMPONENT}/${COMPONENT}_${STEP}_${VERIF_CASE}_create_job_scripts.py
    export err=$?; err_chk
    chmod u+x ${VERIF_CASE}_${STEP}/plot_job_scripts/${group}/*
    nc=1
    if [ "${USE_CFP}" == "YES" ]; then
        group_ncount_poe=$( find  ${DATA}/${VERIF_CASE}_${STEP}/plot_job_scripts/${group} -name poe* | wc -l )
        while [ $nc -le ${group_ncount_poe} ]; do
            poe_script=${DATA}/${VERIF_CASE}_${STEP}/plot_job_scripts/${group}/poe_jobs${nc}
            chmod 775 ${poe_script}
            export MP_PGMMODEL=mpmd
            export MP_CMDFILE=${poe_script}
            if [ "${machine}" == "WCOSS2" ]; then
                nselect=$(cat ${PBS_NODEFILE} | wc -l)
                nnp=$((${nselect} * ${nproc}))
                launcher="mpiexec -np ${nnp} -ppn ${nproc} --cpu-bind verbose,depth cfp"
            elif [ "${machine}" == "HERA" ] || [ "${machine}" = "ORION" ] || [ "${machine}" = "S4" ] || [ "${machine}" == "JET" ]; then
                export SLURM_KILL_BAD_EXIT=0
                launcher="srun --export=ALL --multi-prog"
            fi
            ${launcher} ${MP_CMDFILE}
            export err=$?; err_chk
            nc=$((nc+1))
        done
    else
        group_ncount_poe=$( find  ${DATA}/${VERIF_CASE}_${STEP}/plot_job_scripts/${group} -name job* | wc -l )
        while [ ${nc} -le ${group_ncount_job} ]; do
            ${DATA}/${VERIF_CASE}_${STEP}/plot_job_scripts/${group}/job${nc}
            export err=$?; err_chk
            nc=$((nc+1))
        done
    fi
done

# Copy files to desired location
if [ "${SENDCOM}" == "YES" ]; then
    # Make and copy tar file
    cd ${VERIF_CASE}_${STEP}/plot_output/tar_files
    for VERIF_TYPE in ${g2op_type_list}; do
        large_tar_file=${DATA}/${VERIF_CASE}_${STEP}/plot_output/${RUN}.${end_date}/${NET}.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}_${VERIF_TYPE}.last${NDAYS}days.v${end_date}.tar
        tar -cvf ${large_tar_file} ${VERIF_CASE}_${VERIF_TYPE}*.tar
        if [ -f ${large_tar_file} ]; then
           cp -v ${large_tar_file} ${COMOUT}/.
        fi
    done
    cd ${DATA}
fi

if [ "${SENDDBN}" == "YES" ]; then
    ${DBNROOT}/bin/dbn_alert MODEL EVS_RZDM ${job} ${COMOUT}/${NET}.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}_${VERIF_TYPE}.last${NDAYS}days.v${end_date}.tar
fi
##
## Headline Plots
##
mkdir -p ${COMOUTheadline}/headline
for region in CONUS CONUS_East CONUS_West CONUS_South CONUS_Central; do
    export region
    case ${region} in
        CONUS) smregion=conus;;
        CONUS_East) smregion=conus_e;;
        CONUS_West) smregion=conus_w;;
        CONUS_South) smregion=conus_s;;
        CONUS_Central) smregion=conus_c;;
        Appalachia) smregion=apl;;
        CPlains) smregion=cpl;;
        DeepSouth) smregion=ds;;
        GreatBasin) smregion=grb;;
        GreatLakes) smregion=grlk;;
        Mezquital) smregion=mez;;
        MidAtlantic) smregion=matl;;
        NorthAtlantic) smregion=ne;;
        NPlains) smregion=npl;;
        NRockies) smregion=nrk;;
        PacificNW) smregion=npw;;
        PacificSW) smregion=psw;;
        Prairie) smregion=pra;;
        Southeast) smregion=se;;
        Southwest) smregion=sw;;
        SPlains) smregion=spl;;
        SRockies) smregion=srk;;
        *) echo "Selected region is not defined, reset to CONUS"
           smregion="conus";;
    esac
    for inithr in 12; do
        export inithr

        for var in OZMAX8 PMAVE; do
            export var

            case ${var} in
                OZMAX8)
                        export flead=47
                        export lev=L1
                        export lev_obs=A8
                        export select_headline_csi="70";;
                PMAVE)
                        export flead=40
                        export lev=A23
                        export lev_obs=A1
                        export select_headline_csi="35";;
            esac
            export linetype=CTC
            export select_headline_threshold=">${select_headline_csi}"
            mkdir -p ${COMOUT}/${var}
            smlev=`echo ${lev} | tr A-Z a-z`
            smvar=`echo ${var} | tr A-Z a-z`
            figtype=csi

            figfile=headline_${COMPONENT}.${figtype}_gt${select_headline_csi}.${smvar}.${smlev}.last${NDAYS}days.timeseries_init${inithr}z_f${flead}.buk_${smregion}.png
            cpfile=${COMOUTheadline}/headline/${figfile}
            if [ ! -e ${cpfile} ]; then
                ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/py_plotting_${smvar}_headline.config
                export err=$?; err_chk
            else
                echo "RESTART - plot exists; copying over to plot directory"
                cpreq ${cpfile} ${PLOTDIR_headline}
            fi
  
            cpfile=${PLOTDIR_headline}/${figfile}
            if [ -e ${PLOTDIR_headline}/aq/*/evs*png ]; then
                mv ${PLOTDIR_headline}/aq/*/evs*png ${cpfile}
                cp -v ${cpfile} ${COMOUTheadline}/headline
            elif [ ! -e ${cpfile} ]; then
                echo "WARNING: NO HEADLINE PLOT FOR ${var} ${figtype} ${region}"
                echo "WARNING: This is possible where there is no exceedance of the critical threshold in the last ${NDAYS} days"
            fi
        done
    done
done


# Tar up headline plot tarball and copy to the headline plot directory

cd ${PLOTDIR_headline}
tarfile=evs.plots.${COMPONENT}.${RUN}.headline.last${NDAYS}days.v${VDATE}.tar
tar -cvf ${tarfile} *png

if [ "${SENDCOM}" == "YES" ]; then
    mkdir -m 775 -p ${COMOUTheadline}
    if [ -s ${tarfile} ]; then
        cp -v ${tarfile} ${COMOUTheadline}
    else
        echo "WARNING: Can not find ${PLOTDIR_headline}/${tarfile}"
    fi
fi

if [ "${SENDDBN}" == "YES" ]; then     
    if [ -s ${COMOUTheadline}/${tarfile} ]; then
        $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job ${COMOUTheadline}/${tarfile}
    else
        echo "WARNING: Can not find ${COMOUTheadline}/${tarfile}"
    fi
fi

exit
