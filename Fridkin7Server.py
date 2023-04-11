"""
Yonathan Fridkin
Sockets - Server side
"""
import sys
import os
import time
import socket
import select
from scapy.all import *
import threading
import _thread
import random

times = {}
def open_port():
    """
    Find the first free port and return it
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("",0))
    port = s.getsockname()[1]
    s.close()
    return port
 
def client_request(address):
    """
    Have an open thread in all times to see UDP messages of clients and respond to them
    """
    data = subprocess.check_output('ipconfig').decode('iso-8859-1')
    my_ip = [line for line in data.split('\n') if line.find('IPv4 Address') >= 0][0][37:].split(' ')[1] # machine IP
    text = "Server Hello \n" + my_ip + "\n" + str(address[1])
    text = text.encode('utf-8')
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    port = int(address[1])

    while True:
        data = sniff(count = 1, filter="udp and dst 255.255.255.255") # braodcast

        a = data[0].show(dump=True)
        try:
            if "Client" in a:
                content = a[a.index("Client"):len(a) - 2]
                client_ip = re.findall('\d+\.\d+\.\d+\.\d+', content)[0]
                client_port = re.findall(r'\d+', content)[-1]
                addr = (client_ip, int(client_port))
                sock.sendto(text, addr)
        except Exception() as e:
            print(e)
            pass  


def checker(readables, server):
    """
    go over clients and check their time to send them connect messages
    """         
    global times
    kicked = [] # save a list of the kickec connections
    while True:
        for sock in times.keys():
            if sock in kicked or sock is server: continue
            if time.time() - times[sock] >= 60:
                if 60 - round((time.time() - times[sock])) > 0:
                    text = "WARNING: disconnecting in "
                    text += str(15-round((time.time() - times[sock]))) + " seconds"
                    text = text.encode('utf-8')
                    sock.send(text)
            if time.time() - times[sock] >= 75:
                text = "close time".encode('utf-8')
                sock.send(text)
                time.sleep(1)
                readables.remove(sock)
                kicked.append(sock)
                sock.close()  
        time.sleep(1)          

def Terminate(sock, text, readables):
    sock.send(text)
    time.sleep(0.2)
    readables.remove(sock)
    sock.close()

def randomise():
    arr = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "K", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]    
    password = ""
    for i in range(5):
        index = random.randint(0, len(arr)-1)
        password += arr[index]
    return password    



def up_time(server, address):
    """
    The main server function that runs while the server is up
    """
    password = randomise()
    Admin_password = "123"
    global times
    threading.Thread(target=client_request, daemon = True, args=(address,)).start()
    readables = [server] # all connecions
    writables = [server] # all connections
    checking = threading.Thread(target=checker, daemon=True, args=(readables,server))
    checking.start()
    Quit_Active = [] # an array of boolean values that determine for each connection if it requests quitting
    Rooms = [] # list of rooms - each room is a list of the participants
    contents = [] # for each room in Rooms have a list of messages sent
    while True:
        readable, writable, exceptional = select.select(readables, writables, [])
        for sock in readable:
            if sock is server: # connection request
                cli_sock, addr = sock.accept()
                print("new connection from: ", addr)
                readables.append(cli_sock)
                Quit_Active.append(False)
                time.sleep(0.1)
                cli_sock.send(f"Admin \n{Admin_password}".encode('utf-8'))
                # First ask client if he wants to join an existing room or create new
            else: # data from connection
                try:
                    print("current status of contents: ", contents)
                    data = sock.recv(1024).decode('utf-8')
                    print("received: ", data)
                    times[sock] = time.time() # update time
                    # understand if connection is already in room or not
                    in_room = None

                    if data == "rooms":
                        print("received rooms")
                        text = "a"
                        for room in Rooms: text += str(len(room))
                        print("text: ", text)
                        sock.send(text.encode('utf-8'))
                        continue
                    
                    for room in Rooms: # understand if client is in room
                        if sock in room:
                            in_room = room
                            break                    
                    #------------------------------------
                    if in_room == None:
                        
                        if "Admin" in data:
                            print("data received")
                            print(data)
                            print("received admin")
                            data = data.split('\n')[1]
                            print("new data: ", data)
                            if data == Admin_password:
                                data = "success"
                                sock.send(data.encode('utf-8'))
                                for room_content in contents:
                                    print("room content is: ", room_content)
                                    data = ""
                                    for messages in room_content:
                                        print("en: ", messages)
                                        data += messages + "\n"
                                    print("final message: ", data)
                                    sock.send(data.encode('utf-8'))
                            else:
                                data = "fail"
                                sock.send(data.encode('utf-8')) 
                            continue  

                        if not "Join" in data and data != "Create":
                            text = "Not in room, enter a room or create one first".encode('utf-8')
                            sock.send(text)
                            continue        
                        elif "Join" in data:
                            try:
                                times[sock] = time.time()
                                room_number = int(data.split(' ')[2])
                                Rooms[room_number - 1].append(sock)
                                contents.append([])
                                text = "Successfuly joined room".encode('utf-8')
                            except:
                                text = "Incorrect room number, try again please".encode('utf-8')    
                            sock.send(text)

                        elif in_room == None and data == "Create":
                            #time.sleep(0.4)
                            times[sock] = time.time()
                            Rooms.append([sock])
                            contents.append([])
                            text = ("Created Room \n " + str(len(Rooms))).encode('utf-8')
                            try:
                                sock.send(text)

                            except Exception as e: print(e)    
                    #--------------------------------------------

                    elif "/Quit" in data:
                        text = "Please enter the password: ".encode('utf-8')
                        sock.send(text)
                        Quit_Active[readables.index(sock) - 1] = True       

                    else:  
                        if Quit_Active[readables.index(sock) - 1]:
                            if data == password:
                                text = "Terminating..".encode('utf-8')
                                sock.send(text)
                                text = "close quit".encode('utf-8')
                                for cli_sock in readables:
                                    if cli_sock is server: continue
                                    threading.Thread(target=Terminate, args=(cli_sock, text, readables)).start()
                                time.sleep(0.2)
                                server.close()
                                readables.remove(server)
                                os._exit(1)    
                                
                            elif data == "Go back":
                                text = "Cancelling termination".encode('utf-8')
                                sock.send(text)
                                Quit_Active[readables.index(sock) - 1] = False

                            else:
                                text = "Incorect password, try again".encode('utf-8')
                                sock.send(text)
                            pass               
                        
                        else: # client not requesting QUIT
                            
                            # first check that user is in room             
                            content = Rooms.index(in_room) # array of content
                            print("content: ", content)
                            contents[content].append(data)
                            
                            if "/close" in data:
                                text = "close self"
                                sock.send(text.encode('utf-8'))
                                Rooms[Rooms.index(in_room)].remove(sock)
                                print(Rooms)
                            
                            elif "/echo" in data:
                                text = "<Server: " + time.asctime() + "> " + data[data.index('/echo') + 5:]
                                sock.send(text.encode('utf-8'))
                                contents[content].append(text)

                            else:
                                text = data.encode('utf-8')
                                for cli_sock in in_room:
                                    if cli_sock is sock: continue
                                    else:
                                        cli_sock.send(text)


                except:
                    pass
                    
def main():
    data = subprocess.check_output('ipconfig').decode('iso-8859-1')
    my_ip = [line for line in data.split('\n') if line.find('IPv4 Address') >= 0][0][37:].split(' ')[1] # machine IP
    port = open_port()
    address = ('', port)
    print("The server is on: ", address)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(address)
    server.listen(3)
    up_time(server, address)


if __name__ == '__main__':
    main()


