import sys

import socket
import threading
import logging

#logging.basicConfig(filename='server.log', filemode='w', format='%(levelname)s:%(message)s', level=logging.DEBUG)
logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s', level=logging.DEBUG)

class Server:
    def __init__(self, host='127.0.0.1', port=1234):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        
        self.clients = dict()

    def broadcast(self, message):
        for client in self.clients:
            client.send(message)

    def handle(self, client):
        while True:
            try:
                message = client.recv(1024)
                if not message:
                    nickname = self.clients[client]
                    client.close()
                    self.clients.pop(client)
                    self.broadcast(f'{nickname} just left!'.encode('ascii'))
                else:
                    self.broadcast(message)
            except:
                break
                
    def run(self):
        while True:
            client, address = self.server.accept()
            print(f'Connected with {str(address)}')
            
            nickname = client.recv(1024).decode('ascii')
            self.clients[client] = nickname
            
            print(f'Client nickname is {nickname}')
            self.broadcast(f'{nickname} joined!'.encode('ascii'))
            
            thread = threading.Thread(target=self.handle, args=(client,))
            thread.start()
        
if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Need 1 arguments')
        sys.exit()
    
    server = Server(port=int(sys.argv[1]))
    server.run()
    