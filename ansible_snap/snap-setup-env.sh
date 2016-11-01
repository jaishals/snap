#!bin/bash
count=$(echo $PATH | grep -c "/opt/hadoop/default/bin")
if [ $count -eq 0 ]; then
 export PATH=:"$PATH:/opt/hadoop/default/bin"
fi
