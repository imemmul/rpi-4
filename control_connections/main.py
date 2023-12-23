import paramiko
import time
import subprocess
import json
import re
from ping3 import ping, verbose_ping

config_path = "/usr/local/bin/config.json"

def load_json(config_path):
    with open(config_path, "r") as cf_file:
        config = json.load(cf_file)
    return config

def check_ssh_connections(host, port, username, password, connectors):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for c in connectors:
        try:
            client.connect(hostname=host, port=port, username=username, password=password)
            stdin, stdout, stderr = client.exec_command("ss -tunp | grep ':22 ' | grep ESTAB")
            active_connections = stdout.read().decode().strip()
            is_match = re.search(c, active_connections)
            if is_match:
                return True
            else:
                return False
        except Exception as e:
            print(f"Error connecting to GPU machine: {e}")
            return False
        finally:
            client.close()

def shutdown_gpu_machine(host, port, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=host, port=port, username=username, password=password)
        channel = client.get_transport().open_session()
        command = f"echo {password} | sudo -S shutdown -h now"
        stdin, stdout, stderr = client.exec_command(command)
        print("Shutdown command sent to GPU machine.")
    except Exception as e:
        print(f"Error sending shutdown command: {e}")
    finally:
        client.close()


config = load_json(config_path)

host = config['ip']
port = 22
username = config['username']
password = config['password']
connectors = config['connectors']

def device_is_online(device_ip):
    result = ping(device_ip)
    return result

check_interval = 10

while True:
    time.sleep(60 * check_interval)
    if device_is_online(host):
        if not check_ssh_connections(host, port, username, password, connectors):
            print(f"shutdown", flush=True)
            shutdown_gpu_machine(host, port, username, password)
        else:
            print("Device is online and connected.", flush=True)
    else:
        print(f"device is not online", flush=True)
        
