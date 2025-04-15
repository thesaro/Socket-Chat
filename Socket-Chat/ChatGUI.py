import socket
import tkinter as tk
from tkinter import font, simpledialog, messagebox
import threading
import time

class ChatGUI:
    def __init__(self, ip_address, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server.connect((ip_address, port))
        except ConnectionRefusedError:
            messagebox.showerror("Connection Error", "Could not connect to server")
            exit()
        
        self.Window = tk.Tk()
        self.Window.withdraw()
        
        self.login = tk.Toplevel()
        self.setup_login_window()
        
        self.Window.mainloop()

    def setup_login_window(self):
        self.login.title("Login")
        self.login.resizable(width=False, height=False)
        self.login.configure(width=400, height=350)
        
        self.pls = tk.Label(self.login, 
                          text="Please login to chat", 
                          justify=tk.CENTER, 
                          font="Helvetica 14 bold")
        self.pls.place(relheight=0.15, relx=0.2, rely=0.07)

        self.userLabel = tk.Label(self.login, text="Username: ", font="Helvetica 12")
        self.userLabel.place(relheight=0.2, relx=0.1, rely=0.2)

        self.userEntry = tk.Entry(self.login, font="Helvetica 14")
        self.userEntry.place(relwidth=0.4, relheight=0.12, relx=0.35, rely=0.2)
        self.userEntry.focus()

        self.roomLabel = tk.Label(self.login, text="Room ID: ", font="Helvetica 12")
        self.roomLabel.place(relheight=0.2, relx=0.1, rely=0.4)

        self.roomEntry = tk.Entry(self.login, font="Helvetica 14")
        self.roomEntry.place(relwidth=0.4, relheight=0.12, relx=0.35, rely=0.4)

        self.go = tk.Button(self.login, 
                         text="CONTINUE", 
                         font="Helvetica 14 bold", 
                         command=lambda: self.go_ahead(self.userEntry.get(), self.roomEntry.get()))
        self.go.place(relx=0.35, rely=0.6)

    def go_ahead(self, username, room_id):
        if not username or not room_id:
            messagebox.showerror("Error", "Username and room ID are required")
            return
            
        self.username = username
        self.room_id = room_id
        
        try:
            self.server.send(f"User {username}".encode())
            time.sleep(0.1)
            self.server.send(f"Join {room_id}".encode())
        except:
            messagebox.showerror("Connection Error", "Could not connect to server")
            exit()
        
        self.login.destroy()
        self.setup_chat_window()
        
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.daemon = True
        receive_thread.start()

    def setup_chat_window(self):
        self.Window.deiconify()
        self.Window.title(f"Chat Room: {self.room_id}")
        self.Window.resizable(width=False, height=False)
        self.Window.configure(width=600, height=700, bg="#17202A")
        
        # Chat header
        self.chatHeader = tk.Label(self.Window, 
                                 bg="#17202A", 
                                 fg="#EAECEE", 
                                 text=f"Chat Room: {self.room_id} | User: {self.username}", 
                                 font="Helvetica 13 bold", 
                                 pady=5)
        self.chatHeader.place(relwidth=1)
        
        # Divider
        self.divider = tk.Label(self.Window, width=450, bg="#ABB2B9")
        self.divider.place(relwidth=1, rely=0.07, relheight=0.012)
        
        # Chat text area
        self.textCons = tk.Text(self.Window, 
                              width=20, 
                              height=2, 
                              bg="#17202A", 
                              fg="#EAECEE", 
                              font="Helvetica 12", 
                              padx=5, 
                              pady=5,
                              wrap=tk.WORD)
        self.textCons.place(relheight=0.745, relwidth=0.74, rely=0.08)
        
        # user list
        self.userList = tk.Listbox(self.Window, bg="#2C3E50", fg="#EAECEE", font="Helvetica 12")
        self.userList.place(relheight=0.745, relwidth=0.25, relx=0.74, rely=0.08)
        
        # scrollbar for chat
        chat_scrollbar = tk.Scrollbar(self.textCons)
        chat_scrollbar.place(relheight=1, relx=0.974)
        chat_scrollbar.config(command=self.textCons.yview)
        self.textCons.config(yscrollcommand=chat_scrollbar.set)
        
        # scrollbar for user list
        user_scrollbar = tk.Scrollbar(self.userList)
        user_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.userList.config(yscrollcommand=user_scrollbar.set)
        user_scrollbar.config(command=self.userList.yview)
        
        # bottom area
        self.bottomLabel = tk.Label(self.Window, bg="#ABB2B9", height=80)
        self.bottomLabel.place(relwidth=1, rely=0.825)
        
        # message entry
        self.msgEntry = tk.Entry(self.bottomLabel, 
                               bg="#2C3E50", 
                               fg="#EAECEE", 
                               font="Helvetica 12")
        self.msgEntry.place(relwidth=0.6, relheight=0.06, rely=0.008, relx=0.011)
        self.msgEntry.focus()
        self.msgEntry.bind("<Return>", lambda event: self.send_message())
        
        # send button
        self.sendButton = tk.Button(self.bottomLabel, 
                                  text="Send", 
                                  font="Helvetica 13 bold", 
                                  width=20, 
                                  bg="#ABB2B9",
                                  command=self.send_message)
        self.sendButton.place(relx=0.62, rely=0.008, relheight=0.06, relwidth=0.15)
        
        # private message button
        self.privateButton = tk.Button(self.bottomLabel, 
                                     text="Private", 
                                     font="Helvetica 13 bold", 
                                     width=20, 
                                     bg="#ABB2B9",
                                     command=self.send_private_message)
        self.privateButton.place(relx=0.78, rely=0.008, relheight=0.06, relwidth=0.2)
        
        self.textCons.config(cursor="arrow", state=tk.DISABLED)

    def send_message(self):
        message = self.msgEntry.get().strip()
        if not message:
            return
            
        self.msgEntry.delete(0, tk.END)
        
        if message == "/exit":
            try:
                self.server.send(message.encode())
            except:
                pass
            self.Window.quit()
            return
            
        try:
            self.server.send(message.encode())
            self.display_message(f"<You> {message}")
        except:
            self.display_message("Failed to send message")

    def send_private_message(self):
        selected = self.userList.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a user from the list")
            return
        
        target_user = self.userList.get(selected)
        if target_user == self.username:
            messagebox.showwarning("Invalid Target", "You cannot send a PM to yourself")
            return
            
        message = simpledialog.askstring("Private Message", 
                                        f"Message to {target_user}:",
                                        parent=self.Window)
        if message:
            full_msg = f"/pm {target_user} {message}"
            try:
                self.server.send(full_msg.encode())
                self.display_message(f"[PM to {target_user}] {message}")
            except:
                self.display_message("Failed to send private message")

    def receive(self):
        while True:
            try:
                message = self.server.recv(1024).decode()
                if not message:
                    self.display_message("Disconnected from server")
                    break
                
                # handle different message types
                if message.startswith("USERLIST:"):
                    # update user list panel
                    users = message[9:].split(",")
                    self.update_user_list(users)
                elif "[PM from" in message:
                    # highlight private messages
                    self.display_private_message(message)
                else:
                    # display normal message
                    self.display_message(message)
                
            except ConnectionResetError:
                self.display_message("Connection lost with server")
                break
            except Exception as e:
                print("Error:", e)
                self.display_message("An error occurred")
                break

    def display_message(self, message):
        self.textCons.config(state=tk.NORMAL)
        self.textCons.insert(tk.END, message + "\n")
        self.textCons.config(state=tk.DISABLED)
        self.textCons.see(tk.END)

    def display_private_message(self, message):
        self.textCons.config(state=tk.NORMAL)
        # Insert with different color for PMs
        self.textCons.tag_config("pm", foreground="#58D68D")  # green color for PMs
        self.textCons.insert(tk.END, message + "\n", "pm")
        self.textCons.config(state=tk.DISABLED)
        self.textCons.see(tk.END)

    def update_user_list(self, users):
        self.userList.delete(0, tk.END)
        for user in sorted(users):
            if user and user != self.username:  # skip empty strings and self
                self.userList.insert(tk.END, user)

    def on_closing(self):
        try:
            self.server.send("/exit".encode())
        except:
            pass
        self.Window.destroy()

if __name__ == "__main__":
    ip_address = "127.0.0.1"
    port = 12345
    gui = ChatGUI(ip_address, port)