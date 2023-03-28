#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_prep.sh
# Purpose of Script: To copy RTOFS production data from /com to EVS workspace
#    and to maintain a 12-day archive.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

# get latest RTOFS data
mkdir -p $COMOUTprep/rtofs.$VDATE
cd $COMOUTprep/rtofs.$VDATE
leads='n024 f024 f048 f072 f096 f120 f144 f168 f192'
for lead in ${leads}; do
  pattern="rtofs_glo_*_${lead}_*.nc"
  cp -p --no-clobber $COMINrtofs/rtofs.$VDATE/${pattern} . &
done
wait
rm -f *hvr*.nc  # don't need these

# touch RTOFS data in previous 12 days to keep them in scrub space
TDATE=$(date --date="$VDATE -1 day" +%Y%m%d)
EDATE=$(date --date="$VDATE -12 days" +%Y%m%d)
while [ $TDATE -ge $EDATE ] ; do 
  cd $COMOUTprep/rtofs.$TDATE
  touch *.nc
  for dir in $(ls -d */); do
    touch $dir/*.nc
  done

  TDATE=$(date --date="$TDATE -1 day" +%Y%m%d)
done
exit

################################ END OF SCRIPT ################################
