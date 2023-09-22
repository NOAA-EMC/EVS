#!/bin/bash
###############################################################################
# Name of Script: exevs_glwu_prep.sh
# Purpose of Script: To copy glwu production data from /dcom to EVS workspace
#    and to maintain a 12-day archive.
# Author: Samira Ardani (samira.ardani@noaa.gov)
###############################################################################

set -x

# get latest glwu data
mkdir -p $COMOUTprep/glwu.$VDATE
cd $COMOUTprep/glwu.$VDATE
leads='n024 f024 f048 f072 f096 f120 f144 f168 f192'
for lead in ${leads}; do
  pattern="glwu.glwu*_*${lead}_*.nc"
  if [ $SENDCOM = "YES" ]; then
   cp -p --no-clobber $COMINglwu/glwu.$VDATE/${pattern} . &
  fi
done
wait
rm -f *hvr*.nc  # don't need these

exit

################################ END OF SCRIPT ################################
