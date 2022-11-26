"""Python scripts to get your machine ip address"""
import socket

print(socket.gethostbyname(socket.gethostname()))