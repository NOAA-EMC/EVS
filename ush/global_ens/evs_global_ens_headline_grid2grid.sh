#!/bin/ksh

# For GEFS Headline grid2grid  
# Author: Binbin Zhou, IMSG
# Update log: 9/4/2022, beginning version  
#

set -x 



###########################################################
#export global parameters unified for all mpi sub-tasks
############################################################
export regrid='NONE'

############################################################

model_list=$1
verify_list=$2

if [ $model_list = gefs ] ; then
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh headline_gfsanl
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh headline_gefs
elif  [ $model_list = naefs ] ; then
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh headline_gfsanl
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh headline_cmcanl
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh headline_gefs
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh headline_cmce
elif [ $model_list = gfs ] ; then
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh headline_gfsanl
   $USHevs/global_ens/evs_gens_atmos_check_input_files.sh headline_gfs
fi


tail='/headline'
prefix=${EVSIN%%$tail*}
index=${#prefix}
echo $index
COM_IN=${EVSIN:0:$index}
echo $COM_IN

>run_all_gens_g2g_poe.sh

models=$model_list

verify="upper" 

if [ $verify = upper ] ; then 

    for modnam in $models ; do 

      MODL=`echo $modnam | tr '[a-z]' '[A-Z]'`

      if [ $modnam = gefs ] ; then
        anl=gfsanl
        mbrs=30
      elif [ $modnam = cmce ] ; then
        anl=cmcanl
        mbrs=20
      elif [ $modnam = ecme ] ; then
        anl=ecmanl
        mbrs=50
      elif [ $modnam = naefs ] ; then
        $USHevs/global_ens/evs_gens_atmos_g2g_reset_naefs.sh
        anl=gfsanl
	if [ $gefs_number = 20 ] ; then
	  mbrs=40
        elif [ $gefs_number = 30 ] ; then	  
          mbrs=50
	fi 
      elif [ $modnam = gfs ] ; then 
	anl=gfsanl
	mbrs=1
      else
        echo ":wrong model: $modnam"
      fi 

      cycs="00"

      for cyc in ${cycs} ; do

       for fhr in fhr1 ; do

        >run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

            echo  "export output_base=${WORK}/grid2grid/run_${modnam}_valid_at_t${cyc}z_${fhr}" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        if [ $modnam = naefs ] ; then
          echo  "export modelpath=${WORK}/naefs" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        else
          echo  "export modelpath=$COM_IN" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        fi

        echo  "export OBTYPE=GDAS" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export maskpath=$maskpath" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        echo  "export gdashead=$anl" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export gdasgrid=grid3" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export gdaspath=$COM_IN" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export modelgrid=grid3.f" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export model=$modnam"  >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export MODEL=$MODL" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export modelhead=$modnam" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        echo  "export vbeg=$cyc" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export vend=$cyc" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export valid_increment=21600" >>  run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        echo  "export lead='24, 48, 72, 96, 120, 144, 168, 192, 216,  240,  264, 288, 312, 336, 360, 384' "  >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
 

        if [ $modnam = ecme ] ; then
           echo  "export modeltail='.grib1'" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        else
           echo  "export modeltail='.grib2'" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        fi
 
        echo  "export extradir='atmos/'" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export climpath=$CLIMO/era5" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
        echo  "export members=$mbrs" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh


        if [ $modnam = naefs ] ; then 

          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GenEnsProd_fcstNAEFS_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/EnsembleStat_fcstNAEFS_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstNAEFS_obsModelAnalysis_climoERA5_mean.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        elif [ $modnam = ecme ] ; then

          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/EnsembleStat_fcstECME_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstECME_obsModelAnalysis_climoERA5_mean.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh


        elif [ $modnam = gefs ] || [ $modnam = cmce ] ; then

          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GenEnsProd_fcstGEFS_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/EnsembleStat_fcstGEFS_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh
          echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstGEFS_obsModelAnalysis_climoERA5_mean.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        elif  [ $modnam = gfs ] ; then
	  echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2GRID_CONF}/GridStat_fcstGFS_obsModelAnalysis_climoERA5.conf " >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        else

          echo "wrong model"
        exit

        fi

        [[ $SENDCOM="YES" ]] && echo "cp \$output_base/stat/${modnam}/grid_stat*.stat $COMOUTsmall" >> run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        chmod +x run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh

        echo "${DATA}/run_${modnam}_valid_at_t${cyc}z_${fhr}_g2g.sh" >> run_all_gens_g2g_poe.sh


      done #end of fhr 

     done #end of cycle

   done #end if modnam 

   chmod 775 run_all_gens_g2g_poe.sh

fi #end of if verify=upper  



if [ -s run_all_gens_g2g_poe.sh ] ; then
  ${DATA}/run_all_gens_g2g_poe.sh	 
fi


if [ $gather = yes ] ; then

 $USHevs/global_ens/evs_global_ens_atmos_gather.sh $MODELNAME grid2grid 00 00 

fi
 
 
