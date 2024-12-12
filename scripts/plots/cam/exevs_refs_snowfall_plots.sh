#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the refs snowfall plotting python script
# Last updated: 05/30/2024, Binbin Zhou Lynker@EMC/NCEP
#******************************************************************************
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

restart=$COMOUT/restart/$last_days/refs_snowfall_plots
if [ ! -d  $restart ] ; then
  mkdir -p $restart
fi 

export eval_period='TEST'

export interp_pnts=''

export init_end=$VDATE
export valid_end=$VDATE

model_list='REFS_SNOW'
models='REFS_SNOW'

VX_MASK_LISTs='CONUS CONUS_East CONUS_West CONUS_South CONUS_Central'

n=0
while [ $n -le $last_days ] ; do
    hrs=$((n*24))
    first_day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
    n=$((n+1))
done

export init_beg=$first_day
export valid_beg=$first_day

#*************************************************************
# Virtual link the refs's stat data files of last 31/90 days
#*************************************************************
n=0
while [ $n -le $last_days ] ; do
  #hrs=`expr $n \* 24`
  hrs=$((n*24))
  day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
  echo $day
  $USHevs/cam/evs_get_refs_stat_file_link_plots.sh $day "$model_list"
  export err=$?; err_chk
  n=$((n+1))
done 

export plot_dir=$DATA/out/precip/${valid_beg}-${valid_end}
#For restart:
if [ ! -d $plot_dir ] ; then
  mkdir -p $plot_dir
fi

verif_case=precip
verif_type=ccpa

#***************************************
# Build a POE file to collect sub=jobs
# **************************************
> run_all_poe.sh

for VX_MASK_LIST in $VX_MASK_LISTs ; do
 
   domain=`echo $VX_MASK_LIST | tr '[A-Z]' '[a-z]'`

for stats in ets_fbias ratio_pod_csi fss ; do 
 if [ $stats = ets_fbias ] ; then
    stat_list='ets, fbias'
    line_tp='ctc'
    VARs='WEASD'
    interp_pnts=''
    score_types='threshold_average '
 elif [ $stats = ratio_pod_csi ] ; then
    stat_list='sratio, pod, csi'
    line_tp='ctc'
    VARs='WEASD'
    interp_pnts=''
    score_types='performance_diagram'
 elif [ $stats = fss ] ; then
    stat_list='fss'
    line_tp='nbrcnt'
    VARs='WEASD'    
    interp_pnts='1,9,25,49,91,121'
    score_types='threshold_average' 
 else
  err_exit "$stats is not a valid stat"
 fi   

 for score_type in $score_types ; do

  for VAR in $VARs ; do

     var=`echo $VAR | tr '[A-Z]' '[a-z]'`

     for FCST_LEVEL_value in A06 A24 ; do
 
	 OBS_LEVEL_value=$FCST_LEVEL_value

    	 if [ $FCST_LEVEL_value  = A06 ] ; then
            export fcst_leads='6,12,18,24,30,36,42,48'
            export fcst_valid_hours='00 06 12 18'
            accum=06h
         elif [ $FCST_LEVEL_value = A24 ] ; then
            export fcst_leads='24,30,36,42,48'
            export fcst_valid_hours='00 12'
	    accum=24h
         fi

         	 
      for lead in $fcst_leads ; do

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

       for line_type in $line_tp ; do 

	for fcst_valid_hour in $fcst_valid_hours ; do

	 #*****************************
	 # Build sub-jobs
	 # ****************************
         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh  

      #***********************************************************************************************************************************
      #  Check if this sub-job has been completed in the previous run for restart
      if [ ! -e $restart/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.completed ] ; then
      #***********************************************************************************************************************************
      
	echo "#!/bin/ksh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh 
        echo "export PLOT_TYPE=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh

        echo "export eval_period=TEST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
        else
          echo "export date_type=VALID" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
        fi


         echo "export var_name=$VAR" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh

         echo "export line_type=$line_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh

	 if [ $stats = fss ] ; then
	   
	   echo "export interp=NBRHD_SQUARE" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
         else	   
           echo "export interp=NEAREST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
	 fi

         echo "export score_py=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
 
         thresh_fcst='>=0.0254, >=0.1016, >=0.2032, >=0.3048'
	 thresh_obs=$thresh_fcst

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/cam/evs_refs_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh

         echo "${DATA}/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh

	 #Save for restart
	 echo "if [ -s ${plot_dir}/${score_type}_regional_${domain}_valid_${fcst_valid_hour}z_${accum}_${var}*.png ] ; then " >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
	 #threshold_average_regional_conus_east_valid_12z_24h_weasd_ets_f24-30-36-42-48.png
         echo "  cp -v ${plot_dir}/${score_type}_regional_${domain}_valid_${fcst_valid_hour}z_${accum}_${var}*.png $restart" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
	 echo "  >$restart/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.completed" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
	 echo "fi" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh

         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh 
         echo "${DATA}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh" >> run_all_poe.sh

	else
	 #Restart from existing png files of previous run
	 if [ -s $restart/${score_type}_regional_${domain}_valid_${fcst_valid_hour}z_${accum}_${var}*.png ] ; then
	  cp  $restart/${score_type}_regional_${domain}_valid_${fcst_valid_hour}z_${accum}_${var}*.png ${plot_dir}/.
	 fi
        fi

       done #end of fcst_valid_hour        

      done #end of line_type

     done #end of FCST_LEVEL_value

    done #end of VAR

  done #end of fcst_lead

 done #end of score_type

done #end of stats 

done #end of vx_mask_list
chmod +x run_all_poe.sh

#***************************************************************************
# Run the POE script in parallel or in sequence order to generate png files
#**************************************************************************
if [ $run_mpi = yes ] ; then
   mpiexec -np 30 -ppn 30 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
fi
export err=$?; err_chk


#**************************************************
# Change plot file names to meet the EVS standard
#**************************************************
cd $plot_dir

for stats in ets fbias fss ; do
  score_type='threshold_average' 
  scoretype='threshmean'

  for var in weasd ; do
   for level in 06h 24h ; do
    if [ $stats = fss ] ; then 
       if [ $level = 06h ] ; then
        valids="00z 06z 12z 18z"
        lead=width1-3-5-7-9-11_f6-12-18-24-30-36-42-48
       elif [ $level = 24h ] ; then
        valids="00z 12z"
        lead=width1-3-5-7-9-11_f24-30-36-42-48
       fi	
    else	    
      if [ $level = 06h ] ; then
	valids="00z 06z 12z 18z"
        lead=f6-12-18-24-30-36-42-48
      elif [ $level = 24h ] ; then
        valids="00z 12z"
        lead=f24-30-36-42-48
      fi
    fi
  
   for valid in $valids ; do   
    for domain in conus conus_east conus_west conus_south conus_central  ; do
      if [ -s ${score_type}_regional_${domain}_valid_${valid}_${level}_${var}_${stats}_${lead}.png ] ; then
       mv ${score_type}_regional_${domain}_valid_${valid}_${level}_${var}_${stats}_${lead}.png  evs.refs.${stats}.${var}_${level}.last${last_days}days.${scoretype}_valid${valid}.buk_${domain}.png
      fi
    done
   done
  done
 done
done


score_type='performance_diagram'  
scoretype='perfdiag'

for var in weasd ; do
 for level in 06h 24h ; do
    if [ $level = 06h ] ; then
        valids="00z 06z 12z 18z"
        lead=f6-12-18-24-30-36-42-48__ge0.0254ge0.1016ge0.2032ge0.3048
    elif [ $level = 24h ] ; then
        valids="00z 12z"
        lead=f24-30-36-42-48__ge0.0254ge0.1016ge0.2032ge0.3048
    fi

  for valid in $valids ; do  
    for domain in conus conus_east conus_west conus_south conus_central  ; do
      if [ -s ${score_type}_regional_${domain}_valid_${valid}_${level}_${var}_${lead}.png ] ; then
         mv ${score_type}_regional_${domain}_valid_${valid}_${level}_${var}_${lead}.png  evs.refs.ctc.${var}_${level}.last${last_days}days.${scoretype}_valid${valid}.buk_${domain}.png
      fi 
    done
  done
 done
done

if [ -s *.png ] ; then
 tar -cvf evs.plots.refs.snowfall.last${last_days}days.v${VDATE}.tar *.png
fi

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


if [ $SENDCOM = YES ] && [ -s evs.plots.refs.snowfall.last${last_days}days.v${VDATE}.tar ] ; then
 cp -v evs.plots.refs.snowfall.last${last_days}days.v${VDATE}.tar  $COMOUT/.  
fi

if [ $SENDDBN = YES ] ; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.refs.snowfall.last${last_days}days.v${VDATE}.tar
fi
