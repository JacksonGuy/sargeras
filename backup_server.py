import socket
from _thread import *
import threading

HOST = "127.0.0.1"
PORT = 8081

def thread(c, addr):
    while True:
        try:
            command = input(">> ")
            c.send(command.encode())
            response = c.recv(1024).decode()
            print("[{address}] Response: \n{r}".format(address=addr[0], r=response))
        except:
            print("[{address}] Connection Closed".format(address=addr[0]))
            c.close()
            break

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST,PORT))

    s.listen(5)
    while True:
        c, addr = s.accept()
        print("[{address}] Established Connection".format(address=addr[0]))
        start_new_thread(thread, (c,addr,))
    s.close()

if __name__ == "__main__":
    main()
