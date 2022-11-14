
files=`ls *.conf`

for conf in $files ; do 
  sed -e "s!G004_!G003_!g" $conf > a
  mv a $conf
done

 
