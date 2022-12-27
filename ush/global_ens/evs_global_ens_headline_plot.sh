#!/bin/ksh

set -x 

export stat_data=$DATA/all_stats
mkdir -p $stat_data


yyyy=${VDATE:0:4}
tail='/gefs'
prefix=${COMIN%%$tail*}
index=${#prefix}
echo $index
COM_IN=${COMIN:0:$index}
echo $COM_IN


for mm in 01 02 03 04 05 06 07 08 09 10 ; do
  if [ $mm = 03 ] || [ $mm = 05 ] || [ $mm = 07 ] || [ $mm = 08 ] || [ $mm = 10 ] || [ $mm = 12 ] ; then
    days='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31'
  elif [ $mm = 01 ] ; then
    days='02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31'	  
  elif [ $mm = 02 ] ; then
    days='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 '
  else
    days='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30'
  fi

 for dd in $days ; do
     day=$yyyy$mm$dd
   for model in gfs gefs naefs ; do
     MODEL=`echo $model | tr '[a-z]' '[A-Z]'`
     mkdir -p $stat_data/$model

     if [ $mm -le 9 ] ; then
        stat_file=${COM_IN}/${model}.${day}/${model}_headline_grid2grid_v${day}.stat
     else
        stat_file=${COM_IN}/${model}.${day}/evs.stats.${model}_headline_grid2grid_v${day}.stat
     fi

     #if [ -s $stat_file ] ; then
     #  cp $stat_file  ${COM_IN}/${model}.${day}/${model}_headline_grid2grid_v${day}.stat
     #fi 

      #stat=${COM_IN}/${model}.${day}/${model}_headline_grid2grid_v${day}.stat

     if [ -s $stat ] ; then
       ln -sf $stat_file $stat_data/$model/${model}_headline_grid2grid_v${day}.stat
     fi 
   done
 done
done


last=Oct

export model
for model in gfs gefs naefs ; do
    export MODEL=`echo $model | tr '[a-z]' '[A-Z]'`
    >${MODEL}_500HGT_NH_PAC_${yyyy}.txt

    export beg_day=20220102
    export end_day=20221031
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


sed -e "s!YYYY!${yyyy}!g" -e "s!December!$last!g"  $USHevs/global_ens/evs_global_ens_headline_plot.py  >  evs_global_ens_headline_plot.py 


python evs_global_ens_headline_plot.py



