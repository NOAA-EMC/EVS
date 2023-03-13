set -x

STARTDATE=2023020900
ENDDATE=2023022700
DATE=$STARTDATE

while [ $DATE -le $ENDDATE ]; do

echo $DATE > curdate
DAY=`cut -c 1-8 curdate`

cd /lfs/h2/emc/vpppg/noscrub/emc.vpppg/evs/v1.0/stats/global_ens
ln -sf /lfs/h2/emc/vpppg/noscrub/binbin.zhou/com/evs/v1.0/stats/global_ens/atmos.$DAY atmos.$DAY
ln -sf /lfs/h2/emc/vpppg/noscrub/binbin.zhou/com/evs/v1.0/stats/global_ens/headline.$DAY headline.$DAY

DATE=`/apps/ops/prod/nco/core/prod_util.v2.0.7/exec/ndate +24 $DATE`

done
exit

