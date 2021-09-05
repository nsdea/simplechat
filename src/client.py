#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

import random
import tkinter
import webbrowser
import tkinter.messagebox

messages_sent_count = 0
connected = False

def display(text):
    global chat_display
    
    if not text.startswith('['):
        text = '[CLIENT] ' + text

    print(text)
    
    
    random_message_id = random.randint(1000000000, 9999999999)
    chat_display.config(state='normal')
    
    if text.startswith('[CLIENT] ERROR') or text.startswith('[SERVER] ERROR'):
        chat_display.tag_config(random_message_id, font=('Consolas', 20, 'bold'), foreground='red')
        chat_display.insert('end', text + '\n', random_message_id)

    else:
        chat_display.tag_config(random_message_id, font=('Consolas', 20))
        chat_display.insert('end', text.split()[0] + ' ', random_message_id)
        chat_display.insert('end', ' '.join(text.split()[1:]) + '\n')

    chat_display.see('end')
    chat_display.config(state='disabled')

def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode('utf8')
            display(msg)

            if '<LINK>' in msg:
                webbrowser.open(msg.split('<LINK>')[1])

        except (OSError, NameError):  # Possibly client has left the chat or no connection is established yet
            break

def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    global IP
    global PORT
    global window
    global connected
    global messages_sent_count
    
    msg = message_var.get()
    message_var.set('')  # Clears input field.
    
    if not connected:
        if ':' in msg:
            (IP, PORT) = msg.split(':')

        client_socket = socket(AF_INET, SOCK_STREAM)

        try:
            client_socket.connect((IP, PORT))

        except Exception as e:
            display(f'ERROR: Could not connect to "{IP}:{PORT}". Check if the server is running. <{e}>')

        else:
            receive_thread = Thread(target=receive)
            receive_thread.start()
            connected = True

    elif messages_sent_count == 1:
        window.title(msg)

    else:
        try:
            client_socket.send(bytes(msg, 'utf8'))

            if msg == 'quit':
                client_socket.close()
                window.quit()
        except NameError:
            display('ERROR: Connection failed. Try restarting and choosing another server.')

    messages_sent_count += 1

def on_closing(event=None):
    """This function is to be called when the window is closed."""
    message_var.set('quit')
    send()

window = tkinter.Tk()
window.geometry('800x500')
window.config(background='#111111')
window.title('Login')

messages_frame = tkinter.Frame(window, borderwidth=0, highlightthickness=0, bd=0)
message_var = tkinter.StringVar()  # For the messages to be sent.
scrollbar = tkinter.Scrollbar(messages_frame, borderwidth=0, highlightthickness=0, bd=0)  # To navigate through past messages.

# Following will contain the messages.
chat_display = tkinter.Listbox(
    messages_frame,
    height=13,
    width=50,
    font=('Consolas', 20),
    yscrollcommand=scrollbar.set,
    xscrollcommand=scrollbar.set,
    bg='#111111',
    fg='green',
    highlightcolor='red'
)

chat_display = tkinter.Text(
    messages_frame,
    height=13,
    width=50,
    font=('Consolas', 20),
    yscrollcommand=scrollbar.set,
    xscrollcommand=scrollbar.set,
    bg='#111111',
    fg='green',
    highlightcolor='red',
    selectbackground='red',
    selectforeground='green',
    relief='flat',
)

scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
chat_display.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
chat_display.pack()

messages_frame.pack()

send_frame = tkinter.Frame(
    window,
    bd=0,
    bg='#111F11',
    relief='flat',
)
send_frame.pack(side='bottom', fill='x')

entry_field = tkinter.Entry(
    send_frame,
    textvariable=message_var,
    bg='#111F11',
    fg='green',
    font=('Consolas', 20, 'bold'),
    width=46,
    relief='flat',
    cursor='xterm green',
    insertbackground='green',
)
entry_field.bind('<Return>', send)
entry_field.pack(side='left')#fill='x')
entry_field.focus_set()

send_button = tkinter.Button(
    send_frame,
    text='▶',
    command=send,
    bg='#111111',
    fg='green',
    width=3,
    relief='flat',
    activebackground='black',
    highlightcolor='black',
    highlightbackground='black',
    activeforeground='green',
    font=('Consolas', 24),
)
send_button.pack(side='right')#side='bottom', fill='x')

window.protocol('WM_DELETE_WINDOW', on_closing)

# Socket connection setup
IP = 'localhost'
PORT = 1183
BUFSIZ = 1024

display(f'Please type in a "<IP>:<PORT>" to connect to. Or press enter to use {IP}:{PORT}')

tkinter.mainloop()  # Starts GUI execution.