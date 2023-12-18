import socket
import threading
import select
import sys

def main():
    """ USERNAME = sys.argv[1]
    HOSTNAME = sys.argv[2]
    PORT = int(sys.argv[3]) """
    
    USERNAME = 'Joe'
    HOSTNAME = socket.gethostname()
    PORT = 1234

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOSTNAME, PORT))
    
    receiveThread = threading.Thread(target=receive, args=(client, USERNAME))
    receiveThread.start()
    
    writeThread = threading.Thread(target=write, args=(client, USERNAME))
    writeThread.start()

def receive(client, nickname):
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            client.close()
            break

def write(client, nickname):
    while True:
        body = input('> ')
        message = f'{nickname}: {body}'
        client.send(message.encode('ascii'))

class Client:
    def __init__(self, name='Joe', host=socket.gethostname(), port=1234):
        self.name = name
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.client.send(name.encode('ascii'))
        
    def operate(self):
        while True:
            try:
                r,w,e = select.select([0, self.client], [], [], 0.5)
            
                for s in r:
                    if s == self.client:
                        msg = s.recv(1024).decode('ascii')
                        if not msg:
                            sys.exit()
                        else:
                            print(msg)
                    else:
                        try:
                            msg = input('')
                        except:
                            print('fuck')
                            self.client.close()
                            break
                        self.client.send(f'{self.name}: {msg}'.encode('ascii'))
                        print('msg sent')
                        
            except:
                print('Interrupted')
                self.client.close()
                break
            
if __name__ == '__main__':
    """ if len(sys.argv) < 3:
        sys.exit('Please run with all arguments') """
    
    client = Client()
    client.operate()