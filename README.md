# client server YA

This is a client - server application that supports communications with multiple clients. It enables the clients to join or create chatrooms and communicate with one another or with the server (via echo communication). In this guide I will explain the features, uses and logic behind the code.  

# Table of contents
- Establishing connection
- Features
- Limitation

# Establishing connection
This project assumes two things: the server and client are on the same LAN and their IP and port are unknown to each other. To solve this problem the client first sends a UDP broadcast message across the LAN containing that says 'Client' and contains his IP. From the moment the server is up, he opens a thread to handle these types of broadcast messages. The server uses scapy to sniff packets that answer the following requirement (UDP broadcast) and sends them back a UDP message containing the IP and port he sits on. After the client sends his broadcast message he listens on said port for a reply from the server.

# Features
This project contains a few interesting features:
- A timer the server holds that kicks idle clients after 2 minutes of inactivity
- A close command to leave a chatroom and join a different one
- An admin page (passowrd needed) that shows a log for each room (all the communication done inside it)
- Name login - the client first needs to enter a name to be recognized as
- Quit - the client can enter a password and terminate the server program - closing connections with all clients

# Timer
In order to find "lazy" clients the server opens a special thread that checks their last activity. The server has a dictionary that for each connection holds the last time data was received and updates it whenever new data arrives. The thread runs infinitely and checks if the 2 minutes have passed since the last activity and sends kick messages if it happens.

# /close
Clients are able to freely leave and enter chatrooms with the /close command. The close command is easily executed since the server keeps track of the current rooms and their participants using arrays. Once a client wants out or in of a room, all the server has to do is remove or append their connection to the right place in the array.

# Admin login
clients can login as admins and view the history of each room by entering a password. They will be presented with a special page that shows the existing chatrooms and each chatroom will lead them to a new page showing the log in a linear timeline.

# Name login
clients must enter a name before starting to communicate with others. 

# /Quit
clients can shut the server by using the Quit command and entering a password

# Photos

![image](https://user-images.githubusercontent.com/71512040/231188653-be0fdb1f-8a26-4067-b25d-97423de91d30.png)
The menu page, where clients can choose to join a chatroom or create one, and are presented with the passwords, admin and name fields

![image](https://user-images.githubusercontent.com/71512040/231189153-35551bf6-bef8-4653-a978-ff38b9901346.png)
The chat room, where clients can communicate and execute other commands

# Limitations
The code has one main limitation: it relies on the effectiveness of one UDP broadcast messages - in other words in doesn't bombard the network and risks some form of packet loss that will lead to the client being unable to connect.

