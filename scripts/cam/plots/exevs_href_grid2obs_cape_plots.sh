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

model_list='HREF_MEAN'
models='HREF_MEAN'

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
  $USHevs/cam/evs_get_href_stat_file_link_plots.sh $day HREF_MEAN
  n=$((n+1))
done 

																  
export fcst_init_hour="0,6,12,18"
export fcst_valid_hour="0,3,6,9,12,15,18,21,24"

export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}

export fcst_init_hour="0,6,12,18"
export fcst_valid_hour="0,3,6,9,12,15,18,21"
valid_time='valid00z_03z_06z_09z_12z_15z_18z_21z'
init_time='init00z_06z_12z_18z'

verif_case=grid2obs

> run_all_poe.sh

for stats in csi fbias  ; do 

 stat_list=$stats
 line_tp='ctc'
 VARs='CAPEsfc MLCAPE'
 score_types='lead_average'
 threshs="250  500 1000 2000"

 for thresh in $threshs ; do 

  for score_type in $score_types ; do

   export fcst_leads="6,9,12,15,18,21,24,27,30,33,36,39,42,45,48"

   for lead in $fcst_leads ; do 

    for VAR in $VARs ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       if [ $VAR = CAPEsfc ]  ; then
          FCST_LEVEL_values="L0"
       elif [ $VAR = MLCAPE ] ; then
	  FCST_LEVEL_values="ML"
       fi 	  

       if [ $VAR = CAPEsfc ] || [ $VAR = MLCAPE ] ; then 
	   doms="dom1 dom2 dom3 dom4 dom5"
       fi 

       for dom in $doms ; do 

       if [ $VAR = CAPEsfc ] || [ $VAR = MLCAPE ] ; then

	 if [ $dom = dom1 ] ; then      
             VX_MASK_LIST="CONUS, CONUS_East, CONUS_West"
	 elif [ $dom = dom2 ] ; then
	      VX_MASK_LIST="CONUS_South, CONUS_Central,  Appalachia"
	 elif [ $dom = dom3 ] ; then
	      VX_MASK_LIST="DeepSouth, GreatBasin, Mezquital"
	 elif [ $dom = dom4 ] ; then
	      VX_MASK_LIST="MidAtlantic,  PacificNW"
	 elif [ $dom = dom4 ] ; then
              VX_MASK_LIST="Southeast, SPlains"
	 fi
       fi

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

        OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in $line_tp ; do 

         > run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh  

        verif_type=conus_sfc

        echo "export PLOT_TYPE=$score_type" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export field=${var}_${level}" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export met_ver=$met_v" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export eval_period=TEST" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh
        else
          echo "export date_type=VALID" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh
        fi


         echo "export var_name=$VAR" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh

         echo "export line_type=$line_type" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export interp=BILIN" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export score_py=$score_type" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh

         thresh_fcst=">=${thresh}"
	 thresh_obs=$thresh_fcst

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/cam/evs_href_plots_config.sh > run_py.${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh

         chmod +x  run_py.${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh

         echo "${DATA}/run_py.${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh" >> run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh

         chmod +x  run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh 
         echo "${DATA}/run_${stats}.${thresh}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh" >> run_all_poe.sh

      done #end of line_type

     done #end of FCST_LEVEL_value

    done #end of VAR

  done #end of fcst_lead

 done #end of dom 

 done #end of score_type

 done #end of thresh 

done #end of stats 

chmod +x run_all_poe.sh


if [ $run_mpi = yes ] ; then
  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
   mpiexec -np 80 -ppn 80 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
fi

cd $plot_dir

 	
for score_type in lead_average ; do

  for var in cape mlcape ; do
   if [ $var = cape ] ; then
       var_new=cape
       level=l0
       stats="csi fbias"
   elif [ $var = mlcape ] ; then
       var_new=mlcape
       level=ml
       stats="csi fbias"
   fi
   
   valid="valid_all_times"

  if [ $score_type = lead_average ] ; then
     scoretype=fhrmean
  fi 

  for stat in $stats ; do

    for domain in conus conus_east conus_west conus_south conus_central alaska appalachia cplains deepsouth greatbasin greatlakes mezquital midatlantic northatlantic nolains nrockies pacificnw pacificsw prairie southeast southwest splains nplains srockies ; do

     if [ $domain = alaska ] ; then
         new_domain=$domain
     else
         new_domain=buk_${domain}
     fi

          for thresh in ge250 ge500 ge1000 ge2000 ; do
           mv ${score_type}_regional_${domain}_valid_all_times_${var}_${stat}_${thresh}.png evs.href.${stat}.${var_new}_${level}.${thresh}.last${past_days}days.${scoretype}_${valid}.${new_domain}.png
          done

       done #domain
    done #stat
  done  #var
done    #score_type

tar -cvf evs.plots.href.grid2obs.cape.past${past_days}days.v${VDATE}.tar *.png

cp  evs.plots.href.grid2obs.cape.past${past_days}days.v${VDATE}.tar  $COMOUT/.  

















