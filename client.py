"""Module providing functionality for networks programming"""
import socket
import threading
import sys
import os

HEADERSIZE = 10
ENCODING = 'utf-8'

class Client:
    """Class representing a client"""
    def __init__(self, username='John_Pork', host='127.0.0.1', port='1234'):
        # Setup client socket
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.username = username

        # Define two seperate thread handling reads and writes from and to the server
        self.receive_thread = threading.Thread(target=self.receive, args=())
        self.write_thread = threading.Thread(target=self.write, args=())

        self.running = True

        # Variable to check if message is a file
        self.file_name = ''

    def delete_folder(self, folder_name):
        """Function to delete a folder and its contents"""
        if os.path.exists(folder_name):
            for entry in os.scandir(folder_name):
                if entry.is_file():
                    os.unlink(entry.path)
                    print(f"Deleted file: {os.path.basename(entry.path)}")

            os.rmdir(folder_name)
            print(f"Folder '{folder_name}' has been deleted")

    def make_folder(self, folder_name):
        """Function to initialize a folder"""
        self.delete_folder(folder_name)
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' has been created")

    def get_message(self, message_length):
        """Function to receive full messages"""
        full_message = ''
        while True:
            message = self.client.recv(1024)

            if not message:
                return ''

            full_message += message.decode(ENCODING)
            if len(full_message) == message_length:
                return full_message

    def get_file(self, message_length):
        """Function to receive full files"""
        full_file = b''
        while True:
            message = self.client.recv(1024)

            if not message:
                return ''

            full_file += message
            progress = (len(full_file) / message_length) * 100
            self.show_progress_bar(progress)

            if len(full_file) == message_length:
                print(' Success!')
                return full_file

    def show_progress_bar(self, progress):
        """Function to show a download progress bar"""
        bar_length = 25
        progress = max(0, min(progress, 100))  # Ensure progress is between 0 and 100
        width = int(bar_length * progress / 100)
        percentage = f"{progress:.2f}%"
        progress_bar = '[' + '#' * width + ' ' * (bar_length - width) + ']' + ' ' + percentage
        # Uses ANSI character to move cursor left
        # Not sure if it works on windows or not, but works on Linux
        sys.stdout.write("\u001b[1000D" + progress_bar)
        sys.stdout.flush()

    def send_message(self, message):
        """Function to send encoded messages with header size"""
        message = f'{len(message):<{HEADERSIZE}}' + message
        self.client.sendall(message.encode(ENCODING))

    def receive(self):
        """Function to receive and display messages from the server"""
        while self.running:
            # Get message length in header
            message_length = self.client.recv(10).decode(ENCODING)

            # If the other thread is not alive then quit
            if not self.write_thread.is_alive():
                sys.exit(0)

            # If received empty string, it means server has issues
            if message_length:
                message_length = int(message_length)
                if self.file_name:
                    file_string = self.get_file(message_length)
                    file_path = os.path.join(self.username, self.file_name)
                    with open(file_path, 'wb') as file:
                        file.write(file_string)
                    print(f"File saved at: {file_path}")
                    self.file_name = ''
                else:
                    message = self.get_message(message_length)
                    print(message)
            else:
                print('Something went wrong. Press any key to exit. Disconnecting...')
                self.running = False
                self.client.close()
                sys.exit(0)

    def write(self):
        """Function to send messages to the server"""
        while self.running:
            body = input()
            # If the other thread is not alive then quit
            if not self.receive_thread.is_alive():
                sys.exit(0)

            if not body:
                continue

            # Commands start with a '/'
            if body[0] == '/':
                body = self.run_command(body)

            self.send_message(body)

    def run_command(self, command):
        """Function to run commands when a forward slash given"""
        command_type = command.split(' ')[0]
        match command_type[1:]:
            case 'help':
                pass

            case 'make_folder':
                pass

            case 'download':
                if len(command.split(' ')) == 1:
                    print('Fetching download folder content...')
                else:
                    self.file_name = command.split(' ')[1]
                    print('Downloading...')

            case 'whisper':
                if len(command.split(' ')) < 3:
                    return '/'
                print('Whispering...')

            case 'leave':
                print('Leaving...')
                self.running = False

        return command

    def run(self):
        """Function to run the client object"""
        self.receive_thread.start()
        self.write_thread.start()

        self.make_folder(self.username)
        self.send_message(self.username)

if __name__ == '__main__':
    if len(sys.argv) <= 3:
        print('Need 3 arguments')
        sys.exit()

    client = Client(username=sys.argv[1], host=sys.argv[2], port=int(sys.argv[3]))
    client.run()
    