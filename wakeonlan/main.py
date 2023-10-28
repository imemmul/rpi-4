import subprocess
import wakeonlan
from ping3 import ping, verbose_ping
import time
import subprocess
import json


config_path = "/usr/local/bin/config.json"
bash_script_path = "/usr/local/bin/machine.sh"


def ssh_connect(bash_script_path):
    try:
        subprocess.run(["bash", bash_script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running the Bash script: {e}")
    else:
        print("Bash script executed successfully.")

def load_json(config_path):
    with open(config_path, "r") as cf_file:
        config = json.load(cf_file)
    return config

def device_is_online(device_ip):
    result = ping(device_ip)
    return result


def main():
    config = load_json(config_path)
    target_device_ip = config['ip']
    target_device_mac = config['mac']
    sent_ping = False
    connected = False
    # Check if the target device is online
    while not connected:
        if sent_ping:
            print(f"Connecting to machine...\nThis may take couple minutes.")
        if device_is_online(target_device_ip) or sent_ping:
            while not connected:
                try:
                    ssh_connect("/home/emir_rpi4/dev/rpi-4/wakeonlan/machine.sh")
                    connected = True
                except Exception as e:
                    print(f"problem in ssh: {e}")
                time.sleep(10)
        else:
            print(f"The target device ({target_device_ip}) is currently offline.")

            # Ask the user if they want to wake up the target device
            user_input = input("Do you want to wake up the target device (Y/N)? ").strip().lower()

            if user_input == 'y':
                # Send a WoL magic packet to wake up the target device
                wakeonlan.send_magic_packet(target_device_mac)
                print(f"WoL packet sent to {target_device_ip} to wake it up.")
                sent_ping = True
            else:
                connected = True
                print("Connection to target device aborted.")

if __name__ == "__main__":
    main()
