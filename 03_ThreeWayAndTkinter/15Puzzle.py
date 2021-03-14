import time
import tkinter as tk
import tkinter.messagebox
import typing as t
import random

# In the game all values belong to this interval
NUMBER_LIMITS = [1, 15]
BOARD_SIZE = 4
# From which cell the game grid starts
GAME_GRID_ROW = 1
GAME_GRID_COLUMN = 0

class GameRequest(t.NamedTuple):
    button_idx: int
    new_grid_row: int
    new_grid_column: int

class GameState():
    ''' The Puzzle 15 stat.
    Keeps track of the game cells
    '''
    def __init__(self, val_lst: t.List[int]):
        assert(len(val_lst) == BOARD_SIZE * BOARD_SIZE - 1)
        self.cells = []
        # A button doesn't change its value
        # Keep the dict to find button by value fast
        self.val_to_button_idx = {}
        for row in range(BOARD_SIZE):
            cell_row = []
            for column in range(BOARD_SIZE):
                if row * BOARD_SIZE + column < BOARD_SIZE * BOARD_SIZE - 1:
                    cell_row.append(val_lst[row * BOARD_SIZE + column])
                    self.val_to_button_idx[val_lst[row * BOARD_SIZE + column]] = \
                        row * BOARD_SIZE + column
                else:
                    # 0 indicates lack of the element
                    cell_row.append(0)
            self.cells.append(cell_row)
        self.cells[BOARD_SIZE - 1][BOARD_SIZE - 1] = 0
        # Track the location of the empty space on the board
        self.empty_loc = (BOARD_SIZE - 1, BOARD_SIZE - 1)

    def is_win(self) -> bool:
        ''' Has the player won the game?
        '''
        if self.empty_loc[0] != BOARD_SIZE - 1 \
           or self.empty_loc[1] != BOARD_SIZE - 1:
            return False
        for row in range(BOARD_SIZE):
            for column in range(BOARD_SIZE):
                if row * BOARD_SIZE + column < BOARD_SIZE * BOARD_SIZE - 1:
                    if self.cells[row][column] != row * BOARD_SIZE + column + 1:
                        return False
        return True

    def get_button_by_value(self, val: int) -> int:
        ''' Given the value of a button label,
        find the button index in array
        '''
        assert(val > 0 and val < BOARD_SIZE * BOARD_SIZE)
        return self.val_to_button_idx[val]

    def move_cell(self, row_idx: int, column_idx: int) -> GameRequest:
        ''' In the game request
        Results:
            Game request, with the grid position relative to 
            the cell start
        '''
        assert(row_idx >= 0 and row_idx < BOARD_SIZE)
        assert(column_idx >= 0 and column_idx < BOARD_SIZE)
        cell_val = self.cells[row_idx][column_idx]
        # The cell neighbors the empty space
        if abs(self.empty_loc[0] - row_idx) + \
           abs(self.empty_loc[1] - column_idx) == 1:
            # Swap the cell and the empty space
            empty_loc_row = self.empty_loc[0]
            empty_loc_column = self.empty_loc[1]
            self.empty_loc = (row_idx, column_idx)
            self.cells[row_idx][column_idx] = 0
            self.cells[empty_loc_row][empty_loc_column] = cell_val
            return GameRequest(button_idx=self.get_button_by_value(cell_val),
                               new_grid_row = empty_loc_row,
                               new_grid_column = empty_loc_column)
        return None

class BoardButton(tk.Button):
    ''' Initialize a button with a numerical label.
    It will belong to a puzzle board
    '''
    def __init__(self, number: int, row_idx: int, column_idx: int,
                 handler: t.Callable[[int, int], None],
                 master=None):
        ''' Handler requires two arguments: row_idx and column_idx 
        '''
        # The number must be in the limits
        assert(number >= NUMBER_LIMITS[0] and number <= NUMBER_LIMITS[1])
        MAX_DIGITS_IN_NUMBER = 2
        # Constants for defining the button's design
        WIDTH_MULTIPLIER = 3
        WIDTH_TO_HEIGHT_RATIO = 2
        super().__init__(master, text=str(number),command=self.on_click)
        self.grid(row=row_idx, column=column_idx, sticky=tk.N+tk.S+tk.E+tk.W)
        self['width'] = MAX_DIGITS_IN_NUMBER * WIDTH_MULTIPLIER
        self['height'] = self['width'] // WIDTH_TO_HEIGHT_RATIO
        # Auxiliary buttons occupy the first level of grid
        self.row_idx = row_idx - GAME_GRID_ROW
        self.column_idx = column_idx - GAME_GRID_COLUMN
        self.handler = handler

    def update_grid(self, new_row_idx, new_column_idx):
        self.row_idx = new_row_idx
        self.column_idx = new_column_idx
        self.grid(row=new_row_idx + GAME_GRID_ROW, 
                  column=new_column_idx + GAME_GRID_COLUMN,
                  sticky=tk.N+tk.S+tk.E+tk.W)

    def on_click(self):
        self.handler(self.row_idx, self.column_idx)


class GameFrame(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        self.create_widgets()

    def create_widgets(self):
        BUTTON_WIDTH = 10
        BUTTON_HEIGHT = 1
        top = self.winfo_toplevel()
        # Enable scaling
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        for row_idx in range(BOARD_SIZE+1):
            self.rowconfigure(row_idx, weight=1)
        for column_idx in range(BOARD_SIZE):
            self.columnconfigure(column_idx, weight=1)

        self.quit_button = tk.Button(self, text='Quit', width=BUTTON_WIDTH,
                                     height=BUTTON_HEIGHT, command=self.quit)
        self.new_button = tk.Button(self, text='New',
                                    width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                    command=self.generate_board)
        self.new_button.grid(row=0, column=0, columnspan=2, sticky=tk.N+tk.S)

        self.quit_button.grid(row=0, column=2, columnspan=2, sticky=tk.N+tk.S)
        self.generate_board()

    def generate_board(self):
        ''' Generate a new game board.
        Fill it with numbers (1..15) in random order
        '''
        val_lst = list(range(1, 16))
        random.shuffle(val_lst)
        self.numeric_buttons = []
        for row_idx in range(4):
            for column_idx in range(4):
                # Leave the corner empty
                if row_idx * 4 + column_idx < 15:
                    self.numeric_buttons.append(
                        BoardButton(val_lst[row_idx * 4 + column_idx],
                                    row_idx=row_idx + GAME_GRID_ROW,
                                    column_idx=column_idx + GAME_GRID_COLUMN,
                                    master=self,
                                    handler=self.on_click_game_button))
        self.game_state = GameState(val_lst)

    def on_click_game_button(self, row_idx: int, column_idx: int):
        ''' Change a game state after the player clicked on button
        Updates the button location 
        '''
        game_request = self.game_state.move_cell(row_idx, column_idx)
        if game_request is None:
            # Can't move the button
            return (row_idx, column_idx)
        self.numeric_buttons[game_request.button_idx].update_grid(game_request.new_grid_row,
                                                                  game_request.new_grid_column)
        if self.game_state.is_win():
            tk.messagebox.showinfo("Congratulations!", "You won!")
            self.generate_board()


game_frame = GameFrame()
game_frame.master.title('15 Puzzle')
game_frame.mainloop()
