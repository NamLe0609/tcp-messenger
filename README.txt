Python Instant Messenger

Overview:
A client-server messaging system, enabling real-time text communication and file sharing over TCP.

Setup:

    Server:
        Run: python server.py [port]

    Client:
        Connect: python client.py [username] [hostname] [port]

Features and Instructions:

    Broadcast: Send messages normally
    Unicast: /whisper [client_name] [message]
    Request list of files: /download
    Download a file: /download [file_name]
    Disconnect from server: /leave


    