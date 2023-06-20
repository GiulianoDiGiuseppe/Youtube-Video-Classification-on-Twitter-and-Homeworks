#http://127.0.1.1:9870/dfshealth.html#tab-overview

import subprocess

subprocess.run("/home/parallels/hadoop/bin/hdfs namenode -format", shell = True)
subprocess.run("/home/parallels/hadoop/sbin/start-dfs.sh", shell = True)

