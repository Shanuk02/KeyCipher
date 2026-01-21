import socket
target_ip = input("Enter target IP address: ").strip()
start_port = 1
end_port = 1000
print (f"Scan from {start_port} to {end_port} on {target_ip}")
for port in range(start_port, end_port + 1):
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    result=s.connect_ex((target_ip,port))
    if result==0:
        print (f"Port {port} is open")
        s.close()

print ("Scan completed.")