import pickle
import socket
import threading

server_ip = "0.0.0.0"
port = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((server_ip, port))

server_socket.listen(5)

print("TCP server is running.")

client_connections = {}

def handle_client(client_socket, client_address):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            
            data = pickle.loads(data)
            data['client_address'] = str(client_address)
            data = pickle.dumps(data)

            for connection in client_connections:
                if connection != client_address:
                    client_connections[connection].sendall(data)
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
            if type(e) == ConnectionResetError: break
        
    for connection in client_connections:
        if connection != client_address:
            client_connections[connection].sendall(pickle.dumps({'disconnect': str(client_address)}))

    del client_connections[client_address]
    client_socket.close()

def accept_clients():
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")
        client_connections[client_address] = client_socket
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

threading.Thread(target=accept_clients).start()
