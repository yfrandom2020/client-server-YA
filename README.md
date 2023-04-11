# client server YA

This is a client - server application that supports communications with multiple clients. It enables the clients to join or create chatrooms and communicate with one another or with the server (via echo communication). In this guide I will explain the features, uses and logic behind the code.  

# Table of contents
[Establishing connection]
[Usage]
[Features]
[Limitations]

# Establishing connection
This project assumes two things: the server and client are on the same LAN and their IP and port are unknown to each other. To solve this problem the client first sends a UDP broadcast message across the LAN containing that says 'Client' and contains his IP. From the moment the server is up, he opens a thread to handle these types of broadcast messages. The server uses scapy to sniff packets that answer the following requirement (UDP broadcast) and sends them back a UDP message containing the IP and port he sits on. After the client sends his broadcast message he listens on said port for a reply from the server.
