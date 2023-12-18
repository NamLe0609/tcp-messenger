import socket
import threading
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

if __name__ == '__main__':
    main()