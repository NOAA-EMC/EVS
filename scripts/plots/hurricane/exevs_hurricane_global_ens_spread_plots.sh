#!/bin/bash
set -x
export PS4=' + exevs_hurricane_global_ens_spread_plots.sh line $LINENO: '

export stormYear=${YYYY}
export basinlist="al ep wp"
export numlist="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 \
	        21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40"

for bas in $basinlist; do
### bas do loop start
for num in $numlist; do
### num do loop start

export stormBasin=${bas}
export stbasin=`echo ${stormBasin} | tr "[a-z]" "[A-Z]"`
echo "${stbasin} upper case: AL/EP/WP"
export stormNumber=${num}

if [ ${stormBasin} = "al" ]; then
  COMINbdeck=${COMINbdeckNHC}
  export comoutatl=${COMOUT}/Atlantic
  if [ ! -d ${comoutatl} ]; then mkdir -p ${comoutatl}; fi
elif [ ${stormBasin} = "ep" ]; then
  COMINbdeck=${COMINbdeckNHC}
  export comoutepa=${COMOUT}/EastPacific
  if [ ! -d ${comoutepa} ]; then mkdir -p ${comoutepa}; fi
elif [ ${stormBasin} = "wp" ]; then
  COMINbdeck=${COMINbdeckJTWC}
  export comoutwpa=${COMOUT}/WestPacific
  if [ ! -d ${comoutwpa} ]; then mkdir -p ${comoutwpa}; fi
fi

export bdeckfile=${COMINbdeck}/b${stormBasin}${stormNumber}${stormYear}.dat
if [ -f ${bdeckfile} ]; then
numrecs=`cat ${bdeckfile} | wc -l`
if [ ${numrecs} -gt 0 ]; then
### two ifs start

export comoutroot=${COMOUT}/${bas}${num}
if [ ! -d ${comoutroot} ]; then mkdir -p ${comoutroot}; fi

#export COMINstats=/lfs/h2/emc/ptmp/$USER/com/evs/1.0/hurricane_global_ens/tropcyc/stats
export STORMroot=${DATA}/${bas}${num}
if [ ! -d ${STORMroot} ]; then mkdir -p ${STORMroot}; fi
cd ${STORMroot}
cp -r ${COMINstats}/${bas}${num}/tc_stat .

#---get the storm name from TC-vital file "syndat_tcvitals.${YYYY}"
if [ ${stormBasin} = "al" ]; then
  grep "NHC  ${stormNumber}L" ${COMINvit} > syndat_tcvitals.${YYYY}.${stormBasin}${stormNumber}
  echo $(tail -n 1 syndat_tcvitals.${YYYY}.${stormBasin}${stormNumber}) > TCvit_tail.txt
  sed -i 's/NHC/NHCC/' TCvit_tail.txt
elif [ ${stormBasin} = "ep" ]; then
  grep "NHC  ${stormNumber}E" ${COMINvit} > syndat_tcvitals.${YYYY}.${stormBasin}${stormNumber}
  echo $(tail -n 1 syndat_tcvitals.${YYYY}.${stormBasin}${stormNumber}) > TCvit_tail.txt
  sed -i 's/NHC/NHCC/' TCvit_tail.txt
elif [ ${stormBasin} = "wp" ]; then
  grep "JTWC ${stormNumber}W" ${COMINvit} > syndat_tcvitals.${YYYY}.${stormBasin}${stormNumber}
  echo $(tail -n 1 syndat_tcvitals.${YYYY}.${stormBasin}${stormNumber}) > TCvit_tail.txt
fi
cat TCvit_tail.txt|cut -c10-18 > TCname.txt
VARIABLE1=$( head -n 1 TCname.txt )
echo "$VARIABLE1"
VARIABLE2=$(printf '%s' "$VARIABLE1" | sed 's/[0-9]//g')
echo "$VARIABLE2"
stormName=$(sed "s/ //g" <<< $VARIABLE2)
echo "Name_${stormName}_Name"
echo "${stormBasin}, ${stormNumber}, ${stormYear}, ${stormName}"

#---Storm Plots 
#export LOGOroot=${FIXevs}/logos
#export PLOTDATA=${STORMroot}
export PLOTDATA1=${STORMroot}
#export RUN="tropcyc"
export img_quality="low"
export fhr_list="0,12,24,36,48,60,72,84,96,108,120,132,144,156,168"
export model_tmp_atcf_name_list="MD01,MD02,MD03,MD04,MD05,MD06,MD07,MD08"
export model_plot_name_list="GEFSerror,EENSerror,CENSerror,UENSerror,GEFSspread,EENSspread,CENSspread,UENSspread"
export plot_CI_bars="NO"
export under="_"
export tc_name=${stbasin}${under}${stormYear}${under}${stormName}
export basin=${stbasin}
export tc_num=${stormNumber}
export tropcyc_model_type="global"

#--update the file: ${PLOTDATA1}/tc_stat/tc_stat.out
# merge track/intensity error/spread into 6-models: MD01,MD02,MD03,MD04,MD05,MD06
cd ${PLOTDATA1}/tc_stat
cp tc_stat.out tc_stat.out_org
grep "JOB_LIST:" tc_stat.out > tc_stat.JOB_LIST
grep "COL_NAME:" tc_stat.out > tc_stat.COL_NAME

grep "SUMMARY:  ABS(AMAX_WIND-BMAX_WIND)" tc_stat.out > tc_stat.intensity.ERR
grep "SUMMARY:  ABS(MAX_WIND_STDEV)" tc_stat.out > tc_stat.intensity.STDEV
sed -i 's/ABS(MAX_WIND_STDEV)     /ABS(AMAX_WIND-BMAX_WIND)/' tc_stat.intensity.STDEV
sed -i 's/MD01/MD05/' tc_stat.intensity.STDEV
sed -i 's/MD02/MD06/' tc_stat.intensity.STDEV
sed -i 's/MD03/MD07/' tc_stat.intensity.STDEV
sed -i 's/MD04/MD08/' tc_stat.intensity.STDEV

grep "SUMMARY:  ABS(TK_ERR)" tc_stat.out > tc_stat.track.ERR
grep "SUMMARY:  ABS(TRACK_SPREAD)" tc_stat.out > tc_stat.track.spread
sed -i 's/ABS(TRACK_SPREAD)/ABS(TK_ERR)      /' tc_stat.track.spread
sed -i 's/MD01/MD05/' tc_stat.track.spread
sed -i 's/MD02/MD06/' tc_stat.track.spread
sed -i 's/MD03/MD07/' tc_stat.track.spread
sed -i 's/MD04/MD08/' tc_stat.track.spread

cat tc_stat.JOB_LIST tc_stat.COL_NAME tc_stat.intensity.ERR tc_stat.intensity.STDEV tc_stat.track.ERR tc_stat.track.spread > tc_stat.NEW
sed -i 's/-amodel MD01 -amodel MD02 -amodel MD03/-amodel MD01 -amodel MD02 -amodel MD03 -amodel MD04 -amodel MD05 -amodel MD06 -amodel MD07 -amodel MD08/' tc_stat.NEW

sed -i 's/-column AMAX_WIND-BMAX_WIND -column ABS(AMAX_WIND-BMAX_WIND) -column ALTK_ERR -column CRTK_ERR -column ABS(TK_ERR) -column ABS(TRACK_SPREAD) -column ABS(MAX_WIND_STDEV)/-column ABS(AMAX_WIND-BMAX_WIND) -column ABS(TK_ERR)/' tc_stat.NEW
cp tc_stat.NEW tc_stat.out
rm -f tc_stat.JOB_LIST tc_stat.COL_NAME tc_stat.intensity.* tc_stat.track.* tc_stat.NEW
#--ending for the update the file: ${PLOTDATA1}/tc_stat/tc_stat.out

export LOGOroot=${FIXevs}/logos
export PLOTDATA=${STORMroot}
cd $STORMdata

python ${USHevs}/${COMPONENT}/plot_tropcyc_lead_spread.py

#/lfs/h2/emc/ptmp/jiayi.peng/metTC/wp02/plot/WP_2022_MALAKAS/images
nimgs=$(ls ${STORMroot}/plot/${tc_name}/images/* |wc -l)
if [ $nimgs -ne 0 ]; then
  cd ${STORMroot}/plot/${tc_name}/images
  convert ABSAMAX_WIND-BMAX_WIND_fhrmean_${tc_name}_global.png ABSAMAX_WIND-BMAX_WIND_fhrmean_${tc_name}_global.gif
  convert ABSTK_ERR_fhrmean_${tc_name}_global.png ABSTK_ERR_fhrmean_${tc_name}_global.gif
  rm -f *.png
  if [ "$SENDCOM" = 'YES' ]; then
    cp ${STORMroot}/plot/${tc_name}/images/ABSAMAX_WIND-BMAX_WIND_fhrmean_${tc_name}_global.gif ${comoutroot}/evs.hurricane_global_ens.abswind_err_spread.${stormBasin}.${stormYear}.${stormName}${stormNumber}.png
    cp ${STORMroot}/plot/${tc_name}/images/ABSTK_ERR_fhrmean_${tc_name}_global.gif ${comoutroot}/evs.hurricane_global_ens.abstk_err_spread.${stormBasin}.${stormYear}.${stormName}${stormNumber}.png
  fi
fi

### two ifs end
fi
fi
### num do loop end
done

#export COMINstats=/lfs/h2/emc/ptmp/$USER/com/evs/1.0/hurricane_global_ens/tropcyc/stats

if [ ${stormBasin} = "al" ]; then
  export comoutbas=${comoutatl}
  export metTCcomout=${DATA}/Atlantic
  if [ ! -d $metTCcomout ]; then mkdir -p $metTCcomout; fi
  cd $metTCcomout
  cp -r ${COMINstats}/Atlantic/tc_stat .
  cp $metTCcomout/tc_stat/tc_stat_basin.out $metTCcomout/tc_stat/tc_stat.out
elif [ ${stormBasin} = "ep" ]; then
  export comoutbas=${comoutepa}
  export metTCcomout=${DATA}/EastPacific
  if [ ! -d $metTCcomout ]; then mkdir -p $metTCcomout; fi
  cd $metTCcomout
  cp -r ${COMINstats}/EastPacific/tc_stat .
  cp $metTCcomout/tc_stat/tc_stat_basin.out $metTCcomout/tc_stat/tc_stat.out
elif [ ${stormBasin} = "wp" ]; then
  export comoutbas=${comoutwpa}
  export metTCcomout=${DATA}/WestPacific
  if [ ! -d $metTCcomout ]; then mkdir -p $metTCcomout; fi
  cd $metTCcomout
  cp -r ${COMINstats}/WestPacific/tc_stat .
  cp $metTCcomout/tc_stat/tc_stat_basin.out $metTCcomout/tc_stat/tc_stat.out
fi

#--- Basin-Storms Plots 
#export LOGOroot=${FIXevs}/logos
#export PLOTDATA=${metTCcomout}
#export RUN="tropcyc"
export img_quality="low"
export fhr_list="0,12,24,36,48,60,72,84,96,108,120,132,144,156,168"
export model_tmp_atcf_name_list="MD01,MD02,MD03,MD04,MD05,MD06,MD07,MD08"
export model_plot_name_list="GEFSerror,EENSerror,CENSerror,UENSerror,GEFSspread,EENSspread,CENSspread,UENSspread"
export plot_CI_bars="NO"
export stormNameB=Basin
export tc_name=${stbasin}${under}${stormYear}${under}${stormNameB}
export basin=${stbasin}
export tc_num= 
export tropcyc_model_type="global"

# update the file: ${PLOTDATA1}/tc_stat/tc_stat.out
# merge track/intensity error/spread into 6-models: MD01,MD02,MD03,MD04,MD05,MD06
cd ${PLOTDATA1}/tc_stat
cp tc_stat.out tc_stat.out_org
grep "JOB_LIST:" tc_stat.out > tc_stat.JOB_LIST
grep "COL_NAME:" tc_stat.out > tc_stat.COL_NAME

grep "SUMMARY:  ABS(AMAX_WIND-BMAX_WIND)" tc_stat.out > tc_stat.intensity.ERR
grep "SUMMARY:  ABS(MAX_WIND_STDEV)" tc_stat.out > tc_stat.intensity.STDEV
sed -i 's/ABS(MAX_WIND_STDEV)     /ABS(AMAX_WIND-BMAX_WIND)/' tc_stat.intensity.STDEV
sed -i 's/MD01/MD05/' tc_stat.intensity.STDEV
sed -i 's/MD02/MD06/' tc_stat.intensity.STDEV
sed -i 's/MD03/MD07/' tc_stat.intensity.STDEV
sed -i 's/MD04/MD08/' tc_stat.intensity.STDEV

grep "SUMMARY:  ABS(TK_ERR)" tc_stat.out > tc_stat.track.ERR
grep "SUMMARY:  ABS(TRACK_SPREAD)" tc_stat.out > tc_stat.track.spread
sed -i 's/ABS(TRACK_SPREAD)/ABS(TK_ERR)      /' tc_stat.track.spread
sed -i 's/MD01/MD05/' tc_stat.track.spread
sed -i 's/MD02/MD06/' tc_stat.track.spread
sed -i 's/MD03/MD07/' tc_stat.track.spread
sed -i 's/MD04/MD08/' tc_stat.track.spread

cat tc_stat.JOB_LIST tc_stat.COL_NAME tc_stat.intensity.ERR tc_stat.intensity.STDEV tc_stat.track.ERR tc_stat.track.spread > tc_stat.NEW
sed -i 's/-amodel MD01 -amodel MD02 -amodel MD03/-amodel MD01 -amodel MD02 -amodel MD03 -amodel MD04 -amodel MD05 -amodel MD06 -amodel MD07 -amodel MD08/' tc_stat.NEW

sed -i 's/-column AMAX_WIND-BMAX_WIND -column ABS(AMAX_WIND-BMAX_WIND) -column ALTK_ERR -column CRTK_ERR -column ABS(TK_ERR) -column ABS(TRACK_SPREAD) -column ABS(MAX_WIND_STDEV)/-column ABS(AMAX_WIND-BMAX_WIND) -column ABS(TK_ERR)/' tc_stat.NEW
cp tc_stat.NEW tc_stat.out
rm -f tc_stat.JOB_LIST tc_stat.COL_NAME tc_stat.intensity.* tc_stat.track.* tc_stat.NEW
# ending for the update the file: ${PLOTDATA1}/tc_stat/tc_stat.out

export LOGOroot=${FIXevs}/logos
export PLOTDATA=${metTCcomout}
cd $metTCcomout

python ${USHevs}/${COMPONENT}/plot_tropcyc_lead_spread.py

bimgs=$(ls ${metTCcomout}/plot/${tc_name}/images/* |wc -l)
if [ $bimgs -ne 0 ]; then
  cd ${metTCcomout}/plot/${tc_name}/images
  convert ABSAMAX_WIND-BMAX_WIND_fhrmean_${tc_name}_global.png ABSAMAX_WIND-BMAX_WIND_fhrmean_${tc_name}_global.gif
  convert ABSMAX_WIND_STDEV_fhrmean_${tc_name}_global.png ABSMAX_WIND_STDEV_fhrmean_${tc_name}_global.gif
  convert ABSTK_ERR_fhrmean_${tc_name}_global.png ABSTK_ERR_fhrmean_${tc_name}_global.gif
  rm -f *.png
  if [ "$SENDCOM" = 'YES' ]; then
    cp -r ${metTCcomout}/plot/${tc_name}/images/ABSAMAX_WIND-BMAX_WIND_fhrmean_${tc_name}_global.gif ${comoutbas}/evs.hurricane_global_ens.abswind_err_spread.${stormBasin}.${stormYear}.season.png
    cp -r ${metTCcomout}/plot/${tc_name}/images/ABSMAX_WIND_STDEV_fhrmean_${tc_name}_global.gif ${comoutbas}/evs.hurricane_global_ens.abswind_stdev_spread.${stormBasin}.${stormYear}.season.png
    cp -r ${metTCcomout}/plot/${tc_name}/images/ABSTK_ERR_fhrmean_${tc_name}_global.gif ${comoutbas}/evs.hurricane_global_ens.abstk_err_spread.${stormBasin}.${stormYear}.season.png
  fi
fi
### bas do loop end
done
