import time
import tkinter as tk
import typing as t


class GraphEditorFrame(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        self.create_widgets()

    def create_widgets(self):
        ''' Create widgets
        '''
        BUTTON_WIDTH = 5
        BUTTON_HEIGHT = 1
        TEXTEDITOR_LINEHEIGHT = 26
        TEXTEDITOR_CHARACTERWIDTH = 60
        GRAPHEDITOR_HEIGHT = 200
        GRAPHEDITOR_WIDTH = 400
        # Texteditor spans one row more than graph editor
        TEXTEDITOR_ROWSPAN = 20
        TEXTEDITOR_COLUMNSPAN = 30
        GRAPHEDITOR_COLUMNSPAN = 10
        assert(GRAPHEDITOR_COLUMNSPAN > 5)
        top = self.winfo_toplevel()
        # Enable scaling
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        for row_idx in range(TEXTEDITOR_ROWSPAN+2):
            self.rowconfigure(row_idx, weight=1)
        for column_idx in range(TEXTEDITOR_COLUMNSPAN+GRAPHEDITOR_COLUMNSPAN):
            self.columnconfigure(column_idx, weight=1)
        # Texteditor interface
        self.filename_label = tk.Label(self, text='image.txt')
        self.filename_label.grid(row=0, column=0,
                                 columnspan=TEXTEDITOR_COLUMNSPAN)
        # Grapheditor interface
        self.inkcolor_button = tk.Button(self, text='Ink')
        self.bordersize_entry = tk.Spinbox(self, text='2', width=4)
        self.oval_menubutton = tk.Menubutton(self, text='Oval',
                                             width=BUTTON_WIDTH,
                                             height=BUTTON_HEIGHT)
        self.figure_menu = tk.Menu(self)
        self.figure_menu.add_checkbutton(label='Oval')
        self.oval_menubutton['menu'] = self.figure_menu
        self.mousepos_label = tk.Label(self, text='0:0')

        # Grapheditor interface location
        self.inkcolor_button.grid(row=0, column=TEXTEDITOR_COLUMNSPAN + 1,
                                  rowspan=2)
        self.bordersize_entry.grid(row=0, column=TEXTEDITOR_COLUMNSPAN + 2,
                                   rowspan=2)
        self.oval_menubutton.grid(row=0, column=TEXTEDITOR_COLUMNSPAN + 3,
                                  rowspan=2)
        self.mousepos_label.grid(row=0, column=TEXTEDITOR_COLUMNSPAN + 4,
                                 rowspan=2)

        self.text_editor = tk.Text(self, width=TEXTEDITOR_CHARACTERWIDTH,
                                   height=TEXTEDITOR_LINEHEIGHT)
        self.text_editor.grid(row=1, column=0, rowspan=TEXTEDITOR_ROWSPAN,
                              columnspan=TEXTEDITOR_COLUMNSPAN,
                              sticky=tk.N+tk.S+tk.E+tk.W)
        self.graph_editor = tk.Canvas(self, bg='#854116',
                                      width=GRAPHEDITOR_WIDTH,
                                      height=GRAPHEDITOR_HEIGHT)
        self.graph_editor.grid(row=2, column=TEXTEDITOR_COLUMNSPAN,
                               columnspan=GRAPHEDITOR_COLUMNSPAN,
                               rowspan=TEXTEDITOR_ROWSPAN - 1,
                               sticky=tk.N+tk.S+tk.E+tk.W)
        # Add empty space to fix the first row buttons
        self.columnconfigure(TEXTEDITOR_COLUMNSPAN + 5,
                             minsize=GRAPHEDITOR_WIDTH - 5 * BUTTON_WIDTH,
                             weight=1)

        # Application control buttons
        self.quit_button = tk.Button(self, text='Quit', width=BUTTON_WIDTH,
                                     height=BUTTON_HEIGHT, command=self.quit)
        self.save_button = tk.Button(self, text='Save',
                                     width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                     command=self.save_text)
        self.load_button = tk.Button(self, text='Load',
                                     width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                     command=self.load_text)
        self.save_button.grid(row=TEXTEDITOR_ROWSPAN + 1, column=0,
                              sticky=tk.N+tk.S+tk.E+tk.W)
        self.load_button.grid(row=TEXTEDITOR_ROWSPAN + 1, column=1,
                              sticky=tk.N+tk.S+tk.E+tk.W)
        self.quit_button.grid(row=TEXTEDITOR_ROWSPAN + 1,
                              column=TEXTEDITOR_COLUMNSPAN +
                              GRAPHEDITOR_COLUMNSPAN - 1, sticky=tk.N+tk.S)

    def save_text(self):
        pass

    def load_text(self):
        pass


graph_editor_frame = GraphEditorFrame()
graph_editor_frame.master.title('Graph Edit')
graph_editor_frame.mainloop()
