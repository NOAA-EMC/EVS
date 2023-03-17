#!/bin/ksh

set -x 

modnam=$1



if [ $modnam = prepbufr ] ; then

 mkdir -p $WORK/prepbufr.$VDATE
 export output_base=${WORK}/pb2nc

 for grid in G130 G214 ; do

  for cyc in 00 01 02 03 04 05 06 07 08  09 10 11 12 13 14 15 16 17 18 19 20  21 22 23  ; do

     export vbeg=${cyc}
     export vend=${cyc}
     export verif_grid=$grid

     ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr.cong
     cp ${WORK}/pb2nc/prepbufr_nc/*.nc $WORK/prepbufr.${VDATE}
  
  done

  done

fi

