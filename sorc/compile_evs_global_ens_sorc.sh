#!/bin/sh

SORCevs_gens=`pwd`

source ../versions/build.ver

source ../modulefiles/v1.0

set -x

SORCevs_gefs=`pwd`


#compile product generator sorc
cd $SORCevs_gens/evs_global_ens_adjust_CMCE_NAEFS.fd
make cmce

echo "All sorc codes are compiled"  
exit 
