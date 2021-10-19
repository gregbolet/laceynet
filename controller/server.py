#!/usr/bin/python3

import socket

HOST = 'controller.laceynet'
PORT = 65432

def main():
    print("Hello from Controller!")

    # AF_INET is IPV4, SOCK_STREAM is for TCP protocol
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Associate the given HOST with the given PORT
        s.bind((HOST, PORT))

        # Make this a listening server
        s.listen()

        # Block and wait for an incoming connection
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            print('AKA: ', socket.gethostbyaddr(addr[0]))
            while True:
                # Blocking calls
                data = conn.recv(1024)

                # If no bytes are received, connection is closed
                #if not data:
                #    break

                # Send the data back to the client
                conn.sendall(data)

    return

main()
