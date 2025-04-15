# Socket Chat

A simple chat application with TLI and GUI clients using Python sockets.

## Features

- Real-time public and private messaging
- Multiple chat rooms
- Online user list
- Both TLI and GUI interfaces

## Screenshots

| TLI Messaging | GUI Login | Chat GUI |
|------------|------------|-------------------|
| ![TLI](image/tli.png) | ![GUI](image/gui_login.png) | ![PM](image/gui_chat.png) |

## Quick Start
```bash
1. Start the server:
python server.py

2. Run clients:
# TLI version
python client.py

# GUI version
python ChatGUI.py
```
## Basic Commands
Public chat: Just type and press Enter

Private message: /pm username your-message (CLI)   ***    If you wanna send a pv message to someone in GUI chat just click on the username in the user list then click on Private button

Exit: /exit

List users (CLI): /users

## Requirements
Python 3.6+

Tkinter
