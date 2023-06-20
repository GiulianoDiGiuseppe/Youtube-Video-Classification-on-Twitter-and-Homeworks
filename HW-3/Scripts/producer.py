#"/opt/kafka_2.11-0.9.0.0/bin/zookeeper-server-start.sh /opt/kafka_2.11-0.9.0.0/config/zookeeper.properties"
# "/opt/kafka_2.11-0.9.0.0/bin/kafka-server-start.sh /opt/kafka_2.11-0.9.0.0/config/server.properties"


import psutil
import subprocess
from time import sleep 
from datetime import  datetime

name_topic = "launchv5"

#,"/opt/kafka_2.11-0.9.0.0/bin/kafka-topics.sh --list --zookeeper localhost:2181"]

def connect(name_topic):
    cmds = ["cd /opt/kafka_2.11-0.9.0.0"
        ,"/opt/kafka_2.11-0.9.0.0/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic "+name_topic
    ]

    try:
        for cmd in cmds:
            result = subprocess.Popen(cmd, shell=True)
            print('Comando eseguito correttamente.')
            print('Err:\n', result.stderr)
        
    except subprocess.CalledProcessError as ex:
        print('Esecuzione fallita.')
        print('Err:', ex.stderr)


def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def get_stats():
    msg={}
    timestamp = datetime.now()
    formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    msg["timestamp"] = formatted_timestamp
    STRUMENT='CPU '
    msg[STRUMENT+'Physical cores']=psutil.cpu_count(logical=False)
    msg[STRUMENT+'Total cores']=psutil.cpu_count(logical=True)
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        msg[STRUMENT+'Core'+str(i)]= percentage

    STRUMENT='RAM '
    svmem = psutil.virtual_memory()
    msg[STRUMENT+'Total']=get_size(svmem.total)
    msg[STRUMENT+'Available']=get_size(svmem.available)
    msg[STRUMENT +'Used']=get_size(svmem.used)
    msg[STRUMENT +'Percentage']=svmem.percent
    swap = psutil.swap_memory()
    STRUMENT='RAM SWAP'
    msg[STRUMENT+'Total']=get_size(swap.total)
    msg[STRUMENT+'Free']=get_size(swap.free)
    msg[STRUMENT+'Used']=get_size(swap.used)
    msg[STRUMENT+'Percentage']=swap.percent
    STRUMENT=str('DISK  ')
    disk_io = psutil.disk_io_counters()
    msg[STRUMENT+'Total read']=get_size(disk_io.read_bytes)
    msg[STRUMENT+'Total write']=get_size(disk_io.write_bytes)

    return str(msg)

connect(name_topic=name_topic)
subprocess.run("cd /opt/kafka_2.11-0.9.0.0",shell=True)
i = 0
while(1):
    cmd_prod = "/opt/kafka_2.11-0.9.0.0/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic "+name_topic
    cmd_full = "echo "+ '\"'+name_topic+" "+get_stats()+'\" | ' + cmd_prod
    cmd_mess = subprocess.run(cmd_full, shell=True, capture_output=True, text=True)
    print(f"Message {i} sent")
    sleep(0.1)
    i+=1
    if i==5000:
        break 




