#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_verif_prep.sh
# Purpose of Script: To pre-process RTOFS forecast data into the same spatial
#    and temporal scales as validation data.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

echo "***** START PROCESSING RTOFS FORECASTS on `date` *****"

# convert RTOFS tri-polar coordinates into lat-lon grids
# n024 is nowcast = f000 forecast
mkdir -p $COMOUT/rtofs.$VDATE/$RUN

for ftype in prog diag ice; do
cdo remapbil,$FIXevs/rtofs_$RUN.grid \
$COMOUT/rtofs.$VDATE/rtofs_glo_2ds_n024_${ftype}.nc \
$COMOUT/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_${ftype}.$RUN.nc
done

# f024 forecast for VDATE was issued 1 day earlier
INITDATE=$(date --date="$VDATE -1 day" +%Y%m%d)
mkdir -p $COMOUT/rtofs.$INITDATE/$RUN

for ftype in prog diag ice; do
cdo remapbil,$FIXevs/rtofs_$RUN.grid \
$COMOUT/rtofs.$INITDATE/rtofs_glo_2ds_f024_${ftype}.nc \
$COMOUT/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f024_${ftype}.$RUN.nc
done

# f048 forecast for VDATE was issued 2 days earlier
INITDATE=$(date --date="$VDATE -2 days" +%Y%m%d)
mkdir -p $COMOUT/rtofs.$INITDATE/$RUN

for ftype in prog diag ice; do
cdo remapbil,$FIXevs/rtofs_$RUN.grid \
$COMOUT/rtofs.$INITDATE/rtofs_glo_2ds_f048_${ftype}.nc \
$COMOUT/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f048_${ftype}.$RUN.nc
done

# f072 forecast for VDATE was issued 3 days earlier
INITDATE=$(date --date="$VDATE -3 days" +%Y%m%d)
mkdir -p $COMOUT/rtofs.$INITDATE/$RUN

for ftype in prog diag ice; do
cdo remapbil,$FIXevs/rtofs_$RUN.grid \
$COMOUT/rtofs.$INITDATE/rtofs_glo_2ds_f072_${ftype}.nc \
$COMOUT/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f072_${ftype}.$RUN.nc
done

# f096 forecast for VDATE was issued 4 days earlier
INITDATE=$(date --date="$VDATE -4 days" +%Y%m%d)
mkdir -p $COMOUT/rtofs.$INITDATE/$RUN

for ftype in prog diag ice; do
cdo remapbil,$FIXevs/rtofs_$RUN.grid \
$COMOUT/rtofs.$INITDATE/rtofs_glo_2ds_f096_${ftype}.nc \
$COMOUT/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f096_${ftype}.$RUN.nc
done

# f120 forecast for VDATE was issued 5 days earlier
INITDATE=$(date --date="$VDATE -5 days" +%Y%m%d)
mkdir -p $COMOUT/rtofs.$INITDATE/$RUN

for ftype in prog diag ice; do
cdo remapbil,$FIXevs/rtofs_$RUN.grid \
$COMOUT/rtofs.$INITDATE/rtofs_glo_2ds_f120_${ftype}.nc \
$COMOUT/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f120_${ftype}.$RUN.nc
done

# f144 forecast for VDATE was issued 6 days earlier
INITDATE=$(date --date="$VDATE -6 days" +%Y%m%d)
mkdir -p $COMOUT/rtofs.$INITDATE/$RUN

for ftype in prog diag ice; do
cdo remapbil,$FIXevs/rtofs_$RUN.grid \
$COMOUT/rtofs.$INITDATE/rtofs_glo_2ds_f144_${ftype}.nc \
$COMOUT/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f144_${ftype}.$RUN.nc
done

# f168 forecast for VDATE was issued 7 days earlier
INITDATE=$(date --date="$VDATE -7 days" +%Y%m%d)
mkdir -p $COMOUT/rtofs.$INITDATE/$RUN

for ftype in prog diag ice; do
cdo remapbil,$FIXevs/rtofs_$RUN.grid \
$COMOUT/rtofs.$INITDATE/rtofs_glo_2ds_f168_${ftype}.nc \
$COMOUT/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f168_${ftype}.$RUN.nc
done

# f192 forecast for VDATE was issued 8 days earlier
INITDATE=$(date --date="$VDATE -8 days" +%Y%m%d)
mkdir -p $COMOUT/rtofs.$INITDATE/$RUN

for ftype in prog diag ice; do
cdo remapbil,$FIXevs/rtofs_$RUN.grid \
$COMOUT/rtofs.$INITDATE/rtofs_glo_2ds_f192_${ftype}.nc \
$COMOUT/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f192_${ftype}.$RUN.nc
done

echo "********** COMPLETED SUCCESSFULLY on `date` **********"
exit

################################ END OF SCRIPT ################################
