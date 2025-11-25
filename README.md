# PySocketChat — Minimal TCP Chat (Server & Client)

A tiny, educational Python chat system built with the standard library (`socket`, `threading`). It contains a multi‑client **server** and a simple **client** you can run from the terminal.

> Perfect for learning TCP sockets, threading, and basic client/server patterns.

## Features
- Multi‑client broadcast chat over TCP
- Nickname handshake (`NICK`) between server and client
- Minimal, dependency‑free Python (stdlib only)
- Clear, commented code for students

## Repo layout
```
server.py    # Run first on a host/VPS (listens for clients)
client.py    # Run on any machine to join the chat
README.md

```

## Quick start

### 1) Start the server
On the machine/VM where you want to host the chat room:
```bash
python3 server.py
# If your server binds a host/port, edit the variables at the top of server.py
# Optional: open your firewall or router port-forward as needed
```

### 2) Connect a client
On your local machine (or another remote machine):
```bash
python3 client.py
# If client.py contains a hard-coded IP/port, change them to your server's public IP and the chosen port
```

> Tip: If you’re connecting across the public internet, run the server with host `0.0.0.0` and ensure your firewall allows the server port (e.g., 59000). On the client, use the server’s **public** IP.

## GitHub setup (new repo)

1. Create a new GitHub repository (suggested name): **PySocketChat**
   - Description: *Minimal TCP chat in Python (server + client) using sockets and threading, no dependencies.*
   - Topics: `python`, `sockets`, `tcp`, `chat`, `threading`, `networking`, `education`

2. In your project folder (where `server.py` and `client.py` live), run:
```bash
git init
git add .
git commit -m "Initial commit: minimal TCP chat (server+client)"
git branch -M main
git remote add origin https://github.com/<your-username>/PySocketChat.git
git push -u origin main
```

## Usage notes
- The current sample code **broadcasts** every message to all connected clients (including the sender). If you prefer to skip echoing back to the sender, adjust `broadcast()` to ignore the source socket.
- Nicknames are requested by the server using a `NICK` prompt on connect.
- To shut down cleanly, close the client terminal or implement a command (e.g., `end`) and handle it in both client and server.

## Roadmap / ideas
- Add `/quit` or `end` command to leave gracefully
- Suppress echo to sender
- Simple chat commands (`/list`, `/nick`, `/help`)
- Basic message timestamps
- TLS option using `ssl` module
- Dockerfile for quick container runs

## Author/Year


**Author:** Shardul Panchal  
**Year:** 2025


## How it works — Code Walkthrough

This repo has two scripts: **`server.py`** and **`client.py`**. Both use only Python’s standard library (`socket`, `threading`). Below is a high‑level tour of the code so you can understand/modify it quickly.

### Server (`server.py`)

**Purpose:** Accept multiple TCP clients and broadcast messages to everyone connected.

**Typical flow:**
1. **Create a TCP socket & bind**
   ```py
   server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   server.bind((HOST, PORT))   # e.g., HOST="0.0.0.0", PORT=59000
   server.listen()
   ```
   - `0.0.0.0` listens on all interfaces. Use a specific IP if you want to restrict it.

2. **Accept loop (main thread)**
   ```py
   while True:
       client, address = server.accept()
       # ask for a nickname
       client.send(b"NICK")
       nickname = client.recv(1024).decode("ascii")
       clients.append(client); nicknames.append(nickname)
       # start a thread to handle this client
       threading.Thread(target=handle, args=(client,), daemon=True).start()
   ```
   - Each new connection is handled by a new **thread** so multiple clients can chat concurrently.
   - The server first sends a special `NICK` prompt. The client responds with its nickname.

3. **Per‑client handler (`handle`)**
   ```py
   def handle(client):
       while True:
           try:
               msg = client.recv(1024)  # bytes
               broadcast(msg)           # send to everyone (see tweak below to skip sender)
           except:
               # remove a broken/disconnected client
               idx = clients.index(client)
               left = nicknames[idx]
               clients.pop(idx); nicknames.pop(idx)
               client.close()
               broadcast(f"{left} left the chat!".encode("ascii"))
               break
   ```
   - `recv()` blocks until the client sends data or disconnects.
   - On error/disconnect, we clean up the lists and notify others.

4. **Broadcast helper**
   ```py
   def broadcast(message):
       for c in clients:
           c.send(message)
   ```
   - Sends the exact bytes to all connected clients.
   - **Tip:** To *not* echo a sender’s own message back, pass the source socket and skip it:
     ```py
     def broadcast(message, exclude=None):
         for c in clients:
             if c is not exclude:
                 c.send(message)
     ```

### Client (`client.py`)

**Purpose:** Connect to the server, share your nickname, and both send/receive chat messages concurrently.

**Typical flow:**
1. **Connect & send nickname**
   ```py
   client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   client.connect((SERVER_IP, PORT))
   ```
   - In a background receiver thread:
     ```py
     def client_receive():
         while True:
             data = client.recv(1024).decode("ascii")
             if data == "NICK":
                 client.send(alias.encode("ascii"))
             else:
                 print(data)
     ```
   - The server’s first message is `NICK` → respond with your chosen nickname (`alias`).

2. **Send loop (main thread)**
   ```py
   def client_send():
       while True:
           text = input("")                 # your message
           message = f"{alias}: {text}"
           client.send(message.encode("ascii"))
   ```
   - Runs forever so you can continuously send messages.
   - The receive thread prints messages from other users as they arrive.

### Graceful exit (optional)
If you add a small command like `end` or `/quit`, the client can leave cleanly and the server can announce it:
``` py
# client side
if text.strip().lower() == "end":
    client.send(f"{alias} left the chat.".encode("ascii"))
    client.close()
    break

# server side (inside handle):
if msg.decode("ascii").strip().lower().endswith("left the chat."):
    # handle as a normal message; the except block will clean up when the socket closes
    pass
```
> You can also send a dedicated control message instead of relying on plain text.

### Why a separate thread for sending and receiving?
Sockets block on `recv()`. Using **two threads** per client keeps the UI responsive: one thread listens for messages while the other waits for user input. On the server, each client gets its own thread so multiple clients are handled in parallel.

### Common tweaks
- **Don’t echo the sender:** pass `exclude=client` to `broadcast()` in `handle()` and skip the sender.
- **Timestamps:** prepend `time.strftime("%H:%M:%S")` to messages.
- **Validation:** limit message size, sanitise nicknames, prevent empty lines.
- **Security:** This demo is plaintext. For real use, wrap sockets with `ssl` for TLS.
- **Firewall/ports:** bind to `0.0.0.0` on the server and open the chosen port (e.g., 59000). Clients must use the server’s public IP and the same port.

---

If you’re new to sockets, the server is a passive listener that accepts connections, and each client maintains a persistent TCP stream to the server. The server relays (“broadcasts”) messages to all connected clients.
