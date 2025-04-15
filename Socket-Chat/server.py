import socket
from _thread import *
import sys
from collections import defaultdict
import time

class Server:
    def __init__(self):
        self.rooms = defaultdict(list)
        self.usernames = {}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.max_connections = 100
        self.connection_count = 0

    def accept_connections(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.server.bind((self.ip_address, int(self.port)))
        self.server.listen(self.max_connections)
        print(f"Server started on {ip_address}:{port}")

        while True:
            if self.connection_count >= self.max_connections:
                time.sleep(1)
                continue
                
            connection, address = self.server.accept()
            self.connection_count += 1
            print(f"{address[0]}:{address[1]} Connected (Total: {self.connection_count})")
            start_new_thread(self.client_thread, (connection, address))

        self.server.close()

    def client_thread(self, connection, address):
            try:
                # get user info
                user_id = connection.recv(1024).decode().strip()
                if not user_id.startswith("User "):
                    raise ValueError("Invalid user format")
                user_id = user_id[5:]
            
                room_id = connection.recv(1024).decode().strip()
                if not room_id.startswith("Join "):
                    raise ValueError("Invalid room format")
                room_id = room_id[5:]
            
                # track connection
                connect_time = time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"{user_id} joined room '{room_id}' from {address[0]} at {connect_time}")
            
                self.usernames[connection] = user_id
            
                if room_id not in self.rooms:
                    connection.send("New chat room created".encode())
                else:
                    connection.send(f"Welcome to chat room '{room_id}'".encode())
            
                self.rooms[room_id].append(connection)
                self.broadcast(f"{user_id} joined the room", connection, room_id, "System")

                while True:
                    try:
                        message = connection.recv(1024).decode().strip()
                        if not message:
                            raise ConnectionError("Client disconnected")
                        
                        if self.handle_special_commands(message, connection, room_id, user_id):
                            continue
                        
                        self.broadcast(message, connection, room_id, user_id)
                    
                    except ConnectionResetError:
                        print(f"Client {user_id} disconnected abruptly")
                        break
                    except Exception as e:
                        print(f"Error with client {user_id}: {str(e)}")
                        break
                    
            finally:
                self.remove_connection(connection, room_id, user_id)
                connection.close()
                self.connection_count -= 1
                print(f"{user_id} disconnected (Total: {self.connection_count})")

    def handle_special_commands(self, message, connection, room_id, user_id):
        if message == "/exit":
            self.broadcast(f"{user_id} left the room", connection, room_id, "System")
            return True
        elif message == "/users":
            users = [self.usernames[conn] for conn in self.rooms[room_id]]
            connection.send(f"Connected users: {', '.join(users)}\n".encode())
            return True
        elif message.startswith("/pm "):
            parts = message.split(maxsplit=2)
            if len(parts) == 3:
                _, target_user, private_msg = parts
                self.send_private_message(connection, room_id, user_id, target_user, private_msg)
            else:
                connection.send("Usage: /pm [username] [message]\n".encode())
            return True
        return False

    def send_private_message(self, sender_conn, room_id, sender_id, target_user, message):
        timestamp = time.strftime("%H:%M:%S")
        private_msg = f"[{timestamp}] [PM from {sender_id}] {message}\n"
        found = False
    
        for client in self.rooms[room_id]:
            try:
                if client != sender_conn and self.usernames[client] == target_user:
                    client.send(private_msg.encode())
                    found = True
            except:
                self.remove_connection(client, room_id, "Unknown")
    
        if found:
            sender_conn.send(f"[{timestamp}] [PM to {target_user}] {message}\n".encode())
        else:
            sender_conn.send(f"User {target_user} not found or offline\n".encode())

    def broadcast(self, message, connection, room_id, sender_id):
        timestamp = time.strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] <{sender_id}> {message}\n"
    
        for client in self.rooms[room_id]:
            try:
                if client != connection:
                    client.send(formatted_msg.encode())
            except:
                self.remove_connection(client, room_id, "Unknown")
    
        # send user list update separately to avoid mixing with messages
        user_names = [self.usernames[conn] for conn in self.rooms[room_id]]
        user_list_msg = f"USERLIST: {','.join(user_names)}\n"
        for client in self.rooms[room_id]:
            try:
                client.send(user_list_msg.encode())
            except:
                self.remove_connection(client, room_id, "Unknown")


    def remove_connection(self, connection, room_id, user_id):
        if room_id in self.rooms and connection in self.rooms[room_id]:
            self.rooms[room_id].remove(connection)
            del self.usernames[connection]
            if not self.rooms[room_id]:
                del self.rooms[room_id]
            print(f"Removed {user_id} from room '{room_id}'")

if __name__ == "__main__":
    ip_address = "127.0.0.1"
    port = 12345

    server = Server()
    server.accept_connections(ip_address, port)
