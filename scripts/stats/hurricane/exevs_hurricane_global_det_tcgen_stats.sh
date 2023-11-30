#!/bin/bash
set -x
export PS4=' + exevs_hurricane_global_det_tcgen_stats.sh line $LINENO: '

export MetOnMachine=${MetOnMachine:-$MET_ROOT}
export YEAR=${YYYY}
export basinlist="al ep wp"
export modellist="gfs ecmwf cmc"

for basin in $basinlist; do
### basin do loop start
for model in $modellist; do
### model do loop start

export DATAroot=${DATA}/tcgen
if [ ! -d ${DATAroot} ]; then mkdir -p ${DATAroot}; fi
export INPUT=${DATAroot}/input/${basin}_${model}
if [ ! -d ${INPUT} ]; then mkdir -p ${INPUT}; fi
export OUTPUT=${DATAroot}/output/${basin}_${model}
if [ ! -d ${OUTPUT} ]; then mkdir -p ${OUTPUT}; fi

if [ ${model} = "gfs" ]; then
  cp ${COMINgenesis}/${model}_genesis_${YEAR} ${INPUT}/ALLgenesis_${YEAR}
  export INIT_FREQ=6
elif [ ${model} = "ecmwf" ]; then
  cp ${COMINgenesis}/${model}_genesis_${YEAR} ${INPUT}/ALLgenesis_${YEAR}
  export INIT_FREQ=12
elif [ ${model} = "cmc" ]; then
  cp ${COMINgenesis}/${model}_genesis_${YEAR} ${INPUT}/ALLgenesis_${YEAR}
  export INIT_FREQ=12
fi

if [ ${basin} = "al" ]; then
  cp ${COMINadeckNHC}/aal*.dat ${INPUT}/.
  cp ${COMINbdeckNHC}/bal*.dat ${INPUT}/.  
  export BASIN_MASK="AL"
  grep "AL,  9" ${INPUT}/ALLgenesis_${YEAR} > ${INPUT}/genesis_${YEAR}
  grep "HC,"  ${INPUT}/ALLgenesis_${YEAR} >> ${INPUT}/genesis_${YEAR}
elif [ ${basin} = "ep" ]; then
  cp ${COMINadeckNHC}/aep*.dat ${INPUT}/.
  cp ${COMINbdeckNHC}/bep*.dat ${INPUT}/.
  export BASIN_MASK="EP"
  grep "EP,  9" ${INPUT}/ALLgenesis_${YEAR} > ${INPUT}/genesis_${YEAR}
  grep "HC,"  ${INPUT}/ALLgenesis_${YEAR} >> ${INPUT}/genesis_${YEAR}
elif [ ${basin} = "wp" ]; then
  cp ${COMINadeckJTWC}/awp*.dat ${INPUT}/.
  cp ${COMINbdeckJTWC}/bwp*.dat ${INPUT}/.
  export BASIN_MASK="WP"
  grep "WP,  9" ${INPUT}/ALLgenesis_${YEAR} > ${INPUT}/genesis_${YEAR}
  grep "HC,"  ${INPUT}/ALLgenesis_${YEAR} >> ${INPUT}/genesis_${YEAR}
fi

#--- run for TC_gen
cd ${OUTPUT}
cp ${PARMevs}/metplus_config/hurricane/stats/TCGen_template.conf .
export VALID_FREQ=6

export SEARCH0="METBASE_template"
export SEARCH1="INPUT_BASE_template"
export SEARCH2="OUTPUT_BASE_template"
export SEARCH3="YEAR_template"
export SEARCH4="INIT_FREQ_template"
export SEARCH5="VALID_FREQ_template"
export SEARCH6="BASIN_MASK_template"

sed -i "s|$SEARCH0|$MetOnMachine|g" TCGen_template.conf
sed -i "s|$SEARCH1|$INPUT|g" TCGen_template.conf
sed -i "s|$SEARCH2|$OUTPUT|g" TCGen_template.conf
sed -i "s|$SEARCH3|$YEAR|g" TCGen_template.conf
sed -i "s|$SEARCH4|$INIT_FREQ|g" TCGen_template.conf
sed -i "s|$SEARCH5|$VALID_FREQ|g" TCGen_template.conf
sed -i "s|$SEARCH6|$BASIN_MASK|g" TCGen_template.conf

run_metplus.py -c ${OUTPUT}/TCGen_template.conf

if [ "$SENDCOM" = 'YES' ]; then
  if [ ! -d ${COMOUT} ]; then mkdir -p ${COMOUT}; fi
  cp ${OUTPUT}/tc_gen_${YEAR}_ctc.txt ${COMOUT}/tc_gen_${YEAR}_ctc_${basin}_${model}.txt
  cp ${OUTPUT}/tc_gen_${YEAR}_cts.txt ${COMOUT}/tc_gen_${YEAR}_cts_${basin}_${model}.txt
  cp ${OUTPUT}/tc_gen_${YEAR}_genmpr.txt ${COMOUT}/tc_gen_${YEAR}_genmpr_${basin}_${model}.txt
  cp ${OUTPUT}/tc_gen_${YEAR}.stat ${COMOUT}/tc_gen_${YEAR}_${basin}_${model}.stat
  cp ${OUTPUT}/tc_gen_${YEAR}_pairs.nc ${COMOUT}/tc_gen_${YEAR}_pairs_${basin}_${model}.nc
fi

### model do loop end
### basin do loop end
done
done
