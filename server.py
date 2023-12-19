import sys

import socket
import threading
import logging

#logging.basicConfig(filename='server.log', filemode='w', format='%(levelname)s:%(message)s', level=logging.DEBUG)
logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s', level=logging.DEBUG)

class Server:
    def __init__(self, host='127.0.0.1', port=1234):
        # Choose encoding method to use for everything
        self.ENCODING = 'utf-8'
        
        # Setup server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        
        # Setup storage for client info
        self.clients = dict()
        self.takenNames = set()

    def broadcast(self, message, mode=0, broadcaster=None, broadcastee=None):
        message = message.encode(self.ENCODING)
        match mode:
            # Broadcast to all
            case 1:
                for client in self.clients:
                    client.send(message)
            
            # Broadcast to all but broadcaster
            case 2:
                for client in self.clients:
                    if client != broadcaster:
                        client.send(message)
            
            # Broadcast to individual
            case 3:
                broadcastee.send(message)
                
    def handle(self, client):
        while True:
            try:
                message = client.recv(1024).decode(self.ENCODING)
                if not message:
                    self.killConnection(client)
                elif message[0] == '/':
                    self.executeCommand(message[1:], client=client)
                else:
                    self.broadcast(message, 2, broadcaster=client)
            except:
                break
    
    def killConnection(self, client):
        address, username = self.clients[client]
        client.close()
        self.clients.pop(client)
        self.takenNames.remove(username)
        self.broadcast(f'{username} just left. Goodbye!', 1)
        print(f'Disonnected with {str(address)}. Remove client named {username}')
    
    def executeCommand(self, command, client=None):
        match command:
            case 'wisper':
                pass
            case 'help':
                pass
            case 'leave':
                self.killConnection(client)
            case default:
                print('Invalid command')
        
    
    def run(self):
        while True:
            client, address = self.server.accept()
            username = client.recv(1024).decode(self.ENCODING)
            
            # Disallow duplicate username in chat
            if username in self.takenNames:
                self.broadcast(f'Username taken', 3, broadcastee=client)
                client.close()
                continue
            
            # Store clients' address and username with the socket as key
            self.clients[client] = (address, username)
            self.takenNames.add(username)
            
            # Broadcast after as it loops over clients dictionary
            print(f'Connected with {str(address)}. Add client named {username}')
            self.broadcast(f'{username} just joined. Welcome!', 1)
            
            thread = threading.Thread(target=self.handle, args=(client,))
            thread.start()
        
if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Need 1 arguments')
        sys.exit()
    
    server = Server(port=int(sys.argv[1]))
    server.run()
    