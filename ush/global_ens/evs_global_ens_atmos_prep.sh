#!/bin/ksh
set -x 

>run_get_all_gens_atmos_poe.sh
>run_get_all_gens_apcp24h_poe.sh
>run_get_all_gens_snow24h_poe.sh
>run_get_all_gens_icec_poe.sh
>run_get_all_gens_sst24h_poe.sh

for model in gefs cmce ecme ; do 

  if [ $model = gefs ] ; then

   if [ $get_gefs = yes ] ; then	   
	    
     for cyc in 00 06 12 18 ; do
       for fhr_range in range1 range2 range3 range4 range5 range6 range7 range8 range9 range10 range11 range12 range13 range14 range15 range16; do	     

	>get_data_${model}_${cyc}_${fhr_range}.sh

	if [ $fhr_range = range1 ] ; then
	  fhr_beg=6
          fhr_end=24
        elif [ $fhr_range = range2 ] ; then
          fhr_beg=30
          fhr_end=48
        elif [ $fhr_range = range3 ] ; then
          fhr_beg=54
          fhr_end=72
	elif [ $fhr_range = range4 ] ; then
	  fhr_beg=78
	  fhr_end=96
	elif [ $fhr_range = range5 ] ; then
          fhr_beg=102
          fhr_end=120

        elif [ $fhr_range = range6 ] ; then
          fhr_beg=126
          fhr_end=144

        elif [ $fhr_range = range7 ] ; then
          fhr_beg=150
          fhr_end=168

        elif [ $fhr_range = range8 ] ; then
          fhr_beg=174
          fhr_end=192

        elif [ $fhr_range = range9 ] ; then
          fhr_beg=198
          fhr_end=216

        elif [ $fhr_range = range10 ] ; then
          fhr_beg=222
          fhr_end=240

        elif [ $fhr_range = range11 ] ; then
          fhr_beg=246
          fhr_end=264

        elif [ $fhr_range = range12 ] ; then
          fhr_beg=270
          fhr_end=288

        elif [ $fhr_range = range13 ] ; then
          fhr_beg=294
          fhr_end=312

        elif [ $fhr_range = range14 ] ; then
          fhr_beg=318
          fhr_end=336

        elif [ $fhr_range = range15 ] ; then
          fhr_beg=342
          fhr_end=360

        elif [ $fhr_range = range16 ] ; then
          fhr_beg=366
          fhr_end=384

        fi 

        echo "$USHevs/global_ens/evs_get_gens_atmos_data.sh $model $cyc $fhr_beg $fhr_end" >> get_data_${model}_${cyc}_${fhr_range}.sh

	chmod +x get_data_${model}_${cyc}_${fhr_range}.sh
        echo "${DATA}/get_data_${model}_${cyc}_${fhr_range}.sh" >> run_get_all_gens_atmos_poe.sh

      done	 
     done
   
     fi

     if [ $get_gefs_apcp06h = yes ] ; then
       for cyc in 00 06 12 18 ; do 

         >get_data_${model}_${cyc}_apcp06h.sh
 
         echo "$USHevs/global_ens/evs_get_gens_atmos_data.sh ${model}_apcp06h $cyc 0 384" >> get_data_${model}_${cyc}_apcp06h.sh
         chmod +x get_data_${model}_${cyc}_apcp06h.sh
         echo "${DATA}/get_data_${model}_${cyc}_apcp06h.sh" >> run_get_all_gens_atmos_poe.sh

       done
     fi

     if [ $get_gefs_apcp24h = yes ] ; then
       for cyc in 00 12 ; do

         >get_data_${model}_${cyc}_apcp24h.sh

         echo "$USHevs/global_ens/evs_get_gens_atmos_data.sh ${model}_apcp24h $cyc 0 384" >> get_data_${model}_${cyc}_apcp24h.sh
         chmod +x get_data_${model}_${cyc}_apcp24h.sh
         echo "${DATA}/get_data_${model}_${cyc}_apcp24h.sh" >> run_get_all_gens_apcp24h_poe.sh

       done	
     fi			

     if [ $get_gefs_snow24h = yes ] ; then
       for cyc in 00 12 ; do

        >get_data_${model}_${cyc}_snow24h.sh

        echo "$USHevs/global_ens/evs_get_gens_atmos_data.sh ${model}_snow24h $cyc 0 384" >> get_data_${model}_${cyc}_snow24h.sh
        chmod +x get_data_${model}_${cyc}_snow24h.sh
        echo "${DATA}/get_data_${model}_${cyc}_snow24h.sh" >> run_get_all_gens_snow24h_poe.sh

       done
     fi


     if [ $get_gefs_icec24h = yes ] ; then
           >get_data_${model}_icec.sh
           echo "$USHevs/global_ens/evs_get_gens_atmos_data.sh  gefs_icec24h" >> get_data_${model}_icec.sh
           #echo "$USHevs/global_ens/evs_get_gens_atmos_data.sh  gefs_icec7day" >> get_data_${model}_icec.sh
           chmod +x get_data_${model}_icec.sh
           echo "${DATA}/get_data_${model}_icec.sh" >> run_get_all_gens_icec_poe.sh
     fi

     if [ $get_gefs_sst24h = yes ] ; then
	   >get_data_${model}_sst24h.sh
           echo "$USHevs/global_ens/evs_get_gens_atmos_data.sh  gefs_sst24h" >> get_data_${model}_sst24h.sh
           chmod +x get_data_${model}_sst24h.sh
	   echo "${DATA}/get_data_${model}_sst24h.sh" >> run_get_all_gens_sst24h_poe.sh
     fi 

   elif [ $model = cmce ] ; then  

     if [ $get_cmce = yes ] ; then 

      for cyc in 00 12 ; do

       for fhr_range in range1 range2 range3 range4 range5 range6 range7 range8 ; do

	>get_data_${model}_${cyc}_${fhr_range}.sh

	 if [ $fhr_range = range1 ] ; then
           fhr_beg=12
	   fhr_end=48
         elif [ $fhr_range = range2 ] ; then
	   fhr_beg=60
	   fhr_end=96

        elif [ $fhr_range = range3 ] ; then
          fhr_beg=108
          fhr_end=144

        elif [ $fhr_range = range4 ] ; then
          fhr_beg=156
          fhr_end=192

        elif [ $fhr_range = range5 ] ; then
          fhr_beg=204
          fhr_end=240

        elif [ $fhr_range = range6 ] ; then
          fhr_beg=252
          fhr_end=288

        elif [ $fhr_range = range7 ] ; then
          fhr_beg=300
          fhr_end=336

        elif [ $fhr_range = range8 ] ; then
          fhr_beg=348
          fhr_end=384
	   	
         fi

         echo "$USHevs/global_ens/evs_get_gens_atmos_data.sh $model $cyc $fhr_beg $fhr_end" >> get_data_${model}_${cyc}_${fhr_range}.sh

         chmod +x get_data_${model}_${cyc}_${fhr_range}.sh
         echo "${DATA}/get_data_${model}_${cyc}_${fhr_range}.sh" >> run_get_all_gens_atmos_poe.sh

       done
      done

     fi 

     if [ $get_cmce_apcp06h = yes ] ; then
        for cyc in 00 12 ; do

          >get_data_${model}_${cyc}_apcp06h.sh

          echo "$USHevs/global_ens/evs_get_gens_atmos_data.sh ${model}_apcp06h $cyc 0 384" >> get_data_${model}_${cyc}_apcp06h.sh
          chmod +x get_data_${model}_${cyc}_apcp06h.sh
          echo "${DATA}/get_data_${model}_${cyc}_apcp06h.sh" >> run_get_all_gens_atmos_poe.sh

        done
     fi 

     if [ $get_cmce_apcp24h = yes ] ; then
        for cyc in 00 12 ; do

	  >get_data_${model}_${cyc}_apcp24h.sh

          echo "$USHevs/global_ens/evs_get_gens_atmos_data.sh ${model}_apcp24h $cyc 0 384" >> get_data_${model}_${cyc}_apcp24h.sh
          chmod +x get_data_${model}_${cyc}_apcp24h.sh
          echo "${DATA}/get_data_${model}_${cyc}_apcp24h.sh" >> run_get_all_gens_apcp24h_poe.sh

        done
     fi      


     if [ $get_cmce_snow24h = yes ] ; then
	for cyc in 00 12 ; do

          >get_data_${model}_${cyc}_snow24h.sh

          echo "$USHevs/global_ens/evs_get_gens_atmos_data.sh ${model}_snow24h $cyc 0 384" >> get_data_${model}_${cyc}_snow24h.sh
          chmod +x get_data_${model}_${cyc}_snow24h.sh
          echo "${DATA}/get_data_${model}_${cyc}_snow24h.sh" >> run_get_all_gens_snow24h_poe.sh

        done
     fi


   elif [ $model = ecme ] ; then

     if [ $get_ecme = yes ] ; then
       >get_data_${model}_atmos.sh
       echo "$USHevs/global_ens/evs_get_gens_atmos_data.sh $model " >> get_data_${model}_atmos.sh 
       chmod +x get_data_${model}_atmos.sh
       echo "${DATA}/get_data_${model}_atmos.sh" >> run_get_all_gens_atmos_poe.sh
       #already include get_ecme_apcp06h in this process
     fi

     if [ $get_ecme_apcp24h = yes ] ; then
      >get_data_${model}_apcp24h.sh
      echo "$USHevs/global_ens/evs_get_gens_atmos_data.sh ${model}_apcp24h" >> get_data_${model}_apcp24h.sh     
      chmod +x get_data_${model}_apcp24h.sh
      echo "${DATA}/get_data_${model}_apcp24h.sh" >> run_get_all_gens_apcp24h_poe.sh
     fi

     if [ $get_ecme_snow24h = yes ] ; then
       >get_data_${model}_snow24h.sh
       echo "$USHevs/global_ens/evs_get_gens_atmos_data.sh ${model}_snow24h" >> get_data_${model}_snow24h.sh
       chmod +x get_data_${model}_snow24h.sh
       echo "${DATA}/get_data_${model}_snow24h.sh" >> run_get_all_gens_snow24h_poe.sh
    fi


   else

    echo "$model =>  wrong model"
    exit

   fi

done #end of model


if [ $run_mpi = yes ] ; then

 if [ -s run_get_all_gens_atmos_poe.sh ] ; then
   chmod +x run_get_all_gens_atmos_poe.sh 
   mpiexec  -n 174 -ppn 174 --cpu-bind core --depth=2 cfp  ${DATA}/run_get_all_gens_atmos_poe.sh
 fi

 #Only after the above jobs are finished, following jobs can be run!

 if [ -s run_get_all_gens_apcp24h_poe.sh ] ; then
   chmod +x run_get_all_gens_apcp24h_poe.sh
   ${DATA}/run_get_all_gens_apcp24h_poe.sh
 fi

  if [ -s run_get_all_gens_snow24h_poe.sh ] ; then
    chmod +x run_get_all_gens_snow24h_poe.sh
    ${DATA}/run_get_all_gens_snow24h_poe.sh
  fi

  if [ -s run_get_all_gens_icec_poe.sh ] ; then
     chmod +x run_get_all_gens_icec_poe.sh
     ${DATA}/run_get_all_gens_icec_poe.sh
  fi     


    if [ -s run_get_all_gens_sst24h_poe.sh ] ; then
      chmod +x run_get_all_gens_sst24h_poe.sh
      ${DATA}/run_get_all_gens_sst24h_poe.sh
    fi

else

 if [ -s run_get_all_gens_atmos_poe.sh ] ; then
   chmod +x run_get_all_gens_atmos_poe.sh 
   ${DATA}/run_get_all_gens_atmos_poe.sh
 fi
 if [ -s run_get_all_gens_apcp24h_poe.sh ] ; then
   chmod +x run_get_all_gens_apcp24h_poe.sh
   ${DATA}/run_get_all_gens_apcp24h_poe.sh
 fi

 if [ -s run_get_all_gens_snow24h_poe.sh ] ; then
    chmod +x run_get_all_gens_snow24h_poe.sh
    ${DATA}/run_get_all_gens_snow24h_poe.sh
 fi

 if [ -s run_get_all_gens_icec_poe.sh ] ; then
    chmod +x run_get_all_gens_icec_poe.sh
    ${DATA}/run_get_all_gens_icec_poe.sh
 fi

 if [ -s run_get_all_gens_sst24h_poe.sh ] ; then
    chmod +x run_get_all_gens_sst24h_poe.sh
    ${DATA}/run_get_all_gens_sst24h_poe.sh
 fi

fi 

exit 


