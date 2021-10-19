#!/usr/bin/python3

import socket

HOST = 'controller.laceynet'
PORT = 65432

def main():
    print("Hello from Worker!")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b'Hello, world')
        data = s.recv(1024)
        print('Received', repr(data))

    return

main()
