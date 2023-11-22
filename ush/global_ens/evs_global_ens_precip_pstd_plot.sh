#!/bin/ksh
#***********************************************************
# This file to average PSTD line type data over stat files
# for plotting but is not used in current version, or
# can be deleted !!!
#
#  Last update: 11/16/2023, by Binbin Zhou (Lynker@NCPE/EMC)
#*********************************************************
set -x 

export stat_data=$DATA/all_stats
mkdir -p $stat_data


yyyy=${VDATE:0:4}
tail='/gefs'
prefix=${EVSIN%%$tail*}
index=${#prefix}
echo $index
COM_IN=${EVSIN:0:$index}
echo $COM_IN


for mm in 10; do
  if [ $mm = 01 ] || [ $mm = 03 ] || [ $mm = 05 ] || [ $mm = 07 ] || [ $mm = 08 ] || [ $mm = 10 ] || [ $mm = 12 ] ; then
    days='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31'
  elif [ $mm = 02 ] ; then
    days='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 '
  else
    days='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30'
  fi

 for dd in $days ; do
     day=$yyyy$mm$dd
   for model in gfs gefs ecme ; do
     MODEL=`echo $model | tr '[a-z]' '[A-Z]'`
     mkdir -p $stat_data/$model
     stat=${COM_IN}/${model}.${day}/${model}_atmos_precip_v${day}.stat
     if [ -s $stat ] ; then
       ln -sf $stat $stat_data/$model/.
     fi 
   done
 done
done


export model
for model in gefs  ; do
    export MODEL=`echo $model | tr '[a-z]' '[A-Z]'`
    >${MODEL}_500HGT_NH_PAC_${yyyy}.txt

    export beg_day=20221005
    export end_day=20221010
    export valid_increment=86400
    export output_base=$DATA/plot
    export stat_file_dir=$stat_data/$model


   ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${PLOT_CONF}/StatAnlysis_fcstGENS_obsCCPA_PSTD_GatherByDate.conf
   export err=$?; err_chk

    #cp $DATA/agg_stat_PSTD.${model}.12Z  agg_stat_PSTD.${model}.${yyyy}.12Z

    #for fhr in 24 48 72 96  120 144 168 192 216 240 264 288 312 336 360 384 ; do
    #  lead=${fhr}0000
    #  while read -r LINE; do
    #    set -A record $LINE
    #    if [ ${record[3]} = $lead ] ; then
    #      echo  ${record[101]} >> ${MODEL}_500HGT_NH_PAC_${yyyy}.txt 
    #    fi
    # done < agg_stat_SAL1L2_to_CNT.${model}.${yyyy}.00Z
    #done

done


sed -e "s!YYYY!${yyyy}!g" -e "s!December!$last!g"  $USHevs/global_ens/evs_global_ens_headline_plot.py  >  evs_global_ens_headline_plot.py 


python evs_global_ens_headline_plot.py
export err=$?; err_chk



