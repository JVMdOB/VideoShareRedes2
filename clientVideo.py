import socket

# Server address and port
server_host = "177.12.27.67"  # Change this to the IP or hostname of your server
server_port = 8080  # Use the same port number as your server

# Create a socket and connect to the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((server_host, server_port))

# Send a test message to the server
message = "Hello, server!"
client.send(message.encode())

# Receive and print the response from the server
response = client.recv(1024)
print(f"Server response: {response.decode()}")

# Close the client socket
client.close()
