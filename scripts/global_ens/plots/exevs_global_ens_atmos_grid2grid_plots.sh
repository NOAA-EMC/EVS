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
#export past_days=0

export init_end=$VDATE
export valid_end=$VDATE

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
  sh $USHevs/global_ens/evs_get_gens_atmos_stat_file_link.sh $day
  n=$((n+1))
done 


VX_MASK_LIST="G003, NHEM, SHEM, TROPICS, CONUS"
																  
export fcst_init_hour="0,12"
export fcst_valid_hour="0,12"

export plot_dir=$DATA/out/ceil_vis/${valid_beg}-${valid_end}


> run_all_poe.sh 

for score_type in time_series lead_average ; do

  if [ $score_type = time_series ] ; then
    export fcst_init_hour="0,12"
    export fcst_valid_hour="0,12"
    export fcst_leads="120 240 360"
  else
    export fcst_init_hour="0,12"
    export fcst_valid_hour="0,12"
    export fcst_leads="vs_lead" 
  fi
 
  for lead in $fcst_leads ; do 

   if [ $lead = vs_lead ] ; then
	export fcst_lead="12, 24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384"
   else
        export fcst_lead=$lead
   fi

    for VAR in HGT TMP UGRD VGRD PRMSL ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       if [ $VAR = HGT ] ; then
          FCST_LEVEL_values="P500 P700 P1000"
          #FCST_LEVEL_values="P500"
       elif [ $VAR = TMP ] ; then
          FCST_LEVEL_values="P500 P850"
       elif [ $VAR = UGRD ] || [ $VAR = VGRD ] ; then
          FCST_LEVEL_values="P850 P250 Z10"
       elif [ $VAR = PRMSL ] ; then
          FCST_LEVEL_values="L0"
       fi

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

	OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in sal1l2 ; do 

         > run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh  

       echo "export PLOT_TYPE=$score_type" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

       echo "export field=${var}_${level}" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh


        if [ $line_type = ctc ] ; then
          if [ $score_type = performance_diagram ] ; then
           stat_list="sratio, pod, csi"
          else
           stat_list="csi"
          fi
        elif [ $line_type = sl1l2 ] ; then
          stat_list="rmse, bias"
        elif [ $line_type = sal1l2 ] ; then
          stat_list="acc"
        fi

        #echo "export vx_mask_list=$grid" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_case=grid2grid" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_type=anom" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export log_level=INFO" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export met_ver=10.0" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export model='GEFS'" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export eval_period=TEST" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        else
          echo "export date_type=VALID" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        fi


         echo "export var_name=$VAR" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         echo "export line_type=$line_type" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export interp=NEAREST" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export score_py=$score_type" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

	 thresh=' '
         sed -e "s!stat_list!$stat_list!g"  -e "s!thresh_list!$thresh!g"  -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g"  $USHevs/global_ens/evs_gens_atmos_grid2grid_plots.sh > run_py.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         chmod +x  run_py.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         echo "sh run_py.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh


        #if [ $score_type = performance_diagram ] ; then
        #   echo "mv ${plot_dir}/${score_type}_regional_*\${grd}*_*\${vname}*.png ${plot_dir}/evs.narre.ctc.\${field}.last${past_days}days.perfdiag_f012.\${mask}.png" >>  run_narre_${score_type}.${VAR}.${line_type}.sh
        #fi
     
         chmod +x  run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh 
         echo " run_${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_all_poe.sh

      done #end of line_type

     done #end of FCST_LEVEL_value

    done #end of VAR

 done #end of fcst_lead

done #end of score_type

chmod +x run_all_poe.sh

if [ $run_mpi = yes ] ; then
  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
   mpiexec -np 48 -ppn 48 --cpu-bind verbose,depth cfp run_all_poe.sh
else
 sh run_all_poe.sh
fi


exit

cd $plot_dir
  
tar -cvf plots_narre_grid2obs_v${VDATE}.tar *.png

cp plots_narre_grid2obs_v${VDATE}.tar  $COMOUT/.  





