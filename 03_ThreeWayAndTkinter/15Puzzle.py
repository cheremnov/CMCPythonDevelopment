import time
import tkinter as tk
import typing as t
import random

# In the game all values belong to this interval
NUMBER_LIMITS = [1, 15]


class BoardButton(tk.Button):
    ''' Initialize a button with a numerical label.
    It will belong to a puzzle board
    '''
    def __init__(self, number: int,
                 row_idx: int, column_idx: int, master=None):
        # The number must be in the limits
        assert(number >= NUMBER_LIMITS[0] and number <= NUMBER_LIMITS[1])
        MAX_DIGITS_IN_NUMBER = 2
        # Constants for defining the button's design
        WIDTH_MULTIPLIER = 3
        WIDTH_TO_HEIGHT_RATIO = 2
        super().__init__(master, text=str(number))
        self.grid(row=row_idx, column=column_idx, sticky=tk.N+tk.S+tk.E+tk.W)
        self['width'] = MAX_DIGITS_IN_NUMBER * WIDTH_MULTIPLIER
        self['height'] = self['width'] // WIDTH_TO_HEIGHT_RATIO


class GameFrame(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        self.create_widgets()

    def create_widgets(self):
        BOARD_SIZE = 4
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
                                    row_idx=row_idx + 1,
                                    column_idx=column_idx, master=self))


game_frame = GameFrame()
game_frame.master.title('15 Puzzle')
game_frame.mainloop()
