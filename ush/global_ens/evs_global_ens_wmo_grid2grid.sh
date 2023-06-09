#!/bin/ksh

# Script: evs_global_ens_wmo_grid2grid.sh
# Purpose: run Global ensembles (GEFS, CMCE  grid2grid verification for WMO  
# Input parameters:
#   (1) model_list: either gefs or cmce  or all
#   (2) verify_list:  upper 
# Execution steps:
#   (1) Set/export environment parameters for METplus conf files and put them into  procedure files 
#   (2) Set running conf files and put them into  procedure files           
#   (3) Put all MPI procedure files into one MPI script file run_all_gens_g2g_poe.sh
#   (4) If $run_mpi is yes, run the MPI script  in paraalel
#        otherwise run the MPI script in sequence
#
# Author: Binbin Zhou, Lynker
# Update log: 9/4/2022, beginning version  
#

set -x 



###########################################################
#export global parameters unified for all mpi sub-tasks
############################################################
export regrid='OBS'

############################################################

>run_all_gens_g2g_poe.sh

model_list=$1
verify_list=$2

tail='/wmo'
prefix=${COMIN%%$tail*}
index=${#prefix}
echo $index
export COM_IN=${COMIN:0:$index}

if [ $model_list = gefs ] ; then
  $USHevs/global_ens/evs_gens_atmos_check_input_files.sh wmo_gefs
  $USHevs/global_ens/evs_gens_atmos_check_input_files.sh wmo_gfsanl
elif [ $model_list = cmce ] ; then
  $USHevs/global_ens/evs_gens_atmos_check_input_files.sh wmo_cmce
  $USHevs/global_ens/evs_gens_atmos_check_input_files.sh wmo_cmcanl
fi

models=$model_list

if [ $verify_list = all ] ; then
  verifys="upper precip" 
else
  verifys=$verify_list
fi 

for  verify in $verifys ; do  

 if [ $verify = upper ] ; then 

    for modnam in $models ; do 

      MODL=`echo $modnam | tr '[a-z]' '[A-Z]'`

      if [ $modnam = gefs ] ; then
        anl=gfsanl
        mbrs=30
      elif [ $modnam = cmce ] ; then
        anl=cmcanl
        mbrs=20
      else
        echo "wrong model: $modnam"
      fi 

      cycs="00"

      for cyc in ${cycs} ; do

       for fhr in fhr1 ; do

        >run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

            echo  "export output_base=${WORK}/grid2grid/run_${modnam}_valid_at_t${cyc}z_${fhr}" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        echo  "export OBTYPE=GDAS" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export maskpath=$maskpath" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        echo  "export gdashead=$anl" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export gdasgrid=deg1.5" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export gdaspath=$COM_IN" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export modelgrid=grid3.f" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export model=$modnam"  >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export MODEL=$MODL" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export modelhead=$modnam" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export modelpath=$COM_IN" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        echo  "export vbeg=$cyc" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export vend=$cyc" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export valid_increment=21600" >>  run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        echo  "export lead='24, 48, 72, 96, 120, 144, 168, 192, 216, 240, 264, 288, 312, 336, 360, 384' "  >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
 

        echo  "export modeltail='.grib2'" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
 
        echo  "export extradir='atmos/'" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export climpath=$CLIMO/era5" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export members=$mbrs" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GenEnsProd_fcstGEFS_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/EnsembleStat_fcstGEFS_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstGEFS_obsModelAnalysis_climoERA5_mean.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh


        echo "cp \$output_base/stat/${modnam}/*.stat $COMOUTsmall" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        chmod +x run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        echo "run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh" >> run_all_gens_g2g_poe.sh


      done #end of fhr 

     done #end of cycle

   done #end if modnam 

   chmod 775 run_all_gens_g2g_poe.sh

 fi #end of if verify=upper  

done # end of verify  



if [ -s run_all_gens_g2g_poe.sh ] ; then
   run_all_gens_g2g_poe.sh	 
fi


if [ $gather = yes ] ; then

  $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME grid2grid 00 00 

fi
 
 
