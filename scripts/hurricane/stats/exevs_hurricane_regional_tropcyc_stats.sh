#!/bin/bash
export PS4=' + exevs_hurricane_regional_tropcyc_stats.sh line $LINENO: '
#---There is no track forecast for West Pacific from HMON model

export savePlots=${savePlots:-YES}
export stormYear=${YYYY}
export basinlist="al ep"
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
  export COMOUTatl=${COMOUT}/Atlantic
  if [ ! -d ${COMOUTatl} ]; then mkdir -p ${COMOUTatl}; fi
elif [ ${stormBasin} = "ep" ]; then
  COMINbdeck=${COMINbdeckNHC}
  export COMOUTepa=${COMOUT}/EastPacific
  if [ ! -d ${COMOUTepa} ]; then mkdir -p ${COMOUTepa}; fi
elif [ ${stormBasin} = "wp" ]; then
  COMINbdeck=${COMINbdeckJTWC}
  export COMOUTwpa=${COMOUT}/WestPacific
  if [ ! -d ${COMOUTwpa} ]; then mkdir -p ${COMOUTwpa}; fi
fi

export bdeckfile=${COMINbdeck}/b${stormBasin}${stormNumber}${stormYear}.dat
if [ -f ${bdeckfile} ]; then
numrecs=`cat ${bdeckfile} | wc -l`
if [ ${numrecs} -gt 0 ]; then
### two ifs start

export STORMroot=${DATA}/metTC/${bas}${num}
if [ ! -d ${STORMroot} ]; then mkdir -p ${STORMroot}; fi
export STORMdata=${STORMroot}/data
if [ ! -d ${STORMdata} ]; then mkdir -p ${STORMdata}; fi
export COMOUTroot=${COMOUT}/${bas}${num}
if [ ! -d ${COMOUTroot} ]; then mkdir -p ${COMOUTroot}; fi
cd ${STORMdata}

#---get the storm name from TC-vital file "syndat_tcvitals.${YYYY}"
#---copy bdeck files to ${STORMdata}
if [ ${stormBasin} = "al" ]; then
  cp ${COMINbdeckNHC}/b${stormBasin}${stormNumber}${stormYear}.dat ${STORMdata}/.
  grep "NHC  ${stormNumber}L" ${COMINvit} > syndat_tcvitals.${YYYY}.${stormBasin}${stormNumber}
  echo $(tail -n 1 syndat_tcvitals.${YYYY}.${stormBasin}${stormNumber}) > TCvit_tail.txt
  sed -i 's/NHC/NHCC/' TCvit_tail.txt
elif [ ${stormBasin} = "ep" ]; then
  cp ${COMINbdeckNHC}/b${stormBasin}${stormNumber}${stormYear}.dat ${STORMdata}/.
  grep "NHC  ${stormNumber}E" ${COMINvit} > syndat_tcvitals.${YYYY}.${stormBasin}${stormNumber}
  echo $(tail -n 1 syndat_tcvitals.${YYYY}.${stormBasin}${stormNumber}) > TCvit_tail.txt
  sed -i 's/NHC/NHCC/' TCvit_tail.txt
elif [ ${stormBasin} = "wp" ]; then
  cp ${COMINbdeckJTWC}/b${stormBasin}${stormNumber}${stormYear}.dat ${STORMdata}/.
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

#---get the model forecast tracks "AVNO/EMX/CMC" from archive file "tracks.atcfunix.${YY22}"
grep "${stbasin}, ${stormNumber}" ${COMINtrack} > tracks.atcfunix.${YY22}_${stormBasin}${stormNumber}
grep "03, AVNO" tracks.atcfunix.${YY22}_${stormBasin}${stormNumber} > a${stormBasin}${stormNumber}${stormYear}.dat
grep "03, HWRF" tracks.atcfunix.${YY22}_${stormBasin}${stormNumber} >> a${stormBasin}${stormNumber}${stormYear}.dat
grep "03, HMON" tracks.atcfunix.${YY22}_${stormBasin}${stormNumber} >> a${stormBasin}${stormNumber}${stormYear}.dat
grep "03, CTCX" tracks.atcfunix.${YY22}_${stormBasin}${stormNumber} >> a${stormBasin}${stormNumber}${stormYear}.dat
sed -i 's/03, AVNO/03, MD01/' a${stormBasin}${stormNumber}${stormYear}.dat
sed -i 's/03, HWRF/03, MD02/' a${stormBasin}${stormNumber}${stormYear}.dat
sed -i 's/03, HMON/03, MD03/' a${stormBasin}${stormNumber}${stormYear}.dat
sed -i 's/03, CTCX/03, MD04/' a${stormBasin}${stormNumber}${stormYear}.dat

#---get the $startdate, $enddate[YYMMDDHH] from the best track file  
echo $(head -n 1 ${bdeckfile}) > head.txt
echo $(tail -n 1 ${bdeckfile}) > tail.txt
cat head.txt|cut -c9-18 > startymdh.txt
cat tail.txt|cut -c9-18 > endymdh.txt
firstcyc=$( head -n 1 startymdh.txt )
lastcyc=$( head -n 1 endymdh.txt )

export YY01=`echo $firstcyc | cut -c1-4`
export MM01=`echo $firstcyc | cut -c5-6`
export DD01=`echo $firstcyc | cut -c7-8`
export HH01=`echo $firstcyc | cut -c9-10`

export YY02=`echo $lastcyc | cut -c1-4`
export MM02=`echo $lastcyc | cut -c5-6`
export DD02=`echo $lastcyc | cut -c7-8`
export HH02=`echo $lastcyc | cut -c9-10`

export startdate="$YY01$MM01$DD01$HH01"
export enddate="$YY02$MM02$DD02$HH02"
echo "$startdate, $enddate"

#--- run for TC_pairs
#cp ${PARMevs}/TCPairs_template.conf .
cp ${PARMevs}/TCPairs_template_regional.conf TCPairs_template.conf
export SEARCH1="INPUT_BASE_template"
export SEARCH2="OUTPUT_BASE_template"
export SEARCH3="INIT_BEG_template"
export SEARCH4="INIT_END_template"
export SEARCH5="TC_PAIRS_CYCLONE_template"
export SEARCH6="TC_PAIRS_BASIN_template"

sed -i "s|$SEARCH1|$STORMdata|g" TCPairs_template.conf
sed -i "s|$SEARCH2|$STORMroot|g" TCPairs_template.conf
sed -i "s|$SEARCH3|$startdate|g" TCPairs_template.conf
sed -i "s|$SEARCH4|$enddate|g" TCPairs_template.conf
sed -i "s|$SEARCH5|$stormNumber|g" TCPairs_template.conf
sed -i "s|$SEARCH6|$stbasin|g" TCPairs_template.conf

run_metplus.py -c $STORMdata/TCPairs_template.conf

#--- run for TC_stat 
cd $STORMdata
#cp ${PARMevs}/TCStat_template.conf .
cp ${PARMevs}/TCStat_template_regional.conf TCStat_template.conf
sed -i "s|$SEARCH1|$STORMdata|g" TCStat_template.conf
sed -i "s|$SEARCH2|$STORMroot|g" TCStat_template.conf
sed -i "s|$SEARCH3|$startdate|g" TCStat_template.conf
sed -i "s|$SEARCH4|$startdate|g" TCStat_template.conf

export SEARCH7="TC_STAT_INIT_BEG_temp"
export SEARCH8="TC_STAT_INIT_END_temp"
export under="_"
export symdh=${YY01}${MM01}${DD01}${under}${HH01}
export eymdh=${YY02}${MM02}${DD02}${under}${HH02}
echo "$symdh, $eymdh"

sed -i "s|$SEARCH7|$symdh|g" TCStat_template.conf
sed -i "s|$SEARCH8|$eymdh|g" TCStat_template.conf

run_metplus.py -c $STORMdata/TCStat_template.conf

#---Storm Plots 
export LOGOroot=${FIXevs}
export PLOTDATA=${STORMroot}
#export RUN="tropcyc"
export img_quality="low"

export fhr_list="0,12,24,36,48,60,72,84,96,108,120"
export model_tmp_atcf_name_list="MD01,MD02,MD03,MD04"
export model_plot_name_list="GFS,HWRF,HMON,CTCX"
export plot_CI_bars="NO"
export tc_name=${stbasin}${under}${stormYear}${under}${stormName}
export basin=${stbasin}
export tc_num=${stormNumber}
export tropcyc_model_type="regional"
python ${USHevs}/plot_tropcyc_lead_regional.py

#/lfs/h2/emc/ptmp/jiayi.peng/metTC/wp02/plot/WP_2022_MALAKAS/images
nimgs=$(ls ${STORMroot}/plot/${tc_name}/images/* |wc -l)
if [ $nimgs -ne 0 ]; then
  cd ${STORMroot}/plot/${tc_name}/images
  convert ABSAMAX_WIND-BMAX_WIND_fhrmean_${tc_name}_regional.png ABSAMAX_WIND-BMAX_WIND_fhrmean_${tc_name}_regional.gif
  convert AMAX_WIND-BMAX_WIND_fhrmean_${tc_name}_regional.png AMAX_WIND-BMAX_WIND_fhrmean_${tc_name}_regional.gif

  convert ABSTK_ERR_fhrmean_${tc_name}_regional.png ABSTK_ERR_fhrmean_${tc_name}_regional.gif
  convert ALTK_ERR_fhrmean_${tc_name}_regional.png ALTK_ERR_fhrmean_${tc_name}_regional.gif
  convert CRTK_ERR_fhrmean_${tc_name}_regional.png CRTK_ERR_fhrmean_${tc_name}_regional.gif
  rm -f *.png
  if [ "$SENDCOM" = 'YES' ]; then
    if [ ! -d ${COMOUTroot}/tc_pairs ]; then mkdir -p ${COMOUTroot}/tc_pairs; fi
    if [ ! -d ${COMOUTroot}/tc_stat ]; then mkdir -p ${COMOUTroot}/tc_stat; fi
    cp -r ${STORMroot}/tc_pairs/* ${COMOUTroot}/tc_pairs/.
    cp -r ${STORMroot}/tc_stat/* ${COMOUTroot}/tc_stat/.
    if [ ${stormBasin} = "al" ]; then
      cp ${COMOUTroot}/tc_stat/tc_stat_summary.tcst ${COMOUTatl}/${stormBasin}${stormNumber}${stormYear}_stat_summary.tcst 
    elif [ ${stormBasin} = "ep" ]; then
      cp ${COMOUTroot}/tc_stat/tc_stat_summary.tcst ${COMOUTepa}/${stormBasin}${stormNumber}${stormYear}_stat_summary.tcst
    elif [ ${stormBasin} = "wp" ]; then
      cp ${COMOUTroot}/tc_stat/tc_stat_summary.tcst ${COMOUTwpa}/${stormBasin}${stormNumber}${stormYear}_stat_summary.tcst
    fi
    if [ "$savePlots" = 'YES' ]; then
      if [ ! -d ${COMOUTroot}/plot ]; then mkdir -p ${COMOUTroot}/plot; fi
#      cp -r ${STORMroot}/plot/${tc_name}/images/* ${COMOUTroot}/plot/.
      cp ${STORMroot}/plot/${tc_name}/images/ABSAMAX_WIND-BMAX_WIND_fhrmean_${tc_name}_regional.gif ${COMOUTroot}/plot/evs.hurricane_regional.abswind_err.${stormBasin}.${stormYear}.${stormName}${stormNumber}.png
      cp ${STORMroot}/plot/${tc_name}/images/AMAX_WIND-BMAX_WIND_fhrmean_${tc_name}_regional.gif ${COMOUTroot}/plot/evs.hurricane_regional.wind_bias.${stormBasin}.${stormYear}.${stormName}${stormNumber}.png 
      cp ${STORMroot}/plot/${tc_name}/images/ABSTK_ERR_fhrmean_${tc_name}_regional.gif ${COMOUTroot}/plot/evs.hurricane_regional.abstk_err.${stormBasin}.${stormYear}.${stormName}${stormNumber}.png
      cp ${STORMroot}/plot/${tc_name}/images/ALTK_ERR_fhrmean_${tc_name}_regional.gif ${COMOUTroot}/plot/evs.hurricane_regional.altk_bias.${stormBasin}.${stormYear}.${stormName}${stormNumber}.png
      cp ${STORMroot}/plot/${tc_name}/images/CRTK_ERR_fhrmean_${tc_name}_regional.gif ${COMOUTroot}/plot/evs.hurricane_regional.crtk_bias.${stormBasin}.${stormYear}.${stormName}${stormNumber}.png
    fi   
  fi
fi

### two ifs end
fi
fi
### num do loop end
done

#---  Atlantic/EastPacific/WestPacific Basin TC_Stat 
if [ ${stormBasin} = "al" ]; then
  export COMOUTbas=${COMOUTatl}
elif [ ${stormBasin} = "ep" ]; then
  export COMOUTbas=${COMOUTepa}
elif [ ${stormBasin} = "wp" ]; then
  export COMOUTbas=${COMOUTwpa}
fi

nfile=$(ls ${COMOUTbas}/*.tcst |wc -l)
if [ $nfile -ne 0 ]; then

export mdh=010100
export startdateB=${YYYY}${mdh}
export metTCcomin=${COMOUTbas}

if [ ${stormBasin} = "al" ]; then
  export metTCcomout=${DATA}/metTC/atlantic
  if [ ! -d $metTCcomout ]; then mkdir -p $metTCcomout; fi
elif [ ${stormBasin} = "ep" ]; then
  export metTCcomout=${DATA}/metTC/eastpacific
  if [ ! -d $metTCcomout ]; then mkdir -p $metTCcomout; fi
elif [ ${stormBasin} = "wp" ]; then
  export metTCcomout=${DATA}/metTC/westpacific
  if [ ! -d $metTCcomout ]; then mkdir -p $metTCcomout; fi
fi

cd $metTCcomout
#export SEARCH1=INPUT_BASE_template
#export SEARCH2=OUTPUT_BASE_template
#export SEARCH3=INIT_BEG_template
#export SEARCH4=INIT_END_template

#cp ${PARMevs}/TCStat_template_basin.conf .
cp ${PARMevs}/TCStat_template_basin_regional.conf TCStat_template_basin.conf
sed -i "s|$SEARCH1|$metTCcomin|g" TCStat_template_basin.conf
sed -i "s|$SEARCH2|$metTCcomout|g" TCStat_template_basin.conf
sed -i "s|$SEARCH3|$startdateB|g" TCStat_template_basin.conf
sed -i "s|$SEARCH4|$startdateB|g" TCStat_template_basin.conf

#export SEARCH7="TC_STAT_INIT_BEG_temp"
#export SEARCH8="TC_STAT_INIT_END_temp"
export firstday="0101_00"
export lastday="1231_18"
export symdhB=${YYYY}${firstday}
export eymdhB=${YYYY}${lastday}
echo "$symdhB, $eymdhB"

sed -i "s|$SEARCH7|$symdhB|g" TCStat_template_basin.conf
sed -i "s|$SEARCH8|$eymdhB|g" TCStat_template_basin.conf

run_metplus.py -c ${metTCcomout}/TCStat_template_basin.conf
if [ "$SENDCOM" = 'YES' ]; then
  if [ ! -d ${COMOUTbas}/tc_stat ]; then mkdir -p ${COMOUTbas}/tc_stat; fi
  cp ${metTCcomout}/tc_stat/tc_stat.out ${COMOUTbas}/tc_stat/tc_stat_basin.out
  cp ${metTCcomout}/tc_stat/tc_stat_summary.tcst ${COMOUTbas}/tc_stat/tc_stat_summary_basin.tcst
fi
fi

#--- Basin-Storms Plots 
export LOGOroot=${FIXevs}
export PLOTDATA=${metTCcomout}
#export RUN="tropcyc"
export img_quality="low"

export fhr_list="0,12,24,36,48,60,72,84,96,108,120"
export model_tmp_atcf_name_list="MD01,MD02,MD03,MD04"
export model_plot_name_list="GFS,HWRF,HMON,CTCX"
export plot_CI_bars="NO"
export stormNameB=Basin
export tc_name=${stbasin}${under}${stormYear}${under}${stormNameB}
export basin=${stbasin}
export tc_num= 
export tropcyc_model_type="regional"
python ${USHevs}/plot_tropcyc_lead_regional.py

bimgs=$(ls ${metTCcomout}/plot/${tc_name}/images/* |wc -l)
if [ $bimgs -ne 0 ]; then
  cd ${metTCcomout}/plot/${tc_name}/images
  convert ABSAMAX_WIND-BMAX_WIND_fhrmean_${tc_name}_regional.png ABSAMAX_WIND-BMAX_WIND_fhrmean_${tc_name}_regional.gif
  convert AMAX_WIND-BMAX_WIND_fhrmean_${tc_name}_regional.png AMAX_WIND-BMAX_WIND_fhrmean_${tc_name}_regional.gif

  convert ABSTK_ERR_fhrmean_${tc_name}_regional.png ABSTK_ERR_fhrmean_${tc_name}_regional.gif
  convert ALTK_ERR_fhrmean_${tc_name}_regional.png ALTK_ERR_fhrmean_${tc_name}_regional.gif
  convert CRTK_ERR_fhrmean_${tc_name}_regional.png CRTK_ERR_fhrmean_${tc_name}_regional.gif
  rm -f *.png
  if [ "$SENDCOM" = 'YES' ]; then
    if [ ! -d ${COMOUTbas}/plot ]; then mkdir -p ${COMOUTbas}/plot; fi
    if [ "$savePlots" = 'YES' ]; then
#      cp -r ${metTCcomout}/plot/${tc_name}/images/* ${COMOUTbas}/plot/.
      cp -r ${metTCcomout}/plot/${tc_name}/images/ABSAMAX_WIND-BMAX_WIND_fhrmean_${tc_name}_regional.gif ${COMOUTbas}/plot/evs.hurricane_regional.abswind_err.${stormBasin}.${stormYear}.season.png
      cp -r ${metTCcomout}/plot/${tc_name}/images/AMAX_WIND-BMAX_WIND_fhrmean_${tc_name}_regional.gif ${COMOUTbas}/plot/evs.hurricane_regional.wind_bias.${stormBasin}.${stormYear}.season.png
      cp -r ${metTCcomout}/plot/${tc_name}/images/ABSTK_ERR_fhrmean_${tc_name}_regional.gif ${COMOUTbas}/plot/evs.hurricane_regional.abstk_err.${stormBasin}.${stormYear}.season.png
      cp -r ${metTCcomout}/plot/${tc_name}/images/ALTK_ERR_fhrmean_${tc_name}_regional.gif ${COMOUTbas}/plot/evs.hurricane_regional.altk_bias.${stormBasin}.${stormYear}.season.png
      cp -r ${metTCcomout}/plot/${tc_name}/images/CRTK_ERR_fhrmean_${tc_name}_regional.gif ${COMOUTbas}/plot/evs.hurricane_regional.crtk_bias.${stormBasin}.${stormYear}.season.png
    fi   
  fi
fi
### bas do loop end
done
