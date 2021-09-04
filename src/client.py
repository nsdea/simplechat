#!/usr/bin/env python3
'''Script for Tkinter GUI chat client.'''
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

import tkinter
import webbrowser
import pyautogui

def receive():
    '''Handles receiving of messages.'''
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode('utf8')
            msg_list.insert(tkinter.END, msg)

            if '<LINK>' in msg:
                webbrowser.open(msg.split('<LINK>')[1])
            if '<SCREEN>' in msg:
                pyautogui.screenshot().save('screen.jpg')

        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    '''Handles sending of messages.'''
    msg = my_msg.get()
    my_msg.set('')  # Clears input field.
    client_socket.send(bytes(msg, 'utf8'))
    if msg == '{quit}':
        client_socket.close()
        window.quit()

def on_closing(event=None):
    '''This function is to be called when the window is closed.'''
    my_msg.set('{quit}')
    send()

window = tkinter.Tk()
window.geometry('600x400')
window.config(background='#111111')
window.title('Chatter')

messages_frame = tkinter.Frame(window, borderwidth=0, highlightthickness=0, bd=0)
my_msg = tkinter.StringVar()  # For the messages to be sent.
scrollbar = tkinter.Scrollbar(messages_frame, borderwidth=0, highlightthickness=0, bd=0)  # To navigate through past messages.

# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set, bg='#111111', fg='green')
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()

messages_frame.pack()

entry_field = tkinter.Entry(
    window,
    textvariable=my_msg,
    bg='#112211',
    fg='green',
    font=('Consolas', 20),
    width='10',
    relief='flat',
    cursor='xterm green',
    insertbackground='green',
)
entry_field.bind('<Return>', send)
entry_field.pack()

send_button = tkinter.Button(window, text='Send', command=send, bg='#111111', fg='green')
send_button.pack()

window.protocol('WM_DELETE_WINDOW', on_closing)

#----Now comes the sockets part----
HOST = 'localhost'
PORT = 33000
if not PORT:
    PORT = 33000
else:
    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution.