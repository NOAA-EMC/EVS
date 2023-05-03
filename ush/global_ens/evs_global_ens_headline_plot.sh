#!/bin/ksh

set -x 

last_year=$1
this_year=$2

export stat_data=$DATA/all_stats
mkdir -p $stat_data



tail='/gefs'
prefix=${COMIN%%$tail*}
index=${#prefix}
echo $index
COM_IN=${COMIN:0:$index}
echo $COM_IN

for yyyy in $last_year $this_year ; do 
 
 if [ $yyyy = $last_year ] ; then
   months='01 02 03 04 05 06 07 08 09 10 11 12'
 else
   months='01'
 fi

for mm in $months  ; do
  if [ $mm = 03 ] || [ $mm = 05 ] || [ $mm = 07 ] || [ $mm = 08 ] || [ $mm = 10 ] || [ $mm = 12 ] ; then
    days='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31'
  elif [ $mm = 01 ] ; then
    days='02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31'	  
  elif [ $mm = 02 ] ; then
    days='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 '
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

     if [ $mm -le 9 ] && [ $yyyy = $last_year ] ; then
        stat_file=${COM_IN}/${model}.${day}/${model}_headline_grid2grid_v${day}.stat
     else
        stat_file=${COM_IN}/${model}.${day}/evs.stats.${model}_headline_grid2grid_v${day}.stat
     fi

     if [ -s $stat ] ; then
       ln -sf $stat_file $stat_data/$model/${model}_headline_grid2grid_v${day}.stat
     fi 
   done #model
  done #day
 done #mm
done #yyyy

last=December

export model
for model in gfs gefs naefs ; do
    export MODEL=`echo $model | tr '[a-z]' '[A-Z]'`
    >${MODEL}_500HGT_NH_PAC_${yyyy}.txt

    export beg_day=${last_year}0102
    export end_day=${this_year}0116
    export valid_increment=86400
    export output_base=$DATA/plot
    export stat_file_dir=$stat_data/$model

   # stat_analysis -lookin $stat_data/$model/${model}_headline_*${yyyy}*.stat -fcst_valid_hour 00  -job aggregate_stat -line_type SAL1L2 -out_line_type CNT -by FCST_VAR,FCST_LEV,FCST_LEAD,VX_MASK -out_stat agg_stat_SAL1L2_to_CNT.${model}.${yyyy}.00Z

   ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PLOT_CONF}/StatAnlysis_fcstGENS_obsAnalysis_GatherByYear.conf
                         agg_stat_SAL1L2_to_CNT.gfs.00Z 
   cp $DATA/agg_stat_SAL1L2_to_CNT.${model}.00Z  agg_stat_SAL1L2_to_CNT.${model}.${yyyy}.00Z

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


sed -e "s!YYYY!${last_year}!g" -e "s!December!$last!g"  $USHevs/global_ens/evs_global_ens_headline_plot.py  >  evs_global_ens_headline_plot.py 


python evs_global_ens_headline_plot.py

cp NH_H500_PAC_${last_year}.png.png $COMOUT/evs.plot.gefs.headline.hgt_p500.${last_year}.nhem.png 


