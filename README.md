# sargeras
A simple framework for creating malware

## Purpose
Tyler William Warren has a severe World of Warcraft addiction and he needs to be stopped. 

---

## Structure
The client-side part of the malware spawn several subprocesses for functionality and reliability.

### Check
The check process simply ensures that the master process is always running

### Master
The master process is the glue that essentially holds everything together. It is in charge of server communication, managing modules,
and command execution.

### Modules
An important feature of Sargeras is that new scripts can be written independently from the framework and added on even after the malware is already running. This
allows us to update the malware remotely with new features and patches as needed. The master process launches these modules and checks periodically to make sure they are
still running.

### Backup Terminal
Just to be extra careful, the master process also launches a second barebones version of itself with only the command execution feature. This is meant so that, in
worst case scenarios, we can connect to the backup terminal running on the target's computer to fix any issues. This terminal also connected to a seperate server from
the master process and modules.

---

## Server
The server simply takes input from the user and sends the data over a socket to the target. The primary server has two sockets, 8080 and 8082. Port 8080 is used
for primary communication by the master process. Port 8082 is used for communication with modules.

### Backup Server
This is just a barebones verison of the primary server which communicates to the backup process on the target's computer over port 8081.

![diagram of malware structure](/diagram.png)
