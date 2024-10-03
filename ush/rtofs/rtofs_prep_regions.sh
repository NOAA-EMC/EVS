#!/bin/bash
###############################################################################
# Name of Script: rtofs_regions.sh
# Purpose of Script: To create RTOFS subregions with ice mask for calculating
#    performance metrics.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
#         Mallory Row (mallory.row@noaa.gov)
###############################################################################

set -x

# create ice mask: ice grids are defined as grids with ice coverage >= 0.15
#     from RTOFS nowcast (i.e., f000 forecast)
# use non-ice grids to calculate stats
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/rtofs_glo_2ds_f000_ice.$OBTYPE.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/rtofs_glo_2ds_f000_ice.$OBTYPE.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/rtofs_glo_2ds_f000_ice.$OBTYPE.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        -type data -mask_field 'name="ice_coverage"; level="(0,*,*)";' -thresh lt0.15 -name ice_mask
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/ice_mask.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/ice_mask.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi

# create subregions using ice mask
#   Global
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/mask.global.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/mask.global.nc \
        -type lat -thresh 'ge-80 && le90' -intersection -name GLB
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/mask.global.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/mask.global.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi

#   North Atlantic Ocean
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/north_atlantic.lat.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/north_atlantic.lat.nc \
        -type lat -thresh 'ge0 && le60' -intersection
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/north_atlantic.lat.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/north_atlantic.lat.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/mask.north_atlantic.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/north_atlantic.lat.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/north_atlantic.lat.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/north_atlantic.lat.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/mask.north_atlantic.nc \
        -type lon -thresh 'ge-98 && le10' -intersection -name NATL
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/mask.north_atlantic.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/mask.north_atlantic.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi

#   South Atlantic Ocean
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/south_atlantic.lat.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/south_atlantic.lat.nc \
        -type lat -thresh 'ge-80 && le0' -intersection
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/south_atlantic.lat.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/south_atlantic.lat.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/mask.south_atlantic.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/south_atlantic.lat.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/south_atlantic.lat.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/south_atlantic.lat.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/mask.south_atlantic.nc \
        -type lon -thresh 'ge-70 && le20' -intersection -name SATL
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/mask.south_atlantic.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/mask.south_atlantic.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi

#   Equatorial Atlantic Ocean
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/equatorial_atlantic.lat.nc ]; then
     if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc ]; then
         gen_vx_mask \
         $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
         $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
         $DATA/rtofs.$INITDATE/$OBTYPE/equatorial_atlantic.lat.nc \
         -type lat -thresh 'ge-30 && le30' -intersection
         export err=$?; err_chk
         if [ $SENDCOM = "YES" ]; then
		 if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/equatorial_atlantic.lat.nc ]; then
             		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/equatorial_atlantic.lat.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		 fi
         fi
    fi
fi
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/mask.equatorial_atlantic.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/equatorial_atlantic.lat.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/equatorial_atlantic.lat.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/equatorial_atlantic.lat.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/mask.equatorial_atlantic.nc \
        -type lon -thresh 'ge-80 && le30' -intersection -name EQATL
        export err=$?; err_chk
         if [ $SENDCOM = "YES" ]; then
		 if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/mask.equatorial_atlantic.nc ]; then
             		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/mask.equatorial_atlantic.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		 fi
         fi
    fi
fi

#   North Pacific Ocean
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/north_pacific.lat.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/north_pacific.lat.nc \
        -type lat -thresh 'ge0 && le70' -intersection
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/north_pacific.lat.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/north_pacific.lat.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/northeast_pacific.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/north_pacific.lat.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/north_pacific.lat.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/north_pacific.lat.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/northeast_pacific.nc \
        -type lon -thresh 'ge-180 && le-84' -intersection -name NEPAC
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/northeast_pacific.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/northeast_pacific.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/northwest_pacific.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/north_pacific.lat.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/north_pacific.lat.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/north_pacific.lat.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/northwest_pacific.nc \
        -type lon -thresh 'ge101 && le180' -intersection -name NWPAC
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/northwest_pacific.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/northwest_pacific.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/mask.north_pacific.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/northeast_pacific.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/northeast_pacific.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/northwest_pacific.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/mask.north_pacific.nc \
        -type data -mask_field 'name="NWPAC"; level="(*,*)";' -thresh eq1 -union -name NPAC
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/mask.north_pacific.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/mask.north_pacific.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi

#   South Pacific Ocean
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/south_pacific.lat.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/south_pacific.lat.nc \
        -type lat -thresh 'ge-80 && le0' -intersection
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/south_pacific.lat.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/south_pacific.lat.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/southeast_pacific.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/south_pacific.lat.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/south_pacific.lat.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/south_pacific.lat.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/southeast_pacific.nc \
        -type lon -thresh 'ge-180 && le-70' -intersection -name SEPAC
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/southeast_pacific.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/southeast_pacific.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/southwest_pacific.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/south_pacific.lat.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/south_pacific.lat.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/south_pacific.lat.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/southwest_pacific.nc \
        -type lon -thresh 'ge115 && le180' -intersection -name SWPAC
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/southwest_pacific.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/southwest_pacific.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
   fi
fi
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/mask.south_pacific.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/southeast_pacific.nc ] && [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/southwest_pacific.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/southeast_pacific.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/southwest_pacific.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/mask.south_pacific.nc \
        -type data -mask_field 'name="SWPAC"; level="(*,*)";' -thresh eq1 -union -name SPAC
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/mask.south_pacific.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/mask.south_pacific.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
   fi
fi

#   Equatorial Pacific Ocean
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/equatorial_pacific.lat.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/equatorial_pacific.lat.nc \
        -type lat -thresh 'ge-30 && le30' -intersection
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/equatorial_pacific.lat.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/equatorial_pacific.lat.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/centraleast_pacific.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/equatorial_pacific.lat.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/equatorial_pacific.lat.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/equatorial_pacific.lat.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/centraleast_pacific.nc \
        -type lon -thresh 'ge-180 && le-80' -intersection -name CEPAC
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/centraleast_pacific.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/centraleast_pacific.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/centralwest_pacific.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/equatorial_pacific.lat.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/equatorial_pacific.lat.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/equatorial_pacific.lat.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/centralwest_pacific.nc \
        -type lon -thresh 'ge115 && le180' -intersection -name CWPAC
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/centralwest_pacific.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/centralwest_pacific.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/mask.equatorial_pacific.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/centraleast_pacific.nc ] && [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/centralwest_pacific.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/centraleast_pacific.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/centralwest_pacific.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/mask.equatorial_pacific.nc \
        -type data -mask_field 'name="CWPAC"; level="(*,*)";' -thresh eq1 -union -name EQPAC
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/mask.equatorial_pacific.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/mask.equatorial_pacific.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi

#   Indian Ocean
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/indian.lat.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/indian.lat.nc \
        -type lat -thresh 'ge-75 && le30' -intersection
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/indian.lat.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/indian.lat.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/mask.indian.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/indian.lat.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/indian.lat.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/indian.lat.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/mask.indian.nc \
        -type lon -thresh 'ge20 && le115' -intersection -name IND
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/mask.indian.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/mask.indian.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi

#   Southern Ocean
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/mask.southern.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/mask.southern.nc \
        -type lat -thresh 'ge-80 && le-30' -intersection -name SOC
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/mask.southern.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/mask.southern.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi

#   Arctic Ocean
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/mask.arctic.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/mask.arctic.nc \
        -type lat -thresh 'ge50 && le90' -intersection -name Arctic
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/mask.arctic.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/mask.arctic.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi

#   Mediterranean Sea
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/mediterranean.lat.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/ice_mask.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/mediterranean.lat.nc \
        -type lat -thresh 'ge29 && le48' -intersection
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/mediterranean.lat.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/mediterranean.lat.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi
if [ ! -s $COMOUTprep/rtofs.$INITDATE/$OBTYPE/mask.mediterranean.nc ]; then
    if [ -s $EVSINprep/rtofs.$INITDATE/$OBTYPE/mediterranean.lat.nc ]; then
        gen_vx_mask \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/mediterranean.lat.nc \
        $EVSINprep/rtofs.$INITDATE/$OBTYPE/mediterranean.lat.nc \
        $DATA/rtofs.$INITDATE/$OBTYPE/mask.mediterranean.nc \
        -type lon -thresh 'ge-2 && le45' -intersection -name MEDIT
        export err=$?; err_chk
        if [ $SENDCOM = "YES" ]; then
		if [ -s $DATA/rtofs.$INITDATE/$OBTYPE/mask.mediterranean.nc ]; then
            		cp -v $DATA/rtofs.$INITDATE/$OBTYPE/mask.mediterranean.nc $COMOUTprep/rtofs.$INITDATE/$OBTYPE
		fi
        fi
    fi
fi

################################ END OF SCRIPT ################################
