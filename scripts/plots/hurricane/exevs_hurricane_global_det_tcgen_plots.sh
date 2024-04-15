#!/bin/bash
set -x

export PS4=' + exevs_hurricane_global_det_tcgen_plots.sh line $LINENO: '

export cartopyDataDir=${cartopyDataDir:-/apps/ops/prod/data/cartopy}

export YEAR=${YYYY}
export TCGENdays="TC Genesis(05/01/${YEAR}-11/30/${YEAR})"
export basinlist="al ep wp"
export modellist="gfs ecmwf cmc"

noaa_logo() {
  TargetImageName=$1
  WaterMarkLogoFileName=${FIXevs}/logos/noaa.png
  echo "Start NOAA Logo marking... "
  SCALE=50
  composite -gravity northwest -quality 2 \( $WaterMarkLogoFileName -resize $SCALE% \) "$TargetImageName" "$TargetImageName"
  error=$?
  echo "NOAA Logo is generated. "
  return $error
}
nws_logo() {
  TargetImageName=$1
  WaterMarkLogoFileName=${FIXevs}/logos/nws.png
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

export OUTPUT=${DATA}/${basin}_${model}
if [ ! -d ${OUTPUT} ]; then mkdir -p ${OUTPUT}; fi

#--- plot the Hits/False Alarms Distribution
#  /lfs/h2/emc/ptmp/jiayi.peng/com/evs/1.0/hurricane_global_det/tcgen/stats
cd ${OUTPUT}
cp ${USHevs}/hurricane/plots/hits_${basin}.py .
cp ${COMINstats}/tc_gen_${YEAR}_genmpr_${basin}_${model}.txt tc_gen_${YEAR}_genmpr.txt 
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

cp ${USHevs}/${COMPONENT}/false_${basin}.py .
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

cp ${USHevs}/${COMPONENT}/tcgen_space_${basin}.py .
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

if [ ! -d ${COMOUT} ]; then mkdir -p ${COMOUT}; fi
if [ "$SENDCOM" = 'YES' ]; then
  cp ${OUTPUT}/tcgen_hits_${basin}_${model}.gif ${COMOUT}/evs.hurricane_global_det.hits.${basin}.${YEAR}.${model}.season.tcgen.png
  cp ${OUTPUT}/tcgen_falseAlarm_${basin}_${model}.gif ${COMOUT}/evs.hurricane_global_det.fals.${basin}.${YEAR}.${model}.season.tcgen.png
  cp ${OUTPUT}/tcgen_HitFalse_${basin}_${model}.gif ${COMOUT}/evs.hurricane_global_det.hitfals.${basin}.${YEAR}.${model}.season.tcgen.png
fi

### model do loop end
done

#--- plot the Performance Diagram
export DATAplot=${DATA}/${basin}
if [ ! -d ${DATAplot} ]; then mkdir -p ${DATAplot}; fi
cd ${DATAplot}
cp ${USHevs}/${COMPONENT}/tcgen_performance_diagram.py .
grep "GENESIS_DEV" ${COMINstats}/tc_gen_${YEAR}_ctc_${basin}_gfs.txt > dev_tc_gen_${YEAR}_ctc_${basin}_gfs.txt
grep "GENESIS_DEV" ${COMINstats}/tc_gen_${YEAR}_ctc_${basin}_ecmwf.txt > dev_tc_gen_${YEAR}_ctc_${basin}_ecmwf.txt
grep "GENESIS_DEV" ${COMINstats}/tc_gen_${YEAR}_ctc_${basin}_cmc.txt > dev_tc_gen_${YEAR}_ctc_${basin}_cmc.txt
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
  cp ${DATAplot}/tcgen_performance_diagram_${basin}.gif ${COMOUT}/evs.hurricane_global_det.performancediagram.${basin}.${YEAR}.season.tcgen.png
fi
### basin do loop end
done

