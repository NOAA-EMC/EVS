#!/bin/ksh

set -x 

cd $DATA

export prune_dir=$DATA/data
export save_dir=$DATA/out
export output_base_dir=$DATA/stat_archive
export log_metplus=$DATA/logs/GENS_verif_plotting_job.out
mkdir -p $prune_dir
mkdir -p $save_dir
mkdir -p $output_base_dir
mkdir -p $DATA/logs


export eval_period='TEST'

export interp_pnts=''

export init_end=$VDATE
export valid_end=$VDATE

model_list='HREF'
models='HREF'

n=0
while [ $n -le $past_days ] ; do
    hrs=$((n*24))
    first_day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
    n=$((n+1))
done

export init_beg=$first_day
export valid_beg=$first_day

n=0
while [ $n -le $past_days ] ; do
  #hrs=`expr $n \* 24`
  hrs=$((n*24))
  day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
  echo $day
  $USHevs/cam/evs_get_href_stat_file_link_plots.sh $day "$model_list"
  n=$((n+1))
done 


VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central, Alaska, Appalachia, CPlains, DeepSouth, GreatBasin, GreatLakes, Mezquital, MidAtlantic, NorthAtlantic, NPlains, NRockies, PacificNW, PacificSW, Prairie, Southeast, Southwest, SPlains, SRockies"
																  
export fcst_init_hour="0,6,12,18"
export fcst_valid_hour="0,3,6,9,12,15,18,21,24"

export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}


verif_case=grid2obs

> run_all_poe.sh

for stats in rmse_spread ; do 
 if [ $stats = rmse_spread  ] ; then
  stat_list='rmse, spread'
  line_tp='ecnt'
  VARs='TMP2m DPT2m UGRD10m VGRD10m RH2m PRMSL WIND10m GUSTsfc HPBL'
  score_types='lead_average'
 else
  echo $stats is wrong stat
  exit
 fi   

 for score_type in $score_types ; do

  export fcst_init_hour="0,6,12,18"
  export fcst_valid_hour="0,6,12,18"
  valid_time='available_times'
  init_time='init00z_06z_12z_18z'

  export fcst_leads="6,12,18,24,30,36,42,48"

  for lead in $fcst_leads ; do 

    for VAR in $VARs ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       if [ $VAR = TMP2m ] || [ $VAR = DPT2m ] || [ $VAR = RH2m ] ; then 
          FCST_LEVEL_values="Z2"
       elif [ $VAR = UGRD10m ] || [ $VAR = VGRD10m ] || [ $VAR = WIND10m ] ; then
          FCST_LEVEL_values="Z10"
       elif [ $VAR = PRMSL ] || [ $VAR = GUSTsfc ] || [ $VAR = HPBL ] ; then
          FCST_LEVEL_values="L0"
       fi

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

	OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in $line_tp ; do 

         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh  

        verif_type=conus_sfc

        echo "export PLOT_TYPE=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export field=${var}_${level}" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export met_ver=$met_v" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export eval_period=TEST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        else
          echo "export date_type=VALID" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        fi


         echo "export var_name=$VAR" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         echo "export line_type=$line_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export interp=NEAREST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export score_py=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         thresh_fcst=' '
	 thresh_obs=' '

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/cam/evs_href_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         echo "${DATA}/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh


         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh 
         echo "${DATA}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_all_poe.sh

      done #end of line_type

     done #end of FCST_LEVEL_value

    done #end of VAR

  done #end of fcst_lead

 done #end of score_type

done #end of stats 

chmod +x run_all_poe.sh


if [ $run_mpi = yes ] ; then
  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
   mpiexec -np 24 -ppn 24 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
fi


cd $plot_dir

for stats in  rmse_spread ; do
 for score_type in lead_average ; do

  scoretype=fhrmean
  vars='prmsl tmp dpt ugrd vgrd rh wind gust mslet hpbl'

   for domain in conus conus_east conus_west conus_south conus_central alaska appalachia cplains deepsouth greatbasin greatlakes mezquital midatlantic northatlantic nolains nrockies pacificnw pacificsw prairie southeast southwest splains nplains srockies ; do

    for var in $vars ; do

      if [ $var = mslet ] ; then
	  var_new=prmsl
      else
	  var_new=$var
      fi

      if [ $var = tmp ] || [ $var = dpt ] || [ $var = rh ]; then
	 level='2m'
      elif [ $var = ugrd ] || [ $var = vgrd ] || [ $var = wind ] ; then
	 level='10m'
      elif [ $var = mslet ] || [ $var = gust ] || [ $var = hpbl ] ; then
	 level='l0'
      fi


     valid=valid_available_times

      if [ $var = mslet ] || [ $var = gust ] || [  $var = hpbl ] ; then
        mv ${score_type}_regional_${domain}_${valid}_${var}_${stats}.png  evs.href.${stats}.${var}_${level}.last${past_days}days.${scoretype}.${valid_time}.buk_${domain}.png
      else
        mv ${score_type}_regional_${domain}_${valid}_${level}_${var}_${stats}.png  evs.href.${stats}.${var}_${level}.last${past_days}days.${scoretype}.${valid_time}.buk_${domain}.png
      fi

     done #var
   done  #domain
 done    #score_type
done     #stats

#scp *.png wd20bz@emcrzdm:/home/people/emc/www/htdocs/bzhou/evs_evs.plots.href/grid2obs

tar -cvf evs.plots.href.grid2obs.ecnt.past${past_days}days.v${VDATE}.tar *.png

cp evs.plots.href.grid2obs.ecnt.past${past_days}days.v${VDATE}.tar  $COMOUT/.  









