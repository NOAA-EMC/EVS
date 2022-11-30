#!/bin/sh

set -x 

cd $DATA

export prune_dir=$DATA/data
export save_dir=$DATA/out
export output_base_dir=$DATA/stat_archive
export log_metplus=$DATA/logs/NARRE_verif_plotting_job.out
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
  sh $USHevs/narre/evs_get_narre_stat_file_link.sh $day
  n=$((n+1))
done 

VX_MASK_LIST="G130 G214"

#fcst_init_hour=""
#fcst_valid_hour="0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23"
export fcst_valid_hour="0,3,6,9,12,15,18,21"
export fcst_lead="1,2,3,4,5,6,7,8,9,10,11,12"

export plot_dir=$DATA/out/ceil_vis/${valid_beg}-${valid_end}


> run_all_poe.sh 
for grid in $VX_MASK_LIST ; do

 #for score_type in performance_diagram  threshold_average time_series valid_hour_average lead_average ; do
 for score_type in performance_diagram ; do

  for var in VISsfc HGTcldceil ; do 

   #for line_type in ctc sl1l2 ; do 
   for line_type in ctc ; do 

    > run_narre_${grid}.${score_type}.${var}.${line_type}.sh 

     
    if [ $grid = G130 ] ; then
      echo "export mask=buk_conus" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
      echo "export grd=g130"
    elif [ $grid = G214 ] ; then
      echo "export mask=alaska" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
      echo "export grd=g214"
    fi

      echo "export PLOT_TYPE=$score_type" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh

    if [ $var = VISsfc ] ; then
      echo "export field=vis_l0" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
      echo "export vname=vis" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
    elif [ $var = HGTcldceil ] ; then
      echo "export field=ceiling_l0" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
      echo "export vname=hgt" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
    fi


     if [ $var = VISsfc  ] || [ $var = HGTcldceil ] || [ $var = TCDC ] ; then
      FCST_LEVEL_value="L0"
      OBS_LEVEL_value="L0"
     elif [ $var = TMP2m ] || [ $var = RH2m ] || [ $var = DPT2m ] ; then
      FCST_LEVEL_value="Z2"
      OBS_LEVEL_value="Z2"
     elif [ $var = UGRD10m ] || [ $var = VGRD10m ] ; then
      FCST_LEVEL_value="Z10"
      OBS_LEVEL_value="Z10"
     elif [ $var = CAPEsfc ] ; then
      FCST_LEVEL_value="L0"
      OBS_LEVEL_value="L100000-0"
     elif [ $var = PRMSL ] ; then
      FCST_LEVEL_value="Z0"
      OBS_LEVEL_value="Z0"
     fi

     if [ $line_type = ctc ] ; then
       if [ $score_type = performance_diagram ] ; then
         stat_list="sratio, pod, csi"
       else
         stat_list="csi"
       fi
     elif [ $line_type = sl1l2 ] ; then
       stat_list="rmse, bias"
     fi

     if [ $var = VISsfc  ] ; then
      thresh="<805,<1609,<4828,<8045,<16090"
     elif [ $var = HGTcldceil ] ; then
      thresh="<152,<305,<914,<1524,<3048"
     fi

     echo "export vx_mask_list=$grid" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     echo "export verif_case=grid2obs" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     echo "export verif_type=conus_sfc" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh

     echo "export log_level=INFO" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     echo "export met_ver=10.0" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     echo "export model=NARRE_MEAN" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh

     echo "export eval_period=TEST" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh

     if [ $score_type = valid_hour_average ] ; then
       echo "export date_type=INIT" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     else
       echo "export date_type=VALID" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     fi

     echo "export var_name=$var" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     echo "export fcts_level=$FCST_LEVEL_value" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     echo "export obs_level=$OBS_LEVEL_value" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh


     echo "export line_type=$line_type" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     echo "export interp=NEAREST" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     echo "export score_py=$score_type" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh

     sed -e "s!stat_list!$stat_list!g"  -e "s!thresh_list!$thresh!g" -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g"  $USHevs/narre/evs_narre_plots.sh > run_py.${var}_${line_type}.${score_type}.${grid}.sh

     chmod +x run_py.${var}_${line_type}.${score_type}.${grid}.sh

     echo "sh run_py.${var}_${line_type}.${score_type}.${grid}.sh" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
 

     #evs.component.metric1_metricX.parameter_level(_obtype).lastXXdays.plottype.grid_region.png
     #evs.global_det.acc.hgt_p500.last90days.timeseries_valid00z_f120.g004_glb.png
     #evs.cam_ens.ctc.vis_l0.last31days.perfdiag_f048.buk_conus.png
     if [ $score_type = performance_diagram ] ; then
        echo "mv ${plot_dir}/${score_type}_regional_*${grd}*_*${vname}*.png ${plot_dir}/evs.narre.ctc.${field}.last${past_days}days.perfdiag_f012.${mask}.png" >>  run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     fi 
     
     chmod +x  run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     echo "run_narre_${grid}.${score_type}.${var}.${line_type}.sh" >> run_all_poe.sh

    done #end of line_type

  done #end of var

 done #end of score_type

done #end of grid 

chmod +x run_all_poe.sh

if [ $run_mpi = yes ] ; then
  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
   mpiexec -np 4 -ppn 4 --cpu-bind verbose,depth cfp run_all_poe.sh
else
 sh run_all_poe.sh
fi

cd $plot_dir
  
tar -cvf plots_narre_grid2obs_v${VDATE}.tar *.png

cp plots_narre_grid2obs_v${VDATE}.tar  $COMOUT/.  





