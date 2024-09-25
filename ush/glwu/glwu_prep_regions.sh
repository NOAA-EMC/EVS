#!/bin/bash
###############################################################################
# Name of Script: glwu_prep_regions.sh
# Purpose of Script: To create GLWU subregions with ice mask for calculating
#    performance metrics.
# Author: Samira Ardani (samira.ardani@noaa.gov)
###############################################################################

set -x

# create ice mask: ice grids are defined as grids with ice coverage >= 0.15
#     from GLWU nowcast (i.e., f000 forecast)
# use non-ice grids to calculate stats

# Lake Champlain:
if [ -s $COMINglwu/glwu.$VDATE/glwu.glwu_lc.t00z.nc ]; then
	gen_vx_mask \
	$COMINglwu/glwu.$VDATE/glwu.glwu_lc.t00z.nc \
	$COMINglwu/glwu.$VDATE/glwu.glwu_lc.t00z.nc \
	$DATA/masks/ice_mask.nc \
	-type data -mask_field 'name="ice_coverage"; level="(0,*,*)";' -thresh lt0.15 -name ice_mask_lc
	export err=$?; err_chk
	if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/masks/ice_mask_lc.nc ]; then
			cp $DATA/masks/ice_mask_lc.nc $ARCmodel/
		fi
	fi
fi
# Other lakes:

if [ -s $COMINglwu/glwu.$VDATE/glwu.glwu.t00z.nc ]; then
	gen_vx_mask \
	$COMINglwu/glwu.$VDATE/glwu.glwu.t00z.nc \
	$COMINglwu/glwu.$VDATE/glwu.glwu.t00z.nc \
	$DATA/masks/ice_mask.nc \
	-type data -mask_field 'name="ice_coverage"; level="(0,*,*)";' -thresh lt0.15 -name ice_mask
	export err=$?; err_chk
	if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/masks/ice_mask.nc ]; then
			cp $DATA/masks/ice_mask.nc $ARCmodel/
		fi
	fi
fi

# Lake Champlain:
#gen_vx_mask \
# create subregions using ice mask
#   Other lakes
#gen_vx_mask \
#$DATA/masks/ice_mask_lc.nc \
#$DATA/masks/ice_mask.nc \
#$DATA/masks/mask.nc \
#-type lat -thresh 'ge-80 && le90' -intersection -name LC

#if [ $SENDCOM = "YES" ]; then
# cp $DATA/masks/mask.nc $ARCmodel
#fi

#   Other lakes:
if [ -s $ARCmodel/ice_mask.nc ]; then
	gen_vx_mask \
	$DATA/masks/ice_mask.nc \
	$DATA/masks/ice_mask.nc \
	$DATA/masks/greatlakes.lat.nc \
	-type lat -thresh 'ge40.8 && le49' -intersection
	export err=$?; err_chk
	if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/masks/greatlakes.lat.nc ]; then
 			cp $DATA/masks/greatlakes.lat.nc $ARCmodel
		fi
	fi
fi
if [ -s $ARCmodel/greatlakes.lat.nc ]; then
	gen_vx_mask \
	$DATA/masks/greatlakes.lat.nc \
	$DATA/masks/greatlakes.lat.nc \
	$DATA/masks/mask.greatlakes.nc \
	-type lon -thresh 'ge-93 && le-75' -intersection -name GL
	export err=$?; err_chk

	if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/masks/mask.greatlakes.nc ]; then
			cp $DATA/masks/greatlakes.nc $ARCmodel
		fi
	fi
fi

################################ END OF SCRIPT ################################
