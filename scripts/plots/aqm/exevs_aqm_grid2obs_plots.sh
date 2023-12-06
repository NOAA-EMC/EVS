#!/bin/ksh
#######################################################################
## UNIX Script Documentation Block
##                      .
## Script name:         exevs_analyses_grid2obs_plots.sh
## Script description:  This script runs plotting codes to generate plots
##                      of aqm vs airnow observations
## Original Author   :  Perry C. Shafran (perry.shafran@noaa.gov)
##
##   Change Logs:
##
##   11/14/2023   Ho-Chun Huang  replace cp with cpreq
##   11/15/2023   Ho-Chun Huang  combine similar code for multiple variable
##
## Plotting Information
##    OZMAX8 forecast lead option for init::06z are day1::F29, day2::F53, and day3::F77
##                                    init::12z are day1::F23, day2::F47, and day3::F71
##    PMAVE  forecast lead option for init::06z are day1::F22, day2::F46, and day3::F70
##                                    init::12z are day1::F16, day2::F40, and day3::F64
##    Selected csi values need to be defined in settings.py
##        ('grid2obs_aq'::'CTC'::'var_dict'::'OZMAX8'::'obs_var_thresholds'
##          and 'fcst_var_thresholds')
#######################################################################

set -x

# Set up initial directories and initialize variables

export LOGDIR=${DATA}/plots/logs
export LOGDIR_headline=${DATA}/plots_headline/logs

export STATDIR=${DATA}/stats
export PLOTDIR=${DATA}/plots
export PLOTDIR_headline=${DATA}/plots_headline
export OUTDIR=${DATA}/out
export PRUNEDIR=${DATA}/prune

mkdir -p  ${LOGDIR}  ${LOGDIR_headline}
mkdir -p ${STATDIR}  ${PLOTDIR} ${PLOTDIR_headline}
mkdir -p ${PRUNEDIR} ${OUTDIR}

model1=`echo ${MODELNAME} | tr a-z A-Z`
export model1

# Bring in 31 days of stats files

STARTDATE=${VDATE}00
ENDDATE=${PDYm31}00

for aqmtyp in ozone pm25 ozmax8 pmave; do
    for biasc in raw bc; do
        DATE=${STARTDATE}
        while [ ${DATE} -ge ${ENDDATE} ]; do
            echo ${DATE} > curdate
            DAY=`cut -c 1-8 curdate`
            cpfile=evs.stats.${COMPONENT}_${biasc}.${RUN}.${VERIF_CASE}_${aqmtyp}.v${DAY}.stat
            sedfile=evs.stats.${aqmtyp}_${biasc}.${RUN}.${VERIF_CASE}.v${DAY}.stat
            if [ -e ${EVSINaqm}.${DAY}/${cpfile} ]; then
                cpreq ${EVSINaqm}.${DAY}/${cpfile} ${STATDIR}
                sed "s/${model1}/${aqmtyp}_${biasc}/g" ${STATDIR}/${cpfile} > ${STATDIR}/${sedfile}
            else
                echo "WARNING ${COMPONENT} ${STEP} :: Can not find ${EVSINaqm}.${DAY}/${cpfile}"
            fi
            DATE=`${NDATE} -24 ${DATE}`
        done
    done
done

# Create plot for each region

for region in CONUS CONUS_East CONUS_West CONUS_South CONUS_Central Appalachia CPlains DeepSouth GreatBasin GreatLakes Mezquital MidAtlantic NorthAtlantic NPlains NRockies PacificNW PacificSW Prairie Southeast Southwest SPlains SRockies; do
    export region
    case ${region} in
        CONUS)         smregion=conus;;
        CONUS_East)    smregion=conus_e;;
        CONUS_West)    smregion=conus_w;;
        CONUS_South)   smregion=conus_s;;
        CONUS_Central) smregion=conus_c;;
        Appalachia)    smregion=apl;;
        CPlains)       smregion=cpl;;
        DeepSouth)     smregion=ds;;
        GreatBasin)    smregion=grb;;
        GreatLakes)    smregion=grlk;;
        Mezquital)     smregion=mez;;
        MidAtlantic)   smregion=matl;;
        NorthAtlantic) smregion=ne;;
        NPlains)       smregion=npl;;
        NRockies)      smregion=nrk;;
        PacificNW)     smregion=npw;;
        PacificSW)     smregion=psw;;
        Prairie)       smregion=pra;;
        Southeast)     smregion=se;;
        Southwest)     smregion=sw;;
        SPlains)       smregion=spl;;
        SRockies)      smregion=srk;;
        *) echo "Selected region is not defined, reset to CONUS"
           smregion="conus";;
    esac
    #
    # Hourly Plots for ozone and pm25 and 
    #   figure type of bcrmse_me fbar_obar
    #
    for inithr in 06 12; do
        export inithr

        for smvar in ozone pm25; do
            case ${smvar} in
                ozone)
                      config_name=awpozcon
                      export var=OZCON1
                      export lev=A1
                      export lev_obs=A1;;
                pm25)
                      config_name=pm25
                      export var=PMTF
                      export lev=L1
                      export lev_obs=A1;;
            esac
            export linetype=SL1L2
            mkdir -p ${COMOUTplots}/${var}
            smlev=`echo ${lev} | tr A-Z a-z`

            for figtype in bcrmse_me fbar_obar; do
                case ${figtype} in
                    bcrmse_me)
                          config_file=py_plotting_${config_name}.config;;
                    fbar_obar)
                          config_file=py_plotting_${config_name}_fbar.config;;
                esac
                figfile=evs.${COMPONENT}.${figtype}.${smvar}_${smlev}.last31days.fhrmean_init${inithr}z.buk_${smregion}.png
                cpfile=${COMOUTplots}/${var}/${figfile}
                if [ ! -e $${cpfile} ]; then
                    ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/${config_file}
                    export err=$?; err_chk
                else
                    echo "RESTART - ${var} ${figtype} ${region} plot exists; copying over to plot directory"
                    cpreq ${cpfile} ${PLOTDIR}
                fi
  
                cpfile=${PLOTDIR}/${figfile}
                if [ -e ${PLOTDIR}/aq/*/evs*png ]; then
                    mv ${PLOTDIR}/aq/*/evs*png ${cpfile}
                    cpreq ${cpfile} ${COMOUTplots}/${var}
                elif [ ! -e ${cpfile} ]; then
                    echo "WARNING: NO PLOT FOR ${var} ${figtype} ${region}"
                fi

            done
        done
    done
    #
    # Daily Plots for maximum 8-hr average ozone 
    #   and 24-hr average PM2.5
    #   for figure type of perfdiag
    #
    for inithr in 06 12; do
        export inithr

        for var in OZMAX8 PMAVE; do
            export var

            case ${var} in
                OZMAX8)
                    if [ "${inithr}" == "06" ]; then
                        fcst_lead=( 29 53 77 )
                    elif [ "${inithr}" == "12" ]; then
                        fcst_lead=( 23 47 71 )
                    fi
                    export lev=L1
                    export lev_obs=A8;;
                PMAVE)
                    if [ "${inithr}" == "06" ]; then
                        fcst_lead=( 22 46 70 )
                    elif [ "${inithr}" == "12" ]; then
                        fcst_lead=( 16 40 64 )
                    fi
                    export lev=A23
                    export lev_obs=A1;;
            esac
            export linetype=CTC
            mkdir -p ${COMOUTplots}/${var}
            smlev=`echo ${lev} | tr A-Z a-z`
            smvar=`echo ${var} | tr A-Z a-z`
            smlinetype=`echo ${linetype} | tr A-Z a-z`
            figtype=perfdiag

            for flead in "${fcst_lead[@]}"; do
                export flead
                figfile=evs.${COMPONENT}.${smlinetype}.${smvar}.${smlev}.last31days.${figtype}_init${inithr}z_f${flead}.buk_${smregion}.png
                cpfile=${COMOUTplots}/${var}/${figfile}
                if [ ! -e ${cpfile} ]; then
                    ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${VERIF_CASE}/py_plotting_${smvar}.config
                    export err=$?; err_chk
                else
                    echo "RESTART - plot exists; copying over to plot directory"
                    cpreq ${cpfile} ${PLOTDIR}
                fi

                cpfile=${PLOTDIR}/${figfile}
                if [ -e ${PLOTDIR}/aq/*/evs*png ]; then
                    mv ${PLOTDIR}/aq/*/evs*png ${cpfile}
                    cpreq ${cpfile} ${COMOUTplots}/${var}
                elif [ ! -e ${cpfile} ]; then
                    echo "WARNING: NO PLOT FOR ${var} ${figtype} ${region}"
                    echo "WARNING: This is possible where there is no exceedance of any threshold in the past 31 days"
                fi

            done
        done
    done
done

log_dir="$LOGDIR"
if [ -d $log_dir ]; then
   log_file_count=$(find $log_dir -type f | wc -l)
   if [[ $log_file_count -ne 0 ]]; then
       log_files=("$log_dir"/*)
       for log_file in "${log_files[@]}"; do
          if [ -f "$log_file" ]; then
           echo "Start: $log_file"
           cat "$log_file"
           echo "End: $log_file"
         fi
       done
   fi   
fi 

# Tar up plot directory and copy to the plot output directory

cd ${PLOTDIR}
tarfile=evs.plots.${COMPONENT}.${RUN}.${VERIF_CASE}.last31days.v${VDATE}.tar
tar -cvf ${tarfile} *png

if [ "${SENDCOM}" == "YES" ]; then
    if [ -e ${tarfile} ]; then
        mkdir -m 775 -p ${COMOUTplots}
        cpreq -v ${tarfile} ${COMOUTplots}
    else
        echo "WARNING: Can not find ${PLOTDIR}/${tarfile}"
    fi
fi

if [ "${SENDDBN}" == "YES" ] ; then     
    if [ -e ${COMOUTplots}/${tarfile} ]; then
        $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job ${COMOUTplots}/${tarfile}
    else
        echo "WARNING: Can not find ${COMOUTplots}/${tarfile}"
    fi
fi

##
## Headline Plots
##
mkdir -p ${COMOUTplots}/headline
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
            mkdir -p ${COMOUTplots}/${var}
            smlev=`echo ${lev} | tr A-Z a-z`
            smvar=`echo ${var} | tr A-Z a-z`
            figtype=csi

            figfile=headline_${COMPONENT}.${figtype}_gt${select_headline_csi}.${smvar}.${smlev}.last31days.timeseries_init${inithr}z_f${flead}.buk_${smregion}.png
            cpfile=${COMOUTplots}/headline/${figfile}
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
                cpreq ${cpfile} ${COMOUTplots}/headline
            elif [ ! -e ${cpfile} ]; then
                echo "WARNING: NO HEADLINE PLOT FOR ${var} ${figtype} ${region}"
                echo "WARNING: This is possible where there is no exceedance of the critical threshold in the past 31 days"
            fi
        done
    done
done

log_dir="${LOGDIR_headline}"
if [ -d $log_dir ]; then
   log_file_count=$(find $log_dir -type f | wc -l)
   if [[ $log_file_count -ne 0 ]]; then
        log_files=("$log_dir"/*)
        for log_file in "${log_files[@]}"; do
          if [ -f "$log_file" ]; then
            echo "Start: $log_file"
            cat "$log_file"
            echo "End: $log_file"
          fi
        done
   fi
fi



# Tar up headline plot tarball and copy to the headline plot directory

cd ${PLOTDIR_headline}
tarfile=evs.plots.${COMPONENT}.${RUN}.headline.last31days.v${VDATE}.tar
tar -cvf ${tarfile} *png

if [ "${SENDCOM}" == "YES" ]; then
    mkdir -m 775 -p ${COMOUTheadline}
    if [ -e ${tarfile} ]; then
        cpreq -v ${tarfile} ${COMOUTheadline}
    else
        echo "WARNING: Can not find ${PLOTDIR_headline}/${tarfile}"
    fi
fi

if [ "${SENDDBN}" == "YES" ]; then     
    if [ -e ${COMOUTheadline}/${tarfile} ]; then
        $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job ${COMOUTheadline}/${tarfile}
    else
        echo "WARNING: Can not find ${COMOUTheadline}/${tarfile}"
    fi
fi

exit


