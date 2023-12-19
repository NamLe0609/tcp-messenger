import socket
import threading
import sys

class Client:
    
    def __init__(self, username='John_Pork', host='127.0.0.1', port='1234'):
        # Choose encoding method to use for everything
        self.ENCODING = 'utf-8'
        
        # Setup client socket
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.username = username
        
        # Define two seperate thread handling reads and writes from and to the server
        self.receiveThread = threading.Thread(target=self.receive, args=())
        self.writeThread = threading.Thread(target=self.write, args=())
        
        # State to check if client should be running
        self.running = True

    def receive(self):
        while self.running:
            message = self.client.recv(1024).decode(self.ENCODING)
            
            # If the other thread is not alive then quit
            if not self.writeThread.is_alive():
                sys.exit(0)
                
            if message:
                print(message)
            else:
                print('Something went wrong. Disconnecting...')
                self.running = False
                self.client.close()
                sys.exit(0)

    def write(self):
        while self.running:
            body = input('')
            message = ''
            
            # If the other thread is not alive then quit
            if not self.receiveThread.is_alive():
                sys.exit(0)
                
            # Commands start with a '/'
            if body and body[0] == '/':
                self.runCommand(body[1:])
            else:
                message = f'{self.username}: {body}'
                self.client.send(message.encode(self.ENCODING))
            
    def runCommand(self, command):
        match command:
            case 'wisper':
                pass
            case 'help':
                pass
            case 'leave':
                print('Quitting...')
                self.running = False
                self.client.send('/leave'.encode(self.ENCODING))
                sys.exit(0)
                
            case default:
                print('Invalid command')
        
    def run(self):
        self.writeThread.start()
        self.receiveThread.start()
        
        # Send username to server
        self.client.send(self.username.encode(self.ENCODING))

if __name__ == '__main__':
    if len(sys.argv) <= 3:
        print('Need 3 arguments')
        sys.exit()
    client = Client(username=sys.argv[1], host=sys.argv[2], port=int(sys.argv[3]))
    client.run()
    