#!/bin/bash

# checkpoint function  usage:  checkpoint $? Name
function checkpoint {
  if (( $1 == 0 )); then
    echo "$2 $3 OK"
  else
    echo "$2 $3 FAILED, RC=$1"
  fi
}

#                                           
# push the plot files from wcoss to emcrzdm 
#                                           

model=${1:-'global_det'}
modelID=${2:-'gfs'}

plotDir='/path/to/EVS_stats/evs/v1.0/plots/'
rzdmUser='dspindler@emcrzdm.ncep.noaa.gov'
rzdmDir="/path/to/verification/global/${modelID}/wave/para/grid2obs/images"

SSH=/usr/bin/ssh
SCP=/usr/bin/scp

theDate=$(date --date="yesterday" +"%Y%m%d")
#theDate='20230129'
echo "Transfering EVS plots for ${model} ${theDate}"

$SCP ${plotDir}/${model}/${modelID}.${theDate}/*tar ${rzdmUser}:${rzdmDir}/.
UTAR_31="cd ${rzdmDir}; tar -xf evs.plots.${model}.wave.grid2obs.last31days.v${theDate}.tar"
UTAR_90="cd ${rzdmDir}; tar -xf evs.plots.${model}.wave.grid2obs.last90days.v${theDate}.tar"
RM_tar="rm -f ${rzdmDir}/evs.plots.${model}.*.tar"

$SSH ${rzdmUser} ${UTAR_31}
OK=$?
if [ "$OK" != '0' ]
then
  echo ' '
  echo ' ********************************************** '
  echo ' ***   Error untarring 31 day file on RZDM  *** '
  echo ' ********************************************** '
else
  echo ' last31days file untarred'
fi

$SSH ${rzdmUser} ${UTAR_90}
OK=$?
if [ "$OK" != '0' ]
then
  echo ' '
  echo ' ********************************************** '
  echo ' ***   Error untarring 90 day file on RZDM  *** '
  echo ' ********************************************** '
else
  echo ' last90days file untarred'
fi

$SSH ${rzdmUser} ${RM_tar}
OK=$?
if [ "$OK" != '0' ]
then
  echo ' '
  echo ' ********************************************** '
  echo ' ***   Error removing tar files on RZDM     *** '
  echo ' ********************************************** '
else
  echo ' Tar files removed'
fi

