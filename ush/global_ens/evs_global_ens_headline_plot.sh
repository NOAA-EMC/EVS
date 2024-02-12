#!/bin/ksh

#**********************************************************************************************
# Purose: generate GEFS headline ACC plot
#    
# Procedure steps:
#        (1) Collect (virtual link) 12 months of headline stat files
#        (2) Average all of the sheadline stat files  by running MET StatAnlysis too
#            and save the output text files for GEFS, NAEFS and GFS, respectively
#            These 3 text files contained averaged ACC score data
#        (3) Send these 3 text files in $DATA to a python script to generate plot 
#               GEFS_500HGT_NH_PAC_2023.txt files, 
#               GFS_500HGT_NH_PAC_2023.txt and
#               NAEFS_500HGT_NH_PAC_2023.txt
#             Note: These 3 txt files contain ACC for each forecat days which
#                can be used to calculate the days when ACC drops below 0.6
#        (4) Run the python script evs_global_ens_headline_plot.py to generate
#            the headline plot. The plot tar file has only one png file with file name:
#            evs.global_ens.acc.hgt_p500.lastYear0101_thisYear0116.fhrmean_valid00z_f384.g003_nhem.png
#        (5) Send the plot tar file to $COMOUT 
#
#   Last update: 11/16/2023  by Binbin Zhou (Lynker@NCPE/EMC)
#**********************************************************************************************

set -x 

last_year=$1
this_year=$2

export stat_data=$DATA/all_stats
mkdir -p $stat_data



tail='/gefs'
prefix=${EVSIN%%$tail*}
index=${#prefix}
echo $index
COM_IN=${EVSIN:0:$index}
echo $COM_IN

if [ $run_entire_year = yes ] ; then
  years="$last_year $this_year"
else
  years=$this_year
fi

m[1]=01
m[2]=02
m[3]=03
m[4]=04
m[5]=05
m[6]=06
m[7]=07
m[8]=08
m[9]=09
m[10]=10
m[11]=11
m[12]=12

for yyyy in $years ; do

 if [ $yyyy = $last_year ] ; then
   if [ $run_entire_year = yes ] ; then
       months='01 02 03 04 05 06 07 08 09 10 11 12'
   else
       mon=${VDATE:4:2}
       months=${m[1]}
       n=2
       while [ $n -le $mon ] ; do
	months="$months ${m[$n]}"
        n=$((n+1))
       done
   fi
 else
   months='01'
 fi



#********************************************************
# Virtual link 12 months of headline stat files
#*********************************************************
for mm in $months  ; do
  if [ $mm = 03 ] || [ $mm = 05 ] || [ $mm = 07 ] || [ $mm = 08 ] || [ $mm = 10 ] || [ $mm = 12 ] ; then
    days='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31'
  elif [ $mm = 01 ] ; then
    days='02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31'	  
  elif [ $mm = 02 ] ; then
    
    #**************************************
    #Check if the last year was leap year
    #  if nn=0, last year was leap year
    #**************************************	  
    nn=$(($last_year % 4))
    if [ $nn = 0 ] ; then
       days='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 '
    else
       days='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 '
    fi
  else
    days='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30'
  fi

  if [ $yyyy = $this_year ] && [ $mm = 01 ] ; then
    days='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16'
  fi 

 for dd in $days ; do
     day=$yyyy$mm$dd
   for model in gfs gefs naefs ; do
     MODEL=`echo $model | tr '[a-z]' '[A-Z]'`
     mkdir -p $stat_data/$model

     #if [ $mm -le 9 ] && [ $yyyy = $last_year ] ; then
     #   stat_file=${COM_IN}/${model}.${day}/${model}_headline_grid2grid_v${day}.stat
     #else
        stat_file=${COM_IN}/${model}.${day}/evs.stats.${model}.headline.grid2grid.v${day}.stat
     #fi

     if [ -s $stat_file ] ; then
       ln -sf $stat_file $stat_data/$model/${model}_headline_grid2grid_v${day}.stat
     fi 
   done #model
  done #day
 done #mm
done #yyyy

#****************************************************************
# Average the SAL1L2 line type data over all stat files by using
#  MET StatAnlysis tool
#***************************************************************
export model

if [ $run_entire_year = yes ] ; then
  yyyy=$last_year
else
  yyyy=$this_year
fi


for model in gfs gefs naefs ; do
    export MODEL=`echo $model | tr '[a-z]' '[A-Z]'`
    >${MODEL}_500HGT_NH_PAC_${yyyy}.txt

    export beg_day=${last_year}0101
    if [ $run_entire_year = yes ] ; then
      export end_day=${this_year}0116
    else
      export end_day=$VDATE
    fi
    export valid_increment=86400
    export output_base=$DATA/plot
    export stat_file_dir=$stat_data/$model

    stat_analysis -lookin $stat_data/$model/${model}_headline_grid2grid_v*.stat -fcst_valid_hour 00  -job aggregate_stat -line_type SAL1L2 -out_line_type CNT -by FCST_VAR,FCST_LEV,FCST_LEAD,VX_MASK -out_stat agg_stat_SAL1L2_to_CNT.${model}.${yyyy}.00Z

   ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PLOT_CONF}/StatAnlysis_fcstGENS_obsAnalysis_GatherByYear.conf 
   export err=$?; err_chk

   #*********************************************************************************
   # Save StatAnlysis output text file that contain averaged ACC for plotting script
   #*********************************************************************************
   mv $DATA/agg_stat_SAL1L2_to_CNT.${model}.00Z  agg_stat_SAL1L2_to_CNT.${model}.${yyyy}.00Z

    for fhr in 24 48 72 96  120 144 168 192 216 240 264 288 312 336 360 384 ; do
      lead=${fhr}0000
      while read -r LINE; do
        set -A record $LINE
        if [ ${record[3]} = $lead ] ; then
          echo  ${record[101]} >> ${MODEL}_500HGT_NH_PAC_${yyyy}.txt 
        fi
     done < agg_stat_SAL1L2_to_CNT.${model}.${yyyy}.00Z
  done

done

if [ $run_entire_year = yes ] ; then
 last="December 31st ${last_year}"
 first="January 1st"
else
 last=$end_day
 first=$beg_day
fi

#********************************************************************
# Run evs_global_ens_headline_plot.py python script to generate plots
#********************************************************************
sed -e "s!YYYY!${last_year}!g" -e "s!FIRST!$first!g" -e "s!LAST!$last!g"  $USHevs/global_ens/evs_global_ens_headline_plot.py  >  evs_global_ens_headline_plot.py 


python evs_global_ens_headline_plot.py
export err=$?; err_chk

cp -v NH_H500_PAC_${last_year}.png  evs.global_ens.acc.hgt_p500.${beg_day}_${end_day}.fhrmean_valid00z_f384.g003_nhem.png
