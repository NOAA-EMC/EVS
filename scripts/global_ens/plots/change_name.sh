#!/bin/ksh

set -x 
valid_time='valid00z_12z'
init_time='init00z_12z'

past_days=31

for domain in g003 nhem shem tropics conus ; do
   mv performance_diagram_regional_${domain}_valid_00z_12z_cape_f12_to_f384_ge250ge500ge1000ge2000.png  evs.global_ens.ctc.cape_l0.last31days.perfdiag_valid_00z_12z_f12_to_f384.${domain}.png

done

exit


for stats in  acc bias_mae crpss rmse_spread ets_fbias ; do
 for score_type in time_series lead_average ; do

  if [ $stats = ets_fbias ] ; then
    if [ $score_type = time_series ] ; then
      leads='_f120_ge250ge500ge1000ge2000.png _f240_ge250ge500ge1000ge2000.png _f360_ge250ge500ge1000ge2000.png'
      scoretype='timeseries'
    elif [ $score_type = lead_average ] ; then
      leads='_ge250ge500ge1000ge2000.png'
      scoretype='fhrmean'
    fi
    vars='cape'
  else

    if [ $score_type = time_series ] ; then
      leads='_f120.png _f240.png _f360.png'
      scoretype='timeseries' 
    elif [ $score_type = lead_average ] ; then
      leads='.png'
      scoretype='fhrmean'
    fi
    vars='prmsl tmp dpt ugrd vgrd rh'
  fi

  for lead in $leads ; do
    
    if [ $score_type = time_series ] ; then
	lead_time=_${lead:1:4}
    else
        lead_time=''
    fi

   for domain in g003 nhem shem tropics conus ; do

    for var in $vars ; do
      if [ $var = tmp ] || [ $var = dpt ] || [ $var = rh ]; then
	 levels='2m'
      elif [ $var = ugrd ] || [ $var = vgrd ] ; then
	 levels='10m'
      elif [ $var = prmsl ] || [ $var = cape ] ; then
	 levels='l0'
      fi

      for level in $levels ; do

         if [ $var = prmsl ] || [ $var = cape ] ; then

             mv ${score_type}_regional_${domain}_valid_00z_12z_${var}_${stats}${lead}  evs.global_ens.${stats}.${var}.${level}.last${past_days}days.${scoretype}_${valid_time}.${init_time}${lead_time}.${domain}_glb.png

         else
             mv ${score_type}_regional_${domain}_valid_00z_12z_${level}_${var}_${stats}${lead}  evs.global_ens.${stats}.${var}.${level}.last${past_days}days.${scoretype}_${valid_time}.${init_time}${lead_time}.${domain}_glb.png

        fi
               
      done #level

    done #var
   done  #domain
  done   #lead
 done    #score_type
done     #stats






