#!/bin/bash
###############################################################################
# Name of Script: glwu_prep_regions.sh
# Purpose of Script: To create GLWU subregions with ice mask for calculating
#    performance metrics.
# Author: Samira Ardani (samira.ardani@noaa.gov)
###############################################################################

set -x

# create ice mask: ice grids are defined as grids with ice coverage >= 0.15
#     from RTOFS nowcast (i.e., f000 forecast)
# use non-ice grids to calculate stats

# Lake Champlain:
gen_vx_mask \
$COMINglwu/glwu.$VDATE/$RUN/glwu.glwu_lc.t00z.nc \
$COMINglwu/glwu.$VDATE/$RUN/glwu.glwu_lc.t00z.nc \
$DATA/glwu.$VDATE/$RUN/ice_mask.nc \
-type data -mask_field 'name="ice_coverage"; level="(0,*,*)";' -thresh lt0.15 -name ice_mask_lc

if [ $SENDCOM = "YES" ]; then
 cp $DATA/glwu.$VDATE/$RUN/ice_mask_lc.nc $COMINglwu/glwu.$VDATE/$RUN
fi

# Other lakes:
gen_vx_mask \
$COMINglwu/glwu.$VDATE/$RUN/glwu.glwu.t00z.nc \
$COMINglwu/glwu.$VDATE/$RUN/glwu.glwu.t00z.nc \
$DATA/glwu.$VDATE/$RUN/ice_mask.nc \
-type data -mask_field 'name="ice_coverage"; level="(0,*,*)";' -thresh lt0.15 -name ice_mask

if [ $SENDCOM = "YES" ]; then
 cp $DATA/glwu.$VDATE/$RUN/ice_mask.nc $COMINglwu/glwu.$VDATE/$RUN
fi


# Lake Champlain:
gen_vx_mask \
# create subregions using ice mask
#   Other lakes
gen_vx_mask \
$DATA/glwu.$VDATE/$RUN/ice_mask_lc.nc \
$DATA/glwu.$VDATE/$RUN/ice_mask.nc \
$DATA/glwu.$VDATE/$RUN/mask.nc \
-type lat -thresh 'ge-80 && le90' -intersection -name LC

if [ $SENDCOM = "YES" ]; then
 cp $DATA/glwu.$VDATE/$RUN/mask.nc $COMINglwu/glwu.$VDATE/$RUN
fi

#   Other lakes:
gen_vx_mask \
$DATA/glwu.$VDATE/$RUN/ice_mask.nc \
$DATA/glwu.$VDATE/$RUN/ice_mask.nc \
$DATA/glwu.$VDATE/$RUN/greatlakes.lat.nc \
-type lat -thresh 'ge0 && le60' -intersection

if [ $SENDCOM = "YES" ]; then
 cp $DATA/glwu.$VDATE/$RUN/greatlakes.lat.nc $COMINglwu/glwu.$VDATE/$RUN
fi

gen_vx_mask \
$DATA/rtofs.$VDATE/$RUN/greatlakes.lat.nc \
$DATA/rtofs.$VDATE/$RUN/greatlakes.lat.nc \
$DATA/rtofs.$VDATE/$RUN/mask.greatlakes.nc \
-type lon -thresh 'ge-98 && le10' -intersection -name GL


################################ END OF SCRIPT ################################
