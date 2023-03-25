import socket
import threading

HOST = "127.0.0.1"
PORT_MAIN = 8080
PORT_MODULE = 8082

def send(c, addr):
    while True:
        command = input(">> ")
        
        if (command == "close"):
            confirm = input("Are you sure? This will completely shutdown the program (Y/N) ")
            if (confirm == "Y" or command == "y"):
                c.send(command.encode())
            else:
                print("Aborting\n")
        else:
            c.send(command.encode())

def receive(c, addr):
    while True:
        response = c.recv(1024).decode()
        
        if (response != "" and response != None):
            if (response == "ping"):
                c.send("pong".encode())
            else:
                print("\n[{address}] Response: \n{r}".format(address=addr[0], r=response))

def module(c, addr):
    while True:
        data = c.recv(1024).decode()
        if (data != None and data != ""):
            print("\n[{address}] Module Message: \n{r}".format(address=addr[0], r=data))

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST,PORT_MAIN))

    s.listen(5)
    while True:
        c, addr = s.accept()
        print("\n[{address}] Established connection".format(address=addr[0]))
        
        input_thread = threading.Thread(target=send, args=(c, addr,))
        input_thread.start()
        receive_thread = threading.Thread(target=receive, args=(c, addr,))
        receive_thread.start()

    s.close()

def start_module():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT_MODULE))

    s.listen(10)
    while True:
        c, addr = s.accept()
        print("\n[{address}] Module Connected".format(address=addr[0]))
        mod = threading.Thread(target=module, args=(c,addr,))
        mod.start()
    s.close()

if __name__ == '__main__':
    master = threading.Thread(target=main)
    master.start()

    module_check_thread = threading.Thread(target=start_module)
    module_check_thread.start()
