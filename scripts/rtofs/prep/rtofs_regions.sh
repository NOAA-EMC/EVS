#!/bin/bash
###############################################################################
# Name of Script: rtofs_regions.sh
# Purpose of Script: To create RTOFS subregions with ice mask for calculating
#    performance metrics.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
###############################################################################

set -x

# create ice mask: ice grids are defined as grids with ice coverage >= 0.15
#     from RTOFS nowcast (i.e., f000 forecast)
# use non-ice grids to calculate stats
gen_vx_mask \
$COMOUTprep/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_ice.$RUN.nc \
$COMOUTprep/rtofs.$VDATE/$RUN/rtofs_glo_2ds_f000_ice.$RUN.nc \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
-type data -mask_field 'name="ice_coverage"; level="(0,*,*)";' -thresh lt0.15 -name ice_mask

cp $DATA/rtofs.$VDATE/$RUN/ice_mask.nc $COMOUTprep/rtofs.$VDATE/$RUN

# create subregions using ice mask
#   Global
gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/mask.global.nc \
-type lat -thresh 'ge-80 && le90' -intersection -name GLB

cp $DATA/rtofs.$VDATE/$RUN/mask.global.nc $COMOUTprep/rtofs.$VDATE/$RUN

#   North Atlantic Ocean
gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/north_atlantic.lat.nc \
-type lat -thresh 'ge0 && le60' -intersection

cp $DATA/rtofs.$VDATE/$RUN/north_atlantic.lat.nc $COMOUTprep/rtofs.$VDATE/$RUN

gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/north_atlantic.lat.nc \
$DATA/rtofs.$VDATE/$RUN/north_atlantic.lat.nc \
$DATA/rtofs.$VDATE/$RUN/mask.north_atlantic.nc \
-type lon -thresh 'ge-98 && le10' -intersection -name NATL

#   South Atlantic Ocean
gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/south_atlantic.lat.nc \
-type lat -thresh 'ge-80 && le0' -intersection

cp $DATA/rtofs.$VDATE/$RUN/south_atlantic.lat.nc $COMOUTprep/rtofs.$VDATE/$RUN

gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/south_atlantic.lat.nc \
$DATA/rtofs.$VDATE/$RUN/south_atlantic.lat.nc \
$DATA/rtofs.$VDATE/$RUN/mask.south_atlantic.nc \
-type lon -thresh 'ge-70 && le20' -intersection -name SATL

#   Equatorial Atlantic Ocean
gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/equatorial_atlantic.lat.nc \
-type lat -thresh 'ge-30 && le30' -intersection

cp $DATA/rtofs.$VDATE/$RUN/equatorial_atlantic.lat.nc $COMOUTprep/rtofs.$VDATE/$RUN

gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/equatorial_atlantic.lat.nc \
$DATA/rtofs.$VDATE/$RUN/equatorial_atlantic.lat.nc \
$DATA/rtofs.$VDATE/$RUN/mask.equatorial_atlantic.nc \
-type lon -thresh 'ge-80 && le30' -intersection -name EQATL

#   North Pacific Ocean
gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/north_pacific.lat.nc \
-type lat -thresh 'ge0 && le70' -intersection

cp $DATA/rtofs.$VDATE/$RUN/north_pacific.lat.nc $COMOUTprep/rtofs.$VDATE/$RUN

gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/north_pacific.lat.nc \
$DATA/rtofs.$VDATE/$RUN/north_pacific.lat.nc \
$DATA/rtofs.$VDATE/$RUN/northeast_pacific.nc \
-type lon -thresh 'ge-180 && le-84' -intersection -name NEPAC

cp $DATA/rtofs.$VDATE/$RUN/northeast_pacific.nc $COMOUTprep/rtofs.$VDATE/$RUN

gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/north_pacific.lat.nc \
$DATA/rtofs.$VDATE/$RUN/north_pacific.lat.nc \
$DATA/rtofs.$VDATE/$RUN/northwest_pacific.nc \
-type lon -thresh 'ge101 && le180' -intersection -name NWPAC

cp $DATA/rtofs.$VDATE/$RUN/northwest_pacific.nc $COMOUTprep/rtofs.$VDATE/$RUN

gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/northeast_pacific.nc \
$DATA/rtofs.$VDATE/$RUN/northwest_pacific.nc \
$DATA/rtofs.$VDATE/$RUN/mask.north_pacific.nc \
-type data -mask_field 'name="NWPAC"; level="(*,*)";' -thresh eq1 -union -name NPAC

#   South Pacific Ocean
gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/south_pacific.lat.nc \
-type lat -thresh 'ge-80 && le0' -intersection

cp $DATA/rtofs.$VDATE/$RUN/south_pacific.lat.nc $COMOUTprep/rtofs.$VDATE/$RUN

gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/south_pacific.lat.nc \
$DATA/rtofs.$VDATE/$RUN/south_pacific.lat.nc \
$DATA/rtofs.$VDATE/$RUN/southeast_pacific.nc \
-type lon -thresh 'ge-180 && le-70' -intersection -name SEPAC

cp $DATA/rtofs.$VDATE/$RUN/southeast_pacific.nc $COMOUTprep/rtofs.$VDATE/$RUN

gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/south_pacific.lat.nc \
$DATA/rtofs.$VDATE/$RUN/south_pacific.lat.nc \
$DATA/rtofs.$VDATE/$RUN/southwest_pacific.nc \
-type lon -thresh 'ge115 && le180' -intersection -name SWPAC

cp $DATA/rtofs.$VDATE/$RUN/southwest_pacific.nc $COMOUTprep/rtofs.$VDATE/$RUN

gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/southeast_pacific.nc \
$DATA/rtofs.$VDATE/$RUN/southwest_pacific.nc \
$DATA/rtofs.$VDATE/$RUN/mask.south_pacific.nc \
-type data -mask_field 'name="SWPAC"; level="(*,*)";' -thresh eq1 -union -name SPAC

#   Equatorial Pacific Ocean
gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/equatorial_pacific.lat.nc \
-type lat -thresh 'ge-30 && le30' -intersection

cp $DATA/rtofs.$VDATE/$RUN/equatorial_pacific.lat.nc $COMOUTprep/rtofs.$VDATE/$RUN

gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/equatorial_pacific.lat.nc \
$DATA/rtofs.$VDATE/$RUN/equatorial_pacific.lat.nc \
$DATA/rtofs.$VDATE/$RUN/centraleast_pacific.nc \
-type lon -thresh 'ge-180 && le-80' -intersection -name CEPAC

cp $DATA/rtofs.$VDATE/$RUN/centraleast_pacific.nc $COMOUTprep/rtofs.$VDATE/$RUN

gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/equatorial_pacific.lat.nc \
$DATA/rtofs.$VDATE/$RUN/equatorial_pacific.lat.nc \
$DATA/rtofs.$VDATE/$RUN/centralwest_pacific.nc \
-type lon -thresh 'ge115 && le180' -intersection -name CWPAC

cp $DATA/rtofs.$VDATE/$RUN/centralwest_pacific.nc $COMOUTprep/rtofs.$VDATE/$RUN

gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/centraleast_pacific.nc \
$DATA/rtofs.$VDATE/$RUN/centralwest_pacific.nc \
$DATA/rtofs.$VDATE/$RUN/mask.equatorial_pacific.nc \
-type data -mask_field 'name="CWPAC"; level="(*,*)";' -thresh eq1 -union -name EQPAC

#   Indian Ocean
gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/indian.lat.nc \
-type lat -thresh 'ge-75 && le30' -intersection

cp $DATA/rtofs.$VDATE/$RUN/indian.lat.nc $COMOUTprep/rtofs.$VDATE/$RUN

gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/indian.lat.nc \
$DATA/rtofs.$VDATE/$RUN/indian.lat.nc \
$DATA/rtofs.$VDATE/$RUN/mask.indian.nc \
-type lon -thresh 'ge20 && le115' -intersection -name IND

#   Southern Ocean
gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/mask.southern.nc \
-type lat -thresh 'ge-80 && le-30' -intersection -name SOC

#   Arctic Ocean
gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/mask.arctic.nc \
-type lat -thresh 'ge50 && le90' -intersection -name Arctic

#   Mediterranean Sea
gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/ice_mask.nc \
$DATA/rtofs.$VDATE/$RUN/mediterranean.lat.nc \
-type lat -thresh 'ge29 && le48' -intersection

cp $DATA/rtofs.$VDATE/$RUN/mediterranean.lat.nc $COMOUTprep/rtofs.$VDATE/$RUN

gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/mediterranean.lat.nc \
$DATA/rtofs.$VDATE/$RUN/mediterranean.lat.nc \
$DATA/rtofs.$VDATE/$RUN/mask.mediterranean.nc \
-type lon -thresh 'ge-2 && le45' -intersection -name MEDIT

cp -rp $DATA/rtofs.$VDATE/$RUN/*mask* $COMOUTprep/rtofs.$VDATE/$RUN

exit

################################ END OF SCRIPT ################################
