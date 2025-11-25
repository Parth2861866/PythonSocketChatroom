import threading
import socket
import emoji   

alias = input("Enter your nickname: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 59000))
 
def client_receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                # socket closed; exit receive loop
                break
            if message == 'NICK':
                client.send(alias.encode('utf-8'))
            else:
                print(message)
        except:
            print("An error occurred!")
            break
    try:
        client.close()
    except:
        pass

def client_send():
    while True:
        user_input = input("")
        if user_input.strip().lower() == "end":
            # Close socket -> unblocks recv() in the other thread
            try:
                client.shutdown(socket.SHUT_RDWR)
            except:
                pass
            client.close()
            break
        message = f'{alias}: {user_input}'
        try:
            client.send(emoji.emojize(message, language='alias').encode('utf-8'))
        except:
            break

receive_thread = threading.Thread(target=client_receive)
send_thread = threading.Thread(target=client_send)

receive_thread.start()
send_thread.start()

# Wait for sender to finish (e.g., after "end"), then wait for receiver to exit
send_thread.join()
receive_thread.join()


