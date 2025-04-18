#22i1239 cs-g Ai A3 Q3
import pyxel
import random
import copy

# Board and window setup
CELL_SIZE = 10
BOARD_SIZE = 9
WINDOW_SIZE = CELL_SIZE * BOARD_SIZE

# One 3x3 tic-tac-toe board
class MiniBoard:
    def __init__(self):
        self.grid = [["" for _ in range(3)] for _ in range(3)]
        self.winner = None

    # Try marking a cell if it's empty and the board isn't already won
    def mark(self, x, y, player):
        if self.grid[y][x] == "" and not self.winner:
            self.grid[y][x] = player
            self.check_winner()
            return True
        return False

    # Check who won this sub-board (if anyone)
    def check_winner(self):
        lines = self.grid + list(zip(*self.grid))  # rows + cols
        lines.append([self.grid[i][i] for i in range(3)])  # diag \
        lines.append([self.grid[i][2 - i] for i in range(3)])  # diag /
        for line in lines:
            if line[0] != "" and all(cell == line[0] for cell in line):
                self.winner = line[0]
                break

    # Checks if the sub-board is full
    def is_full(self):
        return all(cell != "" for row in self.grid for cell in row)

# Full 9x9 ultimate game logic
class UltimateTicTacToe:
    def __init__(self):
        pyxel.init(WINDOW_SIZE, WINDOW_SIZE + 20, title="Ultimate Tic-Tac-Toe - AC3 CSP AI")

        # 3x3 grid of MiniBoards
        self.boards = [[MiniBoard() for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.next_board = None  # where the next move must go
        self.winner = None
        self.ai_thinking = False
        self.ai_timer = 0

        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    # Called every frame
    def update(self):
        if self.current_player == "X":
            self.human_turn()
        elif self.current_player == "O":
            if not self.ai_thinking:
                self.ai_thinking = True
                self.ai_timer = pyxel.frame_count
            elif pyxel.frame_count - self.ai_timer >= 15:
                self.ai_turn()
                self.ai_thinking = False

    # Handles mouse input for human moves
    def human_turn(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            if my > WINDOW_SIZE:
                return

            gx, gy = mx // CELL_SIZE, my // CELL_SIZE
            bx, by = gx // 3, gy // 3
            cx, cy = gx % 3, gy % 3

            board = self.boards[by][bx]
            if self.winner:
                return
            if self.next_board and (bx, by) != self.next_board:
                return
            if board.grid[cy][cx] != "":
                return

            if board.mark(cx, cy, "X"):
                self.next_board = (cx, cy)
                if self.boards[cy][cx].winner or self.boards[cy][cx].is_full():
                    self.next_board = None
                self.check_ultimate_winner()
                self.current_player = "O"

    # AI makes a move
    def ai_turn(self):
        move = self.csp_ai_move()
        if move:
            bx, by, cx, cy = move
            self.boards[by][bx].mark(cx, cy, "O")
            self.next_board = (cx, cy)
            if self.boards[cy][cx].winner or self.boards[cy][cx].is_full():
                self.next_board = None
            self.check_ultimate_winner()
        self.current_player = "X"

    # Picks the AI move using CSP + MRV
    def csp_ai_move(self):
        valid_moves = self.get_valid_moves("O")
        consistent_moves = self.ac3(valid_moves)
        return self.mrv_heuristic(consistent_moves) if consistent_moves else None

    # Heuristic: prioritize winning the current sub-board first
    # If no winning move, use MRV to pick the move that gives most flexibility
    def mrv_heuristic(self, moves):
        # Check if a move wins the mini-board it's placed in
        def is_winning_move(bx, by, cx, cy):
            board = self.boards[by][bx]
            # Simulate marking and check win (without actually modifying)
            if board.grid[cy][cx] != "":
                return False
            temp_board = copy.deepcopy(board)
            temp_board.mark(cx, cy, "O")
            return temp_board.winner == "O"

        # Step 1: Try to find an immediate winning move
        for move in moves:
            bx, by, cx, cy = move
            if is_winning_move(bx, by, cx, cy):
                return move  # take the win, no questions asked

        # Step 2: Use MRV (pick move that sends opponent to a bigger sub-board)
        def remaining_options(move):
            bx, by, cx, cy = move
            next_board_x, next_board_y = cx, cy
            # if the next board is full or won, player gets free choice
            if self.boards[next_board_y][next_board_x].winner or self.boards[next_board_y][next_board_x].is_full():
                return 9
            empty = sum(1 for row in self.boards[next_board_y][next_board_x].grid for cell in row if cell == "")
            return -empty  # more empty = more flexibility

        return min(moves, key=remaining_options)


    # Basic AC-3 style filtering (remove inconsistent moves)
    def ac3(self, moves):
        queue = list(moves)
        pruned = set()
        while queue:
            move = queue.pop(0)
            if self.is_conflicting(move):
                pruned.add(move)
        return [m for m in moves if m not in pruned]

    # Checks if the move is illegal (cell is taken or board is won)
    def is_conflicting(self, move):
        bx, by, cx, cy = move
        board = self.boards[by][bx]
        return board.winner is not None or board.grid[cy][cx] != ""

    # Returns all legal moves the current player can make
    def get_valid_moves(self, player):
        moves = []

        # if we are locked to a board
        if self.next_board:
            bx, by = self.next_board
            if not self.boards[by][bx].winner and not self.boards[by][bx].is_full():
                for cy in range(3):
                    for cx in range(3):
                        if self.boards[by][bx].grid[cy][cx] == "":
                            moves.append((bx, by, cx, cy))
                return moves

        # otherwise check all valid boards
        for by in range(3):
            for bx in range(3):
                if self.boards[by][bx].winner or self.boards[by][bx].is_full():
                    continue
                for cy in range(3):
                    for cx in range(3):
                        if self.boards[by][bx].grid[cy][cx] == "":
                            moves.append((bx, by, cx, cy))
        return moves

    # Check if someone has won the main board
    def check_ultimate_winner(self):
        macro = [[board.winner if board.winner else "" for board in row] for row in self.boards]

        # check rows and columns
        for i in range(3):
            if macro[i][0] != "" and all(macro[i][j] == macro[i][0] for j in range(3)):
                self.winner = macro[i][0]
            if macro[0][i] != "" and all(macro[j][i] == macro[0][i] for j in range(3)):
                self.winner = macro[0][i]

        # check diagonals
        if macro[0][0] != "" and all(macro[i][i] == macro[0][0] for i in range(3)):
            self.winner = macro[0][0]
        if macro[0][2] != "" and all(macro[i][2 - i] == macro[0][2] for i in range(3)):
            self.winner = macro[0][2]

    # Draw the game state every frame
    def draw(self):
        pyxel.cls(7)

        # highlight the current sub-board
        if self.next_board and not self.winner:
            bx, by = self.next_board
            x = bx * 3 * CELL_SIZE
            y = by * 3 * CELL_SIZE
            pyxel.rectb(x, y, CELL_SIZE * 3, CELL_SIZE * 3, 11)

        # draw all grid lines
        for i in range(10):
            color = 1 if i % 3 == 0 else 5
            pyxel.line(i * CELL_SIZE, 0, i * CELL_SIZE, WINDOW_SIZE, color)
            pyxel.line(0, i * CELL_SIZE, WINDOW_SIZE, i * CELL_SIZE, color)

        # draw the player marks
        for by in range(3):
            for bx in range(3):
                board = self.boards[by][bx]
                for cy in range(3):
                    for cx in range(3):
                        mark = board.grid[cy][cx]
                        x = (bx * 3 + cx) * CELL_SIZE + 2
                        y = (by * 3 + cy) * CELL_SIZE + 2
                        if mark:
                            col = 8 if mark == "X" else 9
                            pyxel.text(x, y, mark, col)

                # if this board is done, color its border
                if board.winner or board.is_full():
                    px = bx * 3 * CELL_SIZE
                    py = by * 3 * CELL_SIZE
                    if board.winner == "X":
                        color = 8
                    elif board.winner == "O":
                        color = 9
                    else:
                        color = 6
                    pyxel.rectb(px + 1, py + 1, CELL_SIZE * 3 - 2, CELL_SIZE * 3 - 2, color)

        # status line
        status = f"Turn: {self.current_player}"
        if self.next_board:
            status += f" | Next Board: {self.next_board}"
        if self.winner:
            status = f"Winner: {self.winner}!"
        pyxel.text(2, WINDOW_SIZE + 2, status, 0)

# launch the game
UltimateTicTacToe()
