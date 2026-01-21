import socket
s=socket.socket()
s.connect(("127.0.0.1", 8888))
s.send ("Hello from client".encode())
data=s.recv(1024).decode()
print("Server says", data)
s.close()