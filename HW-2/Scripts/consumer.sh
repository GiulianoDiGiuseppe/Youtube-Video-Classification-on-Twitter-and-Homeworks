#!/bin/bash

name_topic="launchv5"
hdfs_log_file="/home/parallels/hadoop/logs/hadoop-parallels-namenode-ubuntu-linux-22-04-desktop.log"
command="/opt/kafka_2.11-0.9.0.0/bin/kafka-console-consumer.sh --zookeeper localhost:2181 --topic $name_topic --from-beginning >> $hdfs_log_file"

eval $command

#/opt/kafka_2.11-0.9.0.0/bin/kafka-console-consumer.sh --zookeeper localhost:2181 --topic launchv1 --from-beginning >> /home/parallels/hadoop/logs/hadoop-parallels-namenode-ubuntu-linux-22-04-desktop.log