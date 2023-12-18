import sys

import socket
import logging
import threading
import select

#logging.basicConfig(filename='server.log', filemode='w', format='%(levelname)s:%(message)s', level=logging.DEBUG)
logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s', level=logging.DEBUG)

def main():
    
    HOST = socket.gethostname()
    #PORT = sys.argv[1]
    PORT = 1234

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(False)
    server.bind((HOST, PORT))
    server.listen(5)
    
    clients = dict()
    inputs = [server]
    outputs = []
    
    receive(server=server, 
            clients=clients,
            inputs=inputs,
            outputs=outputs)

def broadcast(message, clients):
    for client in clients:
        client.send(message)

def handle(client, clients):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message, clients)
        except:
            nickname = clients[client]
            client.close()
            clients.pop(client)
            broadcast(f'{nickname} just left!'.encode('ascii'), clients)
            break
            
def receive(server, clients, inputs, outputs):
    while True:
        r,w,e = select.select(inputs, outputs, inputs, 0.5)
        for s in r:
            if s == server:
                client, address = s.accept()
                inputs.append(client)
                print(f'Connected with {str(address)}')
                
                client.send('NICK'.encode('ascii'))
                nickname = client.recv(1024).decode('ascii')
                clients[client] = nickname
                
                print(f'Client nickname is {nickname}')
                broadcast(f'{nickname} joined!'.encode('ascii'), clients)
                
                thread = threading.Thread(target=handle, args=(client, clients,))
                thread.start()
                
if __name__ == '__main__':
    main()
    