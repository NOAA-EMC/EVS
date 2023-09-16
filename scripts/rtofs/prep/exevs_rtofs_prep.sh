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
  if [ $SENDCOM = "YES" ]; then
   cp -p --no-clobber $COMINrtofs/rtofs.$VDATE/${pattern} . &
  fi
done
wait
rm -f *hvr*.nc  # don't need these

exit

################################ END OF SCRIPT ################################
