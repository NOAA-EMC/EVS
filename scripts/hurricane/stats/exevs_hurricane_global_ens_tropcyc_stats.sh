#!/bin/bash
export PS4=' + exevs_hurricane_global_ens_tropcyc_stats.sh line $LINENO: '

export MetOnMachine=/apps/ops/prod/libs/intel/19.1.3.304/met/11.0.0
export LEAD_List="-lead 000000 -lead 120000 -lead 240000 -lead 360000 -lead 480000 -lead 600000 -lead 720000 -lead 840000 -lead 960000 -lead 1080000 -lead 1200000 -lead 1320000 -lead 1440000 -lead 1560000 -lead 1680000"

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

#---get the model forecast tracks "AEMN/EEMN/CEMN" from archive file "tracks.atcfunix.${YY22}"
grep "${stbasin}, ${stormNumber}" ${COMINtrack} > tracks.atcfunix.${YY22}_${stormBasin}${stormNumber}
grep "03, AEMN" tracks.atcfunix.${YY22}_${stormBasin}${stormNumber} > a${stormBasin}${stormNumber}${stormYear}.dat
grep "03, EEMN" tracks.atcfunix.${YY22}_${stormBasin}${stormNumber} >> a${stormBasin}${stormNumber}${stormYear}.dat
grep "03, CEMN" tracks.atcfunix.${YY22}_${stormBasin}${stormNumber} >> a${stormBasin}${stormNumber}${stormYear}.dat
sed -i 's/03, AEMN/03, MD01/' a${stormBasin}${stormNumber}${stormYear}.dat
sed -i 's/03, EEMN/03, MD02/' a${stormBasin}${stormNumber}${stormYear}.dat
sed -i 's/03, CEMN/03, MD03/' a${stormBasin}${stormNumber}${stormYear}.dat
export Model_List="MD01,MD02,MD03"
#export Model_Plot="GEFS,EENS,CENS"

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
cp ${PARMevs}/TCPairs_template.conf .
export SEARCH0="METBASE_template"
export SEARCH1="INPUT_BASE_template"
export SEARCH2="OUTPUT_BASE_template"
export SEARCH3="INIT_BEG_template"
export SEARCH4="INIT_END_template"
export SEARCH5="TC_PAIRS_CYCLONE_template"
export SEARCH6="TC_PAIRS_BASIN_template"
export SEARCHx="MODELLIST_template"

sed -i "s|$SEARCH0|$MetOnMachine|g" TCPairs_template.conf
sed -i "s|$SEARCH1|$STORMdata|g" TCPairs_template.conf
sed -i "s|$SEARCH2|$STORMroot|g" TCPairs_template.conf
sed -i "s|$SEARCH3|$startdate|g" TCPairs_template.conf
sed -i "s|$SEARCH4|$enddate|g" TCPairs_template.conf
sed -i "s|$SEARCH5|$stormNumber|g" TCPairs_template.conf
sed -i "s|$SEARCH6|$stbasin|g" TCPairs_template.conf
sed -i "s|$SEARCHx|$Model_List|g" TCPairs_template.conf

run_metplus.py -c $STORMdata/TCPairs_template.conf

#--- run for TC_stat 
cd $STORMdata
cp ${PARMevs}/TCStat_template.conf .

export SEARCHy="LEAD_template"
sed -i "s|$SEARCH0|$MetOnMachine|g" TCStat_template.conf
sed -i "s|$SEARCH1|$STORMdata|g" TCStat_template.conf
sed -i "s|$SEARCH2|$STORMroot|g" TCStat_template.conf
sed -i "s|$SEARCH3|$startdate|g" TCStat_template.conf
sed -i "s|$SEARCH4|$startdate|g" TCStat_template.conf
sed -i "s|$SEARCHx|$Model_List|g" TCStat_template.conf
sed -i "s|$SEARCHy|$LEAD_List|g" TCStat_template.conf

export SEARCH7="TC_STAT_INIT_BEG_temp"
export SEARCH8="TC_STAT_INIT_END_temp"
export under="_"
export symdh=${YY01}${MM01}${DD01}${under}${HH01}
export eymdh=${YY02}${MM02}${DD02}${under}${HH02}
echo "$symdh, $eymdh"

sed -i "s|$SEARCH7|$symdh|g" TCStat_template.conf
sed -i "s|$SEARCH8|$eymdh|g" TCStat_template.conf

run_metplus.py -c $STORMdata/TCStat_template.conf

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

cp ${PARMevs}/TCStat_template_basin.conf .

#export SEARCHy="LEAD_template"
sed -i "s|$SEARCH0|$MetOnMachine|g" TCStat_template_basin.conf
sed -i "s|$SEARCH1|$metTCcomin|g" TCStat_template_basin.conf
sed -i "s|$SEARCH2|$metTCcomout|g" TCStat_template_basin.conf
sed -i "s|$SEARCH3|$startdateB|g" TCStat_template_basin.conf
sed -i "s|$SEARCH4|$startdateB|g" TCStat_template_basin.conf
sed -i "s|$SEARCHx|$Model_List|g" TCStat_template_basin.conf
sed -i "s|$SEARCHy|$LEAD_List|g" TCStat_template_basin.conf

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

### bas do loop end
done
