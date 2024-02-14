#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the href ecnt plotting python script
# Last updated: 10/30/2023, Binbin Zhou Lynker@EMC/NCEP
##******************************************************************************
set -x 

cd $DATA

export machine=${machine:-"WCOSS2"}
export prune_dir=$DATA/data
export save_dir=$DATA/out
export output_base_dir=$DATA/stat_archive
export log_metplus=$DATA/logs/GENS_verif_plotting_job
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

#*************************************************************
# Virtual link the href's stat data files of past 31/90 days
#*************************************************************
n=0
while [ $n -le $past_days ] ; do
  #hrs=`expr $n \* 24`
  hrs=$((n*24))
  day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
  echo $day
  $USHevs/cam/evs_get_href_stat_file_link_plots.sh $day "$model_list"
  export err=$?; err_chk
  n=$((n+1))
done 


VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central, Alaska, Appalachia, CPlains, DeepSouth, GreatBasin, GreatLakes, Mezquital, MidAtlantic, NorthAtlantic, NPlains, NRockies, PacificNW, PacificSW, Prairie, Southeast, Southwest, SPlains, SRockies"
																  
export fcst_init_hour="0,6,12,18"

export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}


verif_case=grid2obs

#*****************************************
# Build a POE file to collect sub-jobs
# ****************************************
> run_all_poe.sh

for fcst_valid_hour in 00 03 06 09 12 15 18 21 ; do

 for stats in rmse_spread ; do 
   if [ $stats = rmse_spread  ] ; then
     stat_list='rmse, spread'
     line_type='ecnt'
     if [ "$fcst_valid_hour" -eq "00" ] || [ "$fcst_valid_hour" -eq "12" ] ; then
       VARs='TMP2m DPT2m UGRD10m VGRD10m RH2m PRMSL WIND10m GUSTsfc HPBL'
     else
       VARs='TMP2m DPT2m UGRD10m VGRD10m RH2m PRMSL WIND10m GUSTsfc'
     fi
     score_types='lead_average'
   else
     err_exit "$stats is not a valid stat"
   fi   

 for score_type in $score_types ; do

  export fcst_init_hour="0,6,12,18"
  init_time='init00z_06z_12z_18z'

  export fcst_leads="6,9,12,15,18,21,24,27,30,33,36,39,42,45,48"

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

	 #****************
	 # Build sub-jobs
	 # **************
         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh  

        verif_type=conus_sfc

        echo "export PLOT_TYPE=lead_average_valid" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh

        echo "export field=${var}_${level}" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh

        echo "export eval_period=TEST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
        else
          echo "export date_type=VALID" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
        fi


         echo "export var_name=$VAR" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh

         echo "export line_type=$line_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
         echo "export interp=BILIN" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh
         echo "export score_py=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh

         thresh_fcst=' '
	 thresh_obs=' '

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/cam/evs_href_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh

         echo "${DATA}/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh


         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh 
         echo "${DATA}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.sh" >> run_all_poe.sh

     done #end of FCST_LEVEL_value

    done #end of VAR

  done #end of fcst_lead

 done #end of score_type

done #end of stats 

done #valid 

chmod +x run_all_poe.sh

#***************************************************************************
# Run the POE script in parallel or in sequence order to generate png files
#**************************************************************************
if [ $run_mpi = yes ] ; then
   mpiexec -np 72 -ppn 72 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
fi
export err=$?; err_chk

#**************************************************
# Change plot file names to meet the EVS standard
#**************************************************
cd $plot_dir

for valid in 00z 03z 06z 09z 12z 15z 18z 21z ; do
for stats in  rmse_spread ; do
 for score_type in lead_average ; do

  scoretype=fhrmean
  vars='prmsl tmp dpt ugrd vgrd rh wind gust mslet hpbl'

   for domain in conus conus_east conus_west conus_south conus_central alaska appalachia cplains deepsouth greatbasin greatlakes mezquital midatlantic northatlantic nolains nrockies pacificnw pacificsw prairie southeast southwest splains nplains srockies ; do

    if [ $domain = alaska ] ; then
        new_domain=$domain
    else
        new_domain=buk_${domain}
    fi


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


      if [ $var = mslet ] || [ $var = gust ] || [  $var = hpbl ] ; then
	if [ -s ${score_type}_regional_${domain}_valid_${valid}_${var}_${stats}.png ] ; then
          mv ${score_type}_regional_${domain}_valid_${valid}_${var}_${stats}.png  evs.href.${stats}.${var}_${level}.last${past_days}days.${scoretype}_valid_${valid}.${new_domain}.png
        fi 
      else
	if [ -s ${score_type}_regional_${domain}_valid_${valid}_${level}_${var}_${stats}.png ] ; then
          mv ${score_type}_regional_${domain}_valid_${valid}_${level}_${var}_${stats}.png  evs.href.${stats}.${var}_${level}.last${past_days}days.${scoretype}_valid_${valid}.${new_domain}.png
        fi
      fi

     done #var
   done  #domain
 done    #score_type
done     #stats
done     #valid 


tar -cvf evs.plots.href.grid2obs.ecnt.past${past_days}days.v${VDATE}.tar *.png

# Cat the plotting log files
log_dir="$DATA/logs"
if [ -d $log_dir ]; then
    log_file_count=$(find $log_dir -type f | wc -l)
    if [[ $log_file_count -ne 0 ]]; then
        log_files=("$log_dir"/*)
        for log_file in "${log_files[@]}"; do
            if [ -f "$log_file" ]; then
                echo "Start: $log_file"
                cat "$log_file"
                echo "End: $log_file"
            fi
        done
    fi
fi

if [ $SENDCOM = YES ] && [ -s evs.plots.href.grid2obs.ecnt.past${past_days}days.v${VDATE}.tar ] ; then
 cp -v evs.plots.href.grid2obs.ecnt.past${past_days}days.v${VDATE}.tar  $COMOUT/.  
fi

if [ $SENDDBN = YES ] ; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.href.grid2obs.ecnt.past${past_days}days.v${VDATE}.tar
fi  







