#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

import tkinter
import tkinter.messagebox
import webbrowser

messages_sent_count = 0

def display(text):
    global chat_display
    
    chat_display.config(state='normal')
    chat_display.tag_config('author', font=('Consolas', 20, 'bold'))
    
    chat_display.insert('end', text.split()[0] + ' ', 'author')
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

        except OSError:  # Possibly client has left the chat.
            break

def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    global window
    global messages_sent_count
    
    msg = message_var.get()
    message_var.set('')  # Clears input field.
    
    client_socket.send(bytes(msg, 'utf8'))

    if not messages_sent_count:
        window.title(msg)

    if msg == '{quit}':
        client_socket.close()
        window.quit()

    messages_sent_count += 1

def on_closing(event=None):
    """This function is to be called when the window is closed."""
    message_var.set('{quit}')
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
    highlightcolor='black'
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
    highlightcolor='black',
    relief='flat',
)

scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
chat_display.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
chat_display.pack()

messages_frame.pack()

entry_field = tkinter.Entry(
    window,
    textvariable=message_var,
    bg='#111F11',
    fg='green',
    font=('Consolas', 20, 'bold'),
    width=10,
    relief='flat',
    cursor='xterm green',
    insertbackground='green',
)
entry_field.bind('<Return>', send)
entry_field.pack(fill='x')
entry_field.focus_set()

send_button = tkinter.Button(
    window,
    text='Send',
    command=send,
    bg='#111111',
    fg='green',
    width=10,
    font=('Consolas', 20),
)
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

try:
    client_socket.connect(ADDR)

except:
    tkinter.messagebox.showerror(title='Server Error!', message='The server is currently unavailable.')

else:
    receive_thread = Thread(target=receive)
    receive_thread.start()
    tkinter.mainloop()  # Starts GUI execution.