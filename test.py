import os 
import setproctitle
from time import sleep
import socket

setproctitle.setproctitle("test")

HOST = "127.0.0.1"
PORT = 8082

s = socket.socket()

connected = False
while (connected == False):
    try:
        s.connect((HOST,PORT))
        print("[Module] Successfully connected to server")
        connected = True
    except ConnectionRefusedError:
        print("[Module] Connected failed, retrying")
        sleep(5)

while True:
    s.send("This is a test".encode())
    sleep(5)
