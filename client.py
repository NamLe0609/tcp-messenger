import socket
import threading
import sys

class Client:
    
    def __init__(self, username='John_Pork', host='127.0.0.1', port='1234'):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.username = username
        self.client.send(self.username.encode('ascii'))
        
        self.writeThread = threading.Thread(target=self.write, args=())
        self.receiveThread = threading.Thread(target=self.receive, args=())

    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode('ascii')
                if not self.writeThread.is_alive():
                    sys.exit(0)
                if message:
                    print(message)
                else:
                    print('Something went wrong. Disconnecting.')
                    self.client.close()
                    sys.exit(0)
            except:
                break

    def write(self):
        while True:
            body = input('')
            message = ''
            
            if not self.receiveThread.is_alive():
                sys.exit(0)
                
            if body[0] == '/':
                self.runCommand(body)
            else:
                message = f'{self.username}: {body}'
                self.client.send(message.encode('ascii'))
            
    def runCommand(self, command):
        match command[1:]:
            case 'wisper':
                pass
            case 'help':
                pass
            case 'leave':
                print('Quitting...')
                self.client.send('/leave'.encode('ascii'))
                sys.exit(0)
                
            case default:
                print('Invalid command')
        
    def run(self):
        self.receiveThread.start()
        self.writeThread.start()

if __name__ == '__main__':
    if len(sys.argv) <= 3:
        print('Need 3 arguments')
        sys.exit()
    
    client = Client(username=sys.argv[1], host=sys.argv[2], port=int(sys.argv[3]))
    client.run()
    