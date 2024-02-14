#!/bin/ksh
#**************************************************************************************
# Purpose: To build virtually link for past 31/90 days of href stat data files required
#          by href plot jobs
# Last update: 10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
#**************************************************************************************
set -x 

day=$1
MODEL_LIST=$2
VRF_CASE=${VERIF_CASE}

archive=$output_base_dir
prefix=${COMIN%%cam*}
index=${#prefix}
echo $index
COM_IN=${COMIN:0:$index}
echo $COM_IN

if [ ${VERIF_CASE} = profile ] || [ $VERIF_CASE = grid2obs_ecnt ] || [ $VERIF_CASE = grid2obs_ctc ] || [ $VERIF_CASE = grid2obs_mlcape ] || [ $VERIF_CASE = grid2obs_cape ] ; then
  VRF_CASE=grid2obs
elif [ ${VERIF_CASE} = snowfall ] ; then
  VRF_CASE=precip
elif [ ${VERIF_CASE} = precip_fss ] ; then
  VRF_CASE=precip 
else
  VRF_CASE=${VERIF_CASE}
fi

for MODEL in $MODEL_LIST ; do
 
  model=`echo $MODEL | tr '[A-Z]' '[a-z]'`

  model_archive=${archive}/${model}

  mkdir -p $model_archive

  cd $model_archive

  model_stat_dir=${COM_IN}/cam/href.${day}

  stat_file=${model_stat_dir}/evs.stats.${model}.${VRF_CASE}.v${day}.stat

  if [ $VERIF_CASE = grid2obs_mlcape ] || [ $VERIF_CASE = spcoutlook ] || [ $VERIF_CASE = grid2obs_ctc  ] || [ $VERIF_CASE = grid2obs_cape ]  ; then
    if [ -s $stat_file ] ; then
      cp  $stat_file ${MODEL}_${day}.stat
      #Binbin note: fcst level and obs level must be same string!
      #Note2 change MLCAPE's fcst name from CAPE to MLCAPE and level to ML 
      #Note3 change HGT to HGTcldceili for ceiling height to avoid confusing with geopotential height
      grep L0 ${MODEL}_${day}.stat > L0
      sed -e "s!HGT!HGTcldceil!g" -e "s!gpm!m!g" L0 > hgt
      mv hgt L0
      grep MLCAPE ${MODEL}_${day}.stat | sed -e "s! CAPE ! MLCAPE!g" -e "s!L100000-0!ML!g" -e "s!P90-0!ML!g"  > mlcape
      cat mlcape >> L0 
      if [  $VERIF_CASE = grid2obs_ctc  ] || [ $VERIF_CASE = grid2obs_cape ] ; then 
        mv L0  ${MODEL}_${day}.stat
      elif [ $VERIF_CASE = spcoutlook ] ; then
       #Conbine all issued times of one day together
        sed  -e "s!DAY1_1200_MRGL!DAY1_MRGL!g"  -e "s!DAY2_1730_MRGL!DAY2_MRGL!g" -e "s!DAY1_1200_SLGT!DAY1_SLGt!g"  -e "s!DAY2_1730_SLGT!DAY2_SLGT!g"  -e "s!DAY1_1200_TSTM!DAY1_TSTM!g"  -e "s!DAY2_1730_TSTM!DAY2_TSTM!g" -e "s!DAY1_1200_ENH!DAY1_ENH!g"  -e "s!DAY2_1730_ENH!DAY2_ENH!g"  -e "s!DAY1_1200_MDT!DAY1_MDT!g"  -e "s!DAY2_1730_MDT!DAY2_MDT!g" -e "s!DAY1_1200_HIGH!DAY1_HIGH!g" -e "s!DAY2_1730_HIGH!DAY2_HIGH!g" L0 > risk
	mv risk ${MODEL}_${day}.stat 
      fi   	  
    fi
  else
    if [ -s $stat_file ] ; then
      ln -sf $stat_file ${MODEL}_${day}.stat
    fi 
  fi


done
  

