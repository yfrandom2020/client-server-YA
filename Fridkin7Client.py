"""
Yonathan Fridkin
Sockets - Client side
"""

import sys
import os
import time
import socket
from scapy.all import *
import subprocess
import re
import _thread
import threading
from tkinter import *

in_room = False
waiting_data = False
last_message = ""
messages = [""] # the client_listen thread and chat_room function need to communicate the messages received by since the event loop is blocking and so is the recv we need to find an alternative
text = ""
username = ""
Admin_password = ""
def run_command(cmd):
    return subprocess.Popen(cmd,
        shell=True,  # not recommended, but does not open a window
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE).communicate()

def open_port():
    """
    Find the first free port and return it
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("",0))
    port = s.getsockname()[1]
    s.close()
    return port        


def Info():
    """
    Get server ip and port
    """
    my_data = subprocess.check_output('ipconfig').decode('iso-8859-1')
    my_ip = [line for line in my_data.split('\n') if line.find('IPv4 Address') >= 0][0][39:].replace('\r','') # machine IP
    port = open_port()
    data = "Client\n" + my_ip + "\n" + str(port)
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)    
    sock.sendto(data.encode('utf-8'), ('255.255.255.255', port))
    sock.close()
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", port))
    while True:
        data = sock.recv(1024).decode('utf-8')
        if "Server Hello" in data:
            sock.close()
            break
        else:
            pass

    data = data.split('\n')
    s_ip = data[1].replace('\r', '')
    s_port = data[2]
    return s_ip, int(s_port)   


def client_listen(sock):
    """
    The input is blocking so if the client is still in input mode and disconnects we need a way to receive the message
    Client listen is only open when chatroom is open
    """
    global in_room # boolean value to understand if client in chat room already
    global waiting_data  
    global messages   
    global last_message       
    
    while True:
        try:
            data = sock.recv(1024).decode('utf-8')
            messages.append(data)

        except:
            break   


def change_text(root, main_frame, operation):
    """
    Text is a variable that determines the action done in the welcome page
    """
    global username
    global text
    if username != "":
        text += operation
        root.quit()  
    else:
        error_label = Label(main_frame, text="Username not set", fg="red")
        error_label.grid(row=3, column=0)
        root.after(2000, clear_label, error_label)
        return     

def open_room(i,room):
    """
    This is the function that opens the contents of a specific room
    """    
    print("in open room")
    room_page = Toplevel()
    room_page.title(f"Admin page - room {i}")
    room_page.geometry("1200x600")
    room_label = Label(room_page, text="Room log")
    room_label.pack()
    text_box = Text(room_page, bg="lightgray")
    text_box.pack(fill="both", expand=True)
    messages = room.split('\n')
    print("messages: ", messages)
    for message in messages:
        text_box.insert("end", message + "\n")
    scrollbar = Scrollbar(text_box, command = text_box.yview)
    scrollbar.pack(side="right", fill="y")
    text_box.config(yscrollcommand=scrollbar.set)
    room_page.mainloop()   






def send_admin_data(main_frame, sock, admin):
    """
    Send Client password to server and receive the data from him
    """
    global messages
    print("entered")
    last_message = len(messages)# track the index of the last message before sending admin request
    print()
    data = "Admin \n" + admin.get()
    print("data before: ", data)
    admin.delete(0,"end")
    sock.send(data.encode('utf-8'))
    print("sent")
    time.sleep(0.2)
    data = messages[last_message:]
    print("data: ", data)
    if "success" in data:
        # login successful
        # create new window
        print("entered success")
        admin_page = Toplevel()
        label = Label(admin_page, text="Admin page", fg="red")
        label.pack()
        room_contents = data[1:]
        print("room contents: ", room_contents)
        contents_frame = Frame(admin_page)
        contents_frame.pack()
        rooms_text = Text(contents_frame, bg="lightgray")
        rooms_text.pack(fill="both")
        buttons = []
        for i,room in enumerate(room_contents):
            number = len(room.split('\n')) - 1
            button = Button(rooms_text, text = f"Room {i+1} - {number} messages")
            buttons.append(button)
            button.config(command=lambda s = room: open_room(room_contents.index(s) + 1, s))
            rooms_text.window_create("end", window=button)
            rooms_text.insert("end", '\n')
        scrollbar = Scrollbar(admin_page, command = rooms_text.yview)
        #scrollbar.pack(side="right", fill="y")
        scrollbar.place(relx=1, rely=0, relheight=1, anchor="ne")
        rooms_text.config(yscrollcommand=scrollbar.set)    
        admin_page.mainloop()
    else:
        print("fail")
        # login failed
        label = Label(main_frame, text="Login failed", fg="red")
        label.grid(row=3, column=1)
        return
            


 
def Welcome_page(sock):
    """
    Shows page upon running program. shows available chatrooms
    """
    global text
    global waiting_data
    global messages
    global Admin_password
    
    text = "rooms"
    sock.send(text.encode('utf-8'))
    time.sleep(0.3)
    rooms = messages[len(messages) - 1]
    text = ""
    root = Tk()

    root.title("Available chatrooms - Yonathan Fridkin")
    root.geometry("1200x600")
    #root.configure(background="Black")
    # Create the main frame
    main_frame = Frame(root)
    main_frame.grid(row=0, column=0)

    # room grid
    if rooms != "a":
        rooms = rooms.replace('a', '')
        arr = [f"Room {i+1} - active users: {rooms[i]}" for i in range(len(rooms))]
    else:
        arr = []    
    Rooms_Frame = Frame(main_frame, bd = 3, highlightthickness=1, highlightbackground='white')
    Rooms_Frame.grid(row=0, column=0, padx=10, pady = 10)
    #Rooms_Frame.columnconfigure(2, weight=1)
    Room_label = Label(Rooms_Frame, text = "Rooms available")
    Room_label.grid(row=0,column=0, sticky="nesw")
    rooms = Text(Rooms_Frame, bg="lightgray")
    rooms.grid(row=1, column=0)
    scrollbar = Scrollbar(Rooms_Frame, command = rooms.yview)
    scrollbar.grid(row=0, column = 1)
    rooms.config(yscrollcommand=scrollbar.set)
    buttons = []
    for i, room_text in enumerate(arr):
        button = Button(rooms, text = room_text, command=lambda: change_text(root, main_frame,"Join Room " + str(i + 1)))
        buttons.append(button)
        rooms.window_create("end", window=button)
        rooms.insert("end", '\n')
        #button.pack(fill="x")
        #button.grid(row = i, sticky="ew")
    rooms.update()
    rooms.grid_propagate(False)
    create_button = Button(Rooms_Frame, text="Create a room", command=lambda: change_text(root, main_frame,"Create"))
    create_button.grid(row=5, column=0)

    # guide grid
    guide_text = f"Guide: \nClick a room to connect to it \n/close to leave room \n/Quit to close the server (password needed) \n/echo to get server echo response \nEnter password to login as admin and view log of each room \nAdmin password {Admin_password}"
    Guide_Frame = Frame(main_frame)
    Guide_Frame.grid(row=0, column=1)
    Guide_Label = Label(Guide_Frame, text="GUIDE")
    Guide_Label.grid(row=0, column=0)
    text_placement = Text(Guide_Frame, wrap="word")
    text_placement.grid(row=1, column=0)
    text_placement.insert("end", guide_text)
    text_placement.config(state="disabled")

    # Admin Entry
    Admin_Label = Label(main_frame, text="Admin login:")
    Admin_Label.grid(row=1, column=1)
    Admin_Entry = Entry(main_frame, bg="lightgray")
    Admin_Entry.grid(row=2, column=1)
    Admin_Entry.bind("<Return>", lambda event: send_admin_data(main_frame,sock,Admin_Entry))

    # Name entry
    Name_Label = Label(main_frame, text="Enter username:")
    Name_Label.grid(row=1, column=0)
    Name_Entry = Entry(main_frame, bg="lightgray")
    Name_Entry.grid(row=2, column=0)
    Name_Entry.bind("<Return>", lambda event: set_username(root, main_frame, Name_Entry))
    # rendering
    root.mainloop()
    
    Room_Number = -1
    if "Join" in text:
        Room_Number = str(text.split(' ')[2])
    sock.send(text.encode('utf-8'))
    time.sleep(0.1)
    while True:
        data = messages[len(messages) - 1]
        if "Created" in data: 
            Room_Number = str(data.split('\n')[1]).replace(' ','')
        if data: break

    root.destroy()
    if messages == ['']:
        Room_Number = "1"
    chat_room(Room_Number, sock)    
    return

def set_username(root,main_frame, entry):
    """
    set username
    """    
    global username
    name = entry.get()
    username = name
    entry.delete(0,"end")

    set_label = Label(main_frame, text="Username set", fg="green")
    set_label.grid(row=3, column=0)
    root.after(2000, clear_label, set_label)
    return



def chat_room(num, sock):
    """
    After choosing a chat room from the welcome page (or creating one)
    the client is shown the chat room page
    num -> number of chat room
    """   
    global waiting_data
    global messages
    last_message = "" # indicate what is the last message in the list of messages received
    send_message = ""
    while True:
        root = Tk()
        root.geometry("1200x600")
        room_number = "Chat Room " + num
        root.title(room_number)

        chat_label = Label(root, text = "CHAT ROOM", font=("Arial", 20), fg='blue')
        chat_label.pack(pady=10)
        
        main_frame = Frame(root)
        main_frame.pack(fill="both", expand=True)
        
        Text_Entry = Entry(main_frame)
        Text_Entry.pack(fill="both", side="bottom")

        text_box = Text(main_frame, bg = "lightgray")
        text_box.pack(fill="both", side="top", expand=True)

        unsolicited_messages = threading.Thread(target=unsolicited, daemon=True, args=(root, sock, text_box,))
        unsolicited_messages.start()
        Text_Entry.bind("<Return>", lambda event: send_entry_data(sock,Text_Entry, text_box)) # bind the entry to the data function but call it anyway so that even when no data function is still called

        scrollbar = Scrollbar(text_box, command = text_box.yview)
        scrollbar.pack(side="right", fill="y")
        text_box.config(yscrollcommand=scrollbar.set)
        
        root.mainloop()

        Welcome_page(sock)
    return

def unsolicited(root, sock, text_box):
    """
    send_entry_data only shows messages made by you
    unsolicited shows the rest
    """    
    global messages
    global last_message
    global username
    while True:
        try:
            if last_message != messages[len(messages) - 1] and not "Created Room" in messages[len(messages) - 1]:
                last_message = messages[len(messages) - 1]
                if "close" in messages[len(messages) - 1]:
                    if not "self" in messages[len(messages) - 1]: # closing due to quit or time
                        if "time" in messages[len(messages) - 1]:
                            text_label = Label(text = "Out of time, disconnecting from server")
                        elif "quit" in messages[len(messages) - 1]:
                            text_label = Label(text_box,text="Server is closing")
                        text_box.window_create("end", window=text_label)
                        text_box.insert("end", '\n')
                        time.sleep(0.5)
                        sock.close()
                        os._exit(1)
                    else:
                        root.destroy()
                        username = ""
                        return
                    
                else:
                    text_label = Label(text_box, text = messages[len(messages) - 1])
                    last_message = messages[len(messages) - 1]
                    text_box.window_create("end", window=text_label)
                    text_box.insert("end", '\n')
                    last_message = messages[len(messages) - 1]
            time.sleep(1)
        except:
            pass       

def clear_label(label):
    label.config(text="")

def send_entry_data(sock, Text_Entry, text_box):
    
    global last_message
    global messages
    global username
    data = Text_Entry.get()
    Text_Entry.delete(0,"end")
    label_text = f"<{username} {time.asctime()}> {data}"
    label = Label(text_box, text = label_text)
    text_box.window_create("end", window=label)
    text_box.insert("end", '\n')
    sock.send(label_text.encode('utf-8'))
    time.sleep(0.1)
    return

def up_time(server_ip, server_port):
    """
    The main client function
    """
    global in_room
    global Admin_password
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((server_ip, server_port))
    listening = threading.Thread(target=client_listen, daemon= True, args=(client_sock,))
    listening.start()
    Admin_password = messages[len(messages) - 1]
    Welcome_page(client_sock)

def main():
    server_ip, server_port = Info()
    print(server_ip)
    print(server_port)
    up_time(server_ip, server_port)


if __name__ == '__main__':
    main()