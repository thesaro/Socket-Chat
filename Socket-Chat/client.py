import socket
import threading
import sys
import time

def receive_messages(server):
    while True:
        try:
            message = server.recv(1024).decode()
            if not message:
                print("Disconnected from server")
                sys.exit()
            print(message)
        except Exception as e:
            print(f"Error receiving message: {str(e)}")
            server.close()
            sys.exit()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    IP_address = "127.0.0.1"
    Port = 12345

    try:
        server.connect((IP_address, Port))
        print("Connected to server")
    except Exception as e:
        print(f"Could not connect to server: {str(e)}")
        sys.exit()

    user_id = input("Enter your username: ")
    room_id = input("Enter room ID: ")

    server.send(f"User {user_id}".encode())
    time.sleep(0.1)
    server.send(f"Join {room_id}".encode())

    print("\nType /exit to leave, /users to see online users, /pm [user] [message] to send private message\n")

    # start a thread to receive messages
    receive_thread = threading.Thread(target=receive_messages, args=(server,))
    receive_thread.daemon = True
    receive_thread.start()

    while True:
        try:
            message = input("> ").strip()
        
            if not message:
                continue

            # send message to the server
            server.send((message + "\n").encode())

            if message.lower() == "/exit":
                print("Disconnecting...")
                time.sleep(1)
                server.close()
                sys.exit()

            print(f"<You> {message}")

        except KeyboardInterrupt:
            print("\nDisconnecting...")
            server.send("/exit\n".encode())
            server.close()
            sys.exit()
        except Exception as e:
            print(f"Error: {str(e)}")
            server.close()
            sys.exit()

if __name__ == "__main__":
    main()