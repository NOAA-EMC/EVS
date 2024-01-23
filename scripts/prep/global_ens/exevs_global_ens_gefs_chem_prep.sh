#!/bin/bash
########################################################################
###  UNIX Script Documentation Block
###                      .
### Script name:         exevs_global_ens_chem_grid2obs_prep.sh
### Script description:  To run grid-to-grid verification on all global chem
### Original Author   :  Partha Bhattacharjee
###
###   Change Logs:
###
###   01/16/2024   Ho-Chun Huang  EVSv1.0 EE2 compliance
###
########################################################################
set -x

## For temporary stoage on the working dirary before moving to COMOUT
export finalstat=${DATA}/final
mkdir -p ${finalstat}

export CONFIGevs=${CONFIGevs:-${PARMevs}/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}}
export obstype=`echo ${OBTTYPE} | tr a-z A-Z`
config_file=${CONFIGevs}/ASCII2NC_obs${obstype}.conf

COMOUTchem=${COMOUTprep}/${VDATE}/${OBTTYPE}
mkdir -p ${COMOUTchem}

checkfile=${DCOMIN}/${VDATE}/validation_data/aq/${OBTTYPE}/${VDATE}.lev15
if [ -s ${checkfile} ]; then
    if [ -s ${config_file} ]; then
        run_metplus.py ${config_file}
        export err=$?; err_chk
	if [ ${SENDCOM} = "YES" ]; then
            cpfile=${finalstat}/All_${VDATE}.nc
            if [ -e ${cpfile} ]; then cpreq ${cpfile} ${COMOUTchem};fi
	fi
    else
        echo "WARNING: can not find ${config_file}"
    fi
else
    if [ ${SENDMAIL} = "YES" ]; then
        export subject="AEORNET Level 1.5 NC file Missing for EVS ${COMPONENT}"
        echo "WARNING: No AEORNET Level 1.5 data was available for valid date ${VDATE}" > mailmsg
        echo "Missing file is ${checkfile}" >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $MAILTO 
    fi

    echo "WARNING: No AEORNET Level 1.5 data was available for valid date ${VDATE}"
    echo "WARNING: Missing file is ${checkfile}"
fi

exit


