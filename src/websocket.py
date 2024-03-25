import pickle
import socket

from config import settings

def connect_host():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((settings.SERVER_HOST, settings.SERVER_PORT))
    return client_socket