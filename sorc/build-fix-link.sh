#!/bin/sh

# generate the symbolic link for $HOMEevs/fix
# HOMEevs=$PACKAGEROOT/evs.v1.0.0
# usage: ./build-fix-link.sh

EVS_fix=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix

rm -rf ../fix
mkdir -p ../fix
[ -d $EVS_fix ] && ln -s ${EVS_fix}/* ../fix/ || echo "$EVS_fix does not exist"
