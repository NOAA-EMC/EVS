#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the refs cape plotting python script
# Last updated: 05/30/2024, Binbin Zhou Lynker@EMC/NCEP
#******************************************************************************
set -x 

cd $DATA

export machine=${machine:-"WCOSS2"}
export output_base_dir=$DATA/stat_archive
export CONFIG=${PARMevs}/evs_config/cam

export working=$DATA/output
mkdir -p $working

export METDATAIO_BASE=/apps/ops/para/libs/intel/19.1.3.304/METdataio/3.0.0-beta4/METdataio
export METCALCPY_BASE=/apps/ops/para/libs/intel/19.1.3.304/METcalcpy/3.0.0-beta4
export METPLOTPY_BASE=/apps/ops/para/libs/intel/19.1.3.304/METplotpy/3.0.0-beta4
PYTHONPATH=$METDATAIO_BASE:$METDATAIO_BASE/METdbLoad:$METDATAIO_BASE/METdbLoad/ush:$METDATAIO_BASE/METreformat:$METCALCPY_BASE:$METCALCPY_BASE/metcalcpy:$METPLOTPY_BASE:$METPLOTPY_BASE/metplotpy:$METPLOTPY_BASE/metplotpy/plots

stat_header="VERSION MODEL     DESC            FCST_LEAD FCST_VALID_BEG  FCST_VALID_END  OBS_LEAD OBS_VALID_BEG   OBS_VALID_END   FCST_VAR             FCST_UNITS FCST_LEV OBS_VAR OBS_UNITS OBS_LEV OBTYPE VX_MASK           INTERP_MTHD INTERP_PNTS FCST_THRESH OBS_THRESH COV_THRESH ALPHA LINE_TYPE" 

restart=$COMOUT/restart/$past_days/refs_precip_plots
if [ ! -d  $restart ] ; then
  mkdir -p $restart
fi     

export init_end=$VDATE
export valid_end=$VDATE

model_list='REFS_PROB REFS_EAS'
models='REFS_PROB, REFS_EAS'

VX_MASK_LISTs='CONUS CONUS_East CONUS_West CONUS_South CONUS_Central Alaska'
fcst_valid_hours='00 03 06 09 12 15 18 21'


n=0
while [ $n -le $past_days ] ; do
    hrs=$((n*24))
    first_day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
    n=$((n+1))
done

export init_beg=$first_day
export valid_beg=$first_day

#*************************************************************
# Virtual link the refs's stat data files of past 31/90 days
#*************************************************************
n=0
vdays=""
while [ $n -le $past_days ] ; do
  hrs=$((n*24))
  day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
  vdays="$vdays  $day"
   $USHevs/cam/evs_get_refs_stat_file_link_plots.sh $day "$model_list"
  n=$((n+1))
done 


echo vdays=$vdays

##############################################################################################
#
#STEP 1: Split the big stat files into split stat files based on REGIONs and validation hours
#STEP 2: Run METDATAIO to reformat the split stat files
#STEP 3: Run METCALCPY to aggregate the split stat files
#STEP 4: RUN METPLOTPY to genetate reliability diagram
#
#############################################################################################
metdataio_input_dir=$working/metdataio_input_dir
mkdir -p $metdataio_input_dir
metdataio_output_dir=$working/metdataio_output
mkdir -p $metdataio_output_dir 
log_dir_metdataio=$DATA/log_metdataio
mkdir -p $log_dir_metdataio

metcalcpy_input_dir=$metdataio_output_dir
metcalcpy_output_dir=$working/metcalcpy_output
mkdir -p $metcalcpy_output_dir

metplotpy_input_dir=$metcalcpy_output_dir
metplotpy_output_dir=$working/metplotpy_output
mkdir -p $metplotpy_output_dir

#
#metcalcpy input and output filenames depend on $REGION and $valid
#metcalcpy has no log file
#

#****************************************************************
#STEP 1: Split stat files into different regions and valid times
#****************************************************************
for REGION in $VX_MASK_LISTs ; do
  for valid in $fcst_valid_hours ; do

    metdataio_input_split=$metdataio_input_dir/${REGION}_${valid}
    mkdir -p $metdataio_input_split

    for MODEL in $model_list ; do

     model=`echo $MODEL | tr '[A-Z]' '[a-z]'`

     for vday in $vdays ; do
        big_stat=$DATA/stat_archive/${model}/${MODEL}_${vday}.stat
	if [ -s $big_stat ] ; then
	  >$metdataio_input_split/${MODEL}_${vday}.stat
	  echo "$stat_header" >> $metdataio_input_split/${MODEL}_${vday}.stat
	  grep " $REGION " $big_stat|grep "${vday}_${valid}0000 PROB" >> $metdataio_input_split/${MODEL}_${vday}.stat
	fi
     done
   done
 done
done   

#export plot_dir=$DATA/out/precip/${valid_beg}-${valid_end}
#For restart:
#if [ ! -d $plot_dir ] ; then
#  mkdir -p $plot_dir
#fi

#**********************************************************
#STEP 2: Run METDATAIO to reformat the original stat files
#Run metdataio to reformat the stat files
#**********************************************************
if [ $run_metdataio = yes ] ; then
for REGION in $VX_MASK_LISTs ; do
  for valid in $fcst_valid_hours ; do
	  
  metdataio_output_filename=reformatted_reliability_refs.${REGION}.${valid}.txt
  metdataio_log_filename=log.metdataio.${REGION}.${valid}

sed -e "s!OUTPUT_DIR!$metdataio_output_dir!g" -e "s!OUTPUT_FILENAME!$metdataio_output_filename!g" -e "s!INPUT_STAT_DIR!${metdataio_input_dir}/${REGION}_${valid}!g" -e "s!LOG_DIR!$log_dir_metdataio!g" -e "s!LOG_FILENAME!$metdataio_log_filename!g"  $CONFIG/config.refs.reliability.metdataio.yaml > ${metdataio_output_dir}/reliability_metdataio.${REGION}.${valid}.yaml

   python  $METDATAIO_BASE/METreformat/write_stat_ascii.py ${metdataio_output_dir}/reliability_metdataio.${REGION}.${valid}.yaml
 
 done
done

fi 

#*************************************************************************
# STEP 3: Run METCALCPY and METPLOTPY to aggregate data and generate plot
#         for each reformatted txt file
# ************************************************************************
>run_all_poe.sh
for REGION in $VX_MASK_LISTs ; do

     domain=`echo $REGION | tr '[A-Z]' '[a-z]'`
     if [ $domain = alaska ] ; then
	bukovski=buk_$domain
     else
	bukovski=$domain
     fi

   for VAR in APCP_01 APCP_03 APCP_24'
 
    var=`echo $VAR | tr '[A-Z]' '[a-z]'`
 
    if [ $VAR = APCP_24 ] ; then
	 fcst_valid_hours=12
    else
         fcst_valid_hours='00 03 06 09 12 15 18 21'
    fi

    for valid in $fcst_valid_hours ; do

      for thresh in 12.700 25.400 50.800 76.200 ; do 

       #***************
       # Build sub-jobs
       # ***************
       >run_${REGION}.${valid}.${VAR}.${thresh}.sh  

       #***********************************************************************************************************************************
       #  Check if this sub-job has been completed in the previous run for restart
       #if [ ! -e run_${VAR}.${thresh}.${VX_MASK_LIST}.${fcst_valid_hour}.completed ] ; then
       #***********************************************************************************************************************************
       
       input_metcalcpy_filename=${metcalcpy_input_dir}/reformatted_reliability_refs.${REGION}.${valid}.txt
       output_metcalcpy_filename=${metcalcpy_output_dir}/reliability_${VAR}.gt.${thresh}_pct_agg_stat.${REGION}.${valid}.txt
       sed -e "s!INPUT_FILENAME!$input_metcalcpy_filename!g" -e "s!OUTPUT_FILENAME!$output_metcalcpy_filename!g" -e "s!VAR!$VAR!g" -e "s!THRESHOLD!$thresh!g" -e "s!MODEL!REFS_PROB!g" $CONFIG/config.refs.reliability.metcalcpy.yaml >  ${metcalcpy_output_dir}/reliability_metcalcpy.${REGION}.${valid}.${VAR}.${thresh}.yaml

       echo "if [ -s $input_metcalcpy_filename ] ; then" >> run_${REGION}.${valid}.${VAR}.${thresh}.sh
       echo "  python  $METCALCPY_BASE/metcalcpy/agg_stat.py  ${metcalcpy_output_dir}/reliability_metcalcpy.${REGION}.${valid}.${VAR}.${thresh}.yaml"  >> run_${REGION}.${valid}.${VAR}.${thresh}.sh 
       echo "fi"  >> run_${REGION}.${valid}.${VAR}.${thresh}.sh

       input_metplotcpy_filename=$output_metcalcpy_filename
       output_metplotpy_filename=${metplotpy_output_dir}/evs.refs_gt${thresh}.reliability.${var}.past${past_days}days.perfdiag_valid_${valid}.${bukovski}.png
       sed -e "s!INPUT_FILENAME!$input_metplotcpy_filename!g" -e "s!OUTPUT_FILENAME!$output_metplotpy_filename!g" -e "s!VAR!$VAR!g" -e "s!THRESHOLD!$thresh!g" -e "s!REGION!$REGION!g" -e "s!VALIDBEG!$velid_beg!g" -e "s!VALIDEND!$valid_end!g"  $CONFIG/config.refs.reliability.metplotpy.yaml >  ${metplotpy_output_dir}/reliability_metplotpy.${REGION}.${valid}.${VAR}.${thresh}.yaml

       echo "if [ -s $input_metplotcpy_filename ] ; then" >> run_${REGION}.${valid}.${VAR}.${thresh}.sh
       echo "  python  $METPLOTPY_BASE/metplotpy/plots/reliability_diagram/reliability.py ${metplotpy_output_dir}/reliability_metplotpy.${REGION}.${valid}.${VAR}.${thresh}.yaml" >> run_${REGION}.${valid}.${VAR}.${thresh}.sh
       echo "fi" >> run_${REGION}.${valid}.${VAR}.${thresh}.sh	 

       chmod +x run_${REGION}.${valid}.${VAR}.${thresh}.sh
       echo "$DATA/run_${REGION}.${valid}.${VAR}.${thresh}.sh" >> run_all_poe.sh
    done
  done

 done
done

chmod +x run_all_poe.sh
#***************************************************************************
# Run the POE script in parallel or in sequence order to generate png files
#**************************************************************************
if [ $run_mpi = yes ] ; then   
  mpiexec -np 576 -ppn 72 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  $DATA/run_all_poe.sh	
fi










