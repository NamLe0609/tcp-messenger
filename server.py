import sys

import socket
import threading
import logging
import select

#logging.basicConfig(filename='server.log', filemode='w', format='%(levelname)s:%(message)s', level=logging.DEBUG)
logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s', level=logging.DEBUG)

class Server:
    def __init__(self, host=socket.gethostname(), port=1234):
        # Setup server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(10)
        
        # Setup client mapping
        self.clients = dict()
        
        # Setup select
        self.outputs = []
    
    def getClientAddress(self, client):
        return self.clients[client][0]
    
    def getClientName(self, client):
        return self.clients[client][1]
    
    def operate(self):
        inputs = [self.server]
        while True:
            try:
                r,w,e = select.select(inputs, self.outputs, [], 0.5)
                
                for s in r:
                    if s == self.server:
                        client, address = self.server.accept()
                        print(f'Connected with {str(address)}')
                        
                        self.clients[client] = (address, client.recv(1024).decode('ascii'))
                        inputs.append(client)
                        
                        print(f'Client nickname is {self.getClientName(client)}')
                        for o in self.outputs:
                            o.send(f'{self.getClientName(client)} joined!'.encode('ascii'))
                    else:
                        msg = s.recv(1024).decode('ascii')
                        if msg:
                            for o in self.outputs:
                                if o != s:
                                    o.send(msg)
                        else:
                            s.close()
                            inputs.remove(s)
                            self.outputs.remove(s)
                            
                            for o in self.outputs:
                                o.send(f'{self.getClientName(s)} just left!'.encode('ascii'))
                                
                            self.clients.pop(s)
            
            except KeyboardInterrupt:    
                self.server.close()
        
if __name__ == '__main__':
    server = Server()
    server.operate()