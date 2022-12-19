

files=`ls *.ecf`
echo  $files

for ecf in $files ; do
 sed -e 's!/para!\/prod!g' $ecf > a
 mv a $ecf 
done


