import socket

def print_board(board):
    for i, row in enumerate(board):
        print(" | ".join([cell if cell is not None else " " for cell in row]))
        if i < 2:
            print("-" * 9)
    print("\n")

def board_to_string(board):
    rows = []
    for i, row in enumerate(board):
        rows.append("|".join([cell if cell is not None else " " for cell in row]))
        if i < 2:
            rows.append("-" * 9)
    return "\n".join(rows)

def check_winner(board):
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] is not None:
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] is not None:
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2]
    return None

def is_draw(board):
    for row in board:
        if None in row:
            return False
    return True

def parse_move(move):
    try:
        row, col = map(int, move.split(","))
        if 0 <= row < 3 and 0 <= col < 3:
            return row, col
        else:
            print("Move out of bounds. Please enter a valid move.")
            return None, None
    except ValueError:
        print("Invalid input format. Please enter your move as 'row,col'.")
    return None, None


def server_program():
    host = '172.20.2.33'
    port = 5000  # initiate port no above 1024
    board = [[None for _ in range(3)] for _ in range(3)]  # Initialize a 3x3 board

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    print("Server started. Waiting for a connection...")

    server_socket.listen(1)
    conn, address = server_socket.accept()
    print("Connection from: " + str(address))

    conn.sendall(("Welcome to Tic Tac Toe! You are 'O'. Server is 'X'.\n"
                  + board_to_string(board) + "\nYour move (O) enter as row, col: ").encode())
    client_turn = True  # Assume the client starts first
    while True:
        if client_turn:
            raw = conn.recv(1024).decode().strip()
            if not raw:
                break
            print(f"Received move from client: {raw}")


            row, col = parse_move(raw)
            if row is None:
                conn.sendall("Invalid move. Please enter a valid move.".encode())
                continue
            if board[row][col] is not None:
                conn.sendall("Invalid move. Cell already occupied.".encode())
                continue
        
            board[row][col] = 'O'  # Assume the server is always 'X'
            print_board(board)

            winner = check_winner(board)
            if winner:
                conn.sendall(f"Player {winner} wins!".encode())
                print(f"Player {winner} wins!")
                break
            elif is_draw(board):
                conn.sendall("It's a draw!".encode())
                print("It's a draw!")
                break
            conn.sendall((board_to_string(board) + "\nServer's turn.").encode())
            client_turn = False


        else:    
            print_board(board)
            move = input("Your move (row,col): ")
            row, col = parse_move(move)
            if row is None and col is None:
                print("Invalid move. Please enter a valid move.")
                continue

            board[row][col] = 'X'  # Assume the server is always 'X'
            winner = check_winner(board)
            if winner:
                conn.sendall(f"Player {winner} wins!".encode())
                print(f"Player {winner} wins!")
                break
            elif is_draw(board):
                conn.sendall("It's a draw!".encode())
                print("It's a draw!")
                break

            conn.sendall((board_to_string(board) + "\nYour move.").encode())
            client_turn = True

    conn.sendall(("\nGame over.").encode())        
    conn.close()  # close the connection
    server_socket.close()  # close the server socket

if __name__ == '__main__':
    server_program()