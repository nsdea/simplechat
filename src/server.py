#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
import os
import socket
import random
import time

from threading import Thread
from typing import NoReturn

def send(client, text):
    client.send(bytes(text, 'utf8'))

def on_join_request():
    """Sets up handling for incoming clients."""
    
    while True:
        client, client_address = server.accept()
        print('%s:%s connected' % client_address)
        send(client, '[SYSTEM] Type your name to join the chat.')
        
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()

def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""
    
    name = client.recv(BUFFER_SIZE).decode('utf8').replace(' ', '_')
    if not name:
        name = f'Guest{random.randint(1000, 9999)}'
    
    send(client, f'>>> Welcome to the chat, @{name}!')
    broadcast(f'@{name} joined the chat!')
    clients[client] = name

    while True:
        msg = client.recv(BUFFER_SIZE)
        
        if msg != bytes('{quit}', 'utf8'):
            broadcast(msg, '@' + name)
        else:
            client.send(bytes('{quit}', 'utf8'))
            client.close()
            del clients[client]
            broadcast(f'{name} left the chat.')
            break

def broadcast(msg, prefix='[SERVER] '):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    
    # if isinstance(msg, str):
    #     msg = bytes(msg, 'utf8')

    for sock in clients:
        sock.send(bytes(f'[{prefix}] ', 'utf8') + msg)

clients = {}
addresses = {}

HOST = ''
PORT = 33000
BUFFER_SIZE = 1024

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server.bind((HOST, PORT))

except Exception as e:
    print('SERVER ERROR:', e)
    os.system('pkill -f python.exe')
    exit()

if __name__ == '__main__':
    server.listen(5)
    
    print('SERVER ONLINE')
    
    join_thread = Thread(target=on_join_request)
    join_thread.start()
    join_thread.join()
    server.close()
