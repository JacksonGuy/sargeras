import socket
from _thread import *
import threading

HOST = "127.0.0.1"
PORT = 8081

def send(c, addr):
    while True:
        command = input(">> ")
        c.send(command.encode())

def receive(c, addr):
    while True:
        response = c.recv(1024).decode()
        if (response != "" and response != None):
            if (response == "ping"):
                c.send("pong".encode())
            else:
                print("\n[{address}] Response: \n{r}".format(address=addr[0], r=response))

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST,PORT))

    s.listen(5)
    while True:
        c, addr = s.accept()
        print("[{address}] Established Connection".format(address=addr[0]))
    
        send_thread = threading.Thread(target=send, args=(c, addr,))
        send_thread.start()

        recv_thread = threading.Thread(target=receive, args=(c, addr,))
        recv_thread.start()

    s.close()

if __name__ == "__main__":
    main()
