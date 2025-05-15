#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the href snowfall plotting python script
# Last updated:
#              01/10/2025, add MPMD, by Binbin Zhou Lynker@EMC/NCEP
#              07/09/2024, add restart, by Binbin Zhou Lynker@EMC/NCEP 
#              05/30/2024, Binbin Zhou Lynker@EMC/NCEP
#******************************************************************************
set -x 

mkdir -p $DATA/scripts
cd $DATA/scripts

export machine=${machine:-"WCOSS2"}
export output_base_dir=$DATA/stat_archive
mkdir -p $output_base_dir

all_plots=$DATA/plots/all_plots
mkdir -p $all_plots
if [ $SENDCOM = YES ] ; then
 restart=$COMOUT/restart/$last_days/href_snowfall_plots
 if [ ! -d  $restart ] ; then
  mkdir -p $restart
 fi 
fi

export eval_period='TEST'

export interp_pnts=''

export init_end=$VDATE
export valid_end=$VDATE

model_list='HREF_SNOW'
models='HREF_SNOW'

VX_MASK_LISTs='CONUS CONUS_East CONUS_West CONUS_South CONUS_Central'

n=0
while [ $n -le $last_days ] ; do
    hrs=$((n*24))
    first_day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
    n=$((n+1))
done

export init_beg=$first_day
export valid_beg=$first_day
export obsv=" - Validation: NOHRSC"

#*************************************************************
# Virtual link the href's stat data files of last 31/90 days
#*************************************************************
n=0
while [ $n -le $last_days ] ; do
  #hrs=`expr $n \* 24`
  hrs=$((n*24))
  day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
  echo $day
  $USHevs/cam/evs_get_href_stat_file_link_plots.sh $day "$model_list"
  export err=$?; err_chk
  n=$((n+1))
done 

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
	echo "set -x" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh 

	save_dir=$DATA/plots/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}
	plot_dir=$save_dir/precip/${valid_beg}-${valid_end}
        mkdir -p $plot_dir
        mkdir -p $save_dir/data

	echo "export save_dir=$save_dir" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
	echo "export log_metplus=$save_dir/log_verif_plotting_job.out" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
	echo "export prune_dir=$save_dir/data" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh

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

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/cam/evs_href_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh

         echo "${DATA}/scripts/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh

	 echo "if [ -s ${plot_dir}/${score_type}_regional_${domain}_valid_${fcst_valid_hour}z_${accum}_${var}*.png ] ; then " >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
         echo "  cp -v ${plot_dir}/${score_type}_regional_${domain}_valid_${fcst_valid_hour}z_${accum}_${var}*.png $all_plots" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
	 echo "  echo completed >${plot_dir}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.completed" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
         #Copy files to restart directory
	 echo "  if [ $SENDCOM = YES ] ; then" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
	 echo "    cp -v $all_plots/${score_type}_regional_${domain}_valid_${fcst_valid_hour}z_${accum}_${var}*.png $restart" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
	 echo "    cp -v ${plot_dir}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.completed $restart" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
	 echo "  fi" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
	 echo "fi" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh

         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh 
         echo "${DATA}/scripts/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh" >> run_all_poe.sh

        else
	 if [ -s $restart/${score_type}_regional_${domain}_valid_${fcst_valid_hour}z_${accum}_${var}*.png ] ; then
	   cp -v $restart/${score_type}_regional_${domain}_valid_${fcst_valid_hour}z_${accum}_${var}*.png $all_plots
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
mpiexec -np 30 -ppn 30 --cpu-bind verbose,depth cfp ${DATA}/scripts/run_all_poe.sh
export err=$?; err_chk

#**************************************************
# Change plot file names to meet the EVS standard
#**************************************************
cd $all_plots

for stats in ets fbias fss ; do
  score_type='threshold_average' 
  scoretype='threshmean'

  for var in weasd ; do
   for level in 06h 24h ; do
    if [ $stats = fss ] ; then 
       if [ $level = 06h ] ; then
        valids="00z 06z 12z 18z"
        lead=width1-3-5-7-9-11_f6-12-18-24-30-36-42-48
	new_level=a06
       elif [ $level = 24h ] ; then
        valids="00z 12z"
        lead=width1-3-5-7-9-11_f24-30-36-42-48
	 new_level=a24
       fi	
    else	    
      if [ $level = 06h ] ; then
	valids="00z 06z 12z 18z"
        lead=f6-12-18-24-30-36-42-48
	 new_level=a06
      elif [ $level = 24h ] ; then
        valids="00z 12z"
        lead=f24-30-36-42-48
	 new_level=a24
      fi
    fi

   for valid in $valids ; do   
    for domain in conus conus_east conus_west conus_south conus_central  ; do
        
     if [ $domain = conus ] ; then
	 new_domain=buk_conus
     elif [ $domain = conus_east ] ; then
   	 new_domain=buk_conus_e
     elif [ $domain = conus_west ] ; then
   	 new_domain=buk_conus_w
     elif [ $domain = conus_south ] ; then
	 new_domain=buk_conus_s
     elif [ $domain = conus_central ] ; then
         new_domain=buk_conus_c
     fi

     if [ -s ${score_type}_regional_${domain}_valid_${valid}_${level}_${var}_${stats}_${lead}.png ] ; then
       mv ${score_type}_regional_${domain}_valid_${valid}_${level}_${var}_${stats}_${lead}.png  evs.href.${stats}.${var}_${new_level}.last${last_days}days.${scoretype}_valid${valid}.${new_domain}.png
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
	 new_level=a06
    elif [ $level = 24h ] ; then
        valids="00z 12z"
        lead=f24-30-36-42-48__ge0.0254ge0.1016ge0.2032ge0.3048
	 new_level=a24
    fi

   for valid in $valids ; do
    for domain in conus conus_east conus_west conus_south conus_central  ; do

     if [ $domain = conus ] ; then
         new_domain=buk_conus
     elif [ $domain = conus_east ] ; then
         new_domain=buk_conus_e
     elif [ $domain = conus_west ] ; then
         new_domain=buk_conus_w
     elif [ $domain = conus_south ] ; then
         new_domain=buk_conus_s
     elif [ $domain = conus_central ] ; then
         new_domain=buk_conus_c
     fi

      if [ -s ${score_type}_regional_${domain}_valid_${valid}_${level}_${var}_${lead}.png ] ; then
         mv ${score_type}_regional_${domain}_valid_${valid}_${level}_${var}_${lead}.png  evs.href.ctc.${var}_${new_level}.last${last_days}days.${scoretype}_valid${valid}.${new_domain}.png
      fi 
    done
   done
 done
done

if [ -s evs*.png ] ; then
  tar -cvf evs.plots.href.snowfall.last${last_days}days.v${VDATE}.tar evs*.png
fi

# Cat the plotting log files
log_dir="$DATA/plots"
if [ -s $log_dir/*/log*.out ]; then
  log_files=`ls $log_dir/*/log*.out`
  for log_file in $log_files ; do
     echo "Start: $log_file"
     cat  "$log_file"
     echo "End: $log_file"
  done   
fi 

if [ $SENDCOM = YES ] && [ -s evs.plots.href.snowfall.last${last_days}days.v${VDATE}.tar ] ; then
 cp -v evs.plots.href.snowfall.last${last_days}days.v${VDATE}.tar  $COMOUT/.  
fi

if [ $SENDDBN = YES ] ; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.href.snowfall.last${last_days}days.v${VDATE}.tar
fi





