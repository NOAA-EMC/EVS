#!/bin/bash
export PS4=' + exevs_hurricane_global_det_tcgen_stats.sh line $LINENO: '

export savePlots=${savePlots:-YES}
export YEAR=${YYYY}
export TCGENdays="TC Genesis(05/01/${YEAR}-11/30/${YEAR})"
export basinlist="al ep wp"
export modellist="gfs ecmwf cmc"

noaa_logo() {
  TargetImageName=$1
  WaterMarkLogoFileName=${FIXevs}/noaa.png
  echo "Start NOAA Logo marking... "
  SCALE=50
  composite -gravity northwest -quality 2 \( $WaterMarkLogoFileName -resize $SCALE% \) "$TargetImageName" "$TargetImageName"
  error=$?
  echo "NOAA Logo is generated. "
  return $error
}
nws_logo() {
  TargetImageName=$1
  WaterMarkLogoFileName=${FIXevs}/nws.png
  echo "Start NWS Logo marking... "
  SCALE=50
  composite -gravity northeast -quality 2 \( $WaterMarkLogoFileName -resize $SCALE% \) "$TargetImageName" "$TargetImageName"
  error=$?
  echo "NWS Logo is generated. "
  return $error
}

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
cp ${PARMevs}/TCGen_template.conf .
export VALID_FREQ=6

export SEARCH1="INPUT_BASE_template"
export SEARCH2="OUTPUT_BASE_template"
export SEARCH3="YEAR_template"
export SEARCH4="INIT_FREQ_template"
export SEARCH5="VALID_FREQ_template"
export SEARCH6="BASIN_MASK_template"

sed -i "s|$SEARCH1|$INPUT|g" TCGen_template.conf
sed -i "s|$SEARCH2|$OUTPUT|g" TCGen_template.conf
sed -i "s|$SEARCH3|$YEAR|g" TCGen_template.conf
sed -i "s|$SEARCH4|$INIT_FREQ|g" TCGen_template.conf
sed -i "s|$SEARCH5|$VALID_FREQ|g" TCGen_template.conf
sed -i "s|$SEARCH6|$BASIN_MASK|g" TCGen_template.conf

run_metplus.py -c ${OUTPUT}/TCGen_template.conf

#--- plot the Hits/False Alarms Distribution
#export OUTPUT=${DATAroot}/output/${basin}_${model}
cd ${OUTPUT}
cp ${USHevs}/hits_${basin}.py .
grep "00    FYOY" tc_gen_${YEAR}_genmpr.txt > tc_gen_hits.txt
export hitfile="tc_gen_hits.txt"
python hits_${basin}.py
convert TC_genesis.png tcgen_hits_${basin}_${model}.gif

# Attach NOAA logo
export gif_name=tcgen_hits_${basin}_${model}.gif
TargetImageName=$gif_name
noaa_logo $TargetImageName
error=$?

# Attach NWS logo
export gif_name=tcgen_hits_${basin}_${model}.gif
TargetImageName=$gif_name
nws_logo $TargetImageName
error=$?

rm -f TC_genesis.png

cp ${USHevs}/false_${basin}.py .
grep "00    FYON" tc_gen_${YEAR}_genmpr.txt > tc_gen_false.txt
grep "NA    FYON" tc_gen_${YEAR}_genmpr.txt >> tc_gen_false.txt
export falsefile="tc_gen_false.txt"
python false_${basin}.py
convert TC_genesis.png tcgen_falseAlarm_${basin}_${model}.gif
rm -f TC_genesis.png

# Attach NOAA logo
export gif_name1=tcgen_falseAlarm_${basin}_${model}.gif
TargetImageName=$gif_name1
noaa_logo $TargetImageName
error=$?

# Attach NWS logo
export gif_name1=tcgen_falseAlarm_${basin}_${model}.gif
TargetImageName=$gif_name1
nws_logo $TargetImageName
error=$?

cp ${USHevs}/tcgen_space_${basin}.py .
python tcgen_space_${basin}.py
convert TC_genesis.png tcgen_HitFalse_${basin}_${model}.gif
rm -f TC_genesis.png

# Attach NOAA logo
export gif_name2=tcgen_HitFalse_${basin}_${model}.gif
TargetImageName=$gif_name2
noaa_logo $TargetImageName
error=$?

# Attach NWS logo
export gif_name2=tcgen_HitFalse_${basin}_${model}.gif
TargetImageName=$gif_name2
nws_logo $TargetImageName
error=$?

#export COMOUTroot=${COMOUT}/${basin}_${model}
export COMOUTroot=${COMOUT}
if [ "$SENDCOM" = 'YES' ]; then
  if [ ! -d ${COMOUTroot} ]; then mkdir -p ${COMOUTroot}; fi
  cp ${OUTPUT}/tc_gen_${YEAR}_ctc.txt ${COMOUTroot}/tc_gen_${YEAR}_ctc_${basin}_${model}.txt
  cp ${OUTPUT}/tc_gen_${YEAR}_cts.txt ${COMOUTroot}/tc_gen_${YEAR}_cts_${basin}_${model}.txt
  cp ${OUTPUT}/tc_gen_${YEAR}_genmpr.txt ${COMOUTroot}/tc_gen_${YEAR}_genmpr_${basin}_${model}.txt
  cp ${OUTPUT}/tc_gen_${YEAR}.stat ${COMOUTroot}/tc_gen_${YEAR}_${basin}_${model}.stat
  cp ${OUTPUT}/tc_gen_${YEAR}_pairs.nc ${COMOUTroot}/tc_gen_${YEAR}_pairs_${basin}_${model}.nc
  if [ "$savePlots" = 'YES' ]; then
#    cp ${OUTPUT}/*.gif ${COMOUTroot}/.
    cp ${OUTPUT}/tcgen_hits_${basin}_${model}.gif ${COMOUTroot}/evs.hurricane_global_det.hits.${basin}.${YEAR}.${model}.season.tcgen.png
    cp ${OUTPUT}/tcgen_falseAlarm_${basin}_${model}.gif ${COMOUTroot}/evs.hurricane_global_det.fals.${basin}.${YEAR}.${model}.season.tcgen.png
    cp ${OUTPUT}/tcgen_HitFalse_${basin}_${model}.gif ${COMOUTroot}/evs.hurricane_global_det.hitfals.${basin}.${YEAR}.${model}.season.tcgen.png
  fi   
fi

### model do loop end
done
#--- plot the Performance Diagram
export DATAplot=${DATAroot}/${basin}
if [ ! -d ${DATAplot} ]; then mkdir -p ${DATAplot}; fi
cd ${DATAplot}
cp ${USHevs}/tcgen_performance_diagram.py .
grep "GENESIS_DEV" ${COMOUTroot}/tc_gen_${YEAR}_ctc_${basin}_gfs.txt > dev_tc_gen_${YEAR}_ctc_${basin}_gfs.txt
grep "GENESIS_DEV" ${COMOUTroot}/tc_gen_${YEAR}_ctc_${basin}_ecmwf.txt > dev_tc_gen_${YEAR}_ctc_${basin}_ecmwf.txt
grep "GENESIS_DEV" ${COMOUTroot}/tc_gen_${YEAR}_ctc_${basin}_cmc.txt > dev_tc_gen_${YEAR}_ctc_${basin}_cmc.txt
export CTCfile01="dev_tc_gen_${YEAR}_ctc_${basin}_gfs.txt"
export CTCfile02="dev_tc_gen_${YEAR}_ctc_${basin}_ecmwf.txt"
export CTCfile03="dev_tc_gen_${YEAR}_ctc_${basin}_cmc.txt"
python tcgen_performance_diagram.py
convert tcgen_performance_diagram.png tcgen_performance_diagram_${basin}.gif

# Attach NOAA logo
export gif_name2=tcgen_performance_diagram_${basin}.gif
TargetImageName=$gif_name2
noaa_logo $TargetImageName
error=$?

# Attach NWS logo
export gif_name2=tcgen_performance_diagram_${basin}.gif
TargetImageName=$gif_name2
nws_logo $TargetImageName
error=$?

if [ "$SENDCOM" = 'YES' ]; then
if [ "$savePlots" = 'YES' ]; then
#  cp ${DATAplot}/*.gif ${COMOUTroot}/.
  cp ${DATAplot}/tcgen_performance_diagram_${basin}.gif ${COMOUTroot}/evs.hurricane_global_det.performancediagram.${basin}.${YEAR}.season.tcgen.png
fi
fi
### basin do loop end
done

