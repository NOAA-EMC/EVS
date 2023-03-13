set -x

STARTDATE=2023021500
ENDDATE=2023022800
DATE=$STARTDATE

while [ $DATE -le $ENDDATE ]; do

echo $DATE > curdate
DAY=`cut -c 1-8 curdate`

cd /lfs/h2/emc/vpppg/noscrub/emc.vpppg/evs/v1.0/prep/rtofs
ln -sf  /lfs/h2/emc/ptmp/Lichuan.Chen/evs/v1.0/prep/rtofs/rtofs.${DAY} rtofs.${DAY}

DATE=`/apps/ops/prod/nco/core/prod_util.v2.0.7/exec/ndate +24 $DATE`

done
exit

