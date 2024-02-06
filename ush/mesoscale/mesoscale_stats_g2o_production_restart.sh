#!/bin/bash
# =============================================================================
# NAME: mesoscale_stats_g2o_production_restart.sh
# CONTRIBUTOR(S): RS, roshan.shrestha@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Make files ready for restart 
# =============================================================================

set -x 

cwd=`pwd`
echo "Working in: ${cwd}"

if [ "${STEP}" = "stats" ]; then
   
   DATA_METplus_output="${DATA}/${VERIF_CASE}/METplus_output"
   
   COMOUT_RUN_VDATE_VERIF_CASE=${COMOUT}/${RUN}.${VDATE}/${MODELNAME}/${VERIF_CASE}
   
   DAT2a=${VERIF_CASE}/METplus_output/${VERIF_TYPE}/point_stat/${MODELNAME}.${VDATE}
   
   TDAT=${DATA}/${DAT2a}
   mkdir -p ${TDAT}

   if [ -d ${COMOUT_RUN_VDATE_VERIF_CASE} ]; then
      cnf=$(ls ${COMOUT_RUN_VDATE_VERIF_CASE}/point_stat* 2>/dev/null | wc -l)
      if [ $cnf -gt 0 ]; then
         for file in ${COMOUT_RUN_VDATE_VERIF_CASE}/point_stat*; do
	     if [ -s $file ]; then
                cp -v $file ${TDAT}/
	     fi
         done
      fi
   fi
   
fi
