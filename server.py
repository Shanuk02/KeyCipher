import socket
s=socket.socket() #create communication socket
s.bind(("0.0.0.0", 8888)) #server attaches to ip and port
s.listen(1) #waiting for client
conn, addr = s.accept() #connection established
print("Connection from", addr)
data=conn.recv(1024).decode() #data transfer
print("Connected by", data)
conn.send("Hello from server".encode())
conn.close()
s.close()