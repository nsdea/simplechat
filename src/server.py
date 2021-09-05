#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
import os
import time
import socket
import random

from threading import Thread

def byte(text: str):
    return bytes(text, 'utf8')

def send(connection, text):
    connection.send(byte(text))

def receive(client):
    global BUFFER_SIZE
    
    time.sleep(0.1)
    try:
        return client.recv(BUFFER_SIZE).decode('utf8')
    except ConnectionResetError as e:
        broadcast(f'ERROR - Could not receive data: <{e}>')
        return ''

def on_join_request():
    """Sets up handling for incoming clients."""
    
    while True:
        connection, client_address = server.accept()
        print('%s:%s connected' % client_address)
        send(connection, '[SYSTEM] Type your name to join the chat.')
        
        addresses[connection] = client_address
        Thread(target=handle_client, args=(connection,)).start()

def handle_client(connection):  # Takes client socket as argument.
    """Handles a single client connection."""
    
    name = receive(connection).replace(' ', '_')
    if not name:
        name = f'Guest{random.randint(1000, 9999)}'

    send(connection, f'>>> Welcome to the chat, @{name}!')
    broadcast(f'@{name} joined the chat!')
    clients[connection] = name

    while True:
        msg = receive(connection)
        broadcast(msg, f'@{name}')

        if msg == 'quit':
            connection.send(byte('quit'))
            connection.close()
            del clients[connection]
            broadcast(f'{name} left the chat.')
            break
        
        elif msg == 'info':
            readable_clientlist = ''
            print(clients)

            for connection in clients.keys():
                info_str = str(connection)
                (ip, port) = info_str.split("laddr")[1]
                connection_info = f'{ip}:{port}'
                readable_clientlist += f'{connection_info}\t\t{clients[connection]}\n'

            broadcast(clients)

def broadcast(msg, prefix='SERVER'):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    
    if not isinstance(msg, bytes):
        msg = byte(str(msg))

    for client in clients:
        client.send(byte(f'[{prefix}] ') + msg)

clients = {}
addresses = {}

HOST = ''
PORT = 1183
BUFFER_SIZE = 1024

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server.bind((HOST, PORT))

except Exception as e:
    print('SERVER ERROR:', e)
    server.close()

if __name__ == '__main__':
    server.listen(5)
    
    print('SERVER ONLINE')
    
    join_thread = Thread(target=on_join_request)
    join_thread.start()
    join_thread.join()
    server.close()
