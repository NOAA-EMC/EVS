#!/bin/sh

SORCevs_gens=`pwd`

source ../modulefiles/v1.0

source ../versions/build.ver

set -x

#SORCevs_gefs=`pwd`

cd $SORCevs_gens/evs_sref_adjust_precip24_time.fd
make precip

#compile product generator sorc
cd $SORCevs_gens/evs_global_ens_adjust_CMCE_NAEFS.fd
make cmce

echo "All sorc codes are compiled"  
exit 
