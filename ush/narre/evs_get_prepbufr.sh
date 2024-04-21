#!/bin/ksh
#**************************************************************************
#  Purpose: Get required input forecast and validation data files
#           for narre stat jobs
#  Last update:  3/26/2024, add restart capability, by Binbin Zhou Lynker@EMC/NCEP
#                10/27/2023, by Binbin Zhou Lynker@EMC/NCEP
#************************************************************************
#
set -x 

modnam=$1



if [ $modnam = prepbufr ] ; then

 mkdir -p $WORK/prepbufr.$VDATE
 export output_base=${WORK}/pb2nc

 for vhr in 00  03  06  09  12  15  18   21  ; do
  if [ -s $COMINobsproc/rap.${VDATE}/rap.t${vhr}z.prepbufr.tm00 ] ; then 
   for grid in G130 G242 ; do
     export vbeg=${vhr}
     export vend=${vhr}
     export verif_grid=$grid
     ${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/Pb2nc_obsRAP_Prepbufr.conf
     export err=$?; err_chk
     cp ${WORK}/pb2nc/prepbufr_nc/*.nc $WORK/prepbufr.${VDATE}
     echo "Pb2nc_obsRAP_Prepbufr  Metplus log file start:"
     cat $output_base/logs/*
     echo "Pb2nc_obsRAP_Prepbufr  Metplus log file End:"
   done
  else 
    echo "WARNING:  No Prepbufr data available $COMINobsproc/rap.${VDATE}/rap.t${vhr}z.prepbufr.tm00 for ${VDATE}"
    if [ $SENDMAIL = YES ] ; then
     export subject="Prepbufr Data Missing for EVS ${COMPONENT}"
     echo "Warning:  No Prepbufr data available for ${VDATE}" > mailmsg
     echo Missing file is $COMINobsproc/rap.${VDATE}/rap.t${vhr}z.prepbufr.tm00  >> mailmsg
     echo "Job ID: $jobid" >> mailmsg
     cat mailmsg | mail -s "$subject" $MAILTO  
     exit
    fi
  fi
 done
 #Save for restart
  if [ -d $WORK/prepbufr.${VDATE} ] ; then
      cp -r $WORK/prepbufr.${VDATE}  $COMOUTsmall
  fi
 

fi

