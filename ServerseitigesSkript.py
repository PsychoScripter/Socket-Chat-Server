"""
    this code on local hast...
    soo please tern on your MySql first(XAMPP Control Panel)
    then run server 1- ServerseitigesSkript.py and 2- ClientseitigesSkript.py

"""
from cryptography.fernet import Fernet
import socket
import threading
import banner
from db import my_db
from create_database import create_database, create_table

# Message length
MEASURE = 1024
SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = "192.168.165.65"
PORT = 15000
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
PRIVATE_CHAT_CODE = '00'
# create object from database
qq = my_db()
# Global variable that mantain client's connections
connections = []
online_clients = []
connected_clients = dict()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

key = Fernet.generate_key()
cipher_suite = Fernet(key)


# check database is created
def check_database():
    try:
        create_database()
        create_table()
        print('Database created')
        print('Table created')
    except Exception as e:
        print("The database is available")


# Function to encrypt the message
def encrypt_message(message):
    return cipher_suite.encrypt(message.encode())


# Function to decode the message
def decrypt_message(encrypted_message):
    return cipher_suite.decrypt(encrypted_message).decode()


def handle_user_connection(conn, addr, username):
    '''
        Get user connection in order to keep receiving their messages and
        sent to others users/connections.
    '''
    print(f"new connection from{addr}\n")

    broadcast(f"{username} has joined the chat!")
    conn.send(encrypt_message("if you want to private chat, enter: 00\n"
                              "if you want to go, enter: left\n"))
    while True:
        try:
            # Get client message
            encrypted_msg = conn.recv(1024)
            # If no message is received, there is a chance that connection has ended
            # so in this case, we need to close connection and remove it from connections list.
            if encrypted_msg:
                # Decrypt the message
                decrypted_msg = cipher_suite.decrypt(encrypted_msg).decode()

                # Log message sent by user
                print(f"{addr} ,username: {username}: {decrypted_msg}")

                # want to private chat
                if decrypted_msg == PRIVATE_CHAT_CODE:
                    print(f"{username} wants private chat!!!")
                    private_chat(conn, username)

                # want to exit chat
                elif decrypted_msg == "left":
                    # remove_connection(conn)
                    online_clients.remove(username)
                    connected_clients.pop(username)
                    broadcast(f"{username} {decrypted_msg}")
                    conn.close()
                # Build message format and broadcast to users connected on server
                else:
                    broadcast(f"{username}: {decrypted_msg}")

            # Close connection if no message was sent
            else:
                remove_connection(conn)
                break

        except Exception as e:
            print(f'Error to handle user connection: {e}')
            remove_connection(conn)
            break


# If the user wants to have a private chat
def private_chat(conn, username):
    conn.send(encrypt_message("please enter your user for private chat: "))

    user_for_chat = conn.recv(MEASURE).decode(FORMAT)
    user_for_chat = decrypt_message(user_for_chat)
    for client in online_clients:
        if user_for_chat == client:

            conn.send(encrypt_message(f"ok... Now you can send a private message to {user_for_chat}"))
            conn.send(encrypt_message(f"if you want to quit, enter 123"))
            private_cast(username, user_for_chat, conn)
        else:
            conn.send(encrypt_message(f"{user_for_chat} offline..."))
            print(f"{username} cant't send a private message to {user_for_chat} because {user_for_chat} is offline")


def private_cast(username, user_for_chat, conn):
    user_for_chat.upper()
    username.upper()
    while True:
        try:
            message = conn.recv(MEASURE).decode(FORMAT)
            message = decrypt_message(message)
            if message == '123':
                conn.send(encrypt_message("by by"))
                break
            # geve a connancon ip rof senf a message
            connections_private = connected_clients[user_for_chat]
            connections_private.send(encrypt_message(f"{username}, PRIVATE_MESSAGE: {message}"))

        except:
            # remove_client(client, a)
            pass


def singing(conn):
    # choose what do you want to do
    chooses = ("what do you want to do?\n"
               "1. Login\n"
               "2. Register\n"
               "choose a number for your choice: ")
    conn.send(encrypt_message(chooses))
    chooses = conn.recv(MEASURE).decode(FORMAT)
    chooses = decrypt_message(chooses)

    while True:
        if chooses == '1':
            massage_wellcome = "Wellcome, please login...\n"
            massage_password = "password:"
            massage_username = "username:"

            massage_login_successful = "login successful\n"
            massage_login_wrong = 'login wrong\n'
            message_user_exists = "username already exists\n"

            conn.send(encrypt_message(massage_wellcome))

            conn.send(encrypt_message(massage_username))
            login_username = conn.recv(MEASURE).decode(FORMAT)
            login_username = decrypt_message(login_username)
            conn.send(encrypt_message(massage_password))
            login_password = conn.recv(MEASURE).decode(FORMAT)
            login_password = decrypt_message(login_password)

            if login_username not in online_clients:
                if qq.check_password(login_username, login_password):
                    online_clients.append(login_username)
                    # for private chat
                    connected_clients.update({login_username: conn})

                    conn.send(encrypt_message(massage_login_successful))
                    return login_username
                else:
                    conn.send(encrypt_message(massage_login_wrong))
            else:
                conn.send(encrypt_message(message_user_exists))
                remove_connection(conn)

        elif chooses == '2':
            massage_wellcome = "Okay...\n"
            massage_username = "username: "
            massage_password = "password: "
            register_massage = "Register successful\n"
            invalid = "username or password is invalid"

            conn.send(encrypt_message(massage_wellcome))
            while True:
                conn.send(encrypt_message(massage_username))
                new_username = conn.recv(MEASURE).decode(FORMAT)
                new_username = decrypt_message(new_username)
                conn.send(encrypt_message(massage_password))
                new_password = conn.recv(MEASURE).decode(FORMAT)
                new_password = decrypt_message(new_password)
                try:
                    qq.add_users(new_username, new_password)
                    conn.send(encrypt_message(register_massage))
                    online_clients.append(new_username)
                    # for private chat
                    connected_clients.update({new_username: conn})
                    return new_username
                except:
                    conn.send(invalid)
                    break
        else:
            conn.send(encrypt_message("Invalid command"))


# send key for client
def key_exchange(conn, key):
    conn.send(key)
    chooses = conn.recv(MEASURE).decode(FORMAT)

    while chooses != 'got':
        try:
            conn.send(key)
            chooses = conn.recv(MEASURE).decode(FORMAT)
        except:
            conn.send('error')


def broadcast(message):
    for client in connections:
        try:
            client.send(encrypt_message(message))
        except:
            # remove_client(client, a)
            pass


def remove_connection(conn: socket.socket) -> None:
    '''
        Remove specified connection from connections list
    '''

    # Check if connection exists on connections list
    if conn in connections:
        # Close socket connection and remove connection from connections list
        conn.close()
        connections.remove(conn)


def start_server() -> None:
    '''
        Main process that receive client's connections and start a new thread
        to handle their messages
    '''

    try:
        # Create server and specifying that it can only handle 4 connections by time!
        server.listen(PORT)

        print('Server running!')

        while True:
            # Accept client connection
            conn, addr = server.accept()
            # send key
            key_exchange(conn, key)

            print('Connected by', addr)

            username = singing(conn)
            # Add client connection to connections list
            connections.append(conn)

            # Start a new thread to handle client connection and receive it's messages
            # in order to send to others connections
            threading.Thread(target=handle_user_connection, args=[conn, addr, username]).start()
            print(f"[ACTIVE CONNECTION] {threading.activeCount() - 1}")

    except Exception as e:
        print(f'An error has occurred when instancing socket: {e}')
    finally:
        # In case of any problem we clean all connections and close the server connection
        if len(connections) > 0:
            for conn in connections:
                remove_connection(conn)

        start_server()


if __name__ == "__main__":
    # my banner
    banner.banner()

    # first check The database is available
    check_database()
    start_server()
