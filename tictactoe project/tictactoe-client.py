import socket

def client_program():
    host = '172.20.2.33'
    port = 5000

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    while True:
        data = client_socket.recv(1024).decode()  # receive response
        if not data:
            break
        print(data)

        if "Game over" in data or "wins" in data or "draw" in data:
            break

        if "Your move" in data or "Invalid move" in data:
            message = input("Enter move: ")  # take input
            client_socket.sendall(message.encode())  # send message

    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()