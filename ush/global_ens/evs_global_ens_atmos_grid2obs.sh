#!/bin/ksh
set -x 

#Binbin note: If METPLUS_BASE,  PARM_BASE not set, then they will be set to $METPLUS_PATH
#             by config_launcher.py in METplus-3.0/ush
#             why config_launcher.py is not in METplus-3.1/ush ??? 


###########################################################
#export global parameters unified for all mpi sub-tasks
############################################################
export regrid='NONE'
############################################################


model_list=$1

models=$model_list

if [ $model_list = naefs ] ; then
  $USHevs/global_ens/evs_gens_atmos_check_input_files.sh gefs
  $USHevs/global_ens/evs_gens_atmos_check_input_files.sh cmce
else
  $USHevs/global_ens/evs_gens_atmos_check_input_files.sh model_list
fi

$USHevs/global_ens/evs_gens_atmos_check_input_files.sh prepbufr
$USHevs/global_ens/evs_gens_atmos_check_input_files.sh prepbufr_profile


>run_all_gens_g2o_poe.sh

tail='/atmos'
prefix=${COMIN%%$tail*}
index=${#prefix}
echo $index
COM_IN=${COMIN:0:$index}
echo $COM_IN



for modnam in $models ; do

   export model=$modnam
   MODNAM=`echo $model | tr '[a-z]' '[A-Z]'`
   if [ $modnam = gefs ] ; then
     mbrs=30
   elif [ $modnam = cmce ] ; then
     mbrs=20
   elif [ $modnam = naefs ] ; then
     $USHevs/global_ens/evs_gens_atmos_g2o_create_naefs.sh 
     if [ $gefs_number = 20 ] ; then
       mbrs=40
     elif [ $gefs_number = 30 ] ; then
       mbrs=50
     fi
   elif [ $modnam = ecme ] ; then
     mbrs=50
   else
     echo "wrong model"
   fi

  if [ $modnam = gefs ] ; then 
   cycles="00 06 12 18"
  else
   cycles="00 12"
  fi 


 for cyc in ${cycles}  ; do

  for field in sfc profile cloud ; do

  if [ $field = profile ] ; then
     fhrs='fhr1 fhr2 fhr3 fhr4'
  elif [ $field = cloud ] ; then
    if [  $modnam = gefs ] ; then	  
      fhrs='fhr30 fhr31 fhr32'
    else
      fhrs='fhr30 fhr31'
    fi
  elif [ $field = sfc ] ; then
    if [ $modnam = gefs ] ; then
      fhrs='fhr21 fhr22 fhr23 fhr24'
    else
      fhrs='fhr30 fhr31'
    fi 
  fi

  for fhr in $fhrs ; do

  >run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh

    echo  "export output_base=$WORK/grid2obs/run_${modnam}_${cyc}_${fhr}_${field}_g2o" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh

    if [ $modnam = naefs ] ; then
      echo  "export modelpath=${WORK}/naefs_g2o" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
    else
      echo  "export modelpath=$COM_IN" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
    fi


    echo  "export prepbufrhead=gfs" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
    echo  "export prepbufrgrid=prepbufr.f00.nc" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
    echo  "export prepbufrpath=$COM_IN" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
    echo  "export model=$modnam"  >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
    if [ $modnam = naefs ] && [ $gefs_number = 30 ] ; then
      echo  "export MODEL=${MODNAM}v7" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
    else
      echo  "export MODEL=${MODNAM}" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
    fi

    echo  "export vbeg=$cyc" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
    echo  "export vend=$cyc" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
    echo  "export valid_increment=100" >>  run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh

    if [ $modnam = gefs ] ; then

       #For profile
       if [ $fhr = fhr1 ] ; then
          echo  "export lead='  6, 12, 18, 24, 30, 36, 42, 48,  54, 60, 66, 72, 78, 84, 90, 96' " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       elif [ $fhr = fhr2 ] ; then
          echo  "export lead='102,108,114,120,126,132,138,144,150,156,162,168,174,180,186,192' " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       elif [ $fhr = fhr3 ] ; then
          echo  "export lead='198,204,210,216,222,228,234,240,246,252,258,264,270,276,282,288' " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       elif [ $fhr = fhr4 ] ; then
          echo  "export lead='294,300,306,312,318,324,330,336,342,348,354,360,366,372,378,384' " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh

       #For Cloud 
       elif [ $fhr = fhr30 ] ; then
           echo  "export lead='  6,  12,  18,  24,  30,  36,  42,  48,  54,  60,  66,  72,  78,  84,  90,  96, 102, 108, 114, 120, 126 '  " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       elif [ $fhr = fhr31 ] ; then
           echo  "export lead='132, 138, 144, 150, 156, 162, 168, 174, 180, 186, 192, 198, 204, 210, 216, 222, 228, 234, 240, 246, 252'  " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       elif [ $fhr = fhr32 ] ; then
	   echo  "export lead='258, 264, 270, 276, 282, 288, 294, 300, 306, 312, 318, 324, 330, 336, 342, 348, 354, 360, 366, 372, 378, 384' " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       #For sfc
       elif [ $fhr = fhr21 ] ; then
           echo  "export lead='6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72,78, 84,90, 96'  " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       elif [ $fhr = fhr22 ] ; then
           echo  "export lead='102, 108,114, 120,126, 132,138, 144,150, 156,162, 168,174, 180,186, 192'  " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       elif [ $fhr = fhr23 ] ; then
           echo  "export lead='198,204,210, 216,222, 228,234, 240,246, 252,258, 264,270, 276,282, 288'  " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       elif [ $fhr = fhr24 ] ; then
           echo  "export lead='294, 300,306, 312,318, 324,330, 336,342, 348,354, 360,366, 372,378, 384'  " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh

       fi

    elif [ $modnam = ecme ] ; then

       echo "ecme fields ..."
       #For Cloud and sfc 
       if [ $fhr = fhr30 ] ; then
            echo  "export lead='12, 24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180' "  >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       elif [ $fhr = fhr31 ] ; then
            echo  "export lead='192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360' "  >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
        


       #For profile
       elif [ $fhr = fhr1 ] ; then
            echo  "export lead=' 12, 24, 36, 48, 60, 72, 84, 96' " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       elif [ $fhr = fhr2 ] ; then
            echo  "export lead='108,120,132,144, 156,168,180,192' " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       elif [ $fhr = fhr3 ] ; then
            echo  "export lead='204,216,228,240,252,264,276,288' " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       elif [ $fhr = fhr4 ] ; then
            echo  "export lead='300,312,324,336,348,360' " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       fi

    else
       echo "cmce and naefs fields ...."

       #For cloud and sfc
       if [ $fhr = fhr30 ] ; then
           echo  "export lead='12, 24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192' "  >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       elif [ $fhr = fhr31 ] ; then
           echo  "export lead='204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384' "  >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh

       #For profile
       elif [ $fhr = fhr1 ] ; then
           echo  "export lead=' 12, 24, 36, 48,  60, 72, 84, 96' " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       elif [ $fhr = fhr2 ] ; then
           echo  "export lead='108,120,132,144,156,168,180,192' " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       elif [ $fhr = fhr3 ] ; then
           echo  "export lead='204,216,228,240,252,264,276,288' " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       elif [ $fhr = fhr4 ] ; then
           echo  "export lead='300,312,324,336,348,360,372,384' " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
       fi

    fi


    echo  "export modelhead=$modnam" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh

    if [ $modnam = ecme ] ; then
     echo  "export modeltail='.grib1'" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
     echo  "export modelgrid=grid4.f" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
    else
     echo  "export modeltail='.grib2'" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
     echo  "export modelgrid=grid3.f" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
    fi 

    echo  "export extradir='atmos/'" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh

    echo  "export climpath=$CLIMO/era5" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
    echo  "export climgrid=grid3" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
    echo  "export climtail='.grib1'" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
    echo  "export members=$mbrs" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh

    if [ $field = cloud ] ; then 

      if [ $modnam = gefs ] || [ $modnam = cmce ] || [ $modnam = ecme ] ; then

        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcst${MODNAM}_obsPREPBUFR_CLOUD.conf " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcst${MODNAM}_obsPREPBUFR_CLOUD.conf " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcst${MODNAM}_obsPREPBUFR_CLOUD_mean.conf " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcst${MODNAM}_obsPREPBUFR_CLOUD_prob.conf " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh

      fi

    elif [ $field = sfc ] ; then

      if [ $modnam = gefs ] || [ $modnam = cmce ] || [ $modnam = ecme ] ; then

        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcst${MODNAM}_obsPREPBUFR_SFC_climoERA5.conf  " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcst${MODNAM}_obsPREPBUFR_SFC_climoERA5.conf  " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcst${MODNAM}_obsPREPBUFR_SFC_mean_climoERA5.conf " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh

       elif [ $modnam = naefs ] ; then

        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstNAEFSbc_obsPREPBUFR_SFC_climoERA5.conf  " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
	echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstNAEFSbc_obsPREPBUFR_SFC_climoERA5.conf  " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
	echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstNAEFSbc_obsPREPBUFR_SFC_mean_climoERA5.conf " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
      
      fi

    elif [ $field = profile ] ; then

      if [ $modnam = gefs ] || [ $modnam = cmce ] || [ $modnam = ecme ] ; then

        echo  "export prepbufrgrid=prepbufr_profile.f00.nc" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcst${MODNAM}_obsPREPBUFR_PROFILE.conf " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
 
      elif [ $modnam = naefs ] ; then

        echo  "export prepbufrgrid=prepbufr_profile.f00.nc" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
	echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/GenEnsProd_fcstNAEFSbc_obsPREPBUFR_UPPER_climoERA5.conf " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
	echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/EnsembleStat_fcstNAEFSbc_obsPREPBUFR_UPPER.conf " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh
        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstNAEFSbc_obsPREPBUFR_UPPER_mean_climoERA5.conf " >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh

      fi

    fi 

   echo  "cp \$output_base/stat/${modnam}/*.stat $COMOUTsmall" >> run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh 

   chmod +x run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh

   echo "${DATA}/run_${modnam}_${cyc}_${fhr}_${field}_g2o.sh" >> run_all_gens_g2o_poe.sh 

  done # end of fhr 

  done #end of field

 done #end of cyc

done #end of model

chmod 775 run_all_gens_g2o_poe.sh

if [ $run_mpi = yes ] ; then
  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH

   if [ ${models} = gefs ] ; then
    mpiexec -n 44 -ppn 44 --cpu-bind verbose,depth cfp ${DATA}/run_all_gens_g2o_poe.sh
   else
    mpiexec -n 20 -ppn 20 --cpu-bind verbose,depth cfp ${DATA}/run_all_gens_g2o_poe.sh
   fi

else
    ${DATA}/run_all_gens_g2o_poe.sh
fi 


if [ $gather = yes ] ; then

   if [ ${models} = gefs ] ; then
     $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME grid2obs 00 18
   else
     $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME grid2obs 00 12
   fi

fi


