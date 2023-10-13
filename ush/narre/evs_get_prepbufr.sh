#!/bin/ksh

set -x 

modnam=$1



if [ $modnam = prepbufr ] ; then

 mkdir -p $WORK/prepbufr.$VDATE
 export output_base=${WORK}/pb2nc

 if [ -s $COMINobsproc/rap.${VDATE}/rap.t00z.prepbufr.tm00 ] ; then 
  for grid in G130 G242 ; do
   #for cyc in 00 01 02 03 04 05 06 07 08  09 10 11 12 13 14 15 16 17 18 19 20  21 22 23  ; do
   for cyc in 00  03  06  09  12  15  18   21  ; do
     export vbeg=${cyc}
     export vend=${cyc}
     export verif_grid=$grid

     ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr.conf
     cp ${WORK}/pb2nc/prepbufr_nc/*.nc $WORK/prepbufr.${VDATE}
  
   done
  done
 else 
  if [ $SENDMAIL = YES ] ; then
   export subject="Prepbufr Data Missing for EVS ${COMPONENT}"
   echo "Warning:  No Prepbufr data available for ${VDATE}" > mailmsg
   echo Missing file is $COMINobsproc/rap.${VDATE}/rap.t??z.prepbufr.tm00  >> mailmsg
   echo "Job ID: $jobid" >> mailmsg
   cat mailmsg | mail -s "$subject" $maillist  
   exit
  fi
 fi

fi

