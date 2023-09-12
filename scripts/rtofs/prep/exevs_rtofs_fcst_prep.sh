#!/bin/bash
###############################################################################
# Name of Script: exevs_rtofs_fcst_prep.sh
# Purpose of Script: To pre-process RTOFS forecast data into the same spatial
#    and temporal scales as validation data.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

echo "***** START PROCESSING RTOFS FORECASTS on `date` *****"

# convert RTOFS tri-polar coordinates into lat-lon grids
# n024 is nowcast = f000 forecast
mkdir -p $COMOUTprep/rtofs.$VDATE/$RUN
mkdir -p $DATA/rtofs.$VDATE/$RUN

for ftype in prog diag ice; do
  cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
  $COMOUTprep/rtofs.$VDATE/rtofs_glo_2ds_n024_${ftype}.nc \
  $DATA/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_${ftype}.$RUN.nc
  if [ $SENDCOM = "YES" ]; then
   cp $DATA/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_${ftype}.$RUN.nc $COMOUTprep/rtofs.$VDATE/$RUN
  fi
done

if [ $RUN = 'argo' ] ; then
  for ftype in t s; do
    cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
    $COMOUTprep/rtofs.$VDATE/rtofs_glo_3dz_n024_daily_3z${ftype}io.nc \
    $DATA/rtofs.$VDATE/$RUN/rtofs_glo_3dz_f000_daily_3z${ftype}io.$RUN.nc
    if [ $SENDCOM = "YES" ]; then
     cp $DATA/rtofs.$VDATE/$RUN/rtofs_glo_3dz_f000_daily_3z${ftype}io.$RUN.nc $COMOUTprep/rtofs.$VDATE/$RUN
    fi
  done
fi

# f024 forecast for VDATE was issued 1 day earlier
INITDATE=$(date --date="$VDATE -1 day" +%Y%m%d)
mkdir -p $COMOUTprep/rtofs.$INITDATE/$RUN
mkdir -p $DATA/rtofs.$INITDATE/$RUN

for ftype in prog diag ice; do
  cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
  $COMOUTprep/rtofs.$INITDATE/rtofs_glo_2ds_f024_${ftype}.nc \
  $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f024_${ftype}.$RUN.nc
  if [ $SENDCOM = "YES" ]; then
   cp $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f024_${ftype}.$RUN.nc $COMOUTprep/rtofs.$INITDATE/$RUN
  fi
done

if [ $RUN = 'argo' ] ; then
  for ftype in t s; do
    cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
    $COMOUTprep/rtofs.$INITDATE/rtofs_glo_3dz_f024_daily_3z${ftype}io.nc \
    $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f024_daily_3z${ftype}io.$RUN.nc
    if [ $SENDCOM = "YES" ]; then
     cp $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f024_daily_3z${ftype}io.$RUN.nc $COMOUTprep/rtofs.$INITDATE/$RUN
    fi
  done
fi

# f048 forecast for VDATE was issued 2 days earlier
INITDATE=$(date --date="$VDATE -2 days" +%Y%m%d)
mkdir -p $COMOUTprep/rtofs.$INITDATE/$RUN
mkdir -p $DATA/rtofs.$INITDATE/$RUN

for ftype in prog diag ice; do
  cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
  $COMOUTprep/rtofs.$INITDATE/rtofs_glo_2ds_f048_${ftype}.nc \
  $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f048_${ftype}.$RUN.nc
  if [ $SENDCOM = "YES" ]; then
   cp $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f048_${ftype}.$RUN.nc $COMOUTprep/rtofs.$INITDATE/$RUN
  fi
done

if [ $RUN = 'argo' ] ; then
  for ftype in t s; do
    cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
    $COMOUTprep/rtofs.$INITDATE/rtofs_glo_3dz_f048_daily_3z${ftype}io.nc \
    $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f048_daily_3z${ftype}io.$RUN.nc
    if [ $SENDCOM = "YES" ]; then
     cp $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f048_daily_3z${ftype}io.$RUN.nc $COMOUTprep/rtofs.$INITDATE/$RUN
    fi
  done
fi

# f072 forecast for VDATE was issued 3 days earlier
INITDATE=$(date --date="$VDATE -3 days" +%Y%m%d)
mkdir -p $COMOUTprep/rtofs.$INITDATE/$RUN
mkdir -p $DATA/rtofs.$INITDATE/$RUN

for ftype in prog diag ice; do
  cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
  $COMOUTprep/rtofs.$INITDATE/rtofs_glo_2ds_f072_${ftype}.nc \
  $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f072_${ftype}.$RUN.nc
  if [ $SENDCOM = "YES" ]; then
   cp $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f072_${ftype}.$RUN.nc $COMOUTprep/rtofs.$INITDATE/$RUN
  fi
done

if [ $RUN = 'argo' ] ; then
  for ftype in t s; do
    cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
    $COMOUTprep/rtofs.$INITDATE/rtofs_glo_3dz_f072_daily_3z${ftype}io.nc \
    $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f072_daily_3z${ftype}io.$RUN.nc
    if [ $SENDCOM = "YES" ]; then
     cp $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f072_daily_3z${ftype}io.$RUN.nc $COMOUTprep/rtofs.$INITDATE/$RUN
    fi
  done
fi

# f096 forecast for VDATE was issued 4 days earlier
INITDATE=$(date --date="$VDATE -4 days" +%Y%m%d)
mkdir -p $COMOUTprep/rtofs.$INITDATE/$RUN
mkdir -p $DATA/rtofs.$INITDATE/$RUN

for ftype in prog diag ice; do
  cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
  $COMOUTprep/rtofs.$INITDATE/rtofs_glo_2ds_f096_${ftype}.nc \
  $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f096_${ftype}.$RUN.nc
  if [ $SENDCOM = "YES" ]; then
   cp $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f096_${ftype}.$RUN.nc $COMOUTprep/rtofs.$INITDATE/$RUN
  fi 
done

if [ $RUN = 'argo' ] ; then
  for ftype in t s; do
    cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
    $COMOUTprep/rtofs.$INITDATE/rtofs_glo_3dz_f096_daily_3z${ftype}io.nc \
    $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f096_daily_3z${ftype}io.$RUN.nc
    if [ $SENDCOM = "YES" ]; then
     cp  $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f096_daily_3z${ftype}io.$RUN.nc $COMOUTprep/rtofs.$INITDATE/$RUN
    fi
  done
fi

# f120 forecast for VDATE was issued 5 days earlier
INITDATE=$(date --date="$VDATE -5 days" +%Y%m%d)
mkdir -p $COMOUTprep/rtofs.$INITDATE/$RUN
mkdir -p $DATA/rtofs.$INITDATE/$RUN

for ftype in prog diag ice; do
  cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
  $COMOUTprep/rtofs.$INITDATE/rtofs_glo_2ds_f120_${ftype}.nc \
  $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f120_${ftype}.$RUN.nc
  if [ $SENDCOM = "YES" ]; then
   cp $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f120_${ftype}.$RUN.nc $COMOUTprep/rtofs.$INITDATE/$RUN
  fi
done

if [ $RUN = 'argo' ] ; then
  for ftype in t s; do
    cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
    $COMOUTprep/rtofs.$INITDATE/rtofs_glo_3dz_f120_daily_3z${ftype}io.nc \
    $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f120_daily_3z${ftype}io.$RUN.nc
    if [ $SENDCOM = "YES" ]; then
     cp $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f120_daily_3z${ftype}io.$RUN.nc $COMOUTprep/rtofs.$INITDATE/$RUN
    fi
  done
fi

# f144 forecast for VDATE was issued 6 days earlier
INITDATE=$(date --date="$VDATE -6 days" +%Y%m%d)
mkdir -p $COMOUTprep/rtofs.$INITDATE/$RUN
mkdir -p $DATA/rtofs.$INITDATE/$RUN

for ftype in prog diag ice; do
  cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
  $COMOUTprep/rtofs.$INITDATE/rtofs_glo_2ds_f144_${ftype}.nc \
  $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f144_${ftype}.$RUN.nc
  if [ $SENDCOM = "YES" ]; then
   cp $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f144_${ftype}.$RUN.nc $COMOUTprep/rtofs.$INITDATE/$RUN
  fi
done

if [ $RUN = 'argo' ] ; then
  for ftype in t s; do
    cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
    $COMOUTprep/rtofs.$INITDATE/rtofs_glo_3dz_f144_daily_3z${ftype}io.nc \
    $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f144_daily_3z${ftype}io.$RUN.nc
    if [ $SENDCOM = "YES" ]; then
     cp $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f144_daily_3z${ftype}io.$RUN.nc $COMOUTprep/rtofs.$INITDATE/$RUN
    fi
  done
fi

# f168 forecast for VDATE was issued 7 days earlier
INITDATE=$(date --date="$VDATE -7 days" +%Y%m%d)
mkdir -p $COMOUTprep/rtofs.$INITDATE/$RUN
mkdir -p $DATA/rtofs.$INITDATE/$RUN

for ftype in prog diag ice; do
  cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
  $COMOUTprep/rtofs.$INITDATE/rtofs_glo_2ds_f168_${ftype}.nc \
  $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f168_${ftype}.$RUN.nc
  if [ $SENDCOM = "YES" ]; then
   cp $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f168_${ftype}.$RUN.nc $COMOUTprep/rtofs.$INITDATE/$RUN
  fi
done

if [ $RUN = 'argo' ] ; then
  for ftype in t s; do
    cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
    $COMOUTprep/rtofs.$INITDATE/rtofs_glo_3dz_f168_daily_3z${ftype}io.nc \
    $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f168_daily_3z${ftype}io.$RUN.nc
    if [ $SENDCOM = "YES" ]; then
     cp $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f168_daily_3z${ftype}io.$RUN.nc $COMOUTprep/rtofs.$INITDATE/$RUN
    fi
  done
fi

# f192 forecast for VDATE was issued 8 days earlier
INITDATE=$(date --date="$VDATE -8 days" +%Y%m%d)
mkdir -p $COMOUTprep/rtofs.$INITDATE/$RUN
mkdir -p $DATA/rtofs.$INITDATE/$RUN

for ftype in prog diag ice; do
  cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
  $COMOUTprep/rtofs.$INITDATE/rtofs_glo_2ds_f192_${ftype}.nc \
  $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f192_${ftype}.$RUN.nc
  if [ $SENDCOM = "YES" ]; then
   cp $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_2ds_f192_${ftype}.$RUN.nc $COMOUTprep/rtofs.$INITDATE/$RUN
  fi
done

if [ $RUN = 'argo' ] ; then
  for ftype in t s; do
    cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
    $COMOUTprep/rtofs.$INITDATE/rtofs_glo_3dz_f192_daily_3z${ftype}io.nc \
    $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f192_daily_3z${ftype}io.$RUN.nc
    if [ $SENDCOM = "YES" ]; then
     cp $DATA/rtofs.$INITDATE/$RUN/rtofs_glo_3dz_f192_daily_3z${ftype}io.$RUN.nc $COMOUTprep/rtofs.$INITDATE/$RUN
    fi
  done
fi


# Create the masks
 
$HOMEevs/scripts/$COMPONENT/$STEP/rtofs_regions.sh

echo "********** COMPLETED SUCCESSFULLY on `date` **********"
exit

################################ END OF SCRIPT ################################
