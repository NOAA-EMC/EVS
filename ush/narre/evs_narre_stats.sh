#!/bin/ksh
set -x 
#**************************************************************************
#  Purpose: To run the METplus-based stat generation jobs
#  Last update: 3/26/2024, Add restart capability, by Binbin Zhou Lynker@EMC/NCEP
#               10/27/2023, by Binbin Zhou Lynker@EMC/NCEP
#************************************************************************
#


export regrid='NONE'
export vday=$VDATE

echo COMOUTsmall=$COMOUTsmall

#**********************************************
# Build POE script to collect sub-jobs
# *********************************************
>run_all_narre_poe.sh


#************************************************************
#Get prepbufr data
# 1. First check if has prepbugr data saved from previous run 
# 2. if yes, then copy them for restart
#    otherwise run evs_get_prepbufr.sh
#************************************************************
if [ ! -d $COMOUTsmall/prepbufr.${VDATE} ] ; then 
 $USHevs/narre/evs_get_prepbufr.sh prepbufr
 export err=$?; err_chk
else
 #Restart: copy saved stat files from previous runs
 cp -r $COMOUTsmall/prepbufr.${VDATE} $WORK/.
fi
 
obsv='prepbufr'

#******************************************************************
# Check if all stats sub-tasks are completed in the previous runs
if [ ! -s $COMOUTsmall/stats_completed ] ; then
#*****************************************************************

#######for prod in mean prob sclr ; do
for prod in mean  ; do

 export model=narre${prod}
 export PROD='MEAN'

 for dom in CONUS Alaska ; do

  for range in range1 range2 range3 range4 ; do 

     #************************************************************
     # setup sub-jobs and all required environment for METplus run
     # *********************************************************** 
     >run_narre_${model}.${dom}.${range}.sh

      #Check for restart: check if the single sub-job is completed in the previous run
      #If this job has been completed in the previous run, then skip it
      if [ ! -e $COMOUTsmall/run_narre_${model}.${dom}.${range}.completed ] ; then

       echo  "#!/bin/ksh">>run_narre_${model}.${dom}.${range}.sh
       echo  "export range=$range" >> run_narre_${model}.${dom}.${range}.sh

       echo  "export output_base=$WORK/grid2obs/${model}.${dom}.${range}" >> run_narre_${model}.${dom}.${range}.sh 

       echo  "export domain=$dom" >> run_narre_${model}.${dom}.${range}.sh

       if [ $dom = CONUS ] ; then
         echo  "export verif_grid='G130'" >> run_narre_${model}.${dom}.${range}.sh
         echo  "export obsvgrid='G130'" >> run_narre_${model}.${dom}.${range}.sh         

         if [ $prod = sclr ] ; then
            echo  "export modelgrid=prob.grd130" >> run_narre_${model}.${dom}.${range}.sh
         else
            echo  "export modelgrid=${prod}.grd130" >> run_narre_${model}.${dom}.${range}.sh
         fi

       elif [ $dom = Alaska ] ; then
         echo  "export verif_grid='G242'" >> run_narre_${model}.${dom}.${range}.sh 
         echo  "export obsvgrid='G242'" >> run_narre_${model}.${dom}.${range}.sh

         if [ $prod = sclr ] ; then
            echo  "export modelgrid=prob.grd242" >> run_narre_${model}.${dom}.${range}.sh
         else
            echo  "export modelgrid=${prod}.grd242" >> run_narre_${model}.${dom}.${range}.sh
         fi
      
       else
         exit
       fi          

       echo  "export obsvhead=$obsv" >> run_narre_${model}.${dom}.${range}.sh
       echo  "export obsvpath=$WORK" >> run_narre_${model}.${dom}.${range}.sh

       if [ $range = range1 ] ; then
         echo  "export vbeg=0" >>run_narre_${model}.${dom}.${range}.sh
         echo  "export vend=5" >>run_narre_${model}.${dom}.${range}.sh
       elif [ $range = range2 ] ; then
         echo  "export vbeg=6" >>run_narre_${model}.${dom}.${range}.sh
         echo  "export vend=11" >>run_narre_${model}.${dom}.${range}.sh
       elif [ $range = range3 ] ; then
         echo  "export vbeg=12" >>run_narre_${model}.${dom}.${range}.sh
         echo  "export vend=17" >>run_narre_${model}.${dom}.${range}.sh
       elif [ $range = range4 ] ; then
         echo  "export vbeg=18" >>run_narre_${model}.${dom}.${range}.sh
         echo  "export vend=23" >>run_narre_${model}.${dom}.${range}.sh
       else
         echo "Wrong range"
         exit
       fi 
  
       echo  "export valid_increment=3600" >> run_narre_${model}.${dom}.${range}.sh
       echo  "export lead='01,02,03,04,05,06,07,08,09,10,11,12'" >> run_narre_${model}.${dom}.${range}.sh

       echo  "export model=$model"  >> run_narre_${model}.${dom}.${range}.sh
       echo  "export MODEL=NARRE_${PROD}" >> run_narre_${model}.${dom}.${range}.sh
       echo  "export regrid=NONE" >> run_narre_${model}.${dom}.${range}.sh
       echo  "export modelhead=$model" >> run_narre_${model}.${dom}.${range}.sh
       echo  "export modelpath=$COMINnarre" >> run_narre_${model}.${dom}.${range}.sh
       echo  "export modeltail='.grib2'" >> run_narre_${model}.${dom}.${range}.sh
       echo  "export extradir='ensprod/'" >> run_narre_${model}.${dom}.${range}.sh

       echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstNARRE_obsPREPBUFR_SFC_mean.conf " >> run_narre_${model}.${dom}.${range}.sh
       echo  "echo Start:  stat metplus log files for ${model}.${dom}.${range}" >> run_narre_${model}.${dom}.${range}.sh
       echo  "cat \$output_base/logs/* " >> run_narre_${model}.${dom}.${range}.sh
       echo  "echo End: stat metplus log files for ${model}.${dom}.${range}" >> run_narre_${model}.${dom}.${range}.sh

       echo "if [ -s \$output_base/stat/*.stat ] ; then " >> run_narre_${model}.${dom}.${range}.sh
       echo " cp \$output_base/stat/*.stat $COMOUTsmall" >> run_narre_${model}.${dom}.${range}.sh
       echo "fi" >> run_narre_${model}.${dom}.${range}.sh 

       #indicate sub-task is completed for restart 
       echo ">$COMOUTsmall/run_narre_${model}.${dom}.${range}.completed" >> run_narre_${model}.${dom}.${range}.sh

       chmod +x run_narre_${model}.${dom}.${range}.sh
       echo "${DATA}/run_narre_${model}.${dom}.${range}.sh" >> run_all_narre_poe.sh

      fi # check restart for sub-task

   done #end of range loop

  done #end of dom loop

done #end of prod loop

#****************************************************************************
# Run the POE script in MPI or in Sequence order to generate small stat files
# ***************************************************************************
chmod 775 run_all_narre_poe.sh
if [ $run_mpi = yes ] ; then
  mpiexec  -n 8 -ppn 8 --cpu-bind core --depth=2 cfp  ${DATA}/run_all_narre_poe.sh
  export err=$?; err_chk
else
   ${DATA}/run_all_narre_poe.sh
   export err=$?; err_chk
fi

>COMOUTsmall/stats_completed
echo "stats are completed" >> COMOUTsmall/stats_completed

fi # check restart for all tasks



#*****************************************************
# Combine small stat files to a big stat file (final)
#****************************************************
if [ $gather = yes ] && [ -s $COMOUTsmall/*.stat ] ; then
  $USHevs/narre/evs_narre_gather.sh
  export err=$?; err_chk
fi
