#!/bin/bash -e
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
# NCEP EMC Verification System (EVS) - CAM
#
# CONTRIBUTORS: Marcel Caron, marcel.caron@noaa.gov, Affiliate @ NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Submit to MAILTO mailing list any mail messages that were written 
#          during cam_check_input_data.py
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

set -x

MAILMSGDIR=${DATA}

if [ -s ${MAILMSGDIR}/mailmsghead_gen ] && [ -s ${MAILMSGDIR}/mailmsgbody_gen ] && [ -s ${MAILMSGDIR}/mailmsgsubj_gen ]; then
    awk -i inplace '{$1=$1};!seen[$0]++' ${MAILMSGDIR}/mailmsgsubj_gen
    awk -i inplace '{$1=$1};!seen[$0]++' ${MAILMSGDIR}/mailmsghead_gen
    awk -i inplace '{$1=$1};!seen[$0]++' ${MAILMSGDIR}/mailmsgbody_gen
    awk '!/^[[:blank:]]*$/' ${MAILMSGDIR}/mailmsghead_gen
    awk '!/^[[:blank:]]*$/' ${MAILMSGDIR}/mailmsgbody_gen
    cat ${MAILMSGDIR}/mailmsghead_gen >>${MAILMSGDIR}/mailmsg_gen
    echo '' >> ${MAILMSGDIR}/mailmsg_gen
    cat ${MAILMSGDIR}/mailmsgbody_gen >>${MAILMSGDIR}/mailmsg_gen
    subject_i=$(tr '\n' ', ' < ${MAILMSGDIR}/mailmsgsubj_gen)
    subject="${subject_i:0:900} Data Missing for EVS ${COMPONENT}"
    echo '' >> ${MAILMSGDIR}/mailmsg_gen
    echo "Job ID: ${jobid}" >>${MAILMSGDIR}/mailmsg_gen
    cat ${MAILMSGDIR}/mailmsg_gen | mail -s "${subject}" "${MAILTO}"
fi
if [ -s ${MAILMSGDIR}/mailmsghead_fcst ] && [ -s ${MAILMSGDIR}/mailmsgbody_fcst ] && [ -s ${MAILMSGDIR}/mailmsgsubj_fcst ]; then
    awk -i inplace '{$1=$1};!seen[$0]++' ${MAILMSGDIR}/mailmsgsubj_fcst
    awk -i inplace '{$1=$1};!seen[$0]++' ${MAILMSGDIR}/mailmsghead_fcst
    awk -i inplace '{$1=$1};!seen[$0]++' ${MAILMSGDIR}/mailmsgbody_fcst
    awk '!/^[[:blank:]]*$/' ${MAILMSGDIR}/mailmsghead_fcst
    awk '!/^[[:blank:]]*$/' ${MAILMSGDIR}/mailmsgbody_fcst
    tr '\n' ', ' < ${MAILMSGDIR}/mailmsghead_fcst >>${MAILMSGDIR}/mailmsg_fcst
    echo '' >> ${MAILMSGDIR}/mailmsg_fcst
    cat ${MAILMSGDIR}/mailmsgbody_fcst >>${MAILMSGDIR}/mailmsg_fcst
    subject_i=$(tr '\n' ', ' < ${MAILMSGDIR}/mailmsgsubj_fcst)
    subject="${subject_i:0:900} Data Missing for EVS ${COMPONENT}"
    echo '' >> ${MAILMSGDIR}/mailmsg_fcst
    echo "Job ID: ${jobid}" >>${MAILMSGDIR}/mailmsg_fcst
    cat ${MAILMSGDIR}/mailmsg_fcst | mail -s "${subject}" "${MAILTO}"
fi
if [ -s ${MAILMSGDIR}/mailmsghead_anl ] && [ -s ${MAILMSGDIR}/mailmsgbody_anl ] && [ -s ${MAILMSGDIR}/mailmsgsubj_anl ]; then
    awk -i inplace '{$1=$1};!seen[$0]++' ${MAILMSGDIR}/mailmsgsubj_anl
    awk -i inplace '{$1=$1};!seen[$0]++' ${MAILMSGDIR}/mailmsghead_anl
    awk -i inplace '{$1=$1};!seen[$0]++' ${MAILMSGDIR}/mailmsgbody_anl
    awk '!/^[[:blank:]]*$/' ${MAILMSGDIR}/mailmsghead_anl
    awk '!/^[[:blank:]]*$/' ${MAILMSGDIR}/mailmsgbody_anl
    cat ${MAILMSGDIR}/mailmsghead_anl >>${MAILMSGDIR}/mailmsg_anl
    echo '' >> ${MAILMSGDIR}/mailmsg_anl
    cat ${MAILMSGDIR}/mailmsgbody_anl >>${MAILMSGDIR}/mailmsg_anl
    subject_i=$(tr '\n' ', ' < ${MAILMSGDIR}/mailmsgsubj_anl)
    subject="${subject_i:0:900} Data Missing for EVS ${COMPONENT}"
    echo '' >> ${MAILMSGDIR}/mailmsg_anl
    echo "Job ID: ${jobid}" >>${MAILMSGDIR}/mailmsg_anl
    cat ${MAILMSGDIR}/mailmsg_anl | mail -s "${subject}" "${MAILTO}"
fi
if [ -s ${MAILMSGDIR}/mailmsghead_unk ] && [ -s ${MAILMSGDIR}/mailmsgbody_unk ] && [ -s ${MAILMSGDIR}/mailmsgsubj_unk ]; then
    awk -i inplace '{$1=$1};!seen[$0]++' ${MAILMSGDIR}/mailmsgsubj_unk
    awk -i inplace '{$1=$1};!seen[$0]++' ${MAILMSGDIR}/mailmsghead_unk
    awk -i inplace '{$1=$1};!seen[$0]++' ${MAILMSGDIR}/mailmsgbody_unk
    awk '!/^[[:blank:]]*$/' ${MAILMSGDIR}/mailmsghead_unk
    awk '!/^[[:blank:]]*$/' ${MAILMSGDIR}/mailmsgbody_unk
    cat ${MAILMSGDIR}/mailmsghead_unk >>${MAILMSGDIR}/mailmsg_unk
    echo '' >> ${MAILMSGDIR}/mailmsg_unk
    cat ${MAILMSGDIR}/mailmsgbody_unk >>${MAILMSGDIR}/mailmsg_unk
    subject_i=$(tr '\n' ', ' < ${MAILMSGDIR}/mailmsgsubj_unk)
    subject="${subject_i:0:900} Data Missing for EVS ${COMPONENT}"
    echo '' >> ${MAILMSGDIR}/mailmsg_unk
    echo "Job ID: ${jobid}" >>${MAILMSGDIR}/mailmsg_unk
    cat ${MAILMSGDIR}/mailmsg_unk | mail -s "${subject}" "${MAILTO}"
fi
