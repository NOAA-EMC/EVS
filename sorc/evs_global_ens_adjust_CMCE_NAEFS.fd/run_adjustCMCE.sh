ln -sf gfsanl.t00z.grid3.f000.grib2 gfsanl
ln -sf cmcanl.t00z.grid3.f000.grib2 cmcanl 
echo "gefs_file_list.t00z.f240 cmce_file_list.t00z.f240"|../../exec/verf_g2g_adjustCMC.x 
