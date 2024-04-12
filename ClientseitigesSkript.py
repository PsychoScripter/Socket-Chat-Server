"""
    this code on local hast...
    soo please tern on your MySql first(XAMPP Control Panel)
    then run server 1- ServerseitigesSkript.py and 2- ClientseitigesSkript.py

"""

from cryptography.fernet import Fernet
import socket
import threading

from banner import banner

MEASURE = 1024
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 15000
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'


# Function to encrypt the message
def encrypt_message(message, cipher_suite):
    return cipher_suite.encrypt(message.encode())


# Function to decode the message
def decrypt_message(encrypted_message, cipher_suite):
    return cipher_suite.decrypt(encrypted_message).decode()


def handle_messages(connection: socket.socket, key):
    msg = ''
    cipher_suite = Fernet(key)
    while True:
        try:
            msg = connection.recv(MEASURE).decode(FORMAT)
            if msg == 'left':
                connection.close()
                break
            elif msg:
                print(decrypt_message(msg, cipher_suite))

        except Exception as e:
            print(f'Error handling message from server: {e}')
            connection.close()
            break


# Get the key
def key_exc(conn):
    key = '0'
    while key == '0':
        try:
            key = conn.recv(MEASURE).decode(FORMAT)
            # print(key)
            conn.send('got'.encode(FORMAT))
            return key
        except:
            key = '0'


def client() -> None:
    try:
        # Instantiate socket and start connection with server
        socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_instance.connect(ADDR)
        # Get the key
        key = key_exc(socket_instance)

        threading.Thread(target=handle_messages, args=[socket_instance, key]).start()
        cipher_suite = Fernet(key)

        while True:
            msg = input()

            if msg == 'left':
                encrypted_msg = encrypt_message(msg, cipher_suite)
                socket_instance.send(encrypted_msg)
                break

            # Parse message to utf-8
            encrypted_msg = encrypt_message(msg, cipher_suite)
            socket_instance.send(encrypted_msg)

        socket_instance.close()

    except Exception as e:
        print(f'Error connecting to server socket {e}')
        socket_instance.close()


if __name__ == "__main__":
    banner()
    client()
