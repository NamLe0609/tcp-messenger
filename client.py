"""Module providing functionality for networks programming"""
import socket
import threading
import sys
import os

HEADERSIZE = 10
ENCODING = 'utf-8'
FILE_MSG = '0'
TEXT_MSG = '1'

class Client:
    """Class representing a client"""
    def __init__(self, username='John_Pork', host='127.0.0.1', port='1234'):
        # Setup client socket
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((host, port))
        except ConnectionRefusedError:
            print('Could not connect to server')
            sys.exit(0)
        self.username = username

        # Define two seperate thread handling reads and writes from and to the server
        self.receive_thread = threading.Thread(target=self.receive, args=())
        self.write_thread = threading.Thread(target=self.write, args=())
        self.receive_thread.daemon = True
        self.write_thread.daemon = True

        self.running = True

        # Variable to keep track of file name
        self.file_name = ''

    def delete_folder(self, folder_name):
        """Function to delete a folder and its contents"""
        if os.path.exists(folder_name):
            for entry in os.scandir(folder_name):
                if entry.is_file():
                    os.unlink(entry.path)
                    print(f"Deleted file: {os.path.basename(entry.path)}")

            os.rmdir(folder_name)

    def make_folder(self, folder_name):
        """Function to initialize a folder"""
        self.delete_folder(folder_name)
        os.makedirs(folder_name)

    def get_message(self, message_length):
        """Function to receive full messages"""
        full_message = ''
        remaining = message_length
        while True:
            # Receive either 4096, or the remaining,
            # whichever is smaller since we do not want to overbuffer
            message = self.client.recv(min(remaining, 4096))

            if not message:
                return ''

            remaining -= len(message)
            full_message += message.decode(ENCODING)
            if len(full_message) == message_length:
                return full_message

    def get_file(self, message_length, file_path):
        """Function to receive full files and write it to user folder"""
        try:
            with open(file_path, 'wb') as file:
                remaining = message_length
                while remaining > 0:
                    # Receive either 65536, or the remaining,
                    # whichever is smaller since we do not want to overbuffer
                    # Large buffer size helps with download speeds
                    message = self.client.recv(min(remaining, 65536))

                    if not message:
                        print(' Something went wrong!')
                        break

                    file.write(message)
                    remaining -= len(message)
                    progress = 1 - remaining / message_length
                    self.show_progress_bar(progress)

                if remaining == 0:
                    print(' Success!')
        except OSError:
            self.exit_thread()

    def show_progress_bar(self, progress):
        """Function to show a download progress bar"""
        bar_length = 25
        width = int(bar_length * progress)
        progress *= 100
        percentage = f"{progress:.2f}%"
        progress_bar = '[' + '#' * width + ' ' * (bar_length - width) + ']' + ' ' + percentage
        # Uses ANSI character to move cursor left
        sys.stdout.write("\u001b[1000D" + progress_bar)
        sys.stdout.flush()

    def send_message(self, message):
        """Function to send encoded messages with header size"""
        message = f'{len(message):<{HEADERSIZE}}' + message
        self.client.sendall(message.encode(ENCODING))

    def receive(self):
        """Function to receive and display messages from the server"""
        try:
            while self.running:
                # Get message length in header
                try:
                    message_header = self.client.recv(HEADERSIZE).decode(ENCODING)
                except ConnectionResetError:
                    message_header = ''

                # If received empty string, it means server has issues
                if message_header:
                    message_type = message_header[0]
                    message_length = int(message_header[1:])

                    if message_type == FILE_MSG:
                        file_path = os.path.join(self.username, self.file_name)
                        self.get_file(message_length, file_path)
                        print(f"File saved at: {file_path}")
                    else:
                        message = self.get_message(message_length)
                        print(message)
                else:
                    self.exit_thread()
        except OSError:
            self.exit_thread()

    def write(self):
        """Function to send messages to the server"""
        while self.running:
            try:
                body = input()
            except EOFError:
                self.exit_thread()

            # Empty input ignored
            if not body:
                continue

            # Prevent overly large message (1000 characters!)
            # Large messages doesnt cause problems, but are very ugly.
            # This feature can be added without causing problems
            #if len(body) > 1000:
            #    print('Your message is too big!')

            # Commands start with a '/'
            if body[0] == '/':
                body = self.run_command(body)

            self.send_message(body)

    def run_command(self, command):
        """Function to run commands when a forward slash given"""
        command_type = command.split(' ')[0]
        match command_type[1:]:

            case 'download':
                if len(command.split(' ')) == 1:
                    print('Fetching download folder content...')
                elif len(command.split(' ')) == 2:
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
        # This art is exclusively for decorative purposes
        # Welcome message still is sent from the server
        # This is not meant for marking!
        print(r"""

.----------------------------------------------------------------.
| ██████╗██╗  ██╗ █████╗ ████████╗████████╗██╗███╗   ██╗ ██████╗ |
|██╔════╝██║  ██║██╔══██╗╚══██╔══╝╚══██╔══╝██║████╗  ██║██╔════╝ |
|██║     ███████║███████║   ██║      ██║   ██║██╔██╗ ██║██║  ███╗|
|██║     ██╔══██║██╔══██║   ██║      ██║   ██║██║╚██╗██║██║   ██║|
|╚██████╗██║  ██║██║  ██║   ██║      ██║   ██║██║ ╚████║╚██████╔╝|
| ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝ |
'----------------------------------------------------------------'

        """)

        self.write_thread.join()
        self.receive_thread.join()
        sys.exit(0)

    def exit_thread(self):
        """Function to exit program"""
        print('\nSomething went wrong. Press any key to exit. Disconnecting...')
        self.running = False
        sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) <= 3:
        print('Need 3 arguments')
        sys.exit()

    client = Client(username=sys.argv[1], host=sys.argv[2], port=int(sys.argv[3]))
    try:
        client.run()
    except KeyboardInterrupt:
        pass
        