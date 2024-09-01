# Python Instant Messenger

A client-server messaging system, enabling real-time text communication and file sharing over TCP.

## Setup:

**Run the server**: `python server.py [port]`

**Connect a client**: `python client.py [username] [hostname] [port]`

## Features and Instructions:

- **Broadcast**: Send messages normally (Type and press enter)
- **Unicast**: `/whisper [client_name] [message]`
- **Request list of files**: `/download`
- **Download a file**: `/download [file_name]`
- **Disconnect from server**: `/leave`

## Notes:

**Downloading**: For the file name, include the file extension type like .bin or .mp3.

**Download file**: A download folder has been created with 5 sample bin files. To test sending videos and images, add these to this folder.    
