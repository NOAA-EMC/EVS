#!/bin/ksh

#Note: This script is to adjust CMCE members by adding the difference between GFS analysis and CMC analysis to
#each CMCE member.
 
set -x




if [ $RUN = atmos ] ; then
  leads='00 12 24 36 48 60 72 84 96 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384'
  vcycs="00 12" 
else
  leads='24 48 72 96  120 144 168 192 216 240 264 288 312 336 360 384'
  vcycs="00"
fi  

mkdir -p $WORK/naefs

 cd $WORK/naefs

for vcyc in $vcycs ; do 
 
   ln -sf ${COMIN}.${vday}/gefs/gfsanl.t${vcyc}z.grid3.f000.grib2 gfsanl
   ln -sf ${COMIN}.${vday}/cmce/cmcanl.t${vcyc}z.grid3.f000.grib2 cmcanl


 for lead in $leads ; do
   obsv_cyc=${vday}${vcyc}     #validation time: xxxx.tvcycz.f00
   fcst_time=`$NDATE -$lead $obsv_cyc`
   fyyyymmdd=${fcst_time:0:8}
   fcyc=${fcst_time:8:2}
  
   naefs_dir=$COMOUT_naefs.${fyyyymmdd}/naefs

   if [ ! -d $naefs_dir ] ; then
     mkdir -p $naefs_dir 
   fi 

   fhr=$lead
   typeset -Z3 fhr

   for mbr in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
     ln -sf  ${COMIN}.${fyyyymmdd}/gefs/gefs.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2  gefs.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2 
   done

   for mbr in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do
     ln -sf  ${COMIN}.${fyyyymmdd}/cmce/cmce.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2  cmce.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2
   done

   sed -e "s!CYC!$fcyc!g" -e "s!GRID!3!g" -e "s!FHR!$fhr!g" $ENS_LIST/evs_g2g_gefs_file_list > gefs_file_list.t${fcyc}z.f${fhr}
   sed -e "s!CYC!$fcyc!g" -e "s!GRID!3!g" -e "s!FHR!$fhr!g" $ENS_LIST/evs_g2g_cmce_file_list > cmce_file_list.t${fcyc}z.f${fhr}

   echo "gefs_file_list.t${fcyc}z.f${fhr}  cmce_file_list.t${fcyc}z.f${fhr}"|$EXECevs/evs_g2g_adjustCMC.x

   for mb in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 ; do
     mbr=$mb
     typeset -Z2 mbr
     ln -sf ${COMIN}.${fyyyymmdd}/gefs/gefs.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2  $naefs_dir/naefs.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2
   done
  
   for mb in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 ; do
     mbr=$mb
     typeset -Z2 mbr
     mbr50=$((mb+30))
     if [ -s cmce.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2.adj ] ; then
      mv cmce.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2.adj $naefs_dir/naefs.ens${mbr50}.t${fcyc}z.grid3.f${fhr}.grib2
     fi 
   done


 done
done

cd $WORK


