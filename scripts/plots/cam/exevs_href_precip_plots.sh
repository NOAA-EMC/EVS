#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the href cape plotting python script
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
 restart=$COMOUT/restart/$last_days/href_precip_plots
 if [ ! -d  $restart ] ; then
  mkdir -p $restart
 fi     
fi

export eval_period='TEST'

export interp_pnts=''

export init_end=$VDATE
export valid_end=$VDATE

model_list='HREF_MEAN HREF_AVRG HREF_LPMM HREF_PMMN'
models='HREF_MEAN,  HREF_AVRG, HREF_LPMM, HREF_PMMN'

VX_MASK_LISTs='CONUS CONUS_East CONUS_West CONUS_South CONUS_Central Alaska'

n=0
while [ $n -le $last_days ] ; do
    hrs=$((n*24))
    first_day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
    n=$((n+1))
done

export init_beg=$first_day
export valid_beg=$first_day

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
  n=$((n+1))
done 


verif_case=precip
verif_type=ccpa

#*****************************************
# Build a POE file to collect sub-jobs
# ****************************************
> run_all_poe.sh

for VX_MASK_LIST in $VX_MASK_LISTs ; do
 	
  domain=`echo $VX_MASK_LIST | tr '[A-Z]' '[a-z]'`

for stats in ets_fbias ratio_pod_csi fss ; do 
 if [ $stats = ets_fbias ] ; then
    stat_list='ets, fbias'
    line_tp='ctc'
    VARs='APCP_01 APCP_03 APCP_24'
    interp_pnts=''
    score_types='threshold_average '
 elif [ $stats = ratio_pod_csi ] ; then
    stat_list='sratio, pod, csi'
    line_tp='ctc'
    VARs='APCP_01 APCP_03 APCP_24'
    interp_pnts=''
    score_types='performance_diagram'
 elif [ $stats = fss ] ; then
    stat_list='fss'
    line_tp='nbrcnt'
    VARs='APCP_01 APCP_03 APCP_24'    
    interp_pnts='1,9,25,49,91,121'
    score_types='threshold_average' 
 else
  err_exit "$stats is not a valid stat"
 fi   

 for score_type in $score_types ; do

  for VAR in $VARs ; do
 
   var=`echo $VAR | tr '[A-Z]' '[a-z]'`

   if [ $VAR = APCP_01 ] ; then
	#export fcst_leads='3,6,9,12,15,18,21,24'
	export fcst_leads='1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24'
	export fcst_valid_hours='00 03 06 09 12 15 18 21'
	FCST_LEVEL_values=A01
   elif [ $VAR = APCP_03 ] ; then
         export fcst_leads='3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48'
	 export fcst_valid_hours='00 03 06 09 12 15 18 21'
	 FCST_LEVEL_values=A03
   elif [ $VAR = APCP_24 ] ; then
         export fcst_leads='24,30,36,42,48'
	 export fcst_valid_hours='12'
	 FCST_LEVEL_values=A24
   fi

  for lead in $fcst_leads ; do 

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

	if [ $VX_MASK_LIST = Alaska ] ; then
          OBS_LEVEL_value=L0
	else
          OBS_LEVEL_value=$FCST_LEVEL_value
        fi

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in $line_tp ; do 

       for fcst_valid_hour in $fcst_valid_hours ; do	      

	 #***************
	 # Build sub-jobs
	 # ***************
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
 
	 if [ $VAR = APCP_01 ] ; then
           thresh_fcst='>=0.254, >=2.54, >=6.35, >=12.7, >=25.4'
         elif [ $VAR = APCP_03 ] ; then
           thresh_fcst='>=2.54, >=6.35, >=12.7, >=25.4, >=50.8'
         elif [ $VAR = APCP_24 ] ; then
           thresh_fcst='>=12.7, >=25.4, >=50.8, >=76.2'
	 fi
	 thresh_obs=$thresh_fcst

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/cam/evs_href_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh

         echo "${DATA}/scripts/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh

	 echo "if [ -s ${plot_dir}/${score_type}_regional_${domain}_valid_${fcst_valid_hour}z_*${var}*.png ] ; then " >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
	 echo "  cp -v ${plot_dir}/${score_type}_regional_${domain}_valid_${fcst_valid_hour}z_*${var}*.png $all_plots" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
	 echo "  echo completed >${plot_dir}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.completed" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
	 #Copy files to restart directory
         echo "  if [ $SENDCOM = YES ] ; then" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
	 echo "    cp -v $all_plots/${score_type}_regional_${domain}_valid_${fcst_valid_hour}z_*${var}*.png $restart" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
	 echo "    cp -v ${plot_dir}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.completed $restart" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
	 echo "  fi" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh
	 echo "fi" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh

         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh 
         echo "${DATA}/scripts/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.${fcst_valid_hour}.sh" >> run_all_poe.sh

       else
	if [ -s $restart/${score_type}_regional_${domain}_valid_${fcst_valid_hour}z_*${var}*.png ] ; then
	  cp -v $restart/${score_type}_regional_${domain}_valid_${fcst_valid_hour}z_*${var}*.png $all_plots
	fi
       fi 

       done # end of fcst_valid_hour

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
mpiexec -np 304 -ppn 76 --cpu-bind verbose,depth cfp ${DATA}/scripts/run_all_poe.sh
export err=$?; err_chk

#**************************************************
# Change plot file names to meet the EVS standard
#**************************************************

cd $all_plots

for stats in ets fbias fss ; do
  score_type='threshold_average' 
  scoretype='threshmean'

  for var in apcp_01 apcp_03 apcp_24 ; do

    if [ $var = apcp_01 ] || [ $var = apcp_03 ] ; then
      valids="00z 03z 06z 09z 12z 15z 18z 21z"
    elif [ $var = apcp_24 ] ; then
      valids="12z"
    fi 

    if [ $var = apcp_01 ] ; then
      new_var=apcp_a01
    elif [ $var = apcp_03 ] ; then
       new_var=apcp_a03
    elif [ $var = apcp_24 ] ; then
       new_var=apcp_a24
    fi 

    level=${var:5:2}h
    if [ $stats = fss ] ; then 
       if [ $var = apcp_01 ] ; then
        lead=width1-3-5-7-9-11_f1_to_f24
       elif [ $var = apcp_03 ] ; then
        lead=width1-3-5-7-9-11_f3_to_f48
       elif [ $var = apcp_24 ] ; then
        lead=width1-3-5-7-9-11_f24-30-36-42-48
       fi	
    else	    
      if [ $var = apcp_01 ] ; then
        lead=f1_to_f24
      elif [ $var = apcp_03 ] ; then
        lead=f3_to_f48
      elif [ $var = apcp_24 ] ; then
        lead=f24-30-36-42-48
      fi
    fi

   for domain in conus conus_east conus_west conus_south conus_central alaska  ; do

     if [ $domain = alaska ] ; then
       new_domain=$domain
     elif [ $domain = conus ] ; then
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

    for valid in $valids ; do
 
      if [ -s ${score_type}_regional_${domain}_valid_${valid}_${level}_${var}_${stats}_${lead}.png ] ; then
        ls ${score_type}_regional_${domain}_valid_${valid}_${level}_${var}_${stats}_${lead}.png
        mv ${score_type}_regional_${domain}_valid_${valid}_${level}_${var}_${stats}_${lead}.png  evs.href.${stats}.${new_var}.last${last_days}days.${scoretype}_valid${valid}.${new_domain}.png
      fi
    done
  done

 done
done


score_type='performance_diagram'  
scoretype='perfdiag'

for var in apcp_01 apcp_03 apcp_24 ; do
  
    if [ $var = apcp_01 ] || [ $var = apcp_03 ] ; then
	 valids="00z 03z 06z 09z 12z 15z 18z 21z"
    elif [ $var = apcp_24 ] ; then
         valids="12z"
    fi

    level=${var:5:2}h
    if [ $var = apcp_01 ] ; then
        lead=f1_to_f24__ge0.254ge2.54ge6.35ge12.7ge25.4
	new_var=apcp_a01
    elif [ $var = apcp_03 ] ; then
        lead=f3_to_f48__ge2.54ge6.35ge12.7ge25.4ge50.8
	new_var=apcp_a03
    elif [ $var = apcp_24 ] ; then
        lead=f24-30-36-42-48__ge12.7ge25.4ge50.8ge76.2
	new_var=apcp_a24
    fi

   for domain in conus conus_east conus_west conus_south conus_central alaska  ; do
    for valid in $valids ; do

     if [ $domain = alaska ] ; then
         new_domain=$domain
     elif [ $domain = conus ] ; then
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
       mv ${score_type}_regional_${domain}_valid_${valid}_${level}_${var}_${lead}.png  evs.href.ctc.${new_var}.last${last_days}days.${scoretype}_valid${valid}.${new_domain}.png
      fi

    done
  done
done

if [ -s evs*.png ] ; then
  tar -cvf evs.plots.href.precip.last${last_days}days.v${VDATE}.tar evs*.png
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


if [ $SENDCOM = YES ] && [ -s evs.plots.href.precip.last${last_days}days.v${VDATE}.tar ] ; then
 cp -v evs.plots.href.precip.last${last_days}days.v${VDATE}.tar  $COMOUT/.  
fi

if [ $SENDDBN = YES ] ; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.href.precip.last${last_days}days.v${VDATE}.tar
fi

