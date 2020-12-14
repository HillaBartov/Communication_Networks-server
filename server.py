import socket
import sys
import os


# Extract the file path from the message
def get_path(message):
    if not message:
        message = "empty"
    elif message.find("redirect") != -1:
        return "redirect"
    else:
        start_index = message.find("/") + 1
        end_index = message.find("HTTP") - 1
        message = message[start_index:end_index]
        if message == "":
            message = "index.html"
    return message


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(("127.0.0.1", int(sys.argv[1])))

server.listen(5)
# Change current location to the files directory
try:
    os.chdir("files")
except OSError as e:
    print("Could not find files directory")

while True:
    client_socket, client_address = server.accept()
    # Time-out for client message
    client_socket.settimeout(1)
    connection = True
    status = "keep-alive"
    while connection:
        try:
            data = client_socket.recv(10000).decode('utf-8')
        # data receive timeout - break
        except socket.timeout as e:
            break
        # Print Clients request
        print(data)
        # Change state form keep-alive to close
        if data.find("Connection: close") != -1:
            # Close connection after reply
            connection = False
            status = "close"
        path = get_path(data)
        if path == "empty":
            break
        try:
            # Image file
            if path.find("jpg") or path.find("ico"):
                # Read in binary mode
                f = open(path, "rb")
                content = f.read()
            # Non-Image file
            else:
                f = open(path)
                content = f.read().encode()
            # reply length
            length = os.path.getsize(path)
            # Build reply format
            reply = ("HTTP/1.1 200 OK\nConnection: " + status + "\nContent-Length: " + str(
                length) + "\n\n").encode() + content
        # Requested file not found
        except OSError:
            # Redirect
            if path.find("redirect") != -1:
                reply = "HTTP/1.1 301 Moved Permanently\nConnection: close\nLocation: /result.html\n\n".encode()
            # Not Found
            else:
                reply = "HTTP/1.1 404 Not Found\nConnection: close\n\n".encode()
            # close connection
            connection = False
        # Send Server's reply to the client
        client_socket.send(reply)
    # Close client socket while connection = False or after 1 second - receive timeout
    client_socket.close()
