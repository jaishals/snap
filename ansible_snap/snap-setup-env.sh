#!bin/bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export HADOOP_PREFIX=/opt/hadoop/default
count=$(echo $PATH | grep -c "/opt/hadoop/default/bin")
if [ $count -eq 0 ]; then
 export PATH=:"$PATH:/opt/hadoop/default/bin"
fi
