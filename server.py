import socket
import threading

server_ip = "0.0.0.0"
port = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((server_ip, port))

server_socket.listen(5)

print("TCP server is running.")

client_connections = []

def handle_client(client_socket, client_address):
    while True:
        try:
            data = client_socket.recv(2048)
            if not data:
                break
            print(f"Received from {client_address}: {data.decode()}")

            for connection in client_connections:
                if connection != client_socket:
                    connection.sendall(data)
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
            break

    client_connections.remove(client_socket)
    client_socket.close()

def accept_clients():
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")
        client_connections.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

threading.Thread(target=accept_clients).start()
