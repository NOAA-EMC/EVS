#!/bin/bash
source /u/ho-chun.huang/versions/run.ver
#
ls global_ens_chem* > tlist
count=0
while read line
do
  shfile[$count]=$(echo $line | awk '{print $1}')
  ((count++))
done<tlist

old_ver='mallory.row'
new_ver='ho-chun.huang'
old_ver='Mallory Row'
new_ver='Ho-Chun Huang'
for i in "${shfile[@]}"
do
   echo ${i}
   if [ "${i}" == $0 ]; then continue; fi
   if [ "${i}" == "xtest1" ]; then continue; fi
   if [ -d ${i} ]; then continue; fi
   ## mv ${i}.bak ${i}
   if [ -e xtest1 ]; then /bin/rm -f xtest1; fi
   grep "${old_ver}" ${i} > xtest1
   if [ -s xtest1 ]; then
      mv ${i} ${i}.bak
      sed -e "s!${old_ver}!${new_ver}!" ${i}.bak > ${i}
      ## awk '!/SHELL=\/bin\/bash/' ${i}.bak > ${i}
      ## echo "diff ${i} ${i}.bak"
      chmod u+x ${i}
      diff ${i} ${i}.bak
   fi
done
/bin/rm xtest1 tlist
##
## delete a block of line
##
## old_beg="if cdate_beg == cdate_end:$"
## old_end="   figure_date = header_date$"
## sed "/${old_beg}/,/${old_end}/d" ${i}.bak > ${i}

exit
