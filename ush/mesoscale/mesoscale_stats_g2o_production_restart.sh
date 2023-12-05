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
   
   DAT1=${DATA%/*};	#echo "DAT1 = ${DAT1}"
   
   DAT2a=${VERIF_CASE}/METplus_output/${VERIF_TYPE}/point_stat/${MODELNAME}.${VDATE}
   
   TDAT=${DATA}/${DAT2a}
   mkdir -p ${TDAT}

   if [ -d ${COMOUT_RUN_VDATE_VERIF_CASE} ]; then
      cnf=$(ls ${COMOUT_RUN_VDATE_VERIF_CASE}/point_stat* 2>/dev/null | wc -l)
      if [ $cnf -gt 0 ]; then
         cpreq -pv ${COMOUT_RUN_VDATE_VERIF_CASE}/point_stat* ${TDAT}/
      fi
   fi
   
   DAT2=$(find ${DAT1}/ -type d | grep ${DAT2a} | sort | uniq)
   echo ""
   for DAT3 in $DAT2; do
      if [ "$DAT3" != "$TDAT" ]; then 
         echo "Looking : $DAT3"
	 cd $TDAT; # lst=$(ls point_stat* 2>/dev/null | sort);
	 ls point_stat* 2>/dev/null | sort > ${DATA}/lst.tt
	 cd $DAT3; # lss=$(ls point_stat* 2>/dev/null | sort);
	 ls point_stat* 2>/dev/null | sort > ${DATA}/lss.tt

	 lsc=$(comm -23 ${DATA}/lss.tt ${DATA}/lst.tt)
	 rm -f ${DATA}/lss.tt ${DATA}/lst.tt
	 
	 cnc=${#lsc}; # echo $cnc;
         if [ $cnc -gt 0 ]; then
            for f in $lsc; do
               echo "cpreq -pv ${DAT3}/${f} ${TDAT}/"
	       cpreq -pv ${DAT3}/${f} ${TDAT}/
             done
	 fi
      fi
   done
fi
