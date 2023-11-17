import tkinter as tk
from tkinter import font
from tkinter import simpledialog
from tkinter.colorchooser import askcolor
from typing import NamedTuple

class Player(NamedTuple):
    label: str
    color: str


class Move(NamedTuple):
    row: int
    col: int
    label: str = ""

class ScoreCounter:
    def __init__(self):
        self.scores = {"X": 0, "O": 0}

    def increment_score(self, player_label):
        self.scores[player_label] += 1

    def get_score(self, player_label):
        return self.scores[player_label]

class TicTacToeGame:
    def __init__(self, board_size=3):
        self.board_size = board_size
        self.current_player = Player(label="X", color="blue")
        self.next_player = Player(label="O", color="green")
        self.winner_combo = []
        self._current_moves = [[Move(row, col) for col in range(board_size)] for row in range(board_size)]
        self._has_winner = False
        self._winning_combos = self._get_winning_combos()
        self.scores = ScoreCounter()

    def _get_winning_combos(self):
        combos = []
        for row in self._current_moves:
            for start_col in range(self.board_size - 2):
                combo = [(row[start_col + i].row, row[start_col + i].col) for i in range(3)]
                combos.append(combo)

        for col in range(self.board_size):
            for start_row in range(self.board_size - 2):
                combo = [(start_row + i, col) for i in range(3)]
                combos.append(combo)

        for start_row in range(self.board_size - 2):
            for start_col in range(self.board_size - 2):
                diagonal1 = [(start_row + i, start_col + i) for i in range(3)]
                diagonal2 = [(start_row + i, start_col + 2 - i) for i in range(3)]
                combos.append(diagonal1)
                combos.append(diagonal2)

        return combos

    def is_valid_move(self, move):
        row, col = move.row, move.col
        return not self._has_winner and self._current_moves[row][col].label == ""

    def process_move(self, move):
        row, col = move.row, move.col
        self._current_moves[row][col] = move
        for combo in self._winning_combos:
            results = set(self._current_moves[n][m].label for n, m in combo)
            if len(results) == 1 and "" not in results:
                self._has_winner = True
                self.winner_combo = combo
                break

    def has_winner(self):
        return self._has_winner

    def is_tied(self):

        played_moves = [move.label for row in self._current_moves for move in row]
        return not self._has_winner and all(played_moves)

    def toggle_player(self):
        self.current_player, self.next_player = self.next_player, self.current_player

    def reset_game(self):
        self.current_player = Player(label="X", color="blue")
        self.next_player = Player(label="O", color="green")
        self.winner_combo = []
        self._current_moves = [[Move(row, col) for col in range(self.board_size)] for row in range(self.board_size)]
        self._has_winner = False

class TicTacToeBoard(tk.Tk):
    def __init__(self, game, board_size):
        super().__init__()
        self.title("Tic Tac Toe")
        self._cells = {}
        self._game = game
        self._create_menu()
        self.board_size = board_size
        self.grid_frame = None
        self._create_board_display()
        self._create_board_grid()

    def _create_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar)
        creator_menu = tk.Menu(master=menu_bar)
        file_menu.add_command(label="Restart", command=self.reset_board)
        file_menu.add_command(label="Change Player Color", command=self.change_player_color)
        file_menu.add_command(label="Change Board Size", command=self.change_board_size)
        file_menu.add_command(label="Change Background Color", command=self.change_board_background)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=quit)
        menu_bar.add_cascade(label="Settings", menu=file_menu)
        menu_bar.add_cascade(label="Creator", menu=creator_menu)
        creator_menu.add_command(label="Spardaus")
        creator_menu.add_command(label="https://github.com/Spardaus/TicTacToe")
        creator_menu.add_command(label="2023_11_10")

    def change_board_background(self):
        new_color = askcolor(title="Choose Background Color")[1]
        if new_color:
            self.config(bg=new_color)
            if self.grid_frame:
                self.grid_frame.config(bg=new_color)
            for button in self._cells.keys():
                button.config(highlightbackground=new_color)

    def change_player_color(self):
        player = self._game.current_player
        new_color = askcolor(title=f"Choose Color for Player {player.label}")
        if new_color[1]:
            player = player._replace(color=new_color[1])
            self._game.current_player = player
            self._update_display(f"{self._game.current_player.label}'s Turn", player.color)

    def change_board_size(self):
        result = simpledialog.askinteger("Board Size", "Enter board size (e.g., 3 for 3x3):", initialvalue=self.board_size)
        if result:
            self.destroy()
            game = TicTacToeGame(board_size=result)
            board = TicTacToeBoard(game, result)
            board.mainloop()

    def _create_board_display(self):
        display_frame = tk.Frame(master=self)
        display_frame.pack(fill=tk.X)
        self.display = tk.Label(
            master=display_frame,
            text=f"{self._game.current_player.label}'s Turn",
            font=font.Font(size=28, weight="bold"),
        )
        self.display.pack()

    def _create_board_grid(self):
        self.grid_frame = tk.Frame(master=self, bg="lightblue")
        self.grid_frame.pack()
        for row in range(self.board_size):
            self.rowconfigure(row, weight=1, minsize=50)
            self.columnconfigure(row, weight=1, minsize=75)
            for col in range(self.board_size):
                button = tk.Button(
                    master=self.grid_frame,
                    text="",
                    font=font.Font(size=36, weight="bold"),
                    fg="black",
                    width=3,
                    height=2,
                    highlightbackground="lightblue",
                )
                self._cells[button] = (row, col)
                button.bind("<ButtonPress-1>", self.play)
                button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    def play(self, event):
        clicked_btn = event.widget
        row, col = self._cells[clicked_btn]
        move = Move(row, col, self._game.current_player.label)
        if self._game.is_valid_move(move):
            self._update_button(clicked_btn)
            self._game.process_move(move)
            if self._game.is_tied():
                self._update_display(msg="It's a Tie!", color="red")
            elif self._game.has_winner():
                self._highlight_cells()
                msg = f'Player "{self._game.current_player.label}" Wins!'
                color = self._game.current_player.color
                self._update_display(msg, color)
                self._game.scores.increment_score(self._game.current_player.label)
                self._update_display(f"Scores: X - {self._game.scores.get_score('X')}, O - {self._game.scores.get_score('O')}", color)
            else:
                self._game.toggle_player()
                self._update_display(f"{self._game.current_player.label}'s Turn", self._game.current_player.color)

    def _update_button(self, clicked_btn):
        clicked_btn.config(text=self._game.current_player.label)
        clicked_btn.config(fg=self._game.current_player.color)

    def _update_display(self, msg, color="black"):
        self.display["text"] = msg
        self.display["fg"] = color

    def _highlight_cells(self):
        for button, coordinates in self._cells.items():
            if coordinates in self._game.winner_combo:
                button.config(highlightbackground="red")

    def reset_board(self):
        self._game.reset_game()
        self._update_display(f"{self._game.current_player.label}'s Turn", self._game.current_player.color)
        for button in self._cells.keys():
            button.config(highlightbackground="lightblue")
            button.config(text="")
            button.config(fg="black")

def main():
    board_size = simpledialog.askinteger("Board Size", "Enter board size (e.g., 3 for 3x3):")
    if board_size:
        game = TicTacToeGame(board_size=board_size)
        board = TicTacToeBoard(game, board_size)
        board.mainloop()

if __name__ == "__main__":
    main()
