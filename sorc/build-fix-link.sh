#!/bin/sh

# generate the symbolic link for $HOMEevs/fix
# HOMEevs=$PACKAGEROOT/evs.v1.0.0
# usage: ./build-fix-link.sh

EVS_fix=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix

if [ ! -L ../fix ]; then
  echo "creating symbolic link for FIXevs ..."
  [ -d $EVS_fix ] && ln -s ${EVS_fix} ../fix || echo "$EVS_fix does not exist"
  echo "created"
  ls -l ../fix
else
  echo "symbolic link for FIXevs previously created"
  ls -l ../fix
fi
