#!/bin/ksh

# Script: evs_global_ens_snow_ice.sh
# Purpose: run Global ensembles (GEFS, CMCE, EC and NAES)  snow and sea ice verification for upper fields 
#            end 24hr APCP by setting several METPlus environment variables and running METplus conf files 
# Input parameters:
#   (1) model_list: either gefs or cmce or ecme or naefs or all
#   (2) verify_list: either upper or precip or all
# Execution steps:
#   Both upper and precip have similar steps:
#   (1) Set/export environment parameters for METplus conf files and put them into  procedure files 
#   (2) Set running conf files and put them into  procedure files           
#   (3) Put all MPI procedure files into one MPI script file run_all_gens_snowfall_poe.sh
#   (4) If $run_mpi is yes, run the MPI script  in paraalel
#        otherwise run the MPI script in sequence
# Note: total number of parallels = grid2grid (models x cycles) + precip (models)
#   The maximum (4 models) = 4 + 2 + 2 + 2 + 4 = 14,  in this case 14 nodes should be set in its ecf,   
#
# Author: Binbin Zhou, IMSG
# Update log: 2/4/2022, beginning version  
#

set -x 



###########################################################
#export global parameters unified for all mpi sub-tasks
############################################################
export regrid='NONE'

############################################################

>run_all_gens_snowfall_poe.sh

modnam=$1
verify=$2

$USHevs/global_ens/evs_gens_atmos_check_input_files.sh nohrsc
$USHevs/global_ens/evs_gens_atmos_check_input_files.sh $modnam

tail='/atmos'
prefix=${COMIN%%$tail*}
index=${#prefix}
echo $index
COM_IN=${COMIN:0:$index}
echo $COM_IN


anl=nohrsc
cyc='12'

if [ $verify = snowfall ] ; then 

      MODL=`echo $modnam | tr '[a-z]' '[A-Z]'`

      if [ $modnam = gefs ] ; then
        mbrs=30
	types='WEASD SNOD'
      elif [ $modnam = cmce ] ; then
        mbrs=20
	types='WEASD SNOD'
      elif [ $modnam = ecme ] ; then
        mbrs=50
	types='weasd'
      else
        echo "wrong model: $modnam"
      fi 

      for type in $types ; do

        >run_${modnam}_${verify}_${type}.sh

        echo  "export output_base=${WORK}/${verify}/run_${modnam}_${verify}_${type}" >> run_${modnam}_${verify}_${type}.sh

	echo  "export type=$type" >> run_${modnam}_${verify}_${type}.sh
        echo  "export modelpath=$COM_IN" >> run_${modnam}_${verify}_${type}.sh

        echo  "export OBTYPE=NOHSRC" >> run_${modnam}_${verify}_${type}.sh
        echo  "export maskpath=$maskpath" >> run_${modnam}_${verify}_${type}.sh

        echo  "export obsvhead=$anl" >> run_${modnam}_${verify}_${type}.sh
        echo  "export obsvgrid=grid184" >> run_${modnam}_${verify}_${type}.sh
        echo  "export obsvpath=$COM_IN" >> run_${modnam}_${verify}_${type}.sh
 
 	
	if [ ${modnam} = ecme ] ; then
		echo  "export modelgrid=grid4.weasd_24h.f" >> run_${modnam}_${verify}_${type}.sh
	else	
                echo  "export modelgrid=grid3.${type}_24h.f" >> run_${modnam}_${verify}_${type}.sh
	fi
        echo  "export model=$modnam"  >> run_${modnam}_${verify}_${type}.sh
        echo  "export MODEL=$MODL" >> run_${modnam}_${verify}_${type}.sh
        echo  "export modelhead=$modnam" >> run_${modnam}_${verify}_${type}.sh

        echo  "export vbeg=$cyc" >> run_${modnam}_${verify}_${type}.sh
        echo  "export vend=$cyc" >> run_${modnam}_${verify}_${type}.sh
        echo  "export valid_increment=21600" >>  run_${modnam}_${verify}_${type}.sh


         if [ $modnam = cmce ] || [ $modnam = gefs ] ; then
	  if [ $type = WEASD ] ; then
	    echo "export options='censor_thresh = lt0; censor_val = 0; set_attr_units = \"m\"; convert(x) = x * 0.01' " >> run_${modnam}_${verify}_${type}.sh
          elif [ $type = SNOD ] ; then
            echo "export options='censor_thresh = lt0; censor_val = 0 ' " >> run_${modnam}_${verify}_${type}.sh
	  fi

	  echo  "export lead='12, 24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384' "  >> run_${modnam}_${verify}_${type}.sh
 
         elif [  $modnam = ecme ] ; then
          echo  "export lead='12, 24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360' "  >> run_${modnam}_${verify}_${type}.sh
        fi

        echo  "export modeltail='.nc'" >> run_${modnam}_${verify}_${type}.sh
        echo  "export members=$mbrs" >> run_${modnam}_${verify}_${type}.sh


        if [ $modnam = ecme ] ; then

         echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GenEnsProd_fcstECME_obsNOHRSC24h.conf " >> run_${modnam}_${verify}_${type}.sh  
         echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/EnsembleStat_fcstECME_obsNOHRSC24h.conf " >> run_${modnam}_${verify}_${type}.sh  
 	 echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstECME_obsNOHRSC24h_mean.conf " >> run_${modnam}_${verify}_${type}.sh   
  	 echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstECME_obsNOHRSC24h_prob.conf " >> run_${modnam}_${verify}_${type}.sh

        elif [ $modnam = gefs ] || [ $modnam = cmce ] ; then

          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GenEnsProd_fcstGEFS_obsNOHRSC24h.conf " >> run_${modnam}_${verify}_${type}.sh

	  echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/EnsembleStat_fcstGEFS_obsNOHRSC24h.conf " >> run_${modnam}_${verify}_${type}.sh
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstGEFS_obsNOHRSC24h_mean.conf " >> run_${modnam}_${verify}_${type}.sh
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstGEFS_obsNOHRSC24h_prob.conf " >> run_${modnam}_${verify}_${type}.sh

        else

          echo "wrong model"
        exit

        fi

        [[ $SENDCOM="YES" ]] && echo "cp \$output_base/stat/${modnam}/*.stat $COMOUTsmall" >> run_${modnam}_${verify}_${type}.sh

        chmod +x run_${modnam}_${verify}_${type}.sh

        echo "${DATA}/run_${modnam}_${verify}_${type}.sh" >> run_all_gens_snowfall_poe.sh

   done

   chmod 775 run_all_gens_snowfall_poe.sh

fi #end of if verify=snowfall  




if [ -s run_all_gens_snowfall_poe.sh ] ; then
    ${DATA}/run_all_gens_snowfall_poe.sh	 
fi


if [ $gather = yes ] ; then

  $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME $verify 12 12 

fi
 
 
