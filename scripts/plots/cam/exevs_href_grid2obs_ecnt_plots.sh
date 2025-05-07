#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the href ecnt plotting python script
# Last updated: 
#                 01/10/2025, add MPMD, by Binbin Zhou Lynker@EMC/NCEP
#                 07/09/2024, add restart, by Binbin Zhou Lynker@EMC/NCEP
#                 05/30/2024, Binbin Zhou Lynker@EMC/NCEP
##******************************************************************************
set -x 

mkdir -p $DATA/scripts
cd $DATA/scripts

export machine=${machine:-"WCOSS2"}
export output_base_dir=$DATA/stat_archive
mkdir -p $output_base_dir

all_plots=$DATA/plots/all_plots
mkdir -p $all_plots
if [ $SENDCOM = YES ] ; then
 restart=$COMOUT/restart/$last_days/href_ecnt_plots
 if [ ! -d  $restart ] ; then
  mkdir -p $restart
 fi
fi
export eval_period='TEST'

export interp_pnts=''

export init_end=$VDATE
export valid_end=$VDATE

model_list='HREF'
models='HREF'

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
  hrs=$((n*24))
  day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
  echo $day
  $USHevs/cam/evs_get_href_stat_file_link_plots.sh $day "$model_list"
  export err=$?; err_chk
  n=$((n+1))
done 


VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central, Alaska, Appalachia, CPlains, DeepSouth, GreatBasin, GreatLakes, Mezquital, MidAtlantic, NorthAtlantic, NPlains, NRockies, PacificNW, PacificSW, Prairie, Southeast, Southwest, SPlains, SRockies"
																  
export fcst_init_hour="0,6,12,18"

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

       if [ $VAR = TMP2m ] ; then
	  new_var=tmp
       elif [ $VAR = DPT2m ] ; then
	  new_var=dpt
       elif [ $VAR = RH2m ] ; then
	  new_var=rh
       elif [ $VAR = UGRD10m  ] ; then
          new_var=ugrd
       elif [ $VAR = VGRD10m  ] ; then
          new_var=vgrd
       elif [ $VAR = WIND10m ] ; then
          new_var=wind
       elif [ $VAR = PRMSL ] ; then
          new_var=mslet
       elif [ $VAR = GUSTsfc ] ; then
          new_var=gust
       elif [ $VAR = HPBL ] ; then
          new_var=hpbl
       fi	  

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

	OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

        doms="dom1 dom2 dom3 dom4 dom5 dom6 dom7 dom8"

	for dom in $doms ; do

         if [ $dom = dom1 ] ; then
	    VX_MASK_LIST="CONUS, CONUS_East, CONUS_West" 
	    subregions="conus conus_east conus_west"
	  elif [ $dom = dom2 ] ; then
	    VX_MASK_LIST="CONUS_South, CONUS_Central, Alaska"
	    subregions="conus_south conus_central alaska"
          elif [ $dom = dom3 ] ; then
            VX_MASK_LIST="Appalachia, CPlains, DeepSouth"
            subregions="appalachia cplains deepsouth"	
	  elif [ $dom = dom4 ] ; then
            VX_MASK_LIST="GreatBasin, GreatLakes, Mezquital"
	    subregions="greatbasin greatlakes mezquital"
	  elif [ $dom = dom5 ] ; then
            VX_MASK_LIST="MidAtlantic, NorthAtlantic, NPlains"
            subregions="midatlantic northatlantic nplains"
          elif [ $dom = dom6 ] ; then
            VX_MASK_LIST="NRockies, PacificNW, PacificSW"
	    subregions="nrockies pacificnw pacificsw"
           elif [ $dom = dom7 ] ; then
	    VX_MASK_LIST="SRockies, Prairie, Southeast"
            subregions="srockies prairie southeast"
	   elif [ $dom = dom8 ] ; then
            VX_MASK_LIST="Southwest, SPlains"
            subregions="southwest splains"	    
	 fi

	 #****************
	 # Build sub-jobs
	 # **************
         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh  

      #***********************************************************************************************************************************
      #  Check if this sub-job has been completed in the previous run for restart
      if [ ! -e $restart/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.completed ] ; then
      #***********************************************************************************************************************************
     
	echo "#!/bin/ksh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh 
	echo "set -x" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh 
        verif_type=conus_sfc

        save_dir=$DATA/plots/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}
        plot_dir=$save_dir/sfc_upper/${valid_beg}-${valid_end}
        mkdir -p $plot_dir
        mkdir -p $save_dir/data

        echo "export save_dir=$save_dir" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh
	echo "export log_metplus=$save_dir/log_verif_plotting_job.out" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh
	echo "export prune_dir=$save_dir/data" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh


        echo "export PLOT_TYPE=lead_average_valid" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh

        echo "export field=${var}_${level}" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh

        echo "export eval_period=TEST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh
        else
          echo "export date_type=VALID" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh
        fi


         echo "export var_name=$VAR" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh

         echo "export line_type=$line_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh
         echo "export interp=BILIN" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh
         echo "export score_py=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh

         thresh_fcst=' '
	 thresh_obs=' '

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/cam/evs_href_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh

         echo "${DATA}/scripts/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh

         #Save for restart and tar files
	 echo "for domain in $subregions ; do "  >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh
	 echo "if [ -s ${plot_dir}/${score_type}_regional_\${domain}_valid_${fcst_valid_hour}z_*${new_var}_${stats}.png ] ; then" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh
	 echo " cp -v ${plot_dir}/${score_type}_regional_\${domain}_valid_${fcst_valid_hour}z_*${new_var}_${stats}.png $all_plots" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh
	 echo " echo completed >${plot_dir}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.completed" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh 

	 #Copy files to restart directory
	 echo " if [ $SENDCOM = YES ] ; then" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh
	 echo "  cp -v ${plot_dir}/${score_type}_regional_\${domain}_valid_${fcst_valid_hour}z_*${new_var}_${stats}.png $restart" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh
	 echo "  cp -v ${plot_dir}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.completed $restart" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh 
	 echo " fi" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh
	 echo "fi" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh
         echo "done" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh

         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh 
         echo "${DATA}/scripts/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${fcst_valid_hour}.${dom}.sh" >> run_all_poe.sh

       else
	 for domain in $subregions ; do
           if [ -s $restart/${score_type}_regional_${domain}_valid_${fcst_valid_hour}z_*${new_var}_${stats}.png ] ; then
	     cp -v $restart/${score_type}_regional_${domain}_valid_${fcst_valid_hour}z_*${new_var}_${stats}.png $all_plots 
           fi
         done	   
       fi 

      done #end of dom 

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
mpiexec -np 66 -ppn 66 --cpu-bind verbose,depth cfp ${DATA}/scripts/run_all_poe.sh
export err=$?; err_chk

#**************************************************
# Change plot file names to meet the EVS standard
#**************************************************
cd $all_plots

for valid in 00z 03z 06z 09z 12z 15z 18z 21z ; do
for stats in  rmse_spread ; do
 for score_type in lead_average ; do

  scoretype=fhrmean
  vars='prmsl tmp dpt ugrd vgrd rh wind gust mslet hpbl'

   for domain in conus conus_east conus_west conus_south conus_central alaska appalachia cplains deepsouth greatbasin greatlakes mezquital midatlantic northatlantic nrockies pacificnw pacificsw prairie southeast southwest splains nplains srockies ; do

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
     elif [ $domain = appalachia ] ; then
	 new_domain=buk_apl
     elif [ $domain = cplains  ] ; then
         new_domain=buk_cpl
     elif [ $domain = deepsouth  ] ; then	
         new_domain=buk_ds
     elif [ $domain = greatbasin ] ; then
         new_domain=buk_grb	     
     elif [ $domain = greatlakes ] ; then
         new_domain=buk_grlk	     
     elif [ $domain = mezquital ] ; then
         new_domain=buk_mez	     
     elif [ $domain = midatlantic ] ; then
         new_domain=buk_matl	     
     elif [ $domain = northatlantic ] ; then
         new_domain=buk_ne	     
     elif [ $domain = nrockies ] ; then
         new_domain=buk_nrk	     
     elif [ $domain = pacificnw ] ; then
         new_domain=buk_npw	     
     elif [ $domain = pacificsw ] ; then
         new_domain=buk_psw	     
     elif [ $domain = prairie ] ; then
         new_domain=buk_pra	     
     elif [ $domain = southeast ] ; then
         new_domain=buk_se	     
     elif [ $domain = southwest ] ; then
         new_domain=buk_sw	     
     elif [ $domain = splains ] ; then
         new_domain=buk_spl	     
     elif [ $domain = nplains ] ; then
	 new_domain=buk_npl
     elif [ $domain = srockies ] ; then
         new_domain=buk_srk	     
     fi
    for var in $vars ; do

      if [ $var = mslet ] ; then
	  var_new=prmsl
      else
	  var_new=$var
      fi

      if [ $var = tmp ] || [ $var = dpt ] || [ $var = rh ]; then
	 level='2m'
	 new_level='z2'
      elif [ $var = ugrd ] || [ $var = vgrd ] || [ $var = wind ] ; then
	 level='10m'
	 new_level='z10'
      elif [ $var = mslet ] || [ $var = gust ] || [ $var = hpbl ] ; then
	 level='l0'
      fi


      if [ $var = mslet ] || [ $var = gust ] || [  $var = hpbl ] ; then
	if [ -s ${score_type}_regional_${domain}_valid_${valid}_${var}_${stats}.png ] ; then
          mv ${score_type}_regional_${domain}_valid_${valid}_${var}_${stats}.png  evs.href.${stats}.${var}_${level}.last${last_days}days.${scoretype}_valid${valid}.${new_domain}.png
        fi 
      else
	if [ -s ${score_type}_regional_${domain}_valid_${valid}_${level}_${var}_${stats}.png ] ; then
          mv ${score_type}_regional_${domain}_valid_${valid}_${level}_${var}_${stats}.png  evs.href.${stats}.${var}_${new_level}.last${last_days}days.${scoretype}_valid${valid}.${new_domain}.png
        fi
      fi

     done #var
   done  #domain
 done    #score_type
done     #stats
done     #valid 

if [ -s evs*.png ] ; then
 tar -cvf evs.plots.href.grid2obs.ecnt.last${last_days}days.v${VDATE}.tar evs*.png
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

if [ $SENDCOM = YES ] && [ -s evs.plots.href.grid2obs.ecnt.last${last_days}days.v${VDATE}.tar ] ; then
 cp -v evs.plots.href.grid2obs.ecnt.last${last_days}days.v${VDATE}.tar  $COMOUT/.  
fi

if [ $SENDDBN = YES ] ; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.href.grid2obs.ecnt.last${last_days}days.v${VDATE}.tar
fi  







