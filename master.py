import os
import psutil
import socket
import subprocess
import threading
import setproctitle
from time import sleep
import platform

setproctitle.setproctitle("master")

opsys = platform.system()

HOST = "127.0.0.1"
PORT = 8080

s = socket.socket()

process_run = True
connected = False

# List of modules to check for
# We start out with the backup terminal included
module_list = ["backup"]

def kill_process(name):
    global opsys
    for proc in psutil.process_iter():
        if (opsys == "Linux"):
            if proc.name() == name:
                proc.kill()
                return True
        elif (opsys == "Windows"):
            if proc.name() == (name + ".exe"):
                proc.kill()
                return True
    return False

def ping():
    global process_run
    global connected
    print("[Ping] Starting ping thread")
    while True and process_run:
        if connected:
            try:
                s.send("ping".encode())
                sleep(5)
            except BrokenPipeError:
                # Failed to send message because socket connection broke
                print("[Ping] Disconnected from Server: Server Offline")
                connected = False
                process_run = False

# Makes sure that the check process is always running
def check():
    print("[Master] Starting check thread")
    while True and process_run:
        sleep(3)
        running = False
        
        # Iterate over running processes and look for the check process
        for proc in psutil.process_iter():
            process = proc.as_dict(attrs=['name', 'pid'])
            if (process['name'] == 'check'):
                running = True
                break

        # Check processes not running, relaunch it
        if (running == False):
            try:
                result = subprocess.Popen(
                    "python3 check.py",
                    shell=True,
                    text=True,
                    universal_newlines=True,
                    start_new_session=True
                )
                print("[Master] Relauched check process")
            except subprocess.CalledProcessError as exc:
                print(exc.output)

# Auto checks that module processes are still running
def modules():
    # Load modules from module directory
    for filename in os.listdir("./modules/"):
        if (filename not in module_list):
            # Name of the script without .py
            module_list.append(filename[:len(filename)-3])

    print("[Master] Starting modules thread")
    while True and process_run:
        sleep(10)
        for m in module_list:
            # Assume mpdule isn't running and search process list for module
            running = False
            for proc in psutil.process_iter():
                process = proc.as_dict(attrs=['name', 'pid'])
                if (process['name'] == m):
                    # Module is running
                    running = True
                    break
            # Module not running, start it
            if (running == False):
                try:
                    result = subprocess.Popen(
                        "python3 " + m + ".py",
                        shell=True,
                        text=True,
                        universal_newlines=True,
                        start_new_session=True
                    )
                    print("[Master] Relauched module: " + m)
                except subprocess.CalledProcessError as exc:
                    s.send(exc.output.encode())

def comms():
    global process_run
    global connected
    print("[Master] Starting comms thread")

    # Start ping thread
    ping_thread = threading.Thread(target=ping)
    ping_thread.start()

    while (connected == False):
        try:
            s.connect((HOST,PORT))
            print("[Master] Successfully Connected to Server")
            connected = True
        except ConnectionRefusedError:
            print("[Master] Connection failed, retrying")
            sleep(5)
    while process_run and connected:
        data = ""
        s.settimeout(10)
        data = s.recv(1024).decode()
        
        if (data != "" and data != "pong"):
            print("[Master] Server: " + data)
            
            tokens = data.split()
            if (data == "restart"):
                run = False
                process_run = False
                break
            if (data == "close"):
                kill_process("check")
                for mod in module_list:
                    module_list.remove(mod)
                    kill_process(mod)
                s.send("Killed all remote processes.".encode())
                kill_process("master")
            elif (tokens[0] == "addmod"):
                # Add module to program
                name = tokens[1]
                if (name not in module_list):
                    module_list.append(name)
                    try:
                        result = subprocess.Popen(
                            "python3 " + tokens[1] + ".py",
                            shell=True,
                            text=True,
                            universal_newlines=True,
                            start_new_session=True
                        )
                        s.send("Success".encode())
                    except subprocess.CalledProcessError as exc:
                        s.send(exc.output.encode())
                else:
                    s.send("Failed to add module: module already exists.".encode())
            elif (tokens[0] == "removemod"):
                # Remove module from program
                name = tokens[1]
                if (name in module_list):
                    module_list.remove(name)
                    kill_process(name)
                    s.send("Success".encode())
                else:
                    s.send("Failed to remove modeule: module does not exist".encode())
            else:
                # Normal console command
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
                    if (result == None and result == ""):
                        s.send("Success".encode())
                    else:
                        s.send(result.encode())
    s.close()
    
if __name__ == "__main__":
    comms = threading.Thread(target=comms)
    comms.start()

    check = threading.Thread(target=check)
    check.start()

    modules = threading.Thread(target=modules)
    modules.start()
