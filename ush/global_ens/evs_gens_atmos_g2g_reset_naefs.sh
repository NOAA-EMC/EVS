#!/bin/ksh
#************************************************************************************************************
# Purpose: Dynamically create NAEFS member files based on prep bias-corrected GEFS and CMCE members
#          for both NAEFS and headline grid2grid verification. The created NAEFS member files are stored in 
#          the working directory $WORK($DATA)/naefs
#
#    Note: 1. The CMCE members are adjusted by adding the difference between GFS analysis and CMC analysis to
#             each CMCE member. This work is done by the Fortran program in sorc/evs_g2g_adjustCMC.fd
#          2. For NAEFS 6, use 20 GEFS bias-corrected members, for NAEFS/v7, use GEFS 30 bias-corrected members
#
# Last update: 11/16/2023, by Binbin Zhou Lynker@EMC/NCEP
#
#************************************************************************************************************
 
set -x

if [ $RUN = atmos ] ; then
  leads='00 12  24 36 48 60 72 84 96 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384'
  vhours="00 12" 
else
  leads='24 48 72 96  120 144 168 192 216 240 264 288 312 336 360 384'
  vhours="00"
fi  

mkdir -p $WORK/naefs
cd $WORK/naefs

if [ $gefs_number = 20 ] ; then
  gefs_mbrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20"
elif [ $gefs_number = 30 ] ; then
  gefs_mbrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30"
fi
cmce_mbrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20"

for vhour in $vhours ; do

   if [ -s ${EVSIN}.${vday}/gefs/gfsanl.t${vhour}z.grid3.f000.grib2 ]; then
       ln -sf ${EVSIN}.${vday}/gefs/gfsanl.t${vhour}z.grid3.f000.grib2 gfsanl
   fi
   if [ -s ${EVSIN}.${vday}/cmce/cmcanl.t${vhour}z.grid3.f000.grib2 ]; then
       ln -sf ${EVSIN}.${vday}/cmce/cmcanl.t${vhour}z.grid3.f000.grib2 cmcanl
   fi

   for lead in $leads ; do
     obsv_time=${vday}${vhour}     #validation time: xxxx.tvhourz.f00
     fcst_time=`$NDATE -$lead $obsv_time`
     fyyyymmdd=${fcst_time:0:8}
     ihour=${fcst_time:8:2}
     fhr=$lead
     typeset -Z3 fhr

     for mbr in $gefs_mbrs ; do
       if [ $RUN = headline ] ; then
	 #****************************************************************************
         #Note: in headline.yyyymmdd/gefs, the files were from atmos.yyyymmdd/gefs_bc
	 #      So they are bias-corrected files
	 #****************************************************************************
         if [ -s ${EVSIN}.${fyyyymmdd}/gefs/gefs.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2 ]; then
           ln -sf  ${EVSIN}.${fyyyymmdd}/gefs/gefs.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2  gefs.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2
         fi
       else
         if [ -s ${EVSIN}.${fyyyymmdd}/gefs_bc/gefs_bc.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2 ]; then
           ln -sf  ${EVSIN}.${fyyyymmdd}/gefs_bc/gefs_bc.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2  gefs.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2
         fi
       fi
     done # gefs_mbrs

     for mbr in $cmce_mbrs ; do
       if [ $RUN = headline ] ; then
	 #*****************************************************************************      
         #Note: in headline.yyyymmdd/cmce, the files were from atmos.yyyymmdd/cmce_bc
	 #      So they are bias-corrected files
	 #****************************************************************************
         if [ -s ${EVSIN}.${fyyyymmdd}/cmce/cmce.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2 ]; then
           ln -sf  ${EVSIN}.${fyyyymmdd}/cmce/cmce.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2  cmce.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2
         fi
       else
         if [ -s ${EVSIN}.${fyyyymmdd}/cmce_bc/cmce_bc.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2 ]; then
           ln -sf  ${EVSIN}.${fyyyymmdd}/cmce_bc/cmce_bc.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2  cmce.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2
         fi
       fi
     done # cmce_mbrs

     #************************************************************************************
     # Run  Fortran program in sorc/evs_g2g_adjustCMC.fd to get the difference between
     #      GFS analysis and CMC analysis in each grid, and add it to each CMCE members
     #************************************************************************************      
     if [ $gefs_number = 20 ] ; then
       sed -e "s!IHR!$ihour!g" -e "s!GRID!3!g" -e "s!FHR!$fhr!g" $ENS_LIST/evs_g2g_gefs_file_list.20 > gefs_file_list.t${ihour}z.f${fhr}
     elif [  $gefs_number = 30 ] ; then
       sed -e "s!IHR!$ihour!g" -e "s!GRID!3!g" -e "s!FHR!$fhr!g" $ENS_LIST/evs_g2g_gefs_file_list.30 > gefs_file_list.t${ihour}z.f${fhr}
     fi
     sed -e "s!IHR!$ihour!g" -e "s!GRID!3!g" -e "s!FHR!$fhr!g" $ENS_LIST/evs_g2g_cmce_file_list > cmce_file_list.t${ihour}z.f${fhr}
     echo "gefs_file_list.t${ihour}z.f${fhr}  cmce_file_list.t${ihour}z.f${fhr}"|$EXECevs/evs_g2g_adjustCMC.x
     export err=$?; err_chk

     for mb in $gefs_mbrs ; do
       mbr=$mb
       typeset -Z2 mbr
       if [ -s gefs.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2 ]; then
         mv gefs.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2     naefs.ens${mbr}.${fyyyymmdd}.t${ihour}z.grid3.f${fhr}.grib2
       fi
     done # gefs_mbrs

     for mb in $cmce_mbrs ; do
       mbr=$mb
       typeset -Z2 mbr
       mbr50=$((mb+$gefs_number))
       if [ -s cmce.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2.adj ] ; then
         mv cmce.ens${mbr}.t${ihour}z.grid3.f${fhr}.grib2.adj naefs.ens${mbr50}.${fyyyymmdd}.t${ihour}z.grid3.f${fhr}.grib2
       fi
     done # cmce_mbrs

   done # leads

done #vhours

cd $WORK
