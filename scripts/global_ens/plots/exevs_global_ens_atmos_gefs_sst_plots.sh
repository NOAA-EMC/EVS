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

export interp_pnts=' '

export init_end=$VDATE
export valid_end=$VDATE

model_list='GEFS'
models='GEFS'

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
  $USHevs/global_ens/evs_get_gens_atmos_stat_file_link_plots.sh $day "$model_list"
  n=$((n+1))
done 


VX_MASK_LIST="G003, NHEM, SHEM, TROPICS"
																  
export fcst_init_hour="0,12"
export fcst_valid_hour="0"
valid_time='valid00z'
init_time='init00_12z'

export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}


verif_case=grid2grid
verif_type=sfc

> run_all_poe.sh

for stats in rmse_me ; do 
 if [ $stats = rmse_me  ] ; then
   stat_list='rmse, me'
   line_tp='ecnt'
 else
   echo $stats is wrong stat
   exit
 fi   

 for score_type in time_series lead_average ; do

  if [ $score_type = time_series ] ; then
    export fcst_leads="120 240 360"
  else
    export fcst_leads="vs_lead" 
  fi
 
  for lead in $fcst_leads ; do 

   if [ $lead = vs_lead ] ; then
	export fcst_lead="24,36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384"
   else
        export fcst_lead=$lead
   fi

    for VAR in  SST ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       FCST_LEVEL_values="Z0"

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

	OBS_LEVEL_value="0,*,*"

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in $line_tp ; do 

         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh  

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
     
	 thresh_fcst=''
         thresh_obs=''

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g" -e "s!thresh_obs!$thresh_obs!g"  -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/global_ens/evs_gens_atmos_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         echo "${DATA}/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh


         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh 
         echo " ${DATA}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_all_poe.sh

      done #end of line_type

     done #end of FCST_LEVEL_value

    done #end of VAR

  done #end of fcst_lead

 done #end of score_type

done #end of stats 

chmod +x run_all_poe.sh

#if [ $run_mpi = yes ] ; then
#  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
#   mpiexec -np 4 -ppn 4 --cpu-bind verbose,depth cfp run_all_poe.sh
#else
  ${DATA}/run_all_poe.sh
#fi

cd $plot_dir
for stats in rmse_me ; do
 for score_type in time_series lead_average ; do

  if [ $score_type = time_series ] ; then
    leads='_f120.png _f240.png _f360.png'
    scoretype='timeseries' 

  elif [ $score_type = lead_average ] ; then
    leads='.png'
    scoretype='fhrmean'
  fi


  for lead in $leads ; do
    
    if [ $score_type = time_series ] ; then
	lead_time=_${lead:1:4}
    else
        lead_time=_f384
    fi

   for domain in g003 nhem shem tropics ; do

     if [ $domain = g003 ] ; then
       domain_new=glb
     else
       domain_new=$domain
     fi

    for var in tmp ; do

      for level in z0 ; do

        mv ${score_type}_regional_${domain}_valid_00z_sfc_${var}_${level}_mean_${stats}${lead}  evs.global_ens.${stats}.sst.last${past_days}days.${scoretype}.${valid_time}${lead_time}.g003_${domain_new}.png
               
      done #level

    done #var
   done  #domain
  done   #lead
 done    #score_type
done     #stats

#scp *.png wd20bz@emcrzdm:/home/people/emc/www/htdocs/bzhou/evs_plots/gens/sst

tar -cvf evs.plots.gefs.sst.v${VDATE}.past${past_days}days.tar *.png

cp evs.plots.gefs.sst.v${VDATE}.past${past_days}days.tar  $COMOUT/.  





