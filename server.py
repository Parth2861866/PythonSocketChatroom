"""
Chat Room Server
"""

import socket
import threading
import time


def broadcast(message, sender=None):
    for c in clients:
        if c is not sender:
            c.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                raise ConnectionError
            # do NOT echo back to the sender
            broadcast(message, sender=client)
        except:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames.pop(index)
                # This goes to everyone else
                broadcast(f"{nickname} left the chat!".encode('utf-8'))
            break

def receive():
    first_accept = True
    while True:
        try:
            if first_accept:
                server.settimeout(10)  # only for first connection
                print("Waiting for connection (10s timeout)...")
            else:
                server.settimeout(None)  # normal blocking afterwards
                print("Waiting for connection...")

            client, address = server.accept()
            print(f"Connected with {str(address)}")

            # Once we have at least one client, stop using a timeout
            first_accept = False
            server.settimeout(None)

            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            nicknames.append(nickname)
            clients.append(client)

            print(f"Nickname of the client is {nickname}")
            broadcast(f"{nickname} joined the chat!".encode('utf-8'))
            client.send('Connected to the server!'.encode('utf-8'))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()

        except socket.timeout:
            print("No connections within 10 seconds, shutting down server.")
            break


#host = input("Enter host (default 'localhost'): ")

host = '127.0.0.1'
port = 59000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
print(f"Server started on {host}:{port}")
clients = []
nicknames = []

print("Server will timeout in 10sec...\n")
receive()
print("Server is shutting down...")
server.close()

